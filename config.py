"""
Configuration file for the AI Job Application Agent
Modified to use OpenAI GPT API
"""
import os
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Optional

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
RESUMES_DIR = DATA_DIR / "resumes"
APPLICATIONS_DIR = DATA_DIR / "applications"
JOBS_DIR = DATA_DIR / "jobs"

# Create directories if they don't exist
for dir_path in [DATA_DIR, LOGS_DIR, RESUMES_DIR, APPLICATIONS_DIR, JOBS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# API Configuration - Changed to OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Job Board URLs - India Focused
JOB_BOARDS = {
    "linkedin": {
        "base_url": "https://www.linkedin.com/jobs/search/",
        "search_params": {
            "keywords": "data scientist",
            "location": "India",
            "f_TPR": "r86400",  # Last 24 hours
            "f_JT": "F",  # Full-time
        }
    },
    "indeed": {
        "base_url": "https://www.indeed.co.in/jobs",
        "search_params": {
            "q": "data scientist",
            "l": "India",
            "fromage": "1",  # Last 1 day
        }
    },
    "glassdoor": {
        "base_url": "https://www.glassdoor.co.in/Job/jobs.htm",
        "search_params": {
            "sc.keyword": "data scientist",
            "locT": "N",
            "locId": "115",  # India
        }
    },
    "naukri": {
        "base_url": "https://www.naukri.com/data-scientist-jobs",
        "search_params": {
            "k": "data scientist",
            "l": "India",
        }
    },
    "shine": {
        "base_url": "https://www.shine.com/job-search/data-scientist-jobs",
        "search_params": {
            "q": "data scientist",
            "loc": "India",
        }
    },
    "instahyre": {
        "base_url": "https://www.instahyre.com/search-jobs/",
        "search_params": {
            "job_title": "data scientist",
        }
    },
    "foundit": {  # Previously Monster India
        "base_url": "https://www.foundit.in/srp/results",
        "search_params": {
            "query": "data scientist",
            "locations": "India",
        }
    }
}

# User Profile Configuration
class UserProfile(BaseModel):
    name: str = "Arpit Pandey"
    email: str = "arpitpandey6599@gmail.com"
    phone: str = "+91-8359808703"
    location: str = "India"
    
    # Job Preferences
    job_titles: List[str] = [
        "Data Scientist",
        "Senior Data Scientist",
        "ML Engineer",
        "Machine Learning Engineer",
        "GenAI Engineer",
        "AI/ML Scientist"
    ]
    
    skills: List[str] = [
        "Python", "Machine Learning", "Deep Learning",
        "Generative AI", "LLMs", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Scikit-learn",
        "SQL", "AWS", "Docker", "Git"
    ]
    
    locations: List[str] = [
        "Bangalore", "Mumbai", "Pune", "Hyderabad",
        "Delhi", "Gurgaon", "Noida", "Chennai", "Remote"
    ]
    
    experience_years: int = 4
    expected_salary_min: Optional[int] = 27  # in LPA
    expected_salary_max: Optional[int] = 50
    
    # Application preferences
    auto_apply: bool = False  # Set to True for full automation
    apply_with_cover_letter: bool = True
    max_applications_per_day: int = 50
    
    # Filters
    job_types: List[str] = ["Full-time", "Contract"]
    work_modes: List[str] = ["Remote", "Hybrid", "On-site"]
    
    # Resume path
    resume_path: str = str(RESUMES_DIR / "resume.pdf")


# Agent Configuration - Modified for OpenAI
class AgentConfig(BaseModel):
    # Changed to use GPT-3.5-turbo for free tier compatibility
    model: str = "gpt-3.5-turbo"  # Most cost-effective model
    temperature: float = 0.7
    max_tokens: int = 2048  # Reduced for cost optimization
    
    # Scraping configuration
    scrape_interval_hours: int = 6
    max_jobs_per_board: int = 100
    
    # Matching configuration
    similarity_threshold: float = 0.5  # For job-resume matching
    
    # Rate limiting - More conservative for free tier
    requests_per_minute: int = 3  # Lower for free tier
    delay_between_applications: int = 60  # seconds
    
    # Headless browser
    headless: bool = True
    
    # Database
    db_path: str = str(DATA_DIR / "job_applications.db")


# Initialize default configs
DEFAULT_USER_PROFILE = UserProfile()
DEFAULT_AGENT_CONFIG = AgentConfig()

# Logging configuration
LOGGING_CONFIG = {
    "rotation": "500 MB",
    "retention": "10 days",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "level": "INFO"
}