#!/usr/bin/env python3
"""
Simple Supabase test - shows what works and what needs RLS adjustment
"""

import os
from dotenv import load_dotenv
from database.supabase_client import get_supabase_client
import uuid

def test_basic_connection():
    """Test basic Supabase connection and table existence"""
    load_dotenv()
    
    print("🔍 Testing Basic Supabase Setup")
    print("=" * 50)
    
    try:
        client = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Test if tables exist by trying to select with limit 0
        tables_to_test = [
            "users", "projects", "tasks", "time_entries", 
            "activity_data", "screenshots", "invitations", "password_reset_tokens"
        ]
        
        existing_tables = []
        for table in tables_to_test:
            try:
                result = client.table(table).select("id").limit(0).execute()
                existing_tables.append(table)
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' not found: {e}")
        
        if len(existing_tables) == len(tables_to_test):
            print(f"\n🎉 All {len(existing_tables)} tables exist!")
            
            # Test Row Level Security status
            print("\n🔒 Testing Row Level Security...")
            try:
                # Try to insert a test record
                test_data = {
                    "id": str(uuid.uuid4()),
                    "name": "RLS Test",
                    "email": f"test-{uuid.uuid4()}@example.com",
                    "role": "user"
                }
                
                result = client.table("users").insert(test_data).execute()
                if result.data:
                    print("✅ RLS allows inserts (or RLS is disabled)")
                    # Clean up
                    client.table("users").delete().eq("id", test_data["id"]).execute()
                else:
                    print("⚠️  RLS might be blocking inserts")
                    
            except Exception as e:
                if "row-level security policy" in str(e):
                    print("🔒 RLS is active and blocking operations")
                    print("\n📋 To fix this for testing:")
                    print("1. Go to Supabase Dashboard")
                    print("2. SQL Editor")
                    print("3. Run: ALTER TABLE users DISABLE ROW LEVEL SECURITY;")
                    print("4. Repeat for all tables for testing")
                    print("5. Re-enable RLS before production: ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
                else:
                    print(f"❌ Other error: {e}")
            
            return True
        else:
            print(f"\n❌ Only {len(existing_tables)}/{len(tables_to_test)} tables found")
            print("Run the schema SQL in Supabase dashboard first")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def show_supabase_info():
    """Show Supabase configuration info"""
    load_dotenv()
    
    print("\n📊 Supabase Configuration")
    print("=" * 50)
    print(f"URL: {os.getenv('SUPABASE_URL')}")
    print(f"Service Key: {'Set' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'Missing'}")
    print(f"Anon Key: {'Set' if os.getenv('SUPABASE_ANON_KEY') else 'Missing'}")
    
    print("\n🔧 For Production Use:")
    print("1. Keep RLS enabled")
    print("2. Set up proper authentication in your app")
    print("3. RLS policies will secure your data")
    
    print("\n🧪 For Development/Testing:")
    print("1. Temporarily disable RLS on tables")
    print("2. Or create bypass policies for service role")
    print("3. Or use authenticated requests in tests")

if __name__ == "__main__":
    success = test_basic_connection()
    show_supabase_info()
    
    if success:
        print("\n✅ Supabase setup is working!")
        print("🎯 Next: Handle RLS for your use case")
    else:
        print("\n❌ Setup incomplete")
        print("🔧 Run the schema SQL first")