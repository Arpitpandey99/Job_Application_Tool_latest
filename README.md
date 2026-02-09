# AI Job Application Agent 🤖

An advanced, agentic AI system that automates the entire job application process using Claude AI. Built specifically for Data Scientists targeting jobs in India across multiple platforms.

## 🌟 Features

### Core Capabilities
- **Resume Parsing**: Automatically extracts and structures information from your resume
- **Multi-Platform Scraping**: Scrapes jobs from LinkedIn, Indeed, Naukri, Shine, Instahyre, and more
- **AI-Powered Matching**: Uses semantic similarity + ML to match jobs with your profile
- **Cover Letter Generation**: Creates personalized, ATS-optimized cover letters for each job
- **Application Automation**: Automates form filling and application submission
- **Application Tracking**: SQLite database to track all applications and their status

### Advanced Features
- **Agentic Workflow**: Fully autonomous end-to-end pipeline
- **Anti-Detection Measures**: Sophisticated scraping with human-like behavior
- **Scheduled Execution**: Run automatically every N hours
- **Web Dashboard**: Beautiful React dashboard for monitoring and control
- **Skill Matching**: Identifies matching skills and gaps for each position
- **ATS Optimization**: Optimizes cover letters for Applicant Tracking Systems

## 🏗️ Architecture

```
┌─────────────────┐
│  Resume Parser  │ ──> Extracts structured data from resume
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Job Scraper    │ ──> Scrapes from LinkedIn, Indeed, Naukri, etc.
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Job Matcher    │ ──> ML-based semantic matching
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Cover Letter    │ ──> AI-generated personalized letters
│   Generator     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Application    │ ──> Automated form filling & submission
│   Automator     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Tracker DB     │ ──> SQLite database for tracking
└─────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.9+
- Chrome/Chromium browser
- ChromeDriver (for Selenium)
- Anthropic API key

### Setup

1. **Clone or download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download spaCy model** (optional, for enhanced NLP)
```bash
python -m spacy download en_core_web_sm
```

4. **Set up environment variables**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

5. **Install ChromeDriver**
```bash
# On Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# On macOS with Homebrew
brew install chromedriver

# Or download from: https://chromedriver.chromium.org/
```

## 🚀 Quick Start

### Basic Usage

```python
from agent import JobApplicationAgent

# Initialize the agent
agent = JobApplicationAgent(
    anthropic_api_key="your-api-key"
)

# Run the full pipeline
results = agent.run_full_pipeline(
    resume_path="/path/to/your/resume.pdf",
    platforms=['linkedin', 'indeed', 'naukri'],
    max_applications=10,
    auto_submit=False  # Set to True for automatic submission
)
```

### Command Line Interface

```bash
# Basic run
python agent.py --resume resume.pdf --max-apps 10

# With specific platforms
python agent.py --resume resume.pdf --platforms linkedin indeed naukri

# Scheduled execution (every 6 hours)
python agent.py --resume resume.pdf --schedule 6 --max-apps 50

# Enable auto-submit (be careful!)
python agent.py --resume resume.pdf --auto-submit --max-apps 5
```

## 📊 Web Dashboard

Launch the dashboard to monitor and control the agent:

```bash
# Simply open the HTML file in your browser
open dashboard.html
```

The dashboard provides:
- Real-time statistics
- Job matching results
- Application tracking
- Configuration management
- Activity timeline

## 🔧 Configuration

Edit `config.py` to customize:

```python
# User Profile
DEFAULT_USER_PROFILE = UserProfile(
    name="Your Name",
    email="your.email@example.com",
    phone="+91-XXXXXXXXXX",
    job_titles=["Data Scientist", "ML Engineer"],
    skills=["Python", "Machine Learning", "GenAI"],
    locations=["Bangalore", "Mumbai", "Remote"],
    experience_years=3,
    max_applications_per_day=50,
    auto_apply=False
)

