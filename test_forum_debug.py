#!/usr/bin/env python3

import requests
import json

# Test forum functionality
def test_forum():
    base_url = "http://localhost:10000"
    
    # Test 1: Check if forum page loads
    print("=== Testing Forum Page ===")
    try:
        response = requests.get(f"{base_url}/forum")
        print(f"Forum page status: {response.status_code}")
        if response.status_code == 302:
            print("Redirected to login - this is expected if not logged in")
        elif response.status_code == 200:
            print("Forum page loaded successfully")
    except Exception as e:
        print(f"Error accessing forum page: {e}")
    
    # Test 2: Check API endpoint
    print("\n=== Testing API Endpoint ===")
    try:
        response = requests.get(f"{base_url}/api/forum/messages")
        print(f"API status: {response.status_code}")
        if response.status_code == 401:
            print("Unauthorized - user needs to login")
        elif response.status_code == 200:
            data = response.json()
            print(f"API returned {len(data)} messages")
        else:
            print(f"Unexpected response: {response.text[:200]}")
    except Exception as e:
        print(f"Error accessing API: {e}")
    
    # Test 3: Check database directly
    print("\n=== Testing Database ===")
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check topics
    c.execute("SELECT id, name FROM forum_topics ORDER BY id")
    topics = c.fetchall()
    print(f"Available topics: {topics}")
    
    # Check messages in topic 5
    c.execute("SELECT COUNT(*) FROM forum_messages WHERE topic_id = 5")
    count = c.fetchone()[0]
    print(f"Messages in topic 5 (General Discussion): {count}")
    
    # Check user access
    c.execute("SELECT username, role, paid FROM users WHERE username = 'raj'")
    user = c.fetchone()
    if user:
        print(f"User 'raj': role={user[1]}, paid={user[2]}")
    
    conn.close()

if __name__ == "__main__":
    test_forum() 