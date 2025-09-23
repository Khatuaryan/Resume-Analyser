#!/usr/bin/env python3
"""
Firebase setup script.
Creates initial data in Firebase Firestore.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from database.firebase_connection import get_firebase_connection

async def setup_firebase():
    """Setup Firebase with initial data."""
    try:
        # Initialize Firebase connection
        firebase = await get_firebase_connection()
        
        # Create admin user
        admin_user = {
            "email": "admin@resumeanalyzer.com",
            "full_name": "System Administrator",
            "phone": "+1-000-000-0000",
            "company": "Resume Analyzer System",
            "role": "hr",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4Qz8K8K",  # password123@
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        await firebase.create_document("users", "admin-hr-001", admin_user)
        print("✅ Admin user created")
        
        # Create sample candidate users
        candidate_users = [
            {
                "email": "candidate1@email.com",
                "full_name": "John Smith",
                "phone": "+1-555-0124",
                "company": None,
                "role": "candidate",
                "hashed_password": "$2b$12$236Tj8RHjEyFu4crghoIt.HOvoRSGvxCAqRy16UUhBgtS.UalhRr2",  # password123
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "email": "candidate2@email.com",
                "full_name": "Emily Davis",
                "phone": "+1-555-0125",
                "company": None,
                "role": "candidate",
                "hashed_password": "$2b$12$pumZBtN9Vocw3lyH1a3fM.l6q/ZuhciRccIVf04AoCCF1mIv4iDJ.",  # password123
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
        ]
        
        for i, user in enumerate(candidate_users, 1):
            await firebase.create_document("users", f"candidate-{i:03d}", user)
            print(f"✅ Created candidate: {user['full_name']} ({user['email']})")
        
        # Create sample resume data
        sample_resumes = [
            {
                "candidate_id": "candidate-001",
                "filename": "john_smith_resume.pdf",
                "file_path": "uploads/resumes/john_smith_resume.pdf",
                "file_type": "pdf",
                "file_size": 102400,
                "status": "processed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "parsed_data": {
                    "personal_info": {"name": "John Smith"},
                    "contact_info": {"email": "candidate1@email.com", "phone": "+1-555-0124"},
                    "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB", "Express"],
                    "experience": [
                        {
                            "title": "Software Developer",
                            "company": "Tech Corp",
                            "duration": "2020-2023",
                            "description": "Developed web applications using React and Node.js"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Bachelor of Computer Science",
                            "institution": "University of Tech",
                            "year": "2018"
                        }
                    ]
                },
                "analysis_score": 85.5
            },
            {
                "candidate_id": "candidate-002",
                "filename": "emily_davis_resume.pdf",
                "file_path": "uploads/resumes/emily_davis_resume.pdf",
                "file_type": "pdf",
                "file_size": 95680,
                "status": "processed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "parsed_data": {
                    "personal_info": {"name": "Emily Davis"},
                    "contact_info": {"email": "candidate2@email.com", "phone": "+1-555-0125"},
                    "skills": ["Java", "Spring Boot", "MySQL", "AWS", "Docker", "Kubernetes"],
                    "experience": [
                        {
                            "title": "Backend Developer",
                            "company": "Data Solutions Inc",
                            "duration": "2021-2024",
                            "description": "Built scalable backend services using Java and Spring Boot"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master of Software Engineering",
                            "institution": "Tech University",
                            "year": "2021"
                        }
                    ]
                },
                "analysis_score": 92.3
            }
        ]
        
        for i, resume in enumerate(sample_resumes, 1):
            await firebase.create_document("resumes", f"resume-{i:03d}", resume)
            print(f"✅ Created resume: {resume['filename']} for {resume['candidate_id']}")
        
        print("\\n📊 Firebase Setup Complete!")
        print("   Users: 3 (1 admin + 2 candidates)")
        print("   Resumes: 2 with parsed data")
        print("   Database: Firebase Firestore")
        print("\\n🌐 Access your data at: https://console.firebase.google.com/")
        
    except Exception as e:
        print(f"❌ Error setting up Firebase: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(setup_firebase())
