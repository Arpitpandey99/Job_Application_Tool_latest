"""
Example Usage Script - Demonstrates how to use the AI Job Application Agent

This script shows various ways to use the agent, from basic to advanced.
"""
import os
from pathlib import Path

# Import the agent
from agent import JobApplicationAgent
from config import UserProfile, AgentConfig

def example_1_basic_usage():
    """
    Example 1: Basic usage - Run the complete pipeline
    """
    print("=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)
    
    # Initialize agent
    agent = JobApplicationAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Run the full pipeline
    results = agent.run_full_pipeline(
        resume_path="data/resumes/resume.pdf",
        platforms=['linkedin', 'indeed', 'naukri'],
        max_applications=5,
        auto_submit=False  # Review before submitting
    )
    
    print(f"Completed! Applied to {len(results)} jobs")


def example_2_step_by_step():
    """
    Example 2: Step-by-step execution with more control
    """
    print("=" * 70)
    print("EXAMPLE 2: Step-by-Step Execution")
    print("=" * 70)
    
    agent = JobApplicationAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Step 1: Parse resume
    print("\n📄 Parsing resume...")
    parsed_resume = agent.load_and_parse_resume("data/resumes/resume.pdf")
    print(f"Found {len(parsed_resume.skills)} skills")
    print(f"Experience: {parsed_resume.total_experience_years} years")
    
    # Step 2: Scrape jobs
    print("\n🔍 Scraping jobs...")
    jobs = agent.scrape_jobs(
        platforms=['linkedin', 'indeed'],
        keywords='data scientist machine learning',
        location='Bangalore'
    )
    print(f"Scraped {len(jobs)} jobs")
    
    # Step 3: Match jobs
    print("\n🎯 Matching jobs...")
    matches = agent.match_jobs(top_k=10)
    print(f"Found {len(matches)} good matches")
    
    # Print top 3 matches
    print("\nTop 3 matches:")
    for i, match in enumerate(matches[:3], 1):
        print(f"{i}. {match.job.title} at {match.job.company}")
        print(f"   Score: {match.match_score:.2%}")
        print(f"   Reason: {match.reasoning[:100]}...")
        print()
    
    # Step 4: Generate cover letters
    print("✍️ Generating cover letters...")
    cover_letters = agent.generate_cover_letters(
        matches=matches[:5],
        num_letters=5
    )
    print(f"Generated {len(cover_letters)} cover letters")
    
    # Step 5: Apply (manual review mode)
    print("\n📤 Preparing applications...")
    results = agent.apply_to_jobs(
        matches=matches[:3],
        max_applications=3,
        auto_submit=False
    )
    
    print("\nApplication Summary:")
    for result in results:
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {result.get('job_title')} at {result.get('company')}")


def example_3_custom_configuration():
    """
    Example 3: Using custom configuration
    """
    print("=" * 70)
    print("EXAMPLE 3: Custom Configuration")
    print("=" * 70)
    
    # Create custom user profile
    user_profile = UserProfile(
        name="John Doe",
        email="john.doe@example.com",
        phone="+91-9876543210",
        location="Bangalore",
        job_titles=[
            "Senior Data Scientist",
            "ML Engineer",
            "AI Research Scientist"
        ],
        skills=[
            "Python", "TensorFlow", "PyTorch", "Scikit-learn",
            "Deep Learning", "NLP", "Computer Vision",
            "LLMs", "Generative AI", "MLOps",
            "AWS", "Docker", "Kubernetes"
        ],
        locations=["Bangalore", "Mumbai", "Pune", "Remote"],
        experience_years=5,
        expected_salary_min=25,  # LPA
        expected_salary_max=40,
        max_applications_per_day=30,
        auto_apply=False
    )
    
    # Create custom agent configuration
    agent_config = AgentConfig(
        model="claude-sonnet-4-20250514",
        temperature=0.7,
        scrape_interval_hours=8,
        max_jobs_per_board=150,
        similarity_threshold=0.75,  # Higher threshold for better matches
        headless=True
    )
    
    # Initialize with custom config
    agent = JobApplicationAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        user_profile=user_profile,
        agent_config=agent_config
    )
    
    # Run pipeline
    results = agent.run_full_pipeline(
        resume_path="data/resumes/resume.pdf",
        platforms=['linkedin', 'naukri', 'instahyre'],
        max_applications=10,
        auto_submit=False
    )
    
    print(f"Applied to {len(results)} jobs with custom configuration")


def example_4_scheduled_execution():
    """
    Example 4: Scheduled execution (runs every N hours)
    """
    print("=" * 70)
    print("EXAMPLE 4: Scheduled Execution")
    print("=" * 70)
    
    agent = JobApplicationAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    print("Starting scheduled execution...")
    print("Will run every 6 hours. Press Ctrl+C to stop.")
    
    # This will run continuously
    agent.schedule_recurring_jobs(
        resume_path="data/resumes/resume.pdf",
        interval_hours=6
    )


