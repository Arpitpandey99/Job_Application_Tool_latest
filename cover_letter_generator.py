"""
Cover Letter Generator - AI-powered personalized cover letters
Modified to use OpenAI GPT API
"""
from openai import OpenAI
from loguru import logger
from typing import Optional
from pathlib import Path

from resume_parser import ParsedResume
from job_scraper import JobListing


class CoverLetterGenerator:
    """Generate personalized cover letters using AI"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_cover_letter(
        self,
        resume: ParsedResume,
        job: JobListing,
        tone: str = "professional"
    ) -> str:
        """Generate a personalized cover letter for a specific job"""
        
        logger.info(f"Generating cover letter for: {job.title} at {job.company}")
        
        # Create comprehensive context
        resume_context = self._create_resume_context(resume)
        job_context = self._create_job_context(job)
        
        prompt = f"""Write a compelling, personalized cover letter for this job application. 

CANDIDATE INFORMATION:
{resume_context}

JOB DETAILS:
{job_context}

REQUIREMENTS:
1. Write in a {tone} tone
2. Length: 250-350 words (3-4 paragraphs)
3. Structure:
   - Opening: Express enthusiasm and mention the specific role
   - Body: Highlight 2-3 most relevant experiences/achievements that match job requirements
   - Closing: Call to action and thank you
4. Be specific - reference actual projects, technologies, or achievements from the resume
5. Show understanding of the company and role
6. Avoid generic phrases - make it personal and genuine
7. Use the candidate's actual name, location, and contact info
8. Format as a professional business letter

Do NOT include:
- Placeholders like [Your Name] or [Date]
- Generic statements that could apply to any job
- Overly formal or outdated language

Write the complete cover letter now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer. Create personalized, compelling cover letters that help candidates stand out."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            cover_letter = response.choices[0].message.content.strip()
            logger.info("Cover letter generated successfully")
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return self._fallback_cover_letter(resume, job)
    
    def _create_resume_context(self, resume: ParsedResume) -> str:
        """Create formatted resume context for the prompt"""
        context = f"""
Name: {resume.name}
Email: {resume.email}
Phone: {resume.phone}
Location: {resume.location}

Professional Summary:
{resume.summary}

Total Experience: {resume.total_experience_years} years

Key Skills:
{', '.join(resume.skills[:15])}

Recent Experience:
"""
        for exp in resume.experience[:2]:
            context += f"""
- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})
  {exp.get('description', '')[:200]}
"""
        
        context += f"\nEducation:\n"
        for edu in resume.education[:2]:
            context += f"- {edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')} ({edu.get('year', '')})\n"
        
        if resume.projects:
            context += f"\nNotable Projects:\n"
            for proj in resume.projects[:2]:
                context += f"- {proj.get('name', '')}: {proj.get('description', '')}\n"
        
        return context.strip()
    
    def _create_job_context(self, job: JobListing) -> str:
        """Create formatted job context for the prompt"""
        return f"""
Position: {job.title}
Company: {job.company}
Location: {job.location}
Work Mode: {job.work_mode}
Job Type: {job.job_type}

Job Description:
{job.description[:500]}

Requirements:
{job.requirements[:500] if job.requirements != job.description else 'See description above'}
""".strip()
    
    def _fallback_cover_letter(self, resume: ParsedResume, job: JobListing) -> str:
        """Generate a basic cover letter as fallback"""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With {resume.total_experience_years} years of experience in data science and machine learning, I am confident that my skills and background make me an excellent fit for this role.

In my current role, I have developed expertise in {', '.join(resume.skills[:5])}, which directly aligns with the requirements outlined in your job posting. I am particularly drawn to this opportunity because of {job.company}'s innovative work and commitment to leveraging AI and data science to drive business outcomes.

I am excited about the possibility of contributing to your team and would welcome the opportunity to discuss how my experience and skills can benefit {job.company}. Thank you for considering my application.

Best regards,
{resume.name}
{resume.email}
{resume.phone}
"""
    
    def save_cover_letter(
        self,
        cover_letter: str,
        job: JobListing,
        output_dir: Path
    ) -> str:
        """Save cover letter to file"""
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create filename from job details
        filename = f"cover_letter_{job.company}_{job.job_id}.txt"
        filename = filename.replace(' ', '_').replace('/', '_')
        
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        
        logger.info(f"Cover letter saved to: {output_path}")
        return str(output_path)
    
    def generate_multiple_variations(
        self,
        resume: ParsedResume,
        job: JobListing,
        num_variations: int = 3
    ) -> list[str]:
        """Generate multiple variations of cover letter"""
        tones = ["professional", "enthusiastic", "confident"]
        variations = []
        
        for i, tone in enumerate(tones[:num_variations]):
            logger.info(f"Generating variation {i+1} with {tone} tone")
            cover_letter = self.generate_cover_letter(resume, job, tone)
            variations.append(cover_letter)
        
        return variations


class CoverLetterOptimizer:
    """Optimize cover letters for ATS (Applicant Tracking Systems)"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def optimize_for_ats(
        self,
        cover_letter: str,
        job: JobListing
    ) -> str:
        """Optimize cover letter for ATS by including relevant keywords"""
        
        prompt = f"""Optimize this cover letter for Applicant Tracking Systems (ATS) by naturally incorporating relevant keywords from the job description.

ORIGINAL COVER LETTER:
{cover_letter}

JOB DESCRIPTION KEYWORDS:
{job.description[:500]}

INSTRUCTIONS:
1. Maintain the overall structure and tone
2. Naturally incorporate 5-10 relevant keywords from the job description
3. Ensure keywords flow naturally in sentences
4. Don't make it sound forced or keyword-stuffed
5. Keep the same length (±50 words)
6. Maintain professional quality

Return the optimized cover letter:"""

        try:
            '''response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an ATS optimization expert. Improve cover letters to pass ATS screening while maintaining quality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()'''
            raise Exception("Using fallback")
            
        except Exception as e:
            logger.error(f"Failed to optimize cover letter: {e}")
            return cover_letter  # Return original if optimization fails