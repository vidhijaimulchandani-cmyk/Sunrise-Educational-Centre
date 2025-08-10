#!/usr/bin/env python3
"""
Simple test script to verify the admission system is working
"""

import sqlite3
import os

def test_admission_system():
    print("🧪 Testing Admission System...")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists('users.db'):
        print("❌ users.db not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check admissions table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if not c.fetchone():
            print("❌ admissions table not found!")
            return False
        else:
            print("✅ admissions table exists")
        
        # Check admission_access table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if not c.fetchone():
            print("❌ admission_access table not found!")
            return False
        else:
            print("✅ admission_access table exists")
        
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
        
        # Test database connection using DATABASE variable
        print("\n🔍 Testing database connection...")
        try:
            # This simulates what the Flask app would do
            test_conn = sqlite3.connect('users.db')
            test_c = test_conn.cursor()
            test_c.execute("SELECT COUNT(*) FROM admissions")
            count = test_c.fetchone()[0]
            test_conn.close()
            print(f"✅ Database connection successful - {count} admissions found")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        conn.close()
        print("\n🎉 Admission system test completed successfully!")
        print("💡 The system appears to be ready for use!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_admission_system()