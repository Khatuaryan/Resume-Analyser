"""
Enhanced NLP Service with Advanced Features Integration
Integrates all advanced features: ML models, LLM, OCR, multilingual support,
ontology, and bias detection for comprehensive resume analysis.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os

# Import all advanced services
from .nlp_service import NLPService
from .ml_models import initialize_ml_models, predict_with_ml_models, train_ml_models
from .llm_service import initialize_llm_service, analyze_resume_with_llm, generate_llm_skill_recommendations
from .ocr_service import initialize_ocr_service, parse_image_resume, get_ocr_capabilities
from .multilingual_service import initialize_multilingual_service, parse_resume_multilingual, detect_language
from .ontology_service import initialize_ontology_service, enhance_candidate_scoring_with_ontology
from .bias_service import initialize_bias_service, analyze_candidate_bias, generate_bias_report

logger = logging.getLogger(__name__)

class EnhancedNLPService:
    """Enhanced NLP service with all advanced features integrated."""
    
    def __init__(self):
        self.base_nlp = NLPService()
        self.features_enabled = {
            'ml_models': os.getenv('ENABLE_ML_MODELS', 'true').lower() == 'true',
            'llm_integration': os.getenv('ENABLE_LLM', 'false').lower() == 'true',
            'ocr_processing': os.getenv('ENABLE_OCR', 'true').lower() == 'true',
            'multilingual': os.getenv('ENABLE_MULTILINGUAL', 'true').lower() == 'true',
            'ontology': os.getenv('ENABLE_ONTOLOGY', 'true').lower() == 'true',
            'bias_detection': os.getenv('ENABLE_BIAS_DETECTION', 'true').lower() == 'true'
        }
        self.initialized = False
    
    async def initialize(self):
        """Initialize all enabled services."""
        if self.initialized:
            return
        
        try:
            # Initialize base NLP service
            await self.base_nlp.initialize()
            
            # Initialize advanced services based on configuration
            if self.features_enabled['ml_models']:
                await initialize_ml_models()
                logger.info("ML models service initialized")
            
            if self.features_enabled['llm_integration']:
                await initialize_llm_service()
                logger.info("LLM service initialized")
            
            if self.features_enabled['ocr_processing']:
                await initialize_ocr_service()
                logger.info("OCR service initialized")
            
            if self.features_enabled['multilingual']:
                await initialize_multilingual_service()
                logger.info("Multilingual service initialized")
            
            if self.features_enabled['ontology']:
                await initialize_ontology_service()
                logger.info("Ontology service initialized")
            
            if self.features_enabled['bias_detection']:
                await initialize_bias_service()
                logger.info("Bias detection service initialized")
            
            self.initialized = True
            logger.info("Enhanced NLP service initialized with features: " + 
                      ", ".join([k for k, v in self.features_enabled.items() if v]))
            
        except Exception as e:
            logger.error(f"Error initializing enhanced NLP service: {e}")
            raise e
    
    async def parse_resume_enhanced(
        self, 
        file_path: str, 
        file_type: str,
        language: str = None
    ) -> Dict[str, Any]:
        """Enhanced resume parsing with all available features."""
        try:
            # Detect if file is image-based
            is_image = file_type.lower() in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']
            
            if is_image and self.features_enabled['ocr_processing']:
                # Use OCR for image-based resumes
                ocr_result = await parse_image_resume(file_path, file_type, language or 'en')
                if ocr_result['success']:
                    text = ocr_result['raw_text']
                    parsed_data = ocr_result['parsed_data']
                else:
                    return {
                        'success': False,
                        'error': 'OCR processing failed',
                        'parsed_data': None
                    }
            else:
                # Use base NLP service for text-based files
                base_result = await self.base_nlp.parse_resume(file_path, file_type)
                if base_result['success']:
                    text = base_result['raw_text']
                    parsed_data = base_result['parsed_data']
                else:
                    return base_result
            
            # Detect language if multilingual support is enabled
            detected_language = 'en'
            if self.features_enabled['multilingual']:
                detected_language = await detect_language(text)
                if detected_language != 'en':
                    # Re-parse with language-specific model
                    multilingual_result = await parse_resume_multilingual(text, detected_language)
                    if multilingual_result['success']:
                        parsed_data = multilingual_result['parsed_data']
            
            # Enhance with LLM analysis if enabled
            llm_analysis = None
            if self.features_enabled['llm_integration']:
                try:
                    llm_analysis = await analyze_resume_with_llm(parsed_data, {})
                except Exception as e:
                    logger.warning(f"LLM analysis failed: {e}")
            
            return {
                'success': True,
                'parsed_data': parsed_data,
                'raw_text': text,
                'detected_language': detected_language,
                'llm_analysis': llm_analysis,
                'features_used': [k for k, v in self.features_enabled.items() if v],
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced resume parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'parsed_data': None
            }
    
    async def calculate_enhanced_candidate_score(
        self, 
        resume_data: Dict[str, Any], 
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate candidate score using all available methods."""
        try:
            scores = {}
            confidence_scores = {}
            
            # Base NLP scoring
            base_score = await self.base_nlp.calculate_candidate_score(resume_data, job_requirements)
            scores['base_nlp'] = base_score
            confidence_scores['base_nlp'] = 0.8
            
            # ML models scoring (if enabled)
            if self.features_enabled['ml_models']:
                try:
                    ml_score = await predict_with_ml_models(resume_data, job_requirements)
                    scores['ml_models'] = ml_score
                    confidence_scores['ml_models'] = ml_score.get('confidence', 0.7)
                except Exception as e:
                    logger.warning(f"ML models scoring failed: {e}")
            
            # Ontology-enhanced scoring (if enabled)
            if self.features_enabled['ontology']:
                try:
                    candidate_skills = resume_data.get('skills', [])
                    ontology_score = await enhance_candidate_scoring_with_ontology(
                        candidate_skills, job_requirements
                    )
                    scores['ontology'] = ontology_score
                    confidence_scores['ontology'] = ontology_score.get('confidence', 0.6)
                except Exception as e:
                    logger.warning(f"Ontology scoring failed: {e}")
            
            # LLM analysis (if enabled)
            llm_analysis = None
            if self.features_enabled['llm_integration']:
                try:
                    llm_analysis = await analyze_resume_with_llm(resume_data, job_requirements)
                    if llm_analysis and 'contextual_analysis' in llm_analysis:
                        # Extract score from LLM analysis
                        llm_score = llm_analysis['contextual_analysis'].get('confidence', 0.5) * 100
                        scores['llm'] = {'overall_score': llm_score}
                        confidence_scores['llm'] = llm_analysis.get('confidence', 0.5)
                except Exception as e:
                    logger.warning(f"LLM analysis failed: {e}")
            
            # Bias detection (if enabled)
            bias_analysis = None
            if self.features_enabled['bias_detection']:
                try:
                    overall_score = base_score.get('overall_score', 0)
                    bias_analysis = await analyze_candidate_bias(
                        resume_data, overall_score, job_requirements
                    )
                except Exception as e:
                    logger.warning(f"Bias analysis failed: {e}")
            
            # Calculate ensemble score
            ensemble_score = self._calculate_ensemble_score(scores, confidence_scores)
            
            return {
                'overall_score': ensemble_score,
                'individual_scores': scores,
                'confidence_scores': confidence_scores,
                'llm_analysis': llm_analysis,
                'bias_analysis': bias_analysis,
                'ensemble_method': 'weighted_average',
                'features_used': [k for k, v in self.features_enabled.items() if v],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced candidate scoring failed: {e}")
            return {
                'overall_score': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_ensemble_score(self, scores: Dict[str, Any], confidence_scores: Dict[str, float]) -> float:
        """Calculate ensemble score from multiple methods."""
        if not scores:
            return 0.0
        
        # Weight scores by confidence
        weighted_sum = 0.0
        total_weight = 0.0
        
        for method, score_data in scores.items():
            if isinstance(score_data, dict) and 'overall_score' in score_data:
                score = score_data['overall_score']
                confidence = confidence_scores.get(method, 0.5)
                
                weighted_sum += score * confidence
                total_weight += confidence
        
        if total_weight == 0:
            return 0.0
        
        return round(weighted_sum / total_weight, 2)
    
    async def generate_enhanced_skill_recommendations(
        self, 
        resume_data: Dict[str, Any], 
        market_trends: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate skill recommendations using all available methods."""
        try:
            recommendations = {}
            
            # Base recommendations (from original NLP service)
            base_recommendations = self._generate_base_recommendations(resume_data, market_trends)
            recommendations['base'] = base_recommendations
            
            # LLM recommendations (if enabled)
            if self.features_enabled['llm_integration']:
                try:
                    llm_recommendations = await generate_llm_skill_recommendations(resume_data, market_trends)
                    recommendations['llm'] = llm_recommendations
                except Exception as e:
                    logger.warning(f"LLM skill recommendations failed: {e}")
            
            # Ontology recommendations (if enabled)
            if self.features_enabled['ontology']:
                try:
                    candidate_skills = resume_data.get('skills', [])
                    ontology_recommendations = await enhance_candidate_scoring_with_ontology(
                        candidate_skills, {}
                    )
                    recommendations['ontology'] = ontology_recommendations
                except Exception as e:
                    logger.warning(f"Ontology recommendations failed: {e}")
            
            # Combine recommendations
            combined_recommendations = self._combine_recommendations(recommendations)
            
            return {
                'recommendations': combined_recommendations,
                'individual_recommendations': recommendations,
                'features_used': [k for k, v in self.features_enabled.items() if v],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Enhanced skill recommendations failed: {e}")
            return {
                'recommendations': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_base_recommendations(self, resume_data: Dict[str, Any], market_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Generate base skill recommendations."""
        current_skills = resume_data.get('skills', [])
        top_skills = market_trends.get('top_skills', [])
        
        # Find missing skills
        missing_skills = []
        for skill in top_skills[:10]:  # Top 10 market skills
            if skill['skill'].lower() not in [s.lower() for s in current_skills]:
                missing_skills.append(skill['skill'])
        
        return {
            'recommended_skills': missing_skills[:5],
            'market_alignment': len(missing_skills) / len(top_skills[:10]) if top_skills else 0,
            'reasoning': ['Based on current market trends']
        }
    
    def _combine_recommendations(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Combine recommendations from multiple sources."""
        all_skills = []
        all_reasoning = []
        
        for source, rec_data in recommendations.items():
            if isinstance(rec_data, dict):
                if 'recommended_skills' in rec_data:
                    all_skills.extend(rec_data['recommended_skills'])
                if 'reasoning' in rec_data:
                    all_reasoning.extend(rec_data['reasoning'])
        
        # Remove duplicates and limit
        unique_skills = list(dict.fromkeys(all_skills))[:10]
        
        return {
            'recommended_skills': unique_skills,
            'reasoning': all_reasoning,
            'sources': list(recommendations.keys())
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all enabled services."""
        capabilities = {
            'features_enabled': self.features_enabled,
            'initialized': self.initialized,
            'services': {}
        }
        
        # Get capabilities from each service
        if self.features_enabled['ocr_processing']:
            try:
                capabilities['services']['ocr'] = await get_ocr_capabilities()
            except Exception as e:
                capabilities['services']['ocr'] = {'error': str(e)}
        
        if self.features_enabled['multilingual']:
            try:
                capabilities['services']['multilingual'] = await self._get_multilingual_capabilities()
            except Exception as e:
                capabilities['services']['multilingual'] = {'error': str(e)}
        
        if self.features_enabled['ontology']:
            try:
                capabilities['services']['ontology'] = await self._get_ontology_capabilities()
            except Exception as e:
                capabilities['services']['ontology'] = {'error': str(e)}
        
        return capabilities
    
    async def _get_multilingual_capabilities(self) -> Dict[str, Any]:
        """Get multilingual service capabilities."""
        from .multilingual_service import get_multilingual_capabilities
        return await get_multilingual_capabilities()
    
    async def _get_ontology_capabilities(self) -> Dict[str, Any]:
        """Get ontology service capabilities."""
        from .ontology_service import get_ontology_stats
        return await get_ontology_stats()
    
    async def train_ml_models(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train ML models with historical data."""
        if not self.features_enabled['ml_models']:
            return {'error': 'ML models not enabled'}
        
        try:
            return await train_ml_models(training_data)
        except Exception as e:
            logger.error(f"ML model training failed: {e}")
            return {'error': str(e)}
    
    async def generate_bias_report(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Generate bias detection report."""
        if not self.features_enabled['bias_detection']:
            return {'error': 'Bias detection not enabled'}
        
        try:
            return await generate_bias_report(time_period_days)
        except Exception as e:
            logger.error(f"Bias report generation failed: {e}")
            return {'error': str(e)}

# Global enhanced NLP service instance
enhanced_nlp_service = EnhancedNLPService()

async def initialize_enhanced_nlp():
    """Initialize enhanced NLP service."""
    await enhanced_nlp_service.initialize()

async def parse_resume_enhanced(
    file_path: str, 
    file_type: str, 
    language: str = None
) -> Dict[str, Any]:
    """Parse resume with all enhanced features."""
    return await enhanced_nlp_service.parse_resume_enhanced(file_path, file_type, language)

async def calculate_enhanced_candidate_score(
    resume_data: Dict[str, Any], 
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate candidate score with all enhanced features."""
    return await enhanced_nlp_service.calculate_enhanced_candidate_score(resume_data, job_requirements)

async def generate_enhanced_skill_recommendations(
    resume_data: Dict[str, Any], 
    market_trends: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate skill recommendations with all enhanced features."""
    return await enhanced_nlp_service.generate_enhanced_skill_recommendations(resume_data, market_trends)

async def get_enhanced_service_capabilities() -> Dict[str, Any]:
    """Get enhanced service capabilities."""
    return await enhanced_nlp_service.get_service_capabilities()
