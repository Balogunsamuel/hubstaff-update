import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Supabase:
    client: Optional[Client] = None

supabase_db = Supabase()

def connect_to_supabase():
    """Create Supabase connection"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        supabase_db.client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        raise

def get_supabase_client():
    """Get Supabase client"""
    if not supabase_db.client:
        connect_to_supabase()
    return supabase_db.client

class SupabaseOperations:
    
    @staticmethod
    def create_document(table: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified table"""
        client = get_supabase_client()
        
        # Add timestamps
        document["created_at"] = datetime.utcnow().isoformat()
        document["updated_at"] = datetime.utcnow().isoformat()
        
        result = client.table(table).insert(document).execute()
        if result.data:
            return result.data[0]["id"]
        raise Exception("Failed to create document")
    
    @staticmethod
    def get_document(table: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single document from the table"""
        client = get_supabase_client()
        
        # Build query
        query_builder = client.table(table).select("*")
        for key, value in query.items():
            query_builder = query_builder.eq(key, value)
        
        result = query_builder.limit(1).execute()
        if result.data:
            return result.data[0]
        return None
    
    @staticmethod
    def get_documents(table: str, query: Dict[str, Any] = None, 
                     sort_by: str = None, sort_desc: bool = False,
                     limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get multiple documents from the table"""
        client = get_supabase_client()
        
        # Build query
        query_builder = client.table(table).select("*")
        
        if query:
            for key, value in query.items():
                if isinstance(value, dict) and "$in" in value:
                    # Handle MongoDB-style $in queries
                    query_builder = query_builder.in_(key, value["$in"])
                else:
                    query_builder = query_builder.eq(key, value)
        
        # Add sorting
        if sort_by:
            query_builder = query_builder.order(sort_by, desc=sort_desc)
        
        # Add pagination
        if offset:
            query_builder = query_builder.range(offset, offset + (limit or 1000) - 1)
        elif limit:
            query_builder = query_builder.limit(limit)
        
        result = query_builder.execute()
        return result.data if result.data else []
    
    @staticmethod
    def update_document(table: str, query: Dict[str, Any], 
                       update: Dict[str, Any]) -> bool:
        """Update a document in the table"""
        client = get_supabase_client()
        
        # Add updated timestamp
        update["updated_at"] = datetime.utcnow().isoformat()
        
        # Build update query
        query_builder = client.table(table)
        for key, value in query.items():
            query_builder = query_builder.eq(key, value)
        
        result = query_builder.update(update).execute()
        return len(result.data) > 0 if result.data else False
    
    @staticmethod
    def delete_document(table: str, query: Dict[str, Any]) -> bool:
        """Delete a document from the table"""
        client = get_supabase_client()
        
        # Build delete query
        query_builder = client.table(table)
        for key, value in query.items():
            query_builder = query_builder.eq(key, value)
        
        result = query_builder.delete().execute()
        return len(result.data) > 0 if result.data else False
    
    @staticmethod
    def count_documents(table: str, query: Dict[str, Any] = None) -> int:
        """Count documents in the table"""
        client = get_supabase_client()
        
        query_builder = client.table(table).select("*", count="exact")
        
        if query:
            for key, value in query.items():
                query_builder = query_builder.eq(key, value)
        
        result = query_builder.execute()
        return result.count if result.count else 0