#!/usr/bin/env python3
"""
Enhanced Live Class Management System
"""

import sqlite3
from datetime import datetime, timedelta
import secrets
import os

def enhance_live_class_system():
    """Enhance the live class system with better features"""
    print("🚀 Enhancing Live Class Management System...")
    print("=" * 60)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # 1. Add enhanced status tracking
        print("\n📋 Step 1: Adding enhanced status tracking...")
        
        # Add new status types if they don't exist
        c.execute("""
            UPDATE live_classes 
            SET status = 'scheduled' 
            WHERE status IS NULL OR status = ''
        """)
        
        # Add duration tracking
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN duration_minutes INTEGER DEFAULT 60")
            print("  ✅ Added duration tracking")
        except sqlite3.OperationalError:
            print("  ℹ️  Duration tracking already exists")
        
        # Add host information
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN host_user_id INTEGER")
            print("  ✅ Added host tracking")
        except sqlite3.OperationalError:
            print("  ℹ️  Host tracking already exists")
        
        # Add attendance tracking
        try:
            c.execute("ALTER TABLE live_classes ADD COLUMN attendance_count INTEGER DEFAULT 0")
            print("  ✅ Added attendance tracking")
        except sqlite3.OperationalError:
            print("  ℹ️  Attendance tracking already exists")
        
        # 2. Create attendance tracking table
        print("\n📋 Step 2: Creating attendance tracking...")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                left_at TEXT,
                duration_minutes INTEGER DEFAULT 0,
                FOREIGN KEY (class_id) REFERENCES live_classes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(class_id, user_id)
            )
        ''')
        print("  ✅ Created attendance tracking table")
        
        # 3. Create live class messages table (if not exists)
        print("\n📋 Step 3: Setting up messaging system...")
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS live_class_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'chat',
                created_at TEXT NOT NULL,
                FOREIGN KEY (class_id) REFERENCES live_classes(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("  ✅ Created live class messages table")
        
        # 4. Add indexes for better performance
        print("\n📋 Step 4: Adding database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_live_classes_status ON live_classes(status)",
            "CREATE INDEX IF NOT EXISTS idx_live_classes_scheduled_time ON live_classes(scheduled_time)",
            "CREATE INDEX IF NOT EXISTS idx_live_classes_is_active ON live_classes(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_class_id ON live_class_attendance(class_id)",
            "CREATE INDEX IF NOT EXISTS idx_attendance_user_id ON live_class_attendance(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_class_id ON live_class_messages(class_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON live_class_messages(created_at)"
        ]
        
        for index_sql in indexes:
            try:
                c.execute(index_sql)
            except sqlite3.OperationalError:
                pass
        
        print("  ✅ Added performance indexes")
        
        # 5. Update existing classes with better data
        print("\n📋 Step 5: Updating existing classes...")
        
        # Set default duration for existing classes
        c.execute("""
            UPDATE live_classes 
            SET duration_minutes = 60 
            WHERE duration_minutes IS NULL
        """)
        
        # Update status for better consistency
        c.execute("""
            UPDATE live_classes 
            SET status = CASE 
                WHEN is_active = 1 THEN 'active'
                WHEN status = 'completed' THEN 'completed'
                WHEN status = 'cancelled' THEN 'cancelled'
                ELSE 'scheduled'
            END
        """)
        
        print("  ✅ Updated existing classes")
        
        # 6. Create helper functions
        print("\n📋 Step 6: Creating helper functions...")
        
        # Add these functions to auth_handler.py
        helper_functions = '''
