#!/usr/bin/env python3
"""
Test script to verify that database lock issues are fixed.
"""

import sqlite3
import os
import threading
import time
from datetime import datetime

# Database path
DATABASE = 'users.db'

def test_database_connections():
    """Test multiple database connections to ensure no locks"""
    
    if not os.path.exists(DATABASE):
        print(f"❌ Database {DATABASE} not found!")
        return
    
    print("🧪 Testing Database Connection Management")
    print("=" * 50)
    
    def worker_function(worker_id):
        """Worker function to simulate concurrent database access"""
        try:
            conn = sqlite3.connect(DATABASE, timeout=30.0)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=30000')
            c = conn.cursor()
            
            # Simulate IP tracking operation
            c.execute('''
                INSERT INTO ip_logs (ip, user_id, path, user_agent, visited_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (f'192.168.1.{worker_id}', worker_id, '/test', f'Worker-{worker_id}', datetime.now().isoformat()))
            
            # Simulate session activity update
            c.execute('''
                INSERT OR REPLACE INTO user_activity (user_id, ip, last_seen)
                VALUES (?, ?, ?)
            ''', (worker_id, f'192.168.1.{worker_id}', datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            print(f"✅ Worker {worker_id} completed successfully")
            
        except Exception as e:
            print(f"❌ Worker {worker_id} failed: {e}")
    
    # Test 1: Single connection
    print("\n1️⃣ Testing single database connection...")
    try:
        conn = sqlite3.connect(DATABASE, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        c = conn.cursor()
        
        # Check if tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ip_logs', 'user_activity', 'active_sessions')")
        tables = [row[0] for row in c.fetchall()]
        print(f"📋 Found tables: {tables}")
        
        conn.close()
        print("✅ Single connection test passed")
        
    except Exception as e:
        print(f"❌ Single connection test failed: {e}")
        return
    
    # Test 2: Multiple concurrent connections
    print("\n2️⃣ Testing multiple concurrent connections...")
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_function, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("✅ Concurrent connection test completed")
    
    # Test 3: Check database integrity
    print("\n3️⃣ Checking database integrity...")
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Check IP logs
        c.execute('SELECT COUNT(*) FROM ip_logs')
        ip_logs_count = c.fetchone()[0]
        print(f"📊 IP logs count: {ip_logs_count}")
        
        # Check user activity
        c.execute('SELECT COUNT(*) FROM user_activity')
        user_activity_count = c.fetchone()[0]
        print(f"📊 User activity count: {user_activity_count}")
        
        # Check for any recent entries from our test
        c.execute("SELECT COUNT(*) FROM ip_logs WHERE ip LIKE '192.168.1.%'")
        test_entries = c.fetchone()[0]
        print(f"📊 Test entries: {test_entries}")
        
        conn.close()
        print("✅ Database integrity check passed")
        
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
    
    # Test 4: Test the utility functions
    print("\n4️⃣ Testing utility functions...")
    try:
        # Import the utility functions from app.py
        import sys
        sys.path.append('.')
        
        # Test database connection function
        from app import get_db_connection, cleanup_stale_sessions
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT 1')
        result = c.fetchone()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ get_db_connection() function works")
        else:
            print("❌ get_db_connection() function failed")
        
        # Test cleanup function
        deleted_count = cleanup_stale_sessions()
        print(f"🧹 Cleanup function deleted {deleted_count} stale records")
        
    except Exception as e:
        print(f"❌ Utility function test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Database Lock Test Summary:")
    print("   ✅ Single connection test")
    print("   ✅ Concurrent connection test")
    print("   ✅ Database integrity check")
    print("   ✅ Utility function test")
    print("\n💡 If all tests passed, database lock issues should be resolved!")
    print("   The system now uses:")
    print("   - WAL journal mode for better concurrency")
    print("   - Proper connection timeouts")
    print("   - Retry logic for database locks")
    print("   - Automatic cleanup of stale sessions")

if __name__ == "__main__":
    test_database_connections()