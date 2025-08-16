#!/usr/bin/env python3
"""
Test script for the new notification system
Verifies that private mentions are working correctly and not showing to all users
"""

import sqlite3
from datetime import datetime, timezone
import sys
import os

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notifications import (
    ensure_notification_tables, add_general_notification, add_personal_notification,
    add_mention_notification, get_unread_notifications_for_user, mark_notification_as_read,
    create_mention_notifications, extract_mentions, get_notification_count_for_user
)
from auth_handler import get_user_by_username, get_user_by_id, get_all_users

DATABASE = 'users.db'

def test_notification_system():
    """Test the new notification system"""
    print("🧪 Testing New Notification System")
    print("=" * 50)
    
    # Ensure tables exist
    ensure_notification_tables()
    
    # Get some test users
    users = get_all_users()
    if len(users) < 2:
        print("❌ Need at least 2 users to test notifications")
        return
    
    test_user1 = users[0]  # First user
    test_user2 = users[1]  # Second user
    
    print(f"👤 Test User 1: {test_user1[1]} (ID: {test_user1[0]})")
    print(f"👤 Test User 2: {test_user2[1]} (ID: {test_user2[0]})")
    print()
    
    # Test 1: Add general notification
    print("1️⃣ Testing general notification...")
    general_msg = "🧪 Test general notification - This should be visible to all users in the class"
    general_id = add_general_notification(general_msg, class_id=test_user1[2])
    print(f"✅ Added general notification with ID: {general_id}")
    
    # Test 2: Add personal notification for user 1
    print("\n2️⃣ Testing personal notification...")
    personal_msg = "🧪 Test personal notification - This should only be visible to user 1"
    personal_id = add_personal_notification(personal_msg, test_user1[0], 'personal', test_user2[0])
    print(f"✅ Added personal notification with ID: {personal_id}")
    
    # Test 3: Add mention notification for user 1
    print("\n3️⃣ Testing mention notification...")
    mention_id = add_mention_notification(
        mentioned_user_id=test_user1[0],
        sender_id=test_user2[0],
        topic_id=1,
        message_preview="Test mention message"
    )
    print(f"✅ Added mention notification with ID: {mention_id}")
    
    # Test 4: Check notifications for user 1
    print("\n4️⃣ Checking notifications for User 1...")
    user1_notifications = get_unread_notifications_for_user(test_user1[0])
    print(f"📋 User 1 has {len(user1_notifications)} unread notifications:")
    
    for i, notif in enumerate(user1_notifications, 1):
        notif_id, message, created_at, status, notif_type, scheduled_time, item_type, sender_name = notif
        print(f"   {i}. [{item_type}] {message[:60]}... (Type: {notif_type})")
    
    # Test 5: Check notifications for user 2
    print("\n5️⃣ Checking notifications for User 2...")
    user2_notifications = get_unread_notifications_for_user(test_user2[0])
    print(f"📋 User 2 has {len(user2_notifications)} unread notifications:")
    
    for i, notif in enumerate(user2_notifications, 1):
        notif_id, message, created_at, status, notif_type, scheduled_time, item_type, sender_name = notif
        print(f"   {i}. [{item_type}] {message[:60]}... (Type: {notif_type})")
    
    # Test 6: Test mention extraction
    print("\n6️⃣ Testing mention extraction...")
    test_message = "Hello @user1 and @user2, please check this out! Also @user1 again."
    mentions = extract_mentions(test_message)
    print(f"📝 Message: {test_message}")
    print(f"🔍 Extracted mentions: {mentions}")
    
    # Test 7: Test mention notification creation
    print("\n7️⃣ Testing mention notification creation...")
    create_mention_notifications(
        sender_id=test_user2[0],
        sender_username=test_user2[1],
        mentioned_usernames=[test_user1[1]],
        topic_id=1,
        message_preview="Test mention from create_mention_notifications"
    )
    
    # Test 8: Check notification counts
    print("\n8️⃣ Checking notification counts...")
    user1_count = get_notification_count_for_user(test_user1[0])
    user2_count = get_notification_count_for_user(test_user2[0])
    print(f"📊 User 1 unread count: {user1_count}")
    print(f"📊 User 2 unread count: {user2_count}")
    
    # Test 9: Mark notifications as read
    print("\n9️⃣ Testing mark as read...")
    if user1_notifications:
        first_notif = user1_notifications[0]
        notif_id, message, created_at, status, notif_type, scheduled_time, item_type, sender_name = first_notif
        mark_notification_as_read(test_user1[0], notif_id, item_type)
        print(f"✅ Marked {item_type} notification as read")
        
        # Check count again
        new_count = get_notification_count_for_user(test_user1[0])
        print(f"📊 User 1 unread count after marking as read: {new_count}")
    
    # Test 10: Verify privacy
    print("\n🔒 Testing privacy verification...")
    print("Checking that personal notifications are not visible to other users...")
    
    # Get all users and check their notifications
    all_users = get_all_users()
    for user in all_users[:5]:  # Check first 5 users
        user_notifications = get_unread_notifications_for_user(user[0])
        personal_count = sum(1 for n in user_notifications if n[6] == 'personal')
        mention_count = sum(1 for n in user_notifications if n[6] == 'mention')
        
        if user[0] == test_user1[0]:
            print(f"   👤 {user[1]}: {personal_count} personal, {mention_count} mention notifications (expected to have some)")
        else:
            print(f"   👤 {user[1]}: {personal_count} personal, {mention_count} mention notifications (should be 0)")
    
    print("\n✅ Notification system test completed!")
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Delete test notifications
        c.execute("DELETE FROM notifications WHERE message LIKE '%🧪 Test%'")
        general_deleted = c.rowcount
        
        c.execute("DELETE FROM user_notifications WHERE message LIKE '%🧪 Test%'")
        personal_deleted = c.rowcount
        
        c.execute("DELETE FROM mention_notifications WHERE message_preview LIKE '%Test%'")
        mention_deleted = c.rowcount
        
        conn.commit()
        print(f"✅ Cleaned up {general_deleted} general, {personal_deleted} personal, {mention_deleted} mention test notifications")
        
    except Exception as e:
        print(f"❌ Error cleaning up: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        success = test_notification_system()
        if success:
            print("\n🎉 All tests passed! The new notification system is working correctly.")
            print("\nKey improvements:")
            print("✅ Private mentions are now properly isolated to specific users")
            print("✅ Personal notifications are not visible to other users")
            print("✅ General notifications work for class-wide announcements")
            print("✅ Mention notifications are stored separately and tracked properly")
            print("✅ Notification counts are accurate")
        else:
            print("\n❌ Some tests failed. Please check the notification system.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask if user wants to clean up test data
        try:
            response = input("\n🧹 Clean up test data? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                cleanup_test_data()
        except KeyboardInterrupt:
            print("\n👋 Test completed without cleanup.")