# Enhanced Live Class Functions
def get_live_class_with_attendance(class_id):
    """Get live class details with attendance count"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT lc.*, COUNT(lca.id) as attendance_count
        FROM live_classes lc
        LEFT JOIN live_class_attendance lca ON lc.id = lca.class_id
        WHERE lc.id = ?
        GROUP BY lc.id
    ''', (class_id,))
    result = c.fetchone()
    conn.close()
    return result

def record_attendance(class_id, user_id, username, action='join'):
    """Record user attendance in live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().isoformat()
    
    if action == 'join':
        try:
            c.execute('''
                INSERT INTO live_class_attendance (class_id, user_id, username, joined_at)
                VALUES (?, ?, ?, ?)
            ''', (class_id, user_id, username, now))
            # Update attendance count
            c.execute('''
                UPDATE live_classes 
                SET attendance_count = attendance_count + 1 
                WHERE id = ?
            ''', (class_id,))
        except sqlite3.IntegrityError:
            # User already joined, update join time
            c.execute('''
                UPDATE live_class_attendance 
                SET joined_at = ? 
                WHERE class_id = ? AND user_id = ?
            ''', (now, class_id, user_id))
    elif action == 'leave':
        c.execute('''
            UPDATE live_class_attendance 
            SET left_at = ?, 
                duration_minutes = ROUND((julianday(?) - julianday(joined_at)) * 24 * 60)
            WHERE class_id = ? AND user_id = ? AND left_at IS NULL
        ''', (now, now, class_id, user_id))
    
    conn.commit()
    conn.close()

