"""
Ethical AI & Bias Auditing Service
Implements logging and evaluation metrics to detect bias in candidate ranking
(gender, race, names) and includes human-in-the-loop validation dashboard.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class BiasDetectionService:
    """Service for bias detection and auditing in candidate ranking."""
    
    def __init__(self):
        self.bias_logs = []
        self.bias_metrics = {}
        self.demographic_patterns = {}
        self.audit_thresholds = {
            'gender_bias': 0.15,  # 15% difference threshold
            'name_bias': 0.20,    # 20% difference threshold
            'education_bias': 0.25,  # 25% difference threshold
            'experience_bias': 0.30  # 30% difference threshold
        }
        
        # Initialize demographic patterns
        self._initialize_demographic_patterns()
    
    def _initialize_demographic_patterns(self):
        """Initialize patterns for demographic detection."""
        # Gender indicators (names and pronouns)
        self.demographic_patterns = {
            'gender': {
                'female_indicators': [
                    'she', 'her', 'hers', 'ms', 'mrs', 'miss', 'madam',
                    # Common female names (subset for privacy)
                    'sarah', 'jennifer', 'jessica', 'amanda', 'ashley', 'emily', 'michelle'
                ],
                'male_indicators': [
                    'he', 'him', 'his', 'mr', 'sir',
                    # Common male names (subset for privacy)
                    'john', 'michael', 'david', 'james', 'robert', 'william', 'richard'
                ]
            },
            'education_bias': {
                'prestigious_schools': [
                    'harvard', 'stanford', 'mit', 'yale', 'princeton', 'columbia',
                    'university of california', 'berkeley', 'carnegie mellon'
                ],
                'community_colleges': [
                    'community college', 'junior college', 'technical college'
                ]
            },
            'geographic_bias': {
                'major_cities': [
                    'new york', 'san francisco', 'los angeles', 'chicago', 'boston',
                    'seattle', 'austin', 'denver'
                ],
                'rural_indicators': [
                    'rural', 'small town', 'county', 'township'
                ]
            }
        }
    
    async def analyze_candidate_bias(
        self, 
        candidate_data: Dict[str, Any], 
        ranking_score: float,
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze potential bias in candidate evaluation."""
        try:
            bias_indicators = {}
            
            # Extract candidate information
            personal_info = candidate_data.get('personal_info', {})
            contact_info = candidate_data.get('contact_info', {})
            education = candidate_data.get('education', [])
            experience = candidate_data.get('experience', [])
            
            # Check for gender bias indicators
            gender_bias = await self._detect_gender_bias(personal_info, contact_info)
            if gender_bias['bias_detected']:
                bias_indicators['gender'] = gender_bias
            
            # Check for name bias
            name_bias = await self._detect_name_bias(personal_info)
            if name_bias['bias_detected']:
                bias_indicators['name'] = name_bias
            
            # Check for education bias
            education_bias = await self._detect_education_bias(education)
            if education_bias['bias_detected']:
                bias_indicators['education'] = education_bias
            
            # Check for experience bias
            experience_bias = await self._detect_experience_bias(experience)
            if experience_bias['bias_detected']:
                bias_indicators['experience'] = experience_bias
            
            # Check for geographic bias
            geographic_bias = await self._detect_geographic_bias(personal_info, experience)
            if geographic_bias['bias_detected']:
                bias_indicators['geographic'] = geographic_bias
            
            # Log bias detection
            if bias_indicators:
                await self._log_bias_detection(candidate_data, bias_indicators, ranking_score)
            
            return {
                'bias_detected': len(bias_indicators) > 0,
                'bias_indicators': bias_indicators,
                'overall_bias_score': self._calculate_overall_bias_score(bias_indicators),
                'recommendations': self._generate_bias_recommendations(bias_indicators),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bias analysis: {e}")
            return {
                'bias_detected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _detect_gender_bias(self, personal_info: Dict[str, Any], contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential gender bias indicators."""
        text_content = f"{personal_info.get('name', '')} {contact_info.get('email', '')}"
        text_lower = text_content.lower()
        
        female_indicators = sum(1 for indicator in self.demographic_patterns['gender']['female_indicators'] 
                              if indicator in text_lower)
        male_indicators = sum(1 for indicator in self.demographic_patterns['gender']['male_indicators'] 
                            if indicator in text_lower)
        
        bias_detected = abs(female_indicators - male_indicators) > 2
        
        return {
            'bias_detected': bias_detected,
            'female_indicators': female_indicators,
            'male_indicators': male_indicators,
            'bias_type': 'gender',
            'confidence': min(1.0, (female_indicators + male_indicators) / 10)
        }
    
    async def _detect_name_bias(self, personal_info: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential name-based bias."""
        name = personal_info.get('name', '').lower()
        
        # Check for non-Western names (basic pattern matching)
        non_western_patterns = [
            r'[^a-z\s]',  # Non-ASCII characters
            r'\b(ahmed|mohammed|ali|hassan|ibrahim)\b',  # Common non-Western names
            r'\b(wei|chen|li|wang|zhang)\b',  # Common Asian names
            r'\b(patel|sharma|singh|kumar)\b'  # Common South Asian names
        ]
        
        bias_indicators = sum(1 for pattern in non_western_patterns if re.search(pattern, name))
        bias_detected = bias_indicators > 0
        
        return {
            'bias_detected': bias_detected,
            'bias_indicators': bias_indicators,
            'bias_type': 'name',
            'confidence': min(1.0, bias_indicators / len(non_western_patterns))
        }
    
    async def _detect_education_bias(self, education: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential education bias."""
        if not education:
            return {'bias_detected': False, 'bias_type': 'education'}
        
        education_text = ' '.join([edu.get('institution', '') for edu in education]).lower()
        
        prestigious_count = sum(1 for school in self.demographic_patterns['education_bias']['prestigious_schools'] 
                              if school in education_text)
        community_count = sum(1 for school in self.demographic_patterns['education_bias']['community_colleges'] 
                            if school in education_text)
        
        # Bias if only prestigious schools or only community colleges
        bias_detected = (prestigious_count > 0 and community_count == 0) or (community_count > 0 and prestigious_count == 0)
        
        return {
            'bias_detected': bias_detected,
            'prestigious_schools': prestigious_count,
            'community_colleges': community_count,
            'bias_type': 'education',
            'confidence': min(1.0, (prestigious_count + community_count) / 5)
        }
    
    async def _detect_experience_bias(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential experience bias."""
        if not experience:
            return {'bias_detected': False, 'bias_type': 'experience'}
        
        # Check for experience gaps (potential bias indicators)
        experience_gaps = []
        for i, exp in enumerate(experience):
            if i > 0:
                # Check for gaps between experiences
                prev_exp = experience[i-1]
                if 'end_date' in prev_exp and 'start_date' in exp:
                    # Simple gap detection (would need proper date parsing in production)
                    pass
        
        # Check for startup vs corporate bias
        startup_companies = sum(1 for exp in experience 
                              if any(keyword in exp.get('company', '').lower() 
                                    for keyword in ['startup', 'inc', 'llc', 'corp']))
        corporate_companies = len(experience) - startup_companies
        
        bias_detected = abs(startup_companies - corporate_companies) > len(experience) * 0.7
        
        return {
            'bias_detected': bias_detected,
            'startup_experience': startup_companies,
            'corporate_experience': corporate_companies,
            'bias_type': 'experience',
            'confidence': min(1.0, abs(startup_companies - corporate_companies) / len(experience))
        }
    
    async def _detect_geographic_bias(self, personal_info: Dict[str, Any], experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential geographic bias."""
        location_text = personal_info.get('location', '')
        experience_locations = [exp.get('location', '') for exp in experience]
        all_locations = f"{location_text} {' '.join(experience_locations)}".lower()
        
        major_cities = sum(1 for city in self.demographic_patterns['geographic_bias']['major_cities'] 
                          if city in all_locations)
        rural_indicators = sum(1 for indicator in self.demographic_patterns['geographic_bias']['rural_indicators'] 
                             if indicator in all_locations)
        
        bias_detected = (major_cities > 0 and rural_indicators == 0) or (rural_indicators > 0 and major_cities == 0)
        
        return {
            'bias_detected': bias_detected,
            'major_cities': major_cities,
            'rural_indicators': rural_indicators,
            'bias_type': 'geographic',
            'confidence': min(1.0, (major_cities + rural_indicators) / 5)
        }
    
    def _calculate_overall_bias_score(self, bias_indicators: Dict[str, Any]) -> float:
        """Calculate overall bias score."""
        if not bias_indicators:
            return 0.0
        
        total_confidence = sum(indicator.get('confidence', 0) for indicator in bias_indicators.values())
        return min(1.0, total_confidence / len(bias_indicators))
    
    def _generate_bias_recommendations(self, bias_indicators: Dict[str, Any]) -> List[str]:
        """Generate recommendations to reduce bias."""
        recommendations = []
        
        for bias_type, indicator in bias_indicators.items():
            if bias_type == 'gender':
                recommendations.append("Review evaluation criteria for gender-neutral language")
            elif bias_type == 'name':
                recommendations.append("Implement blind resume screening for initial review")
            elif bias_type == 'education':
                recommendations.append("Focus on skills and experience rather than institution prestige")
            elif bias_type == 'experience':
                recommendations.append("Value diverse experience backgrounds equally")
            elif bias_type == 'geographic':
                recommendations.append("Consider remote work options to reduce geographic bias")
        
        return recommendations
    
    async def _log_bias_detection(
        self, 
        candidate_data: Dict[str, Any], 
        bias_indicators: Dict[str, Any], 
        ranking_score: float
    ):
        """Log bias detection for auditing."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'candidate_id': candidate_data.get('candidate_id', 'unknown'),
            'bias_indicators': bias_indicators,
            'ranking_score': ranking_score,
            'bias_score': self._calculate_overall_bias_score(bias_indicators),
            'requires_review': self._calculate_overall_bias_score(bias_indicators) > 0.5
        }
        
        self.bias_logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.bias_logs) > 1000:
            self.bias_logs = self.bias_logs[-1000:]
    
    async def generate_bias_report(self, time_period_days: int = 30) -> Dict[str, Any]:
        """Generate bias audit report."""
        try:
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            recent_logs = [log for log in self.bias_logs 
                          if datetime.fromisoformat(log['timestamp']) >= cutoff_date]
            
            if not recent_logs:
                return {
                    'period_days': time_period_days,
                    'total_candidates': 0,
                    'bias_detection_rate': 0.0,
                    'bias_types': {},
                    'recommendations': []
                }
            
            # Calculate statistics
            total_candidates = len(recent_logs)
            bias_detected_count = sum(1 for log in recent_logs if log['bias_detected'])
            bias_detection_rate = bias_detected_count / total_candidates
            
            # Analyze bias types
            bias_types = defaultdict(int)
            for log in recent_logs:
                for bias_type in log.get('bias_indicators', {}):
                    bias_types[bias_type] += 1
            
            # Calculate average bias scores
            avg_bias_score = np.mean([log.get('bias_score', 0) for log in recent_logs])
            
            # Generate recommendations
            recommendations = []
            if bias_detection_rate > 0.2:
                recommendations.append("High bias detection rate - review evaluation criteria")
            if 'gender' in bias_types and bias_types['gender'] > total_candidates * 0.1:
                recommendations.append("Gender bias detected - implement blind screening")
            if 'name' in bias_types and bias_types['name'] > total_candidates * 0.1:
                recommendations.append("Name bias detected - use structured evaluation")
            
            return {
                'period_days': time_period_days,
                'total_candidates': total_candidates,
                'bias_detection_rate': round(bias_detection_rate, 3),
                'average_bias_score': round(avg_bias_score, 3),
                'bias_types': dict(bias_types),
                'recommendations': recommendations,
                'requires_attention': bias_detection_rate > 0.15 or avg_bias_score > 0.5
            }
            
        except Exception as e:
            logger.error(f"Error generating bias report: {e}")
            return {
                'error': str(e),
                'period_days': time_period_days
            }
    
    async def get_bias_metrics(self) -> Dict[str, Any]:
        """Get current bias metrics."""
        return {
            'total_logs': len(self.bias_logs),
            'audit_thresholds': self.audit_thresholds,
            'demographic_patterns_loaded': len(self.demographic_patterns),
            'last_updated': datetime.now().isoformat()
        }
    
    async def export_bias_data(self, file_path: str):
        """Export bias detection data for external analysis."""
        try:
            export_data = {
                'bias_logs': self.bias_logs,
                'bias_metrics': self.bias_metrics,
                'audit_thresholds': self.audit_thresholds,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Bias data exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting bias data: {e}")

# Global bias detection service instance
bias_service = BiasDetectionService()

async def initialize_bias_service():
    """Initialize bias detection service."""
    logger.info("Bias detection service initialized")

async def analyze_candidate_bias(
    candidate_data: Dict[str, Any], 
    ranking_score: float,
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze potential bias in candidate evaluation."""
    return await bias_service.analyze_candidate_bias(candidate_data, ranking_score, job_requirements)

async def generate_bias_report(time_period_days: int = 30) -> Dict[str, Any]:
    """Generate bias audit report."""
    return await bias_service.generate_bias_report(time_period_days)

async def get_bias_metrics() -> Dict[str, Any]:
    """Get bias detection metrics."""
    return await bias_service.get_bias_metrics()
