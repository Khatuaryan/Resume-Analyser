"""
Advanced Features Router
Provides endpoints for ML models, LLM integration, OCR, multilingual support,
ontology, and bias detection features.
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from database.connection import get_collection
from auth.jwt_handler import get_current_user, get_current_hr_user
from services.enhanced_nlp_service import (
    parse_resume_enhanced, calculate_enhanced_candidate_score,
    generate_enhanced_skill_recommendations, get_enhanced_service_capabilities,
    train_ml_models, generate_bias_report
)

router = APIRouter()

@router.post("/resumes/parse-enhanced")
async def parse_resume_with_advanced_features(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Parse resume with all advanced features (OCR, multilingual, LLM)."""
    try:
        # Save uploaded file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_filename = f"temp_{uuid.uuid4().hex}.{file_extension}"
        temp_path = f"uploads/temp/{temp_filename}"
        
        # Create temp directory if it doesn't exist
        import os
        os.makedirs("uploads/temp", exist_ok=True)
        
        # Save file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse with enhanced features
        result = await parse_resume_enhanced(temp_path, file_extension, language)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced parsing failed: {str(e)}"
        )

@router.post("/candidates/score-enhanced")
async def calculate_enhanced_candidate_score_endpoint(
    candidate_data: Dict[str, Any],
    job_requirements: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Calculate candidate score using all advanced methods."""
    try:
        result = await calculate_enhanced_candidate_score(candidate_data, job_requirements)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced scoring failed: {str(e)}"
        )

@router.get("/skills/recommendations-enhanced")
async def get_enhanced_skill_recommendations_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """Get skill recommendations using all advanced methods."""
    try:
        # Get user's resume data
        resumes_collection = get_collection("resumes")
        latest_resume = await resumes_collection.find_one(
            {"candidate_id": current_user.user_id, "status": "processed"},
            sort=[("created_at", -1)]
        )
        
        if not latest_resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No processed resume found"
            )
        
        # Get market trends
        jobs_collection = get_collection("jobs")
        all_jobs = await jobs_collection.find({"status": "active"}).to_list(length=None)
        
        # Extract market trends
        skill_frequency = {}
        for job in all_jobs:
            for skill in job.get("required_skills", []):
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        market_trends = {
            'top_skills': [{'skill': skill, 'count': count} for skill, count in skill_frequency.items()],
            'total_jobs': len(all_jobs)
        }
        
        # Generate enhanced recommendations
        result = await generate_enhanced_skill_recommendations(
            latest_resume.get('parsed_data', {}), market_trends
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced recommendations failed: {str(e)}"
        )

@router.get("/capabilities")
async def get_service_capabilities(
    current_user: dict = Depends(get_current_user)
):
    """Get capabilities of all advanced services."""
    try:
        capabilities = await get_enhanced_service_capabilities()
        return capabilities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capabilities: {str(e)}"
        )

@router.post("/ml-models/train")
async def train_ml_models_endpoint(
    training_data: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_hr_user)
):
    """Train ML models with historical data (HR only)."""
    try:
        result = await train_ml_models(training_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML model training failed: {str(e)}"
        )

@router.get("/bias/report")
async def get_bias_report_endpoint(
    time_period_days: int = 30,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get bias detection report (HR only)."""
    try:
        result = await generate_bias_report(time_period_days)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias report generation failed: {str(e)}"
        )

@router.get("/bias/dashboard")
async def get_bias_dashboard(
    current_user: dict = Depends(get_current_hr_user)
):
    """Get bias detection dashboard data (HR only)."""
    try:
        # Get recent bias reports
        bias_reports = []
        for days in [7, 30, 90]:
            report = await generate_bias_report(days)
            bias_reports.append({
                'period_days': days,
                'report': report
            })
        
        return {
            'bias_reports': bias_reports,
            'dashboard_updated': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias dashboard failed: {str(e)}"
        )

@router.post("/candidates/bias-analysis")
async def analyze_candidate_bias_endpoint(
    candidate_data: Dict[str, Any],
    ranking_score: float,
    job_requirements: Dict[str, Any],
    current_user: dict = Depends(get_current_hr_user)
):
    """Analyze candidate for potential bias (HR only)."""
    try:
        from services.bias_service import analyze_candidate_bias
        
        result = await analyze_candidate_bias(candidate_data, ranking_score, job_requirements)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bias analysis failed: {str(e)}"
        )

@router.get("/ontology/stats")
async def get_ontology_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get ontology statistics."""
    try:
        from services.ontology_service import get_ontology_stats
        
        stats = await get_ontology_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ontology stats failed: {str(e)}"
        )

@router.get("/multilingual/supported-languages")
async def get_supported_languages(
    current_user: dict = Depends(get_current_user)
):
    """Get supported languages for multilingual processing."""
    try:
        from services.multilingual_service import get_multilingual_capabilities
        
        capabilities = await get_multilingual_capabilities()
        return capabilities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multilingual capabilities failed: {str(e)}"
        )

@router.post("/ocr/process-image")
async def process_image_resume(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    current_user: dict = Depends(get_current_user)
):
    """Process image-based resume using OCR."""
    try:
        # Save uploaded file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_filename = f"temp_{uuid.uuid4().hex}.{file_extension}"
        temp_path = f"uploads/temp/{temp_filename}"
        
        # Create temp directory if it doesn't exist
        import os
        os.makedirs("uploads/temp", exist_ok=True)
        
        # Save file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process with OCR
        from services.ocr_service import parse_image_resume
        result = await parse_image_resume(temp_path, file_extension, language)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )

@router.get("/llm/analysis")
async def get_llm_analysis(
    resume_data: Dict[str, Any],
    job_requirements: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Get LLM-based analysis of resume."""
    try:
        from services.llm_service import analyze_resume_with_llm
        
        result = await analyze_resume_with_llm(resume_data, job_requirements)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM analysis failed: {str(e)}"
        )
