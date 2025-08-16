"""
Notifications System for Sunrise Education Centre
Handles all notification types including private mentions, general notifications, and personal messages
"""

import sqlite3
from datetime import datetime, timezone
import re
from typing import List, Dict, Optional, Tuple

# Database configuration
DATABASE = 'users.db'

def get_ist_timestamp():
    """Get current timestamp in IST format"""
    ist_time = datetime.now(timezone.utc).astimezone()
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

def ensure_notification_tables():
    """Ensure all notification-related tables exist with proper structure"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Main notifications table for general notifications
        c.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            class_id INTEGER,
            created_at TEXT,
            target_paid_status TEXT DEFAULT 'all',
            status TEXT DEFAULT 'active',
            notification_type TEXT DEFAULT 'general',
            scheduled_time TEXT,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )''')
        
        # User-specific notifications table for private notifications
        c.execute('''CREATE TABLE IF NOT EXISTS user_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'personal',
            created_at TEXT,
            is_read INTEGER DEFAULT 0,
            read_at TEXT,
            sender_id INTEGER,
            related_id INTEGER,  -- For forum messages, live classes, etc.
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )''')
        
        # User notification status table for tracking read/unread
        c.execute('''CREATE TABLE IF NOT EXISTS user_notification_status (
            user_id INTEGER,
            notification_id INTEGER,
            seen_at TEXT,
            PRIMARY KEY (user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (notification_id) REFERENCES notifications (id)
        )''')
        
        # Mention notifications table for forum mentions
        c.execute('''CREATE TABLE IF NOT EXISTS mention_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentioned_user_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            forum_message_id INTEGER,
            topic_id INTEGER,
            message_preview TEXT,
            created_at TEXT,
            is_read INTEGER DEFAULT 0,
            read_at TEXT,
            FOREIGN KEY (mentioned_user_id) REFERENCES users (id),
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (forum_message_id) REFERENCES forum_messages (id),
            FOREIGN KEY (topic_id) REFERENCES forum_topics (id)
        )''')
        
        conn.commit()
        print("✅ Notification tables ensured successfully")
        
    except Exception as e:
        print(f"❌ Error ensuring notification tables: {e}")
    finally:
        conn.close()

def add_general_notification(message: str, class_id: Optional[int] = None, 
                           target_paid_status: str = 'all', 
                           notification_type: str = 'general',
                           scheduled_time: Optional[str] = None) -> int:
    """
    Add a general notification for a class or all users
    
    Args:
        message: Notification message
        class_id: Class ID (None for all classes)
        target_paid_status: 'all', 'paid', 'unpaid'
        notification_type: Type of notification
        scheduled_time: Scheduled time for the notification
    
    Returns:
        Notification ID
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO notifications 
            (message, class_id, created_at, target_paid_status, status, notification_type, scheduled_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message, class_id, get_ist_timestamp(), target_paid_status, 'active', notification_type, scheduled_time))
        
        notification_id = c.lastrowid
        conn.commit()
        print(f"✅ Added general notification: {message[:50]}...")
        return notification_id
        
    except Exception as e:
        print(f"❌ Error adding general notification: {e}")
        return None
    finally:
        conn.close()

def add_personal_notification(message: str, user_id: int, 
                            notification_type: str = 'personal',
                            sender_id: Optional[int] = None,
                            related_id: Optional[int] = None) -> int:
    """
    Add a personal notification for a specific user
    
    Args:
        message: Notification message
        user_id: Target user ID
        notification_type: Type of notification
        sender_id: ID of user who triggered the notification
        related_id: Related entity ID (forum message, live class, etc.)
    
    Returns:
        Notification ID
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO user_notifications 
            (user_id, message, notification_type, created_at, sender_id, related_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, message, notification_type, get_ist_timestamp(), sender_id, related_id))
        
        notification_id = c.lastrowid
        conn.commit()
        print(f"✅ Added personal notification for user {user_id}: {message[:50]}...")
        return notification_id
        
    except Exception as e:
        print(f"❌ Error adding personal notification: {e}")
        return None
    finally:
        conn.close()

def add_mention_notification(mentioned_user_id: int, sender_id: int, 
                           forum_message_id: Optional[int] = None,
                           topic_id: Optional[int] = None,
                           message_preview: str = "") -> int:
    """
    Add a mention notification for forum mentions
    
    Args:
        mentioned_user_id: ID of mentioned user
        sender_id: ID of user who mentioned
        forum_message_id: ID of forum message
        topic_id: ID of forum topic
        message_preview: Preview of the message
    
    Returns:
        Mention notification ID
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO mention_notifications 
            (mentioned_user_id, sender_id, forum_message_id, topic_id, message_preview, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (mentioned_user_id, sender_id, forum_message_id, topic_id, message_preview, get_ist_timestamp()))
        
        mention_id = c.lastrowid
        conn.commit()
        print(f"✅ Added mention notification for user {mentioned_user_id} from user {sender_id}")
        return mention_id
        
    except Exception as e:
        print(f"❌ Error adding mention notification: {e}")
        return None
    finally:
        conn.close()

