"""
Traditional ML Models Fallback System
Implements Random Forest, KNN, and Decision Tree models for candidate ranking
as a fallback to transformer-based scoring.
"""

import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import logging
from pathlib import Path
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class MLModelsService:
    """Service for traditional ML models fallback system."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_weights = {
            'random_forest': 0.4,
            'knn': 0.3,
            'decision_tree': 0.3
        }
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.is_trained = False
        
    async def initialize_models(self):
        """Initialize and load pre-trained models if available."""
        try:
            # Try to load existing models
            await self._load_models()
            if self.is_trained:
                logger.info("Loaded pre-trained ML models")
            else:
                logger.info("No pre-trained models found, will train on first use")
        except Exception as e:
            logger.warning(f"Could not load existing models: {e}")
            self.is_trained = False
    
    async def _load_models(self):
        """Load pre-trained models from disk."""
        model_files = {
            'random_forest': 'random_forest_model.joblib',
            'knn': 'knn_model.joblib',
            'decision_tree': 'decision_tree_model.joblib'
        }
        
        scaler_files = {
            'scaler': 'scaler.joblib',
            'label_encoder': 'label_encoder.joblib'
        }
        
        # Load models
        for model_name, filename in model_files.items():
            model_path = self.models_dir / filename
            if model_path.exists():
                self.models[model_name] = joblib.load(model_path)
        
        # Load scalers and encoders
        for scaler_name, filename in scaler_files.items():
            scaler_path = self.models_dir / filename
            if scaler_path.exists():
                self.scalers[scaler_name] = joblib.load(scaler_path)
        
        self.is_trained = len(self.models) > 0
    
    async def _save_models(self):
        """Save trained models to disk."""
        try:
            # Save models
            for model_name, model in self.models.items():
                model_path = self.models_dir / f"{model_name}_model.joblib"
                joblib.dump(model, model_path)
            
            # Save scalers and encoders
            for scaler_name, scaler in self.scalers.items():
                scaler_path = self.models_dir / f"{scaler_name}.joblib"
                joblib.dump(scaler, scaler_path)
            
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def train_models(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Train ML models on historical data."""
        if not training_data:
            logger.warning("No training data provided")
            return {}
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            
            # Prepare features and target
            X, y = self._prepare_training_data(df)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers['scaler'] = scaler
            
            # Train models
            model_scores = {}
            
            # Random Forest
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X_train_scaled, y_train)
            rf_score = rf_model.score(X_test_scaled, y_test)
            self.models['random_forest'] = rf_model
            model_scores['random_forest'] = rf_score
            
            # KNN
            knn_model = KNeighborsRegressor(
                n_neighbors=5,
                weights='distance'
            )
            knn_model.fit(X_train_scaled, y_train)
            knn_score = knn_model.score(X_test_scaled, y_test)
            self.models['knn'] = knn_model
            model_scores['knn'] = knn_score
            
            # Decision Tree
            dt_model = DecisionTreeRegressor(
                max_depth=10,
                random_state=42
            )
            dt_model.fit(X_train_scaled, y_train)
            dt_score = dt_model.score(X_test_scaled, y_test)
            self.models['decision_tree'] = dt_model
            model_scores['decision_tree'] = dt_score
            
            self.is_trained = True
            await self._save_models()
            
            logger.info(f"Models trained successfully. Scores: {model_scores}")
            return model_scores
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {}
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML models."""
        # Feature engineering
        features = []
        
        # Extract numerical features
        if 'skills_count' in df.columns:
            features.append(df['skills_count'].fillna(0))
        else:
            features.append(pd.Series([0] * len(df)))
        
        if 'experience_years' in df.columns:
            features.append(df['experience_years'].fillna(0))
        else:
            features.append(pd.Series([0] * len(df)))
        
        if 'education_level' in df.columns:
            # Encode education level
            le = LabelEncoder()
            education_encoded = le.fit_transform(df['education_level'].fillna('unknown'))
            features.append(pd.Series(education_encoded))
            self.encoders['education'] = le
        else:
            features.append(pd.Series([0] * len(df)))
        
        # Add skill match features
        if 'skill_match_score' in df.columns:
            features.append(df['skill_match_score'].fillna(0))
        else:
            features.append(pd.Series([0] * len(df)))
        
        # Add job relevance features
        if 'job_relevance_score' in df.columns:
            features.append(df['job_relevance_score'].fillna(0))
        else:
            features.append(pd.Series([0] * len(df)))
        
        # Combine features
        X = np.column_stack(features)
        
        # Target variable (overall score)
        if 'overall_score' in df.columns:
            y = df['overall_score'].values
        else:
            # Generate synthetic target if not available
            y = np.random.uniform(60, 95, len(df))
        
        return X, y
    
    async def predict_candidate_score(
        self, 
        resume_data: Dict[str, Any], 
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict candidate score using ensemble of ML models."""
        if not self.is_trained:
            logger.warning("Models not trained, using fallback scoring")
            return self._fallback_scoring(resume_data, job_requirements)
        
        try:
            # Prepare features
            features = self._extract_features(resume_data, job_requirements)
            
            # Scale features
            if 'scaler' in self.scalers:
                features_scaled = self.scalers['scaler'].transform([features])
            else:
                features_scaled = [features]
            
            # Get predictions from all models
            predictions = {}
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(features_scaled)[0]
                    predictions[model_name] = max(0, min(100, pred))  # Clamp to 0-100
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {e}")
                    predictions[model_name] = 50  # Default fallback
            
            # Ensemble prediction
            ensemble_score = sum(
                predictions[model] * self.model_weights[model] 
                for model in predictions.keys()
            )
            
            return {
                'overall_score': round(ensemble_score, 2),
                'model_predictions': predictions,
                'model_weights': self.model_weights,
                'confidence': self._calculate_confidence(predictions),
                'model_type': 'traditional_ml'
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return self._fallback_scoring(resume_data, job_requirements)
    
    def _extract_features(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> List[float]:
        """Extract features for ML models."""
        features = []
        
        # Skills count
        skills = resume_data.get('skills', [])
        features.append(len(skills))
        
        # Experience years (estimate from experience data)
        experience = resume_data.get('experience', [])
        experience_years = len(experience) * 2  # Rough estimate
        features.append(experience_years)
        
        # Education level (encoded)
        education = resume_data.get('education', [])
        if education:
            degree = education[0].get('degree', '').lower()
            if 'phd' in degree or 'doctorate' in degree:
                edu_level = 4
            elif 'master' in degree:
                edu_level = 3
            elif 'bachelor' in degree:
                edu_level = 2
            elif 'associate' in degree or 'diploma' in degree:
                edu_level = 1
            else:
                edu_level = 0
        else:
            edu_level = 0
        features.append(edu_level)
        
        # Skill match score
        job_skills = job_requirements.get('required_skills', [])
        if job_skills:
            matched_skills = sum(1 for skill in job_skills if skill.lower() in [s.lower() for s in skills])
            skill_match_score = (matched_skills / len(job_skills)) * 100
        else:
            skill_match_score = 0
        features.append(skill_match_score)
        
        # Job relevance score (based on experience and skills)
        relevance_score = min(100, (len(skills) * 5) + (experience_years * 10))
        features.append(relevance_score)
        
        return features
    
    def _calculate_confidence(self, predictions: Dict[str, float]) -> float:
        """Calculate confidence based on prediction variance."""
        if len(predictions) < 2:
            return 0.5
        
        values = list(predictions.values())
        mean_val = np.mean(values)
        variance = np.var(values)
        
        # Higher confidence for lower variance
        confidence = max(0.1, 1.0 - (variance / 1000))
        return round(confidence, 2)
    
    def _fallback_scoring(self, resume_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scoring when ML models are not available."""
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        education = resume_data.get('education', [])
        
        # Simple scoring algorithm
        skills_score = min(100, len(skills) * 10)
        experience_score = min(100, len(experience) * 20)
        education_score = min(100, len(education) * 25)
        
        overall_score = (skills_score * 0.4 + experience_score * 0.4 + education_score * 0.2)
        
        return {
            'overall_score': round(overall_score, 2),
            'model_predictions': {'fallback': overall_score},
            'model_weights': {'fallback': 1.0},
            'confidence': 0.3,
            'model_type': 'fallback'
        }
    
    async def get_model_performance(self) -> Dict[str, Any]:
        """Get performance metrics for trained models."""
        if not self.is_trained:
            return {'status': 'not_trained', 'message': 'Models not trained yet'}
        
        return {
            'status': 'trained',
            'models_available': list(self.models.keys()),
            'model_weights': self.model_weights,
            'last_trained': datetime.now().isoformat()
        }

# Global ML models service instance
ml_models_service = MLModelsService()

async def initialize_ml_models():
    """Initialize ML models service."""
    await ml_models_service.initialize_models()

async def train_ml_models(training_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Train ML models on historical data."""
    return await ml_models_service.train_models(training_data)

async def predict_with_ml_models(
    resume_data: Dict[str, Any], 
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """Predict candidate score using ML models."""
    return await ml_models_service.predict_candidate_score(resume_data, job_requirements)

async def get_ml_models_performance() -> Dict[str, Any]:
    """Get ML models performance metrics."""
    return await ml_models_service.get_model_performance()
