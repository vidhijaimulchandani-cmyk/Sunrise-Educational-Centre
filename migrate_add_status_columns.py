import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

print("Adding status columns to notifications and live_classes tables...")

# Add status column to notifications table
try:
    c.execute("ALTER TABLE notifications ADD COLUMN status TEXT DEFAULT 'active'")
    print("✓ Added 'status' column to notifications table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'status' column already exists in notifications table")
    else:
        print(f"Error adding status column to notifications: {e}")

# Add status column to live_classes table
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN status TEXT DEFAULT 'scheduled'")
    print("✓ Added 'status' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'status' column already exists in live_classes table")
    else:
        print(f"Error adding status column to live_classes: {e}")

# Add scheduled_time column to live_classes table for better scheduling
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN scheduled_time TEXT")
    print("✓ Added 'scheduled_time' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'scheduled_time' column already exists in live_classes table")
    else:
        print(f"Error adding scheduled_time column to live_classes: {e}")

# Add target_class column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN target_class TEXT DEFAULT 'all'")
    print("✓ Added 'target_class' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'target_class' column already exists in live_classes table")
    else:
        print(f"Error adding target_class column to live_classes: {e}")

# Add class_stream column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN class_stream TEXT")
    print("✓ Added 'class_stream' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'class_stream' column already exists in live_classes table")
    else:
        print(f"Error adding class_stream column to live_classes: {e}")

# Add class_type column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN class_type TEXT DEFAULT 'lecture'")
    print("✓ Added 'class_type' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'class_type' column already exists in live_classes table")
    else:
        print(f"Error adding class_type column to live_classes: {e}")

# Add paid_status column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN paid_status TEXT DEFAULT 'unpaid'")
    print("✓ Added 'paid_status' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'paid_status' column already exists in live_classes table")
    else:
        print(f"Error adding paid_status column to live_classes: {e}")

# Add subject column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN subject TEXT")
    print("✓ Added 'subject' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'subject' column already exists in live_classes table")
    else:
        print(f"Error adding subject column to live_classes: {e}")

# Add teacher_name column
try:
    c.execute("ALTER TABLE live_classes ADD COLUMN teacher_name TEXT")
    print("✓ Added 'teacher_name' column to live_classes table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'teacher_name' column already exists in live_classes table")
    else:
        print(f"Error adding teacher_name column to live_classes: {e}")

# Add scheduled_time column to notifications table for scheduled notifications
try:
    c.execute("ALTER TABLE notifications ADD COLUMN scheduled_time TEXT")
    print("✓ Added 'scheduled_time' column to notifications table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'scheduled_time' column already exists in notifications table")
    else:
        print(f"Error adding scheduled_time column to notifications: {e}")

# Add notification_type column to distinguish between live class and study resource notifications
try:
    c.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'general'")
    print("✓ Added 'notification_type' column to notifications table")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e):
        print("✓ 'notification_type' column already exists in notifications table")
    else:
        print(f"Error adding notification_type column to notifications: {e}")

conn.commit()
conn.close()

print("\nMigration completed successfully!")
print("\nStatus values for notifications:")
print("- 'active': Currently active notification")
print("- 'scheduled': Scheduled for future")
print("- 'completed': Completed/expired")
print("- 'cancelled': Cancelled")

print("\nStatus values for live_classes:")
print("- 'scheduled': Scheduled for future")
print("- 'active': Currently running")
print("- 'completed': Class completed")
print("- 'cancelled': Class cancelled")

print("\nNotification types:")
print("- 'general': General notification")
print("- 'live_class': Live class related")
print("- 'study_resource': Study resource related") 