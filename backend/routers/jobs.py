"""
Job management router for HR users.
Handles job posting, updating, and candidate management.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from database.firebase_adapter import get_collection
from models.job import (
    JobCreate, JobUpdate, JobResponse, JobSearch, JobApplication,
    JobApplicationResponse, JobStatus, JobAnalytics, JobStatusUpdate,
    JobCompletionNotification
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
    now = datetime.utcnow()
    completion_date = now + timedelta(days=job_data.auto_complete_days) if job_data.auto_complete_days else None
    
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
        "auto_complete_days": job_data.auto_complete_days,
        "completion_date": completion_date,
        "status": JobStatus.ACTIVE,
        "created_at": now,
        "updated_at": now,
        "application_count": 0,
        "view_count": 0,
        "unique_view_count": 0,
        "completed_at": None,
        "is_auto_completed": False
    }
    
    # Insert job into database
    result = await jobs_collection.insert_one(job_doc)
    if not result.get("inserted_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )
    
    # Map _id to id for Pydantic model
    job_doc['id'] = job_doc['_id']
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
    
    # Map _id to id for each job
    for job in jobs:
        job['id'] = job['_id']
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
    
    # Map _id to id for each job
    for job in jobs:
        job['id'] = job['_id']
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
    
    # Map _id to id for Pydantic model
    job['id'] = job['_id']
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
    # Map _id to id for Pydantic model
    updated_job['id'] = updated_job['_id']
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
    
    # Map _id to id for each job
    for job in jobs:
        job['id'] = job['_id']
    return [JobResponse(**job) for job in jobs]

@router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: str,
    status_update: JobStatusUpdate,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update job status (active/inactive/completed)."""
    jobs_collection = get_collection("jobs")
    
    # Check if job exists and belongs to HR
    job = await jobs_collection.find_one({"_id": job_id, "hr_id": current_user.user_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Prevent reactivating completed jobs
    if job.get("status") == JobStatus.COMPLETED and status_update.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reactivate completed jobs"
        )
    
    # Update job status
    update_data = {
        "status": status_update.status,
        "updated_at": datetime.utcnow()
    }
    
    # If completing job, set completion date
    if status_update.status == JobStatus.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    
    await jobs_collection.update_one(
        {"_id": job_id},
        {"$set": update_data}
    )
    
    # Get updated job
    updated_job = await jobs_collection.find_one({"_id": job_id})
    updated_job['id'] = updated_job['_id']
    return JobResponse(**updated_job)

@router.get("/{job_id}/analytics", response_model=JobAnalytics)
async def get_job_analytics(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get analytics for a specific job."""
    jobs_collection = get_collection("jobs")
    applications_collection = get_collection("applications")
    
    # Check if job exists and belongs to HR
    job = await jobs_collection.find_one({"_id": job_id, "hr_id": current_user.user_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get applications for this job
    applications = await applications_collection.find({"job_id": job_id}).to_list(length=None)
    
    # Calculate analytics
    total_applications = len(applications)
    unique_views = job.get("unique_view_count", 0)
    hr_views = job.get("view_count", 0) - unique_views
    application_rate = (total_applications / unique_views) if unique_views > 0 else 0.0
    
    # Analyze applications
    status_distribution = {}
    experience_distribution = {}
    location_distribution = {}
    all_skills = []
    
    for app in applications:
        # Status distribution
        status = app.get("status", "pending")
        status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Get candidate info for additional analytics
        candidate = await get_collection("users").find_one({"_id": app["candidate_id"]})
        if candidate:
            # Experience distribution
            exp_level = candidate.get("experience_level", "unknown")
            experience_distribution[exp_level] = experience_distribution.get(exp_level, 0) + 1
            
            # Location distribution
            location = candidate.get("location", "unknown")
            location_distribution[location] = location_distribution.get(location, 0) + 1
    
    # Get top skills from applications
    # This would need to be enhanced based on your resume analysis data
    
    analytics = JobAnalytics(
        job_id=job_id,
        total_applications=total_applications,
        unique_views=unique_views,
        hr_views=hr_views,
        application_rate=application_rate,
        top_skills=all_skills[:10],  # Top 10 skills
        experience_distribution=experience_distribution,
        location_distribution=location_distribution,
        status_distribution=status_distribution,
        created_at=job["created_at"],
        updated_at=job["updated_at"]
    )
    
    return analytics

@router.get("/{job_id}/candidates", response_model=List[JobApplicationResponse])
async def get_job_candidates(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get all candidates who applied to a specific job."""
    jobs_collection = get_collection("jobs")
    applications_collection = get_collection("applications")
    users_collection = get_collection("users")
    
    # Check if job exists and belongs to HR
    job = await jobs_collection.find_one({"_id": job_id, "hr_id": current_user.user_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get applications with candidate details
    applications = await applications_collection.find({"job_id": job_id}).to_list(length=None)
    
    candidate_applications = []
    for app in applications:
        candidate = await users_collection.find_one({"_id": app["candidate_id"]})
        if candidate:
            candidate_applications.append(JobApplicationResponse(
                id=app["_id"],
                job_id=app["job_id"],
                candidate_id=app["candidate_id"],
                candidate_name=candidate.get("full_name", "Unknown"),
                candidate_email=candidate.get("email", "Unknown"),
                cover_letter=app.get("cover_letter"),
                application_date=app.get("application_date", datetime.utcnow()),
                status=app.get("status", "pending"),
                resume_id=app.get("resume_id"),
                match_score=app.get("match_score")
            ))
    
    return candidate_applications

@router.patch("/{job_id}/candidates/{candidate_id}/status")
async def update_candidate_status(
    job_id: str,
    candidate_id: str,
    status: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update candidate application status."""
    applications_collection = get_collection("applications")
    jobs_collection = get_collection("jobs")
    
    # Check if job exists and belongs to HR
    job = await jobs_collection.find_one({"_id": job_id, "hr_id": current_user.user_id})
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update application status
    result = await applications_collection.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return {"message": f"Candidate status updated to {status}"}

@router.get("/hr/auto-complete-check")
async def check_auto_complete_jobs(
    current_user: dict = Depends(get_current_hr_user)
):
    """Check and auto-complete jobs that have reached their completion date."""
    jobs_collection = get_collection("jobs")
    now = datetime.utcnow()
    
    # Find jobs that should be auto-completed
    jobs_to_complete = await jobs_collection.find({
        "hr_id": current_user.user_id,
        "status": JobStatus.ACTIVE,
        "completion_date": {"$lte": now}
    }).to_list(length=None)
    
    completed_jobs = []
    for job in jobs_to_complete:
        # Update job status to completed
        await jobs_collection.update_one(
            {"_id": job["_id"]},
            {
                "$set": {
                    "status": JobStatus.COMPLETED,
                    "completed_at": now,
                    "is_auto_completed": True,
                    "updated_at": now
                }
            }
        )
        
        completed_jobs.append({
            "job_id": job["_id"],
            "title": job["title"],
            "completion_date": job["completion_date"]
        })
    
    return {
        "message": f"Auto-completed {len(completed_jobs)} jobs",
        "completed_jobs": completed_jobs
    }