def get_unread_notifications_for_user(user_id: int) -> List[Tuple]:
    """
    Get all unread notifications for a specific user
    
    Args:
        user_id: User ID
    
    Returns:
        List of notification tuples
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Get user info
        c.execute('SELECT class_id, paid FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        if not result:
            return []
        
        class_id, user_paid_status = result
        all_notifications = []
        
        # 1. Get general notifications for user's class
        c.execute('''
            SELECT n.id, n.message, n.created_at, n.status, n.notification_type, 
                   n.scheduled_time, 'general' as item_type, NULL as sender_name
            FROM notifications n
            LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = ?
            WHERE n.class_id = ? AND uns.notification_id IS NULL
            AND (n.target_paid_status = 'all' OR n.target_paid_status = ?)
            AND n.status IN ('active', 'scheduled')
        ''', (user_id, class_id, user_paid_status))
        general_notifications = c.fetchall()
        all_notifications.extend(general_notifications)
        
        # 2. Get personal notifications for this specific user
        c.execute('''
            SELECT un.id, un.message, un.created_at, 'active' as status, 
                   un.notification_type, un.created_at as scheduled_time, 
                   'personal' as item_type, u.username as sender_name
            FROM user_notifications un
            LEFT JOIN users u ON un.sender_id = u.id
            WHERE un.user_id = ? AND un.is_read = 0
        ''', (user_id,))
        personal_notifications = c.fetchall()
        all_notifications.extend(personal_notifications)
        
        # 3. Get mention notifications for this specific user
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
            WHERE mn.mentioned_user_id = ? AND mn.is_read = 0
        ''', (user_id,))
        mention_notifications = c.fetchall()
        all_notifications.extend(mention_notifications)
        
        # 4. Get personal chat messages (unread)
        c.execute('''
            SELECT pc.id, pc.message, pc.created_at, 'active' as status, 
                   'personal_chat' as notification_type, pc.created_at as scheduled_time,
                   'personal_chat' as item_type, u.username as sender_name
            FROM personal_chats pc
            JOIN users u ON pc.sender_id = u.id
            WHERE pc.receiver_id = ? AND pc.is_read = 0
        ''', (user_id,))
        personal_messages = c.fetchall()
        all_notifications.extend(personal_messages)
        
        # Sort by creation time (newest first)
        all_notifications.sort(key=lambda x: x[2], reverse=True)
        
        return all_notifications
        
    except Exception as e:
        print(f"❌ Error getting notifications for user {user_id}: {e}")
        return []
    finally:
        conn.close()

def mark_notification_as_read(user_id: int, notification_id: int, notification_type: str = 'general'):
    """
    Mark a notification as read
    
    Args:
        user_id: User ID
        notification_id: Notification ID
        notification_type: Type of notification ('general', 'personal', 'mention', 'personal_chat')
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        if notification_type == 'general':
            # Mark general notification as seen
            c.execute('''
                INSERT OR REPLACE INTO user_notification_status 
                (user_id, notification_id, seen_at) VALUES (?, ?, ?)
            ''', (user_id, notification_id, get_ist_timestamp()))
            
        elif notification_type == 'personal':
            # Mark personal notification as read
            c.execute('''
                UPDATE user_notifications 
                SET is_read = 1, read_at = ? 
                WHERE id = ? AND user_id = ?
            ''', (get_ist_timestamp(), notification_id, user_id))
            
        elif notification_type == 'mention':
            # Mark mention notification as read
            c.execute('''
                UPDATE mention_notifications 
                SET is_read = 1, read_at = ? 
                WHERE id = ? AND mentioned_user_id = ?
            ''', (get_ist_timestamp(), notification_id, user_id))
            
        elif notification_type == 'personal_chat':
            # Mark personal chat message as read
            c.execute('''
                UPDATE personal_chats 
                SET is_read = 1 
                WHERE id = ? AND receiver_id = ?
            ''', (notification_id, user_id))
        
        conn.commit()
        print(f"✅ Marked {notification_type} notification {notification_id} as read for user {user_id}")
        
    except Exception as e:
        print(f"❌ Error marking notification as read: {e}")
    finally:
        conn.close()

def get_notification_count_for_user(user_id: int) -> int:
    """
    Get count of unread notifications for a user
    
    Args:
        user_id: User ID
    
    Returns:
        Count of unread notifications
    """
    notifications = get_unread_notifications_for_user(user_id)
    return len(notifications)

