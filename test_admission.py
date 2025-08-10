#!/usr/bin/env python3
import sqlite3
import os

def test_admission_system():
    print("Testing admission system...")
    
    # Check if database exists
    if not os.path.exists('users.db'):
        print("❌ users.db not found!")
        return False
    
    # Check database connection
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check admissions table structure
    try:
        c.execute("PRAGMA table_info(admissions)")
        columns = c.fetchall()
        print(f"✅ Admissions table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    except Exception as e:
        print(f"❌ Error checking admissions table: {e}")
        return False
    
    # Check if required columns exist
    required_columns = [
        'user_id', 'submit_ip', 'approved_at', 'approved_by', 
        'disapproved_at', 'disapproved_by', 'disapproval_reason'
    ]
    
    existing_columns = [col[1] for col in columns]
    missing_columns = [col for col in required_columns if col not in existing_columns]
    
    if missing_columns:
        print(f"⚠️  Missing columns: {missing_columns}")
        print("Adding missing columns...")
        
        for col in missing_columns:
            try:
                c.execute(f'ALTER TABLE admissions ADD COLUMN {col} TEXT')
                print(f"  ✅ Added column: {col}")
            except Exception as e:
                print(f"  ❌ Error adding {col}: {e}")
        
        conn.commit()
        print("✅ Database schema updated")
    else:
        print("✅ All required columns exist")
    
    # Check admission_access table
    try:
        c.execute("PRAGMA table_info(admission_access)")
        access_columns = c.fetchall()
        print(f"✅ Admission access table has {len(access_columns)} columns")
    except Exception as e:
        print(f"❌ Admission access table error: {e}")
        print("Creating admission_access table...")
        
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS admission_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_id INTEGER NOT NULL,
                access_username TEXT UNIQUE NOT NULL,
                access_password TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            conn.commit()
            print("✅ Admission access table created")
        except Exception as e2:
            print(f"❌ Error creating table: {e2}")
    
    # Check uploads directory
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads directory")
    
    if not os.path.exists('uploads/admission_photos'):
        os.makedirs('uploads/admission_photos')
        print("✅ Created admission_photos directory")
    
    conn.close()
    print("\n✅ Admission system test completed!")
    return True

if __name__ == "__main__":
    test_admission_system()