"""
Application Automation - Automate job application submissions
"""
import time
import random
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger
from pathlib import Path

from resume_parser import ParsedResume
from job_scraper import JobListing


class ApplicationAutomator:
    """Automate job application form filling and submission"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        
    def init_driver(self):
        """Initialize WebDriver"""
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def apply_to_job(
        self,
        job: JobListing,
        resume: ParsedResume,
        resume_path: str,
        cover_letter_path: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Apply to a job posting
        Returns: Dict with status and details
        """
        logger.info(f"Starting application for: {job.title} at {job.company}")
        
        result = {
            'success': False,
            'job_id': job.job_id,
            'job_title': job.title,
            'company': job.company,
            'applied_at': None,
            'error': None
        }
        
        try:
            self.init_driver()
            
            # Route to appropriate handler based on job source
            if job.source == 'linkedin':
                result = self._apply_linkedin(job, resume, resume_path, cover_letter_path)
            elif job.source == 'indeed':
                result = self._apply_indeed(job, resume, resume_path, cover_letter_path)
            elif job.source == 'naukri':
                result = self._apply_naukri(job, resume, resume_path, cover_letter_path)
            else:
                result['error'] = f"Unsupported job source: {job.source}"
                
        except Exception as e:
            logger.error(f"Application error: {e}")
            result['error'] = str(e)
        finally:
            if self.driver:
                self.driver.quit()
        
        return result
    
    def _apply_linkedin(
        self,
        job: JobListing,
        resume: ParsedResume,
        resume_path: str,
        cover_letter_path: Optional[str]
    ) -> Dict:
        """Apply to LinkedIn job (requires login)"""
        logger.info("LinkedIn application - Manual login required")
        
        self.driver.get(job.apply_url)
        time.sleep(3)
        
        # Check if user needs to login
        if "login" in self.driver.current_url.lower():
            logger.warning("LinkedIn requires login. Please login manually.")
            input("Press Enter after you've logged in...")
        
        try:
            # Multiple selectors for Easy Apply button
            easy_apply_selectors = [
                "//button[contains(@class, 'jobs-apply-button')]",
                "//button[contains(text(), 'Easy Apply')]",
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(@class, 'jobs-apply') and contains(@class, 'artdeco-button')]",
                "//button[contains(@class, 'jobs-s-apply')]",
                "//button[@aria-label='Easy Apply']"
            ]
            
            easy_apply_btn = None
            for selector in easy_apply_selectors:
                try:
                    easy_apply_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logger.info(f"Found Easy Apply button with selector: {selector}")
                    break
                except:
                    continue
            
            if not easy_apply_btn:
                logger.warning("Could not find Easy Apply button - job may require external application")
                try:
                    external_link = self.driver.find_element(By.XPATH, 
                        "//a[contains(@href, 'applyUrl') or contains(text(), 'Apply on company website')]"
                    )
                    external_url = external_link.get_attribute('href')
                    
                    logger.info(f"External application URL found: {external_url}")
                    
                    return {
                        'success': False,
                        'job_id': job.job_id,
                        'job_title': job.title,
                        'company': job.company,
                        'error': 'Requires external application',
                        'external_url': external_url,
                        'note': 'Visit this URL to apply manually'
                    }
                except:
                    return {
                        'success': False,
                        'job_id': job.job_id,
                        'error': 'Easy Apply not available'
                    }
            
            easy_apply_btn.click()
            time.sleep(2)
            
            # Fill application form
            self._fill_linkedin_form(resume, resume_path)
            
            return {
                'success': True,
                'job_id': job.job_id,
                'job_title': job.title,
                'company': job.company,
                'applied_at': time.time(),
                'error': None
            }
            
        except Exception as e:
            logger.warning(f"Application error: {e}")
            return {
                'success': False,
                'job_id': job.job_id,
                'error': str(e)
            }
    
    def _fill_linkedin_form(self, resume: ParsedResume, resume_path: str):
        """Fill LinkedIn Easy Apply form"""
        try:
            # Phone number
            phone_fields = self.driver.find_elements(By.XPATH, "//input[@type='tel' or contains(@id, 'phone')]")
            for field in phone_fields:
                if field.is_displayed():
                    field.clear()
                    field.send_keys(resume.phone)
            
            # Resume upload
            resume_upload = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if resume_upload:
                resume_upload[0].send_keys(str(Path(resume_path).absolute()))
                time.sleep(2)
            
            # Handle multi-step forms
            max_steps = 10
            for step in range(max_steps):
                try:
                    # Look for "Next" button
                    next_btn = self.driver.find_element(
                        By.XPATH,
                        "//button[contains(@aria-label, 'Continue') or contains(text(), 'Next')]"
                    )
                    
                    if next_btn.is_displayed() and next_btn.is_enabled():
                        next_btn.click()
                        time.sleep(2)
                    else:
                        break
                        
                except NoSuchElementException:
                    # No more next buttons - try to find submit
                    break
            
            # Submit or Review
            submit_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label, 'Submit') or contains(text(), 'Submit application')]"
            )
            
            if submit_buttons:
                logger.info("Found submit button - Application ready to submit")
                # In production, would click submit here
                # submit_buttons[0].click()
                logger.warning("DEMO MODE - Not actually submitting")
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
    
    def _apply_indeed(
        self,
        job: JobListing,
        resume: ParsedResume,
        resume_path: str,
        cover_letter_path: Optional[str]
    ) -> Dict:
        """Apply to Indeed job"""
        logger.info("Indeed application")
        
        self.driver.get(job.apply_url)
        time.sleep(3)
        
        try:
            # Look for "Apply Now" button
            apply_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply now')]"))
            )
            apply_btn.click()
            time.sleep(2)
            
            # Fill form fields
            self._fill_indeed_form(resume, resume_path)
            
            return {
                'success': True,
                'job_id': job.job_id,
                'job_title': job.title,
                'company': job.company,
                'applied_at': time.time(),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Indeed application error: {e}")
            return {
                'success': False,
                'job_id': job.job_id,
                'error': str(e)
            }
    
    def _fill_indeed_form(self, resume: ParsedResume, resume_path: str):
        """Fill Indeed application form"""
        try:
            # Name
            name_field = self.driver.find_elements(By.NAME, "name")
            if name_field and name_field[0].is_displayed():
                name_field[0].send_keys(resume.name)
            
            # Email
            email_field = self.driver.find_elements(By.NAME, "email")
            if email_field and email_field[0].is_displayed():
                email_field[0].send_keys(resume.email)
            
            # Phone
            phone_field = self.driver.find_elements(By.NAME, "phone")
            if phone_field and phone_field[0].is_displayed():
                phone_field[0].send_keys(resume.phone)
            
            # Resume upload
            resume_upload = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if resume_upload:
                resume_upload[0].send_keys(str(Path(resume_path).absolute()))
                time.sleep(2)
            
            logger.info("Indeed form filled successfully")
            
        except Exception as e:
            logger.error(f"Error filling Indeed form: {e}")
    
    def _apply_naukri(
        self,
        job: JobListing,
        resume: ParsedResume,
        resume_path: str,
        cover_letter_path: Optional[str]
    ) -> Dict:
        """Apply to Naukri job"""
        logger.info("Naukri application")
        
        self.driver.get(job.apply_url)
        time.sleep(3)
        
        try:
            # Naukri typically requires login
            if "login" in self.driver.current_url.lower():
                logger.warning("Naukri requires login")
                return {
                    'success': False,
                    'job_id': job.job_id,
                    'error': 'Login required'
                }
            
            # Look for apply button
            apply_btn = self.driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Apply')] | //a[contains(text(), 'Apply')]"
            )
            
            if apply_btn:
                apply_btn[0].click()
                time.sleep(2)
                
                logger.info("Naukri application initiated")
                return {
                    'success': True,
                    'job_id': job.job_id,
                    'job_title': job.title,
                    'company': job.company,
                    'applied_at': time.time(),
                    'error': None
                }
            
        except Exception as e:
            logger.error(f"Naukri application error: {e}")
            return {
                'success': False,
                'job_id': job.job_id,
                'error': str(e)
            }


class ApplicationTracker:
    """Track application status and history"""
    
    def __init__(self, db_path: str):
        import sqlite3
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for tracking"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                job_title TEXT,
                company TEXT,
                source TEXT,
                applied_at TIMESTAMP,
                status TEXT,
                match_score REAL,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_application(self, application_data: Dict):
        """Add application to tracking database"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO applications 
                (job_id, job_title, company, source, applied_at, status, match_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                application_data.get('job_id'),
                application_data.get('job_title'),
                application_data.get('company'),
                application_data.get('source'),
                datetime.now(),
                'Applied',
                application_data.get('match_score'),
                application_data.get('notes', '')
            ))
            
            conn.commit()
            logger.info(f"Added application to tracker: {application_data.get('job_id')}")
            
        except sqlite3.IntegrityError:
            logger.warning(f"Application already tracked: {application_data.get('job_id')}")
        finally:
            conn.close()
    
    def get_application_stats(self) -> Dict:
        """Get application statistics"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM applications")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Applied'")
        applied = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(match_score) FROM applications")
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_applications': total,
            'applied': applied,
            'average_match_score': avg_score
        }