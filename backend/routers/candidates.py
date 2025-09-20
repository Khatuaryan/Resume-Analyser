"""
Candidate management router for HR users.
Handles candidate ranking, scoring, and management for job applications.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from database.connection import get_collection
from models.resume import CandidateRanking
from models.job import JobApplicationResponse
from auth.jwt_handler import get_current_hr_user, get_current_user
from services.nlp_service import calculate_candidate_score

router = APIRouter()

@router.get("/job/{job_id}/rankings", response_model=List[CandidateRanking])
async def get_candidate_rankings(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get ranked candidates for a specific job (HR only)."""
    jobs_collection = get_collection("jobs")
    applications_collection = get_collection("applications")
    rankings_collection = get_collection("candidate_rankings")
    resumes_collection = get_collection("resumes")
    users_collection = get_collection("users")
    
    # Check if job belongs to current HR
    job = await jobs_collection.find_one({
        "_id": job_id,
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Get all applications for this job
    applications = await applications_collection.find({"job_id": job_id}).to_list(length=None)
    
    if not applications:
        return []
    
    # Generate rankings for each candidate
    rankings = []
    for i, application in enumerate(applications):
        candidate_id = application["candidate_id"]
        
        # Get candidate's latest resume
        resume = await resumes_collection.find_one(
            {"candidate_id": candidate_id, "status": "processed"},
            sort=[("created_at", -1)]
        )
        
        if not resume:
            continue
        
        # Get or generate ranking
        existing_ranking = await rankings_collection.find_one({
            "candidate_id": candidate_id,
            "job_id": job_id
        })
        
        if existing_ranking:
            rankings.append(CandidateRanking(**existing_ranking))
        else:
            # Generate new ranking
            ranking = await generate_candidate_ranking(
                candidate_id, job_id, resume, job
            )
            rankings.append(ranking)
    
    # Sort rankings by match score
    rankings.sort(key=lambda x: x.match_score, reverse=True)
    
    # Update ranking positions
    for i, ranking in enumerate(rankings):
        ranking.ranking_position = i + 1
        await rankings_collection.update_one(
            {"_id": ranking.id},
            {"$set": {"ranking_position": i + 1}}
        )
    
    return rankings

async def generate_candidate_ranking(
    candidate_id: str,
    job_id: str,
    resume: dict,
    job: dict
) -> CandidateRanking:
    """Generate candidate ranking based on resume and job requirements."""
    rankings_collection = get_collection("candidate_rankings")
    
    try:
        # Get parsed resume data
        parsed_data = resume.get("parsed_data", {})
        
        # Prepare job requirements
        job_requirements = {
            "required_skills": job.get("required_skills", []),
            "preferred_skills": job.get("preferred_skills", []),
            "experience_level": job.get("experience_level"),
            "job_type": job.get("job_type")
        }
        
        # Calculate scores using NLP service
        scores = await calculate_candidate_score(parsed_data, job_requirements)
        
        # Create ranking document
        ranking_id = str(uuid.uuid4())
        ranking_doc = {
            "_id": ranking_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "match_score": scores["overall_score"],
            "skills_match": scores["skill_score"],
            "experience_match": scores["experience_score"],
            "education_match": scores["education_score"],
            "ranking_position": 0,  # Will be updated after sorting
            "ranking_date": datetime.utcnow(),
            "notes": f"Auto-generated ranking based on {len(scores.get('matched_skills', []))} matched skills"
        }
        
        # Save ranking
        await rankings_collection.insert_one(ranking_doc)
        
        return CandidateRanking(**ranking_doc)
        
    except Exception as e:
        # Return default ranking on error
        ranking_id = str(uuid.uuid4())
        return CandidateRanking(
            id=ranking_id,
            candidate_id=candidate_id,
            job_id=job_id,
            match_score=0.0,
            skills_match=0.0,
            experience_match=0.0,
            education_match=0.0,
            ranking_position=0,
            ranking_date=datetime.utcnow(),
            notes="Error generating ranking"
        )

@router.get("/job/{job_id}/applications", response_model=List[JobApplicationResponse])
async def get_job_applications_with_details(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get detailed applications for a job with candidate information."""
    jobs_collection = get_collection("jobs")
    applications_collection = get_collection("applications")
    users_collection = get_collection("users")
    resumes_collection = get_collection("resumes")
    rankings_collection = get_collection("candidate_rankings")
    
    # Check if job belongs to current HR
    job = await jobs_collection.find_one({
        "_id": job_id,
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    # Get applications
    applications = await applications_collection.find({"job_id": job_id}).to_list(length=None)
    
    # Enrich applications with candidate and ranking data
    enriched_applications = []
    for app in applications:
        # Get candidate info
        candidate = await users_collection.find_one({"_id": app["candidate_id"]})
        
        # Get resume info
        resume = await resumes_collection.find_one(
            {"candidate_id": app["candidate_id"]},
            sort=[("created_at", -1)]
        )
        
        # Get ranking info
        ranking = await rankings_collection.find_one({
            "candidate_id": app["candidate_id"],
            "job_id": job_id
        })
        
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
            "match_score": ranking["match_score"] if ranking else None
        }
        
        enriched_applications.append(JobApplicationResponse(**enriched_app))
    
    # Sort by match score if available
    enriched_applications.sort(
        key=lambda x: x.match_score or 0,
        reverse=True
    )
    
    return enriched_applications

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update application status (HR only)."""
    applications_collection = get_collection("applications")
    jobs_collection = get_collection("jobs")
    
    # Get application
    application = await applications_collection.find_one({"_id": application_id})
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if job belongs to current HR
    job = await jobs_collection.find_one({
        "_id": application["job_id"],
        "hr_id": current_user.user_id
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update application status
    new_status = status_data.get("status")
    valid_statuses = ["pending", "reviewed", "shortlisted", "rejected", "hired"]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    result = await applications_collection.update_one(
        {"_id": application_id},
        {"$set": {"status": new_status}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update application status"
        )
    
    return {"message": f"Application status updated to {new_status}"}

@router.get("/candidate/{candidate_id}/profile")
async def get_candidate_profile(
    candidate_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get detailed candidate profile (HR only)."""
    users_collection = get_collection("users")
    resumes_collection = get_collection("resumes")
    applications_collection = get_collection("applications")
    
    # Get candidate info
    candidate = await users_collection.find_one({"_id": candidate_id})
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get candidate's resumes
    resumes = await resumes_collection.find(
        {"candidate_id": candidate_id}
    ).to_list(length=None)
    
    # Get candidate's applications
    applications = await applications_collection.find(
        {"candidate_id": candidate_id}
    ).to_list(length=None)
    
    # Get latest resume analysis
    latest_resume = None
    if resumes:
        latest_resume = max(resumes, key=lambda x: x["created_at"])
    
    return {
        "candidate": {
            "id": candidate["_id"],
            "full_name": candidate["full_name"],
            "email": candidate["email"],
            "phone": candidate.get("phone"),
            "role": candidate["role"]
        },
        "resumes": resumes,
        "applications_count": len(applications),
        "latest_resume": latest_resume
    }

@router.get("/search", response_model=List[dict])
async def search_candidates(
    query: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_hr_user)
):
    """Search candidates based on criteria (HR only)."""
    users_collection = get_collection("users")
    resumes_collection = get_collection("resumes")
    
    # Build search query
    search_query = {"role": "candidate"}
    
    if query:
        search_query["$or"] = [
            {"full_name": {"$regex": query, "$options": "i"}},
            {"email": {"$regex": query, "$options": "i"}}
        ]
    
    # Get candidates
    candidates = await users_collection.find(search_query).skip(skip).limit(limit).to_list(length=limit)
    
    # Enrich with resume data
    enriched_candidates = []
    for candidate in candidates:
        # Get latest resume
        latest_resume = await resumes_collection.find_one(
            {"candidate_id": candidate["_id"]},
            sort=[("created_at", -1)]
        )
        
        enriched_candidate = {
            "id": candidate["_id"],
            "full_name": candidate["full_name"],
            "email": candidate["email"],
            "phone": candidate.get("phone"),
            "latest_resume": latest_resume,
            "has_resume": latest_resume is not None
        }
        
        enriched_candidates.append(enriched_candidate)
    
    return enriched_candidates
