"""
Resume management router for handling resume uploads, parsing, and analysis.
Handles file uploads, NLP processing, and resume data management.
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
import uuid
import os
import aiofiles
from pathlib import Path

from database.connection import get_collection
from models.resume import (
    ResumeResponse, ResumeStatus, ParsedResumeData, ResumeAnalysis
)
from auth.jwt_handler import get_current_candidate_user, get_current_user
from services.nlp_service import parse_resume_file, calculate_candidate_score

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_candidate_user)
):
    """Upload and parse a resume file (Candidate only)."""
    resumes_collection = get_collection("resumes")
    
    # Validate file type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, DOCX, and TXT files are allowed."
        )
    
    # Validate file size (10MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{current_user.user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Create resume document
        resume_id = str(uuid.uuid4())
        resume_doc = {
            "_id": resume_id,
            "candidate_id": current_user.user_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_type": file_extension,
            "file_size": file_size,
            "status": ResumeStatus.UPLOADED,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "parsed_data": None,
            "analysis_score": None
        }
        
        # Insert resume into database
        result = await resumes_collection.insert_one(resume_doc)
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save resume"
            )
        
        # Start parsing process asynchronously
        await parse_resume_async(resume_id, str(file_path), file_extension)
        
        return ResumeResponse(**resume_doc)
        
    except Exception as e:
        # Clean up file if database operation failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )

async def parse_resume_async(resume_id: str, file_path: str, file_type: str):
    """Parse resume asynchronously."""
    resumes_collection = get_collection("resumes")
    
    try:
        # Update status to processing
        await resumes_collection.update_one(
            {"_id": resume_id},
            {"$set": {"status": ResumeStatus.PROCESSING}}
        )
        
        # Parse resume using NLP service
        parse_result = await parse_resume_file(file_path, file_type)
        
        if parse_result["success"]:
            # Update resume with parsed data
            await resumes_collection.update_one(
                {"_id": resume_id},
                {
                    "$set": {
                        "status": ResumeStatus.PROCESSED,
                        "parsed_data": parse_result["parsed_data"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Update status to failed
            await resumes_collection.update_one(
                {"_id": resume_id},
                {
                    "$set": {
                        "status": ResumeStatus.FAILED,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
    except Exception as e:
        # Update status to failed
        await resumes_collection.update_one(
            {"_id": resume_id},
            {
                "$set": {
                    "status": ResumeStatus.FAILED,
                    "updated_at": datetime.utcnow()
                }
            }
        )

@router.get("/", response_model=List[ResumeResponse])
async def get_candidate_resumes(
    current_user: dict = Depends(get_current_candidate_user)
):
    """Get all resumes for the current candidate."""
    resumes_collection = get_collection("resumes")
    
    resumes = await resumes_collection.find({"candidate_id": current_user.user_id}).to_list(length=None)
    
    return [ResumeResponse(**resume) for resume in resumes]

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resume by ID."""
    resumes_collection = get_collection("resumes")
    
    resume = await resumes_collection.find_one({"_id": resume_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check access permissions
    if current_user.role == "candidate" and resume["candidate_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ResumeResponse(**resume)

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_candidate_user)
):
    """Delete a resume (Candidate only)."""
    resumes_collection = get_collection("resumes")
    
    # Check if resume exists and belongs to current candidate
    resume = await resumes_collection.find_one({
        "_id": resume_id,
        "candidate_id": current_user.user_id
    })
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found or access denied"
        )
    
    # Delete file from filesystem
    if os.path.exists(resume["file_path"]):
        os.remove(resume["file_path"])
    
    # Delete resume from database
    result = await resumes_collection.delete_one({"_id": resume_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete resume"
        )
    
    return {"message": "Resume deleted successfully"}

@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
async def get_resume_analysis(
    resume_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get resume analysis results."""
    resumes_collection = get_collection("resumes")
    analysis_collection = get_collection("resume_analysis")
    
    # Check if resume exists
    resume = await resumes_collection.find_one({"_id": resume_id})
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check access permissions
    if current_user.role == "candidate" and resume["candidate_id"] != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get analysis from database
    analysis = await analysis_collection.find_one({"resume_id": resume_id})
    
    if not analysis:
        # Generate analysis if not exists
        analysis = await generate_resume_analysis(resume_id, resume)
    
    return ResumeAnalysis(**analysis)

async def generate_resume_analysis(resume_id: str, resume: dict) -> dict:
    """Generate resume analysis."""
    analysis_collection = get_collection("resume_analysis")
    
    try:
        parsed_data = resume.get("parsed_data", {})
        
        # Calculate basic scores
        skills = parsed_data.get("skills", [])
        experience = parsed_data.get("experience", [])
        education = parsed_data.get("education", [])
        
        # Calculate scores (simplified)
        skills_score = min(len(skills) * 10, 100)
        experience_score = min(len(experience) * 20, 100)
        education_score = min(len(education) * 25, 100)
        completeness_score = (skills_score + experience_score + education_score) / 3
        
        overall_score = (skills_score * 0.3 + experience_score * 0.4 + education_score * 0.2 + completeness_score * 0.1)
        
        # Generate analysis
        analysis_doc = {
            "_id": str(uuid.uuid4()),
            "resume_id": resume_id,
            "candidate_id": resume["candidate_id"],
            "overall_score": round(overall_score, 2),
            "skills_score": round(skills_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "completeness_score": round(completeness_score, 2),
            "strengths": _generate_strengths(parsed_data),
            "weaknesses": _generate_weaknesses(parsed_data),
            "suggestions": _generate_suggestions(parsed_data),
            "skill_gaps": _identify_skill_gaps(skills),
            "analysis_date": datetime.utcnow()
        }
        
        # Save analysis
        await analysis_collection.insert_one(analysis_doc)
        
        return analysis_doc
        
    except Exception as e:
        # Return default analysis on error
        return {
            "_id": str(uuid.uuid4()),
            "resume_id": resume_id,
            "candidate_id": resume["candidate_id"],
            "overall_score": 0.0,
            "skills_score": 0.0,
            "experience_score": 0.0,
            "education_score": 0.0,
            "completeness_score": 0.0,
            "strengths": [],
            "weaknesses": ["Unable to analyze resume"],
            "suggestions": ["Please try uploading a different format"],
            "skill_gaps": [],
            "analysis_date": datetime.utcnow()
        }

def _generate_strengths(parsed_data: dict) -> List[str]:
    """Generate strengths based on parsed data."""
    strengths = []
    
    if len(parsed_data.get("skills", [])) > 5:
        strengths.append("Strong technical skills")
    
    if len(parsed_data.get("experience", [])) > 2:
        strengths.append("Relevant work experience")
    
    if len(parsed_data.get("education", [])) > 0:
        strengths.append("Educational background")
    
    if len(parsed_data.get("projects", [])) > 0:
        strengths.append("Project experience")
    
    return strengths

def _generate_weaknesses(parsed_data: dict) -> List[str]:
    """Generate weaknesses based on parsed data."""
    weaknesses = []
    
    if len(parsed_data.get("skills", [])) < 3:
        weaknesses.append("Limited technical skills")
    
    if len(parsed_data.get("experience", [])) < 1:
        weaknesses.append("Limited work experience")
    
    if not parsed_data.get("contact_info", {}).get("email"):
        weaknesses.append("Missing contact information")
    
    return weaknesses

def _generate_suggestions(parsed_data: dict) -> List[str]:
    """Generate improvement suggestions."""
    suggestions = []
    
    if len(parsed_data.get("skills", [])) < 5:
        suggestions.append("Add more technical skills to your resume")
    
    if not parsed_data.get("contact_info", {}).get("linkedin"):
        suggestions.append("Include your LinkedIn profile")
    
    if len(parsed_data.get("projects", [])) < 2:
        suggestions.append("Add more project examples")
    
    return suggestions

def _identify_skill_gaps(skills: List[str]) -> List[str]:
    """Identify potential skill gaps."""
    common_skills = ["python", "javascript", "sql", "git", "communication"]
    skill_gaps = []
    
    skills_lower = [skill.lower() for skill in skills]
    for skill in common_skills:
        if skill not in skills_lower:
            skill_gaps.append(skill.title())
    
    return skill_gaps
