#!/usr/bin/env python3
import sqlite3
import os

def test_database():
    print("🔍 Testing database structure...")
    
    # Check if users.db exists
    if not os.path.exists('users.db'):
        print("❌ users.db not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if admissions table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if not c.fetchone():
            print("❌ admissions table not found!")
            return False
        
        # Check table structure
        c.execute("PRAGMA table_info(admissions)")
        columns = c.fetchall()
        
        print("📋 Admissions table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check for required columns
        required_columns = [
            'user_id', 'submit_ip', 'approved_at', 'approved_by', 
            'disapproved_at', 'disapproved_by', 'disapproval_reason'
        ]
        
        existing_columns = [col[1] for col in columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required columns present")
        
        # Check admission_access table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if not c.fetchone():
            print("❌ admission_access table not found!")
            return False
        else:
            print("✅ admission_access table exists")
        
        # Check uploads directory
        if not os.path.exists('uploads'):
            print("❌ uploads directory not found!")
            return False
        else:
            print("✅ uploads directory exists")
        
        if not os.path.exists('uploads/admission_photos'):
            print("❌ uploads/admission_photos directory not found!")
            return False
        else:
            print("✅ uploads/admission_photos directory exists")
        
        conn.close()
        print("✅ Database structure test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()