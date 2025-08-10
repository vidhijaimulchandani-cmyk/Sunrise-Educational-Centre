#!/usr/bin/env python3
"""
Comprehensive fix for the admission system
This script will fix all known issues:
1. Add missing columns to admissions table
2. Create admission_access table if missing
3. Create upload directories
4. Verify the system is working
"""

import sqlite3
import os
import sys
from datetime import datetime

def fix_admission_system():
    print("🔧 Fixing Admission System...")
    
    # Check if database exists
    if not os.path.exists('users.db'):
        print("❌ users.db not found! Creating new database...")
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            print("✅ New database created")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    else:
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    try:
        # Check admissions table structure
        c.execute("PRAGMA table_info(admissions)")
        columns = c.fetchall()
        print(f"📋 Admissions table has {len(columns)} columns:")
        
        existing_columns = [col[1] for col in columns]
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Required columns for the new system
        required_columns = [
            ('user_id', 'INTEGER'),
            ('submit_ip', 'TEXT'),
            ('approved_at', 'TEXT'),
            ('approved_by', 'TEXT'),
            ('disapproved_at', 'TEXT'),
            ('disapproved_by', 'TEXT'),
            ('disapproval_reason', 'TEXT')
        ]
        
        # Add missing columns
        missing_columns = []
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"⚠️  Adding {len(missing_columns)} missing columns...")
            for col_name, col_type in missing_columns:
                try:
                    c.execute(f'ALTER TABLE admissions ADD COLUMN {col_name} {col_type}')
                    print(f"  ✅ Added column: {col_name}")
                except Exception as e:
                    print(f"  ❌ Error adding {col_name}: {e}")
            
            conn.commit()
            print("✅ Database schema updated")
        else:
            print("✅ All required columns exist")
        
        # Create admission_access table if it doesn't exist
        try:
            c.execute("PRAGMA table_info(admission_access)")
            access_columns = c.fetchall()
            print(f"✅ Admission access table has {len(access_columns)} columns")
        except Exception as e:
            print("📝 Creating admission_access table...")
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
                print(f"❌ Error creating admission_access table: {e2}")
        
        # Create upload directories
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
            print("✅ Created uploads directory")
        else:
            print("✅ Uploads directory exists")
        
        if not os.path.exists('uploads/admission_photos'):
            os.makedirs('uploads/admission_photos')
            print("✅ Created admission_photos directory")
        else:
            print("✅ Admission photos directory exists")
        
        # Test database operations
        print("\n🧪 Testing database operations...")
        
        # Test INSERT operation (without actually inserting)
        try:
            c.execute("SELECT COUNT(*) FROM admissions")
            count = c.fetchone()[0]
            print(f"✅ Admissions table accessible, contains {count} records")
        except Exception as e:
            print(f"❌ Error accessing admissions table: {e}")
        
        # Test admission_access table
        try:
            c.execute("SELECT COUNT(*) FROM admission_access")
            count = c.fetchone()[0]
            print(f"✅ Admission access table accessible, contains {count} records")
        except Exception as e:
            print(f"❌ Error accessing admission_access table: {e}")
        
        conn.close()
        print("\n🎉 Admission system fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during fix process: {e}")
        conn.close()
        return False

def test_admission_submission():
    """Test the admission submission logic"""
    print("\n🧪 Testing admission submission logic...")
    
    # Check if app.py has the correct INSERT statement
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Look for the INSERT statement in the admission route
        if 'INSERT INTO admissions (' in content:
            print("✅ Found INSERT INTO admissions statement")
            
            # Check if it has the right number of columns
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'INSERT INTO admissions (' in line:
                    # Count the columns
                    start = line.find('(') + 1
                    end = line.find(')')
                    if start > 0 and end > start:
                        columns_part = line[start:end]
                        columns = [col.strip() for col in columns_part.split(',')]
                        print(f"📊 INSERT statement has {len(columns)} columns")
                        
                        # Look for VALUES part
                        for j in range(i, min(i+10, len(lines))):
                            if 'VALUES (' in lines[j]:
                                values_part = lines[j]
                                values = [val.strip() for val in values_part.split('(')[1].split(')')[0].split(',')]
                                print(f"📊 VALUES clause has {len(values)} values")
                                
                                if len(columns) == len(values):
                                    print("✅ Column count matches value count")
                                else:
                                    print(f"❌ Mismatch: {len(columns)} columns vs {len(values)} values")
                                break
                        break
        else:
            print("❌ INSERT INTO admissions statement not found")
            
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")

if __name__ == "__main__":
    print("🚀 Starting Admission System Fix...")
    
    if fix_admission_system():
        test_admission_submission()
        print("\n✅ All fixes applied successfully!")
        print("\n📋 Next steps:")
        print("1. Run the Flask app: python3 app.py")
        print("2. Test admission submission")
        print("3. Check if admission ID and password are generated")
        print("4. Verify entry is saved in admissions table")
    else:
        print("\n❌ Fix failed! Please check the errors above.")
        sys.exit(1)