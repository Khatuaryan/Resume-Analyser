"""
Multilingual Resume Support Service
Adds support for multiple languages (Spanish, French) for NER and keyword extraction
with fallback to English if translation fails.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
import spacy
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    Translator = None
from langdetect import detect, DetectorFactory
import re
from datetime import datetime

# Set seed for consistent language detection
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class MultilingualService:
    """Service for multilingual resume processing."""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese'
        }
        
        self.nlp_models = {}
        if GOOGLETRANS_AVAILABLE:
            self.translator = Translator()
        else:
            self.translator = None
        self.initialized = False
        
        # Language-specific patterns
        self.language_patterns = {
            'en': {
                'education_keywords': ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma'],
                'experience_keywords': ['experience', 'worked', 'job', 'position', 'role', 'company'],
                'skill_keywords': ['skills', 'technologies', 'programming', 'languages', 'tools'],
                'contact_keywords': ['contact', 'email', 'phone', 'address', 'location']
            },
            'es': {
                'education_keywords': ['universidad', 'colegio', 'grado', 'licenciatura', 'maestría', 'doctorado', 'diploma'],
                'experience_keywords': ['experiencia', 'trabajé', 'trabajo', 'puesto', 'rol', 'empresa'],
                'skill_keywords': ['habilidades', 'tecnologías', 'programación', 'lenguajes', 'herramientas'],
                'contact_keywords': ['contacto', 'correo', 'teléfono', 'dirección', 'ubicación']
            },
            'fr': {
                'education_keywords': ['université', 'collège', 'diplôme', 'licence', 'maîtrise', 'doctorat', 'certificat'],
                'experience_keywords': ['expérience', 'travaillé', 'emploi', 'poste', 'rôle', 'entreprise'],
                'skill_keywords': ['compétences', 'technologies', 'programmation', 'langages', 'outils'],
                'contact_keywords': ['contact', 'email', 'téléphone', 'adresse', 'localisation']
            }
        }
    
    async def initialize(self):
        """Initialize multilingual models."""
        if self.initialized:
            return
        
        try:
            # Load language models
            for lang_code in ['en', 'es', 'fr']:
                try:
                    if lang_code == 'en':
                        try:
                            self.nlp_models[lang_code] = spacy.load("en_core_web_sm")
                        except OSError:
                            logger.warning("spaCy model 'en_core_web_sm' not found. Using basic English model.")
                            self.nlp_models[lang_code] = spacy.blank("en")
                    elif lang_code == 'es':
                        try:
                            self.nlp_models[lang_code] = spacy.load("es_core_news_sm")
                        except OSError:
                            logger.warning("spaCy model 'es_core_news_sm' not found. Using basic Spanish model.")
                            self.nlp_models[lang_code] = spacy.blank("es")
                    elif lang_code == 'fr':
                        try:
                            self.nlp_models[lang_code] = spacy.load("fr_core_news_sm")
                        except OSError:
                            logger.warning("spaCy model 'fr_core_news_sm' not found. Using basic French model.")
                            self.nlp_models[lang_code] = spacy.blank("fr")
                    
                    logger.info(f"Loaded {lang_code} model successfully")
                except OSError:
                    logger.warning(f"Could not load {lang_code} model, using English fallback")
                    self.nlp_models[lang_code] = self.nlp_models.get('en')
            
            self.initialized = True
            logger.info("Multilingual service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing multilingual service: {e}")
            self.initialized = False
    
    async def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            if not text.strip():
                return 'en'
            
            # Use langdetect for language detection
            detected_lang = detect(text)
            
            # Validate detected language
            if detected_lang in self.supported_languages:
                return detected_lang
            else:
                logger.warning(f"Unsupported language detected: {detected_lang}, falling back to English")
                return 'en'
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'
    
    async def translate_text(self, text: str, target_lang: str = 'en') -> str:
        """Translate text to target language."""
        try:
            if not text.strip():
                return text
            
            # Detect source language
            source_lang = await self.detect_language(text)
            
            if source_lang == target_lang:
                return text
            
            # Translate text
            result = self.translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    async def parse_resume_multilingual(
        self, 
        text: str, 
        detected_language: str = None
    ) -> Dict[str, Any]:
        """Parse resume with multilingual support."""
        try:
            # Detect language if not provided
            if not detected_language:
                detected_language = await self.detect_language(text)
            
            # Get appropriate NLP model
            nlp_model = self.nlp_models.get(detected_language, self.nlp_models.get('en'))
            
            if not nlp_model:
                logger.error("No NLP model available")
                return self._fallback_parsing(text)
            
            # Parse with language-specific model
            doc = nlp_model(text)
            
            # Extract information using language-specific patterns
            parsed_data = await self._extract_multilingual_info(doc, detected_language)
            
            # Translate to English for consistency
            if detected_language != 'en':
                parsed_data = await self._translate_parsed_data(parsed_data)
            
            return {
                'success': True,
                'detected_language': detected_language,
                'parsed_data': parsed_data,
                'confidence': self._calculate_parsing_confidence(parsed_data)
            }
            
        except Exception as e:
            logger.error(f"Multilingual parsing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'parsed_data': self._fallback_parsing(text)
            }
    
    async def _extract_multilingual_info(self, doc, language: str) -> Dict[str, Any]:
        """Extract information using language-specific patterns."""
        patterns = self.language_patterns.get(language, self.language_patterns['en'])
        
        parsed_data = {
            'personal_info': {},
            'contact_info': {},
            'education': [],
            'experience': [],
            'skills': [],
            'projects': [],
            'certifications': [],
            'languages': [],
            'summary': ''
        }
        
        # Extract entities using spaCy
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                parsed_data['personal_info']['name'] = ent.text
            elif ent.label_ == "GPE":
                parsed_data['personal_info']['location'] = ent.text
            elif ent.label_ == "ORG":
                # Could be company or institution
                pass
        
        # Extract education using language-specific keywords
        education_section = self._find_section_by_keywords(doc, patterns['education_keywords'])
        if education_section:
            parsed_data['education'] = self._parse_education_section(education_section, language)
        
        # Extract experience
        experience_section = self._find_section_by_keywords(doc, patterns['experience_keywords'])
        if experience_section:
            parsed_data['experience'] = self._parse_experience_section(experience_section, language)
        
        # Extract skills
        skills_section = self._find_section_by_keywords(doc, patterns['skill_keywords'])
        if skills_section:
            parsed_data['skills'] = self._parse_skills_section(skills_section, language)
        
        # Extract contact information
        contact_section = self._find_section_by_keywords(doc, patterns['contact_keywords'])
        if contact_section:
            parsed_data['contact_info'] = self._parse_contact_section(contact_section)
        
        return parsed_data
    
    def _find_section_by_keywords(self, doc, keywords: List[str]) -> str:
        """Find text section containing specific keywords."""
        sentences = [sent.text for sent in doc.sents]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                return sentence
        
        return ""
    
    def _parse_education_section(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Parse education section."""
        education = []
        
        # Split by common separators
        lines = re.split(r'[;\n]', text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for degree patterns
            degree_patterns = {
                'en': r'(bachelor|master|phd|diploma|certificate)',
                'es': r'(licenciatura|maestría|doctorado|diploma|certificado)',
                'fr': r'(licence|maîtrise|doctorat|diplôme|certificat)'
            }
            
            pattern = degree_patterns.get(language, degree_patterns['en'])
            if re.search(pattern, line, re.IGNORECASE):
                education.append({
                    'degree': line,
                    'institution': 'Unknown',
                    'description': line
                })
        
        return education
    
    def _parse_experience_section(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Parse experience section."""
        experience = []
        
        # Split by common separators
        lines = re.split(r'[;\n]', text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for job title patterns
            if any(word in line.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'consultant']):
                experience.append({
                    'title': line,
                    'company': 'Unknown',
                    'description': line
                })
        
        return experience
    
    def _parse_skills_section(self, text: str, language: str) -> List[str]:
        """Parse skills section."""
        skills = []
        
        # Common technical skills
        tech_skills = [
            'python', 'javascript', 'java', 'react', 'node', 'sql', 'aws',
            'docker', 'kubernetes', 'git', 'html', 'css', 'mongodb'
        ]
        
        text_lower = text.lower()
        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        return skills
    
    def _parse_contact_section(self, text: str) -> Dict[str, Any]:
        """Parse contact information."""
        contact_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = ''.join(phone_match.groups())
        
        return contact_info
    
    async def _translate_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate parsed data to English for consistency."""
        try:
            translated_data = parsed_data.copy()
            
            # Translate education
            for edu in translated_data.get('education', []):
                if 'degree' in edu:
                    edu['degree'] = await self.translate_text(edu['degree'])
                if 'description' in edu:
                    edu['description'] = await self.translate_text(edu['description'])
            
            # Translate experience
            for exp in translated_data.get('experience', []):
                if 'title' in exp:
                    exp['title'] = await self.translate_text(exp['title'])
                if 'description' in exp:
                    exp['description'] = await self.translate_text(exp['description'])
            
            # Translate summary
            if 'summary' in translated_data:
                translated_data['summary'] = await self.translate_text(translated_data['summary'])
            
            return translated_data
            
        except Exception as e:
            logger.error(f"Translation of parsed data failed: {e}")
            return parsed_data
    
    def _calculate_parsing_confidence(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate confidence score for parsing."""
        confidence = 0.5
        
        # Check for key sections
        if parsed_data.get('education'):
            confidence += 0.1
        if parsed_data.get('experience'):
            confidence += 0.1
        if parsed_data.get('skills'):
            confidence += 0.1
        if parsed_data.get('contact_info'):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _fallback_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback parsing when multilingual processing fails."""
        return {
            'personal_info': {},
            'contact_info': {},
            'education': [],
            'experience': [],
            'skills': [],
            'projects': [],
            'certifications': [],
            'languages': [],
            'summary': text[:500] + '...' if len(text) > 500 else text
        }
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages."""
        return self.supported_languages
    
    async def get_language_capabilities(self) -> Dict[str, Any]:
        """Get language processing capabilities."""
        return {
            'supported_languages': self.supported_languages,
            'nlp_models_loaded': list(self.nlp_models.keys()),
            'translation_available': True,
            'initialized': self.initialized
        }

# Global multilingual service instance
multilingual_service = MultilingualService()

async def initialize_multilingual_service():
    """Initialize multilingual service."""
    await multilingual_service.initialize()

async def parse_resume_multilingual(
    text: str, 
    detected_language: str = None
) -> Dict[str, Any]:
    """Parse resume with multilingual support."""
    return await multilingual_service.parse_resume_multilingual(text, detected_language)

async def detect_language(text: str) -> str:
    """Detect language of text."""
    return await multilingual_service.detect_language(text)

async def translate_text(text: str, target_lang: str = 'en') -> str:
    """Translate text to target language."""
    return await multilingual_service.translate_text(text, target_lang)

async def get_multilingual_capabilities() -> Dict[str, Any]:
    """Get multilingual service capabilities."""
    return await multilingual_service.get_language_capabilities()
