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
        print("🔥 Starting Firebase setup...")
        # Initialize Firebase connection
        firebase = await get_firebase_connection()
        print("✅ Firebase connection established")
        
        # Check if admin user already exists
        existing_admin = await firebase.get_document("users", "admin-hr-001")
        if existing_admin:
            print("✅ Admin user already exists")
        else:
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
        
        # No sample candidate users - system will be ready for real users
        
        # No sample resume data - system will be ready for real resumes
        
        print("\\n📊 Firebase Setup Complete!")
        print("   Users: 1 (1 admin)")
        print("   Resumes: 0 (ready for real resumes)")
        print("   Database: Firebase Firestore")
        print("\\n🌐 Access your data at: https://console.firebase.google.com/")
        
    except Exception as e:
        print(f"❌ Error setting up Firebase: {e}")
        print("⚠️  Continuing with application startup...")
        # Don't raise the exception to prevent app startup failure

if __name__ == "__main__":
    asyncio.run(setup_firebase())
