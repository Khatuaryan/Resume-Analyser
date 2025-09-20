"""
Example data for testing the Smart Resume Analyzer Platform.
This script creates sample users, jobs, and resumes for demonstration.
"""

import asyncio
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sample data
SAMPLE_USERS = [
    {
        "email": "hr@techcorp.com",
        "full_name": "Sarah Johnson",
        "phone": "+1-555-0123",
        "company": "TechCorp",
        "role": "hr",
        "password": "password123"
    },
    {
        "email": "candidate1@email.com",
        "full_name": "John Smith",
        "phone": "+1-555-0124",
        "role": "candidate",
        "password": "password123"
    },
    {
        "email": "candidate2@email.com",
        "full_name": "Emily Davis",
        "phone": "+1-555-0125",
        "role": "candidate",
        "password": "password123"
    }
]

SAMPLE_JOBS = [
    {
        "title": "Senior Software Engineer",
        "description": "We are looking for a Senior Software Engineer to join our team. You will be responsible for developing and maintaining our web applications using modern technologies.",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "job_type": "full_time",
        "experience_level": "senior",
        "salary_min": 120000,
        "salary_max": 180000,
        "required_skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
        "preferred_skills": ["Docker", "Kubernetes", "PostgreSQL", "Redis"],
        "benefits": ["Health Insurance", "401k", "Flexible Hours", "Remote Work"],
        "requirements": ["Bachelor's degree in Computer Science", "5+ years experience", "Strong problem-solving skills"],
        "responsibilities": ["Develop web applications", "Code reviews", "Mentor junior developers", "Architecture decisions"]
    },
    {
        "title": "Frontend Developer",
        "description": "Join our frontend team to build amazing user experiences. We use React, TypeScript, and modern CSS frameworks.",
        "company": "TechCorp",
        "location": "New York, NY",
        "job_type": "full_time",
        "experience_level": "mid",
        "salary_min": 80000,
        "salary_max": 120000,
        "required_skills": ["React", "JavaScript", "TypeScript", "CSS", "HTML"],
        "preferred_skills": ["Next.js", "Tailwind CSS", "GraphQL", "Jest"],
        "benefits": ["Health Insurance", "401k", "Learning Budget", "Gym Membership"],
        "requirements": ["3+ years frontend experience", "Portfolio of work", "Team collaboration skills"],
        "responsibilities": ["Build user interfaces", "Optimize performance", "Cross-browser testing", "Code reviews"]
    },
    {
        "title": "Data Scientist",
        "description": "We need a Data Scientist to analyze large datasets and build ML models. Experience with Python, pandas, and scikit-learn required.",
        "company": "DataCorp",
        "location": "Seattle, WA",
        "job_type": "full_time",
        "experience_level": "mid",
        "salary_min": 90000,
        "salary_max": 140000,
        "required_skills": ["Python", "Pandas", "Scikit-learn", "SQL", "Statistics"],
        "preferred_skills": ["TensorFlow", "PyTorch", "AWS", "Docker"],
        "benefits": ["Health Insurance", "401k", "Research Time", "Conference Budget"],
        "requirements": ["Master's degree in Data Science", "3+ years experience", "Strong analytical skills"],
        "responsibilities": ["Analyze data", "Build ML models", "Present findings", "Collaborate with engineering"]
    }
]

