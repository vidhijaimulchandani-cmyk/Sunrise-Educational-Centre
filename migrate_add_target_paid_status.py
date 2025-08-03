import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check if the column already exists
c.execute("PRAGMA table_info(notifications)")
columns = [row[1] for row in c.fetchall()]

if 'target_paid_status' not in columns:
    c.execute("ALTER TABLE notifications ADD COLUMN target_paid_status TEXT DEFAULT 'all'")
    print("Column 'target_paid_status' added to notifications table.")
else:
    print("Column 'target_paid_status' already exists.")

conn.commit()
conn.close() 