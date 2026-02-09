"""
Job Scraper - Multi-platform job scraping using requests + BeautifulSoup
Uses HTTP requests for scraping (no Selenium dependency for scraping phase).
Selenium is only needed for application submission (application_automator.py).
"""
import time
import random
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import quote_plus
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


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


class LinkedInScraper:
    """Scraper for LinkedIn Jobs using public API (no login required)"""

    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 10) -> List[JobListing]:
        """Scrape jobs from LinkedIn public job search"""
        logger.info(f"Scraping LinkedIn for: {keywords} in {location}")
        jobs = []

        try:
            # LinkedIn public jobs search page (no auth required)
            encoded_kw = quote_plus(keywords)
            encoded_loc = quote_plus(location)
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_kw}&location={encoded_loc}&f_TPR=r86400&position=1&pageNum=0"

            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(search_url, timeout=30)
            logger.info(f"LinkedIn response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"LinkedIn returned status {response.status_code}")
                return jobs

            soup = BeautifulSoup(response.text, 'html.parser')

            # LinkedIn public search uses 'base-card' divs
            job_cards = soup.find_all('div', class_='base-card')[:max_jobs]
            logger.info(f"Found {len(job_cards)} job cards on LinkedIn")

            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    date_elem = card.find('time')

                    if not all([title_elem, company_elem, link_elem]):
                        continue

                    job_url = link_elem.get('href', '')
                    job_id = job_url.split('/')[-1].split('?')[0] if job_url else f"li_{int(time.time())}_{random.randint(1000,9999)}"

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    loc = location_elem.text.strip() if location_elem else location

                    # Get job description from detail page
                    description = self._get_job_description(session, job_url)

                    work_mode = 'Not specified'
                    desc_lower = description.lower()
                    if 'remote' in desc_lower:
                        work_mode = 'Remote'
                    elif 'hybrid' in desc_lower:
                        work_mode = 'Hybrid'
                    elif 'on-site' in desc_lower or 'onsite' in desc_lower:
                        work_mode = 'On-site'

                    job = JobListing(
                        job_id=f"linkedin_{job_id}",
                        title=title,
                        company=company,
                        location=loc,
                        job_type='Full-time',
                        work_mode=work_mode,
                        salary=None,
                        description=description,
                        requirements=description,
                        posted_date=date_elem.get('datetime', '') if date_elem else '',
                        apply_url=job_url,
                        source='linkedin',
                        scraped_at=datetime.now()
                    )
                    jobs.append(job)
                    logger.info(f"Scraped: {title} at {company}")

                    # Small delay between detail page requests
                    time.sleep(random.uniform(1, 2))

                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")

        return jobs

    def _get_job_description(self, session: requests.Session, job_url: str) -> str:
        """Fetch job description from detail page"""
        try:
            if not job_url:
                return ''
            resp = session.get(job_url, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                desc_elem = soup.find('div', class_='show-more-less-html__markup')
                if desc_elem:
                    return desc_elem.get_text(strip=True)[:2000]
                # Fallback: try description section
                desc_section = soup.find('section', class_='description')
                if desc_section:
                    return desc_section.get_text(strip=True)[:2000]
        except Exception as e:
            logger.debug(f"Could not fetch job details: {e}")
        return ''


class IndeedScraper:
    """Scraper for Indeed India"""

    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 10) -> List[JobListing]:
        """Scrape jobs from Indeed India"""
        logger.info(f"Scraping Indeed for: {keywords} in {location}")
        jobs = []

        try:
            encoded_kw = quote_plus(keywords)
            encoded_loc = quote_plus(location)
            search_url = f"https://www.indeed.co.in/jobs?q={encoded_kw}&l={encoded_loc}&fromage=3"

            session = requests.Session()
            session.headers.update(HEADERS)
            response = session.get(search_url, timeout=30)
            logger.info(f"Indeed response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"Indeed returned status {response.status_code}")
                return jobs

            soup = BeautifulSoup(response.text, 'html.parser')

            # Indeed job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')[:max_jobs]

            # Fallback selectors if primary doesn't work
            if not job_cards:
                job_cards = soup.find_all('div', class_='cardOutline')[:max_jobs]
            if not job_cards:
                job_cards = soup.find_all('td', class_='resultContent')[:max_jobs]
            if not job_cards:
                # Try finding jobs by data attributes
                job_cards = soup.find_all('div', {'data-jk': True})[:max_jobs]

            logger.info(f"Found {len(job_cards)} job cards on Indeed")

            for card in job_cards:
                try:
                    title_elem = card.find('h2', class_='jobTitle') or card.find('h2') or card.find('a', {'data-jk': True})
                    company_elem = card.find('span', {'data-testid': 'company-name'}) or card.find('span', class_='companyName')
                    location_elem = card.find('div', {'data-testid': 'text-location'}) or card.find('div', class_='companyLocation')

                    if not title_elem:
                        continue

                    title_text = title_elem.get_text(strip=True)

                    # Get job link
                    link_elem = card.find('a', href=True)
                    job_key = ''
                    if link_elem:
                        href = link_elem.get('href', '')
                        jk_match = re.search(r'jk=([a-f0-9]+)', href)
                        if jk_match:
                            job_key = jk_match.group(1)
                        elif link_elem.get('data-jk'):
                            job_key = link_elem.get('data-jk')
                    if not job_key:
                        job_key = card.get('data-jk', f"indeed_{int(time.time())}_{random.randint(1000,9999)}")

                    job_url = f"https://www.indeed.co.in/viewjob?jk={job_key}" if job_key else ''

                    # Get snippet/description
                    snippet_elem = card.find('div', class_='job-snippet') or card.find('div', class_='snippet')
                    description = snippet_elem.get_text(strip=True) if snippet_elem else title_text

                    job = JobListing(
                        job_id=f"indeed_{job_key}",
                        title=title_text,
                        company=company_elem.get_text(strip=True) if company_elem else 'Not specified',
                        location=location_elem.get_text(strip=True) if location_elem else location,
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
                    logger.info(f"Scraped: {title_text} at {job.company}")

                except Exception as e:
                    logger.warning(f"Error parsing Indeed job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")

        return jobs


class NaukriScraper:
    """Scraper for Naukri.com"""

    def scrape_jobs(self, keywords: str, location: str, max_jobs: int = 10) -> List[JobListing]:
        """Scrape jobs from Naukri"""
        logger.info(f"Scraping Naukri for: {keywords} in {location}")
        jobs = []

        try:
            keywords_url = keywords.replace(' ', '-')
            search_url = f"https://www.naukri.com/{keywords_url}-jobs"

            session = requests.Session()
            session.headers.update(HEADERS)
            session.headers['Referer'] = 'https://www.naukri.com/'
            response = session.get(search_url, timeout=30)
            logger.info(f"Naukri response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"Naukri returned status {response.status_code}")
                return jobs

            soup = BeautifulSoup(response.text, 'html.parser')

            # Naukri job cards - try multiple selectors
            job_cards = soup.find_all('article', class_='jobTuple')[:max_jobs]
            if not job_cards:
                job_cards = soup.find_all('div', class_='srp-jobtuple-wrapper')[:max_jobs]
            if not job_cards:
                job_cards = soup.find_all('div', class_='cust-job-tuple')[:max_jobs]
            if not job_cards:
                # Try finding by data attributes or other patterns
                job_cards = soup.find_all('div', attrs={'data-job-id': True})[:max_jobs]

            # If still no cards, try parsing embedded JSON data
            if not job_cards:
                jobs = self._parse_from_script_data(soup, max_jobs)
                if jobs:
                    return jobs

            logger.info(f"Found {len(job_cards)} job cards on Naukri")

            for card in job_cards:
                try:
                    title_elem = card.find('a', class_='title') or card.find('a', class_='job-title-href')
                    company_elem = card.find('a', class_='subTitle') or card.find('a', class_='comp-name')
                    location_elem = card.find('span', class_='locWdth') or card.find('span', class_='loc-wrap')
                    description_elem = card.find('div', class_='job-description') or card.find('div', class_='job-desc')

                    if not title_elem:
                        continue

                    job_url = title_elem.get('href', '')
                    if job_url and not job_url.startswith('http'):
                        job_url = f"https://www.naukri.com{job_url}"

                    job_id = job_url.split('/')[-1].split('?')[0] if job_url else f"nk_{int(time.time())}_{random.randint(1000,9999)}"

                    job = JobListing(
                        job_id=f"naukri_{job_id}",
                        title=title_elem.get_text(strip=True),
                        company=company_elem.get_text(strip=True) if company_elem else 'Not specified',
                        location=location_elem.get_text(strip=True) if location_elem else location,
                        job_type='Full-time',
                        work_mode='Not specified',
                        salary=None,
                        description=description_elem.get_text(strip=True) if description_elem else '',
                        requirements='',
                        posted_date='',
                        apply_url=job_url,
                        source='naukri',
                        scraped_at=datetime.now()
                    )
                    jobs.append(job)
                    logger.info(f"Scraped: {job.title} at {job.company}")

                except Exception as e:
                    logger.warning(f"Error parsing Naukri job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"Naukri scraping error: {e}")

        return jobs

    def _parse_from_script_data(self, soup: BeautifulSoup, max_jobs: int) -> List[JobListing]:
        """Try to extract job data from embedded JSON/script tags"""
        jobs = []
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                        job = self._parse_ld_json(data)
                        if job:
                            jobs.append(job)
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') == 'JobPosting':
                                job = self._parse_ld_json(item)
                                if job:
                                    jobs.append(job)
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception:
            pass
        return jobs[:max_jobs]

    def _parse_ld_json(self, data: dict) -> Optional[JobListing]:
        """Parse a JSON-LD JobPosting into a JobListing"""
        try:
            title = data.get('title', '')
            company = ''
            if isinstance(data.get('hiringOrganization'), dict):
                company = data['hiringOrganization'].get('name', '')
            location = ''
            if isinstance(data.get('jobLocation'), dict):
                addr = data['jobLocation'].get('address', {})
                if isinstance(addr, dict):
                    location = addr.get('addressLocality', addr.get('addressRegion', ''))
            url = data.get('url', '')
            desc = data.get('description', '')
            # Strip HTML
            desc = BeautifulSoup(desc, 'html.parser').get_text(strip=True)[:2000] if desc else ''

            return JobListing(
                job_id=f"naukri_{hash(url) % 100000}",
                title=title,
                company=company,
                location=location,
                job_type=data.get('employmentType', 'Full-time'),
                work_mode='Not specified',
                salary=None,
                description=desc,
                requirements=desc,
                posted_date=data.get('datePosted', ''),
                apply_url=url,
                source='naukri',
                scraped_at=datetime.now()
            )
        except Exception:
            return None


class MultiPlatformScraper:
    """Orchestrates scraping across multiple platforms"""

    def __init__(self, headless: bool = True):
        self.scrapers = {
            'linkedin': LinkedInScraper(),
            'indeed': IndeedScraper(),
            'naukri': NaukriScraper(),
        }

    def scrape_all_platforms(
        self,
        keywords: str,
        location: str,
        platforms: List[str] = None,
        max_jobs_per_platform: int = 10
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
                time.sleep(random.uniform(2, 4))

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
            signature = f"{job.title.lower()}_{job.company.lower()}"
            if signature not in seen:
                seen.add(signature)
                unique_jobs.append(job)

        return unique_jobs
