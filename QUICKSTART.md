# 🚀 Quick Start Guide - AI Job Application Agent

Get up and running in 5 minutes!

## Prerequisites
- Python 3.9+
- Chrome browser
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Install ChromeDriver
```bash
# macOS
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-chromedriver
```

## Quick Test (5 minutes)

### Option 1: Run Examples
```bash
# Interactive examples
python examples.py

# Select option 2 for step-by-step demo
```

### Option 2: Direct Command Line
```bash
# Basic run (will process 5 jobs)
python agent.py \
  --resume /path/to/your/resume.pdf \
  --max-apps 5 \
  --platforms linkedin indeed naukri

# Review mode (won't auto-submit)
python agent.py \
  --resume resume.pdf \
  --max-apps 10
```

### Option 3: Python Script
```python
from agent import JobApplicationAgent

# Initialize
agent = JobApplicationAgent(
    anthropic_api_key="your-key"
)

# Run pipeline
results = agent.run_full_pipeline(
    resume_path="resume.pdf",
    max_applications=5,
    auto_submit=False  # Safe mode
)

print(f"Applied to {len(results)} jobs!")
```

## Web Dashboard

Open `dashboard.html` in your browser to monitor:
- Job scraping status
- Match scores
- Application tracking
- Configuration settings

```bash
open dashboard.html
# or
python -m http.server 8000
# Then visit http://localhost:8000/dashboard.html
```

## Your First Run - Step by Step

### 1. Prepare Your Resume
```bash
mkdir -p data/resumes
cp /path/to/your/resume.pdf data/resumes/resume.pdf
```

### 2. Configure Settings (Optional)
Edit `config.py`:
```python
DEFAULT_USER_PROFILE = UserProfile(
    name="Your Name",
    email="your@email.com",
    phone="+91-XXXXXXXXXX",
    job_titles=["Data Scientist", "ML Engineer"],
    locations=["Bangalore", "Mumbai", "Remote"],
    max_applications_per_day=30
)
```

### 3. Run the Agent
```bash
python agent.py --resume data/resumes/resume.pdf --max-apps 10
```

### 4. Review Output
Check these directories:
```
data/
├── parsed_resume.json          # Your extracted resume data
├── jobs/                       # Scraped jobs
│   └── scraped_jobs_*.json
├── applications/               # Application data
│   ├── matches_*.json         # Job matches
│   ├── match_report_*.txt     # Detailed report
│   └── cover_letters/         # Generated letters
└── job_applications.db         # Tracking database
```

## Common Use Cases

### Case 1: Quick Job Search (5-10 minutes)
```bash
python agent.py \
  --resume resume.pdf \
  --platforms linkedin naukri \
  --max-apps 5
```

### Case 2: Comprehensive Search (30-60 minutes)
```bash
python agent.py \
  --resume resume.pdf \
  --platforms linkedin indeed naukri shine \
  --max-apps 50
```

### Case 3: Scheduled Automation (Runs continuously)
```bash
python agent.py \
  --resume resume.pdf \
  --schedule 6 \
  --max-apps 30
```

### Case 4: Specific Location/Role
```python
agent = JobApplicationAgent(api_key="...")

# Scrape only remote ML jobs
agent.load_and_parse_resume("resume.pdf")
jobs = agent.scrape_jobs(
    keywords="machine learning engineer",
    location="Remote"
)

# Filter and match
remote_jobs = [j for j in jobs if 'remote' in j.work_mode.lower()]
agent.scraped_jobs = remote_jobs
matches = agent.match_jobs()
```

## Important Notes

### Safety Features
- ✅ **Default: Safe Mode** - Won't auto-submit without your confirmation
- ✅ **Rate Limiting** - Automatic delays between requests
- ✅ **Duplicate Prevention** - Tracks applications to avoid duplicates
- ✅ **Review Dashboard** - See all matches before applying

### Enable Auto-Submit (Use Carefully!)
```bash
# Only after testing in safe mode
python agent.py \
  --resume resume.pdf \
  --max-apps 10 \
  --auto-submit
```

### Best Practices
1. **Start Small**: Test with 5-10 applications first
2. **Review First**: Check generated cover letters and matches
3. **Monitor Dashboard**: Keep an eye on the web dashboard
4. **Update Resume**: Keep your resume current
5. **Check Logs**: Review `data/logs/` for any issues

## Troubleshooting

### Issue: ChromeDriver not found
```bash
# Check Chrome version
google-chrome --version

# Install matching ChromeDriver
# Visit: https://chromedriver.chromium.org/downloads
```

### Issue: API Key Error
```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat .env
```

### Issue: Resume parsing failed
- Ensure resume is in PDF format
- Check if text is extractable (not an image PDF)
- Try with `pdftotext resume.pdf` to verify

### Issue: Website scraping errors
- Some sites update their structure
- Try running in non-headless mode: Edit `config.py` → `headless=False`
- Check `data/logs/` for specific errors

## What Happens During a Run?

```
1. 📄 Resume Parsing (~10 seconds)
   ├─ Extract text from PDF
   ├─ Parse skills, experience, education
   └─ Create structured profile

2. 🔍 Job Scraping (~3-5 minutes)
   ├─ Search LinkedIn, Indeed, Naukri
   ├─ Extract job details
   └─ Remove duplicates

3. 🎯 Job Matching (~30 seconds)
   ├─ Semantic similarity analysis
   ├─ Skill matching
   └─ Generate match scores

4. ✍️ Cover Letter Generation (~5 seconds each)
   ├─ Personalized content
   ├─ ATS optimization
   └─ Save to files

5. 📤 Application Submission (~60 seconds each)
   ├─ Navigate to job page
   ├─ Fill application forms
   ├─ Upload resume & cover letter
   └─ Track in database
```

## Next Steps

1. **Optimize Your Resume**: Ensure it's ATS-friendly
2. **Customize Settings**: Edit `config.py` for your preferences
3. **Review Matches**: Check `data/applications/match_report_*.txt`
4. **Track Applications**: Monitor `dashboard.html`
5. **Iterate**: Adjust threshold and preferences based on results

## Getting Help

- Check logs: `cat data/logs/agent_*.log`
- Read full documentation: `README.md`
- Review examples: `python examples.py`
- Database queries: `sqlite3 data/job_applications.db`

## Pro Tips

### Tip 1: Better Matches
Increase similarity threshold in `config.py`:
```python
similarity_threshold=0.8  # Higher = pickier
```

### Tip 2: Focus on Quality
```bash
# Scrape more, apply to fewer (top matches only)
python agent.py \
  --resume resume.pdf \
  --max-apps 10  # Will scrape 300+ but only apply to top 10
```

### Tip 3: Platform-Specific
```bash
# LinkedIn only (usually higher quality)
python agent.py \
  --resume resume.pdf \
  --platforms linkedin \
  --max-apps 20
```

### Tip 4: Location Filter
```python
# In your script
agent.scrape_jobs(location="Bangalore")  # Specific city
agent.scrape_jobs(location="Remote")     # Remote only
```

### Tip 5: Continuous Monitoring
```bash
# Run every 8 hours, apply to 20 best matches
python agent.py \
  --resume resume.pdf \
  --schedule 8 \
  --max-apps 20
```

---

**Ready to start? Run this now:**

```bash
python setup.py  # One-time setup
python agent.py --resume resume.pdf --max-apps 5  # First run
```

Good luck with your job search! 🎉
