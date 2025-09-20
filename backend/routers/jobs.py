"""
Job management router for HR users.
Handles job posting, updating, and candidate management.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from database.connection import get_collection
from models.job import (
    JobCreate, JobUpdate, JobResponse, JobSearch, JobApplication,
    JobApplicationResponse, JobStatus
)
from auth.jwt_handler import get_current_hr_user, get_current_user
from services.nlp_service import calculate_candidate_score

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_hr_user)
):
    """Create a new job posting (HR only)."""
    jobs_collection = get_collection("jobs")
    
    # Create job document
    job_id = str(uuid.uuid4())
    job_doc = {
        "_id": job_id,
        "hr_id": current_user.user_id,
        "title": job_data.title,
        "description": job_data.description,
        "company": job_data.company,
        "location": job_data.location,
        "job_type": job_data.job_type,
        "experience_level": job_data.experience_level,
        "salary_min": job_data.salary_min,
        "salary_max": job_data.salary_max,
        "required_skills": job_data.required_skills,
        "preferred_skills": job_data.preferred_skills,
        "benefits": job_data.benefits,
        "requirements": job_data.requirements,
        "responsibilities": job_data.responsibilities,
        "status": JobStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "application_count": 0,
        "view_count": 0
    }
    
    # Insert job into database
    result = await jobs_collection.insert_one(job_doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )
    
    return JobResponse(**job_doc)

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status_filter: Optional[JobStatus] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get list of jobs with pagination and filtering."""
    jobs_collection = get_collection("jobs")
    
    # Build filter query
    filter_query = {}
    if status_filter:
        filter_query["status"] = status_filter
    
    # Get jobs with pagination
    cursor = jobs_collection.find(filter_query).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    return [JobResponse(**job) for job in jobs]

@router.get("/search", response_model=List[JobResponse])
async def search_jobs(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Search jobs with various filters."""
    jobs_collection = get_collection("jobs")
    
    # Build search query
    search_query = {"status": JobStatus.ACTIVE}
    
    if query:
        search_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"company": {"$regex": query, "$options": "i"}}
        ]
    
    if location:
        search_query["location"] = {"$regex": location, "$options": "i"}
    
    if job_type:
        search_query["job_type"] = job_type
    
    if experience_level:
        search_query["experience_level"] = experience_level
    
    if skills:
        skill_list = [skill.strip() for skill in skills.split(",")]
        search_query["required_skills"] = {"$in": skill_list}
    
    # Get jobs with pagination
    cursor = jobs_collection.find(search_query).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    return [JobResponse(**job) for job in jobs]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific job by ID."""
    jobs_collection = get_collection("jobs")
    
    job = await jobs_collection.find_one({"_id": job_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Increment view count
    await jobs_collection.update_one(
        {"_id": job_id},
        {"$inc": {"view_count": 1}}
    )
    
    return JobResponse(**job)

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_update: JobUpdate,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update a job posting (HR only)."""
    jobs_collection = get_collection("jobs")
    
    # Check if job exists and belongs to current HR
    job = await jobs_collection.find_one({
        "_id": job_id,
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}
    
    # Add non-None fields to update
    for field, value in job_update.dict().items():
        if value is not None:
            update_data[field] = value
    
    # Update job
    result = await jobs_collection.update_one(
        {"_id": job_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update job"
        )
    
    # Return updated job
    updated_job = await jobs_collection.find_one({"_id": job_id})
    return JobResponse(**updated_job)

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Delete a job posting (HR only)."""
    jobs_collection = get_collection("jobs")
    
    # Check if job exists and belongs to current HR
    job = await jobs_collection.find_one({
        "_id": job_id,
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Delete job
    result = await jobs_collection.delete_one({"_id": job_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete job"
        )
    
    return {"message": "Job deleted successfully"}

@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
async def get_job_applications(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get applications for a specific job (HR only)."""
    applications_collection = get_collection("applications")
    users_collection = get_collection("users")
    resumes_collection = get_collection("resumes")
    
    # Check if job belongs to current HR
    jobs_collection = get_collection("jobs")
    job = await jobs_collection.find_one({
        "_id": job_id,
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Get applications for this job
    applications = await applications_collection.find({"job_id": job_id}).to_list(length=None)
    
    # Enrich applications with candidate data
    enriched_applications = []
    for app in applications:
        # Get candidate info
        candidate = await users_collection.find_one({"_id": app["candidate_id"]})
        
        # Get resume info
        resume = await resumes_collection.find_one({"candidate_id": app["candidate_id"]})
        
        enriched_app = {
            "id": app["_id"],
            "job_id": app["job_id"],
            "candidate_id": app["candidate_id"],
            "candidate_name": candidate["full_name"] if candidate else "Unknown",
            "candidate_email": candidate["email"] if candidate else "Unknown",
            "cover_letter": app.get("cover_letter"),
            "application_date": app["application_date"],
            "status": app["status"],
            "resume_id": resume["_id"] if resume else None,
            "match_score": app.get("match_score")
        }
        
        enriched_applications.append(JobApplicationResponse(**enriched_app))
    
    return enriched_applications

@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    application_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Apply to a job (Candidate only)."""
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply to jobs"
        )
    
    applications_collection = get_collection("applications")
    jobs_collection = get_collection("jobs")
    
    # Check if job exists and is active
    job = await jobs_collection.find_one({
        "_id": job_id,
        "status": JobStatus.ACTIVE
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not active"
        )
    
    # Check if already applied
    existing_application = await applications_collection.find_one({
        "job_id": job_id,
        "candidate_id": current_user.user_id
    })
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied to this job"
        )
    
    # Create application
    application_id = str(uuid.uuid4())
    application_doc = {
        "_id": application_id,
        "job_id": job_id,
        "candidate_id": current_user.user_id,
        "cover_letter": application_data.get("cover_letter"),
        "application_date": datetime.utcnow(),
        "status": "pending"
    }
    
    # Insert application
    result = await applications_collection.insert_one(application_doc)
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application"
        )
    
    # Update job application count
    await jobs_collection.update_one(
        {"_id": job_id},
        {"$inc": {"application_count": 1}}
    )
    
    return {"message": "Application submitted successfully", "application_id": application_id}

@router.get("/hr/my-jobs", response_model=List[JobResponse])
async def get_hr_jobs(
    current_user: dict = Depends(get_current_hr_user)
):
    """Get jobs posted by current HR user."""
    jobs_collection = get_collection("jobs")
    
    jobs = await jobs_collection.find({"hr_id": current_user.user_id}).to_list(length=None)
    
    return [JobResponse(**job) for job in jobs]
