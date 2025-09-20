"""
Skills and recommendations router.
Handles skill suggestions, gap analysis, and learning recommendations.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from database.connection import get_collection
from models.resume import SkillRecommendation
from auth.jwt_handler import get_current_candidate_user, get_current_user
from services.nlp_service import nlp_service

router = APIRouter()

@router.get("/recommendations", response_model=SkillRecommendation)
async def get_skill_recommendations(
    current_user: dict = Depends(get_current_candidate_user)
):
    """Get skill recommendations for the current candidate."""
    recommendations_collection = get_collection("skill_recommendations")
    resumes_collection = get_collection("resumes")
    jobs_collection = get_collection("jobs")
    
    # Get candidate's latest resume
    latest_resume = await resumes_collection.find_one(
        {"candidate_id": current_user.user_id, "status": "processed"},
        sort=[("created_at", -1)]
    )
    
    if not latest_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed resume found. Please upload and process a resume first."
        )
    
    # Check if recommendations already exist
    existing_recommendations = await recommendations_collection.find_one({
        "candidate_id": current_user.user_id
    })
    
    if existing_recommendations:
        return SkillRecommendation(**existing_recommendations)
    
    # Generate new recommendations
    recommendations = await generate_skill_recommendations(
        current_user.user_id, latest_resume
    )
    
    return recommendations

async def generate_skill_recommendations(
    candidate_id: str,
    resume: dict
) -> SkillRecommendation:
    """Generate skill recommendations based on resume and market trends."""
    recommendations_collection = get_collection("skill_recommendations")
    
    try:
        parsed_data = resume.get("parsed_data", {})
        current_skills = parsed_data.get("skills", [])
        
        # Get market trends from job postings
        jobs_collection = get_collection("jobs")
        all_jobs = await jobs_collection.find({"status": "active"}).to_list(length=None)
        
        # Extract skills from job postings
        job_skills = []
        for job in all_jobs:
            job_skills.extend(job.get("required_skills", []))
            job_skills.extend(job.get("preferred_skills", []))
        
        # Find most in-demand skills
        skill_frequency = {}
        for skill in job_skills:
            skill_lower = skill.lower()
            skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Sort skills by frequency
        sorted_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # Get top skills not in candidate's current skills
        current_skills_lower = [skill.lower() for skill in current_skills]
        recommended_skills = []
        skill_importance = {}
        
        for skill, frequency in sorted_skills[:20]:  # Top 20 skills
            if skill not in current_skills_lower:
                recommended_skills.append(skill.title())
                skill_importance[skill.title()] = frequency
        
        # Generate learning resources
        learning_resources = generate_learning_resources(recommended_skills[:10])
        
        # Generate reasoning
        reasoning = generate_recommendation_reasoning(current_skills, recommended_skills[:10])
        
        # Create recommendation document
        recommendation_id = str(uuid.uuid4())
        recommendation_doc = {
            "_id": recommendation_id,
            "candidate_id": candidate_id,
            "recommended_skills": recommended_skills[:10],
            "skill_importance": skill_importance,
            "learning_resources": learning_resources,
            "recommendation_date": datetime.utcnow(),
            "reasoning": reasoning
        }
        
        # Save recommendations
        await recommendations_collection.insert_one(recommendation_doc)
        
        return SkillRecommendation(**recommendation_doc)
        
    except Exception as e:
        # Return default recommendations on error
        return SkillRecommendation(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            recommended_skills=["Python", "JavaScript", "SQL", "Git", "Communication"],
            skill_importance={"Python": 50, "JavaScript": 45, "SQL": 40, "Git": 35, "Communication": 30},
            learning_resources={},
            recommendation_date=datetime.utcnow(),
            reasoning=["Based on market trends and your current skills"]
        )

def generate_learning_resources(skills: List[str]) -> Dict[str, List[str]]:
    """Generate learning resources for recommended skills."""
    resources = {}
    
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in ["python", "javascript", "java", "c++"]:
            resources[skill] = [
                f"Learn {skill} on Codecademy",
                f"Practice {skill} on LeetCode",
                f"Build projects with {skill}",
                f"Read {skill} documentation"
            ]
        elif skill_lower in ["sql", "database"]:
            resources[skill] = [
                "SQL Tutorial on W3Schools",
                "Practice SQL on HackerRank",
                "Learn database design principles",
                "Work with real databases"
            ]
        elif skill_lower in ["git", "github"]:
            resources[skill] = [
                "Git Tutorial on Atlassian",
                "Practice Git commands",
                "Contribute to open source projects",
                "Learn GitHub workflows"
            ]
        else:
            resources[skill] = [
                f"Research {skill} best practices",
                f"Find {skill} tutorials online",
                f"Practice {skill} in real projects",
                f"Join {skill} communities"
            ]
    
    return resources

def generate_recommendation_reasoning(current_skills: List[str], recommended_skills: List[str]) -> List[str]:
    """Generate reasoning for skill recommendations."""
    reasoning = []
    
    if len(current_skills) < 5:
        reasoning.append("You have limited technical skills. Adding more skills will improve your marketability.")
    
    if "python" not in [skill.lower() for skill in current_skills]:
        reasoning.append("Python is one of the most in-demand programming languages.")
    
    if "javascript" not in [skill.lower() for skill in current_skills]:
        reasoning.append("JavaScript is essential for web development roles.")
    
    if "sql" not in [skill.lower() for skill in current_skills]:
        reasoning.append("SQL is required for most data-related positions.")
    
    if "git" not in [skill.lower() for skill in current_skills]:
        reasoning.append("Git is essential for version control and collaboration.")
    
    reasoning.append("These skills are frequently mentioned in job postings.")
    reasoning.append("Adding these skills will increase your match score for more positions.")
    
    return reasoning

@router.get("/market-trends")
async def get_market_trends(
    current_user: dict = Depends(get_current_user)
):
    """Get current market trends for skills (available to all users)."""
    jobs_collection = get_collection("jobs")
    
    # Get all active jobs
    jobs = await jobs_collection.find({"status": "active"}).to_list(length=None)
    
    # Analyze skill trends
    skill_frequency = {}
    location_trends = {}
    job_type_trends = {}
    
    for job in jobs:
        # Count skills
        for skill in job.get("required_skills", []):
            skill_lower = skill.lower()
            skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Count locations
        location = job.get("location", "Unknown")
        location_trends[location] = location_trends.get(location, 0) + 1
        
        # Count job types
        job_type = job.get("job_type", "Unknown")
        job_type_trends[job_type] = job_type_trends.get(job_type, 0) + 1
    
    # Sort trends
    top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
    top_locations = sorted(location_trends.items(), key=lambda x: x[1], reverse=True)[:10]
    top_job_types = sorted(job_type_trends.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "top_skills": [{"skill": skill, "count": count} for skill, count in top_skills],
        "top_locations": [{"location": location, "count": count} for location, count in top_locations],
        "top_job_types": [{"job_type": job_type, "count": count} for job_type, count in top_job_types],
        "total_jobs": len(jobs),
        "analysis_date": datetime.utcnow()
    }

@router.get("/skill-gap-analysis")
async def get_skill_gap_analysis(
    job_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_candidate_user)
):
    """Analyze skill gaps for a specific job or general market."""
    resumes_collection = get_collection("resumes")
    jobs_collection = get_collection("jobs")
    
    # Get candidate's latest resume
    latest_resume = await resumes_collection.find_one(
        {"candidate_id": current_user.user_id, "status": "processed"},
        sort=[("created_at", -1)]
    )
    
    if not latest_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed resume found"
        )
    
    current_skills = latest_resume.get("parsed_data", {}).get("skills", [])
    
    if job_id:
        # Analyze against specific job
        job = await jobs_collection.find_one({"_id": job_id})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        required_skills = job.get("required_skills", [])
        preferred_skills = job.get("preferred_skills", [])
        
        # Find missing skills
        current_skills_lower = [skill.lower() for skill in current_skills]
        missing_required = [skill for skill in required_skills if skill.lower() not in current_skills_lower]
        missing_preferred = [skill for skill in preferred_skills if skill.lower() not in current_skills_lower]
        
        return {
            "job_id": job_id,
            "job_title": job.get("title"),
            "current_skills": current_skills,
            "missing_required_skills": missing_required,
            "missing_preferred_skills": missing_preferred,
            "match_percentage": calculate_skill_match_percentage(current_skills, required_skills)
        }
    else:
        # General market analysis
        all_jobs = await jobs_collection.find({"status": "active"}).to_list(length=None)
        
        # Get all skills from jobs
        all_skills = []
        for job in all_jobs:
            all_skills.extend(job.get("required_skills", []))
            all_skills.extend(job.get("preferred_skills", []))
        
        # Find most common missing skills
        skill_frequency = {}
        for skill in all_skills:
            skill_lower = skill.lower()
            skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Get skills not in candidate's current skills
        current_skills_lower = [skill.lower() for skill in current_skills]
        missing_skills = []
        for skill, frequency in skill_frequency.items():
            if skill not in current_skills_lower:
                missing_skills.append({"skill": skill.title(), "frequency": frequency})
        
        # Sort by frequency
        missing_skills.sort(key=lambda x: x["frequency"], reverse=True)
        
        return {
            "current_skills": current_skills,
            "missing_skills": missing_skills[:20],  # Top 20 missing skills
            "total_jobs_analyzed": len(all_jobs),
            "analysis_date": datetime.utcnow()
        }

def calculate_skill_match_percentage(current_skills: List[str], required_skills: List[str]) -> float:
    """Calculate percentage of required skills that candidate has."""
    if not required_skills:
        return 100.0
    
    current_skills_lower = [skill.lower() for skill in current_skills]
    required_skills_lower = [skill.lower() for skill in required_skills]
    
    matches = sum(1 for skill in required_skills_lower if skill in current_skills_lower)
    return (matches / len(required_skills_lower)) * 100

@router.get("/learning-paths")
async def get_learning_paths(
    skill: str = Query(..., description="Skill to get learning path for"),
    current_user: dict = Depends(get_current_user)
):
    """Get learning path for a specific skill."""
    learning_paths = {
        "python": {
            "beginner": [
                "Learn Python basics on Codecademy",
                "Practice with Python exercises on HackerRank",
                "Build a simple calculator project",
                "Learn about variables, loops, and functions"
            ],
            "intermediate": [
                "Learn object-oriented programming",
                "Practice with data structures",
                "Build a web scraper",
                "Learn about libraries like pandas and numpy"
            ],
            "advanced": [
                "Learn about decorators and generators",
                "Build a web application with Flask/Django",
                "Practice with algorithms and data structures",
                "Contribute to open source Python projects"
            ]
        },
        "javascript": {
            "beginner": [
                "Learn JavaScript basics on MDN",
                "Practice with JavaScript exercises",
                "Build a simple interactive webpage",
                "Learn about DOM manipulation"
            ],
            "intermediate": [
                "Learn ES6+ features",
                "Practice with frameworks like React or Vue",
                "Build a single-page application",
                "Learn about async programming"
            ],
            "advanced": [
                "Learn about design patterns",
                "Build a full-stack application",
                "Practice with testing frameworks",
                "Learn about performance optimization"
            ]
        }
    }
    
    skill_lower = skill.lower()
    if skill_lower in learning_paths:
        return {
            "skill": skill,
            "learning_path": learning_paths[skill_lower],
            "recommended_duration": "3-6 months per level"
        }
    else:
        return {
            "skill": skill,
            "learning_path": {
                "beginner": [
                    f"Research {skill} fundamentals",
                    f"Find {skill} tutorials online",
                    f"Practice {skill} basics",
                    f"Join {skill} communities"
                ],
                "intermediate": [
                    f"Build projects with {skill}",
                    f"Learn {skill} best practices",
                    f"Practice advanced {skill} concepts",
                    f"Contribute to {skill} projects"
                ],
                "advanced": [
                    f"Master {skill} advanced topics",
                    f"Teach others {skill}",
                    f"Lead {skill} projects",
                    f"Stay updated with {skill} trends"
                ]
            },
            "recommended_duration": "3-6 months per level"
        }
