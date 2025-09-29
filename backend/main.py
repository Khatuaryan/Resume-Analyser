"""
Smart Resume Analyzer Platform - Main FastAPI Application
This is the main entry point for the backend API server.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database.firebase_connection import get_firebase_connection
from routers import auth, jobs, resumes, candidates, skills, advanced_features
from services.nlp_service import initialize_nlp_models
from services.enhanced_nlp_service import initialize_enhanced_nlp

# Load environment variables
load_dotenv()

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("🔥 Initializing core services...")
    await get_firebase_connection()
    print("✅ Firebase connection established")
    
    # Load ML models in background to avoid blocking startup
    print("🤖 Loading ML models in background...")
    try:
        await initialize_nlp_models()
        print("✅ NLP models loaded")
    except Exception as e:
        print(f"⚠️  NLP models loading failed: {e}")
    
    try:
        await initialize_enhanced_nlp()
        print("✅ Enhanced NLP models loaded")
    except Exception as e:
        print(f"⚠️  Enhanced NLP models loading failed: {e}")
    
    print("🚀 Backend startup complete!")
    yield
    # Shutdown
    # Firebase doesn't need explicit connection closing

app = FastAPI(
    title="Smart Resume Analyzer Platform",
    description="A comprehensive platform for HR and candidates to manage resumes, job postings, and skill analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(advanced_features.router, prefix="/api/advanced", tags=["Advanced Features"])

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Smart Resume Analyzer Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Smart Resume Analyzer Platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
