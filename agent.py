"""
Main AI Agent - Orchestrates the entire job application workflow
Modified to use OpenAI GPT API
"""
import time
import schedule
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger
import json

from config import (
    DEFAULT_USER_PROFILE, DEFAULT_AGENT_CONFIG,
    DATA_DIR, APPLICATIONS_DIR, JOBS_DIR, LOGGING_CONFIG
)
from resume_parser import ResumeParser, ParsedResume
from job_scraper import MultiPlatformScraper, JobListing
from job_matcher import JobMatcher, JobMatch
from cover_letter_generator import CoverLetterGenerator, CoverLetterOptimizer
from application_automator import ApplicationAutomator, ApplicationTracker


class JobApplicationAgent:
    """Main AI agent that orchestrates automated job applications"""
    
    def __init__(
        self,
        openai_api_key: str,
        user_profile=None,
        agent_config=None
    ):
        # Initialize configuration
        self.user_profile = user_profile or DEFAULT_USER_PROFILE
        self.config = agent_config or DEFAULT_AGENT_CONFIG
        
        # Setup logging
        logger.add(
            DATA_DIR / "logs" / "agent_{time}.log",
            **LOGGING_CONFIG
        )
        
        logger.info("Initializing Job Application Agent with OpenAI GPT...")
        
        # Initialize components with OpenAI
        self.resume_parser = ResumeParser(openai_api_key, model=self.config.model)
        self.job_scraper = MultiPlatformScraper(headless=self.config.headless)
        self.job_matcher = JobMatcher(
            openai_api_key,
            similarity_threshold=self.config.similarity_threshold,
            model=self.config.model
        )
        self.cover_letter_generator = CoverLetterGenerator(openai_api_key, model=self.config.model)
        self.cover_letter_optimizer = CoverLetterOptimizer(openai_api_key, model=self.config.model)
        self.application_automator = ApplicationAutomator(headless=self.config.headless)
        self.application_tracker = ApplicationTracker(self.config.db_path)
        
        # State
        self.parsed_resume: Optional[ParsedResume] = None
        self.scraped_jobs: List[JobListing] = []
        self.matched_jobs: List[JobMatch] = []
        
        logger.info("Agent initialized successfully with GPT-3.5-turbo")
    
    def load_and_parse_resume(self, resume_path: str) -> ParsedResume:
        """Step 1: Load and parse resume"""
        logger.info("=" * 50)
        logger.info("STEP 1: Loading and parsing resume")
        logger.info("=" * 50)
        
        self.parsed_resume = self.resume_parser.parse_resume(resume_path)
        
        logger.info(f"Parsed resume for: {self.parsed_resume.name}")
        logger.info(f"Experience: {self.parsed_resume.total_experience_years} years")
        logger.info(f"Skills: {len(self.parsed_resume.skills)} identified")
        
        # Save parsed resume
        resume_json_path = DATA_DIR / "parsed_resume.json"
        with open(resume_json_path, 'w') as f:
            json.dump({
                'name': self.parsed_resume.name,
                'email': self.parsed_resume.email,
                'phone': self.parsed_resume.phone,
                'location': self.parsed_resume.location,
                'summary': self.parsed_resume.summary,
                'skills': self.parsed_resume.skills,
                'experience': self.parsed_resume.experience,
                'education': self.parsed_resume.education,
                'total_experience_years': self.parsed_resume.total_experience_years
            }, f, indent=2)
        
        logger.info(f"Resume data saved to: {resume_json_path}")
        
        return self.parsed_resume
    
    def scrape_jobs(
        self,
        platforms: List[str] = None,
        keywords: str = None,
        location: str = None,
        max_jobs_total: int = None
    ) -> List[JobListing]:
        """Step 2: Scrape jobs from multiple platforms"""
        logger.info("=" * 50)
        logger.info("STEP 2: Scraping jobs from platforms")
        logger.info("=" * 50)
        
        if not self.parsed_resume:
            raise ValueError("Resume not parsed. Call load_and_parse_resume() first.")
        
        # Use profile settings if not specified
        if platforms is None:
            platforms = ['linkedin', 'indeed', 'naukri']
        
        if keywords is None:
            # Use job titles from profile or infer from resume
            keywords = self.user_profile.job_titles[0] if self.user_profile.job_titles else "data scientist"
        
        if location is None:
            location = self.parsed_resume.location or "India"
        
        logger.info(f"Searching for: {keywords}")
        logger.info(f"Location: {location}")
        logger.info(f"Platforms: {', '.join(platforms)}")
        
        if max_jobs_total:
            max_per_platform = max_jobs_total // len(platforms)
        else:
            max_per_platform = self.config.max_jobs_per_board

        self.scraped_jobs = self.job_scraper.scrape_all_platforms(
            keywords=keywords,
            location=location,
            platforms=platforms,
            max_jobs_per_platform=max_per_platform
        )
        
        logger.info(f"Total jobs scraped: {len(self.scraped_jobs)}")
        
        # Save scraped jobs
        jobs_json_path = JOBS_DIR / f"scraped_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(jobs_json_path, 'w', encoding='utf-8') as f:
            json.dump([job.to_dict() for job in self.scraped_jobs], f, indent=2, default=str)
        
        logger.info(f"Jobs data saved to: {jobs_json_path}")
        
        return self.scraped_jobs
    
    def match_jobs(self, top_k: int = 20) -> List[JobMatch]:
        """Step 3: Match jobs with resume"""
        logger.info("=" * 50)
        logger.info("STEP 3: Matching jobs with resume")
        logger.info("=" * 50)

        if not self.parsed_resume:
            raise ValueError("Resume not parsed.")

        # Gracefully handle cases where scraping returned no jobs
        if not self.scraped_jobs:
            logger.warning("No jobs scraped; skipping job matching step.")
            self.matched_jobs = []
            return self.matched_jobs

        self.matched_jobs = self.job_matcher.match_jobs(
            resume=self.parsed_resume,
            jobs=self.scraped_jobs,
            top_k=top_k
        )
        
        logger.info(f"Found {len(self.matched_jobs)} matching jobs")
        
        # Generate match report
        report_path = APPLICATIONS_DIR / f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.job_matcher.create_match_report(
            self.parsed_resume,
            self.matched_jobs,
            str(report_path)
        )
        
        # Save matches as JSON
        matches_json_path = APPLICATIONS_DIR / f"matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(matches_json_path, 'w', encoding='utf-8') as f:
            json.dump([{
                'job': match.job.to_dict(),
                'match_score': match.match_score,
                'skill_match_percentage': match.skill_match_percentage,
                'reasoning': match.reasoning,
                'matching_skills': match.matching_skills,
                'missing_skills': match.missing_skills
            } for match in self.matched_jobs], f, indent=2, default=str)
        
        return self.matched_jobs
    
    def generate_cover_letters(
        self,
        matches: List[JobMatch] = None,
        num_letters: int = 10
    ) -> Dict[str, str]:
        """Step 4: Generate cover letters for top matches"""
        logger.info("=" * 50)
        logger.info("STEP 4: Generating cover letters")
        logger.info("=" * 50)
        
        if matches is None:
            matches = self.matched_jobs[:num_letters]
        
        if not self.parsed_resume:
            raise ValueError("Resume not parsed.")
        
        cover_letters = {}
        
        for i, match in enumerate(matches, 1):
            logger.info(f"Generating cover letter {i}/{len(matches)} for: {match.job.title}")
            
            try:
                # Generate cover letter
                cover_letter = self.cover_letter_generator.generate_cover_letter(
                    resume=self.parsed_resume,
                    job=match.job,
                    tone="professional"
                )
                
                # Optimize for ATS
                optimized_letter = self.cover_letter_optimizer.optimize_for_ats(
                    cover_letter=cover_letter,
                    job=match.job
                )
                
                # Save to file
                cover_letter_path = self.cover_letter_generator.save_cover_letter(
                    optimized_letter,
                    match.job,
                    APPLICATIONS_DIR / "cover_letters"
                )
                
                cover_letters[match.job.job_id] = cover_letter_path
                
                # Rate limiting for free tier
                time.sleep(3)  # Increased delay for free tier
                
            except Exception as e:
                logger.error(f"Failed to generate cover letter: {e}")
                continue
        
        logger.info(f"Generated {len(cover_letters)} cover letters")
        
        return cover_letters
    
    def apply_to_jobs(
        self,
        matches: List[JobMatch] = None,
        max_applications: int = 10,
        resume_path: str = None,
        auto_submit: bool = False
    ) -> List[Dict]:
        """Step 5: Apply to jobs (with safety checks)"""
        logger.info("=" * 50)
        logger.info("STEP 5: Applying to jobs")
        logger.info("=" * 50)
        
        if matches is None:
            matches = self.matched_jobs[:max_applications]
        
        if resume_path is None:
            resume_path = self.user_profile.resume_path
        
        if not auto_submit:
            logger.warning("Auto-submit is disabled. Applications will be prepared but not submitted.")
        
        application_results = []
        
        for i, match in enumerate(matches, 1):
            logger.info(f"Processing application {i}/{len(matches)}: {match.job.title}")
            
            try:
                # Get cover letter path
                cover_letter_path = APPLICATIONS_DIR / "cover_letters" / f"cover_letter_{match.job.company}_{match.job.job_id}.txt"
                
                # Apply to job
                result = self.application_automator.apply_to_job(
                    job=match.job,
                    resume=self.parsed_resume,
                    resume_path=resume_path,
                    cover_letter_path=str(cover_letter_path) if cover_letter_path.exists() else None
                )
                
                result['match_score'] = match.match_score
                result['source'] = match.job.source
                
                # Track application
                self.application_tracker.add_application(result)
                
                application_results.append(result)
                
                # Rate limiting
                time.sleep(self.config.delay_between_applications)
                
            except Exception as e:
                logger.error(f"Application failed: {e}")
                application_results.append({
                    'success': False,
                    'job_id': match.job.job_id,
                    'error': str(e)
                })
        
        # Save results
        results_path = APPLICATIONS_DIR / f"application_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(application_results, f, indent=2, default=str)
        
        logger.info(f"Application results saved to: {results_path}")
        
        # Print summary
        successful = sum(1 for r in application_results if r.get('success'))
        logger.info(f"Applications summary: {successful}/{len(application_results)} successful")
        
        return application_results
    
    def run_full_pipeline(
        self,
        resume_path: str,
        platforms: List[str] = None,
        max_applications: int = 10,
        auto_submit: bool = False
    ):
        """Run the complete job application pipeline"""
        logger.info("=" * 70)
        logger.info("STARTING FULL JOB APPLICATION PIPELINE (OpenAI GPT)")
        logger.info("=" * 70)
        
        start_time = time.time()
        
        try:
            # Step 1: Parse resume
            self.load_and_parse_resume(resume_path)
            
            # Step 2: Scrape jobs
            self.scrape_jobs(platforms=platforms, max_jobs_total=max_applications * 3)
            
            # Step 3: Match jobs
            self.match_jobs(top_k=50)
            
            # Step 4: Generate cover letters
            self.generate_cover_letters(num_letters=max_applications)
            
            # Step 5: Apply to jobs
            results = self.apply_to_jobs(
                max_applications=max_applications,
                resume_path=resume_path,
                auto_submit=auto_submit
            )
            
            elapsed_time = time.time() - start_time
            
            logger.info("=" * 70)
            logger.info(f"PIPELINE COMPLETED in {elapsed_time:.2f} seconds")
            logger.info("=" * 70)
            
            # Get stats
            stats = self.application_tracker.get_application_stats()
            logger.info(f"Total applications tracked: {stats['total_applications']}")
            logger.info(f"Average match score: {stats['average_match_score']:.2%}")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def schedule_recurring_jobs(
        self,
        resume_path: str,
        interval_hours: int = 6
    ):
        """Schedule recurring job scraping and application"""
        logger.info(f"Scheduling job pipeline to run every {interval_hours} hours")
        
        def job():
            self.run_full_pipeline(
                resume_path=resume_path,
                max_applications=self.user_profile.max_applications_per_day,
                auto_submit=self.user_profile.auto_apply
            )
        
        schedule.every(interval_hours).hours.do(job)
        
        # Run once immediately
        job()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)


# CLI Interface
def main():
    """Command-line interface for the agent"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='AI Job Application Agent (OpenAI GPT)')
    parser.add_argument('--resume', required=True, help='Path to resume PDF')
    parser.add_argument('--api-key', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--platforms', nargs='+', default=['linkedin', 'indeed', 'naukri'],
                       help='Job platforms to scrape')
    parser.add_argument('--max-apps', type=int, default=10, help='Maximum applications')
    parser.add_argument('--auto-submit', action='store_true', help='Automatically submit applications')
    parser.add_argument('--schedule', type=int, help='Run every N hours')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key required. Use --api-key or set OPENAI_API_KEY environment variable")
    
    # Create agent
    agent = JobApplicationAgent(openai_api_key=api_key)
    
    # Run
    if args.schedule:
        agent.schedule_recurring_jobs(
            resume_path=args.resume,
            interval_hours=args.schedule
        )
    else:
        agent.run_full_pipeline(
            resume_path=args.resume,
            platforms=args.platforms,
            max_applications=args.max_apps,
            auto_submit=args.auto_submit
        )


if __name__ == "__main__":
    main()