"""
Simple Examples - OpenAI GPT Version

Quick examples to get you started with the job application agent.
"""
import os
from agent import JobApplicationAgent
from config import UserProfile, AgentConfig


def example_basic():
    """
    Most basic usage - just run it!
    """
    print("=" * 70)
    print("EXAMPLE: Basic Usage with OpenAI GPT")
    print("=" * 70)
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='your-key'")
        return
    
    # Create agent
    agent = JobApplicationAgent(openai_api_key=api_key)
    
    # Run complete pipeline
    results = agent.run_full_pipeline(
        resume_path="data/resumes/resume.pdf",
        platforms=['linkedin', 'indeed'],
        max_applications=5,
        auto_submit=False  # Safety first!
    )
    
    print(f"\n✅ Completed! Processed {len(results)} applications")


def example_step_by_step():
    """
    Step-by-step execution for more control
    """
    print("=" * 70)
    print("EXAMPLE: Step-by-Step with GPT-3.5-turbo")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY first")
        return
    
    agent = JobApplicationAgent(openai_api_key=api_key)
    
    # Step 1: Parse resume
    print("\n📄 Step 1: Parsing resume...")
    resume = agent.load_and_parse_resume("data/resumes/resume.pdf")
    print(f"   ✅ Parsed resume for {resume.name}")
    print(f"   📊 {len(resume.skills)} skills, {resume.total_experience_years} years exp")
    
    # Step 2: Scrape jobs
    print("\n🔍 Step 2: Scraping jobs...")
    jobs = agent.scrape_jobs(
        platforms=['linkedin'],
        keywords="data scientist",
        location="Bangalore"
    )
    print(f"   ✅ Found {len(jobs)} jobs")
    
    # Step 3: Match jobs
    print("\n🎯 Step 3: Matching jobs...")
    matches = agent.match_jobs(top_k=10)
    print(f"   ✅ Found {len(matches)} good matches")
    
    # Show top 3
    print("\n   Top 3 matches:")
    for i, match in enumerate(matches[:3], 1):
        print(f"   {i}. {match.job.title} at {match.job.company}")
        print(f"      Score: {match.match_score:.2%}")
    
    # Step 4: Generate cover letters
    print("\n✍️  Step 4: Generating cover letters...")
    agent.generate_cover_letters(num_letters=5)
    print("   ✅ Cover letters saved to data/applications/cover_letters/")
    
    print("\n🎉 Done! Check the files in data/applications/")


def example_custom_config():
    """
    Using custom configuration
    """
    print("=" * 70)
    print("EXAMPLE: Custom Configuration")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY first")
        return
    
    # Custom user profile
    my_profile = UserProfile(
        name="John Doe",
        email="john@example.com",
        phone="+91-9876543210",
        location="Bangalore",
        job_titles=["Data Scientist", "ML Engineer"],
        skills=[
            "Python", "TensorFlow", "PyTorch",
            "Machine Learning", "Deep Learning",
            "NLP", "Computer Vision"
        ],
        experience_years=5,
        max_applications_per_day=20
    )
    
    # Custom agent config - use GPT-3.5 for cost efficiency
    my_config = AgentConfig(
        model="gpt-3.5-turbo",  # Most cost-effective
        temperature=0.7,
        max_tokens=2048,
        similarity_threshold=0.75,  # Higher = more selective
        requests_per_minute=3  # Free tier friendly
    )
    
    # Create agent with custom config
    agent = JobApplicationAgent(
        openai_api_key=api_key,
        user_profile=my_profile,
        agent_config=my_config
    )
    
    # Run
    results = agent.run_full_pipeline(
        resume_path="data/resumes/resume.pdf",
        platforms=['linkedin', 'naukri'],
        max_applications=10,
        auto_submit=False
    )
    
    print(f"\n✅ Custom config run complete! {len(results)} applications processed")


def example_cost_efficient():
    """
    Cost-efficient approach for free tier
    """
    print("=" * 70)
    print("EXAMPLE: Cost-Efficient Usage (Free Tier Optimized)")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY first")
        return
    
    # Conservative config for free tier
    free_tier_config = AgentConfig(
        model="gpt-3.5-turbo",  # Cheapest option
        max_tokens=1500,  # Reduced tokens
        similarity_threshold=0.8,  # Only best matches
        requests_per_minute=2,  # Conservative rate
        delay_between_applications=90  # Longer delays
    )
    
    agent = JobApplicationAgent(
        openai_api_key=api_key,
        agent_config=free_tier_config
    )
    
    print("\n💰 Free tier optimization:")
    print("   - Using gpt-3.5-turbo (most economical)")
    print("   - Processing only top matches (threshold 0.8)")
    print("   - Conservative rate limits")
    
    # Parse resume once
    resume = agent.load_and_parse_resume("data/resumes/resume.pdf")
    
    # Scrape jobs
    jobs = agent.scrape_jobs(platforms=['linkedin'])
    
    # Only match top 20
    matches = agent.match_jobs(top_k=20)
    
    # Generate letters for top 5 only
    agent.generate_cover_letters(num_letters=5)
    
    print("\n✅ Done with minimal API usage!")
    print(f"   Estimated cost: ~$0.05-0.10")


def example_test_api():
    """
    Simple API test
    """
    print("=" * 70)
    print("EXAMPLE: Test OpenAI API Connection")
    print("=" * 70)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set OPENAI_API_KEY first")
        return
    
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    print("\n🧪 Testing API connection...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful!' if you can read this."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")
        print(f"💰 Estimated cost: ${response.usage.total_tokens * 0.000002:.6f}")
        
    except Exception as e:
        print(f"❌ API Error: {e}")


def main():
    """
    Run examples
    """
    print("\n" + "=" * 70)
    print("AI JOB APPLICATION AGENT - OpenAI GPT Examples")
    print("=" * 70)
    
    print("\nAvailable examples:")
    print("1. Basic Usage (5 applications)")
    print("2. Step-by-Step Execution")
    print("3. Custom Configuration")
    print("4. Cost-Efficient (Free Tier)")
    print("5. Test API Connection")
    
    choice = input("\nSelect example (1-5): ").strip()
    
    examples = {
        '1': example_basic,
        '2': example_step_by_step,
        '3': example_custom_config,
        '4': example_cost_efficient,
        '5': example_test_api
    }
    
    if choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Invalid choice!")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n" + "=" * 70)
        print("⚠️  WARNING: OPENAI_API_KEY not set!")
        print("=" * 70)
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr create a .env file:")
        print("  echo 'OPENAI_API_KEY=your-key' > .env")
        print("\nGet your key at: https://platform.openai.com/api-keys")
        print("=" * 70 + "\n")
    
    main()