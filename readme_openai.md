# AI Job Application Agent 🤖 (OpenAI GPT Version)

An advanced, agentic AI system that automates the entire job application process using **OpenAI's GPT models**. Built specifically for Data Scientists targeting jobs in India across multiple platforms.

> **🆕 Now powered by OpenAI GPT-3.5-turbo** - Optimized for free tier usage!

## 🌟 Features

### Core Capabilities
- **Resume Parsing**: Automatically extracts and structures information from your resume using GPT
- **Multi-Platform Scraping**: Scrapes jobs from LinkedIn, Indeed, Naukri, Shine, Instahyre, and more
- **AI-Powered Matching**: Uses semantic similarity + ML to match jobs with your profile
- **Cover Letter Generation**: Creates personalized, ATS-optimized cover letters with GPT
- **Application Automation**: Automates form filling and application submission
- **Application Tracking**: SQLite database to track all applications and their status

### What's New - OpenAI Version
- ✅ **Cost-Effective**: Uses GPT-3.5-turbo (~$0.01 per application)
- ✅ **Free Tier Friendly**: Optimized rate limits and token usage
- ✅ **Fast**: GPT-3.5-turbo is faster than GPT-4
- ✅ **Reliable**: Same quality for resume parsing and cover letters
- ✅ **Scalable**: Can upgrade to GPT-4 for better quality

## 💰 Pricing & Free Tier

### OpenAI Free Tier
- **$5 free credits** for first 3 months (new accounts)
- **~500-700 applications** possible with $5 credit
- **Rate limit**: 3 requests/minute

### Cost Breakdown (GPT-3.5-turbo)
- Resume parsing: **$0.005** per resume
- Cover letter generation: **$0.004** per letter
- Job matching: **$0.001** per job
- **Total**: **~$0.01 per complete application**

### Example Costs
- 10 applications: **$0.10**
- 50 applications: **$0.50**
- 100 applications: **$1.00**
- 500 applications: **$5.00** (full free tier)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the repository
# Install dependencies
pip install -r requirements.txt
```

### 2. Get OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key

### 3. Set API Key

```bash
# Option A: Environment variable
export OPENAI_API_KEY='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'

# Option B: .env file
echo "OPENAI_API_KEY=your-key" > .env
```

### 4. Add Resume

```bash
mkdir -p data/resumes
cp /path/to/your/resume.pdf data/resumes/resume.pdf
```

### 5. Run!

```bash
# Quick test with 5 applications
python agent.py --resume data/resumes/resume.pdf --max-apps 5
```

## 📖 Detailed Usage

### Basic Usage

```python
from agent import JobApplicationAgent

# Initialize agent
agent = JobApplicationAgent(
    openai_api_key="your-api-key"
)

# Run full pipeline
results = agent.run_full_pipeline(
    resume_path="data/resumes/resume.pdf",
    platforms=['linkedin', 'indeed', 'naukri'],
    max_applications=10,
    auto_submit=False  # Review before submitting
)

print(f"Completed {len(results)} applications!")
```

### Step-by-Step Execution

```python
agent = JobApplicationAgent(openai_api_key="your-key")

# Step 1: Parse resume
resume = agent.load_and_parse_resume("resume.pdf")
print(f"Found {len(resume.skills)} skills")

# Step 2: Scrape jobs
jobs = agent.scrape_jobs(
    platforms=['linkedin', 'indeed'],
    location='Bangalore'
)
print(f"Scraped {len(jobs)} jobs")

# Step 3: Match jobs
matches = agent.match_jobs(top_k=20)
print(f"Found {len(matches)} matches")

# Step 4: Generate cover letters
agent.generate_cover_letters(num_letters=10)

# Step 5: Apply (review mode)
results = agent.apply_to_jobs(max_applications=5, auto_submit=False)
```

### Command Line Interface

```bash
# Basic usage
python agent.py --resume resume.pdf --max-apps 10

# Specific platforms
python agent.py \
  --resume resume.pdf \
  --platforms linkedin naukri \
  --max-apps 20

# Scheduled execution (every 6 hours)
python agent.py \
  --resume resume.pdf \
  --schedule 6 \
  --max-apps 30
```

## ⚙️ Configuration

### Model Selection

Edit `config.py`:

```python
class AgentConfig(BaseModel):
    # For free tier (recommended)
    model: str = "gpt-3.5-turbo"
    
    # For better quality (paid tier)
    # model: str = "gpt-4-turbo"
    # model: str = "gpt-4o"
    
    max_tokens: int = 2048
```

### User Profile

Edit `config.py`:

```python
class UserProfile(BaseModel):
    name: str = "Your Name"
    email: str = "your@email.com"
    phone: str = "+91-XXXXXXXXXX"
    
    job_titles: List[str] = [
        "Data Scientist",
        "ML Engineer"
    ]
    
    skills: List[str] = [
        "Python", "Machine Learning",
        "TensorFlow", "PyTorch"
    ]
    
    locations: List[str] = [
        "Bangalore", "Mumbai", "Remote"
    ]
    
    max_applications_per_day: int = 50
```

## 📊 Cost Optimization Tips

### 1. Use GPT-3.5-turbo (Default)
- 10x cheaper than GPT-4
- Sufficient quality for most tasks
- Faster processing

### 2. Batch Processing
```python
# Parse resume once, reuse multiple times
agent.load_and_parse_resume("resume.pdf")

