#!/usr/bin/env python3
"""
Quick Live Class Fix
"""

import sqlite3
from datetime import datetime

def quick_fix():
    """Quick fix for live class issues"""
    print("🔧 Quick Live Class Fix")
    print("=" * 40)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Fix status inconsistencies
        print("\n📋 Fixing status inconsistencies...")
        
        # Fix completed classes
        c.execute("UPDATE live_classes SET is_active = 0 WHERE status = 'completed' AND is_active = 1")
        print(f"  ✅ Fixed {c.rowcount} completed classes")
        
        # Fix cancelled classes
        c.execute("UPDATE live_classes SET is_active = 0 WHERE status = 'cancelled' AND is_active = 1")
        print(f"  ✅ Fixed {c.rowcount} cancelled classes")
        
        # Fix active classes
        c.execute("UPDATE live_classes SET status = 'active' WHERE is_active = 1 AND status != 'active'")
        print(f"  ✅ Fixed {c.rowcount} active classes")
        
        # Add missing columns
        print("\n📋 Adding missing columns...")
        
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN duration_minutes INTEGER DEFAULT 60")
            print("  ✅ Added duration column")
        except:
            print("  ℹ️  Duration column already exists")
        
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN attendance_count INTEGER DEFAULT 0")
            print("  ✅ Added attendance column")
        except:
            print("  ℹ️  Attendance column already exists")
        
        # Create attendance table
        print("\n📋 Creating attendance table...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                user_id INTEGER,
                username TEXT,
                joined_at TEXT
            )
        ''')
        print("  ✅ Created attendance table")
        
        # Create messages table
        print("\n📋 Creating messages table...")
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                user_id INTEGER,
                username TEXT,
                message TEXT,
                created_at TEXT
            )
        ''')
        print("  ✅ Created messages table")
        
        # Show current status
        print("\n📋 Current status...")
        c.execute("SELECT status, COUNT(*) FROM live_classes GROUP BY status")
        for status, count in c.fetchall():
            print(f"  {status}: {count} classes")
        
        conn.commit()
        print("\n✅ Quick fix completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    quick_fix()
    print("\nNext steps:")
    print("1. Restart Flask app")
    print("2. Test live class creation")
    print("3. Check status management") 