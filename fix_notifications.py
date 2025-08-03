#!/usr/bin/env python3
"""
Fix notifications system by updating database schema
"""

import sqlite3
from datetime import datetime

def fix_notifications_system():
    """Fix the notifications system by updating the database schema"""
    print("🔧 Fixing notifications system...")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Check current database version
        c.execute('PRAGMA user_version')
        db_version = c.fetchone()[0]
        print(f"Current database version: {db_version}")
        
        # Add missing columns to notifications table if they don't exist
        c.execute("PRAGMA table_info(notifications)")
        columns = [row[1] for row in c.fetchall()]
        
        missing_columns = []
        if 'status' not in columns:
            missing_columns.append('status')
        if 'scheduled_time' not in columns:
            missing_columns.append('scheduled_time')
        if 'notification_type' not in columns:
            missing_columns.append('notification_type')
        
        if missing_columns:
            print(f"Adding missing columns: {missing_columns}")
            for column in missing_columns:
                if column == 'status':
                    c.execute("ALTER TABLE notifications ADD COLUMN status TEXT DEFAULT 'active'")
                elif column == 'scheduled_time':
                    c.execute("ALTER TABLE notifications ADD COLUMN scheduled_time TEXT")
                elif column == 'notification_type':
                    c.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'general'")
        
        # Add missing columns to users table if they don't exist
        c.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in c.fetchall()]
        
        if 'mobile_no' not in user_columns:
            c.execute("ALTER TABLE users ADD COLUMN mobile_no TEXT")
            print("Added mobile_no column to users table")
        
        if 'email_address' not in user_columns:
            c.execute("ALTER TABLE users ADD COLUMN email_address TEXT")
            print("Added email_address column to users table")
        
        if 'banned' not in user_columns:
            c.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
            print("Added banned column to users table")
        
        # Update existing notifications to have proper status and notification_type
        c.execute("UPDATE notifications SET status = 'active' WHERE status IS NULL")
        c.execute("UPDATE notifications SET notification_type = 'general' WHERE notification_type IS NULL")
        c.execute("UPDATE notifications SET target_paid_status = 'all' WHERE target_paid_status IS NULL")
        
        # Update database version
        c.execute('PRAGMA user_version = 4')
        
        # Commit changes
        conn.commit()
        print("✅ Notifications system fixed successfully!")
        
        # Show current notifications
        c.execute("SELECT COUNT(*) FROM notifications")
        notification_count = c.fetchone()[0]
        print(f"Total notifications in database: {notification_count}")
        
        # Show recent notifications
        c.execute("""
            SELECT id, message, created_at, status, notification_type, target_paid_status 
            FROM notifications 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_notifications = c.fetchall()
        
        if recent_notifications:
            print("\n📋 Recent notifications:")
            for notif in recent_notifications:
                print(f"  ID: {notif[0]}, Message: {notif[1][:50]}..., Status: {notif[3]}, Type: {notif[4]}")
        else:
            print("\n📋 No notifications found in database")
        
    except Exception as e:
        print(f"❌ Error fixing notifications: {e}")
        conn.rollback()
    finally:
        conn.close()

def test_notification_system():
    """Test the notification system by creating a test notification"""
    print("\n🧪 Testing notification system...")
    
    try:
        from auth_handler import add_notification, get_unread_notifications_for_user, get_all_users
        
        # Get first user for testing
        users = get_all_users()
        if not users:
            print("❌ No users found in database")
            return
        
        test_user_id = users[0][0]  # First user's ID
        test_username = users[0][1]  # First user's username
        
        print(f"Testing with user: {test_username} (ID: {test_user_id})")
        
        # Create a test notification
        add_notification(
            message="🧪 Test notification - System is working!",
            class_id=1,  # Assuming class ID 1 exists
            target_paid_status='all',
            status='active',
            notification_type='test'
        )
        
        # Get unread notifications for the user
        notifications = get_unread_notifications_for_user(test_user_id)
        
        if notifications:
            print(f"✅ Test successful! Found {len(notifications)} unread notifications")
            for notif in notifications[:3]:  # Show first 3
                print(f"  - {notif[1]}")
        else:
            print("⚠️  No unread notifications found (this might be normal)")
        
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")

if __name__ == '__main__':
    print("🚀 Fixing Sunrise Education Centre Notifications System")
    print("=" * 60)
    
    fix_notifications_system()
    test_notification_system()
    
    print("\n" + "=" * 60)
    print("✅ Notification system fix completed!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test notifications by creating a live class or uploading resources")
    print("3. Check the notification bell icon in the top navigation") 