#!/usr/bin/env python3
"""
Setup Script for AI Job Application Agent (OpenAI GPT Version)

This script helps you get started with the job application agent.
"""
import os
import sys
from pathlib import Path
import subprocess

def print_header(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    print("Installing Python packages from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is installed"""
    print("\nChecking for ChromeDriver...")
    try:
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ ChromeDriver found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ ChromeDriver not found!")
    print("\nInstallation instructions:")
    print("  macOS: brew install chromedriver")
    print("  Ubuntu/Debian: sudo apt-get install chromium-chromedriver")
    print("  Manual: https://chromedriver.chromium.org/downloads")
    return False

def setup_directories():
    """Create necessary directories"""
    print_header("Setting Up Directories")
    
    directories = [
        "data",
        "data/resumes",
        "data/jobs",
        "data/applications",
        "data/applications/cover_letters",
        "logs"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(exist_ok=True, parents=True)
        print(f"✅ Created: {dir_path}/")
    
    return True

def setup_env_file():
    """Setup .env file for API keys"""
    print_header("Setting Up Environment Variables")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Skipping .env setup")
            return True
    
    print("\n🔑 You need an OpenAI API key to use GPT models.")
    print("Get one at: https://platform.openai.com/api-keys")
    print("\n💡 Free tier users should use gpt-3.5-turbo model")
    
    api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        with open(env_file, 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ .env file created with your API key")
    else:
        print("⚠️  Skipped API key setup")
        print("   Remember to set OPENAI_API_KEY environment variable")
    
    return True

def create_sample_resume():
    """Create a sample resume template"""
    print_header("Resume Setup")
    
    resume_path = Path("data/resumes/resume.pdf")
    
    if resume_path.exists():
        print("✅ Resume already exists at data/resumes/resume.pdf")
        return True
    
    print("⚠️  No resume found!")
    print("\nPlease place your resume (PDF format) at:")
    print("   data/resumes/resume.pdf")
    print("\nYou can also specify a different path when running the agent.")
    
    return True

def download_spacy_model():
    """Download spaCy model if needed"""
    print_header("Optional: NLP Model Setup")
    
    print("Would you like to download the spaCy NLP model?")
    print("This improves resume parsing but is optional (150MB download)")
    
    download = input("Download spaCy model? (y/n): ").lower()
    
    if download == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            print("✅ spaCy model downloaded successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to download spaCy model")
            print("   You can download it later with: python -m spacy download en_core_web_sm")
    else:
        print("Skipped spaCy model download")
    
    return True

def test_installation():
    """Test if everything is working"""
    print_header("Testing Installation")
    
    print("Testing imports...")
    try:
        import openai
        import selenium
        import bs4
        import pandas
        import sentence_transformers
        print("✅ All core packages imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ API key found in environment")
    else:
        print("⚠️  API key not found in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
    
    return True

def show_next_steps():
    """Show next steps to the user"""
    print_header("Setup Complete! 🎉")
    
    print("📌 IMPORTANT: This version uses OpenAI GPT instead of Anthropic Claude")
    print("   - Default model: gpt-3.5-turbo (cost-effective for free tier)")
    print("   - You can upgrade to gpt-4 in config.py if needed")
    
    print("\nNext steps:")
    print("\n1. Place your resume at: data/resumes/resume.pdf")
    print("   (Or note the path to your resume)")
    
    print("\n2. Set your API key (if not done already):")
    print("   export OPENAI_API_KEY='your-api-key'")
    
    print("\n3. Try the examples:")
    print("   python examples.py")
    
    print("\n4. Or run the agent directly:")
    print("   python agent.py --resume data/resumes/resume.pdf --max-apps 5")
    
    print("\n5. Open the dashboard:")
    print("   open dashboard.html")
    
    print("\n6. Read the documentation:")
    print("   cat README.md")
    
    print("\n💰 Cost Management Tips for Free Tier:")
    print("   - Start with small batches (5-10 applications)")
    print("   - Use gpt-3.5-turbo (default, most economical)")
    print("   - Monitor your OpenAI usage dashboard")
    print("   - Free tier has rate limits - agent includes delays")
    
    print("\n" + "=" * 70)
    print("Happy job hunting! 🚀")
    print("=" * 70 + "\n")

def main():
    """Main setup function"""
    print("\n" + "=" * 70)
    print("AI JOB APPLICATION AGENT - SETUP (OpenAI GPT Version)")
    print("=" * 70)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Checking ChromeDriver", check_chromedriver),
        ("Setting up directories", setup_directories),
        ("Setting up environment", setup_env_file),
        ("Checking resume", create_sample_resume),
        ("Optional NLP setup", download_spacy_model),
        ("Testing installation", test_installation),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                print(f"\n⚠️  {step_name} had issues, but continuing...")
        except Exception as e:
            print(f"\n❌ Error during {step_name}: {e}")
            print("Continuing with setup...")
    
    show_next_steps()

if __name__ == "__main__":
    main()