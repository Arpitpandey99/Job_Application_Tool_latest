"""
Job Scraper - Multi-platform job scraping with anti-detection measures
"""
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
from loguru import logger
import json


@dataclass
class JobListing:
    """Structured job listing data"""
    job_id: str
    title: str
    company: str
    location: str
    job_type: str  # Full-time, Contract, etc.
    work_mode: str  # Remote, Hybrid, On-site
    salary: Optional[str]
    description: str
    requirements: str
    posted_date: str
    apply_url: str
    source: str  # linkedin, indeed, etc.
    scraped_at: datetime
    
    def to_dict(self):
        return asdict(self)


class JobScraper:
    """Base scraper class with common functionality"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def init_driver(self):
        """Initialize Selenium WebDriver with anti-detection measures"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Exclude automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None


class LinkedInScraper(JobScraper):
    """Scraper for LinkedIn Jobs"""
    
    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 50) -> List[JobListing]:
        """Scrape jobs from LinkedIn"""
        logger.info(f"Scraping LinkedIn for: {keywords} in {location}")
        jobs = []
        
        try:
            self.init_driver()
            
            # Build search URL
            base_url = "https://www.linkedin.com/jobs/search/"
            search_url = f"{base_url}?keywords={keywords}&location={location}&f_TPR=r86400"
            
            self.driver.get(search_url)
            self.random_delay(3, 5)
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 4)
            
            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='base-card')[:max_jobs]
            
            for card in job_cards:
                try:
                    easy_apply_label = card.find_element(By.XPATH, ".//span[contains(text(), 'Easy Apply')]")
                except:
                    continue
                try:
                    # Extract job details
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    date_elem = card.find('time')
                    
                    if not all([title_elem, company_elem, link_elem]):
                        continue
                    
                    job_url = link_elem.get('href', '')
                    job_id = job_url.split('/')[-1].split('?')[0] if job_url else f"linkedin_{int(time.time())}"
                    
                    # Get detailed job info
                    job_details = self._get_job_details(job_url)
                    
                    job = JobListing(
                        job_id=f"linkedin_{job_id}",
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip(),
                        location=location_elem.text.strip() if location_elem else location,
                        job_type=job_details.get('job_type', 'Full-time'),
                        work_mode=job_details.get('work_mode', 'Not specified'),
                        salary=job_details.get('salary'),
                        description=job_details.get('description', ''),
                        requirements=job_details.get('requirements', ''),
                        posted_date=date_elem.get('datetime', '') if date_elem else '',
                        apply_url=job_url,
                        source='linkedin',
                        scraped_at=datetime.now()
                    )
                    
                    jobs.append(job)
                    logger.info(f"Scraped: {job.title} at {job.company}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
        finally:
            self.close_driver()
        
        return jobs
    
    def _get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information"""
        try:
            self.driver.get(job_url)
            self.random_delay(2, 3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            description_elem = soup.find('div', class_='show-more-less-html__markup')
            description = description_elem.text.strip() if description_elem else ''
            
            # Extract job type and work mode from description or metadata
            job_type = 'Full-time'
            work_mode = 'Not specified'
            
            if 'remote' in description.lower():
                work_mode = 'Remote'
            elif 'hybrid' in description.lower():
                work_mode = 'Hybrid'
            elif 'on-site' in description.lower() or 'onsite' in description.lower():
                work_mode = 'On-site'
            
            return {
                'description': description,
                'requirements': description,  # Can be further parsed
                'job_type': job_type,
                'work_mode': work_mode,
                'salary': None
            }
        except Exception as e:
            logger.warning(f"Could not get job details: {e}")
            return {}


class IndeedScraper(JobScraper):
    """Scraper for Indeed India"""
    
    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 50) -> List[JobListing]:
        """Scrape jobs from Indeed"""
        logger.info(f"Scraping Indeed for: {keywords} in {location}")
        jobs = []
        
        try:
            self.init_driver()
            
            # Build search URL
            search_url = f"https://www.indeed.co.in/jobs?q={keywords}&l={location}&fromage=1"
            
            self.driver.get(search_url)
            self.random_delay(3, 5)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find job cards (Indeed uses 'job_' id prefix)
            job_cards = soup.find_all('div', class_='job_seen_beacon')[:max_jobs]
            
            for card in job_cards:
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', {'data-testid': 'company-name'})
                    location_elem = card.find('div', {'data-testid': 'text-location'})
                    
                    if not title_elem:
                        continue
                    
                    # Get job link
                    link_elem = title_elem.find('a')
                    job_key = link_elem.get('data-jk', '') if link_elem else ''
                    job_url = f"https://www.indeed.co.in/viewjob?jk={job_key}" if job_key else ''
                    
                    # Get snippet/description
                    snippet_elem = card.find('div', class_='job-snippet')
                    description = snippet_elem.text.strip() if snippet_elem else ''
                    
                    job = JobListing(
                        job_id=f"indeed_{job_key}",
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip() if company_elem else 'Not specified',
                        location=location_elem.text.strip() if location_elem else location,
                        job_type='Full-time',
                        work_mode='Not specified',
                        salary=None,
                        description=description,
                        requirements=description,
                        posted_date='',
                        apply_url=job_url,
                        source='indeed',
                        scraped_at=datetime.now()
                    )
                    
                    jobs.append(job)
                    logger.info(f"Scraped: {job.title} at {job.company}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        finally:
            self.close_driver()
        
        return jobs


class NaukriScraper(JobScraper):
    """Scraper for Naukri.com (India's largest job portal)"""
    
    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 50) -> List[JobListing]:
        """Scrape jobs from Naukri"""
        logger.info(f"Scraping Naukri for: {keywords} in {location}")
        jobs = []
        
        try:
            self.init_driver()
            
            # Build search URL
            keywords_url = keywords.replace(' ', '-')
            search_url = f"https://www.naukri.com/{keywords_url}-jobs"
            
            self.driver.get(search_url)
            self.random_delay(3, 5)
            
            # Scroll to load more jobs
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('article', class_='jobTuple')[:max_jobs]
            
            for card in job_cards:
                try:
                    title_elem = card.find('a', class_='title')
                    company_elem = card.find('a', class_='subTitle')
                    experience_elem = card.find('span', class_='expwdth')
                    location_elem = card.find('span', class_='locWdth')
                    description_elem = card.find('div', class_='job-description')
                    
                    if not title_elem:
                        continue
                    
                    job_url = title_elem.get('href', '')
                    if not job_url.startswith('http'):
                        job_url = f"https://www.naukri.com{job_url}"
                    
                    job_id = job_url.split('/')[-1].split('?')[0]
                    
                    job = JobListing(
                        job_id=f"naukri_{job_id}",
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip() if company_elem else 'Not specified',
                        location=location_elem.text.strip() if location_elem else location,
                        job_type='Full-time',
                        work_mode='Not specified',
                        salary=None,
                        description=description_elem.text.strip() if description_elem else '',
                        requirements='',
                        posted_date='',
                        apply_url=job_url,
                        source='naukri',
                        scraped_at=datetime.now()
                    )
                    
                    jobs.append(job)
                    logger.info(f"Scraped: {job.title} at {job.company}")
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Naukri scraping error: {e}")
        finally:
            self.close_driver()
        
        return jobs


class MultiPlatformScraper:
    """Orchestrates scraping across multiple platforms"""
    
    def __init__(self, headless: bool = True):
        self.scrapers = {
            'linkedin': LinkedInScraper(headless),
            'indeed': IndeedScraper(headless),
            'naukri': NaukriScraper(headless),
        }
    
    def scrape_all_platforms(
        self,
        keywords: str,
        location: str,
        platforms: List[str] = None,
        max_jobs_per_platform: int = 50
    ) -> List[JobListing]:
        """Scrape jobs from all specified platforms"""
        
        if platforms is None:
            platforms = list(self.scrapers.keys())
        
        all_jobs = []
        
        for platform in platforms:
            if platform not in self.scrapers:
                logger.warning(f"Unknown platform: {platform}")
                continue
            
            try:
                scraper = self.scrapers[platform]
                jobs = scraper.scrape_jobs(keywords, location, max_jobs_per_platform)
                all_jobs.extend(jobs)
                logger.info(f"Scraped {len(jobs)} jobs from {platform}")
                
                # Delay between platforms
                time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"Error scraping {platform}: {e}")
        
        # Remove duplicates based on title and company
        unique_jobs = self._remove_duplicates(all_jobs)
        logger.info(f"Total unique jobs scraped: {len(unique_jobs)}")
        
        return unique_jobs
    
    def _remove_duplicates(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate job listings"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a signature based on title and company
            signature = f"{job.title.lower()}_{job.company.lower()}"
            if signature not in seen:
                seen.add(signature)
                unique_jobs.append(job)
        
        return unique_jobs