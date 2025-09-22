"""
OCR and Multi-Modal Parsing Service
Supports image-based resumes (scanned PDFs, screenshots) using OCR
and converts extracted text into structured JSON compatible with existing modules.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import io
import base64
from datetime import datetime

# Optional imports for OCR functionality
try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    import easyocr
    from pdf2image import convert_from_path
    import fitz  # PyMuPDF
    OCR_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"OCR dependencies not available: {e}")
    OCR_AVAILABLE = False
    # Create dummy classes to prevent import errors
    cv2 = None
    np = None
    Image = None
    pytesseract = None
    easyocr = None
    convert_from_path = None
    fitz = None

logger = logging.getLogger(__name__)

class OCRService:
    """Service for OCR and multi-modal resume parsing."""
    
    def __init__(self):
        if not OCR_AVAILABLE:
            logger.warning("OCR service initialized but dependencies not available")
        self.tesseract_path = None
        self.easyocr_reader = None
        self.supported_formats = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']
        self.ocr_engines = ['tesseract', 'easyocr', 'pymupdf']
        self.primary_engine = 'tesseract'
        
        # Initialize OCR engines
        if OCR_AVAILABLE:
            self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize OCR engines."""
        try:
            # Initialize EasyOCR
            self.easyocr_reader = easyocr.Reader(['en', 'es', 'fr'])
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize EasyOCR: {e}")
            self.easyocr_reader = None
        
        # Set Tesseract path if available
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR available")
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            self.primary_engine = 'easyocr' if self.easyocr_reader else 'pymupdf'
    
    async def parse_image_resume(
        self, 
        file_path: str, 
        file_type: str,
        language: str = 'en'
    ) -> Dict[str, Any]:
        """Parse image-based resume using OCR."""
        try:
            # Extract text from image
            extracted_text = await self._extract_text_from_image(file_path, file_type, language)
            
            if not extracted_text.strip():
                return {
                    'success': False,
                    'error': 'No text extracted from image',
                    'raw_text': ''
                }
            
            # Process extracted text with NLP
            processed_data = await self._process_ocr_text(extracted_text)
            
            return {
                'success': True,
                'raw_text': extracted_text,
                'parsed_data': processed_data,
                'ocr_engine_used': self.primary_engine,
                'confidence': self._calculate_ocr_confidence(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"Error in OCR parsing: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'parsed_data': None
            }
    
    async def _extract_text_from_image(
        self, 
        file_path: str, 
        file_type: str, 
        language: str
    ) -> str:
        """Extract text from image using multiple OCR engines."""
        if file_type.lower() == 'pdf':
            return await self._extract_from_pdf(file_path, language)
        else:
            return await self._extract_from_image_file(file_path, language)
    
    async def _extract_from_pdf(self, file_path: str, language: str) -> str:
        """Extract text from PDF using multiple methods."""
        extracted_texts = []
        
        # Method 1: PyMuPDF (fastest)
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            if text.strip():
                extracted_texts.append(('pymupdf', text))
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")
        
        # Method 2: PDF to images + OCR
        try:
            images = convert_from_path(file_path, dpi=300)
            ocr_text = ""
            for image in images:
                # Convert PIL to OpenCV format
                img_array = np.array(image)
                if len(img_array.shape) == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Extract text using OCR
                page_text = await self._ocr_image(img_array, language)
                ocr_text += page_text + "\n"
            
            if ocr_text.strip():
                extracted_texts.append(('pdf2image+ocr', ocr_text))
        except Exception as e:
            logger.warning(f"PDF to image conversion failed: {e}")
        
        # Choose best result
        if not extracted_texts:
            return ""
        
        # Prefer PyMuPDF if available, otherwise use OCR
        for method, text in extracted_texts:
            if method == 'pymupdf' and text.strip():
                return text
        
        return extracted_texts[0][1] if extracted_texts else ""
    
    async def _extract_from_image_file(self, file_path: str, language: str) -> str:
        """Extract text from image file."""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Preprocess image
            processed_image = await self._preprocess_image(image)
            
            # Extract text using OCR
            text = await self._ocr_image(processed_image, language)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting from image file: {e}")
            return ""
    
    async def _preprocess_image(self, image: "np.ndarray") -> "np.ndarray":
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return processed
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    async def _ocr_image(self, image: "np.ndarray", language: str) -> str:
        """Extract text from image using available OCR engines."""
        texts = []
        
        # Try Tesseract
        if self.primary_engine == 'tesseract':
            try:
                tesseract_text = pytesseract.image_to_string(
                    image, 
                    lang=language,
                    config='--psm 6'
                )
                if tesseract_text.strip():
                    texts.append(('tesseract', tesseract_text))
            except Exception as e:
                logger.warning(f"Tesseract OCR failed: {e}")
        
        # Try EasyOCR
        if self.easyocr_reader:
            try:
                results = self.easyocr_reader.readtext(image)
                easyocr_text = ' '.join([result[1] for result in results])
                if easyocr_text.strip():
                    texts.append(('easyocr', easyocr_text))
            except Exception as e:
                logger.warning(f"EasyOCR failed: {e}")
        
        # Choose best result
        if not texts:
            return ""
        
        # Prefer the primary engine result
        for engine, text in texts:
            if engine == self.primary_engine:
                return text
        
        # Return the first available result
        return texts[0][1]
    
    async def _process_ocr_text(self, text: str) -> Dict[str, Any]:
        """Process OCR extracted text using NLP."""
        # This would integrate with the existing NLP service
        # For now, return a basic structure
        
        lines = text.split('\n')
        processed_data = {
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
        
        # Basic text processing
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract email
            if '@' in line and '.' in line:
                email_match = line.split()
                for word in email_match:
                    if '@' in word and '.' in word:
                        processed_data['contact_info']['email'] = word
                        break
            
            # Extract phone
            if any(char.isdigit() for char in line) and len(line) > 7:
                processed_data['contact_info']['phone'] = line
            
            # Extract skills (basic keyword matching)
            skill_keywords = [
                'python', 'javascript', 'java', 'react', 'node', 'sql', 'aws',
                'docker', 'kubernetes', 'git', 'html', 'css', 'mongodb'
            ]
            
            for keyword in skill_keywords:
                if keyword.lower() in line.lower():
                    if keyword.title() not in processed_data['skills']:
                        processed_data['skills'].append(keyword.title())
        
        return processed_data
    
    def _calculate_ocr_confidence(self, text: str) -> float:
        """Calculate confidence score for OCR extraction."""
        if not text.strip():
            return 0.0
        
        # Basic confidence calculation
        confidence = 0.5
        
        # Check for common resume elements
        resume_indicators = [
            'experience', 'education', 'skills', 'contact', 'email', 'phone',
            'university', 'college', 'degree', 'bachelor', 'master', 'phd'
        ]
        
        text_lower = text.lower()
        found_indicators = sum(1 for indicator in resume_indicators if indicator in text_lower)
        confidence += (found_indicators / len(resume_indicators)) * 0.3
        
        # Check text length (longer text usually means better extraction)
        if len(text) > 500:
            confidence += 0.1
        if len(text) > 1000:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    async def detect_language(self, text: str) -> str:
        """Detect language of extracted text."""
        try:
            from langdetect import detect
            return detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'  # Default to English
    
    async def enhance_image_quality(self, image_path: str) -> str:
        """Enhance image quality for better OCR results."""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (1, 1), 0)
            
            # Apply sharpening
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(blurred, -1, kernel)
            
            # Save enhanced image
            enhanced_path = image_path.replace('.', '_enhanced.')
            cv2.imwrite(enhanced_path, sharpened)
            
            return enhanced_path
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image_path
    
    async def get_ocr_capabilities(self) -> Dict[str, Any]:
        """Get OCR service capabilities."""
        return {
            'supported_formats': self.supported_formats,
            'available_engines': self.ocr_engines,
            'primary_engine': self.primary_engine,
            'easyocr_available': self.easyocr_reader is not None,
            'tesseract_available': self.primary_engine == 'tesseract',
            'languages_supported': ['en', 'es', 'fr'] if self.easyocr_reader else ['en']
        }

# Global OCR service instance
ocr_service = OCRService()

async def initialize_ocr_service():
    """Initialize OCR service."""
    logger.info("OCR service initialized")

async def parse_image_resume(
    file_path: str, 
    file_type: str, 
    language: str = 'en'
) -> Dict[str, Any]:
    """Parse image-based resume using OCR."""
    return await ocr_service.parse_image_resume(file_path, file_type, language)

async def get_ocr_capabilities() -> Dict[str, Any]:
    """Get OCR service capabilities."""
    return await ocr_service.get_ocr_capabilities()
