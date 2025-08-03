#!/usr/bin/env python3
"""
Comprehensive Live Class System Fix
"""

import sqlite3
from datetime import datetime, timedelta
import os

def fix_live_class_system():
    """Fix all live class system issues"""
    print("🔧 Fixing Live Class System...")
    print("=" * 50)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # 1. Check and fix database schema
        print("\n📋 Step 1: Checking database schema...")
        c.execute("PRAGMA table_info(live_classes)")
        columns = [row[1] for row in c.fetchall()]
        
        required_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'class_code': 'TEXT NOT NULL UNIQUE',
            'pin': 'TEXT NOT NULL',
            'meeting_url': 'TEXT NOT NULL',
            'topic': 'TEXT',
            'description': 'TEXT',
            'is_active': 'INTEGER NOT NULL DEFAULT 1',
            'created_at': 'TEXT NOT NULL',
            'status': 'TEXT DEFAULT "scheduled"',
            'scheduled_time': 'TEXT',
            'paid': 'TEXT DEFAULT "unpaid"'
        }
        
        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"Adding {len(missing_columns)} missing columns...")
            for col_name, col_type in missing_columns:
                try:
                    c.execute(f"ALTER TABLE live_classes ADD COLUMN {col_name} {col_type}")
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e):
                        print(f"  ❌ Error adding {col_name}: {e}")
        else:
            print("✅ Database schema is up to date")
        
        # 2. Fix status and is_active inconsistencies
        print("\n📋 Step 2: Fixing status inconsistencies...")
        
        # Update completed classes to have is_active = 0
        c.execute("""
            UPDATE live_classes 
            SET is_active = 0 
            WHERE status = 'completed' AND is_active = 1
        """)
        completed_fixed = c.rowcount
        print(f"  ✅ Fixed {completed_fixed} completed classes (set is_active = 0)")
        
        # Update cancelled classes to have is_active = 0
        c.execute("""
            UPDATE live_classes 
            SET is_active = 0 
            WHERE status = 'cancelled' AND is_active = 1
        """)
        cancelled_fixed = c.rowcount
        print(f"  ✅ Fixed {cancelled_fixed} cancelled classes (set is_active = 0)")
        
        # Update active classes to have status = 'active'
        c.execute("""
            UPDATE live_classes 
            SET status = 'active' 
            WHERE is_active = 1 AND status != 'active'
        """)
        active_fixed = c.rowcount
        print(f"  ✅ Fixed {active_fixed} active classes (set status = 'active')")
        
        # 3. Auto-update class statuses based on scheduled_time
        print("\n📋 Step 3: Auto-updating class statuses...")
        
        # Get current time
        now = datetime.now()
        
        # Update past scheduled classes to completed
        c.execute("""
            UPDATE live_classes 
            SET status = 'completed', is_active = 0 
            WHERE scheduled_time IS NOT NULL 
            AND scheduled_time < ? 
            AND status = 'scheduled'
        """, (now.isoformat(),))
        past_completed = c.rowcount
        print(f"  ✅ Marked {past_completed} past scheduled classes as completed")
        
        # Update classes that should be active now
        c.execute("""
            UPDATE live_classes 
            SET status = 'active', is_active = 1 
            WHERE scheduled_time IS NOT NULL 
            AND scheduled_time <= ? 
            AND scheduled_time > ? 
            AND status = 'scheduled'
        """, (now.isoformat(), (now - timedelta(hours=2)).isoformat()))
        now_active = c.rowcount
        print(f"  ✅ Marked {now_active} classes as active")
        
        # 4. Clean up orphaned data
        print("\n📋 Step 4: Cleaning up orphaned data...")
        
        # Remove classes with invalid status
        c.execute("""
            DELETE FROM live_classes 
            WHERE status NOT IN ('scheduled', 'active', 'completed', 'cancelled')
        """)
        invalid_removed = c.rowcount
        print(f"  ✅ Removed {invalid_removed} classes with invalid status")
        
        # 5. Add missing data
        print("\n📋 Step 5: Adding missing data...")
        
        # Set default status for classes without status
        c.execute("""
            UPDATE live_classes 
            SET status = 'scheduled' 
            WHERE status IS NULL
        """)
        status_added = c.rowcount
        print(f"  ✅ Added status to {status_added} classes")
        
        # Set default paid status
        c.execute("""
            UPDATE live_classes 
            SET paid = 'unpaid' 
            WHERE paid IS NULL
        """)
        paid_added = c.rowcount
        print(f"  ✅ Added paid status to {paid_added} classes")
        
        # 6. Validate and fix class codes
        print("\n📋 Step 6: Validating class codes...")
        
        # Check for duplicate class codes
        c.execute("""
            SELECT class_code, COUNT(*) 
            FROM live_classes 
            GROUP BY class_code 
            HAVING COUNT(*) > 1
        """)
        duplicates = c.fetchall()
        
        if duplicates:
            print(f"  ⚠️  Found {len(duplicates)} duplicate class codes")
            for code, count in duplicates:
                print(f"     Code '{code}' appears {count} times")
        else:
            print("  ✅ No duplicate class codes found")
        
        # 7. Show current status
        print("\n📋 Step 7: Current live class status...")
        
        c.execute("""
            SELECT status, COUNT(*) 
            FROM live_classes 
            GROUP BY status
        """)
        status_counts = c.fetchall()
        
        print("  Current class distribution:")
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
        
        # Commit all changes
        conn.commit()
        print("\n✅ All fixes applied successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing live classes: {e}")
        conn.rollback()
    finally:
        conn.close()

def test_live_class_functions():
    """Test live class functions after fixes"""
    print("\n🧪 Testing Live Class Functions...")
    print("=" * 50)
    
    try:
        from auth_handler import (
            get_active_live_classes,
            get_scheduled_live_classes,
            get_completed_live_classes,
            get_upcoming_live_classes,
            create_live_class
        )
        
        # Test creating a new class
        print("\n📝 Testing class creation...")
        test_class_id = create_live_class(
            class_code="TEST123",
            pin="1234",
            meeting_url="https://test.com",
            topic="Test Class",
            description="Test description",
            status="scheduled",
            scheduled_time=(datetime.now() + timedelta(hours=1)).isoformat()
        )
        print(f"  ✅ Created test class with ID: {test_class_id}")
        
        # Test getting different class types
        print("\n📋 Testing class retrieval functions...")
        
        active_classes = get_active_live_classes()
        print(f"  Active classes: {len(active_classes)}")
        
        scheduled_classes = get_scheduled_live_classes()
        print(f"  Scheduled classes: {len(scheduled_classes)}")
        
        completed_classes = get_completed_live_classes()
        print(f"  Completed classes: {len(completed_classes)}")
        
        upcoming_classes = get_upcoming_live_classes()
        print(f"  Upcoming classes: {len(upcoming_classes)}")
        
        # Clean up test class
        import sqlite3
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM live_classes WHERE class_code = 'TEST123'")
        conn.commit()
        conn.close()
        print("  ✅ Cleaned up test class")
        
    except Exception as e:
        print(f"❌ Error testing functions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🚀 Live Class System Fix Tool")
    print("=" * 50)
    
    fix_live_class_system()
    test_live_class_functions()
    
    print("\n" + "=" * 50)
    print("✅ Live class system fix completed!")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Test creating a new live class")
    print("3. Check the live class management dashboard")
    print("4. Verify that status updates work properly") 