#!/usr/bin/env python3
import sqlite3
import os

def test_database():
    print("Testing database connection and structure...")
    
    # Check if database exists
    if not os.path.exists('users.db'):
        print("❌ users.db not found!")
        return False
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        print("✅ Database connection successful")
        
        # Check if admissions table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if c.fetchone():
            print("✅ Admissions table exists")
            
            # Check table structure
            c.execute("PRAGMA table_info(admissions)")
            columns = c.fetchall()
            print(f"📋 Table has {len(columns)} columns:")
            
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check if required columns exist
            required_columns = [
                'user_id', 'submit_ip', 'approved_at', 'approved_by', 
                'disapproved_at', 'disapproved_by', 'disapproval_reason'
            ]
            
            existing_columns = [col[1] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"⚠️  Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All required columns exist")
                
        else:
            print("❌ Admissions table does not exist!")
            return False
        
        # Check admission_access table
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if c.fetchone():
            print("✅ Admission access table exists")
        else:
            print("❌ Admission access table does not exist!")
            return False
        
        # Check uploads directory
        if os.path.exists('uploads'):
            print("✅ Uploads directory exists")
        else:
            print("❌ Uploads directory does not exist!")
            return False
            
        if os.path.exists('uploads/admission_photos'):
            print("✅ Admission photos directory exists")
        else:
            print("❌ Admission photos directory does not exist!")
            return False
        
        conn.close()
        print("\n✅ Database test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    test_database()