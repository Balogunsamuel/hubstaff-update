#!/usr/bin/env python3
"""
Test database connections for both MongoDB and Supabase
"""

import os
import asyncio
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database_adapter import db_adapter

async def test_mongodb():
    """Test MongoDB connection"""
    print("🔄 Testing MongoDB connection...")
    
    # Set environment for MongoDB
    os.environ["DATABASE_TYPE"] = "mongodb"
    
    try:
        # Reinitialize adapter with MongoDB
        db_adapter.__init__()
        await db_adapter.connect()
        
        # Test basic operations
        test_doc = {
            "name": "Test User",
            "email": "test@example.com",
            "created_at": datetime.utcnow()
        }
        
        # Create
        doc_id = await db_adapter.create_document("test_users", test_doc)
        print(f"✅ MongoDB: Created document with ID: {doc_id}")
        
        # Read
        found_doc = await db_adapter.get_document("test_users", {"_id": doc_id})
        if found_doc:
            print(f"✅ MongoDB: Retrieved document: {found_doc['name']}")
        else:
            print("❌ MongoDB: Could not retrieve document")
            return False
        
        # Update
        updated = await db_adapter.update_document(
            "test_users", 
            {"_id": doc_id}, 
            {"name": "Updated Test User"}
        )
        print(f"✅ MongoDB: Updated document: {updated}")
        
        # Delete
        deleted = await db_adapter.delete_document("test_users", {"_id": doc_id})
        print(f"✅ MongoDB: Deleted document: {deleted}")
        
        await db_adapter.disconnect()
        print("✅ MongoDB connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_supabase():
    """Test Supabase connection"""
    print("\n🔄 Testing Supabase connection...")
    
    # Check if Supabase credentials are available
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # Set environment for Supabase
    os.environ["DATABASE_TYPE"] = "supabase"
    
    try:
        # Reinitialize adapter with Supabase
        db_adapter.__init__()
        # No async connect needed for Supabase
        
        # Test basic operations (Note: you need to create a test table in Supabase first)
        test_doc = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        # For this test, we'll just try to connect
        from database.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        # Try to query an existing table (users table should exist)
        result = client.table("users").select("id").limit(1).execute()
        print("✅ Supabase: Connection successful!")
        print(f"✅ Supabase: Can query users table (found {len(result.data)} rows)")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("Make sure you've run the SQL schema in Supabase SQL editor")
        return False

async def main():
    """Run all database connection tests"""
    load_dotenv()
    
    print("🧪 Testing Database Connections")
    print("=" * 50)
    
    # Test MongoDB (development)
    mongodb_success = await test_mongodb()
    
    # Test Supabase (production)
    supabase_success = test_supabase()
    
    print("\n📊 Test Results")
    print("=" * 50)
    print(f"MongoDB:  {'✅ PASS' if mongodb_success else '❌ FAIL'}")
    print(f"Supabase: {'✅ PASS' if supabase_success else '❌ FAIL'}")
    
    if mongodb_success and supabase_success:
        print("\n🎉 All database connections working!")
        print("You can now use MongoDB for development and Supabase for production")
    elif mongodb_success:
        print("\n✅ MongoDB working - good for development")
        print("🔧 Set up Supabase for production deployment")
    elif supabase_success:
        print("\n✅ Supabase working - ready for production")
        print("🔧 Fix MongoDB for local development")
    else:
        print("\n❌ Both database connections failed")
        print("Please check your configuration")

if __name__ == "__main__":
    asyncio.run(main())