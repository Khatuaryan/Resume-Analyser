"""
Firebase adapter to provide MongoDB-like interface.
This makes the transition from MongoDB to Firebase easier.
"""

from typing import Dict, List, Any, Optional
import uuid
from database.firebase_connection import get_firebase_connection

class FirebaseQuery:
    """Firebase query object that mimics MongoDB cursor."""
    
    def __init__(self, collection_name: str, query: Dict[str, Any] = None):
        self.collection_name = collection_name
        self.query = query
        self.firebase = None
        self.skip_count = 0
        self.limit_count = None
    
    async def _get_firebase(self):
        """Get Firebase connection."""
        if not self.firebase:
            self.firebase = await get_firebase_connection()
        return self.firebase
    
    def skip(self, count: int):
        """Skip documents (for pagination)."""
        self.skip_count = count
        return self
    
    def limit(self, count: int):
        """Limit number of documents."""
        self.limit_count = count
        return self
    
    async def to_list(self, length: int = None) -> List[Dict[str, Any]]:
        """Convert query to list of documents."""
        firebase = await self._get_firebase()
        collection = firebase.get_collection(self.collection_name)
        
        if self.query:
            # Convert MongoDB query to Firestore query
            docs = collection.where(list(self.query.keys())[0], "==", list(self.query.values())[0]).stream()
        else:
            docs = collection.stream()
        
        result = []
        count = 0
        skipped = 0
        
        for doc in docs:
            # Apply skip
            if skipped < self.skip_count:
                skipped += 1
                continue
                
            # Apply limit
            if self.limit_count is not None and count >= self.limit_count:
                break
            if length is not None and count >= length:
                break
                
            doc_data = doc.to_dict()
            doc_data["_id"] = doc.id  # Add document ID as _id for compatibility
            result.append(doc_data)
            count += 1
        return result

class FirebaseCollection:
    """Firebase collection adapter that mimics MongoDB collection interface."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.firebase = None
    
    async def _get_firebase(self):
        """Get Firebase connection."""
        if not self.firebase:
            self.firebase = await get_firebase_connection()
        return self.firebase
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching the query."""
        firebase = await self._get_firebase()
        collection = firebase.get_collection(self.collection_name)
        
        # Convert MongoDB query to Firestore query
        docs = collection.where(list(query.keys())[0], "==", list(query.values())[0]).limit(1).stream()
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data["_id"] = doc.id  # Add document ID as _id for compatibility
            return doc_data
        return None
    
    def find(self, query: Dict[str, Any] = None):
        """Find documents matching the query."""
        # Return a FirebaseQuery object that mimics MongoDB cursor
        return FirebaseQuery(self.collection_name, query)
    
    async def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Insert one document."""
        firebase = await self._get_firebase()
        doc_id = document.get("_id", str(uuid.uuid4()))
        await firebase.create_document(self.collection_name, doc_id, document)
        return {"inserted_id": doc_id}
    
    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Update one document."""
        firebase = await self._get_firebase()
        
        # Find the document first
        doc = await self.find_one(query)
        if doc:
            doc_id = doc.get("_id")
            if doc_id:
                # Update the document
                await firebase.update_document(self.collection_name, doc_id, update.get("$set", update))
                return {"matched_count": 1, "modified_count": 1}
        
        return {"matched_count": 0, "modified_count": 0}
    
    async def delete_one(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Delete one document."""
        firebase = await self._get_firebase()
        
        # Find the document first
        doc = await self.find_one(query)
        if doc:
            doc_id = doc.get("_id")
            if doc_id:
                await firebase.delete_document(self.collection_name, doc_id)
                return {"deleted_count": 1}
        
        return {"deleted_count": 0}
    
    async def count_documents(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching the query."""
        docs = await self.find(query)
        return len(docs)

def get_collection(collection_name: str) -> FirebaseCollection:
    """Get a Firebase collection adapter."""
    return FirebaseCollection(collection_name)