def delete_notification(notification_id: int, notification_type: str = 'general'):
    """
    Delete a notification
    
    Args:
        notification_id: Notification ID
        notification_type: Type of notification
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        if notification_type == 'general':
            # Delete from notifications table
            c.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
            # Also delete from user_notification_status
            c.execute('DELETE FROM user_notification_status WHERE notification_id = ?', (notification_id,))
            
        elif notification_type == 'personal':
            # Delete from user_notifications table
            c.execute('DELETE FROM user_notifications WHERE id = ?', (notification_id,))
            
        elif notification_type == 'mention':
            # Delete from mention_notifications table
            c.execute('DELETE FROM mention_notifications WHERE id = ?', (notification_id,))
        
        conn.commit()
        print(f"✅ Deleted {notification_type} notification {notification_id}")
        
    except Exception as e:
        print(f"❌ Error deleting notification: {e}")
    finally:
        conn.close()

def create_mention_notifications(sender_id: int, sender_username: str, 
                               mentioned_usernames: List[str], 
                               topic_id: Optional[int] = None,
                               message_preview: str = ""):
    """
    Create mention notifications for mentioned users
    
    Args:
        sender_id: ID of user who sent the message
        sender_username: Username of sender
        mentioned_usernames: List of mentioned usernames
        topic_id: Forum topic ID
        message_preview: Preview of the message
    """
    from auth_handler import get_user_by_username
    
    for username in mentioned_usernames:
        # Get the mentioned user
        mentioned_user = get_user_by_username(username)
        if mentioned_user and mentioned_user[0] != sender_id:  # Don't notify self
            mentioned_user_id = mentioned_user[0]
            
            # Create mention notification
            add_mention_notification(
                mentioned_user_id=mentioned_user_id,
                sender_id=sender_id,
                topic_id=topic_id,
                message_preview=message_preview
            )

def extract_mentions(message: str) -> List[str]:
    """
    Extract mentioned usernames from message text
    
    Args:
        message: Message text
    
    Returns:
        List of mentioned usernames
    """
    mentions = re.findall(r'@(\w+)', message)
    return list(set(mentions))  # Remove duplicates

def get_all_notifications_for_admin() -> List[Tuple]:
    """
    Get all notifications for admin panel
    
    Returns:
        List of all notifications
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Get general notifications
        c.execute('''
            SELECT n.id, n.message, n.created_at, n.status, n.notification_type,
                   CASE 
                       WHEN n.class_id IS NOT NULL THEN c.name
                       ELSE 'All Classes'
                   END as class_name,
                   n.target_paid_status, 'general' as source
            FROM notifications n
            LEFT JOIN classes c ON n.class_id = c.id
            ORDER BY n.created_at DESC
        ''')
        general_notifications = c.fetchall()
        
        # Get personal notifications
        c.execute('''
            SELECT un.id, un.message, un.created_at, 'active' as status, 
                   un.notification_type, u.username as class_name,
                   'personal' as target_paid_status, 'personal' as source
            FROM user_notifications un
            JOIN users u ON un.user_id = u.id
            ORDER BY un.created_at DESC
        ''')
        personal_notifications = c.fetchall()
        
        # Get mention notifications
        c.execute('''
            SELECT mn.id, 
                   'Mention by @' || u.username || ' to @' || mu.username as message,
                   mn.created_at, 'active' as status, 'forum_mention' as notification_type,
                   mu.username as class_name, 'personal' as target_paid_status, 'mention' as source
            FROM mention_notifications mn
            JOIN users u ON mn.sender_id = u.id
            JOIN users mu ON mn.mentioned_user_id = mu.id
            ORDER BY mn.created_at DESC
        ''')
        mention_notifications = c.fetchall()
        
        # Combine and sort
        all_notifications = general_notifications + personal_notifications + mention_notifications
        all_notifications.sort(key=lambda x: x[2], reverse=True)
        
        return all_notifications
        
    except Exception as e:
        print(f"❌ Error getting all notifications: {e}")
        return []
    finally:
        conn.close()

def cleanup_old_notifications(days_old: int = 30):
    """
    Clean up old notifications
    
    Args:
        days_old: Number of days after which to delete notifications
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        cutoff_date = (datetime.now() - datetime.timedelta(days=days_old)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Delete old general notifications
        c.execute('DELETE FROM notifications WHERE created_at < ?', (cutoff_date,))
        general_deleted = c.rowcount
        
        # Delete old personal notifications
        c.execute('DELETE FROM user_notifications WHERE created_at < ?', (cutoff_date,))
        personal_deleted = c.rowcount
        
        # Delete old mention notifications
        c.execute('DELETE FROM mention_notifications WHERE created_at < ?', (cutoff_date,))
        mention_deleted = c.rowcount
        
        # Clean up orphaned status records
        c.execute('''
            DELETE FROM user_notification_status 
            WHERE notification_id NOT IN (SELECT id FROM notifications)
        ''')
        status_deleted = c.rowcount
        
        conn.commit()
        print(f"✅ Cleaned up {general_deleted} general, {personal_deleted} personal, {mention_deleted} mention notifications")
        print(f"✅ Cleaned up {status_deleted} orphaned status records")
        
    except Exception as e:
        print(f"❌ Error cleaning up notifications: {e}")
    finally:
        conn.close()

# Initialize tables when module is imported
ensure_notification_tables()