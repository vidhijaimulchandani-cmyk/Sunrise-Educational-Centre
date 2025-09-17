import sqlite3
from datetime import datetime, timezone

# Import time configuration for IST
from time_config import get_current_ist_time, format_ist_time, get_ist_timestamp

# Standard database path constant
DATABASE = 'users.db'

def get_connection(timeout_seconds: int = 30):
    return sqlite3.connect(DATABASE, timeout=timeout_seconds)

# ==============================================================================
# Database Initialization and Migration
# ==============================================================================

def init_db():
    init_classes_db()  # Ensure classes table is ready first
    conn = sqlite3.connect(DATABASE)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    c = conn.cursor()

    # --- Schema Definitions ---
    # The 'role' and 'class_role' columns are kept temporarily for migration
    # and will be removed in a future step. New code will use class_id.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT, -- Deprecated, for migration
            paid TEXT NOT NULL DEFAULT 'not paid',
            class_id INTEGER REFERENCES classes(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            class_role TEXT, -- Deprecated, for migration
            filepath TEXT NOT NULL,
            title TEXT,
            description TEXT,
            class_id INTEGER REFERENCES classes(id),
            category TEXT NOT NULL DEFAULT 'uncategorized'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            class_role TEXT, -- Deprecated, for migration
            created_at TEXT NOT NULL,
            class_id INTEGER REFERENCES classes(id),
            target_paid_status TEXT DEFAULT 'all',
            status TEXT DEFAULT 'active',
            scheduled_time TEXT,
            notification_type TEXT DEFAULT 'general'
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_notification_status (
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            seen_at TEXT NOT NULL,
            PRIMARY KEY (user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
        )
    ''')
    # This table is from a previous step, ensuring it's still created.
    c.execute('''
        CREATE TABLE IF NOT EXISTS live_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL UNIQUE,
            pin TEXT NOT NULL,
            meeting_url TEXT NOT NULL,
            topic TEXT,
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            scheduled_time TEXT,
            activated_at TEXT,
            completed_at TEXT,
            recording_url TEXT,
            duration_minutes INTEGER,
            attendance_count INTEGER
        )
    ''')
    # Ensure optional columns for class variations exist
    c.execute("PRAGMA table_info(live_classes)")
    live_class_columns = [row[1] for row in c.fetchall()]
    if 'target_class' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN target_class TEXT DEFAULT 'all'")
    if 'class_stream' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN class_stream TEXT")
    if 'class_type' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN class_type TEXT DEFAULT 'lecture'")
    if 'paid_status' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN paid_status TEXT DEFAULT 'unpaid'")
    if 'subject' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN subject TEXT")
    if 'teacher_name' not in live_class_columns:
        c.execute("ALTER TABLE live_classes ADD COLUMN teacher_name TEXT")
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            parent_id INTEGER,
            topic_id INTEGER,
            media_url TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(parent_id) REFERENCES forum_messages(id),
            FOREIGN KEY(topic_id) REFERENCES forum_topics(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS live_class_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            live_class_id INTEGER NOT NULL,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            media_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(live_class_id) REFERENCES live_classes(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            class_id INTEGER REFERENCES classes(id),
            paid TEXT DEFAULT 'unpaid'
        )
    ''')
    # Forum Polls linked to forum messages
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER UNIQUE NOT NULL,
            question TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(message_id) REFERENCES forum_messages(id) ON DELETE CASCADE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_poll_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            FOREIGN KEY(poll_id) REFERENCES forum_polls(id) ON DELETE CASCADE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            voted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(poll_id, user_id),
            FOREIGN KEY(poll_id) REFERENCES forum_polls(id) ON DELETE CASCADE,
            FOREIGN KEY(option_id) REFERENCES forum_poll_options(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create personal chat tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS personal_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_room_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES chat_rooms(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()

    # --- Data Migration ---
    # Use PRAGMA user_version to ensure this migration runs only once.
    c.execute('PRAGMA user_version')
    db_version = c.fetchone()[0]

    if db_version < 1:
        # Migration V1: From text roles to class_id foreign keys
        try:
            # Add new class_id columns
            c.execute('ALTER TABLE users ADD COLUMN class_id INTEGER REFERENCES classes(id)')
            c.execute('ALTER TABLE resources ADD COLUMN class_id INTEGER REFERENCES classes(id)')
            c.execute('ALTER TABLE notifications ADD COLUMN class_id INTEGER REFERENCES classes(id)')

            # Populate the new columns from the old text-based roles
            c.execute('UPDATE users SET class_id = (SELECT id FROM classes WHERE classes.name = users.role)')
            c.execute('UPDATE resources SET class_id = (SELECT id FROM classes WHERE classes.name = resources.class_role)')
            c.execute('UPDATE notifications SET class_id = (SELECT id FROM classes WHERE classes.name = notifications.class_role)')
            
            # Set the new version
            c.execute('PRAGMA user_version = 1')
            conn.commit()
        except sqlite3.OperationalError as e:
            # This might happen if the script is interrupted. It's safe to ignore "duplicate column" errors.
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 2:
        # Migration V2: Add category to resources
        try:
            c.execute("ALTER TABLE resources ADD COLUMN category TEXT NOT NULL DEFAULT 'uncategorized'")
            c.execute('PRAGMA user_version = 2')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 3:
        # Migration V3: Add paid column to forum_topics
        try:
            c.execute("ALTER TABLE forum_topics ADD COLUMN paid TEXT DEFAULT 'unpaid'")
            c.execute('PRAGMA user_version = 3')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 4:
        # Migration V4: Add missing columns to notifications table and user fields
        try:
            c.execute("ALTER TABLE notifications ADD COLUMN status TEXT DEFAULT 'active'")
            c.execute("ALTER TABLE notifications ADD COLUMN scheduled_time TEXT")
            c.execute("ALTER TABLE notifications ADD COLUMN notification_type TEXT DEFAULT 'general'")
            c.execute("ALTER TABLE users ADD COLUMN mobile_no TEXT")
            c.execute("ALTER TABLE users ADD COLUMN email_address TEXT")
            c.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
            c.execute('PRAGMA user_version = 4')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 5:
        # Migration V5: Add missing columns to forum_messages table
        try:
            c.execute("ALTER TABLE forum_messages ADD COLUMN topic_id INTEGER REFERENCES forum_topics(id)")
            c.execute("ALTER TABLE forum_messages ADD COLUMN media_url TEXT")
            c.execute('PRAGMA user_version = 5')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 6:
        # Migration V6: Add status/time/recording fields to live_classes
        try:
            cols = [r[1] for r in c.execute('PRAGMA table_info(live_classes)').fetchall()]
            def addcol(name, type_sql):
                if name not in cols:
                    c.execute(f"ALTER TABLE live_classes ADD COLUMN {name} {type_sql}")
            addcol('status', "TEXT DEFAULT 'scheduled'")
            addcol('scheduled_time', 'TEXT')
            addcol('activated_at', 'TEXT')
            addcol('completed_at', 'TEXT')
            addcol('recording_url', 'TEXT')
            addcol('duration_minutes', 'INTEGER')
            addcol('attendance_count', 'INTEGER')
            c.execute('PRAGMA user_version = 6')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e

    # Forum polls tables are additive and idempotent; ensure they exist for older versions
    try:
        c.execute('SELECT 1 FROM forum_polls LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('''
            CREATE TABLE IF NOT EXISTS forum_polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER UNIQUE NOT NULL,
                question TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(message_id) REFERENCES forum_messages(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS forum_poll_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                FOREIGN KEY(poll_id) REFERENCES forum_polls(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS forum_poll_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                option_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                voted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(poll_id, user_id),
                FOREIGN KEY(poll_id) REFERENCES forum_polls(id) ON DELETE CASCADE,
                FOREIGN KEY(option_id) REFERENCES forum_poll_options(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
    
    # --- Seed Admin User ---
    # Ensure the default admin user 'yash' exists.
    try:
        c.execute("SELECT id FROM classes WHERE name='admin'")
        admin_class_id = c.fetchone()[0]
        c.execute("SELECT id FROM users WHERE username='yash'")
        if c.fetchone() is None:
            # Admin user does not exist, create it.
            c.execute("INSERT INTO users (username, password, class_id, paid) VALUES (?, ?, ?, ?)",
                      ('yash', 'yash', admin_class_id, 'paid'))
            conn.commit()
    except (sqlite3.OperationalError, TypeError):
        # This might fail if tables are not ready, which is fine.
        # It will succeed on the next run.
        pass

    conn.close()
    # Note: init_resources_db and init_live_class_db are now integrated into init_db

def init_classes_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    # One-time population of the standard classes
    c.execute('SELECT COUNT(*) FROM classes')
    if c.fetchone()[0] == 0:
        classes_to_add = [
            'class 9', 'class 10',
            'class 11 applied', 'class 11 core', 'class 12 applied', 'class 12 core',
            'admin', 'teacher'
        ]
        c.executemany('INSERT INTO classes (name) VALUES (?)', [(c,) for c in classes_to_add])
    conn.commit()
    conn.close()

def ensure_live_class_variant_columns():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(live_classes)")
    cols = [row[1] for row in c.fetchall()]
    if 'target_class' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN target_class TEXT DEFAULT 'all'")
    if 'class_stream' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN class_stream TEXT")
    if 'class_type' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN class_type TEXT DEFAULT 'lecture'")
    if 'paid_status' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN paid_status TEXT DEFAULT 'unpaid'")
    if 'subject' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN subject TEXT")
    if 'teacher_name' not in cols:
        c.execute("ALTER TABLE live_classes ADD COLUMN teacher_name TEXT")
    conn.commit()
    conn.close()

# ==============================================================================
# Helper Functions for Classes
# ==============================================================================

def get_all_classes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name FROM classes')
    classes = c.fetchall()
    conn.close()
    return classes

def get_class_id_by_name(class_name):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # First try exact match
    c.execute('SELECT id FROM classes WHERE name = ?', (class_name,))
    result = c.fetchone()
    
    if not result:
        # Try to map common variations
        class_mappings = {
            '9': 'class 9',
            'class 9': 'class 9',
            'Class 9': 'class 9',
            '10': 'class 10',
            'class 10': 'class 10',
            'Class 10': 'class 10',
            '11': 'class 11 applied',
            '11 applied': 'class 11 applied',
            'class 11 applied': 'class 11 applied',
            'Class 11 Applied': 'class 11 applied',
            '11 core': 'class 11 core',
            'class 11 core': 'class 11 core',
            'Class 11 Core': 'class 11 core',
            '12': 'class 12 applied',
            '12 applied': 'class 12 applied',
            'class 12 applied': 'class 12 applied',
            'Class 12 Applied': 'class 12 applied',
            '12 core': 'class 12 core',
            'class 12 core': 'class 12 core',
            'Class 12 Core': 'class 12 core'
        }
        
        mapped_name = class_mappings.get(class_name.lower())
        if mapped_name:
            c.execute('SELECT id FROM classes WHERE name = ?', (mapped_name,))
            result = c.fetchone()
    
    conn.close()
    return result[0] if result else None

# ==============================================================================
# User Management Functions (Refactored)
# ==============================================================================

def register_user(username, password, class_id, mobile_no=None, email_address=None, paid_status='not paid'):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        # New registrations now use class_id directly with configurable paid status
        c.execute('INSERT INTO users (username, password, class_id, paid, mobile_no, email_address) VALUES (?, ?, ?, ?, ?, ?)', 
                  (username, password, class_id, paid_status, mobile_no, email_address))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Try to authenticate with username, email, or phone number
    c.execute('''
        SELECT u.id, c.name FROM users u
        JOIN classes c ON u.class_id = c.id
        WHERE (u.username=? OR u.email_address=? OR u.mobile_no=?) AND u.password=?
    ''', (username, username, username, password))
    result = c.fetchone()
    conn.close()
    if result:
        return result  # (user_id, class_name)
    return None

def get_user_by_mobile(mobile_no):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.class_id, u.paid, c.name, u.banned, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.mobile_no=?
    ''', (mobile_no,))
    user = c.fetchone()
    conn.close()
    return user

def check_email_or_phone_exists(email_address=None, mobile_no=None):
    """Check if email or phone number already exists in the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if email_address and mobile_no:
        c.execute('SELECT COUNT(*) FROM users WHERE email_address=? OR mobile_no=?', (email_address, mobile_no))
    elif email_address:
        c.execute('SELECT COUNT(*) FROM users WHERE email_address=?', (email_address,))
    elif mobile_no:
        c.execute('SELECT COUNT(*) FROM users WHERE mobile_no=?', (mobile_no,))
    else:
        conn.close()
        return False
    
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def get_all_users():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, c.name, u.paid, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
    ''')
    users = c.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.class_id, u.paid, c.name, u.banned, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.id=?
    ''', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.class_id, u.paid, c.name, u.banned, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.username=?
    ''', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_email(email_address):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.class_id, u.paid, c.name, u.banned, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.email_address=?
    ''', (email_address,))
    user = c.fetchone()
    conn.close()
    return user

def update_user(user_id, username, class_id, paid, banned=None, mobile_no=None, email_address=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if banned is not None:
        c.execute('UPDATE users SET username=?, class_id=?, paid=?, banned=?, mobile_no=?, email_address=? WHERE id=?', 
                  (username, class_id, paid, banned, mobile_no, email_address, user_id))
    else:
        c.execute('UPDATE users SET username=?, class_id=?, paid=?, mobile_no=?, email_address=? WHERE id=?', 
                  (username, class_id, paid, mobile_no, email_address, user_id))
    conn.commit()
    conn.close()

def update_user_with_password(user_id, username, password, class_id, paid, banned=None, mobile_no=None, email_address=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if banned is not None:
        c.execute('UPDATE users SET username=?, password=?, class_id=?, paid=?, banned=?, mobile_no=?, email_address=? WHERE id=?', 
                  (username, password, class_id, paid, banned, mobile_no, email_address, user_id))
    else:
        c.execute('UPDATE users SET username=?, password=?, class_id=?, paid=?, mobile_no=?, email_address=? WHERE id=?', 
                  (username, password, class_id, paid, mobile_no, email_address, user_id))
    conn.commit()
    conn.close()

def search_users(query):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, c.name, u.paid, u.mobile_no, u.email_address FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.username LIKE ?
    ''', (f'%{query}%',))
    users = c.fetchall()
    conn.close()
    return users

# (delete_user remains the same as it uses id)

# ==============================================================================
# Resource Management Functions (Refactored)
# ==============================================================================

def save_resource(filename, class_id, filepath, title, description, category):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO resources (filename, class_id, filepath, title, description, category) VALUES (?, ?, ?, ?, ?, ?)', 
              (filename, class_id, filepath, title, description, category))
    conn.commit()
    conn.close()

def get_all_resources():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT r.filename, r.class_id, r.filepath, r.title, r.description, r.category FROM resources r
    ''')
    resources = c.fetchall()
    conn.close()
    return resources

def get_resources_for_class_id(class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT r.filename, r.class_id, r.filepath, r.title, r.description, r.category FROM resources r
        WHERE r.class_id = ?
    ''', (class_id,))
    resources = c.fetchall()
    conn.close()
    return resources

def get_categories_for_class(class_id):
    """Get all categories that are available for a specific class"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create categories table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        category_type TEXT DEFAULT 'general',
        target_class TEXT DEFAULT 'all',
        paid_status TEXT DEFAULT 'unpaid',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        is_active BOOLEAN DEFAULT 1
    )''')
    
    # Get categories that are either for all classes or specifically for this class
    c.execute('''
        SELECT id, name, description, category_type, target_class, paid_status 
        FROM categories 
        WHERE is_active = 1 
        AND (target_class = 'all' OR target_class = ?)
        ORDER BY name
    ''', (str(class_id),))
    
    categories = c.fetchall()
    conn.close()
    return categories

# (delete_resource remains the same as it uses filename)

# ==============================================================================
# Notification Management Functions (Refactored)
# ==============================================================================

def add_notification(message, class_id, target_paid_status='all', status='active', scheduled_time=None, notification_type='general'):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        'INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, scheduled_time, notification_type) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (message, class_id, get_ist_timestamp(), target_paid_status, status, scheduled_time, notification_type)
    )
    conn.commit()
    conn.close()

def get_unread_notifications_for_user(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT class_id, paid FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return []
    class_id, user_paid_status = result
    
    # Fetch class/paid notifications (only active and scheduled)
    c.execute('''
        SELECT n.id, n.message, n.created_at, n.status, n.notification_type, n.scheduled_time, 'notification' as item_type
        FROM notifications n
        LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = ?
        WHERE n.class_id = ? AND uns.notification_id IS NULL
        AND (n.target_paid_status = 'all' OR n.target_paid_status = ?)
        AND n.status IN ('active', 'scheduled')
        ORDER BY n.created_at DESC
    ''', (user_id, class_id, user_paid_status))
    notifications = c.fetchall()
    
    # Fetch personal notifications (notifications specifically for this user)
    c.execute('''
        SELECT n.id, n.message, n.created_at, n.status, n.notification_type, n.scheduled_time, 'personal_notification' as item_type
        FROM notifications n
        LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = ?
        WHERE n.class_id IS NULL AND n.target_paid_status = 'personal' AND uns.notification_id IS NULL
        AND n.status IN ('active', 'scheduled')
        ORDER BY n.created_at DESC
    ''', (user_id,))
    personal_notifications = c.fetchall()
    
    # Fetch personal chat messages (unread)
    c.execute('''
        SELECT 
            pc.id, 
            pc.message, 
            pc.created_at, 
            'active' as status, 
            'personal_chat' as notification_type, 
            pc.created_at as scheduled_time,
            'personal_chat' as item_type,
            u.username as sender_name
        FROM personal_chats pc
        JOIN users u ON pc.sender_id = u.id
        WHERE pc.receiver_id = ? 
        AND pc.is_read = 0
        ORDER BY pc.created_at DESC
    ''', (user_id,))
    personal_messages = c.fetchall()
    
    # Combine all items and sort by creation time
    all_items = notifications + personal_notifications + personal_messages
    all_items.sort(key=lambda x: x[2], reverse=True)
    
    conn.close()
    return all_items

def mark_notification_as_seen(user_id, notification_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO user_notification_status (user_id, notification_id, seen_at) VALUES (?, ?, ?)',
                  (user_id, notification_id, get_ist_timestamp()))
        conn.commit()
    except sqlite3.IntegrityError:
        # This will fail if the primary key (user_id, notification_id) already exists, which is fine.
        # It means the notification was already marked as seen.
        pass
    finally:
        conn.close()

def get_notifications_for_class(class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT message, created_at FROM notifications WHERE class_id=? ORDER BY created_at DESC', (class_id,))
    notifications = c.fetchall()
    conn.close()
    return notifications

def get_all_notifications():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT n.id, n.message,
            CASE 
                WHEN n.class_id IS NOT NULL THEN c.name
                ELSE uclass.name
            END as class_name,
            n.created_at, n.target_paid_status, n.status, n.notification_type, n.scheduled_time
        FROM notifications n
        LEFT JOIN classes c ON n.class_id = c.id
        LEFT JOIN user_notification_status uns ON n.id = uns.notification_id
        LEFT JOIN users u ON uns.user_id = u.id
        LEFT JOIN classes uclass ON u.class_id = uclass.id
        ORDER BY n.created_at DESC
    ''')
    notifications = c.fetchall()
    conn.close()
    return notifications

def add_personal_notification(message, user_id, notification_type='personal'):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Insert notification with class_id as NULL and target_paid_status as 'personal'
    c.execute(
        'INSERT INTO notifications (message, class_id, created_at, target_paid_status, status, notification_type) VALUES (?, NULL, ?, ?, ?, ?)',
        (message, get_ist_timestamp(), 'personal', 'active', notification_type)
    )
    notification_id = c.lastrowid
    
    # Don't mark as seen immediately - let the user see it as an unread notification
    # The notification will be marked as seen when the user actually reads it
    # This ensures ban messages and mention messages appear as unread notifications
    
    conn.commit()
    conn.close()

# ==============================================================================
# Live Class and Other Functions (Remain Unchanged)
# ==============================================================================

# ... (delete_user, delete_resource, live_class functions, etc. are here) ...
# Note: I have integrated the unchanged functions from the previous state of the file below.
def delete_resource(filename):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM resources WHERE filename=?', (filename,))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def create_live_class(
    class_code,
    pin,
    meeting_url,
    topic,
    description,
    status='scheduled',
    scheduled_time=None,
    target_class='all',
    class_stream=None,
    class_type='lecture',
    paid_status='unpaid',
    subject=None,
    teacher_name=None
):
    # Ensure variant columns exist even if init_db was not called
    ensure_live_class_variant_columns()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    created_at = format_ist_time(get_current_ist_time())
    c.execute(
        'INSERT INTO live_classes (class_code, pin, meeting_url, topic, description, created_at, status, scheduled_time, target_class, class_stream, class_type, paid_status, subject, teacher_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            class_code,
            pin,
            meeting_url,
            topic,
            description,
            created_at,
            status,
            scheduled_time,
            target_class,
            class_stream,
            class_type,
            paid_status,
            subject,
            teacher_name,
        ),
    )
    conn.commit()
    new_class_id = c.lastrowid
    conn.close()
    return new_class_id

def get_live_class(class_code, pin):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT meeting_url FROM live_classes WHERE class_code=? AND pin=? AND is_active=1', (class_code, pin))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_active_classes():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, class_code, pin, meeting_url, topic, description, created_at FROM live_classes WHERE is_active=1 ORDER BY created_at DESC')
    classes = c.fetchall()
    conn.close()
    return classes

def get_class_details_by_id(class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT class_code, pin, meeting_url, topic, description FROM live_classes WHERE id=?', (class_id,))
    details = c.fetchone()
    conn.close()
    return details

def deactivate_class(class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE live_classes SET is_active=0 WHERE id=?', (class_id,))
    conn.commit()
    conn.close()

def delete_notification(notification_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM user_notification_status WHERE notification_id=?', (notification_id,))
    c.execute('DELETE FROM notifications WHERE id=?', (notification_id,))
    conn.commit()
    conn.close()

def update_notification_status(notification_id, status):
    """Update the status of a notification"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE notifications SET status = ? WHERE id = ?', (status, notification_id))
    conn.commit()
    conn.close()

def get_notifications_by_status(status):
    """Get notifications by status (active, scheduled, completed, cancelled)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT n.id, n.message, c.name as class_name, n.created_at, n.status, n.notification_type, n.scheduled_time
        FROM notifications n
        LEFT JOIN classes c ON n.class_id = c.id
        WHERE n.status = ?
        ORDER BY n.created_at DESC
    ''', (status,))
    notifications = c.fetchall()
    conn.close()
    return notifications

def get_notifications_by_type(notification_type):
    """Get notifications by type (general, live_class, study_resource)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT n.id, n.message, c.name as class_name, n.created_at, n.status, n.notification_type, n.scheduled_time
        FROM notifications n
        LEFT JOIN classes c ON n.class_id = c.id
        WHERE n.notification_type = ?
        ORDER BY n.created_at DESC
    ''', (notification_type,))
    notifications = c.fetchall()
    conn.close()
    return notifications

def create_topic(name, description, class_id=None, paid='unpaid'):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO forum_topics (name, description, class_id, paid) VALUES (?, ?, ?, ?)', (name, description, class_id, paid))
    conn.commit()
    topic_id = c.lastrowid
    conn.close()
    return topic_id

def get_topics_by_class(class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name, description, created_at FROM forum_topics WHERE class_id = ? ORDER BY created_at DESC', (class_id,))
    topics = c.fetchall()
    conn.close()
    return topics

def get_topics_for_user(user_role, user_paid_status=None):
    """Get topics based on user's role/class and paid status"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if user_role in ['admin', 'teacher']:
        # Admin/teacher can see all topics
        c.execute('SELECT id, name, description, created_at, paid FROM forum_topics ORDER BY created_at DESC')
    else:
        # Students see topics for their class and general topics (class_id is NULL)
        # Filter by paid status: unpaid users only see unpaid topics, paid users see both
        if user_paid_status == 'paid':
            # Paid users can see both paid and unpaid topics for their class
            c.execute('''
                SELECT t.id, t.name, t.description, t.created_at, t.paid 
                FROM forum_topics t 
                LEFT JOIN classes c ON t.class_id = c.id 
                WHERE (t.class_id IS NULL OR c.name = ?) 
                ORDER BY t.created_at DESC
            ''', (user_role,))
        else:
            # Unpaid users can only see unpaid topics for their class
            c.execute('''
                SELECT t.id, t.name, t.description, t.created_at, t.paid 
                FROM forum_topics t 
                LEFT JOIN classes c ON t.class_id = c.id 
                WHERE (t.class_id IS NULL OR c.name = ?) 
                AND (t.paid = 'unpaid' OR t.paid IS NULL)
                ORDER BY t.created_at DESC
            ''', (user_role,))
    
    topics = c.fetchall()
    conn.close()
    return topics

def get_all_topics():
    """Get all forum topics for admin use"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name, description, class_id, created_at, paid FROM forum_topics ORDER BY created_at DESC')
    topics = c.fetchall()
    conn.close()
    return topics

def delete_topic(topic_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM forum_topics WHERE id = ?', (topic_id,))
    conn.commit()
    conn.close()

def can_user_access_topic(user_role, user_paid_status, topic_id):
    """Check if user can access a specific topic based on their role, paid status, and class"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Get topic details
    c.execute('SELECT class_id, paid FROM forum_topics WHERE id = ?', (topic_id,))
    topic = c.fetchone()
    conn.close()
    
    if not topic:
        return False
    
    class_id, topic_paid_status = topic
    
    # Admin/teacher can access all topics
    if user_role in ['admin', 'teacher']:
        return True
    
    # Check if user can access based on paid status
    if topic_paid_status == 'paid' and user_paid_status != 'paid':
        return False
    
    # If topic is paid and user is paid, allow access regardless of class
    if topic_paid_status == 'paid' and user_paid_status == 'paid':
        return True
    
    # Check if topic is for user's class or is general (class_id is NULL)
    if class_id is None:
        return True  # General topic, accessible to all
    
    # Get user's class
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id FROM classes WHERE name = ?', (user_role,))
    user_class = c.fetchone()
    conn.close()
    
    if user_class and user_class[0] == class_id:
        return True
    
    return False

def save_forum_message(user_id, username, message, parent_id=None, topic_id=None, media_url=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Get user details for access control
    user = get_user_by_id(user_id)
    
    if not user or len(user) < 5:
        conn.close()
        return False
    
    user_class_name = user[4]  # class_name from get_user_by_id
    user_paid_status = user[3]  # paid status from get_user_by_id
    
    # Check access control if topic_id is provided
    if topic_id and not can_user_access_topic(user_class_name, user_paid_status, topic_id):
        conn.close()
        return False
    
    c.execute(
        "INSERT INTO forum_messages (user_id, username, message, parent_id, topic_id, media_url) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, username, message, parent_id, topic_id, media_url)
    )
    message_id = c.lastrowid
    conn.commit()
    conn.close()
    return message_id

def get_forum_messages(parent_id=None, topic_id=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if parent_id is None:
        if topic_id is not None:
            c.execute("""
                SELECT m.*, 
                       p.username as reply_to_username, 
                       p.message as reply_to_message
                FROM forum_messages m
                LEFT JOIN forum_messages p ON m.parent_id = p.id
                WHERE m.parent_id IS NULL AND m.topic_id = ? 
                ORDER BY m.timestamp DESC
            """, (topic_id,))
        else:
            c.execute("""
                SELECT m.*, 
                       p.username as reply_to_username, 
                       p.message as reply_to_message
                FROM forum_messages m
                LEFT JOIN forum_messages p ON m.parent_id = p.id
                WHERE m.parent_id IS NULL 
                ORDER BY m.timestamp DESC
            """)
    else:
        c.execute("""
            SELECT m.*, 
                   p.username as reply_to_username, 
                   p.message as reply_to_message
            FROM forum_messages m
            LEFT JOIN forum_messages p ON m.parent_id = p.id
            WHERE m.parent_id = ? 
            ORDER BY m.timestamp ASC
        """, (parent_id,))
    
    messages = c.fetchall()
    conn.close()
    return messages

# ==========================
# Forum Poll helper functions
# ==========================

def create_forum_poll(message_id: int, question: str, options: list[str]):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO forum_polls (message_id, question) VALUES (?, ?)', (message_id, question))
        poll_id = c.lastrowid
        for opt in options:
            c.execute('INSERT INTO forum_poll_options (poll_id, option_text) VALUES (?, ?)', (poll_id, opt))
        conn.commit()
        return poll_id
    finally:
        conn.close()

def get_forum_poll_by_message(message_id: int):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM forum_polls WHERE message_id=?', (message_id,))
    poll = c.fetchone()
    if not poll:
        conn.close()
        return None
    c.execute('SELECT id, option_text FROM forum_poll_options WHERE poll_id=?', (poll['id'],))
    options = [dict(row) for row in c.fetchall()]
    # Votes per option
    results = []
    total_votes = 0
    for opt in options:
        c.execute('SELECT COUNT(*) FROM forum_poll_votes WHERE option_id=?', (opt['id'],))
        count = c.fetchone()[0]
        total_votes += count
        results.append({'option_id': opt['id'], 'option_text': opt['option_text'], 'votes': count})
    conn.close()
    return {
        'poll_id': poll['id'],
        'message_id': message_id,
        'question': poll['question'],
        'options': options,
        'results': results,
        'total_votes': total_votes
    }

def has_user_voted_forum_poll(poll_id: int, user_id: int) -> bool:
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT 1 FROM forum_poll_votes WHERE poll_id=? AND user_id=? LIMIT 1', (poll_id, user_id))
    voted = c.fetchone() is not None
    conn.close()
    return voted

def vote_forum_poll(message_id: int, option_id: int, user_id: int):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Verify poll and option
    c.execute('SELECT id FROM forum_polls WHERE message_id=?', (message_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, 'Poll not found'
    poll_id = row['id']
    c.execute('SELECT 1 FROM forum_poll_options WHERE id=? AND poll_id=?', (option_id, poll_id))
    if not c.fetchone():
        conn.close()
        return False, 'Invalid option'
    # Prevent duplicate votes
    c.execute('SELECT 1 FROM forum_poll_votes WHERE poll_id=? AND user_id=?', (poll_id, user_id))
    if c.fetchone():
        conn.close()
        return False, 'Already voted'
    # Insert vote
    c.execute('INSERT INTO forum_poll_votes (poll_id, option_id, user_id) VALUES (?, ?, ?)', (poll_id, option_id, user_id))
    conn.commit()
    conn.close()
    return True, None

def vote_on_message(message_id, vote_type):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    if vote_type == 'upvote':
        c.execute("UPDATE forum_messages SET upvotes = upvotes + 1 WHERE id = ?", (message_id,))
    elif vote_type == 'downvote':
        c.execute("UPDATE forum_messages SET downvotes = downvotes + 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def delete_forum_message(message_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM forum_messages WHERE id = ? OR parent_id = ?", (message_id, message_id))
    conn.commit()
    conn.close()

def save_live_class_message(live_class_id, user_id, username, message, media_url=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO live_class_messages (live_class_id, user_id, username, message, media_url) VALUES (?, ?, ?, ?, ?)', (live_class_id, user_id, username, message, media_url))
    conn.commit()
    conn.close()

def get_live_class_messages(live_class_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, user_id, username, message, media_url, timestamp FROM live_class_messages WHERE live_class_id=? ORDER BY timestamp ASC', (live_class_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def delete_live_class_message(message_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM live_class_messages WHERE id=?', (message_id,))
    conn.commit()
    conn.close()

# ==============================================================================
# Enhanced Live Class Management Functions
# ==============================================================================

def update_live_class_status(class_id, status):
    """Update the status of a live class"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if status == 'active':
        # Set activated_at when transitioning to active (store as formatted IST time for consistent comparisons)
        from time_config import format_ist_time, get_current_ist_time
        current_time = format_ist_time(get_current_ist_time())
        c.execute('UPDATE live_classes SET status = ?, activated_at = ? WHERE id = ?', (status, current_time, class_id))
    else:
        c.execute('UPDATE live_classes SET status = ? WHERE id = ?', (status, class_id))
    
    conn.commit()
    conn.close()

def get_live_classes_by_status(status):
    """Get live classes by status (scheduled, active, completed, cancelled)"""
    # Ensure variant columns exist
    ensure_live_class_variant_columns()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT 
            id, class_code, pin, meeting_url, topic, description, created_at, status, scheduled_time,
            target_class, class_stream, class_type, paid_status, subject, teacher_name
        FROM live_classes 
        WHERE status = ?
        ORDER BY created_at DESC
    ''', (status,))
    classes = c.fetchall()
    conn.close()
    return classes

def get_scheduled_live_classes():
    """Get all scheduled live classes"""
    return get_live_classes_by_status('scheduled')

def get_active_live_classes():
    """Get all currently active live classes"""
    return get_live_classes_by_status('active')

def get_completed_live_classes():
    """Get all completed live classes"""
    return get_live_classes_by_status('completed')

def get_upcoming_live_classes():
    """Get upcoming scheduled live classes (scheduled for future or without specific time)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = get_current_ist_time()
    c.execute('''
        SELECT 
            id, class_code, pin, meeting_url, topic, description, created_at, status, scheduled_time,
            target_class, class_stream, class_type, paid_status, subject, teacher_name
        FROM live_classes 
        WHERE status = 'scheduled' AND (scheduled_time > ? OR scheduled_time IS NULL)
        ORDER BY scheduled_time ASC
    ''', (format_ist_time(current_time),))
    classes = c.fetchall()
    conn.close()
    return classes

def schedule_live_class(class_code, pin, meeting_url, topic, description, scheduled_time):
    """Schedule a live class for a specific time"""
    return create_live_class(class_code, pin, meeting_url, topic, description, 'scheduled', scheduled_time)

def start_live_class(class_id):
    """Mark a live class as active"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Update status to active and set activation time (store as formatted IST time)
    from time_config import format_ist_time, get_current_ist_time
    current_time = format_ist_time(get_current_ist_time())
    c.execute('''
        UPDATE live_classes 
        SET status = 'active', activated_at = ? 
        WHERE id = ?
    ''', (current_time, class_id))
    
    conn.commit()
    conn.close()

def complete_live_class(class_id):
    """Mark a live class as completed"""
    update_live_class_status(class_id, 'completed')

def cancel_live_class(class_id):
    """Cancel a live class"""
    update_live_class_status(class_id, 'cancelled')

def get_live_class_with_status(class_id):
    """Get live class details including status"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT id, class_code, pin, meeting_url, topic, description, created_at, status, scheduled_time, is_active
        FROM live_classes WHERE id = ?
    ''', (class_id,))
    details = c.fetchone()
    conn.close()
    return details

def auto_update_class_statuses():
    """Automatically update class statuses based on current time"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = get_current_ist_time()
    current_time_str = format_ist_time(current_time)
    
    # Update scheduled classes to active if their time has come
    c.execute('''
        UPDATE live_classes 
        SET status = 'active' 
        WHERE status = 'scheduled' 
        AND scheduled_time <= ?
    ''', (current_time_str,))
    
    # Update active classes to completed if they've been running for more than 2 hours
    # (assuming class duration is 2 hours max)
    from datetime import timedelta
    two_hours_ago = current_time - timedelta(hours=2)
    two_hours_ago_str = format_ist_time(two_hours_ago)
    
    # Only auto-complete classes that have been active for more than 2 hours
    # Use activated_at field if available, otherwise fall back to created_at
    two_hours_ago = current_time - timedelta(hours=2)
    two_hours_ago_str = format_ist_time(two_hours_ago)
    
    c.execute('''
        UPDATE live_classes 
        SET status = 'completed' 
        WHERE status = 'active' 
        AND (activated_at <= ? OR (activated_at IS NULL AND created_at <= ?))
    ''', (two_hours_ago_str, two_hours_ago_str))
    
    conn.commit()
    conn.close()

def end_live_class(class_id, recording_url=None):
    """End a live class (mark as completed) - called when end button is clicked"""
    # Mark completed
    complete_live_class(class_id)
    
    # Also deactivate the class for backward compatibility and set timestamps/recording
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    from datetime import datetime
    completed_time = format_ist_time(get_current_ist_time())
    if recording_url:
        c.execute('UPDATE live_classes SET is_active = 0, completed_at = ?, recording_url = ? WHERE id = ?', (completed_time, recording_url, class_id))
    else:
        c.execute('UPDATE live_classes SET is_active = 0, completed_at = ? WHERE id = ?', (completed_time, class_id))
    conn.commit()
    conn.close()

def set_live_class_recording(class_id, recording_url):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('UPDATE live_classes SET recording_url = ? WHERE id = ?', (recording_url, class_id))
    conn.commit()
    conn.close()

def get_live_classes_for_display():
    """Get all live classes organized by status for display"""
    auto_update_class_statuses()  # Auto-update statuses first
    
    return {
        'upcoming': get_upcoming_live_classes(),
        'active': get_active_live_classes(),
        'completed': get_completed_live_classes()
    }

def is_class_time_to_start(class_id):
    """Check if it's time for a scheduled class to start"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    current_time = get_current_ist_time()
    current_time_str = format_ist_time(current_time)
    
    c.execute('''
        SELECT scheduled_time 
        FROM live_classes 
        WHERE id = ? AND status = 'scheduled'
    ''', (class_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        scheduled_time = result[0]
        if scheduled_time is None:
            return True  # Allow starting if no scheduled time
        return scheduled_time <= current_time_str
    
    return False

def can_start_class(class_id):
    """Check if a class can be started (is scheduled and time has come)"""
    return is_class_time_to_start(class_id)

def can_end_class(class_id):
    """Check if a class can be ended (is currently active)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT status FROM live_classes WHERE id = ?', (class_id,))
    result = c.fetchone()
    conn.close()
    
    return result and result[0] == 'active'

# Enhanced Live Class Helper Functions
def record_attendance(class_id, user_id, username):
    """Record user attendance in live class"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = get_ist_timestamp()
    
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
        
        conn.commit()
        print(f"✅ Attendance recorded for user {username} in class {class_id}")
    except sqlite3.IntegrityError:
        print(f"ℹ️  User {username} already joined class {class_id}")
    except Exception as e:
        print(f"❌ Error recording attendance: {e}")
    finally:
        conn.close()

def get_class_attendance(class_id):
    """Get attendance list for a class"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        SELECT username, joined_at
        FROM live_class_attendance
        WHERE class_id = ?
        ORDER BY joined_at
    ''', (class_id,))
    attendance = c.fetchall()
    conn.close()
    return attendance

def get_live_class_analytics():
    """Get basic analytics for live classes"""
    conn = sqlite3.connect(DATABASE)
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
    
    # Recent classes
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
        'recent_classes': recent_classes
    }

def cleanup_old_classes():
    """Clean up old completed classes (older than 30 days)"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Get old completed classes
    c.execute('''
        SELECT id FROM live_classes 
        WHERE status = 'completed' 
        AND created_at < datetime('now', '-30 days')
    ''')
    old_classes = c.fetchall()
    
    if old_classes:
        class_ids = [str(c[0]) for c in old_classes]
        placeholders = ','.join(['?' for _ in class_ids])
        
        # Delete related data
        c.execute(f'DELETE FROM live_class_attendance WHERE class_id IN ({placeholders})', class_ids)
        c.execute(f'DELETE FROM live_class_messages WHERE class_id IN ({placeholders})', class_ids)
        c.execute(f'DELETE FROM live_classes WHERE id IN ({placeholders})', class_ids)
        
        conn.commit()
        print(f"✅ Cleaned up {len(old_classes)} old classes")
    else:
        print("ℹ️  No old classes to clean up")
    
    conn.close()

def validate_live_class_data():
    """Validate and fix live class data integrity"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Fix status inconsistencies
    c.execute("UPDATE live_classes SET is_active = 0 WHERE status = 'completed' AND is_active = 1")
    c.execute("UPDATE live_classes SET is_active = 0 WHERE status = 'cancelled' AND is_active = 1")
    c.execute("UPDATE live_classes SET status = 'active' WHERE is_active = 1 AND status != 'active'")
    
    # Set default values
    c.execute("UPDATE live_classes SET duration_minutes = 60 WHERE duration_minutes IS NULL")
    c.execute("UPDATE live_classes SET attendance_count = 0 WHERE attendance_count IS NULL")
    
    conn.commit()
    conn.close()
    print("✅ Live class data validated and fixed")

def format_datetime_for_display(datetime_str):
    """Format datetime string for display in notifications"""
    if not datetime_str:
        return "Unknown time"
    
    try:
        # Handle different datetime formats
        if 'T' in datetime_str:
            # ISO format: 2025-01-15T14:30:00
            dt_str = datetime_str.replace('T', ' ')
            if '.' in dt_str:
                dt_str = dt_str.split('.')[0]
        else:
            dt_str = datetime_str
        
        # Parse the datetime
        from datetime import datetime
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        
        # Format for display
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 3600:  # Less than 1 hour
                minutes = diff.seconds // 60
                if minutes == 0:
                    return "Just now"
                elif minutes == 1:
                    return "1 minute ago"
                else:
                    return f"{minutes} minutes ago"
            else:  # More than 1 hour
                hours = diff.seconds // 3600
                if hours == 1:
                    return "1 hour ago"
                else:
                    return f"{hours} hours ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime('%b %d, %Y')
            
    except Exception:
        # Fallback to original format if parsing fails
        return datetime_str[:19].replace('T', ' ') if 'T' in datetime_str else datetime_str

# ==============================================================================
# Personal Chat Functions
# ==============================================================================

def send_personal_message(sender_id, receiver_id, message):
    """Send a personal message between two users"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO personal_chats (sender_id, receiver_id, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, message, get_current_ist_time()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error sending personal message: {e}")
        return False
    finally:
        conn.close()

def get_personal_messages(user1_id, user2_id, limit=50):
    """Get personal messages between two users"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT pc.id, pc.sender_id, pc.receiver_id, pc.message, pc.created_at, pc.is_read,
                   u.username as sender_name
            FROM personal_chats pc
            JOIN users u ON pc.sender_id = u.id
            WHERE (pc.sender_id = ? AND pc.receiver_id = ?) 
               OR (pc.sender_id = ? AND pc.receiver_id = ?)
            ORDER BY pc.created_at DESC
            LIMIT ?
        ''', (user1_id, user2_id, user2_id, user1_id, limit))
        messages = c.fetchall()
        return messages
    except Exception as e:
        print(f"Error getting personal messages: {e}")
        return []
    finally:
        conn.close()

