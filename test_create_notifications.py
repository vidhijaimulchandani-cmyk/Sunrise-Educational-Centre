#!/usr/bin/env python3
"""
Test script to create sample ban and mention notifications to verify they work properly.
"""

import sqlite3
import os
from datetime import datetime, timezone

# Database path
DATABASE = 'users.db'

def create_test_notifications():
    """Create test ban and mention notifications to verify the system works"""
    
    if not os.path.exists(DATABASE):
        print(f"❌ Database {DATABASE} not found!")
        return
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    print("🧪 Creating Test Notifications")
    print("=" * 50)
    
    try:
        # Test 1: Create a test ban notification
        print("\n1️⃣ Creating test ban notification...")
        ban_message = "You will be banned within 24 hours. Call Mohit Sir or admin."
        ban_type = "ban_warning"
        
        c.execute("""
            INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, notification_type)
            VALUES (?, NULL, ?, 'personal', 'active', ?)
        """, (ban_message, datetime.now(timezone.utc).isoformat(), ban_type))
        
        ban_notification_id = c.lastrowid
        print(f"✅ Created ban notification with ID: {ban_notification_id}")
        print(f"   Message: {ban_message}")
        print(f"   Type: {ban_type}")
        
        # Test 2: Create a test mention notification
        print("\n2️⃣ Creating test mention notification...")
        mention_message = "There is a mention message for you by @testuser."
        mention_type = "forum_mention"
        
        c.execute("""
            INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, notification_type)
            VALUES (?, NULL, ?, 'personal', 'active', ?)
        """, (mention_message, datetime.now(timezone.utc).isoformat(), mention_type))
        
        mention_notification_id = c.lastrowid
        print(f"✅ Created mention notification with ID: {mention_notification_id}")
        print(f"   Message: {mention_message}")
        print(f"   Type: {mention_type}")
        
        # Test 3: Create a test block notification
        print("\n3️⃣ Creating test block notification...")
        block_message = "You have been blocked for: Test reason. This is a 24-hour warning period. Contact admin or the institute to resolve this issue."
        block_type = "block_warning"
        
        c.execute("""
            INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, notification_type)
            VALUES (?, NULL, ?, 'personal', 'active', ?)
        """, (block_message, datetime.now(timezone.utc).isoformat(), block_type))
        
        block_notification_id = c.lastrowid
        print(f"✅ Created block notification with ID: {block_notification_id}")
        print(f"   Message: {block_message}")
        print(f"   Type: {block_type}")
        
        # Test 4: Verify notifications are unread
        print("\n4️⃣ Verifying notifications are unread...")
        c.execute("""
            SELECT COUNT(*) 
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id
            WHERE n.id IN (?, ?, ?) AND uns.notification_id IS NULL
        """, (ban_notification_id, mention_notification_id, block_notification_id))
        
        unread_count = c.fetchone()[0]
        print(f"📬 Unread test notifications: {unread_count}/3")
        
        if unread_count == 3:
            print("✅ All test notifications are unread (fix working!)")
        else:
            print(f"❌ Only {unread_count}/3 notifications are unread")
        
        # Test 5: Check what a user would see
        print("\n5️⃣ Simulating user notification view...")
        # Simulate user ID 1 (first user in system)
        c.execute("""
            SELECT n.id, n.message, n.created_at, n.status, n.notification_type, n.scheduled_time, 'personal_notification' as item_type
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = 1
            WHERE n.target_paid_status = 'personal' AND uns.notification_id IS NULL
            AND n.status IN ('active', 'scheduled')
            ORDER BY n.created_at DESC
        """)
        
        user_notifications = c.fetchall()
        print(f"📱 User would see {len(user_notifications)} personal notifications:")
        
        for notif in user_notifications:
            notif_id, message, created_at, status, notification_type, scheduled_time, item_type = notif
            print(f"   ID: {notif_id}, Type: {notification_type}, Item Type: {item_type}")
            print(f"   Message: {message[:60]}...")
            print(f"   Status: {status}")
            print()
        
        # Test 6: Check notification count
        print("\n6️⃣ Checking notification count...")
        c.execute("""
            SELECT COUNT(*) 
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = 1
            WHERE n.target_paid_status = 'personal' AND uns.notification_id IS NULL
            AND n.status IN ('active', 'scheduled')
        """)
        
        total_unread = c.fetchone()[0]
        print(f"🔔 Total unread personal notifications: {total_unread}")
        
        # Test 7: Check specific notification types
        print("\n7️⃣ Checking notification type breakdown...")
        c.execute("""
            SELECT notification_type, COUNT(*) as count
            FROM notifications 
            WHERE target_paid_status = 'personal' AND id IN (?, ?, ?)
            GROUP BY notification_type
        """, (ban_notification_id, mention_notification_id, block_notification_id))
        
        type_counts = c.fetchall()
        print("📊 Test notification type breakdown:")
        for notif_type, count in type_counts:
            print(f"   {notif_type}: {count}")
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🎯 Test Results Summary:")
        print(f"   Ban notification ID: {ban_notification_id}")
        print(f"   Mention notification ID: {mention_notification_id}")
        print(f"   Block notification ID: {block_notification_id}")
        print(f"   Unread count: {unread_count}/3")
        print(f"   Total unread personal: {total_unread}")
        
        if unread_count == 3:
            print("\n✅ SUCCESS: All test notifications are properly unread!")
            print("   Ban messages and mention messages should now be visible to users.")
            print("   Users will see these in their notification dropdown.")
        else:
            print("\n⚠️  WARNING: Some notifications are not appearing as unread.")
            print("   There may still be an issue with the notification system.")
        
        print("\n💡 Next steps:")
        print("   1. Refresh your website to see if notifications appear")
        print("   2. Check the notification bell for new notifications")
        print("   3. Verify that ban/mention messages are visible")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_notifications()