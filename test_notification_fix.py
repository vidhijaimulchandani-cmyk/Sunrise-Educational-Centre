#!/usr/bin/env python3
"""
Test script to verify that ban messages and mention messages now appear as unread notifications
after fixing the add_personal_notification function.
"""

import sqlite3
import os
from datetime import datetime, timezone

# Database path
DATABASE = 'users.db'

def test_notification_system():
    """Test the notification system to ensure ban and mention messages work properly"""
    
    if not os.path.exists(DATABASE):
        print(f"❌ Database {DATABASE} not found!")
        return
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    print("🧪 Testing Notification System Fix")
    print("=" * 50)
    
    try:
        # Test 1: Check if notifications table exists and has correct structure
        print("\n1️⃣ Checking notifications table structure...")
        c.execute("PRAGMA table_info(notifications)")
        columns = [row[1] for row in c.fetchall()]
        required_columns = ['id', 'message', 'class_id', 'created_at', 'target_paid_status', 'status', 'notification_type']
        
        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
        else:
            print("✅ All required columns exist")
        
        # Test 2: Check if user_notification_status table exists
        print("\n2️⃣ Checking user_notification_status table...")
        c.execute("PRAGMA table_info(user_notification_status)")
        status_columns = [row[1] for row in c.fetchall()]
        if status_columns:
            print("✅ user_notification_status table exists")
        else:
            print("❌ user_notification_status table missing")
        
        # Test 3: Check existing notifications
        print("\n3️⃣ Checking existing notifications...")
        c.execute("SELECT COUNT(*) FROM notifications")
        total_notifications = c.fetchone()[0]
        print(f"📊 Total notifications: {total_notifications}")
        
        # Test 4: Check personal notifications specifically
        print("\n4️⃣ Checking personal notifications...")
        c.execute("""
            SELECT id, message, created_at, target_paid_status, notification_type, status
            FROM notifications 
            WHERE target_paid_status = 'personal'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        personal_notifications = c.fetchall()
        
        if personal_notifications:
            print(f"📱 Found {len(personal_notifications)} personal notifications:")
            for notif in personal_notifications:
                notif_id, message, created_at, target_paid_status, notification_type, status = notif
                print(f"   ID: {notif_id}, Type: {notification_type}, Status: {status}")
                print(f"   Message: {message[:50]}...")
                print(f"   Created: {created_at}")
                print()
        else:
            print("📱 No personal notifications found")
        
        # Test 5: Check if any personal notifications are marked as seen
        print("\n5️⃣ Checking personal notification status...")
        c.execute("""
            SELECT COUNT(*) 
            FROM notifications n
            JOIN user_notification_status uns ON n.id = uns.notification_id
            WHERE n.target_paid_status = 'personal'
        """)
        seen_personal = c.fetchone()[0]
        print(f"👁️  Personal notifications marked as seen: {seen_personal}")
        
        # Test 6: Check unread personal notifications
        print("\n6️⃣ Checking unread personal notifications...")
        c.execute("""
            SELECT COUNT(*) 
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = 1
            WHERE n.target_paid_status = 'personal' 
            AND uns.notification_id IS NULL
            AND n.status IN ('active', 'scheduled')
        """)
        unread_personal = c.fetchone()[0]
        print(f"📬 Unread personal notifications: {unread_personal}")
        
        # Test 7: Check specific notification types
        print("\n7️⃣ Checking specific notification types...")
        c.execute("""
            SELECT notification_type, COUNT(*) as count
            FROM notifications 
            WHERE target_paid_status = 'personal'
            GROUP BY notification_type
        """)
        type_counts = c.fetchall()
        
        if type_counts:
            print("📊 Notification type breakdown:")
            for notif_type, count in type_counts:
                print(f"   {notif_type}: {count}")
        else:
            print("📊 No personal notifications found")
        
        # Test 8: Check for ban-related notifications
        print("\n8️⃣ Checking for ban-related notifications...")
        c.execute("""
            SELECT id, message, created_at, notification_type
            FROM notifications 
            WHERE target_paid_status = 'personal' 
            AND (message LIKE '%ban%' OR message LIKE '%block%' OR message LIKE '%warning%')
            ORDER BY created_at DESC
            LIMIT 3
        """)
        ban_notifications = c.fetchall()
        
        if ban_notifications:
            print(f"🚫 Found {len(ban_notifications)} ban/block notifications:")
            for notif in ban_notifications:
                notif_id, message, created_at, notification_type = notif
                print(f"   ID: {notif_id}, Type: {notification_type}")
                print(f"   Message: {message}")
                print(f"   Created: {created_at}")
                print()
        else:
            print("🚫 No ban/block notifications found")
        
        # Test 9: Check for mention notifications
        print("\n9️⃣ Checking for mention notifications...")
        c.execute("""
            SELECT id, message, created_at, notification_type
            FROM notifications 
            WHERE target_paid_status = 'personal' 
            AND (message LIKE '%mention%' OR notification_type = 'forum_mention')
            ORDER BY created_at DESC
            LIMIT 3
        """)
        mention_notifications = c.fetchall()
        
        if mention_notifications:
            print(f"💬 Found {len(mention_notifications)} mention notifications:")
            for notif in mention_notifications:
                notif_id, message, created_at, notification_type = notif
                print(f"   ID: {notif_id}, Type: {notification_type}")
                print(f"   Message: {message}")
                print(f"   Created: {created_at}")
                print()
        else:
            print("💬 No mention notifications found")
        
        # Test 10: Simulate creating a test notification
        print("\n🔟 Testing notification creation...")
        test_message = "TEST: This is a test ban notification to verify the fix works"
        test_type = "test_ban"
        
        # Insert test notification
        c.execute("""
            INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, notification_type)
            VALUES (?, NULL, ?, 'personal', 'active', ?)
        """, (test_message, datetime.now(timezone.utc).isoformat(), test_type))
        
        test_notification_id = c.lastrowid
        print(f"✅ Created test notification with ID: {test_notification_id}")
        
        # Check if it appears as unread
        c.execute("""
            SELECT COUNT(*) 
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id
            WHERE n.id = ? AND uns.notification_id IS NULL
        """, (test_notification_id,))
        
        is_unread = c.fetchone()[0]
        if is_unread:
            print("✅ Test notification appears as unread (fix working!)")
        else:
            print("❌ Test notification is marked as read (fix not working)")
        
        # Clean up test notification
        c.execute("DELETE FROM notifications WHERE id = ?", (test_notification_id,))
        print("🧹 Cleaned up test notification")
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🎯 Test Summary:")
        print(f"   Total notifications: {total_notifications}")
        print(f"   Personal notifications: {len(personal_notifications)}")
        print(f"   Unread personal: {unread_personal}")
        print(f"   Ban/block notifications: {len(ban_notifications)}")
        print(f"   Mention notifications: {len(mention_notifications)}")
        
        if unread_personal > 0:
            print("\n✅ SUCCESS: Personal notifications are now appearing as unread!")
            print("   Ban messages and mention messages should now be visible to users.")
        else:
            print("\n⚠️  WARNING: No unread personal notifications found.")
            print("   This might mean no notifications exist yet, or there's still an issue.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_notification_system()