def example_5_filtering_and_selection():
    """
    Example 5: Advanced filtering and job selection
    """
    print("=" * 70)
    print("EXAMPLE 5: Advanced Filtering")
    print("=" * 70)
    
    agent = JobApplicationAgent(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Parse resume
    parsed_resume = agent.load_and_parse_resume("data/resumes/resume.pdf")
    
    # Scrape jobs
    jobs = agent.scrape_jobs(
        platforms=['linkedin', 'indeed', 'naukri']
    )
    
    # Filter jobs before matching
    print(f"\nTotal jobs scraped: {len(jobs)}")
    
    # Filter by location
    bangalore_jobs = [j for j in jobs if 'bangalore' in j.location.lower()]
    print(f"Jobs in Bangalore: {len(bangalore_jobs)}")
    
    # Filter by work mode
    remote_jobs = [j for j in jobs if 'remote' in j.work_mode.lower()]
    print(f"Remote jobs: {len(remote_jobs)}")
    
    # Filter by company (example)
    target_companies = ['google', 'microsoft', 'amazon', 'meta', 'apple']
    faang_jobs = [j for j in jobs if any(company in j.company.lower() for company in target_companies)]
    print(f"FAANG jobs: {len(faang_jobs)}")
    
    # Match with filtered jobs
    if remote_jobs:
        print("\nMatching remote jobs...")
        agent.scraped_jobs = remote_jobs
        matches = agent.match_jobs(top_k=20)
        
        print(f"\nTop remote job matches:")
        for match in matches[:5]:
            print(f"- {match.job.title} at {match.job.company} ({match.match_score:.2%})")


def example_6_cover_letter_variations():
    """
    Example 6: Generate multiple cover letter variations
    """
    print("=" * 70)
    print("EXAMPLE 6: Cover Letter Variations")
    print("=" * 70)
    
    from cover_letter_generator import CoverLetterGenerator
    from resume_parser import ResumeParser
    
    # Setup
    api_key = os.getenv("ANTHROPIC_API_KEY")
    parser = ResumeParser(api_key)
    generator = CoverLetterGenerator(api_key)
    
    # Parse resume
    resume = parser.parse_resume("data/resumes/resume.pdf")
    
    # Create a sample job
    from job_scraper import JobListing
    from datetime import datetime
    
    sample_job = JobListing(
        job_id="example_123",
        title="Senior Data Scientist - GenAI",
        company="AI Startup Inc",
        location="Bangalore",
        job_type="Full-time",
        work_mode="Hybrid",
        salary="30-40 LPA",
        description="We're looking for an experienced data scientist to work on cutting-edge generative AI projects...",
        requirements="5+ years experience, Python, TensorFlow, PyTorch, LLMs",
        posted_date="2024-01-30",
        apply_url="https://example.com/apply",
        source="linkedin",
        scraped_at=datetime.now()
    )
    
    # Generate variations
    print("\nGenerating 3 cover letter variations...")
    variations = generator.generate_multiple_variations(
        resume=resume,
        job=sample_job,
        num_variations=3
    )
    
    print(f"\nGenerated {len(variations)} variations")
    print("\nVariation 1 (Preview):")
    print(variations[0][:200] + "...")


def example_7_analytics_and_tracking():
    """
    Example 7: Get analytics and application tracking
    """
    print("=" * 70)
    print("EXAMPLE 7: Analytics & Tracking")
    print("=" * 70)
    
    from application_automator import ApplicationTracker
    import sqlite3
    
    tracker = ApplicationTracker("data/job_applications.db")
    
    # Get statistics
    stats = tracker.get_application_stats()
    
    print("\n📊 Application Statistics:")
    print(f"Total Applications: {stats['total_applications']}")
    print(f"Applied: {stats['applied']}")
    print(f"Average Match Score: {stats['average_match_score']:.2%}")
    
    # Query database directly for more insights
    conn = sqlite3.connect("data/job_applications.db")
    cursor = conn.cursor()
    
    # Applications by source
    cursor.execute("""
        SELECT source, COUNT(*) as count 
        FROM applications 
        GROUP BY source 
        ORDER BY count DESC
    """)
    
    print("\n📍 Applications by Platform:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # Recent applications
    cursor.execute("""
        SELECT job_title, company, applied_at, match_score 
        FROM applications 
        ORDER BY applied_at DESC 
        LIMIT 5
    """)
    
    print("\n🕐 Recent Applications:")
    for row in cursor.fetchall():
        print(f"  {row[0]} at {row[1]} (Score: {row[3]:.2%})")
    
    conn.close()


def main():
    """
    Run examples based on user choice
    """
    print("\n" + "=" * 70)
    print("AI JOB APPLICATION AGENT - EXAMPLES")
    print("=" * 70)
    print("\nAvailable examples:")
    print("1. Basic Usage - Complete pipeline")
    print("2. Step-by-Step Execution")
    print("3. Custom Configuration")
    print("4. Scheduled Execution")
    print("5. Advanced Filtering")
    print("6. Cover Letter Variations")
    print("7. Analytics & Tracking")
    print("8. Run All Examples (except scheduled)")
    
    choice = input("\nSelect an example (1-8): ").strip()
    
    examples = {
        '1': example_1_basic_usage,
        '2': example_2_step_by_step,
        '3': example_3_custom_configuration,
        '4': example_4_scheduled_execution,
        '5': example_5_filtering_and_selection,
        '6': example_6_cover_letter_variations,
        '7': example_7_analytics_and_tracking,
    }
    
    if choice == '8':
        # Run all examples except scheduled
        for key in ['1', '2', '3', '5', '6', '7']:
            try:
                examples[key]()
                print("\n" + "-" * 70 + "\n")
            except Exception as e:
                print(f"Error in example {key}: {e}")
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-key'")
        print()
    
    main()
