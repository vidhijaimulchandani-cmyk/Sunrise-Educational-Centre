#!/usr/bin/env python3
"""
Daily reset script to clear completed classes at 12 AM
This script should be run as a cron job or scheduled task
"""

import sqlite3
import os
from datetime import datetime, timedelta
import time

DATABASE = 'users.db'

def daily_reset():
    """Reset completed classes and related data daily at 12 AM"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Get current time
        now = datetime.now()
        
        # Check if it's time for daily reset (12 AM)
        if now.hour == 0 and now.minute < 5:  # Reset window: 12:00 AM to 12:05 AM
            
            print(f"🔄 Starting daily reset at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clear completed live classes older than 1 day
            yesterday = (now - timedelta(days=1)).isoformat()
            cursor.execute('''
                DELETE FROM live_classes 
                WHERE status = 'completed' AND ended_at < ?
            ''', (yesterday,))
            
            completed_classes_deleted = cursor.rowcount
            
            # Clear old benchmark sections for completed classes
            cursor.execute('''
                DELETE FROM benchmark_sections 
                WHERE class_id IN (
                    SELECT id FROM live_classes 
                    WHERE status = 'completed' AND ended_at < ?
                )
            ''', (yesterday,))
            
            sections_deleted = cursor.rowcount
            
            # Clear old chat messages for completed classes
            cursor.execute('''
                DELETE FROM chat_messages 
                WHERE class_id IN (
                    SELECT id FROM live_classes 
                    WHERE status = 'completed' AND ended_at < ?
                )
            ''', (yesterday,))
            
            messages_deleted = cursor.rowcount
            
            # Clear old recordings data
            cursor.execute('''
                DELETE FROM recordings 
                WHERE class_id IN (
                    SELECT id FROM live_classes 
                    WHERE status = 'completed' AND ended_at < ?
                )
            ''', (yesterday,))
            
            recordings_deleted = cursor.rowcount
            
            # Commit changes
            conn.commit()
            
            print(f"✅ Daily reset completed successfully!")
            print(f"   - Completed classes deleted: {completed_classes_deleted}")
            print(f"   - Benchmark sections deleted: {sections_deleted}")
            print(f"   - Chat messages deleted: {messages_deleted}")
            print(f"   - Recordings deleted: {recordings_deleted}")
            
            # Update last reset timestamp
            cursor.execute('''
                INSERT OR REPLACE INTO system_settings (key, value, updated_at)
                VALUES ('last_daily_reset', ?, ?)
            ''', (now.isoformat(), now.isoformat()))
            
            conn.commit()
            
        else:
            print(f"⏰ Not time for daily reset. Current time: {now.strftime('%H:%M')}")
            print(f"   Daily reset runs at 12:00 AM")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during daily reset: {e}")

def create_system_settings_table():
    """Create system_settings table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ System settings table created/verified")
        
    except Exception as e:
        print(f"❌ Error creating system settings table: {e}")

def run_continuous_reset():
    """Run the reset check continuously (for testing)"""
    print("🔄 Starting continuous daily reset monitoring...")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            daily_reset()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("\n🛑 Daily reset monitoring stopped")

if __name__ == "__main__":
    # Create system settings table
    create_system_settings_table()
    
    # Check if running in continuous mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        run_continuous_reset()
    else:
        # Run once
        daily_reset()