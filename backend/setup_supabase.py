#!/usr/bin/env python3
"""
Setup Supabase schema automatically
"""

import os
from dotenv import load_dotenv
from database.supabase_client import get_supabase_client

def setup_supabase_schema():
    """Setup Supabase schema by reading SQL file"""
    load_dotenv()
    
    print("🔄 Setting up Supabase schema...")
    
    # Check credentials
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("❌ Supabase credentials not found in .env")
        return False
    
    try:
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), "database", "supabase_schema.sql")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("✅ Schema file loaded")
        
        # Get Supabase client
        client = get_supabase_client()
        
        # Execute schema (Note: This might not work due to RLS/auth.uid() functions)
        # It's better to run this manually in Supabase dashboard
        print("\n📝 Schema SQL:")
        print("=" * 50)
        print(schema_sql[:500] + "..." if len(schema_sql) > 500 else schema_sql)
        print("=" * 50)
        
        print("\n⚠️  Manual Setup Required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy the contents of 'database/supabase_schema.sql'")
        print("4. Paste and execute in Supabase SQL Editor")
        print("5. Run 'python test_supabase_full.py' to test")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_supabase_schema()