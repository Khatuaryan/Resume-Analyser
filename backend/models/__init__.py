"""
Models package for the Smart Resume Analyzer Platform.
Contains all Pydantic models for the application.
"""

from .user import (
    UserBase, UserCreate, UserLogin, UserResponse, UserInDB,
    HRProfile, CandidateProfile, Token, TokenData, UserRole
)
from .job import (
    JobBase, JobCreate, JobUpdate, JobResponse, JobSearch,
    JobApplication, JobApplicationResponse, JobType, ExperienceLevel, JobStatus
)
from .resume import (
    ResumeBase, ResumeCreate, ResumeResponse, ParsedResumeData,
    ResumeAnalysis, CandidateRanking, SkillRecommendation,
    Education, Experience, Project, ResumeStatus
)

__all__ = [
    # User models
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "UserInDB",
    "HRProfile", "CandidateProfile", "Token", "TokenData", "UserRole",
    
    # Job models
    "JobBase", "JobCreate", "JobUpdate", "JobResponse", "JobSearch",
    "JobApplication", "JobApplicationResponse", "JobType", "ExperienceLevel", "JobStatus",
    
    # Resume models
    "ResumeBase", "ResumeCreate", "ResumeResponse", "ParsedResumeData",
    "ResumeAnalysis", "CandidateRanking", "SkillRecommendation",
    "Education", "Experience", "Project", "ResumeStatus"
]