# Agent Configuration
DEFAULT_AGENT_CONFIG = AgentConfig(
    model="claude-sonnet-4-20250514",
    scrape_interval_hours=6,
    max_jobs_per_board=100,
    similarity_threshold=0.7,
    headless=True  # Run browser in headless mode
)
```

## 📁 Project Structure

```
├── agent.py                      # Main orchestrator
├── config.py                     # Configuration
├── resume_parser.py              # Resume parsing
├── job_scraper.py                # Multi-platform scraping
├── job_matcher.py                # AI-powered matching
├── cover_letter_generator.py    # Cover letter generation
├── application_automator.py     # Application automation
├── dashboard.html                # Web dashboard
├── requirements.txt              # Dependencies
├── data/                         # Data directory
│   ├── resumes/                 # Your resume(s)
│   ├── jobs/                    # Scraped jobs
│   ├── applications/            # Application data
│   │   └── cover_letters/       # Generated cover letters
│   └── job_applications.db      # SQLite database
└── logs/                         # Log files
```

## 🎯 Step-by-Step Workflow

### 1. Parse Resume
```python
parsed_resume = agent.load_and_parse_resume("resume.pdf")
# Extracts: name, email, skills, experience, education, etc.
```

### 2. Scrape Jobs
```python
jobs = agent.scrape_jobs(
    platforms=['linkedin', 'indeed', 'naukri'],
    keywords="data scientist",
    location="India"
)
# Scrapes and deduplicates jobs from all platforms
```

### 3. Match Jobs
```python
matches = agent.match_jobs(top_k=20)
# Uses semantic similarity + skill matching
# Returns top N matches with scores and reasoning
```

### 4. Generate Cover Letters
```python
cover_letters = agent.generate_cover_letters(num_letters=10)
# Creates personalized, ATS-optimized cover letters
```

### 5. Apply to Jobs
```python
results = agent.apply_to_jobs(
    max_applications=10,
    auto_submit=False  # Review before submitting
)
# Automates form filling and tracks applications
```

## 🔍 Job Platforms Supported

### Fully Supported (with automation)
- ✅ **LinkedIn** - Easy Apply jobs
- ✅ **Indeed India** - Direct applications
- ✅ **Naukri.com** - India's largest job portal

### Supported (scraping only)
- 🔄 **Shine.com**
- 🔄 **Instahyre**
- 🔄 **Foundit** (Monster India)
- 🔄 **Glassdoor India**

### Coming Soon
- 🚧 **AngelList**
- 🚧 **Wellfound**
- 🚧 **Cutshort**

## 🛡️ Safety Features

### Built-in Protections
1. **Rate Limiting**: Automatic delays between requests
2. **Anti-Detection**: Mimics human behavior
3. **Manual Review**: Option to review before submission
4. **Application Limits**: Configurable daily limits
5. **Error Handling**: Robust error handling and logging
6. **Database Tracking**: Prevents duplicate applications

### Recommended Practices
- Start with `auto_submit=False` to review applications
- Limit to 20-30 applications per day
- Review generated cover letters periodically
- Keep your resume updated
- Monitor the dashboard regularly

## 📈 Performance Metrics

Typical performance on a modern machine:
- **Resume Parsing**: ~5-10 seconds
- **Job Scraping**: ~2-5 minutes (100 jobs per platform)
- **Job Matching**: ~30-60 seconds (500 jobs)
- **Cover Letter Generation**: ~3-5 seconds per letter
- **Application Submission**: ~30-60 seconds per application

**Full Pipeline**: 15-30 minutes for 50 applications

## 🐛 Troubleshooting

### ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver version
# https://chromedriver.chromium.org/downloads
```

### Scraping Errors
- Websites may update their HTML structure
- Try running in non-headless mode to debug
- Check logs in `data/logs/`
- Some sites require manual login

### API Rate Limits
- Anthropic API has rate limits
- Add delays between requests
- Consider using caching

### Application Failures
- Some jobs require manual application
- External application links not supported
- Login required for many platforms

## 🔐 Privacy & Security

- All data stored locally
- No data sent to third parties (except Anthropic API)
- Resume and applications stored in `data/` directory
- SQLite database not encrypted by default
- API keys should be in environment variables

## 📄 License

This project is for educational and personal use only. Please respect:
- Job platform Terms of Service
- Rate limits and fair use policies
- Privacy regulations (GDPR, etc.)
- Employment laws in your jurisdiction

## 🤝 Contributing

This is a demonstration project. For production use:
- Add more error handling
- Implement proxy rotation
- Add CAPTCHA solving
- Enhance NLP for better matching
- Add more job platforms
- Implement email notifications
- Add interview tracking

## ⚠️ Disclaimer

This tool is for educational purposes. Users are responsible for:
- Complying with platform Terms of Service
- Ensuring application accuracy
- Following employment regulations
- Respecting rate limits
- Manual review of applications

## 📞 Support

For issues:
1. Check the logs in `data/logs/`
2. Review the configuration in `config.py`
3. Try running in debug mode (headless=False)
4. Check ChromeDriver compatibility

## 🎓 For Data Scientists

This system is specifically optimized for:
- Data Science positions
- ML/AI roles
- GenAI positions
- Research scientist roles
- India job market

Keywords optimized for:
- Python, TensorFlow, PyTorch
- Machine Learning, Deep Learning
- NLP, Computer Vision, GenAI
- LLMs, Transformers
- AWS, Azure, Docker, Kubernetes

## 🚀 Advanced Features

### Custom Scrapers
Add your own scrapers by extending `JobScraper` class:

```python
class CustomScraper(JobScraper):
    def scrape_jobs(self, keywords, location, max_jobs):
        # Your scraping logic
        pass
```

### Custom Matching Logic
Modify `JobMatcher` to use custom scoring:

```python
def custom_match_score(self, resume, job):
    # Your matching algorithm
    pass
```

### Webhook Notifications
Add webhooks for application events:

```python
def on_application_success(self, job):
    requests.post(webhook_url, json={'job': job})
```

## 📚 Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Happy Job Hunting! 🎉**

Built with ❤️ using Claude AI
