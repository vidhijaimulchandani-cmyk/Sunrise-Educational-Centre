import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    dob TEXT NOT NULL,
    student_phone TEXT NOT NULL,
    student_email TEXT NOT NULL,
    class TEXT NOT NULL,
    school_name TEXT NOT NULL,
    maths_marks INTEGER NOT NULL,
    maths_rating REAL NOT NULL,
    last_percentage REAL NOT NULL,
    parent_name TEXT NOT NULL,
    parent_phone TEXT NOT NULL,
    passport_photo TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    submit_ip TEXT,
    approved_at TEXT,
    approved_by TEXT,
    disapproved_at TEXT,
    disapproved_by TEXT,
    disapproval_reason TEXT
)
''')

print("'admissions' table created or already exists with all required columns.")
conn.commit()
conn.close() 