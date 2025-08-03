import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Add user_id column to existing admissions table if it doesn't exist
try:
    c.execute('ALTER TABLE admissions ADD COLUMN user_id INTEGER')
    print("Added user_id column to admissions table.")
except sqlite3.OperationalError:
    print("user_id column already exists in admissions table.")

# Create approved_admissions table
c.execute('''
CREATE TABLE IF NOT EXISTS approved_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_admission_id INTEGER,
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
    user_id INTEGER,
    approved_by TEXT,
    approved_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_admission_id) REFERENCES admissions (id)
)
''')

# Create disapproved_admissions table
c.execute('''
CREATE TABLE IF NOT EXISTS disapproved_admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_admission_id INTEGER,
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
    user_id INTEGER,
    disapproved_by TEXT,
    disapproval_reason TEXT,
    disapproved_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (original_admission_id) REFERENCES admissions (id)
)
''')

print("'approved_admissions' table created or already exists.")
print("'disapproved_admissions' table created or already exists.")

conn.commit()
conn.close() 