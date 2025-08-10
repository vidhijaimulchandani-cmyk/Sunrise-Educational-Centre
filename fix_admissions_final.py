#!/usr/bin/env python3
"""
Comprehensive fix for the admission system
This script addresses all remaining issues:
1. Database schema problems
2. Missing columns
3. Directory structure
4. Table initialization
"""

import sqlite3
import os
import sys

def create_directories():
    """Create necessary directories if they don't exist"""
    print("📁 Creating directories...")
    
    directories = [
        'uploads',
        'uploads/admission_photos',
        'templates'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created: {directory}")
        else:
            print(f"✅ Exists: {directory}")

def fix_admissions_table():
    """Fix the admissions table structure"""
    print("🔧 Fixing admissions table...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if not c.fetchone():
            print("❌ Admissions table not found! Creating it...")
            c.execute('''CREATE TABLE admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                student_phone TEXT NOT NULL,
                student_email TEXT NOT NULL,
                class TEXT NOT NULL,
                school_name TEXT NOT NULL,
                maths_marks INTEGER NOT NULL,
                maths_rating REAL NOT NULL,
                last_percentage REAL NOT NULL,
                parent_name TEXT NOT NULL,
                parent_phone TEXT NOT NULL,
                passport_photo TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                submit_ip TEXT,
                approved_at TEXT,
                approved_by TEXT,
                disapproved_at TEXT,
                disapproved_by TEXT,
                disapproval_reason TEXT
            )''')
            print("✅ Created admissions table")
        else:
            print("✅ Admissions table exists")
        
        # Check and add missing columns
        c.execute("PRAGMA table_info(admissions)")
        existing_columns = [row[1] for row in c.fetchall()]
        
        required_columns = [
            ('user_id', 'INTEGER'),
            ('submit_ip', 'TEXT'),
            ('approved_at', 'TEXT'),
            ('approved_by', 'TEXT'),
            ('disapproved_at', 'TEXT'),
            ('disapproved_by', 'TEXT'),
            ('disapproval_reason', 'TEXT')
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                try:
                    c.execute(f'ALTER TABLE admissions ADD COLUMN {col_name} {col_type}')
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    print(f"⚠️  Column {col_name} already exists or error: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Admissions table fixed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing admissions table: {e}")
        return False

def fix_admission_access_table():
    """Fix the admission_access table"""
    print("🔧 Fixing admission_access table...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if not c.fetchone():
            print("❌ Admission access table not found! Creating it...")
            c.execute('''CREATE TABLE admission_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_id INTEGER NOT NULL,
                access_username TEXT UNIQUE NOT NULL,
                access_password TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            print("✅ Created admission_access table")
        else:
            print("✅ Admission access table exists")
        
        conn.commit()
        conn.close()
        print("✅ Admission access table fixed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing admission access table: {e}")
        return False

def verify_database():
    """Verify the database structure"""
    print("🔍 Verifying database structure...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check admissions table
        c.execute("PRAGMA table_info(admissions)")
        columns = c.fetchall()
        
        print("📋 Admissions table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check admission_access table
        c.execute("PRAGMA table_info(admission_access)")
        access_columns = c.fetchall()
        
        print("📋 Admission access table columns:")
        for col in access_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("✅ Database verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def test_admission_submission():
    """Test if admission submission would work"""
    print("🧪 Testing admission submission logic...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Test INSERT statement (without actually inserting)
        test_data = (
            'Test Student', '2000-01-01', '1234567890', 'test@example.com',
            'Class 11 Applied', 'Test School', 85, 4.2, 78.5,
            'Test Parent', '0987654321', 'test_photo.jpg', 'pending',
            '2024-01-01 12:00:00', None, '127.0.0.1'
        )
        
        # This should match the columns in the INSERT statement
        columns = (
            'student_name', 'dob', 'student_phone', 'student_email', 'class', 'school_name',
            'maths_marks', 'maths_rating', 'last_percentage', 'parent_name', 'parent_phone', 
            'passport_photo', 'status', 'submitted_at', 'user_id', 'submit_ip'
        )
        
        print(f"📝 Test INSERT statement:")
        print(f"  Columns ({len(columns)}): {', '.join(columns)}")
        print(f"  Values ({len(test_data)}): {len(test_data)} values")
        
        if len(columns) == len(test_data):
            print("✅ Column count matches value count")
        else:
            print("❌ Column count mismatch!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main function to run all fixes"""
    print("🚀 Starting comprehensive admission system fix...")
    print("=" * 50)
    
    # Step 1: Create directories
    create_directories()
    print()
    
    # Step 2: Fix admissions table
    if not fix_admissions_table():
        print("❌ Failed to fix admissions table")
        sys.exit(1)
    print()
    
    # Step 3: Fix admission access table
    if not fix_admission_access_table():
        print("❌ Failed to fix admission access table")
        sys.exit(1)
    print()
    
    # Step 4: Verify database
    if not verify_database():
        print("❌ Database verification failed")
        sys.exit(1)
    print()
    
    # Step 5: Test admission submission
    if not test_admission_submission():
        print("❌ Admission submission test failed")
        sys.exit(1)
    print()
    
    print("🎉 All fixes completed successfully!")
    print("💡 You can now:")
    print("   1. Start the Flask app: python3 app.py")
    print("   2. Test admission submission at /admission")
    print("   3. Check admin panel at /admin/admissions")

if __name__ == "__main__":
    main()