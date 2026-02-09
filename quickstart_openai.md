# 🚀 Quick Start - OpenAI GPT Version

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key

### 3. Set API Key
```bash
# Option A: Environment variable
export OPENAI_API_KEY='your-key-here'

# Option B: .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

### 4. Add Your Resume
```bash
mkdir -p data/resumes
cp /path/to/your/resume.pdf data/resumes/resume.pdf
```

### 5. Run!
```bash
# Test with 5 applications
python agent.py --resume data/resumes/resume.pdf --max-apps 5
```

---

## 💰 Free Tier Usage

### What You Get
- **$5 free credits** (first 3 months for new accounts)
- **~500-700 applications** with $5 credit using GPT-3.5-turbo
- **3 requests/minute** rate limit

### Cost Per Application
- Resume parsing: ~$0.005
- Cover letter: ~$0.004
- Job matching: ~$0.001
- **Total**: ~$0.01 per application

### Example Budgets
- 10 applications: ~$0.10
- 50 applications: ~$0.50
- 100 applications: ~$1.00

---

## 📝 Basic Usage Examples

### Example 1: Quick Test (5 jobs)
```bash
python agent.py \
  --resume data/resumes/resume.pdf \
  --max-apps 5 \
  --platforms linkedin indeed
```

### Example 2: Specific Location
```python
from agent import JobApplicationAgent

agent = JobApplicationAgent(
    openai_api_key="your-key"
)

# Search Bangalore jobs only
agent.load_and_parse_resume("resume.pdf")
agent.scrape_jobs(location="Bangalore", platforms=['linkedin'])
matches = agent.match_jobs(top_k=10)
```

### Example 3: Generate Cover Letters Only
```python
agent = JobApplicationAgent(openai_api_key="your-key")

agent.load_and_parse_resume("resume.pdf")
agent.scrape_jobs()
agent.match_jobs()
agent.generate_cover_letters(num_letters=10)
# Files saved in data/applications/cover_letters/
```

---

## ⚙️ Configuration

### Change Model (Better Quality)
Edit `config.py`:
```python
class AgentConfig(BaseModel):
    # For free tier (cheapest)
    model: str = "gpt-3.5-turbo"
    
    # For better quality (more expensive)
    # model: str = "gpt-4-turbo"
```

### Adjust Rate Limits
Edit `config.py`:
```python
class AgentConfig(BaseModel):
    requests_per_minute: int = 3  # Lower for free tier
    delay_between_applications: int = 60  # seconds between apps
```

---

## 🎯 Recommended Workflow

### Day 1: Setup & Test
```bash
# 1. Setup
python setup.py

# 2. Small test
python agent.py --resume resume.pdf --max-apps 5

# 3. Review results in data/applications/
```

### Day 2: Real Search
```bash
# Run with more jobs
python agent.py \
  --resume resume.pdf \
  --max-apps 20 \
  --platforms linkedin indeed naukri
```

### Day 3: Monitor & Adjust
```bash
# Check usage: https://platform.openai.com/usage
# Adjust settings in config.py
# Review match_report_*.txt files
```

---

## 📊 Monitoring Costs

### Check OpenAI Usage
1. Visit: https://platform.openai.com/usage
2. View: Tokens used, cost, rate limits
3. Monitor: Daily spending

### Estimate Before Running
```python
# For 50 applications with GPT-3.5-turbo:
# - Resume parsing: 1 × $0.005 = $0.005
# - Job matching: 50 × $0.001 = $0.05
# - Cover letters: 50 × $0.004 = $0.20
# Total: ~$0.25
```

---

## ⚠️ Common Issues

### "Rate limit exceeded"
**Problem**: Free tier limit (3 req/min)  
**Solution**: Wait 60 seconds, or reduce in config:
```python
requests_per_minute: int = 2
```

### "Insufficient quota"
**Problem**: Free credits exhausted  
**Solution**: 
1. Check: https://platform.openai.com/usage
2. Add payment method if needed

### "API key invalid"
**Problem**: Wrong/expired key  
**Solution**: 
```bash
# Get new key from:
# https://platform.openai.com/api-keys

# Set it:
export OPENAI_API_KEY='new-key'
```

---

## 🔥 Pro Tips

### 1. Batch Processing
```python
# Parse resume once, reuse for multiple runs
agent = JobApplicationAgent(openai_api_key="key")
agent.load_and_parse_resume("resume.pdf")

# Run 1: LinkedIn
agent.scrape_jobs(platforms=['linkedin'])
agent.match_jobs()

# Run 2: Indeed (reuses parsed resume)
agent.scrape_jobs(platforms=['indeed'])
agent.match_jobs()
```

### 2. Save API Calls
```python
# Generate fewer cover letters
agent.generate_cover_letters(num_letters=10)  # Not 50

# Use higher match threshold
agent.config.similarity_threshold = 0.8  # Only top matches
```

### 3. Test Locally First
```bash
# Generate cover letters without applying
python agent.py --resume resume.pdf --max-apps 5
# Review files before enabling auto-submit
```

---

## 📁 Output Files

After running, check these directories:

```
data/
├── parsed_resume.json          # Your parsed resume
├── jobs/
│   └── scraped_jobs_*.json    # All scraped jobs
├── applications/
│   ├── matches_*.json         # Job matches
│   ├── match_report_*.txt     # Human-readable report
│   ├── cover_letters/         # Generated letters
│   └── application_results_*.json
└── job_applications.db         # Tracking database
```

---

## 🎓 Learning Path

### Week 1: Learn the Basics
- Run with 5-10 applications
- Review generated cover letters
- Check match scores

### Week 2: Optimize
- Adjust similarity threshold
- Test different platforms
- Fine-tune user profile in config.py

### Week 3: Scale
- Increase to 30-50 applications
- Set up scheduled runs
- Monitor success rate

---

## 🆘 Need Help?

1. **Check logs**: `cat data/logs/agent_*.log`
2. **Review config**: `cat config.py`
3. **Test API**: 
   ```python
   from openai import OpenAI
   client = OpenAI(api_key="your-key")
   response = client.chat.completions.create(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "test"}]
   )
   print(response.choices[0].message.content)
   ```
4. **Check documentation**: See MIGRATION_GUIDE.md

---

## ✅ Pre-Flight Checklist

Before your first real run:

- [ ] OpenAI API key set
- [ ] Resume added to data/resumes/
- [ ] Tested with --max-apps 5
- [ ] Reviewed generated cover letters
- [ ] Checked match_report_*.txt
- [ ] Monitored costs at platform.openai.com/usage
- [ ] Updated config.py with preferences

---

**You're ready! Start with 5 applications and scale up.** 🚀

```bash
python agent.py --resume data/resumes/resume.pdf --max-apps 5
```