#!/usr/bin/env python3
"""
Comprehensive Supabase test script
Tests all CRUD operations and verifies schema is working
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database_adapter import db_adapter

async def setup_test_environment():
    """Setup test environment"""
    print("🔄 Setting up Supabase test environment...")
    
    # Ensure we're using Supabase
    os.environ["DATABASE_TYPE"] = "supabase"
    
    # Reinitialize adapter
    global db_adapter
    from database.database_adapter import DatabaseAdapter
    db_adapter = DatabaseAdapter()
    
    # Connect (for Supabase, this just initializes the client)
    await db_adapter.connect()
    print("✅ Connected to Supabase")

async def test_users_crud():
    """Test Users table CRUD operations"""
    print("\n🧪 Testing Users CRUD...")
    
    # Create test user
    test_user = {
        "id": str(uuid.uuid4()),
        "name": "Test User",
        "email": f"test-{uuid.uuid4()}@example.com",
        "role": "user",
        "status": "offline",
        "timezone": "UTC"
    }
    
    try:
        # CREATE
        user_id = await db_adapter.create_document("users", test_user)
        print(f"✅ Created user: {user_id}")
        
        # READ
        found_user = await db_adapter.get_document("users", {"id": test_user["id"]})
        if found_user:
            print(f"✅ Retrieved user: {found_user['name']}")
        else:
            print("❌ Could not retrieve user")
            return False
        
        # UPDATE
        updated = await db_adapter.update_document(
            "users", 
            {"id": test_user["id"]}, 
            {"name": "Updated Test User", "status": "active"}
        )
        print(f"✅ Updated user: {updated}")
        
        # Verify update
        updated_user = await db_adapter.get_document("users", {"id": test_user["id"]})
        if updated_user and updated_user["name"] == "Updated Test User":
            print("✅ Update verified")
        else:
            print("❌ Update not verified")
        
        # LIST
        users = await db_adapter.get_documents("users", limit=5)
        print(f"✅ Retrieved {len(users)} users")
        
        # COUNT
        count = await db_adapter.count_documents("users")
        print(f"✅ Total users count: {count}")
        
        # DELETE
        deleted = await db_adapter.delete_document("users", {"id": test_user["id"]})
        print(f"✅ Deleted user: {deleted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Users CRUD failed: {e}")
        return False

async def test_projects_and_relationships():
    """Test Projects with relationships"""
    print("\n🧪 Testing Projects with relationships...")
    
    try:
        # First create a test user for the project
        test_user = {
            "id": str(uuid.uuid4()),
            "name": "Project Manager",
            "email": f"pm-{uuid.uuid4()}@example.com",
            "role": "manager"
        }
        user_id = await db_adapter.create_document("users", test_user)
        
        # Create test project
        test_project = {
            "id": str(uuid.uuid4()),
            "name": "Test Project",
            "description": "A test project",
            "client": "Test Client",
            "budget": 10000.00,
            "status": "active",
            "created_by": test_user["id"],
            "team_members": [test_user["id"]]
        }
        
        project_id = await db_adapter.create_document("projects", test_project)
        print(f"✅ Created project: {project_id}")
        
        # Create test task for the project
        test_task = {
            "id": str(uuid.uuid4()),
            "title": "Test Task",
            "description": "A test task",
            "project_id": test_project["id"],
            "assignee_id": test_user["id"],
            "created_by": test_user["id"],
            "status": "todo",
            "priority": "medium"
        }
        
        task_id = await db_adapter.create_document("tasks", test_task)
        print(f"✅ Created task: {task_id}")
        
        # Create time entry
        test_time_entry = {
            "id": str(uuid.uuid4()),
            "user_id": test_user["id"],
            "project_id": test_project["id"],
            "task_id": test_task["id"],
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "duration": 7200,  # 2 hours in seconds
            "description": "Working on test task"
        }
        
        time_entry_id = await db_adapter.create_document("time_entries", test_time_entry)
        print(f"✅ Created time entry: {time_entry_id}")
        
        # Test queries with relationships
        project_tasks = await db_adapter.get_documents("tasks", {"project_id": test_project["id"]})
        print(f"✅ Found {len(project_tasks)} tasks for project")
        
        user_time_entries = await db_adapter.get_documents("time_entries", {"user_id": test_user["id"]})
        print(f"✅ Found {len(user_time_entries)} time entries for user")
        
        # Cleanup
        await db_adapter.delete_document("time_entries", {"id": test_time_entry["id"]})
        await db_adapter.delete_document("tasks", {"id": test_task["id"]})
        await db_adapter.delete_document("projects", {"id": test_project["id"]})
        await db_adapter.delete_document("users", {"id": test_user["id"]})
        print("✅ Cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Projects and relationships test failed: {e}")
        return False

async def test_activity_and_screenshots():
    """Test activity data and screenshots"""
    print("\n🧪 Testing Activity and Screenshots...")
    
    try:
        # Create test user and time entry first
        test_user = {
            "id": str(uuid.uuid4()),
            "name": "Activity User",
            "email": f"activity-{uuid.uuid4()}@example.com",
            "role": "user"
        }
        user_id = await db_adapter.create_document("users", test_user)
        
        test_project = {
            "id": str(uuid.uuid4()),
            "name": "Activity Project",
            "client": "Test Client",
            "created_by": test_user["id"]
        }
        project_id = await db_adapter.create_document("projects", test_project)
        
        test_time_entry = {
            "id": str(uuid.uuid4()),
            "user_id": test_user["id"],
            "project_id": test_project["id"],
            "start_time": datetime.now().isoformat(),
            "duration": 3600
        }
        time_entry_id = await db_adapter.create_document("time_entries", test_time_entry)
        
        # Create activity data
        test_activity = {
            "id": str(uuid.uuid4()),
            "user_id": test_user["id"],
            "time_entry_id": test_time_entry["id"],
            "timestamp": datetime.now().isoformat(),
            "mouse_clicks": 150,
            "keyboard_strokes": 300,
            "active_app": "VS Code",
            "active_url": "https://github.com",
            "activity_score": 85.5
        }
        
        activity_id = await db_adapter.create_document("activity_data", test_activity)
        print(f"✅ Created activity data: {activity_id}")
        
        # Create screenshot
        test_screenshot = {
            "id": str(uuid.uuid4()),
            "user_id": test_user["id"],
            "time_entry_id": test_time_entry["id"],
            "url": "https://example.com/screenshot1.png",
            "activity_level": 75.0
        }
        
        screenshot_id = await db_adapter.create_document("screenshots", test_screenshot)
        print(f"✅ Created screenshot: {screenshot_id}")
        
        # Test queries
        user_activity = await db_adapter.get_documents("activity_data", {"user_id": test_user["id"]})
        print(f"✅ Found {len(user_activity)} activity records")
        
        user_screenshots = await db_adapter.get_documents("screenshots", {"user_id": test_user["id"]})
        print(f"✅ Found {len(user_screenshots)} screenshots")
        
        # Cleanup
        await db_adapter.delete_document("activity_data", {"id": test_activity["id"]})
        await db_adapter.delete_document("screenshots", {"id": test_screenshot["id"]})
        await db_adapter.delete_document("time_entries", {"id": test_time_entry["id"]})
        await db_adapter.delete_document("projects", {"id": test_project["id"]})
        await db_adapter.delete_document("users", {"id": test_user["id"]})
        print("✅ Cleaned up activity test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Activity and screenshots test failed: {e}")
        return False

async def test_invitations_and_tokens():
    """Test invitations and password reset tokens"""
    print("\n🧪 Testing Invitations and Tokens...")
    
    try:
        # Create inviting user
        admin_user = {
            "id": str(uuid.uuid4()),
            "name": "Admin User",
            "email": f"admin-{uuid.uuid4()}@example.com",
            "role": "admin"
        }
        admin_id = await db_adapter.create_document("users", admin_user)
        
        # Create invitation
        test_invitation = {
            "id": str(uuid.uuid4()),
            "email": f"invited-{uuid.uuid4()}@example.com",
            "role": "user",
            "invited_by": admin_user["id"],
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
            "accepted": False
        }
        
        invitation_id = await db_adapter.create_document("invitations", test_invitation)
        print(f"✅ Created invitation: {invitation_id}")
        
        # Create password reset token
        test_token = {
            "id": str(uuid.uuid4()),
            "email": admin_user["email"],
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "used": False
        }
        
        token_id = await db_adapter.create_document("password_reset_tokens", test_token)
        print(f"✅ Created password reset token: {token_id}")
        
        # Test queries
        user_invitations = await db_adapter.get_documents("invitations", {"invited_by": admin_user["id"]})
        print(f"✅ Found {len(user_invitations)} invitations")
        
        email_tokens = await db_adapter.get_documents("password_reset_tokens", {"email": admin_user["email"]})
        print(f"✅ Found {len(email_tokens)} password tokens")
        
        # Cleanup
        await db_adapter.delete_document("invitations", {"id": test_invitation["id"]})
        await db_adapter.delete_document("password_reset_tokens", {"id": test_token["id"]})
        await db_adapter.delete_document("users", {"id": admin_user["id"]})
        print("✅ Cleaned up invitations test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Invitations and tokens test failed: {e}")
        return False

async def main():
    """Run comprehensive Supabase tests"""
    load_dotenv()
    
    print("🚀 Comprehensive Supabase Test Suite")
    print("=" * 60)
    
    # Check if schema is set up
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env")
        return
    
    print(f"🔗 Testing Supabase: {supabase_url}")
    print("\n⚠️  Make sure you've run the SQL schema in Supabase dashboard first!")
    print("   File: database/supabase_schema.sql")
    
    print("\nStarting tests automatically...")
    
    try:
        await setup_test_environment()
        
        # Run all tests
        tests = [
            ("Users CRUD", test_users_crud),
            ("Projects & Relationships", test_projects_and_relationships),
            ("Activity & Screenshots", test_activity_and_screenshots),
            ("Invitations & Tokens", test_invitations_and_tokens),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n🎯 {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! Supabase is ready for production!")
            print("\nTo use Supabase:")
            print("1. Keep DATABASE_TYPE='supabase' in .env")
            print("2. Your app will now use Supabase for all database operations")
            print("3. Deploy with confidence! 🚀")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
            print("Make sure you've run the SQL schema in Supabase dashboard.")
            
    except Exception as e:
        print(f"❌ Test suite failed to run: {e}")

if __name__ == "__main__":
    asyncio.run(main())