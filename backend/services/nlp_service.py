"""
NLP service for resume parsing, analysis, and skill extraction.
Handles PDF/DOCX parsing, NER, and candidate scoring using spaCy and transformers.
"""

import spacy
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
from pathlib import Path
import PyPDF2
from docx import Document
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPService:
    """NLP service for resume analysis and processing."""
    
    def __init__(self):
        self.nlp = None
        self.sentence_model = None
        self.skill_keywords = self._load_skill_keywords()
        self.initialized = False
    
    async def initialize(self):
        """Initialize NLP models asynchronously."""
        if self.initialized:
            return
        
        try:
            # Load spaCy model
            logger.info("Loading spaCy model...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Using basic English model.")
                self.nlp = spacy.blank("en")
            
            # Load sentence transformer model
            logger.info("Loading sentence transformer model...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.initialized = True
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            raise e
    
    def _load_skill_keywords(self) -> Dict[str, List[str]]:
        """Load predefined skill keywords for different categories."""
        return {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust",
                "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css", "sass", "scss"
            ],
            "frameworks": [
                "react", "angular", "vue", "django", "flask", "spring", "express", "laravel", "rails",
                "asp.net", "node.js", "fastapi", "tensorflow", "pytorch", "scikit-learn", "pandas",
                "numpy", "bootstrap", "tailwind", "jquery"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
                "sqlite", "oracle", "sql server", "mariadb", "neo4j", "firebase"
            ],
            "cloud_platforms": [
                "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform", "jenkins",
                "gitlab ci", "github actions", "heroku", "vercel", "netlify"
            ],
            "tools": [
                "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack", "trello",
                "figma", "sketch", "adobe", "photoshop", "illustrator", "vscode", "intellij"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving", "critical thinking",
                "time management", "project management", "agile", "scrum", "mentoring", "collaboration"
            ]
        }
    
    async def parse_resume(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Parse resume file and extract structured data."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Extract text based on file type
            if file_type.lower() == "pdf":
                text = self._extract_text_from_pdf(file_path)
            elif file_type.lower() in ["docx", "doc"]:
                text = self._extract_text_from_docx(file_path)
            else:
                # Assume plain text
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Parse the text using NLP
            parsed_data = await self._parse_text_with_nlp(text)
            
            return {
                "success": True,
                "parsed_data": parsed_data,
                "raw_text": text
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {
                "success": False,
                "error": str(e),
                "parsed_data": None
            }
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    async def _parse_text_with_nlp(self, text: str) -> Dict[str, Any]:
        """Parse text using spaCy NLP pipeline."""
        doc = self.nlp(text)
        
        # Extract personal information
        personal_info = self._extract_personal_info(doc)
        
        # Extract contact information
        contact_info = self._extract_contact_info(doc, text)
        
        # Extract education
        education = self._extract_education(doc)
        
        # Extract experience
        experience = self._extract_experience(doc)
        
        # Extract skills
        skills = self._extract_skills(doc, text)
        
        # Extract projects
        projects = self._extract_projects(doc)
        
        # Extract certifications
        certifications = self._extract_certifications(doc)
        
        # Extract languages
        languages = self._extract_languages(doc)
        
        # Generate summary
        summary = self._generate_summary(doc)
        
        return {
            "personal_info": personal_info,
            "contact_info": contact_info,
            "education": education,
            "experience": experience,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
            "summary": summary
        }
    
    def _extract_personal_info(self, doc) -> Dict[str, Any]:
        """Extract personal information using NER."""
        personal_info = {}
        
        # Extract names (PERSON entities)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if names:
            personal_info["name"] = names[0]
        
        # Extract locations
        locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        if locations:
            personal_info["location"] = locations[0]
        
        return personal_info
    
    def _extract_contact_info(self, doc, text: str) -> Dict[str, Any]:
        """Extract contact information using regex patterns."""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]
        
        # Phone pattern
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = ''.join(phones[0])
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info["linkedin"] = linkedin.group()
        
        return contact_info
    
    def _extract_education(self, doc) -> List[Dict[str, Any]]:
        """Extract education information."""
        education = []
        
        # Look for education-related patterns
        education_keywords = ["university", "college", "degree", "bachelor", "master", "phd", "diploma", "certificate"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in education_keywords):
                # Extract degree and institution
                degree_match = re.search(r'(bachelor|master|phd|diploma|certificate|degree)', sent.text.lower())
                if degree_match:
                    education.append({
                        "degree": degree_match.group().title(),
                        "institution": sent.text.strip(),
                        "description": sent.text.strip()
                    })
        
        return education
    
    def _extract_experience(self, doc) -> List[Dict[str, Any]]:
        """Extract work experience information."""
        experience = []
        
        # Look for experience-related patterns
        exp_keywords = ["experience", "worked", "job", "position", "role", "company"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in exp_keywords):
                # Extract company and position
                company_match = re.search(r'at\s+([A-Z][a-zA-Z\s&]+)', sent.text)
                position_match = re.search(r'(developer|engineer|manager|analyst|consultant|specialist)', sent.text.lower())
                
                if company_match or position_match:
                    experience.append({
                        "company": company_match.group(1) if company_match else "Unknown",
                        "position": position_match.group(1).title() if position_match else "Unknown",
                        "description": sent.text.strip()
                    })
        
        return experience
    
    def _extract_skills(self, doc, text: str) -> List[str]:
        """Extract skills from resume text."""
        skills = []
        text_lower = text.lower()
        
        # Check for predefined skills
        for category, skill_list in self.skill_keywords.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_projects(self, doc) -> List[Dict[str, Any]]:
        """Extract project information."""
        projects = []
        
        # Look for project-related patterns
        project_keywords = ["project", "developed", "built", "created", "implemented"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in project_keywords):
                projects.append({
                    "name": "Project",
                    "description": sent.text.strip()
                })
        
        return projects
    
    def _extract_certifications(self, doc) -> List[str]:
        """Extract certifications."""
        certifications = []
        
        # Look for certification patterns
        cert_keywords = ["certified", "certification", "certificate", "license"]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in cert_keywords):
                certifications.append(sent.text.strip())
        
        return certifications
    
    def _extract_languages(self, doc) -> List[str]:
        """Extract languages."""
        languages = []
        
        # Common languages
        language_list = ["english", "spanish", "french", "german", "chinese", "japanese", "korean", "arabic"]
        
        for sent in doc.sents:
            for lang in language_list:
                if lang in sent.text.lower():
                    languages.append(lang.title())
        
        return list(set(languages))
    
    def _generate_summary(self, doc) -> str:
        """Generate a summary of the resume."""
        # Extract key sentences (simple approach)
        sentences = [sent.text for sent in doc.sents if len(sent.text) > 20]
        
        # Return first few sentences as summary
        summary_sentences = sentences[:3]
        return " ".join(summary_sentences)
    
    async def calculate_candidate_score(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate candidate score based on job requirements."""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Extract skills from resume
            resume_skills = resume_data.get("skills", [])
            job_skills = job_requirements.get("required_skills", [])
            
            # Calculate skill match score
            skill_score = self._calculate_skill_match(resume_skills, job_skills)
            
            # Calculate experience score
            experience_score = self._calculate_experience_score(resume_data, job_requirements)
            
            # Calculate education score
            education_score = self._calculate_education_score(resume_data, job_requirements)
            
            # Calculate overall score
            overall_score = (skill_score * 0.4 + experience_score * 0.4 + education_score * 0.2)
            
            return {
                "overall_score": round(overall_score, 2),
                "skill_score": round(skill_score, 2),
                "experience_score": round(experience_score, 2),
                "education_score": round(education_score, 2),
                "matched_skills": self._get_matched_skills(resume_skills, job_skills),
                "missing_skills": self._get_missing_skills(resume_skills, job_skills)
            }
            
        except Exception as e:
            logger.error(f"Error calculating candidate score: {e}")
            return {
                "overall_score": 0,
                "skill_score": 0,
                "experience_score": 0,
                "education_score": 0,
                "matched_skills": [],
                "missing_skills": []
            }
    
    def _calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill matching score."""
        if not job_skills:
            return 0.0
        
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matches = sum(1 for skill in job_skills_lower if skill in resume_skills_lower)
        return (matches / len(job_skills_lower)) * 100
    
    def _calculate_experience_score(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """Calculate experience score."""
        # Simple implementation - can be enhanced
        experience = resume_data.get("experience", [])
        return min(len(experience) * 20, 100)  # Max 100 for 5+ experiences
    
    def _calculate_education_score(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """Calculate education score."""
        education = resume_data.get("education", [])
        if not education:
            return 0.0
        
        # Simple scoring based on degree level
        degree_scores = {"phd": 100, "master": 80, "bachelor": 60, "diploma": 40, "certificate": 20}
        
        max_score = 0
        for edu in education:
            degree = edu.get("degree", "").lower()
            for degree_type, score in degree_scores.items():
                if degree_type in degree:
                    max_score = max(max_score, score)
        
        return max_score
    
    def _get_matched_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get skills that match between resume and job."""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched = []
        for i, job_skill in enumerate(job_skills_lower):
            if job_skill in resume_skills_lower:
                matched.append(job_skills[i])  # Return original case
        
        return matched
    
    def _get_missing_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """Get skills that are missing from resume."""
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        missing = []
        for i, job_skill in enumerate(job_skills_lower):
            if job_skill not in resume_skills_lower:
                missing.append(job_skills[i])  # Return original case
        
        return missing

# Global NLP service instance
nlp_service = NLPService()

async def initialize_nlp_models():
    """Initialize NLP models."""
    await nlp_service.initialize()

async def parse_resume_file(file_path: str, file_type: str) -> Dict[str, Any]:
    """Parse a resume file."""
    return await nlp_service.parse_resume(file_path, file_type)

async def calculate_candidate_score(resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate candidate score."""
    return await nlp_service.calculate_candidate_score(resume_data, job_requirements)
