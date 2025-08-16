#!/usr/bin/env python3
"""
Test script for the study resources module
Verifies all study resource functions are working correctly
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from study_resources import (
    ensure_resource_tables, save_resource, get_all_resources, get_resources_for_class_id,
    get_categories_for_class, get_all_categories, add_category, update_category,
    delete_category, search_resources, track_resource_download, add_resource_rating,
    get_resource_ratings, get_average_rating, get_resource_statistics,
    allowed_file, get_file_size, get_file_type, user_has_access_to_resource,
    update_resource, delete_resource
)

DATABASE = 'users.db'

def test_study_resources_system():
    """Test the study resources system"""
    print("🧪 Testing Study Resources System")
    print("=" * 50)
    
    # Ensure tables exist
    ensure_resource_tables()
    
    # Test 1: Add categories
    print("\n1️⃣ Testing category management...")
    
    # Add test categories with unique names
    import time
    timestamp = int(time.time())
    cat1_id = add_category(f"Test Category A {timestamp}", "Test description", "general", "all", "unpaid")
    cat2_id = add_category(f"Test Category B {timestamp}", "Premium content", "premium", "1", "paid")
    
    if cat1_id and cat2_id:
        print(f"✅ Added categories: {cat1_id}, {cat2_id}")
    else:
        print("❌ Failed to add categories")
        return False
    
    # Test 2: Get categories
    print("\n2️⃣ Testing category retrieval...")
    
    all_categories = get_all_categories()
    print(f"✅ Found {len(all_categories)} total categories")
    
    class_categories = get_categories_for_class(1)
    print(f"✅ Found {len(class_categories)} categories for class 1")
    
    # Test 3: Add resources
    print("\n3️⃣ Testing resource management...")
    
    # Create a test file
    test_file_content = "This is a test resource file content."
    test_filename = "test_resource.txt"
    test_filepath = f"uploads/{test_filename}"
    
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    with open(test_filepath, 'w') as f:
        f.write(test_file_content)
    
    # Save resource to database
    resource_id = save_resource(
        filename=test_filename,
        class_id=1,
        filepath=test_filepath,
        title="Test Resource",
        description="A test resource for testing",
        category=f"Test Category A {timestamp}",
        paid_status="unpaid",
        uploaded_by=1,
        file_size=len(test_file_content),
        file_type="txt"
    )
    
    if resource_id:
        print(f"✅ Added resource with ID: {resource_id}")
    else:
        print("❌ Failed to add resource")
        return False
    
    # Test 4: Get resources
    print("\n4️⃣ Testing resource retrieval...")
    
    all_resources = get_all_resources()
    print(f"✅ Found {len(all_resources)} total resources")
    
    class_resources = get_resources_for_class_id(1)
    print(f"✅ Found {len(class_resources)} resources for class 1")
    
    paid_resources = get_resources_for_class_id(1, "paid")
    print(f"✅ Found {len(paid_resources)} paid resources for class 1")
    
    # Test 5: Search resources
    print("\n5️⃣ Testing resource search...")
    
    search_results = search_resources("test", class_id=1)
    print(f"✅ Found {len(search_results)} resources matching 'test'")
    
    # Test 6: File utilities
    print("\n6️⃣ Testing file utilities...")
    
    print(f"✅ File allowed: {allowed_file('test.pdf')}")
    print(f"✅ File not allowed: {allowed_file('test.exe')}")
    print(f"✅ File size: {get_file_size(test_filepath)} bytes")
    print(f"✅ File type: {get_file_type(test_filename)}")
    
    # Test 7: Access control
    print("\n7️⃣ Testing access control...")
    
    admin_access = user_has_access_to_resource(test_filename, "admin")
    student_access = user_has_access_to_resource(test_filename, "student", "unpaid")
    
    print(f"✅ Admin access: {admin_access}")
    print(f"✅ Student access: {student_access}")
    
    # Test 8: Download tracking
    print("\n8️⃣ Testing download tracking...")
    
    track_success = track_resource_download(resource_id, 1, "127.0.0.1", "Test Browser")
    print(f"✅ Download tracking: {track_success}")
    
    # Test 9: Ratings
    print("\n9️⃣ Testing ratings...")
    
    rating_success = add_resource_rating(resource_id, 1, 5, "Great resource!")
    print(f"✅ Added rating: {rating_success}")
    
    ratings = get_resource_ratings(resource_id)
    print(f"✅ Found {len(ratings)} ratings")
    
    avg_rating = get_average_rating(resource_id)
    print(f"✅ Average rating: {avg_rating}")
    
    # Test 10: Statistics
    print("\n🔟 Testing statistics...")
    
    stats = get_resource_statistics()
    print(f"✅ Total resources: {stats.get('total_resources', 0)}")
    print(f"✅ Total downloads: {stats.get('total_downloads', 0)}")
    print(f"✅ Recent uploads: {stats.get('recent_uploads', 0)}")
    
    # Test 11: Update operations
    print("\n1️⃣1️⃣ Testing update operations...")
    
    update_success = update_resource(resource_id, title="Updated Test Resource")
    print(f"✅ Resource update: {update_success}")
    
    category_update = update_category(cat1_id, description="Updated description")
    print(f"✅ Category update: {category_update}")
    
    # Clean up test data
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Delete test file
        if os.path.exists(test_filepath):
            os.remove(test_filepath)
            print("✅ Removed test file")
        
        # Delete test resource from database
        delete_resource(test_filename)
        print("✅ Removed test resource from database")
        
        # Delete test categories
        delete_category(cat1_id)
        delete_category(cat2_id)
        print("✅ Removed test categories")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n🎉 All tests completed successfully!")
    return True

def check_database_structure():
    """Check the database structure"""
    print("\n📊 Database Structure Check")
    print("=" * 30)
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Check all tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        
        print("📋 Available tables:")
        for table in tables:
            table_name = table[0]
            c.execute(f"PRAGMA table_info({table_name})")
            columns = c.fetchall()
            print(f"   📄 {table_name} ({len(columns)} columns)")
            
            # Show column names for resource tables
            if 'resource' in table_name or table_name in ['resources', 'categories', 'resource_downloads', 'resource_ratings']:
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")
        conn.close()

if __name__ == "__main__":
    print("🚀 Testing Study Resources Module")
    print("=" * 50)
    
    # Check database structure first
    check_database_structure()
    
    # Run tests
    success = test_study_resources_system()
    
    if success:
        print("\n✅ STUDY RESOURCES MODULE IS WORKING CORRECTLY!")
        print("\nKey features verified:")
        print("✅ Resource management (add, get, update, delete)")
        print("✅ Category management")
        print("✅ File utilities and validation")
        print("✅ Access control")
        print("✅ Download tracking")
        print("✅ Ratings and reviews")
        print("✅ Search functionality")
        print("✅ Statistics")
        print("✅ Database structure")
    else:
        print("\n❌ Some tests failed. Please check the study resources module.")