# Multiple searches without re-parsing
agent.scrape_jobs(platforms=['linkedin'])
agent.scrape_jobs(platforms=['indeed'])
```

### 3. Higher Match Threshold
```python
# Only apply to best matches
AgentConfig(
    similarity_threshold=0.8  # vs default 0.7
)
```

### 4. Limit Cover Letters
```python
# Generate fewer cover letters
agent.generate_cover_letters(num_letters=10)  # vs 50
```

### 5. Monitor Usage
- Check: https://platform.openai.com/usage
- Set spending limits in OpenAI dashboard
- Track token usage in logs

## 🗂️ Project Structure

```
├── agent.py                      # Main orchestrator
├── config.py                     # Configuration (OpenAI)
├── resume_parser.py              # Resume parsing (GPT)
├── job_scraper.py                # Multi-platform scraping
├── job_matcher.py                # AI-powered matching (GPT)
├── cover_letter_generator.py    # Cover letter generation (GPT)
├── application_automator.py     # Application automation
├── requirements.txt              # Dependencies (OpenAI)
├── setup.py                      # Setup script
├── examples_openai.py            # Usage examples
├── MIGRATION_GUIDE.md            # Migration from Anthropic
├── QUICKSTART_OPENAI.md          # Quick start guide
└── data/                         # Data directory
    ├── resumes/                  # Your resume(s)
    ├── jobs/                     # Scraped jobs
    ├── applications/             # Application data
    └── job_applications.db       # SQLite database
```

## 🎯 Supported Platforms

### Fully Supported (with automation)
- ✅ **LinkedIn** - Easy Apply jobs
- ✅ **Indeed India** - Direct applications
- ✅ **Naukri.com** - India's largest job portal

### Supported (scraping only)
- 📄 **Shine.com**
- 📄 **Instahyre**
- 📄 **Foundit** (Monster India)
- 📄 **Glassdoor India**

## 📈 Performance

### Speed (GPT-3.5-turbo)
- **Resume Parsing**: ~3-5 seconds
- **Cover Letter**: ~2-3 seconds
- **Job Matching**: ~1 second per job
- **Full Pipeline (10 apps)**: ~5-10 minutes

### Quality Comparison

| Task | GPT-3.5 | GPT-4 | Claude |
|------|---------|-------|--------|
| Resume Parsing | Very Good | Excellent | Excellent |
| Cover Letters | Very Good | Excellent | Excellent |
| Job Matching | Very Good | Excellent | Excellent |
| Cost (per 1K tokens) | $0.002 | $0.03 | $0.003 |
| Speed | Fastest | Slower | Medium |

## 🔧 Troubleshooting

### Rate Limit Errors
```python
# Increase delays in config.py
AgentConfig(
    requests_per_minute=2,  # Reduce from 3
    delay_between_applications=120  # Increase from 60
)
```

### API Key Issues
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set it correctly
export OPENAI_API_KEY='sk-...'
```

### Insufficient Quota
- Check usage: https://platform.openai.com/usage
- Add payment method if free trial expired
- Reduce `max_applications` to stay within budget

### Poor Quality Outputs
```python
# Try GPT-4 (more expensive but better)
AgentConfig(
    model="gpt-4-turbo"
)
```

## 📚 Documentation

- **Quick Start**: See `QUICKSTART_OPENAI.md`
- **Migration Guide**: See `MIGRATION_GUIDE.md` (if coming from Anthropic)
- **Examples**: Run `python examples_openai.py`
- **API Docs**: https://platform.openai.com/docs

## 🛡️ Safety Features

- **Manual Review Mode**: Review applications before submission
- **Rate Limiting**: Automatic delays to respect API limits
- **Duplicate Prevention**: Tracks applications in database
- **Error Handling**: Robust error handling and logging
- **Cost Controls**: Token limits and request throttling

## ⚠️ Disclaimer

This tool is for educational and personal use. Users are responsible for:
- Complying with platform Terms of Service
- Ensuring application accuracy
- Following employment regulations
- Respecting rate limits
- Managing API costs

## 🔄 Upgrading from Anthropic Version

If you have the Anthropic (Claude) version:

1. Update dependencies: `pip install -r requirements.txt`
2. Change API key: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`
3. Update all files with new versions provided
4. See `MIGRATION_GUIDE.md` for details

## 📊 Example Results

### Sample Run (10 Applications)
```
Resume Parsing: ✅ Completed in 4s
Job Scraping: ✅ Found 347 jobs
Job Matching: ✅ 23 high-quality matches
Cover Letters: ✅ Generated 10 letters
Applications: ✅ 8/10 successful

Total Time: 12 minutes
Total Cost: ~$0.12
```

## 🎓 Best Practices

1. **Start Small**: Test with 5-10 applications first
2. **Review Output**: Check cover letters and matches
3. **Monitor Costs**: Keep an eye on OpenAI usage dashboard
4. **Update Resume**: Keep your resume current
5. **Adjust Threshold**: Fine-tune `similarity_threshold` based on results
6. **Use Free Tier Wisely**: ~500 applications max with $5 credit

## 🤝 Contributing

This is an educational project. Enhancements welcome:
- Additional job platforms
- Better matching algorithms
- Enhanced NLP for skill extraction
- Interview tracking features
- Email notifications

## 📞 Support

For issues:
1. Check logs in `data/logs/`
2. Review configuration in `config.py`
3. See troubleshooting section above
4. Check OpenAI status: https://status.openai.com

## 📝 License

Educational use only. Respect platform ToS and employment laws.

---

**Built with ❤️ using OpenAI GPT**

Ready to automate your job search! 🚀

```bash
# Get started now!
python setup.py
python agent.py --resume resume.pdf --max-apps 5
```