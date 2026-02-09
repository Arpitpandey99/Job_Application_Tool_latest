"""
Job Matcher - AI-powered job matching using semantic similarity
Modified to use OpenAI GPT API
Falls back to TF-IDF matching when sentence-transformers model unavailable
"""
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from dataclasses import dataclass
from openai import OpenAI
from loguru import logger
import json

from resume_parser import ParsedResume
from job_scraper import JobListing


@dataclass
class JobMatch:
    """Job match with score and reasoning"""
    job: JobListing
    match_score: float
    skill_match_percentage: float
    reasoning: str
    missing_skills: List[str]
    matching_skills: List[str]


class JobMatcher:
    """Match jobs with resume using semantic similarity and AI reasoning"""

    def __init__(self, api_key: str, similarity_threshold: float = 0.7, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.similarity_threshold = similarity_threshold
        self.embedding_model = None
        self.use_tfidf = False

        # Try to load sentence transformer, fall back to TF-IDF
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            logger.warning(f"Sentence transformer unavailable ({e}), using TF-IDF matching")
            self.use_tfidf = True
            self.tfidf = TfidfVectorizer(stop_words='english', max_features=5000)

    def match_jobs(
        self,
        resume: ParsedResume,
        jobs: List[JobListing],
        top_k: int = 20
    ) -> List[JobMatch]:
        """Match jobs with resume and return top matches"""

        logger.info(f"Matching {len(jobs)} jobs with resume...")

        resume_text = self._create_resume_text(resume)
        matches = []

        if self.use_tfidf:
            matches = self._match_with_tfidf(resume, resume_text, jobs)
        else:
            resume_embedding = self.embedding_model.encode([resume_text])[0]
            for job in jobs:
                try:
                    job_text = self._create_job_text(job)
                    job_embedding = self.embedding_model.encode([job_text])[0]
                    similarity = cosine_similarity([resume_embedding], [job_embedding])[0][0]
                    skill_match = self._calculate_skill_match(resume, job)
                    match_score = 0.7 * similarity + 0.3 * skill_match['percentage']

                    if match_score >= self.similarity_threshold:
                        reasoning = self._get_ai_reasoning(resume, job, match_score)
                        matches.append(JobMatch(
                            job=job, match_score=match_score,
                            skill_match_percentage=skill_match['percentage'],
                            reasoning=reasoning,
                            missing_skills=skill_match['missing'],
                            matching_skills=skill_match['matching']
                        ))
                except Exception as e:
                    logger.warning(f"Error matching job {job.job_id}: {e}")
                    continue

        matches.sort(key=lambda x: x.match_score, reverse=True)
        logger.info(f"Found {len(matches)} matching jobs (threshold: {self.similarity_threshold})")
        return matches[:top_k]

    def _match_with_tfidf(self, resume: ParsedResume, resume_text: str, jobs: List[JobListing]) -> List['JobMatch']:
        """Fallback matching using TF-IDF when sentence-transformers is unavailable"""
        matches = []
        job_texts = [self._create_job_text(job) for job in jobs]
        all_texts = [resume_text] + job_texts

        tfidf_matrix = self.tfidf.fit_transform(all_texts)
        resume_vec = tfidf_matrix[0:1]
        job_vecs = tfidf_matrix[1:]
        similarities = cosine_similarity(resume_vec, job_vecs)[0]

        for i, (job, similarity) in enumerate(zip(jobs, similarities)):
            skill_match = self._calculate_skill_match(resume, job)
            match_score = 0.6 * similarity + 0.4 * skill_match['percentage']

            if match_score >= self.similarity_threshold:
                reasoning = self._get_ai_reasoning(resume, job, match_score)
                matches.append(JobMatch(
                    job=job, match_score=match_score,
                    skill_match_percentage=skill_match['percentage'],
                    reasoning=reasoning,
                    missing_skills=skill_match['missing'],
                    matching_skills=skill_match['matching']
                ))
        return matches
    
    def _create_resume_text(self, resume: ParsedResume) -> str:
        """Create searchable text from resume"""
        text_parts = [
            resume.summary,
            f"Skills: {', '.join(resume.skills)}",
        ]
        
        # Add experience
        for exp in resume.experience:
            text_parts.append(
                f"{exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')}"
            )
        
        # Add education
        for edu in resume.education:
            text_parts.append(
                f"{edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
            )
        
        return " ".join(text_parts)
    
    def _create_job_text(self, job: JobListing) -> str:
        """Create searchable text from job listing"""
        return f"{job.title} at {job.company}. {job.description} {job.requirements}"
    
    def _calculate_skill_match(self, resume: ParsedResume, job: JobListing) -> Dict:
        """Calculate skill match percentage"""
        resume_skills = set([skill.lower() for skill in resume.skills])
        
        # Extract skills from job description
        job_text = f"{job.description} {job.requirements}".lower()
        
        # Find matching skills
        matching_skills = []
        for skill in resume_skills:
            if skill in job_text:
                matching_skills.append(skill)
        
        # Estimate required skills from job description
        # This is a simplified approach - can be enhanced with NER
        common_tech_skills = [
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
            'kubernetes', 'tensorflow', 'pytorch', 'machine learning',
            'deep learning', 'nlp', 'computer vision', 'data science',
            'ml', 'ai', 'generative ai', 'llm', 'genai'
        ]
        
        job_required_skills = [skill for skill in common_tech_skills if skill in job_text]
        
        if not job_required_skills:
            # If we can't extract skills, assume high match
            percentage = 0.8
            missing = []
        else:
            matching_count = len([s for s in job_required_skills if s in resume_skills])
            percentage = matching_count / len(job_required_skills) if job_required_skills else 0.8
            missing = [s for s in job_required_skills if s not in resume_skills]
        
        return {
            'percentage': percentage,
            'matching': matching_skills,
            'missing': missing
        }
    
    def _get_ai_reasoning(
        self,
        resume: ParsedResume,
        job: JobListing,
        match_score: float
    ) -> str:
        """Get AI reasoning for why this job matches"""
        
        prompt = f"""Analyze why this job is a good match for this candidate. Be concise (2-3 sentences).

Candidate Profile:
- Name: {resume.name}
- Experience: {resume.total_experience_years} years
- Top Skills: {', '.join(resume.skills[:10])}
- Recent Role: {resume.experience[0].get('title', '') if resume.experience else 'N/A'}

Job:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Brief Description: {job.description[:300]}

Match Score: {match_score:.2f}

Provide a brief, professional explanation of why this is a good fit. Focus on skill alignment and experience relevance."""

        try:
            '''response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a career advisor analyzing job matches. Provide concise, helpful explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )'''
            
            #return response.choices[0].message.content.strip()
            return f"Strong match based on {resume.total_experience_years} years experience in {', '.join(resume.skills[:3])}. Skills align well with job requirements."
            
        except Exception as e:
            logger.warning(f"Could not get AI reasoning: {e}")
            return f"This position aligns well with your {resume.total_experience_years} years of experience and skill set."
    
    def create_match_report(
        self,
        resume: ParsedResume,
        matches: List[JobMatch],
        output_path: str = None
    ) -> str:
        """Create a detailed match report"""
        
        report = f"""
JOB MATCH REPORT
Generated: {matches[0].job.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if matches and hasattr(matches[0].job, 'scraped_at') else 'N/A'}

CANDIDATE: {resume.name}
EXPERIENCE: {resume.total_experience_years} years
LOCATION: {resume.location}

TOP SKILLS:
{', '.join(resume.skills[:15])}

===================================
TOP MATCHING JOBS ({len(matches)})
===================================

"""
        
        for i, match in enumerate(matches, 1):
            job = match.job
            report += f"""
{i}. {job.title}
   Company: {job.company}
   Location: {job.location} | {job.work_mode}
   Match Score: {match.match_score:.2%}
   Skill Match: {match.skill_match_percentage:.1%}
   
   Why it's a good fit:
   {match.reasoning}
   
   Matching Skills: {', '.join(match.matching_skills[:10])}
   {f"Skills to develop: {', '.join(match.missing_skills[:5])}" if match.missing_skills else ""}
   
   Apply at: {job.apply_url}
   
   ---
"""
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Match report saved to: {output_path}")
        
        return report