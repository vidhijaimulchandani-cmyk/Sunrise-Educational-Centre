#!/usr/bin/env python3
"""
Simple Live Class System Fix
"""

import sqlite3
from datetime import datetime, timedelta
import secrets

def fix_live_class_system():
    """Fix live class system issues"""
    print("🔧 Fixing Live Class System...")
    print("=" * 50)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # 1. Fix status inconsistencies
        print("\n📋 Step 1: Fixing status inconsistencies...")
        
        # Update completed classes
        c.execute("""
            UPDATE live_classes 
            SET is_active = 0 
            WHERE status = 'completed' AND is_active = 1
        """)
        completed_fixed = c.rowcount
        print(f"  ✅ Fixed {completed_fixed} completed classes")
        
        # Update cancelled classes
        c.execute("""
            UPDATE live_classes 
            SET is_active = 0 
            WHERE status = 'cancelled' AND is_active = 1
        """)
        cancelled_fixed = c.rowcount
        print(f"  ✅ Fixed {cancelled_fixed} cancelled classes")
        
        # Update active classes
        c.execute("""
            UPDATE live_classes 
            SET status = 'active' 
            WHERE is_active = 1 AND status != 'active'
        """)
        active_fixed = c.rowcount
        print(f"  ✅ Fixed {active_fixed} active classes")
        
        # 2. Add missing columns
        print("\n📋 Step 2: Adding missing columns...")
        
        # Add duration column
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN duration_minutes INTEGER DEFAULT 60")
            print("  ✅ Added duration column")
        except sqlite3.OperationalError:
            print("  ℹ️  Duration column already exists")
        
        # Add attendance column
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN attendance_count INTEGER DEFAULT 0")
            print("  ✅ Added attendance column")
        except sqlite3.OperationalError:
            print("  ℹ️  Attendance column already exists")
        
        # 3. Create attendance tracking table
        print("\n📋 Step 3: Creating attendance tracking...")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                left_at TEXT,
                FOREIGN KEY (class_id) REFERENCES live_classes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("  ✅ Created attendance table")
        
        # 4. Create messages table
        print("\n📋 Step 4: Creating messages table...")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (class_id) REFERENCES live_classes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("  ✅ Created messages table")
        
        # 5. Add indexes for performance
        print("\n📋 Step 5: Adding performance indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_live_classes_status ON live_classes(status)",
            "CREATE INDEX IF NOT EXISTS idx_live_classes_active ON live_classes(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_class ON live_class_attendance(class_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_class ON live_class_messages(class_id)"
        ]
        
        for index_sql in indexes:
            try:
                c.execute(index_sql)
            except sqlite3.OperationalError:
                pass
        
        print("  ✅ Added performance indexes")
        
        # 6. Show current status
        print("\n📋 Step 6: Current system status...")
        
        c.execute("SELECT status, COUNT(*) FROM live_classes GROUP BY status")
        status_counts = c.fetchall()
        
        print("  Class distribution:")
        for status, count in status_counts:
            print(f"    {status}: {count} classes")
        
        # Show recent classes
        c.execute("""
            SELECT id, topic, status, is_active, created_at 
            FROM live_classes 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_classes = c.fetchall()
        
        print("\n  Recent classes:")
        for class_id, topic, status, active, created in recent_classes:
            print(f"    ID {class_id}: {topic} ({status}, active: {active})")
        
        # Commit changes
        conn.commit()
        print("\n✅ Live class system fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing live classes: {e}")
        conn.rollback()
    finally:
        conn.close()

def add_helper_functions():
    """Add helper functions to auth_handler.py"""
    print("\n📝 Adding helper functions to auth_handler.py...")
    
    helper_functions = '''
# Live Class Helper Functions
def record_attendance(class_id, user_id, username, action='join'):
    """Record user attendance in live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    if action == 'join':
        try:
            c.execute('''
                INSERT INTO live_class_attendance (class_id, user_id, username, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (class_id, user_id, username, now))
            # Update attendance count
            c.execute('''
                UPDATE live_classes 
                SET attendance_count = attendance_count + 1 
                WHERE id = ?
            ''', (class_id,))
        except sqlite3.IntegrityError:
            pass  # User already joined
    elif action == 'leave':
        c.execute('''
            UPDATE live_class_attendance 
            SET left_at = ? 
            WHERE class_id = ? AND user_id = ? AND left_at IS NULL
        ''', (now, class_id, user_id))
    
    conn.commit()
    conn.close()

def get_class_attendance(class_id):
    """Get attendance list for a class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, joined_at, left_at
        FROM live_class_attendance
        WHERE class_id = ?
        ORDER BY joined_at
    ''', (class_id,))
    attendance = c.fetchall()
    conn.close()
    return attendance

def save_live_class_message(class_id, user_id, username, message):
    """Save a message from live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO live_class_messages (class_id, user_id, username, message, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (class_id, user_id, username, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_live_class_messages(class_id, limit=50):
    """Get recent messages from live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, message, created_at
        FROM live_class_messages
        WHERE class_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (class_id, limit))
    messages = c.fetchall()
    conn.close()
    return messages[::-1]  # Return in chronological order

