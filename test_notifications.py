#!/usr/bin/env python3
"""
Test script to verify notifications are working
"""

import sqlite3
from datetime import datetime

def test_notification_system():
    """Test the notification system"""
    print("🧪 Testing Notification System")
    print("=" * 40)
    
    try:
        from auth_handler import (
            add_notification, 
            get_unread_notifications_for_user, 
            get_all_users, 
            get_all_classes,
            mark_notification_as_seen
        )
        
        # Get test data
        users = get_all_users()
        classes = get_all_classes()
        
        if not users:
            print("❌ No users found in database")
            return
        
        if not classes:
            print("❌ No classes found in database")
            return
        
        test_user = users[0]  # First user
        test_class = classes[0]  # First class
        
        print(f"👤 Test User: {test_user[1]} (ID: {test_user[0]}, Class: {test_user[2]}, Paid: {test_user[3]})")
        print(f"📚 Test Class: {test_class[1]} (ID: {test_class[0]})")
        
        # Test 1: Create a general notification
        print("\n📝 Test 1: Creating general notification...")
        add_notification(
            message="🧪 Test notification - System is working!",
            class_id=test_class[0],
            target_paid_status='all',
            status='active',
            notification_type='test'
        )
        print("✅ General notification created")
        
        # Test 2: Create a paid-only notification
        print("\n📝 Test 2: Creating paid-only notification...")
        add_notification(
            message="💰 Premium content available for paid users!",
            class_id=test_class[0],
            target_paid_status='paid',
            status='active',
            notification_type='premium'
        )
        print("✅ Paid notification created")
        
        # Test 3: Create a personal notification
        print("\n📝 Test 3: Creating personal notification...")
        from auth_handler import add_personal_notification
        add_personal_notification(
            message="👋 Personal message for you!",
            user_id=test_user[0]
        )
        print("✅ Personal notification created")
        
        # Test 4: Get unread notifications for user
        print("\n📋 Test 4: Getting unread notifications...")
        notifications = get_unread_notifications_for_user(test_user[0])
        
        if notifications:
            print(f"✅ Found {len(notifications)} unread notifications:")
            for i, notif in enumerate(notifications, 1):
                print(f"  {i}. {notif[1]} (Type: {notif[4]}, Status: {notif[3]})")
        else:
            print("⚠️  No unread notifications found")
        
        # Test 5: Mark notification as seen
        if notifications:
            print(f"\n👁️  Test 5: Marking first notification as seen...")
            mark_notification_as_seen(test_user[0], notifications[0][0])
            print("✅ Notification marked as seen")
            
            # Check again
            remaining_notifications = get_unread_notifications_for_user(test_user[0])
            print(f"📊 Remaining unread notifications: {len(remaining_notifications)}")
        
        # Test 6: Check database directly
        print("\n🗄️  Test 6: Checking database directly...")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM notifications")
        total_notifications = c.fetchone()[0]
        print(f"📊 Total notifications in database: {total_notifications}")
        
        c.execute("SELECT COUNT(*) FROM user_notification_status")
        total_status_records = c.fetchone()[0]
        print(f"📊 Total notification status records: {total_status_records}")
        
        # Show recent notifications
        c.execute("""
            SELECT id, message, created_at, status, notification_type, target_paid_status 
            FROM notifications 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_notifications = c.fetchall()
        
        print("\n📋 Recent notifications in database:")
        for notif in recent_notifications:
            print(f"  ID: {notif[0]}, Message: {notif[1][:50]}..., Type: {notif[4]}, Status: {notif[3]}")
        
        conn.close()
        
        print("\n" + "=" * 40)
        print("✅ Notification system test completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Login as the test user")
        print("3. Check the notification bell icon")
        print("4. Click on the bell to see the dropdown")
        
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_notification_system() 