"""
Resume models for the Smart Resume Analyzer Platform.
Defines Pydantic models for resume data and analysis results.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ResumeStatus(str, Enum):
    """Resume processing status enumeration."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class Education(BaseModel):
    """Education model."""
    degree: str = Field(..., max_length=100)
    institution: str = Field(..., max_length=200)
    field_of_study: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    location: Optional[str] = Field(None, max_length=100)
    is_current: bool = False

class Experience(BaseModel):
    """Work experience model."""
    title: str = Field(..., max_length=100)
    company: str = Field(..., max_length=200)
    location: Optional[str] = Field(None, max_length=100)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = Field(None, max_length=2000)
    achievements: List[str] = Field(default_factory=list)

class Project(BaseModel):
    """Project model."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    technologies: List[str] = Field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    url: Optional[str] = Field(None, max_length=200)
    github_url: Optional[str] = Field(None, max_length=200)

class ResumeBase(BaseModel):
    """Base resume model."""
    candidate_id: str
    filename: str
    file_path: str
    file_type: str  # pdf, docx, txt
    file_size: int

class ResumeCreate(ResumeBase):
    """Resume creation model."""
    pass

class ResumeResponse(ResumeBase):
    """Resume response model."""
    id: str
    status: ResumeStatus
    created_at: datetime
    updated_at: datetime
    parsed_data: Optional[Dict[str, Any]] = None
    analysis_score: Optional[float] = None

    class Config:
        from_attributes = True

class ParsedResumeData(BaseModel):
    """Parsed resume data model."""
    personal_info: Dict[str, Any] = Field(default_factory=dict)
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text: str = ""

class ResumeAnalysis(BaseModel):
    """Resume analysis results model."""
    resume_id: str
    candidate_id: str
    overall_score: float = Field(ge=0.0, le=100.0)
    skills_score: float = Field(ge=0.0, le=100.0)
    experience_score: float = Field(ge=0.0, le=100.0)
    education_score: float = Field(ge=0.0, le=100.0)
    completeness_score: float = Field(ge=0.0, le=100.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

class CandidateRanking(BaseModel):
    """Candidate ranking model."""
    candidate_id: str
    job_id: str
    match_score: float = Field(ge=0.0, le=100.0)
    skills_match: float = Field(ge=0.0, le=100.0)
    experience_match: float = Field(ge=0.0, le=100.0)
    education_match: float = Field(ge=0.0, le=100.0)
    ranking_position: int
    ranking_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class SkillRecommendation(BaseModel):
    """Skill recommendation model."""
    candidate_id: str
    recommended_skills: List[str] = Field(default_factory=list)
    skill_importance: Dict[str, float] = Field(default_factory=dict)
    learning_resources: Dict[str, List[str]] = Field(default_factory=dict)
    recommendation_date: datetime = Field(default_factory=datetime.utcnow)
    reasoning: List[str] = Field(default_factory=list)