SAMPLE_RESUMES = [
    {
        "filename": "john_smith_resume.pdf",
        "file_type": "pdf",
        "parsed_data": {
            "personal_info": {
                "name": "John Smith",
                "location": "San Francisco, CA"
            },
            "contact_info": {
                "email": "john.smith@email.com",
                "phone": "+1-555-0124",
                "linkedin": "linkedin.com/in/johnsmith"
            },
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "institution": "University of California, Berkeley",
                    "field_of_study": "Computer Science",
                    "end_date": "2020"
                }
            ],
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "start_date": "2020",
                    "end_date": "2023",
                    "description": "Developed web applications using React and Node.js"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB", "AWS"],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built a full-stack e-commerce platform",
                    "technologies": ["React", "Node.js", "MongoDB"]
                }
            ]
        }
    },
    {
        "filename": "emily_davis_resume.pdf",
        "file_type": "pdf",
        "parsed_data": {
            "personal_info": {
                "name": "Emily Davis",
                "location": "New York, NY"
            },
            "contact_info": {
                "email": "emily.davis@email.com",
                "phone": "+1-555-0125",
                "linkedin": "linkedin.com/in/emilydavis"
            },
            "education": [
                {
                    "degree": "Master of Science",
                    "institution": "Stanford University",
                    "field_of_study": "Data Science",
                    "end_date": "2021"
                }
            ],
            "experience": [
                {
                    "title": "Data Scientist",
                    "company": "Analytics Inc",
                    "start_date": "2021",
                    "end_date": "2023",
                    "description": "Built ML models for customer segmentation"
                }
            ],
            "skills": ["Python", "Pandas", "Scikit-learn", "TensorFlow", "SQL", "AWS"],
            "projects": [
                {
                    "name": "Customer Segmentation Model",
                    "description": "Developed ML model for customer segmentation",
                    "technologies": ["Python", "Scikit-learn", "Pandas"]
                }
            ]
        }
    }
]

async def create_sample_data():
    """Create sample data for testing."""
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/resume_analyzer?authSource=admin")
    db = client.resume_analyzer
    
    print("Creating sample data...")
    
    # Create users
    users_collection = db.users
    user_ids = {}
    
    for user_data in SAMPLE_USERS:
        password = user_data.pop("password")
        hashed_password = pwd_context.hash(password)
        
        user_doc = {
            **user_data,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await users_collection.insert_one(user_doc)
        user_ids[user_data["email"]] = str(result.inserted_id)
        print(f"Created user: {user_data['full_name']}")
    
    # Create jobs
    jobs_collection = db.jobs
    job_ids = []
    
    for job_data in SAMPLE_JOBS:
        job_doc = {
            **job_data,
            "hr_id": user_ids["hr@techcorp.com"],
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "application_count": 0,
            "view_count": 0
        }
        
        result = await jobs_collection.insert_one(job_doc)
        job_ids.append(str(result.inserted_id))
        print(f"Created job: {job_data['title']}")
    
    # Create resumes
    resumes_collection = db.resumes
    
    for i, resume_data in enumerate(SAMPLE_RESUMES):
        candidate_email = f"candidate{i+1}@email.com"
        resume_doc = {
            "candidate_id": user_ids[candidate_email],
            "filename": resume_data["filename"],
            "file_path": f"/uploads/resumes/{resume_data['filename']}",
            "file_type": resume_data["file_type"],
            "file_size": 1024000,  # 1MB
            "status": "processed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "parsed_data": resume_data["parsed_data"],
            "analysis_score": 85.5
        }
        
        result = await resumes_collection.insert_one(resume_doc)
        print(f"Created resume: {resume_data['filename']}")
    
    # Create applications
    applications_collection = db.applications
    
    # John Smith applies to first job
    application1 = {
        "job_id": job_ids[0],
        "candidate_id": user_ids["candidate1@email.com"],
        "cover_letter": "I am very interested in this position and believe my skills align well with your requirements.",
        "application_date": datetime.utcnow(),
        "status": "pending"
    }
    await applications_collection.insert_one(application1)
    
    # Emily Davis applies to third job
    application2 = {
        "job_id": job_ids[2],
        "candidate_id": user_ids["candidate2@email.com"],
        "cover_letter": "I have extensive experience in data science and machine learning.",
        "application_date": datetime.utcnow(),
        "status": "pending"
    }
    await applications_collection.insert_one(application2)
    
    print("Sample data created successfully!")
    print("\nSample users created:")
    print("- HR: hr@techcorp.com / password123")
    print("- Candidate 1: candidate1@email.com / password123")
    print("- Candidate 2: candidate2@email.com / password123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
