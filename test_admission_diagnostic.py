#!/usr/bin/env python3
"""
Admission System Diagnostic Script
This script will test the admission system and identify any issues
"""

import sqlite3
import os
import sys
from datetime import datetime

# Database path
DATABASE = 'users.db'

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        conn = sqlite3.connect(DATABASE)
        print("✅ Database connection successful")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_database_file():
    """Check if database file exists and is accessible"""
    print("\n🔍 Checking database file...")
    if os.path.exists(DATABASE):
        size = os.path.getsize(DATABASE)
        print(f"✅ Database file exists, size: {size} bytes")
        return True
    else:
        print("❌ Database file does not exist")
        return False

def check_admissions_table():
    """Check admissions table structure"""
    print("\n🔍 Checking admissions table...")
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if c.fetchone():
            print("✅ Admissions table exists")
            
            # Check table structure
            c.execute("PRAGMA table_info(admissions)")
            columns = c.fetchall()
            print(f"📋 Table has {len(columns)} columns:")
            
            required_columns = [
                'id', 'student_name', 'dob', 'student_phone', 'student_email',
                'class', 'school_name', 'maths_marks', 'maths_rating', 'last_percentage',
                'parent_name', 'parent_phone', 'passport_photo', 'status', 'submitted_at',
                'user_id', 'submit_ip', 'approved_at', 'approved_by', 'disapproved_at',
                'disapproved_by', 'disapproval_reason'
            ]
            
            existing_columns = [col[1] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
            else:
                print("✅ All required columns present")
                
            # Check row count
            c.execute("SELECT COUNT(*) FROM admissions")
            count = c.fetchone()[0]
            print(f"📊 Table has {count} rows")
            
        else:
            print("❌ Admissions table does not exist")
            
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking admissions table: {e}")
        return False

def check_admission_access_table():
    """Check admission_access table structure"""
    print("\n🔍 Checking admission_access table...")
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if c.fetchone():
            print("✅ Admission access table exists")
            
            # Check table structure
            c.execute("PRAGMA table_info(admission_access)")
            columns = c.fetchall()
            print(f"📋 Table has {len(columns)} columns:")
            
            required_columns = ['id', 'admission_id', 'access_username', 'access_password', 'created_at']
            existing_columns = [col[1] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
            else:
                print("✅ All required columns present")
                
            # Check row count
            c.execute("SELECT COUNT(*) FROM admission_access")
            count = c.fetchone()[0]
            print(f"📊 Table has {count} rows")
            
        else:
            print("❌ Admission access table does not exist")
            
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking admission access table: {e}")
        return False

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking required directories...")
    
    directories = ['uploads', 'uploads/admission_photos']
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")

def test_admission_insertion():
    """Test inserting a sample admission"""
    print("\n🔍 Testing admission insertion...")
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Test data
        test_data = {
            'student_name': 'Test Student',
            'dob': '2000-01-01',
            'student_phone': '1234567890',
            'student_email': 'test@example.com',
            'class': 'class 11 core',
            'school_name': 'Test School',
            'maths_marks': 75,
            'maths_rating': 8.0,
            'last_percentage': 85.5,
            'parent_name': 'Test Parent',
            'parent_phone': '0987654321',
            'passport_photo': 'test_photo.jpg',
            'status': 'pending',
            'submitted_at': datetime.now().isoformat(),
            'user_id': None,
            'submit_ip': '127.0.0.1'
        }
        
        # Insert test admission
        c.execute('''INSERT INTO admissions (
            student_name, dob, student_phone, student_email, class, school_name,
            maths_marks, maths_rating, last_percentage, parent_name, parent_phone,
            passport_photo, status, submitted_at, user_id, submit_ip
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (test_data['student_name'], test_data['dob'], test_data['student_phone'],
         test_data['student_email'], test_data['class'], test_data['school_name'],
         test_data['maths_marks'], test_data['maths_rating'], test_data['last_percentage'],
         test_data['parent_name'], test_data['parent_phone'], test_data['passport_photo'],
         test_data['status'], test_data['submitted_at'], test_data['user_id'],
         test_data['submit_ip']))
        
        admission_id = c.lastrowid
        print(f"✅ Test admission inserted with ID: {admission_id}")
        
        # Test creating access credentials
        import secrets
        import hashlib
        
        access_username = f"admission_{admission_id}"
        access_password = secrets.token_urlsafe(8)
        salt = 'admission_salt_2024'
        hashed_password = hashlib.sha256((access_password + salt).encode()).hexdigest()
        
        c.execute('''INSERT INTO admission_access (
            admission_id, access_username, access_password, created_at
        ) VALUES (?, ?, ?, ?)''', (admission_id, access_username, hashed_password, datetime.now().isoformat()))
        
        print(f"✅ Access credentials created - Username: {access_username}, Password: {access_password}")
        
        # Clean up test data
        c.execute('DELETE FROM admission_access WHERE admission_id = ?', (admission_id,))
        c.execute('DELETE FROM admissions WHERE id = ?', (admission_id,))
        print("✅ Test data cleaned up")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing admission insertion: {e}")
        return False

def check_flask_imports():
    """Check if Flask and required modules can be imported"""
    print("\n🔍 Checking Flask imports...")
    try:
        from flask import Flask, request, session
        print("✅ Flask imported successfully")
        
        # Try to import the app
        import app
        print("✅ App module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Flask import failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🚀 Admission System Diagnostic Tool")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(("Database File", check_database_file()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Admissions Table", check_admissions_table()))
    results.append(("Admission Access Table", check_admission_access_table()))
    results.append(("Directories", check_directories()))
    results.append(("Admission Insertion", test_admission_insertion()))
    results.append(("Flask Imports", check_flask_imports()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The admission system should be working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        
        # Recommendations
        print("\n🔧 RECOMMENDATIONS:")
        if not results[0][1]:  # Database file
            print("- Create the database file or check file permissions")
        if not results[1][1]:  # Database connection
            print("- Check database file integrity and permissions")
        if not results[2][1] or not results[3][1]:  # Tables
            print("- Run the database initialization functions")
        if not results[4][1]:  # Directories
            print("- Create missing directories manually")
        if not results[5][1]:  # Insertion test
            print("- Check table structure and constraints")
        if not results[6][1]:  # Flask imports
            print("- Install missing dependencies or check Python environment")

if __name__ == "__main__":
    main()