def get_user_conversations(user_id):
    """Get all conversations for a user"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT DISTINCT 
                CASE 
                    WHEN pc.sender_id = ? THEN pc.receiver_id
                    ELSE pc.sender_id
                END as other_user_id,
                u.username as other_username,
                MAX(pc.created_at) as last_message_time,
                COUNT(CASE WHEN pc.receiver_id = ? AND pc.is_read = 0 THEN 1 END) as unread_count
            FROM personal_chats pc
            JOIN users u ON (
                CASE 
                    WHEN pc.sender_id = ? THEN pc.receiver_id
                    ELSE pc.sender_id
                END = u.id
            )
            WHERE pc.sender_id = ? OR pc.receiver_id = ?
            GROUP BY other_user_id
            ORDER BY last_message_time DESC
        ''', (user_id, user_id, user_id, user_id, user_id))
        conversations = c.fetchall()
        return conversations
    except Exception as e:
        print(f"Error getting user conversations: {e}")
        return []
    finally:
        conn.close()

def mark_messages_as_read(user_id, sender_id):
    """Mark messages as read from a specific sender"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('''
            UPDATE personal_chats 
            SET is_read = 1 
            WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
        ''', (user_id, sender_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        return False
    finally:
        conn.close()

def send_welcome_message(user_id):
    """Send a welcome message to a new user"""
    admin_user_id = get_admin_user_id()
    if admin_user_id:
        welcome_message = "Welcome to your very own Sunrise-Educational-Classes! 🎉 We're excited to have you join our community. Feel free to explore our study resources, join live classes, and connect with other students. If you have any questions, don't hesitate to ask!"
        return send_personal_message(admin_user_id, user_id, welcome_message)
    return False

def get_admin_user_id():
    """Get the admin user ID"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        c.execute('SELECT id FROM users WHERE username = "yash" LIMIT 1')
        result = c.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting admin user ID: {e}")
        return None
    finally:
        conn.close()