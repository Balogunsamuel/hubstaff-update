#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
Run: python test_mongo_connection.py
"""

import sys
import os
import ssl
from pymongo import MongoClient
from dotenv import load_dotenv

def test_connection():
    # Load environment variables
    load_dotenv()
    
    # Use connection string from .env file
    MONGO_URL = os.getenv('MONGO_URL')
    DB_NAME = os.getenv('DB_NAME', 'hubstaff_clone_prod')
    
    if not MONGO_URL:
        print("❌ MONGO_URL not found in .env file")
        print("Please set MONGO_URL in your .env file")
        sys.exit(1)
    
    try:
        # Connect to MongoDB with SSL disabled verification
        client = MongoClient(MONGO_URL, 
                           serverSelectionTimeoutMS=10000,
                           ssl_cert_reqs=ssl.CERT_NONE,
                           ssl_match_hostname=False)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[DB_NAME]
        
        # Insert test document
        test_collection = db.test_collection
        test_doc = {"message": "Hello from Atlas!", "test": True}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Read test document
        found_doc = test_collection.find_one({"test": True})
        print(f"✅ Test document found: {found_doc['message']}")
        
        # Clean up
        test_collection.delete_one({"test": True})
        print("✅ Test document cleaned up")
        
        client.close()
        print("✅ All tests passed! Your MongoDB Atlas is ready.")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. Your connection string is correct")
        print("2. Your IP is whitelisted in Network Access")
        print("3. Your database user has correct permissions")
        sys.exit(1)

if __name__ == "__main__":
    print("Testing MongoDB Atlas connection...")
    print("Update MONGO_URL in this script with your connection string")
    print("-" * 50)
    test_connection()