def update_live_class_status(class_id, status):
    """Update live class status"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        UPDATE live_classes 
        SET status = ?, is_active = ?
        WHERE id = ?
    ''', (status, 1 if status == 'active' else 0, class_id))
    conn.commit()
    conn.close()
'''
    
    # Read current auth_handler.py
    try:
        with open('auth_handler.py', 'r') as f:
            content = f.read()
        
        # Add helper functions at the end
        if '# Live Class Helper Functions' not in content:
            with open('auth_handler.py', 'a') as f:
                f.write('\n' + helper_functions)
            print("  ✅ Added helper functions to auth_handler.py")
        else:
            print("  ℹ️  Helper functions already exist")
            
    except Exception as e:
        print(f"  ❌ Error adding helper functions: {e}")

def test_system():
    """Test the fixed system"""
    print("\n🧪 Testing fixed system...")
    
    try:
        # Test creating a class
        from auth_handler import create_live_class, get_class_details_by_id
        
        test_class_id = create_live_class(
            class_code="TEST123",
            pin="1234",
            meeting_url="/test.mp4",
            topic="Test Class",
            description="Test description"
        )
        print(f"  ✅ Created test class: {test_class_id}")
        
        # Test attendance recording
        from auth_handler import record_attendance
        record_attendance(test_class_id, 1, "test_user", "join")
        print("  ✅ Tested attendance recording")
        
        # Test message saving
        from auth_handler import save_live_class_message
        save_live_class_message(test_class_id, 1, "test_user", "Hello world!")
        print("  ✅ Tested message saving")
        
        # Clean up
        import sqlite3
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM live_class_attendance WHERE class_id = ?", (test_class_id,))
        c.execute("DELETE FROM live_class_messages WHERE class_id = ?", (test_class_id,))
        c.execute("DELETE FROM live_classes WHERE id = ?", (test_class_id,))
        conn.commit()
        conn.close()
        print("  ✅ Cleaned up test data")
        
    except Exception as e:
        print(f"  ❌ Error testing system: {e}")

if __name__ == '__main__':
    print("🚀 Simple Live Class System Fix")
    print("=" * 50)
    
    fix_live_class_system()
    add_helper_functions()
    test_system()
    
    print("\n" + "=" * 50)
    print("✅ Live class system fix completed!")
    print("\nWhat was fixed:")
    print("• Status inconsistencies resolved")
    print("• Added attendance tracking system")
    print("• Added live messaging system")
    print("• Added performance indexes")
    print("• Added helper functions")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test creating a new live class")
    print("3. Check attendance tracking works")
    print("4. Verify live messaging works")
    print("5. Test status updates") 