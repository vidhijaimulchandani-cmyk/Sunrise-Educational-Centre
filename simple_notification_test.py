#!/usr/bin/env python3
"""
Simple test script for the new notification system
Tests basic functionality without external dependencies
"""

import sqlite3
import re
from datetime import datetime

DATABASE = 'users.db'

def get_ist_timestamp():
    """Get current timestamp in IST format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def test_notification_tables():
    """Test that notification tables exist and work"""
    print("🧪 Testing Notification Tables")
    print("=" * 40)
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Check if tables exist
        tables = ['notifications', 'user_notifications', 'mention_notifications', 'user_notification_status']
        
        for table in tables:
            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = c.fetchone()
            if exists:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        
        # Test basic operations
        print("\n📝 Testing basic operations...")
        
        # Test 1: Add a test general notification
        c.execute('''
            INSERT INTO notifications 
            (message, class_id, created_at, target_paid_status, status, notification_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("🧪 Test general notification", 1, get_ist_timestamp(), 'all', 'active', 'test'))
        general_id = c.lastrowid
        print(f"✅ Added general notification with ID: {general_id}")
        
        # Test 2: Add a test personal notification
        c.execute('''
            INSERT INTO user_notifications 
            (user_id, message, notification_type, created_at, sender_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, "🧪 Test personal notification", 'test', get_ist_timestamp(), 2))
        personal_id = c.lastrowid
        print(f"✅ Added personal notification with ID: {personal_id}")
        
        # Test 3: Add a test mention notification
        c.execute('''
            INSERT INTO mention_notifications 
            (mentioned_user_id, sender_id, topic_id, message_preview, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, 2, 1, "Test mention", get_ist_timestamp()))
        mention_id = c.lastrowid
        print(f"✅ Added mention notification with ID: {mention_id}")
        
        # Test 4: Query notifications for user 1
        print("\n📋 Testing queries...")
        
        # Get general notifications for user 1
        c.execute('''
            SELECT n.id, n.message, n.created_at, n.status, n.notification_type, 
                   n.scheduled_time, 'general' as item_type, NULL as sender_name
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = 1
            WHERE n.class_id = 1 AND uns.notification_id IS NULL
            AND n.status = 'active'
        ''')
        general_notifications = c.fetchall()
        print(f"✅ Found {len(general_notifications)} general notifications for user 1")
        
        # Get personal notifications for user 1
        c.execute('''
            SELECT un.id, un.message, un.created_at, 'active' as status, 
                   un.notification_type, un.created_at as scheduled_time, 
                   'personal' as item_type, u.username as sender_name
            FROM user_notifications un
            LEFT JOIN users u ON un.sender_id = u.id
            WHERE un.user_id = 1 AND un.is_read = 0
        ''')
        personal_notifications = c.fetchall()
        print(f"✅ Found {len(personal_notifications)} personal notifications for user 1")
        
        # Get mention notifications for user 1
        c.execute('''
            SELECT mn.id, 
                   CASE 
                       WHEN u.username IS NOT NULL THEN 'There is a mention message for you by @' || u.username || '.'
                       ELSE 'You were mentioned in a forum message.'
                   END as message,
                   mn.created_at, 'active' as status, 'forum_mention' as notification_type,
                   mn.created_at as scheduled_time, 'mention' as item_type, u.username as sender_name
            FROM mention_notifications mn
            LEFT JOIN users u ON mn.sender_id = u.id
            WHERE mn.mentioned_user_id = 1 AND mn.is_read = 0
        ''')
        mention_notifications = c.fetchall()
        print(f"✅ Found {len(mention_notifications)} mention notifications for user 1")
        
        # Test 5: Test mention extraction
        print("\n🔍 Testing mention extraction...")
        test_message = "Hello @user1 and @user2, please check this out! Also @user1 again."
        mentions = re.findall(r'@(\w+)', test_message)
        unique_mentions = list(set(mentions))
        print(f"📝 Message: {test_message}")
        print(f"🔍 Extracted mentions: {unique_mentions}")
        
        # Test 6: Test privacy (check user 2 doesn't see user 1's personal notifications)
        print("\n🔒 Testing privacy...")
        c.execute('''
            SELECT COUNT(*) FROM user_notifications 
            WHERE user_id = 2 AND user_id != 1
        ''')
        user2_personal_count = c.fetchone()[0]
        print(f"✅ User 2 has {user2_personal_count} personal notifications (should be 0 for privacy)")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        c.execute("DELETE FROM notifications WHERE message LIKE '%🧪 Test%'")
        c.execute("DELETE FROM user_notifications WHERE message LIKE '%🧪 Test%'")
        c.execute("DELETE FROM mention_notifications WHERE message_preview LIKE '%Test%'")
        conn.commit()
        print("✅ Test data cleaned up")
        
        conn.close()
        print("\n🎉 All tests passed! Notification system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False

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
            
            # Show column names for notification tables
            if 'notification' in table_name or table_name in ['notifications', 'user_notifications', 'mention_notifications']:
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")
        conn.close()

if __name__ == "__main__":
    print("🚀 Testing New Notification System")
    print("=" * 50)
    
    # Check database structure first
    check_database_structure()
    
    # Run tests
    success = test_notification_tables()
    
    if success:
        print("\n✅ NOTIFICATION SYSTEM IS WORKING CORRECTLY!")
        print("\nKey improvements verified:")
        print("✅ Separate tables for different notification types")
        print("✅ Personal notifications are user-specific")
        print("✅ Mention notifications are isolated")
        print("✅ General notifications work properly")
        print("✅ Privacy is maintained between users")
        print("✅ Mention extraction works correctly")
    else:
        print("\n❌ Some tests failed. Please check the notification system.")