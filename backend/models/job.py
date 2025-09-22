"""
Job models for the Smart Resume Analyzer Platform.
Defines Pydantic models for job postings and related entities.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobType(str, Enum):
    """Job type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"

class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class JobStatus(str, Enum):
    """Job status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    DRAFT = "draft"

class JobBase(BaseModel):
    """Base job model with common fields."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    company: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=100)
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    # New fields for job lifecycle management
    auto_complete_days: int = Field(default=15, ge=1, le=365)  # Days until auto-completion
    completion_date: Optional[datetime] = None  # When job will be auto-completed

class JobCreate(JobBase):
    """Job creation model."""
    pass

class JobUpdate(BaseModel):
    """Job update model with optional fields."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    status: Optional[JobStatus] = None
    auto_complete_days: Optional[int] = Field(None, ge=1, le=365)

class JobResponse(JobBase):
    """Job response model."""
    id: str
    hr_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    application_count: int = 0
    view_count: int = 0
    # Analytics fields
    unique_view_count: int = 0  # Views excluding HR views
    completion_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None  # When job was actually completed
    is_auto_completed: bool = False

    class Config:
        from_attributes = True

class JobSearch(BaseModel):
    """Job search model."""
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    skills: Optional[List[str]] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=50)

class JobApplication(BaseModel):
    """Job application model."""
    job_id: str
    candidate_id: str
    cover_letter: Optional[str] = Field(None, max_length=2000)
    application_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, reviewed, shortlisted, rejected, hired

class JobApplicationResponse(JobApplication):
    """Job application response model."""
    id: str
    candidate_name: str
    candidate_email: str
    resume_id: Optional[str] = None
    match_score: Optional[float] = None

    class Config:
        from_attributes = True

class JobAnalytics(BaseModel):
    """Job analytics model."""
    job_id: str
    total_applications: int = 0
    unique_views: int = 0
    hr_views: int = 0
    application_rate: float = 0.0  # Applications per view
    top_skills: List[str] = Field(default_factory=list)
    experience_distribution: dict = Field(default_factory=dict)
    location_distribution: dict = Field(default_factory=dict)
    status_distribution: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class JobStatusUpdate(BaseModel):
    """Job status update model."""
    status: JobStatus
    reason: Optional[str] = None

class JobCompletionNotification(BaseModel):
    """Job completion notification model."""
    job_id: str
    job_title: str
    total_applications: int
    completion_date: datetime
    hr_email: str
