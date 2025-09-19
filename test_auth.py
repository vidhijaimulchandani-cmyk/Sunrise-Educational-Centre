#!/usr/bin/env python3
"""
Test script to check authentication system
"""

import sqlite3
from auth_handler import authenticate_user, get_all_classes, get_user_by_username

def test_authentication():
    print("🔍 Testing Authentication System")
    print("=" * 50)
    
    # Check if database exists and has users
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get all users
        c.execute('SELECT username, password, class_id FROM users LIMIT 10')
        users = c.fetchall()
        
        print(f"📊 Found {len(users)} users in database:")
        for user in users:
            print(f"  - Username: {user[0]}, Password: {user[1]}, Class ID: {user[2]}")
        
        # Get all classes
        classes = get_all_classes()
        print(f"\n📚 Available classes:")
        for class_id, class_name in classes:
            print(f"  - ID: {class_id}, Name: {class_name}")
        
        conn.close()
        
        # Test authentication with default admin user
        print(f"\n🔐 Testing authentication with default admin user:")
        print(f"  Username: yash")
        print(f"  Password: yash")
        
        result = authenticate_user('yash', 'yash')
        if result:
            user_id, user_role = result
            print(f"  ✅ Authentication successful!")
            print(f"  User ID: {user_id}")
            print(f"  User Role: {user_role}")
        else:
            print(f"  ❌ Authentication failed!")
            
        # Test with wrong credentials
        print(f"\n🔐 Testing with wrong credentials:")
        result = authenticate_user('wrong_user', 'wrong_pass')
        if result:
            print(f"  ❌ This should not succeed!")
        else:
            print(f"  ✅ Correctly rejected wrong credentials")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_authentication()