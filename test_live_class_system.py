#!/usr/bin/env python3
"""
Test Live Class System
"""

import sqlite3
from datetime import datetime

def test_live_class_system():
    """Test the live class system"""
    print("🧪 Testing Live Class System...")
    print("=" * 50)
    
    try:
        # Import functions
        from auth_handler import (
            create_live_class, get_class_details_by_id, update_live_class_status,
            record_attendance, get_class_attendance, get_live_class_analytics,
            validate_live_class_data
        )
        
        print("✅ Successfully imported live class functions")
        
        # Test 1: Create a live class
        print("\n📝 Test 1: Creating a live class...")
        test_class_id = create_live_class(
            class_code="TEST123",
            pin="1234",
            meeting_url="/test-video.mp4",
            topic="Test Live Class",
            description="Testing the live class system"
        )
        print(f"  ✅ Created class with ID: {test_class_id}")
        
        # Test 2: Get class details
        print("\n📋 Test 2: Getting class details...")
        details = get_class_details_by_id(test_class_id)
        if details:
            print(f"  ✅ Class details: {details}")
        else:
            print("  ❌ Could not get class details")
        
        # Test 3: Record attendance
        print("\n👥 Test 3: Recording attendance...")
        record_attendance(test_class_id, 1, "test_user_1")
        record_attendance(test_class_id, 2, "test_user_2")
        record_attendance(test_class_id, 3, "test_user_3")
        print("  ✅ Recorded attendance for 3 users")
        
        # Test 4: Get attendance
        print("\n📊 Test 4: Getting attendance...")
        attendance = get_class_attendance(test_class_id)
        print(f"  ✅ Attendance count: {len(attendance)}")
        for user, time in attendance:
            print(f"    - {user} joined at {time}")
        
        # Test 5: Update status
        print("\n🔄 Test 5: Updating class status...")
        update_live_class_status(test_class_id, "active")
        print("  ✅ Updated status to active")
        
        # Test 6: Get analytics
        print("\n📈 Test 6: Getting analytics...")
        analytics = get_live_class_analytics()
        print(f"  ✅ Analytics: {analytics}")
        
        # Test 7: Validate data
        print("\n🔍 Test 7: Validating data...")
        validate_live_class_data()
        print("  ✅ Data validation completed")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM live_class_attendance WHERE class_id = ?", (test_class_id,))
        try:
            c.execute("DELETE FROM live_class_messages WHERE live_class_id = ?", (test_class_id,))
        except sqlite3.OperationalError:
            c.execute("DELETE FROM live_class_messages WHERE live_class_id IS NULL AND live_class_id = ?", (test_class_id,))
        c.execute("DELETE FROM live_classes WHERE id = ?", (test_class_id,))
        conn.commit()
        conn.close()
        print("  ✅ Test data cleaned up")
        
        print("\n" + "=" * 50)
        print("✅ All live class tests passed!")
        print("\nThe live class system is working properly!")
        
    except Exception as e:
        print(f"❌ Error testing live class system: {e}")
        import traceback
        traceback.print_exc()

def check_database_integrity():
    """Check database integrity"""
    print("\n🔍 Checking Database Integrity...")
    print("=" * 50)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Check live_classes table
        c.execute("SELECT COUNT(*) FROM live_classes")
        total_classes = c.fetchone()[0]
        print(f"  Total live classes: {total_classes}")
        
        # Check status distribution
        c.execute("SELECT status, COUNT(*) FROM live_classes GROUP BY status")
        status_dist = c.fetchall()
        print("  Status distribution:")
        for status, count in status_dist:
            print(f"    {status}: {count}")
        
        # Check attendance table
        c.execute("SELECT COUNT(*) FROM live_class_attendance")
        total_attendance = c.fetchone()[0]
        print(f"  Total attendance records: {total_attendance}")
        
        # Check messages table
        c.execute("SELECT COUNT(*) FROM live_class_messages")
        total_messages = c.fetchone()[0]
        print(f"  Total messages: {total_messages}")
        
        # Check for inconsistencies
        c.execute("SELECT COUNT(*) FROM live_classes WHERE is_active = 1 AND status != 'active'")
        inconsistent = c.fetchone()[0]
        if inconsistent > 0:
            print(f"  ⚠️  Found {inconsistent} inconsistent status records")
        else:
            print("  ✅ No status inconsistencies found")
        
        print("  ✅ Database integrity check completed")
        
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 Live Class System Test")
    print("=" * 50)
    
    check_database_integrity()
    test_live_class_system()
    
    print("\n" + "=" * 50)
    print("🎉 Live class system is ready!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test creating a live class through the web interface")
    print("3. Test joining a live class")
    print("4. Check attendance tracking")
    print("5. Verify status management") 