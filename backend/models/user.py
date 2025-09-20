"""
User models for the Smart Resume Analyzer Platform.
Defines Pydantic models for HR and Candidate users.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration."""
    HR = "hr"
    CANDIDATE = "candidate"

class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)  # For HR users
    role: UserRole

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """User response model (without password)."""
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

class UserInDB(UserBase):
    """User model for database storage."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class HRProfile(BaseModel):
    """HR user profile with additional fields."""
    company: str = Field(..., min_length=2, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)

class CandidateProfile(BaseModel):
    """Candidate user profile with additional fields."""
    current_position: Optional[str] = Field(None, max_length=100)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    location: Optional[str] = Field(None, max_length=100)
    linkedin_url: Optional[str] = Field(None, max_length=200)
    github_url: Optional[str] = Field(None, max_length=200)
    skills: List[str] = []
    preferred_job_types: List[str] = []
    salary_expectation: Optional[int] = Field(None, ge=0)

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    """Token data model for JWT payload."""
    user_id: str
    email: str
    role: UserRole
