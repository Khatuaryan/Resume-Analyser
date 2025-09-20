"""
LLM Integration Service for Contextual Analysis
Provides optional LLM-based evaluation for qualitative candidate feedback,
context detection, and improved semantic understanding of resumes.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-based contextual analysis."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, local
        self.model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.enabled = bool(self.openai_api_key or self.anthropic_api_key)
        self.cache = {}
        
    async def analyze_resume_context(
        self, 
        resume_data: Dict[str, Any], 
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze resume context using LLM."""
        if not self.enabled:
            return self._fallback_analysis(resume_data, job_requirements)
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(resume_data, job_requirements)
            
            # Get LLM response
            response = await self._call_llm(prompt)
            
            # Parse response
            analysis = self._parse_llm_response(response)
            
            return {
                'contextual_analysis': analysis,
                'llm_provider': self.llm_provider,
                'model_used': self.model_name,
                'timestamp': datetime.now().isoformat(),
                'confidence': analysis.get('confidence', 0.7)
            }
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return self._fallback_analysis(resume_data, job_requirements)
    
    def _create_analysis_prompt(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> str:
        """Create analysis prompt for LLM."""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        education = resume_data.get('education', [])
        summary = resume_data.get('summary', '')
        
        job_title = job_requirements.get('title', 'Software Engineer')
        job_description = job_requirements.get('description', '')
        required_skills = job_requirements.get('required_skills', [])
        
        prompt = f"""
        Analyze this candidate's resume for the position of {job_title} and provide a comprehensive evaluation.
        
        CANDIDATE INFORMATION:
        Skills: {', '.join(skills)}
        Experience: {len(experience)} positions
        Education: {len(education)} degrees
        Summary: {summary}
        
        JOB REQUIREMENTS:
        Title: {job_title}
        Description: {job_description}
        Required Skills: {', '.join(required_skills)}
        
        Please provide a JSON response with the following structure:
        {{
            "overall_assessment": "Brief overall assessment of the candidate",
            "strengths": ["List of candidate strengths"],
            "weaknesses": ["List of areas for improvement"],
            "skill_match_analysis": "Detailed analysis of skill alignment",
            "experience_relevance": "Assessment of experience relevance",
            "cultural_fit_indicators": "Indicators of cultural fit",
            "recommendation": "Hire/Maybe/No recommendation with reasoning",
            "interview_questions": ["Suggested interview questions"],
            "development_areas": ["Areas for professional development"],
            "confidence": 0.85
        }}
        
        Focus on:
        1. Technical skill alignment
        2. Experience relevance
        3. Growth potential
        4. Cultural fit indicators
        5. Specific strengths and weaknesses
        6. Interview recommendations
        """
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API."""
        if self.llm_provider == "openai":
            return await self._call_openai(prompt)
        elif self.llm_provider == "anthropic":
            return await self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are an expert HR analyst. Provide detailed, objective analysis of candidates."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_parse(response)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        return {
            "overall_assessment": "LLM analysis completed but parsing failed",
            "strengths": ["Analysis available in raw response"],
            "weaknesses": ["Parsing error occurred"],
            "skill_match_analysis": "See raw response for details",
            "experience_relevance": "Analysis completed",
            "cultural_fit_indicators": "Available in response",
            "recommendation": "Review required",
            "interview_questions": ["General questions recommended"],
            "development_areas": ["See detailed analysis"],
            "confidence": 0.5,
            "raw_response": response
        }
    
    def _fallback_analysis(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available."""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        # Simple rule-based analysis
        strengths = []
        weaknesses = []
        
        if len(skills) > 5:
            strengths.append("Strong technical skills")
        else:
            weaknesses.append("Limited technical skills")
        
        if len(experience) > 2:
            strengths.append("Relevant work experience")
        else:
            weaknesses.append("Limited work experience")
        
        return {
            'contextual_analysis': {
                'overall_assessment': 'Basic analysis completed without LLM',
                'strengths': strengths,
                'weaknesses': weaknesses,
                'skill_match_analysis': 'Basic skill matching performed',
                'experience_relevance': 'Experience reviewed',
                'cultural_fit_indicators': 'Standard assessment',
                'recommendation': 'Review recommended',
                'interview_questions': ['Standard interview questions'],
                'development_areas': ['General development areas'],
                'confidence': 0.3
            },
            'llm_provider': 'fallback',
            'model_used': 'rule_based',
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.3
        }
    
    async def generate_skill_recommendations(
        self, 
        resume_data: Dict[str, Any], 
        market_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate skill recommendations using LLM."""
        if not self.enabled:
            return self._fallback_skill_recommendations(resume_data, market_trends)
        
        try:
            prompt = self._create_skill_recommendation_prompt(resume_data, market_trends)
            response = await self._call_llm(prompt)
            analysis = self._parse_llm_response(response)
            
            return {
                'skill_recommendations': analysis,
                'llm_provider': self.llm_provider,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in LLM skill recommendations: {e}")
            return self._fallback_skill_recommendations(resume_data, market_trends)
    
    def _create_skill_recommendation_prompt(self, resume_data: Dict[str, Any], market_trends: Dict[str, Any]) -> str:
        """Create skill recommendation prompt."""
        current_skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        prompt = f"""
        Based on this candidate's profile and current market trends, provide personalized skill recommendations.
        
        CANDIDATE PROFILE:
        Current Skills: {', '.join(current_skills)}
        Experience Level: {len(experience)} positions
        Current Role: {experience[0].get('title', 'Unknown') if experience else 'Entry Level'}
        
        MARKET TRENDS:
        In-demand Skills: {', '.join(market_trends.get('top_skills', [])[:10])}
        Popular Locations: {', '.join(market_trends.get('top_locations', [])[:5])}
        
        Provide a JSON response with:
        {{
            "recommended_skills": ["List of 5-8 recommended skills"],
            "skill_priorities": ["Priority order of skills to learn"],
            "learning_paths": {{
                "skill1": ["Learning resources for skill1"],
                "skill2": ["Learning resources for skill2"]
            }},
            "market_alignment": "How well candidate aligns with market trends",
            "career_advice": "Specific career development advice",
            "timeline": "Suggested learning timeline",
            "confidence": 0.85
        }}
        """
        
        return prompt
    
    def _fallback_skill_recommendations(self, resume_data: Dict[str, Any], market_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback skill recommendations."""
        return {
            'skill_recommendations': {
                'recommended_skills': ['Python', 'JavaScript', 'SQL', 'Git', 'Communication'],
                'skill_priorities': ['Technical skills', 'Soft skills', 'Industry knowledge'],
                'learning_paths': {
                    'Python': ['Online courses', 'Practice projects', 'Documentation'],
                    'JavaScript': ['Tutorials', 'Build projects', 'Community engagement']
                },
                'market_alignment': 'Basic alignment analysis',
                'career_advice': 'Focus on in-demand skills',
                'timeline': '3-6 months',
                'confidence': 0.3
            },
            'llm_provider': 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    async def detect_bias_indicators(
        self, 
        resume_data: Dict[str, Any], 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect potential bias indicators in analysis."""
        if not self.enabled:
            return {'bias_detected': False, 'indicators': []}
        
        try:
            prompt = self._create_bias_detection_prompt(resume_data, analysis_results)
            response = await self._call_llm(prompt)
            bias_analysis = self._parse_llm_response(response)
            
            return {
                'bias_analysis': bias_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bias detection: {e}")
            return {'bias_detected': False, 'indicators': [], 'error': str(e)}
    
    def _create_bias_detection_prompt(self, resume_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> str:
        """Create bias detection prompt."""
        prompt = f"""
        Analyze this resume evaluation for potential bias indicators.
        
        CANDIDATE INFO:
        Name: {resume_data.get('personal_info', {}).get('name', 'Anonymous')}
        Skills: {', '.join(resume_data.get('skills', []))}
        Experience: {len(resume_data.get('experience', []))} positions
        
        ANALYSIS RESULTS:
        Recommendation: {analysis_results.get('recommendation', 'Unknown')}
        Strengths: {', '.join(analysis_results.get('strengths', []))}
        Weaknesses: {', '.join(analysis_results.get('weaknesses', []))}
        
        Check for potential bias in:
        1. Gender bias in language
        2. Age-related assumptions
        3. Cultural bias
        4. Educational bias
        5. Experience bias
        6. Name-based bias
        
        Provide JSON response:
        {{
            "bias_detected": true/false,
            "bias_indicators": ["List of detected bias indicators"],
            "recommendations": ["Suggestions to reduce bias"],
            "confidence": 0.85
        }}
        """
        
        return prompt

# Global LLM service instance
llm_service = LLMService()

async def initialize_llm_service():
    """Initialize LLM service."""
    logger.info(f"LLM service initialized. Provider: {llm_service.llm_provider}, Enabled: {llm_service.enabled}")

async def analyze_resume_with_llm(
    resume_data: Dict[str, Any], 
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze resume using LLM."""
    return await llm_service.analyze_resume_context(resume_data, job_requirements)

async def generate_llm_skill_recommendations(
    resume_data: Dict[str, Any], 
    market_trends: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate skill recommendations using LLM."""
    return await llm_service.generate_skill_recommendations(resume_data, market_trends)

async def detect_bias_with_llm(
    resume_data: Dict[str, Any], 
    analysis_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Detect bias using LLM."""
    return await llm_service.detect_bias_indicators(resume_data, analysis_results)
