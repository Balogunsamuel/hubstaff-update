import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import logging

# Import both database clients
from .mongodb import DatabaseOperations as MongoOperations, connect_to_mongo, close_mongo_connection, db
from .supabase_client import SupabaseOperations, connect_to_supabase

logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """
    Unified database adapter that switches between MongoDB and Supabase
    based on environment configuration
    """
    
    def __init__(self):
        self.db_type = os.getenv("DATABASE_TYPE", "mongodb").lower()
        self.is_connected = False
    
    async def connect(self):
        """Initialize database connection based on environment"""
        try:
            if self.db_type == "supabase":
                connect_to_supabase()
                logger.info("Connected to Supabase")
            else:
                # Only try MongoDB if we have MONGO_URL
                mongo_url = os.getenv("MONGO_URL")
                if not mongo_url:
                    raise ValueError("MONGO_URL not found for MongoDB connection")
                await connect_to_mongo()
                logger.info("Connected to MongoDB")
            
            self.is_connected = True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.db_type == "mongodb" and self.is_connected:
            await close_mongo_connection()
        self.is_connected = False
    
    def _convert_mongo_id_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB _id queries to Supabase id queries"""
        if "_id" in query:
            query["id"] = query.pop("_id")
        return query
    
    def _convert_supabase_to_mongo_format(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Supabase document to MongoDB format (add _id field)"""
        if doc and "id" in doc and "_id" not in doc:
            doc["_id"] = doc["id"]
        return doc
    
    async def create_document(self, collection: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified collection/table"""
        if self.db_type == "supabase":
            return SupabaseOperations.create_document(collection, document)
        else:
            return await MongoOperations.create_document(collection, document)
    
    async def get_document(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single document from the collection/table"""
        if self.db_type == "supabase":
            query = self._convert_mongo_id_query(query)
            result = SupabaseOperations.get_document(collection, query)
            return self._convert_supabase_to_mongo_format(result) if result else None
        else:
            return await MongoOperations.get_document(collection, query)
    
    async def get_documents(self, collection: str, query: Dict[str, Any] = None, 
                          sort: List = None, limit: int = None, skip: int = 0) -> List[Dict[str, Any]]:
        """Get multiple documents from the collection/table"""
        if self.db_type == "supabase":
            if query:
                query = self._convert_mongo_id_query(query)
            
            # Convert MongoDB sort format to Supabase
            sort_by = None
            sort_desc = False
            if sort:
                if isinstance(sort, list) and len(sort) > 0:
                    if isinstance(sort[0], tuple):
                        sort_by, sort_direction = sort[0]
                        sort_desc = sort_direction == -1
                    elif isinstance(sort[0], str):
                        sort_by = sort[0]
            
            results = SupabaseOperations.get_documents(
                collection, query, sort_by, sort_desc, limit, skip
            )
            return [self._convert_supabase_to_mongo_format(doc) for doc in results]
        else:
            return await MongoOperations.get_documents(collection, query, sort, limit, skip)
    
    async def update_document(self, collection: str, query: Dict[str, Any], 
                            update: Dict[str, Any]) -> bool:
        """Update a document in the collection/table"""
        if self.db_type == "supabase":
            query = self._convert_mongo_id_query(query)
            
            # Handle MongoDB-style $set operations
            if "$set" in update:
                update = update["$set"]
            
            return SupabaseOperations.update_document(collection, query, update)
        else:
            return await MongoOperations.update_document(collection, query, update)
    
    async def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a document from the collection/table"""
        if self.db_type == "supabase":
            query = self._convert_mongo_id_query(query)
            return SupabaseOperations.delete_document(collection, query)
        else:
            return await MongoOperations.delete_document(collection, query)
    
    async def count_documents(self, collection: str, query: Dict[str, Any] = None) -> int:
        """Count documents in the collection/table"""
        if self.db_type == "supabase":
            if query:
                query = self._convert_mongo_id_query(query)
            return SupabaseOperations.count_documents(collection, query)
        else:
            return await MongoOperations.count_documents(collection, query)
    
    async def aggregate(self, collection: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation on the collection (MongoDB only for now)"""
        if self.db_type == "supabase":
            logger.warning("Aggregation not fully supported for Supabase, using basic query")
            # For simple aggregations, we can implement basic functionality
            # Complex aggregations would need to be rewritten as SQL
            return []
        else:
            return await MongoOperations.aggregate(collection, pipeline)

# Global database adapter instance
db_adapter = DatabaseAdapter()

# Convenience functions for backward compatibility
async def get_database():
    """Get database instance (backward compatibility)"""
    if db_adapter.db_type == "mongodb":
        return db.database
    else:
        # For Supabase, return the adapter itself
        return db_adapter