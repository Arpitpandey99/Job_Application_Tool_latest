"""
Job Application Tool - Web UI
Streamlit-based interface for the AI job automation pipeline.
"""
import streamlit as st
import os
import json
import time
from datetime import datetime
from pathlib import Path
import tempfile

# Page config
st.set_page_config(
    page_title="AI Job Application Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = DATA_DIR / "resumes"
APPLICATIONS_DIR = DATA_DIR / "applications"
JOBS_DIR = DATA_DIR / "jobs"
LOGS_DIR = DATA_DIR / "logs"

for d in [DATA_DIR, RESUMES_DIR, APPLICATIONS_DIR, JOBS_DIR, LOGS_DIR, APPLICATIONS_DIR / "cover_letters"]:
    d.mkdir(exist_ok=True, parents=True)


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "resume_parsed": False,
        "parsed_resume": None,
        "scraped_jobs": {},
        "matches": {},
        "cover_letters": {},
        "pipeline_running": False,
        "pipeline_log": [],
        "run_complete": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def log(msg: str):
    """Add message to pipeline log"""
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.pipeline_log.append(f"[{ts}] {msg}")


# ─── SIDEBAR ────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.title("Configuration")

        # API Key
        st.subheader("OpenAI API Key")
        api_key = st.text_input(
            "API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Your OpenAI API key. Also reads from OPENAI_API_KEY env var."
        )

        # Resume Upload
        st.subheader("Resume")
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        existing_resume = RESUMES_DIR / "resume.pdf"
        if uploaded_file:
            resume_path = RESUMES_DIR / uploaded_file.name
            resume_path.write_bytes(uploaded_file.getvalue())
            st.success(f"Uploaded: {uploaded_file.name}")
        elif existing_resume.exists():
            resume_path = existing_resume
            st.info("Using existing resume.pdf")
        else:
            resume_path = None
            st.warning("Please upload a resume PDF")

        # Platform Selection
        st.subheader("Platforms")
        platforms = []
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.checkbox("LinkedIn", value=True):
                platforms.append("linkedin")
        with col2:
            if st.checkbox("Indeed", value=True):
                platforms.append("indeed")
        with col3:
            if st.checkbox("Naukri", value=True):
                platforms.append("naukri")

        # Platform Credentials
        st.subheader("Login Credentials")
        credentials = {}

        with st.expander("LinkedIn Login", expanded=False):
            li_email = st.text_input("LinkedIn Email", key="li_email")
            li_pass = st.text_input("LinkedIn Password", type="password", key="li_pass")
            if li_email and li_pass:
                credentials["linkedin"] = {"email": li_email, "password": li_pass}

        with st.expander("Indeed Login", expanded=False):
            in_email = st.text_input("Indeed Email", key="in_email")
            in_pass = st.text_input("Indeed Password", type="password", key="in_pass")
            if in_email and in_pass:
                credentials["indeed"] = {"email": in_email, "password": in_pass}

        with st.expander("Naukri Login", expanded=False):
            nk_email = st.text_input("Naukri Email", key="nk_email")
            nk_pass = st.text_input("Naukri Password", type="password", key="nk_pass")
            if nk_email and nk_pass:
                credentials["naukri"] = {"email": nk_email, "password": nk_pass}

        # Hyperparameters
        st.subheader("Hyperparameters")
        max_jobs = st.slider("Max Jobs per Platform", 5, 50, 10, step=5)
        similarity_threshold = st.slider("Match Threshold", 0.1, 0.9, 0.3, step=0.05,
                                         help="Lower = more matches, Higher = stricter matching")
        model = st.selectbox("OpenAI Model", ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini", "gpt-4o"],
                             help="gpt-3.5-turbo is cheapest. gpt-4o-mini is a good balance.")
        generate_cover_letters = st.checkbox("Generate Cover Letters", value=True)
        auto_submit = st.checkbox("Auto-Submit Applications", value=False,
                                  help="WARNING: Will actually submit applications!")

        if auto_submit:
            st.warning("Auto-submit is ON. Applications will be submitted!")

        # Job Preferences
        st.subheader("Job Preferences")
        keywords = st.text_input("Search Keywords", value="data scientist")
        location = st.text_input("Location", value="India")

        return {
            "api_key": api_key,
            "resume_path": str(resume_path) if resume_path else None,
            "platforms": platforms,
            "credentials": credentials,
            "max_jobs": max_jobs,
            "similarity_threshold": similarity_threshold,
            "model": model,
            "generate_cover_letters": generate_cover_letters,
            "auto_submit": auto_submit,
            "keywords": keywords,
            "location": location,
        }


# ─── PIPELINE STEPS ─────────────────────────────────────────────────

def run_parse_resume(config, status_container):
    """Parse resume"""
    status_container.info("Parsing resume...")
    log("Parsing resume...")

    from resume_parser import ResumeParser, ParsedResume

    # Check for cached parsed resume
    cached = DATA_DIR / "parsed_resume.json"
    if cached.exists():
        with open(cached) as f:
            data = json.load(f)
        resume = ParsedResume(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            location=data.get("location", "India"),
            summary=data.get("summary", ""),
            skills=data.get("skills", []),
            experience=data.get("experience", []),
            education=data.get("education", []),
            certifications=data.get("certifications", []),
            projects=data.get("projects", []),
            total_experience_years=data.get("total_experience_years", 0),
            raw_text=data.get("raw_text", "")
        )
        log(f"Loaded cached resume for {resume.name}")
    else:
        parser = ResumeParser(config["api_key"], model=config["model"])
        resume = parser.parse_resume(config["resume_path"])
        # Cache it
        resume_data = {
            "name": resume.name, "email": resume.email, "phone": resume.phone,
            "location": resume.location, "summary": resume.summary,
            "skills": resume.skills, "experience": resume.experience,
            "education": resume.education, "certifications": resume.certifications,
            "projects": resume.projects, "total_experience_years": resume.total_experience_years,
        }
        with open(cached, 'w') as f:
            json.dump(resume_data, f, indent=2)
        log(f"Parsed resume for {resume.name} ({len(resume.skills)} skills)")

    st.session_state.parsed_resume = resume
    st.session_state.resume_parsed = True
    status_container.success(f"Resume parsed: {resume.name} | {resume.total_experience_years}yr exp | {len(resume.skills)} skills")
    return resume


def run_scraping(config, status_container):
    """Scrape jobs from selected platforms"""
    from job_scraper import LinkedInScraper, IndeedScraper, NaukriScraper

    scrapers = {
        'linkedin': LinkedInScraper,
        'indeed': IndeedScraper,
        'naukri': NaukriScraper,
    }

    all_jobs = {}
    for platform in config["platforms"]:
        status_container.info(f"Scraping {platform.upper()}...")
        log(f"Scraping {platform}...")

        scraper = scrapers[platform]()
        try:
            jobs = scraper.scrape_jobs(config["keywords"], config["location"], config["max_jobs"])
        except Exception as e:
            log(f"{platform} scraping error: {e}")
            jobs = []

        all_jobs[platform] = jobs
        log(f"{platform}: {len(jobs)} jobs found")

        if jobs:
            status_container.success(f"{platform.upper()}: {len(jobs)} jobs scraped")
        else:
            status_container.warning(f"{platform.upper()}: 0 jobs (site may be blocked or require login)")

    # Save jobs
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for platform, jobs in all_jobs.items():
        if jobs:
            job_data = [{"job_id": j.job_id, "title": j.title, "company": j.company,
                         "location": j.location, "source": j.source, "apply_url": j.apply_url,
                         "description": j.description[:500]} for j in jobs]
            with open(JOBS_DIR / f"scraped_{platform}_{ts}.json", 'w') as f:
                json.dump(job_data, f, indent=2)

    st.session_state.scraped_jobs = all_jobs
    total = sum(len(j) for j in all_jobs.values())
    log(f"Total jobs scraped: {total}")
    return all_jobs


def run_matching(config, resume, all_jobs, status_container):
    """Match jobs with resume"""
    from job_matcher import JobMatcher

    status_container.info("Matching jobs with resume...")
    log("Running job matching...")

    matcher = JobMatcher(
        config["api_key"],
        similarity_threshold=config["similarity_threshold"],
        model=config["model"]
    )

    all_matches = {}
    for platform, jobs in all_jobs.items():
        if not jobs:
            all_matches[platform] = []
            continue

        matches = matcher.match_jobs(resume, jobs, top_k=config["max_jobs"])
        all_matches[platform] = matches
        log(f"{platform}: {len(matches)} matches found")

    st.session_state.matches = all_matches
    total = sum(len(m) for m in all_matches.values())
    status_container.success(f"Matching complete: {total} total matches")
    return all_matches


def run_cover_letters(config, resume, all_matches, status_container):
    """Generate cover letters"""
    from cover_letter_generator import CoverLetterGenerator

    status_container.info("Generating cover letters...")
    log("Generating cover letters...")

    generator = CoverLetterGenerator(config["api_key"], model=config["model"])
    all_letters = {}

    for platform, matches in all_matches.items():
        for match in matches[:3]:  # Max 3 per platform to save tokens
            try:
                letter = generator.generate_cover_letter(resume, match.job)
                path = generator.save_cover_letter(
                    letter, match.job, APPLICATIONS_DIR / "cover_letters"
                )
                all_letters[match.job.job_id] = {"path": path, "content": letter}
                log(f"Cover letter: {match.job.title} at {match.job.company}")
            except Exception as e:
                log(f"Cover letter error: {e}")

    st.session_state.cover_letters = all_letters
    status_container.success(f"{len(all_letters)} cover letters generated")
    return all_letters


def run_tracking(all_matches, status_container):
    """Track applications in database"""
    from application_automator import ApplicationTracker

    tracker = ApplicationTracker(str(DATA_DIR / "job_applications.db"))
    count = 0

    for platform, matches in all_matches.items():
        for match in matches:
            tracker.add_application({
                'job_id': match.job.job_id,
                'job_title': match.job.title,
                'company': match.job.company,
                'source': match.job.source,
                'match_score': match.match_score,
            })
            count += 1

    stats = tracker.get_application_stats()
    status_container.success(f"Tracked {count} applications (DB total: {stats['total_applications']})")
    log(f"Tracked {count} applications")
    return stats


# ─── MAIN UI ─────────────────────────────────────────────────────────

def render_main(config):
    st.title("AI Job Application Tool")
    st.caption("Automated job search, matching, and application for Data Science roles")

    # Validation
    if not config["api_key"]:
        st.error("Please enter your OpenAI API key in the sidebar.")
        return
    if not config["resume_path"]:
        st.error("Please upload a resume PDF in the sidebar.")
        return
    if not config["platforms"]:
        st.error("Please select at least one platform in the sidebar.")
        return

    # Config summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Platforms", len(config["platforms"]))
    col2.metric("Max Jobs/Platform", config["max_jobs"])
    col3.metric("Match Threshold", f"{config['similarity_threshold']:.0%}")
    col4.metric("Model", config["model"])

    st.divider()

    # Run button
    if st.button("Run Pipeline", type="primary", use_container_width=True,
                  disabled=st.session_state.pipeline_running):
        st.session_state.pipeline_running = True
        st.session_state.pipeline_log = []
        st.session_state.run_complete = False
        run_pipeline(config)
        st.session_state.pipeline_running = False
        st.session_state.run_complete = True
        st.rerun()

    # Show results if pipeline has been run
    if st.session_state.run_complete:
        render_results()

    # Pipeline log
    if st.session_state.pipeline_log:
        with st.expander("Pipeline Log", expanded=False):
            st.code("\n".join(st.session_state.pipeline_log), language="text")


def run_pipeline(config):
    """Execute the full pipeline"""
    progress = st.progress(0, text="Starting pipeline...")
    status = st.status("Running pipeline...", expanded=True)

    # Step 1: Parse Resume
    progress.progress(10, text="Parsing resume...")
    resume = run_parse_resume(config, status)

    # Step 2: Scrape Jobs
    progress.progress(30, text="Scraping jobs...")
    all_jobs = run_scraping(config, status)

    total_jobs = sum(len(j) for j in all_jobs.values())
    if total_jobs == 0:
        status.warning("No jobs scraped. Sites may be blocked. Check your network.")
        progress.progress(100, text="Done (no jobs found)")
        return

    # Step 3: Match Jobs
    progress.progress(60, text="Matching jobs...")
    all_matches = run_matching(config, resume, all_jobs, status)

    # Step 4: Cover Letters
    if config["generate_cover_letters"]:
        progress.progress(80, text="Generating cover letters...")
        run_cover_letters(config, resume, all_matches, status)

    # Step 5: Track Applications
    progress.progress(90, text="Tracking applications...")
    run_tracking(all_matches, status)

    progress.progress(100, text="Pipeline complete!")
    status.update(label="Pipeline complete!", state="complete")


def render_results():
    """Render pipeline results"""
    st.subheader("Results")

    # Tabs for each section
    tab_matches, tab_letters, tab_stats = st.tabs(["Job Matches", "Cover Letters", "Statistics"])

    with tab_matches:
        matches = st.session_state.matches
        if not matches or all(len(m) == 0 for m in matches.values()):
            st.info("No matches found. Try lowering the match threshold.")
        else:
            for platform, platform_matches in matches.items():
                if not platform_matches:
                    continue
                st.markdown(f"### {platform.upper()} ({len(platform_matches)} matches)")
                for i, match in enumerate(platform_matches, 1):
                    job = match.job
                    with st.expander(
                        f"{i}. {job.title} at {job.company} — {match.match_score:.0%} match",
                        expanded=(i <= 2)
                    ):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Match Score", f"{match.match_score:.1%}")
                        col2.metric("Skill Match", f"{match.skill_match_percentage:.0%}")
                        col3.metric("Location", job.location)

                        st.markdown(f"**Work Mode:** {job.work_mode} | **Type:** {job.job_type}")
                        st.markdown(f"**Matching Skills:** {', '.join(match.matching_skills[:8])}")
                        if match.missing_skills:
                            st.markdown(f"**Missing Skills:** {', '.join(match.missing_skills[:5])}")
                        st.markdown(f"**Why it fits:** {match.reasoning}")

                        if job.description:
                            with st.popover("View Description"):
                                st.write(job.description[:1000])

                        if job.apply_url:
                            st.link_button("Apply", job.apply_url)

    with tab_letters:
        letters = st.session_state.cover_letters
        if not letters:
            st.info("No cover letters generated.")
        else:
            for job_id, letter_data in letters.items():
                with st.expander(f"Cover Letter — {job_id}", expanded=False):
                    st.text_area("", letter_data["content"], height=300, key=f"cl_{job_id}")
                    st.download_button(
                        "Download",
                        letter_data["content"],
                        file_name=f"cover_letter_{job_id}.txt",
                        key=f"dl_{job_id}"
                    )

    with tab_stats:
        resume = st.session_state.parsed_resume
        if resume:
            st.markdown("#### Candidate Profile")
            col1, col2 = st.columns(2)
            col1.write(f"**Name:** {resume.name}")
            col1.write(f"**Email:** {resume.email}")
            col1.write(f"**Phone:** {resume.phone}")
            col2.write(f"**Experience:** {resume.total_experience_years} years")
            col2.write(f"**Skills:** {len(resume.skills)}")
            col2.write(f"**Location:** {resume.location or 'India'}")

        st.markdown("#### Pipeline Summary")
        total_jobs = sum(len(j) for j in st.session_state.scraped_jobs.values())
        total_matches = sum(len(m) for m in st.session_state.matches.values())
        total_letters = len(st.session_state.cover_letters)

        col1, col2, col3 = st.columns(3)
        col1.metric("Jobs Scraped", total_jobs)
        col2.metric("Jobs Matched", total_matches)
        col3.metric("Cover Letters", total_letters)

        # Per-platform breakdown
        st.markdown("#### Per Platform")
        for platform in st.session_state.scraped_jobs:
            jobs = len(st.session_state.scraped_jobs.get(platform, []))
            matched = len(st.session_state.matches.get(platform, []))
            st.write(f"**{platform.upper()}:** {jobs} scraped, {matched} matched")

        # DB stats
        try:
            from application_automator import ApplicationTracker
            tracker = ApplicationTracker(str(DATA_DIR / "job_applications.db"))
            stats = tracker.get_application_stats()
            st.markdown("#### Application Database")
            st.write(f"Total tracked: **{stats['total_applications']}** | Avg score: **{stats['average_match_score']:.1%}**")
        except Exception:
            pass


# ─── ENTRY POINT ─────────────────────────────────────────────────────

def main():
    init_session_state()
    config = render_sidebar()
    render_main(config)


if __name__ == "__main__":
    main()