def get_class_attendance(class_id):
    """Get attendance list for a class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, joined_at, left_at, duration_minutes
        FROM live_class_attendance
        WHERE class_id = ?
        ORDER BY joined_at
    ''', (class_id,))
    attendance = c.fetchall()
    conn.close()
    return attendance

def save_live_class_message(class_id, user_id, username, message, message_type='chat'):
    """Save a message from live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO live_class_messages (class_id, user_id, username, message, message_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (class_id, user_id, username, message, message_type, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_live_class_messages(class_id, limit=50):
    """Get recent messages from live class"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT username, message, message_type, created_at
        FROM live_class_messages
        WHERE class_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (class_id, limit))
    messages = c.fetchall()
    conn.close()
    return messages[::-1]  # Return in chronological order

def update_live_class_status(class_id, status, host_user_id=None):
    """Update live class status"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    if host_user_id:
        c.execute('''
            UPDATE live_classes 
            SET status = ?, is_active = ?, host_user_id = ?
            WHERE id = ?
        ''', (status, 1 if status == 'active' else 0, host_user_id, class_id))
    else:
        c.execute('''
            UPDATE live_classes 
            SET status = ?, is_active = ?
            WHERE id = ?
        ''', (status, 1 if status == 'active' else 0, class_id))
    
    conn.commit()
    conn.close()

def get_live_class_analytics():
    """Get analytics for live classes"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Total classes by status
    c.execute('''
        SELECT status, COUNT(*) as count
        FROM live_classes
        GROUP BY status
    ''')
    status_counts = c.fetchall()
    
    # Total attendance
    c.execute('SELECT COUNT(*) FROM live_class_attendance')
    total_attendance = c.fetchone()[0]
    
    # Average attendance per class
    c.execute('''
        SELECT AVG(attendance_count) 
        FROM live_classes 
        WHERE status = 'completed'
    ''')
    avg_attendance = c.fetchone()[0] or 0
    
    # Recent activity
    c.execute('''
        SELECT COUNT(*) 
        FROM live_classes 
        WHERE created_at >= datetime('now', '-7 days')
    ''')
    recent_classes = c.fetchone()[0]
    
    conn.close()
    
    return {
        'status_counts': status_counts,
        'total_attendance': total_attendance,
        'avg_attendance': round(avg_attendance, 1),
        'recent_classes': recent_classes
    }
'''
        
        # Write helper functions to a file
        with open('live_class_helpers.py', 'w') as f:
            f.write(helper_functions)
        
        print("  ✅ Created helper functions")
        
        # 7. Test the enhanced system
        print("\n📋 Step 7: Testing enhanced system...")
        
        # Create a test class
        test_class_code = ''.join(secrets.choice('0123456789') for i in range(6))
        test_pin = ''.join(secrets.choice('0123456789') for i in range(4))
        test_meeting_url = "/test-video.mp4"
        test_topic = "Enhanced System Test"
        test_description = "Testing the enhanced live class system"
        
        c.execute('''
            INSERT INTO live_classes (class_code, pin, meeting_url, topic, description, status, duration_minutes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (test_class_code, test_pin, test_meeting_url, test_topic, test_description, 'scheduled', 90, datetime.now().isoformat()))
        
        test_class_id = c.lastrowid
        print(f"  ✅ Created test class with ID: {test_class_id}")
        
        # Test attendance recording
        c.execute('''
            INSERT INTO live_class_attendance (class_id, user_id, username, joined_at)
            VALUES (?, ?, ?, ?)
        ''', (test_class_id, 1, 'test_user', datetime.now().isoformat()))
        
        print("  ✅ Tested attendance recording")
        
        # Clean up test data
        c.execute("DELETE FROM live_class_attendance WHERE class_id = ?", (test_class_id,))
        c.execute("DELETE FROM live_classes WHERE id = ?", (test_class_id,))
        
        # Commit all changes
        conn.commit()
        print("\n✅ Enhanced live class system successfully!")
        
    except Exception as e:
        print(f"❌ Error enhancing live class system: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def create_live_class_dashboard():
    """Create an enhanced live class dashboard"""
    print("\n📊 Creating Enhanced Live Class Dashboard...")
    
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Live Class Dashboard</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    <link rel="stylesheet" href="style.css">
    <style>
        .dashboard-container { max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(100,100,255,0.08); border: 1px solid #e0e7ff; }
        .stat-number { font-size: 2.5rem; font-weight: 700; color: #6a82fb; margin-bottom: 0.5rem; }
        .stat-label { color: #666; font-size: 1rem; }
        .chart-container { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(100,100,255,0.08); margin-bottom: 2rem; }
        .recent-activity { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(100,100,255,0.08); }
        .activity-item { display: flex; align-items: center; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid #eee; }
        .activity-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
        .activity-content { flex: 1; }
        .activity-time { color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h1>📊 Live Class Analytics Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="totalClasses">-</div>
                <div class="stat-label">Total Classes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="activeClasses">-</div>
                <div class="stat-label">Active Classes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalAttendance">-</div>
                <div class="stat-label">Total Attendance</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avgAttendance">-</div>
                <div class="stat-label">Avg. Attendance</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>Class Status Distribution</h3>
            <canvas id="statusChart" width="400" height="200"></canvas>
        </div>
        
        <div class="recent-activity">
            <h3>Recent Activity</h3>
            <div id="activityList">
                <div class="activity-item">
                    <div class="activity-icon" style="background: #e3f2fd; color: #1976d2;">📊</div>
                    <div class="activity-content">
                        <div>Loading recent activity...</div>
                        <div class="activity-time">Just now</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load dashboard data
        async function loadDashboard() {
            try {
                const response = await fetch('/api/live-classes/analytics');
                const data = await response.json();
                
                document.getElementById('totalClasses').textContent = data.total_classes || 0;
                document.getElementById('activeClasses').textContent = data.active_classes || 0;
                document.getElementById('totalAttendance').textContent = data.total_attendance || 0;
                document.getElementById('avgAttendance').textContent = data.avg_attendance || 0;
                
                // Update activity list
                const activityList = document.getElementById('activityList');
                if (data.recent_activity && data.recent_activity.length > 0) {
                    activityList.innerHTML = data.recent_activity.map(activity => `
                        <div class="activity-item">
                            <div class="activity-icon" style="background: ${activity.color}; color: ${activity.textColor};">${activity.icon}</div>
                            <div class="activity-content">
                                <div>${activity.message}</div>
                                <div class="activity-time">${activity.time}</div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    activityList.innerHTML = '<div class="activity-item"><div>No recent activity</div></div>';
                }
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', loadDashboard);
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
'''
    
    with open('live_class_dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    print("✅ Created enhanced dashboard")

if __name__ == '__main__':
    enhance_live_class_system()
    create_live_class_dashboard()
    
    print("\n" + "=" * 60)
    print("✅ Live Class Enhancement Complete!")
    print("\nNew Features Added:")
    print("• Enhanced status tracking")
    print("• Attendance recording system")
    print("• Live messaging system")
    print("• Performance optimizations")
    print("• Analytics dashboard")
    print("• Helper functions for better management")
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Import the helper functions in auth_handler.py")
    print("3. Test the new attendance tracking")
    print("4. Check the enhanced dashboard")
    print("5. Verify live class status management") 