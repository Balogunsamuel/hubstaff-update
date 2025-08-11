#!/usr/bin/env python3
"""
Simple test for database connections
"""

import os
import asyncio
from dotenv import load_dotenv

async def test_mongodb():
    """Test MongoDB connection"""
    print("🔄 Testing MongoDB connection...")
    
    try:
        from database.mongodb import connect_to_mongo, close_mongo_connection
        await connect_to_mongo()
        print("✅ MongoDB: Connection successful!")
        await close_mongo_connection()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_supabase():
    """Test Supabase connection"""
    print("🔄 Testing Supabase connection...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    try:
        from database.supabase_client import connect_to_supabase
        connect_to_supabase()
        print("✅ Supabase: Connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

async def main():
    load_dotenv()
    
    print("🧪 Testing Simple Database Connections")
    print("=" * 50)
    
    mongodb_ok = await test_mongodb()
    supabase_ok = test_supabase()
    
    print("\n📊 Results:")
    print(f"MongoDB (development): {'✅ Ready' if mongodb_ok else '❌ Failed'}")
    print(f"Supabase (production): {'✅ Ready' if supabase_ok else '❌ Failed'}")
    
    if mongodb_ok:
        print("\n🎉 You can use MongoDB for local development!")
    
    if supabase_ok:
        print("🎉 You can use Supabase for production!")
        print("📝 Don't forget to run the schema SQL in Supabase dashboard")

if __name__ == "__main__":
    asyncio.run(main())