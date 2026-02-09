"""
Resume Parser - Extracts structured information from resume PDFs
Modified to use OpenAI GPT API
"""
import re
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from loguru import logger


@dataclass
class ParsedResume:
    """Structured resume data"""
    name: str
    email: str
    phone: str
    location: str
    summary: str
    skills: List[str]
    experience: List[Dict]
    education: List[Dict]
    certifications: List[str]
    projects: List[Dict]
    total_experience_years: float
    raw_text: str


class ResumeParser:
    """Parse resumes using AI to extract structured information"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods for robustness"""
        text = ""
        
        # Method 1: pdfplumber (better for formatted text)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
        
        # Method 2: PyPDF2 (fallback)
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                logger.error(f"PyPDF2 also failed: {e}")
                
        return text.strip()
    
    def parse_resume_with_ai(self, resume_text: str) -> ParsedResume:
        """Use GPT to parse resume into structured format"""
        
        prompt = f"""Analyze this resume and extract structured information. Be thorough and precise.

Resume Text:
{resume_text}

Extract the following information and return ONLY a valid JSON object with this exact structure:
{{
    "name": "Full name of the candidate",
    "email": "Email address",
    "phone": "Phone number",
    "location": "Current location/city",
    "summary": "Professional summary or objective (2-3 sentences)",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start - End (e.g., Jan 2020 - Present)",
            "years": 2.5,
            "description": "Brief description of role and achievements"
        }}
    ],
    "education": [
        {{
            "degree": "Degree name",
            "institution": "University/College name",
            "year": "Graduation year",
            "field": "Field of study"
        }}
    ],
    "certifications": ["Certification 1", "Certification 2", ...],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"]
        }}
    ],
    "total_experience_years": 3.5
}}

Important:
- Extract ALL skills mentioned (technical, soft skills, tools, frameworks)
- Calculate total_experience_years accurately
- If information is missing, use empty string or empty array
- Return ONLY the JSON, no additional text"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Extract information accurately and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            import json
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
            
            parsed_data = json.loads(response_text)
            
            # Create ParsedResume object
            return ParsedResume(
                name=parsed_data.get("name", ""),
                email=parsed_data.get("email", ""),
                phone=parsed_data.get("phone", ""),
                location=parsed_data.get("location", ""),
                summary=parsed_data.get("summary", ""),
                skills=parsed_data.get("skills", []),
                experience=parsed_data.get("experience", []),
                education=parsed_data.get("education", []),
                certifications=parsed_data.get("certifications", []),
                projects=parsed_data.get("projects", []),
                total_experience_years=parsed_data.get("total_experience_years", 0.0),
                raw_text=resume_text
            )
            
        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            # Return basic parsed resume with raw text
            return self._fallback_parse(resume_text)
    
    def _fallback_parse(self, text: str) -> ParsedResume:
        """Enhanced fallback parsing using regex patterns"""
        import re
        
        # Basic email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Basic phone extraction
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        
        # Extract common tech skills
        common_skills = [
            'python', 'sql', 'aws', 'azure', 'docker',
            'genai', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data science', 'ml', 'ai', 'generative ai', 'llm', 
        ]
        
        text_lower = text.lower()
        found_skills = [skill for skill in common_skills if skill in text_lower]
        
        # Try to extract name (usually first line or after "Name:")
        name = ""
        lines = text.split('\n')
        for line in lines[:5]:
            if 'name' in line.lower():
                name = re.sub(r'name[:\-\s]*', '', line, flags=re.IGNORECASE).strip()
                break
        if not name and lines:
            name = lines[0].strip()
        
        return ParsedResume(
            name=name[:100] if name else "",
            email=emails[0] if emails else "",
            phone=phones[0] if phones else "",
            location="India",  # Default
            summary="Experienced professional with skills in " + ", ".join(found_skills[:5]),
            skills=found_skills,
            experience=[],
            education=[],
            certifications=[],
            projects=[],
            total_experience_years=3.0,  # Default estimate
            raw_text=text
        )
    
    def parse_resume(self, resume_path: str) -> ParsedResume:
        """Main method to parse a resume file"""
        logger.info(f"Parsing resume: {resume_path}")
        
        # Extract text
        text = self.extract_text_from_pdf(resume_path)
        
        if not text:
            raise ValueError("Could not extract text from resume")
        
        # Parse with AI
        parsed_resume = self.parse_resume_with_ai(text)
        
        logger.info(f"Successfully parsed resume for: {parsed_resume.name}")
        return parsed_resume


# Utility function
def create_resume_summary(parsed_resume: ParsedResume) -> str:
    """Create a concise summary of the resume for matching"""
    summary = f"""
Name: {parsed_resume.name}
Experience: {parsed_resume.total_experience_years} years
Location: {parsed_resume.location}

Skills: {', '.join(parsed_resume.skills[:15])}

Recent Experience:
"""
    for exp in parsed_resume.experience[:3]:
        summary += f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})\n"
    
    return summary.strip()