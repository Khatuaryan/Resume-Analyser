#!/usr/bin/env python3
"""
Database initialization script.
Creates the admin HR user and sets up the database.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import connect_to_mongo, get_database
from auth.jwt_handler import get_password_hash

async def init_database():
    """Initialize the database with admin user."""
    try:
        # Connect to database first
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        users_collection = db["users"]
        
        # Check if admin user already exists
        existing_admin = await users_collection.find_one({"email": "admin"})
        
        if existing_admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        admin_user = {
            "_id": "admin-hr-001",
            "email": "admin@resumeanalyzer.com",
            "full_name": "System Administrator",
            "phone": "+1-000-000-0000",
            "company": "Resume Analyzer System",
            "role": "hr",
            "hashed_password": get_password_hash("password123@"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert admin user
        result = await users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            print("✅ Admin user created successfully")
            print(f"   Email: admin@resumeanalyzer.com")
            print(f"   Password: password123@")
            print(f"   Role: HR")
        else:
            print("❌ Failed to create admin user")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
