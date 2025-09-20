"""
Database connection and configuration for MongoDB.
Handles connection to MongoDB and provides database instance.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

# Global variables for database connection
client = None
database = None

async def connect_to_mongo():
    """Establish connection to MongoDB."""
    global client, database
    
    try:
        # MongoDB connection string
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        # Create client
        client = AsyncIOMotorClient(mongo_url)
        
        # Test connection
        await client.admin.command('ping')
        
        # Get database
        database_name = os.getenv("DATABASE_NAME", "resume_analyzer")
        database = client[database_name]
        
        print(f"✅ Connected to MongoDB: {database_name}")
        
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise e
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise e

async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    
    if client:
        client.close()
        print("✅ MongoDB connection closed")

def get_database():
    """Get the database instance."""
    if database is None:
        raise Exception("Database not connected. Call connect_to_mongo() first.")
    return database

def get_collection(collection_name: str):
    """Get a specific collection from the database."""
    db = get_database()
    return db[collection_name]
