"""
Firebase connection and database operations.
Handles Firestore database connections and operations.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import firestore as firestore_client

class FirebaseConnection:
    """Firebase Firestore connection manager."""
    
    def __init__(self):
        self.db = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Firebase connection."""
        if self.initialized:
            return
        
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Initialize Firebase Admin SDK
                cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-service-account.json')
                
                if os.path.exists(cred_path):
                    # Use service account file
                    print(f"Using Firebase credentials from: {cred_path}")
                    cred = credentials.Certificate(cred_path)
                elif os.getenv('FIREBASE_CREDENTIALS_JSON'):
                    # Use JSON credentials from environment variable
                    cred_dict = json.loads(os.getenv('FIREBASE_CREDENTIALS_JSON'))
                    cred = credentials.Certificate(cred_dict)
                else:
                    # Use default credentials (for local development)
                    print("Using default Firebase credentials")
                    cred = credentials.ApplicationDefault()
                
                firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            self.initialized = True
            print("✅ Connected to Firebase Firestore")
            
        except Exception as e:
            print(f"❌ Error connecting to Firebase: {e}")
            raise e
    
    def get_collection(self, collection_name: str):
        """Get a Firestore collection reference."""
        if not self.initialized:
            raise Exception("Firebase not initialized")
        return self.db.collection(collection_name)
    
    async def create_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> str:
        """Create a document in Firestore."""
        collection = self.get_collection(collection_name)
        doc_ref = collection.document(document_id)
        doc_ref.set(data)
        return document_id
    
    async def get_document(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore."""
        collection = self.get_collection(collection_name)
        doc = collection.document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    async def update_document(self, collection_name: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in Firestore."""
        collection = self.get_collection(collection_name)
        doc_ref = collection.document(document_id)
        doc_ref.update(data)
        return True
    
    async def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from Firestore."""
        collection = self.get_collection(collection_name)
        doc_ref = collection.document(document_id)
        doc_ref.delete()
        return True
    
    async def query_collection(self, collection_name: str, filters: List[tuple] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Query a collection with optional filters."""
        collection = self.get_collection(collection_name)
        query = collection
        
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        if limit:
            query = query.limit(limit)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

# Global Firebase connection instance
firebase_connection = FirebaseConnection()

async def get_firebase_connection():
    """Get the Firebase connection instance."""
    if not firebase_connection.initialized:
        await firebase_connection.initialize()
    return firebase_connection

def get_collection(collection_name: str):
    """Get a Firestore collection reference."""
    if not firebase_connection.initialized:
        raise Exception("Firebase not initialized. Call initialize() first.")
    return firebase_connection.get_collection(collection_name)
