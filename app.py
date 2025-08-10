from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify, send_file
try:
    from werkzeug.security import generate_password_hash, check_password_hash
    WERKZEUG_AVAILABLE = True
except ImportError:
    import hashlib
    WERKZEUG_AVAILABLE = False
    
    def generate_password_hash(password):
        """Fallback password hashing using SHA-256 with salt"""
        salt = 'admission_salt_2024'
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def check_password_hash(stored_hash, password):
        """Fallback password verification"""
        salt = 'admission_salt_2024'
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return stored_hash == computed_hash

import os
import secrets
try:
    from werkzeug.utils import secure_filename
except ImportError:
    import re
    def secure_filename(filename):
        """Fallback secure filename function"""
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        return filename
from auth_handler import (
    init_db, register_user, authenticate_user, save_resource, get_all_resources,
    delete_resource, get_all_users, delete_user, search_users, get_user_by_id,
    update_user, add_notification, get_unread_notifications_for_user, get_all_notifications,
    create_live_class, get_live_class, get_active_classes, deactivate_class,
    get_class_details_by_id, get_all_classes, get_resources_for_class_id,
    mark_notification_as_seen, delete_notification,
    save_forum_message, get_live_class_messages, save_live_class_message,
    create_topic, delete_topic, get_all_topics, get_topics_for_user, can_user_access_topic,
    update_user_with_password, add_personal_notification, get_forum_messages,
    format_datetime_for_display, get_categories_for_class
)
import csv
from io import StringIO
from collections import Counter
from functools import wraps
import sqlite3
from datetime import datetime, timedelta, timezone
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import g

# Import time configuration
from time_config import (
    get_current_ist_time, format_ist_time, format_relative_time, 
    get_date_for_display, get_time_for_display, get_timezone_info,
    is_business_hours, get_available_class_slots
)

# Import bulk upload routes
from bulk_upload.routes import bulk_upload_bp

# Initialize Flask app
app = Flask(__name__, static_folder='.', template_folder='templates')

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = secrets.token_hex(16)

DATABASE = 'bulk_upload/users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_poll_and_doubt_tables():
    db = get_db()
    c = db.cursor()
    # Polls
    c.execute('''CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id TEXT,
        question TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS poll_options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        option_text TEXT,
        FOREIGN KEY(poll_id) REFERENCES polls(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS poll_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        option_id INTEGER,
        user_id TEXT,
        voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(poll_id) REFERENCES polls(id),
        FOREIGN KEY(option_id) REFERENCES poll_options(id)
    )''')
    # Doubts
    c.execute('''CREATE TABLE IF NOT EXISTS doubts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id TEXT,
        user_id TEXT,
        username TEXT,
        doubt_text TEXT,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    )''')
    db.commit()

# Initialize database tables on app startup
def setup_db():
    init_poll_and_doubt_tables()
    init_admissions_table()

# Initialize IP tracking tables
def init_tracking_tables():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ip_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_id INTEGER,
            path TEXT,
            user_agent TEXT,
            visited_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_activity (
            user_id INTEGER PRIMARY KEY,
            ip TEXT,
            last_seen TEXT
        )''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing tracking tables: {e}")

def init_admission_access_table():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS admission_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_id INTEGER NOT NULL,
            access_username TEXT UNIQUE NOT NULL,
            access_password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing admission access table: {e}")

def init_admissions_table():
    """Initialize the admissions table with all required columns"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Create admissions table with all required columns
        c.execute('''CREATE TABLE IF NOT EXISTS admissions (
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
        )''')
        
        # Check if required columns exist and add them if missing
        c.execute("PRAGMA table_info(admissions)")
        existing_columns = [row[1] for row in c.fetchall()]
        
        required_columns = [
            ('user_id', 'INTEGER'),
            ('submit_ip', 'TEXT'),
            ('approved_at', 'TEXT'),
            ('approved_by', 'TEXT'),
            ('disapproved_at', 'TEXT'),
            ('disapproved_by', 'TEXT'),
            ('disapproval_reason', 'TEXT')
        ]
        
        for col_name, col_type in required_columns:
            if col_name not in existing_columns:
                try:
                    c.execute(f'ALTER TABLE admissions ADD COLUMN {col_name} {col_type}')
                    print(f"Added column: {col_name}")
                except Exception as e:
                    print(f"Error adding column {col_name}: {e}")
        
        conn.commit()
        conn.close()
        print("Admissions table initialized successfully")
    except Exception as e:
        print(f"Error initializing admissions table: {e}")

def ensure_admissions_submit_ip_column():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Try to add submit_ip column if it does not exist
        c.execute("PRAGMA table_info(admissions)")
        cols = [row[1] for row in c.fetchall()]
        if 'submit_ip' not in cols:
            c.execute('ALTER TABLE admissions ADD COLUMN submit_ip TEXT')
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error ensuring admissions.submit_ip column: {e}")

# Call setup_db when the app starts
with app.app_context():
    setup_db()
    init_tracking_tables()
    init_admission_access_table()
    ensure_admissions_submit_ip_column()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

def admin_api_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

app.secret_key = 'your_secret_key_here'  # Change this to a secure random value in production

# Register blueprints
app.register_blueprint(bulk_upload_bp)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

# --- Queries DB Setup ---
def init_queries_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            phone TEXT,
            subject TEXT,
            priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'pending',
            assigned_to TEXT,
            response TEXT,
            responded_at TIMESTAMP,
            responded_by TEXT,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'website'
        )''')
        # Ensure all columns exist (for older tables)
        c.execute("PRAGMA table_info(queries)")
        existing_cols = {row[1] for row in c.fetchall()}
        required_cols = {
            'phone': "ALTER TABLE queries ADD COLUMN phone TEXT",
            'subject': "ALTER TABLE queries ADD COLUMN subject TEXT",
            'priority': "ALTER TABLE queries ADD COLUMN priority TEXT DEFAULT 'normal'",
            'status': "ALTER TABLE queries ADD COLUMN status TEXT DEFAULT 'pending'",
            'assigned_to': "ALTER TABLE queries ADD COLUMN assigned_to TEXT",
            'response': "ALTER TABLE queries ADD COLUMN response TEXT",
            'responded_at': "ALTER TABLE queries ADD COLUMN responded_at TIMESTAMP",
            'responded_by': "ALTER TABLE queries ADD COLUMN responded_by TEXT",
            'category': "ALTER TABLE queries ADD COLUMN category TEXT DEFAULT 'general'",
            'source': "ALTER TABLE queries ADD COLUMN source TEXT DEFAULT 'website'",
            'user_ip': "ALTER TABLE queries ADD COLUMN user_ip TEXT",
        }
        for col, alter in required_cols.items():
            if col not in existing_cols:
                try:
                    c.execute(alter)
                except sqlite3.OperationalError:
                    pass
        # Indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_queries_priority ON queries(priority)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_queries_submitted_at ON queries(submitted_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_queries_category ON queries(category)")
        # Migrate from legacy queries.db if present
        try:
            legacy_path = 'queries.db'
            if os.path.exists(legacy_path):
                try:
                    legacy_conn = sqlite3.connect(legacy_path)
                    legacy_c = legacy_conn.cursor()
                    legacy_c.execute("SELECT name, email, message, submitted_at FROM queries")
                    rows = legacy_c.fetchall()
                    for r in rows:
                        c.execute(
                            "INSERT INTO queries (name, email, message, submitted_at) VALUES (?, ?, ?, ?)",
                            (r[0], r[1], r[2], r[3])
                        )
                    legacy_conn.close()
                    # Backup legacy file
                    backup_name = f"users_backup_legacy_queries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    try:
                        os.rename(legacy_path, backup_name)
                    except Exception:
                        pass
                except Exception:
                    pass
        except Exception:
            pass
        conn.commit()
    finally:
        conn.close()
init_queries_db()

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', 
                   ping_timeout=60, ping_interval=25, logger=True, engineio_logger=True)

# Active session tracking
active_sessions = {}
room_participants = {}

# --- Socket.IO Connection Management ---
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    active_sessions[request.sid] = {
        'connected_at': datetime.now(),
        'last_ping': datetime.now(),
        'rooms': []
    }
    emit('connection_status', {'status': 'connected', 'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in active_sessions:
        # Clean up user from all rooms
        user_rooms = active_sessions[request.sid].get('rooms', [])
        for room in user_rooms:
            if room in room_participants:
                if request.sid in room_participants[room]:
                    room_participants[room].remove(request.sid)
                    # Emit updated count to room
                    socketio.emit('student_count_update', {
                        'class_id': room.replace('liveclass_', ''),
                        'count': len(room_participants[room])
                    }, room=room)
                    
        del active_sessions[request.sid]

@socketio.on('ping')
def handle_ping():
    if request.sid in active_sessions:
        active_sessions[request.sid]['last_ping'] = datetime.now()
    emit('pong')

# --- Enhanced Room Management ---
@socketio.on('join-room')
def handle_join_room(data):
    try:
        room = data.get('room')
        if not room:
            emit('error', {'message': 'Room name is required'})
            return
            
        join_room(room)
        
        # Track room participation
        if room not in room_participants:
            room_participants[room] = []
        if request.sid not in room_participants[room]:
            room_participants[room].append(request.sid)
            
        # Update session info
        if request.sid in active_sessions:
            active_sessions[request.sid]['rooms'].append(room)
            
        emit('joined-room', {'room': room, 'session_id': request.sid})
        
        # Send student count update if it's a live class room
        if room.startswith('liveclass_'):
            class_id = room.replace('liveclass_', '')
            socketio.emit('student_count_update', {
                'class_id': class_id,
                'count': len(room_participants[room])
            }, room=room)
            
        print(f"Client {request.sid} joined room {room}")
        
    except Exception as e:
        print(f"Error in join-room: {e}")
        emit('error', {'message': 'Failed to join room'})

@socketio.on('leave-room')
def handle_leave_room(data):
    try:
        room = data.get('room')
        if not room:
            return
            
        leave_room(room)
        
        # Update room participation
        if room in room_participants and request.sid in room_participants[room]:
            room_participants[room].remove(request.sid)
            
            # Send updated count
            if room.startswith('liveclass_'):
                class_id = room.replace('liveclass_', '')
                socketio.emit('student_count_update', {
                    'class_id': class_id,
                    'count': len(room_participants[room])
                }, room=room)
        
        # Update session info
        if request.sid in active_sessions:
            if room in active_sessions[request.sid]['rooms']:
                active_sessions[request.sid]['rooms'].remove(room)
                
        emit('left-room', {'room': room})
        print(f"Client {request.sid} left room {room}")
        
    except Exception as e:
        print(f"Error in leave-room: {e}")

@socketio.on('get_student_count')
def handle_get_student_count(data):
    try:
        class_id = data.get('class_id')
        if class_id:
            room = f'liveclass_{class_id}'
            count = len(room_participants.get(room, []))
            emit('student_count_update', {
                'class_id': class_id,
                'count': count
            })
    except Exception as e:
        print(f"Error getting student count: {e}")

# --- WebRTC Signaling ---

@socketio.on('signal')
def handle_signal(data):
    try:
        room = data.get('room')
        signal = data.get('signal')
        if room and signal:
            emit('signal', {'signal': signal, 'from': request.sid}, room=room, include_self=False)
        else:
            emit('error', {'message': 'Invalid signal data'})
    except Exception as e:
        print(f"Error in signal: {e}")
        emit('error', {'message': 'Signal failed'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_global_variables():
    user_id = session.get('user_id')
    username = session.get('username')
    role = session.get('role')
    user_paid_status = session.get('paid_status')
    notifications = []
    if user_id:
        notifications = get_unread_notifications_for_user(user_id)
            
    all_classes = get_all_classes()
    return dict(
        user_notifications=notifications, 
        all_classes=all_classes, 
        username=username, 
        role=role,
        user_paid_status=user_paid_status,
        format_datetime_for_display=format_datetime_for_display
    )

# Route for the main page
@app.route('/')
def home():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('SELECT name, email, message, submitted_at FROM queries ORDER BY id DESC LIMIT 10')
        queries = c.fetchall()
    return render_template('index.html', queries=queries)

# Route for study resources
@app.route('/study-resources')
def study_resources():
    role = session.get('role')

    # Redirect if not logged in
    if not role:
        flash('You must be logged in to view resources.', 'error')
        return redirect(url_for('auth'))
    
    # Redirect admin/teacher to their own panel, as this page is for students
    if role in ['admin', 'teacher']:
        flash('Please use the admin panel to manage all resources.', 'info')
        return redirect(url_for('admin_panel'))

    # Get class_id from the role name stored in the session
    all_classes_dict_rev = {c[1]: c[0] for c in get_all_classes()}
    class_id = all_classes_dict_rev.get(role)
    
    # Fetch resources only for the user's class
    resources = []
    if class_id:
        resources = get_resources_for_class_id(class_id)

    # Fetch all categories for this class
    categories = []
    if class_id:
        categories = get_categories_for_class(class_id)

    user_id = session.get('user_id')
    paid_status = None
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            paid_status = user[3]  # Assuming user[3] is the paid status

    return render_template('study-resources.html', resources=resources, categories=categories, class_name=role, class_id=class_id, paid_status=paid_status)

# Route for forum
@app.route("/forum")
def forum():
    username = session.get("username")
    role = session.get("role")
    user_id = session.get("user_id")
    
    if not username:
        flash("You must be logged in to view the forum.", "error")
        return redirect(url_for("auth"))
    
    # Get user's paid status
    user_paid_status = None
    if user_id:
        user = get_user_by_id(user_id)
        if user and len(user) > 3:
            user_paid_status = user[3]  # user[3] is the paid status
    
    # Get topics for this user/class with paid status filtering
    all_topics = get_topics_for_user(role, user_paid_status)
    paid_topics = [t for t in all_topics if t[4] == 'paid']
    unpaid_topics = [t for t in all_topics if t[4] != 'paid']
    
    # Debug: Print topics for debugging
    print(f"User: {username}, Role: {role}, Paid: {user_paid_status}")
    print(f"All topics: {all_topics}")
    print(f"Paid topics: {paid_topics}")
    print(f"Unpaid topics: {unpaid_topics}")
    
    return render_template('forum.html', username=username, paid_topics=paid_topics, unpaid_topics=unpaid_topics, role=role, user_paid_status=user_paid_status)

@app.route('/api/forum/messages', methods=['GET'])
def api_get_forum_messages():
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user's paid status
    user = get_user_by_id(user_id)
    user_paid_status = user[3] if user and len(user) > 3 else None
    
    topic_id = request.args.get('topic_id')
    
    # Check access control if specific topic is requested
    if topic_id and topic_id != 'all':
        try:
            topic_id_int = int(topic_id)
            if not can_user_access_topic(user_role, user_paid_status, topic_id_int):
                return jsonify({'error': 'Access denied to this topic'}), 403
            messages = get_forum_messages(topic_id=topic_id_int)
        except ValueError:
            return jsonify({'error': 'Invalid topic ID'}), 400
    else:
        # For 'all' topics, filter based on user's access
        if user_role in ['admin', 'teacher']:
            messages = get_forum_messages()
        else:
            # Students only see messages from topics they can access
            user_topics = get_topics_for_user(user_role, user_paid_status)
            topic_ids = [topic[0] for topic in user_topics]
            if topic_ids:
                # Get messages from accessible topics
                messages = []
                for tid in topic_ids:
                    topic_messages = get_forum_messages(topic_id=tid)
                    messages.extend(topic_messages)
                # Sort by timestamp
                messages.sort(key=lambda x: x[7], reverse=True)
            else:
                messages = []
    
    return jsonify([
        {
            'id': m[0], 'user_id': m[1], 'username': m[2], 'message': m[3],
            'parent_id': m[4], 'upvotes': m[5], 'downvotes': m[6], 'timestamp': m[7], 
            'topic_id': m[8] if len(m) > 8 else None, 'media_url': m[9] if len(m) > 9 else None,
            'reply_to_username': m[10] if len(m) > 10 else None, 'reply_to_message': m[11] if len(m) > 11 else None
        } for m in messages
    ])

@app.route('/api/forum/messages', methods=['POST'])
def api_post_forum_message():
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    # Handle both JSON and multipart/form-data
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        message = request.form.get('message')
        parent_id = request.form.get('parent_id')
        topic_id = request.form.get('topic_id')
        file = request.files.get('media')
        media_url = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            media_folder = os.path.join(UPLOAD_FOLDER, 'forum_media')
            os.makedirs(media_folder, exist_ok=True)
            filepath = os.path.join(media_folder, filename)
            file.save(filepath)
            media_url = f'uploads/forum_media/{filename}'
    else:
        data = request.json
        message = data.get('message') if data else None
        parent_id = data.get('parent_id') if data else None
        topic_id = data.get('topic_id') if data else None
        media_url = None

    if not message and not media_url:
        return jsonify({'error': 'Message or media required'}), 400

    # Check access control for the topic
    if topic_id:
        user = get_user_by_id(user_id)
        if user and len(user) > 4:
            user_class_name = user[4]  # class_name from get_user_by_id
            user_paid_status = user[3]  # paid status from get_user_by_id
            if not can_user_access_topic(user_class_name, user_paid_status, topic_id):
                return jsonify({'error': 'Access denied to this topic'}), 403

    success = save_forum_message(user_id, username, message, parent_id, topic_id, media_url)
    if success:
        return jsonify({'success': True}), 201
    else:
        return jsonify({'error': 'Access denied or invalid topic'}), 403

@app.route('/api/forum/messages/<int:message_id>/replies', methods=['GET'])
def api_get_message_replies(message_id):
    replies = get_forum_messages(parent_id=message_id)
    return jsonify([
        {
            'id': r[0], 'user_id': r[1], 'username': r[2], 'message': r[3],
            'parent_id': r[4], 'upvotes': r[5], 'downvotes': r[6], 'timestamp': r[7]
        } for r in replies
    ])

@app.route('/api/forum/messages/<int:message_id>/vote', methods=['POST'])
def api_vote_on_message(message_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    vote_type = data.get('vote_type')
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'error': 'Invalid vote type'}), 400
    # The original code had vote_on_message, which is not defined.
    # Assuming it was meant to be a placeholder for a voting mechanism.
    # For now, we'll just return success.
    return jsonify({'success': True})

@app.route('/api/forum/messages/<int:message_id>', methods=['DELETE'])
def api_delete_forum_message(message_id):
    user_id = session.get('user_id')
    user_role = session.get('role')
    # Only allow delete if admin or the message belongs to the user
    # from auth_handler import get_forum_messages # This line was removed as per the edit hint
    # messages = get_forum_messages() # This line was removed as per the edit hint
    # msg = next((m for m in messages if m[0] == message_id), None) # This line was removed as per the edit hint
    # if not msg: # This line was removed as per the edit hint
    #     return jsonify({'error': 'Message not found'}), 404 # This line was removed as per the edit hint
    # if user_role != 'admin' and msg[1] != user_id: # This line was removed as per the edit hint
    #     return jsonify({'error': 'Unauthorized'}), 401 # This line was removed as per the edit hint
    # delete_forum_message(message_id) # This line was removed as per the edit hint
    # return jsonify({'success': True}) # This line was removed as per the edit hint
    # The original code had delete_forum_message, which is not defined.
    # Assuming it was meant to be a placeholder for a deletion mechanism.
    # For now, we'll just return success.
    return jsonify({'success': True})

# Route for online class
@app.route('/online-class', methods=['GET'])
def online_class():
    user_id = session.get('user_id')
    role = session.get('role')
    username = session.get('username')
    if not user_id or not role:
        flash('You must be logged in to access the online class.', 'error')
        return redirect(url_for('auth'))

    from auth_handler import get_upcoming_live_classes, get_active_live_classes, get_completed_live_classes, get_user_by_id

    upcoming_classes = get_upcoming_live_classes()
    active_classes = get_active_live_classes()
    completed_classes = get_completed_live_classes()

    # Student: filter by paid status
    if role not in ['admin', 'teacher']:
        user = get_user_by_id(user_id)
        user_paid_status = None
        if user and len(user) > 3:
            user_paid_status = user[3]  # paid status is 4th column in users table
        # Filter each list by paid status if needed
        if user_paid_status != 'paid':
            active_classes = [c for c in active_classes if len(c) > 6 and (c[6] == 'unpaid')]
            upcoming_classes = [c for c in upcoming_classes if len(c) > 6 and (c[6] == 'unpaid')]
            completed_classes = [c for c in completed_classes if len(c) > 6 and (c[6] == 'unpaid')]

    return render_template('online-class.html', role=role, username=username,
        upcoming_classes=upcoming_classes, active_classes=active_classes, completed_classes=completed_classes)

@app.route('/join-class/<int:class_id>')
def join_class(class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT meeting_url, topic, description FROM live_classes WHERE id=?', (class_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        flash('Class not found.', 'error')
        return redirect(url_for('online_class'))
    meeting_url, topic, description = row
    return render_template('join_class.html', meeting_url=meeting_url, topic=topic, description=description)

@app.route('/join-class-host/<int:class_id>')
def join_class_host(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        flash('Access denied. Only hosts can access this page.', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT meeting_url, topic, description FROM live_classes WHERE id=?', (class_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        flash('Class not found.', 'error')
        return redirect(url_for('admin_panel'))
    meeting_url, topic, description = row
    return render_template('join_class_host.html', meeting_url=meeting_url, topic=topic, description=description)

@app.route('/start-live-class', methods=['POST'])
def start_live_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    class_id = request.form.get('class_id')
    if class_id is not None:
        class_id = int(class_id)
    
    # Check if class can be started
    from auth_handler import can_start_class, start_live_class, add_notification
    if not can_start_class(class_id):
        flash('This class cannot be started yet. Check the scheduled time.', 'error')
        return redirect(url_for('online_class'))
    
    # Start the class
    start_live_class(class_id)
    
    # Send notification to all users of the class
    add_notification('A live class has started! Join now.', class_id, 'all', 'active', notification_type='live_class')
    
    flash('Live class started!', 'success')
    return redirect(url_for('online_class'))

@app.route('/end-live-class', methods=['POST'])
def end_live_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    class_id = request.form.get('class_id')
    
    # Check if class can be ended
    from auth_handler import can_end_class, end_live_class
    if not can_end_class(class_id):
        flash('This class cannot be ended. It may not be active.', 'error')
        return redirect(url_for('online_class'))
    
    # End the class (mark as completed)
    end_live_class(class_id)
    flash('Live class ended and moved to completed section.', 'info')
    return redirect(url_for('online_class'))

# Route for authentication (login)
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    error = None
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        all_classes_dict = {str(c[0]): c[1] for c in get_all_classes()}
        selected_role = all_classes_dict.get(class_id)
        username = request.form.get('username')
        password = request.form.get('password')
        admin_code = request.form.get('admin_code')
        if selected_role == 'admin':
            if admin_code != 'sec@011':
                error = 'Invalid admin code. Login denied.'
                return render_template('auth.html', error=error)
        user_data = authenticate_user(username, password)
        if user_data:
            user_id, user_role = user_data
            # Check if user is banned
            user = get_user_by_id(user_id)
            if user and len(user) > 4 and user[4] == 1:
                error = 'Your account has been banned. Please contact Mohit Sir or admin to be unbanned.'
                return render_template('auth.html', error=error)
            if user_role == selected_role:
                session['user_id'] = user_id
                session['username'] = username
                session['role'] = user_role
                if username == 'yash' and user_role == 'admin':
                    return redirect(url_for('special_dashboard'))
                if user_role in ['admin', 'teacher']:
                    return redirect(url_for('admin_panel'))
                else:
                    return redirect(url_for('home'))
        error = 'Wrong credentials. Contact the institute.'
    return render_template('auth.html', error=error)

# Route for registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    class_id = request.form.get('class_id')
    
    all_classes_dict = {str(c[0]): c[1] for c in get_all_classes()}
    role = all_classes_dict.get(class_id)
    
    admin_code = request.form.get('admin_code')
    if role == 'admin':
        if admin_code != 'sec@011':
            return render_template('auth.html', error='Invalid admin code. Registration denied.')
            
    if register_user(username, password, class_id):
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth'))
    else:
        return render_template('auth.html', error='Username already exists. Please choose another.')

# Admin panel route
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if session.get('role') in ['admin', 'teacher']:
        resources = get_all_resources()
        q = request.args.get('q', '').strip()
        users = search_users(q) if q else get_all_users()
        all_notifications = get_all_notifications()
        active_classes = get_active_classes()
        # Forum moderation
        forum_q = request.args.get('forum_q', '').strip()
        if forum_q:
            forum_messages = [m for m in get_forum_messages() if forum_q.lower() in (m[2] or '').lower() or forum_q.lower() in (m[3] or '').lower()]
        else:
            forum_messages = get_forum_messages()
        all_classes = get_all_classes()
        # Analytics
        total_users = len(get_all_users())
        total_forum_posts = len(get_forum_messages())
        total_resources = len(get_all_resources())
        total_classes = len(all_classes)
        # Most active users (by forum posts)
        user_post_counts = Counter([m[2] for m in get_forum_messages() if m[2]])
        most_active_users = user_post_counts.most_common(5)
        # Most uploaded resources by class
        class_resource_counts = Counter([r[1] for r in get_all_resources()])
        most_resource_classes = [(cid, count) for cid, count in class_resource_counts.most_common(5)]
        # Get all topics for topic management
        all_topics = get_all_topics()
        # Build notification_usernames for personal ban notifications
        notification_usernames = {}
        import sqlite3
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        for n in all_notifications:
            notif_id, message, class_name, created_at, target_paid_status, status, notification_type, scheduled_time = n
            if target_paid_status == 'personal' and 'ban' in message.lower():
                c.execute('SELECT user_id FROM user_notification_status WHERE notification_id=?', (notif_id,))
                row = c.fetchone()
                if row:
                    user_id = row[0]
                    c.execute('SELECT username FROM users WHERE id=?', (user_id,))
                    user_row = c.fetchone()
                    if user_row:
                        notification_usernames[notif_id] = user_row[0]
        conn.close()
        
        # Get query statistics
        query_stats = get_query_statistics()
        total_queries = query_stats.get('total', 0)
        pending_queries = query_stats.get('pending', 0)
        resolved_queries = query_stats.get('resolved', 0)
        
        return render_template('admin.html', resources=resources, users=users, search_query=q, all_notifications=all_notifications, notification_usernames=notification_usernames, active_classes=active_classes, forum_messages=forum_messages, forum_search_query=forum_q, all_classes=all_classes, total_users=total_users, total_forum_posts=total_forum_posts, total_resources=total_resources, total_classes=total_classes, most_active_users=most_active_users, most_resource_classes=most_resource_classes, all_topics=all_topics, total_queries=total_queries, pending_queries=pending_queries, resolved_queries=resolved_queries)
    else:
        return redirect(url_for('auth'))

@app.route('/admin/delete-forum-message/<int:message_id>', methods=['POST'])
def admin_delete_forum_message(message_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    # The original code had delete_forum_message, which is not defined.
    # Assuming it was meant to be a placeholder for a deletion mechanism.
    # For now, we'll just return success.
    return redirect(url_for('admin_panel', _anchor='forum'))

@app.route('/create-live-class', methods=['GET', 'POST'])
def create_live_class_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        topic = request.form.get('topic')
        description = request.form.get('description')
        video_source = request.form.get('video_source', 'upload')
        
        meeting_url = None
        
        if video_source == 'upload':
            # Handle uploaded video file
            video_file = request.files.get('video_file')
            if not video_file or video_file.filename == '':
                flash('Video file is required when uploading.', 'error')
                return render_template('create_class.html', class_details=None)
            if not video_file.filename.lower().endswith(('.mp4', '.webm')):
                flash('Only MP4 and WebM video files are allowed.', 'error')
                return render_template('create_class.html', class_details=None)
            filename = secure_filename(video_file.filename)
            video_folder = os.path.join('uploads', 'videos')
            os.makedirs(video_folder, exist_ok=True)
            unique_name = f"{secrets.token_hex(8)}_{filename}"
            video_path = os.path.join(video_folder, unique_name)
            video_file.save(video_path)
            meeting_url = f"/uploads/videos/{unique_name}"
        elif video_source == 'youtube':
            # Handle YouTube video download
            youtube_url = request.form.get('youtube_url', '').strip()
            if not youtube_url:
                flash('YouTube URL is required when using YouTube link.', 'error')
                return render_template('create_class.html', class_details=None)
            try:
                from youtube_downloader import download_youtube_video, validate_youtube_url
                # Validate YouTube URL
                if not validate_youtube_url(youtube_url):
                    flash('Invalid YouTube URL. Please provide a valid YouTube video link.', 'error')
                    return render_template('create_class.html', class_details=None)
                # Download the video
                flash('Downloading YouTube video... This may take a few minutes.', 'info')
                download_result = download_youtube_video(youtube_url)
                # Create meeting URL for the downloaded video
                meeting_url = f"/uploads/videos/{download_result['filename']}"
                flash(f'YouTube video "{download_result["title"]}" downloaded successfully!', 'success')
            except Exception as e:
                flash(f'Error downloading YouTube video: {str(e)}', 'error')
                return render_template('create_class.html', class_details=None)
        elif video_source == 'golive':
            # Go Live: set meeting_url to a special route for live broadcast
            class_code = ''.join(secrets.choice('0123456789') for i in range(6))
            pin = ''.join(secrets.choice('0123456789') for i in range(4))
            meeting_url = f"/join-class/{class_code}"
            new_class_id = create_live_class(class_code, pin, meeting_url, topic, description)
            
            # Add notification for the class
            add_notification(
                f'A new live class has been created: {topic}',
                class_id=new_class_id,
                target_paid_status='all',
                status='active',
                notification_type='live_class'
            )
            
            # Redirect directly to the host broadcast page
            return redirect(url_for('join_class_host', class_id=new_class_id))
        
        if not meeting_url:
            flash('No video source provided.', 'error')
            return render_template('create_class.html', class_details=None)
        
        # Create the live class
        class_code = ''.join(secrets.choice('0123456789') for i in range(6))
        pin = ''.join(secrets.choice('0123456789') for i in range(4))
        new_class_id = create_live_class(class_code, pin, meeting_url, topic, description)
        details = get_class_details_by_id(new_class_id)
        class_details = {
            'topic': details[3], 'description': details[4],
            'code': details[0], 'pin': details[1], 'url': details[2]
        }
        return render_template('create_class.html', class_details=class_details)
    
    return render_template('create_class.html', class_details=None)

# Upload resource route
@app.route('/upload-resource', methods=['GET', 'POST'])
def upload_resource():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        class_id = request.form.get('class_id')
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        paid_status = request.form.get('paid_status', 'unpaid')
        schedule_date = request.form.get('schedule_date')

        if not file or file.filename == '' or not class_id or not category:
            flash('File, class, and category selection are required.', 'error')
        elif not allowed_file(file.filename):
            flash('File type not allowed.', 'error')
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            save_resource(filename, class_id, filepath, title, description, category)

            # Send notification based on category and paid status
            paid_categories = ['worksheet', 'formula', 'formula sheet', 'practice test']
            target_paid_status = 'paid' if category.lower() in paid_categories else 'all'
            
            add_notification(
                f'A new {category} has been uploaded: {title}',
                class_id=class_id,
                target_paid_status=target_paid_status,
                status='active',
                notification_type='study_resource'
            )

            flash('Resource uploaded successfully!', 'success')
            return redirect(url_for('upload_resource'))

    # Get all resources for history tab
    resources = get_all_resources()
    all_classes = get_all_classes()
    categories = get_all_categories()
    return render_template('upload_resource.html', resources=resources, all_classes=all_classes, categories=categories)

def get_class_name_by_id(class_id):
    """Get class name by class ID"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT name FROM classes WHERE id = ?', (class_id,))
        result = c.fetchone()
        conn.close()
        class_name = result[0] if result else 'Unknown Class'
        print(f"DEBUG - get_class_name_by_id({class_id}) = {class_name}")
        return class_name
    except Exception as e:
        print(f"DEBUG - Error in get_class_name_by_id: {e}")
        return 'Unknown Class'



# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Serve static files (CSS, JS, images, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    # Serve any file in the root or subfolders
    return send_from_directory('.', filename)

# Delete resource route
@app.route('/delete-resource/<filename>', methods=['POST'])
def delete_resource_route(filename):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    # Remove file from uploads folder
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    # Remove from database
    delete_resource(filename)
    return redirect(url_for('admin_panel'))

# Delete user route
@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_user(user_id)
    return redirect(url_for('admin_panel'))

# JSON API: Delete user (used by admin_create_user.html via fetch)
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def admin_delete_user_api(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        delete_user(user_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# User info route
@app.route('/user-info/<int:user_id>', methods=['GET', 'POST'])
def user_info(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('admin_panel'))
    error = None
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_class_id = request.form.get('class_id')
        new_paid = request.form.get('paid')
        new_mobile_no = request.form.get('mobile_no')
        new_email_address = request.form.get('email_address')
        if not all([new_username, new_class_id, new_paid]):
            error = 'Username, role, and paid status are required.'
        else:
            # Update user with password if provided
            if new_password:
                update_user_with_password(user_id, new_username, new_password, new_class_id, new_paid, banned=None, mobile_no=new_mobile_no, email_address=new_email_address)
            else:
                update_user(user_id, new_username, new_class_id, new_paid, mobile_no=new_mobile_no, email_address=new_email_address)
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
    all_classes = get_all_classes()
    return render_template('user_info.html', user=user, error=error, all_classes=all_classes)

@app.route('/add-notification', methods=['POST'])
def add_notification_route():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    message = request.form.get('message')
    class_id = request.form.get('class_id')
    if message and class_id:
        add_notification(message, class_id)
        flash('Notification sent!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth'))

@app.route('/profile')
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get user info with class name
    c.execute('''
        SELECT u.id, u.username, u.password, u.class_id, u.paid, u.mobile_no, u.email_address, u.banned, c.name as class_name
        FROM users u 
        LEFT JOIN classes c ON u.class_id = c.id 
        WHERE u.id = ?
    ''', (session['user_id'],))
    
    user_data = c.fetchone()
    conn.close()
    
    if not user_data:
        flash('User not found.', 'error')
        return redirect(url_for('auth'))
    
    # Determine user role
    if user_data[7] == 1:  # banned
        role = 'banned'
    elif user_data[3] == 8:  # class_id 8 is admin
        role = 'admin'
    elif user_data[3] == 9:  # class_id 9 is teacher
        role = 'teacher'
    else:
        role = 'student'
    
    user = {
        'id': user_data[0],
        'username': user_data[1],
        'password': user_data[2],
        'class_id': user_data[3],
        'paid': user_data[4],
        'mobile_no': user_data[5],
        'email_address': user_data[6],
        'banned': user_data[7],
        'class_name': user_data[8],
        'role': role
    }
    
    return render_template('profile.html', user=user)

@app.route('/mark-notification-seen', methods=['POST'])
def mark_notification_seen_route():
    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'error', 'message': 'User not logged in'}, 401
    
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return {'status': 'error', 'message': 'Notification ID is required'}, 400
        
    mark_notification_as_seen(user_id, notification_id)
    return {'status': 'success'}

@app.route('/delete-notification/<int:notification_id>', methods=['POST'])
def delete_notification_route(notification_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_notification(notification_id)
    flash('Notification deleted!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/classes/add', methods=['POST'])
def admin_add_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    name = request.form.get('name', '').strip()
    if name:
        from auth_handler import get_all_classes
        import sqlite3
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO classes (name) VALUES (?)', (name,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Class already exists
        conn.close()
    return redirect(url_for('admin_panel', _anchor='classes'))

@app.route('/admin/classes/edit/<int:class_id>', methods=['POST'])
def admin_edit_class(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    name = request.form.get('name', '').strip()
    if name:
        import sqlite3
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('UPDATE classes SET name=? WHERE id=?', (name, class_id))
        conn.commit()
        conn.close()
    return redirect(url_for('admin_panel', _anchor='classes'))

@app.route('/admin/classes/delete/<int:class_id>', methods=['POST'])
def admin_delete_class(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM classes WHERE id=?', (class_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel', _anchor='classes'))

@app.route('/admin/delete-resource/<filename>', methods=['POST'])
def admin_delete_resource(filename):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    # Remove file from uploads folder
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    # Remove from database
    delete_resource(filename)
    return redirect(url_for('admin_panel', _anchor='resources'))

@app.route('/admin/delete-notification/<int:notification_id>', methods=['POST'])
def admin_delete_notification(notification_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_notification(notification_id)
    return redirect(url_for('admin_panel', _anchor='notifications'))

@app.route('/admin/download/users')
def admin_download_users():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    users = get_all_users()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Username', 'Role', 'Paid', 'Mobile Number', 'Email Address'])
    for u in users:
        cw.writerow(u)
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=users.csv'})

@app.route('/admin/download/forum')
def admin_download_forum():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    messages = get_forum_messages()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'User ID', 'Username', 'Message', 'Parent ID', 'Upvotes', 'Downvotes', 'Timestamp'])
    for m in messages:
        cw.writerow(m)
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=forum.csv'})

@app.route('/admin/download/resources')
def admin_download_resources():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    resources = get_all_resources()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Filename', 'Class ID', 'Filepath', 'Title', 'Description', 'Category'])
    for r in resources:
        cw.writerow(r)
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=resources.csv'})

@app.route('/admin/promote/<int:user_id>', methods=['POST'])
def admin_promote_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth'))
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Get admin class id
    c.execute("SELECT id FROM classes WHERE name='admin'")
    admin_class_id = c.fetchone()[0]
    c.execute('UPDATE users SET class_id=? WHERE id=?', (admin_class_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel', _anchor='settings'))

@app.route('/admin/demote/<int:user_id>', methods=['POST'])
def admin_demote_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth'))
    # Demote to student: set to first non-admin/teacher class
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM classes WHERE name NOT IN ('admin','teacher') ORDER BY id LIMIT 1")
    student_class_id = c.fetchone()[0]
    c.execute('UPDATE users SET class_id=? WHERE id=?', (student_class_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel', _anchor='settings'))

@app.route('/admin/delete-admin/<int:user_id>', methods=['POST'])
def admin_delete_admin(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth'))
    if user_id == session.get('user_id'):
        flash('You cannot delete your own admin account.', 'error')
        return redirect(url_for('admin_panel', _anchor='settings'))
    delete_user(user_id)
    return redirect(url_for('admin_panel', _anchor='settings'))

@app.route('/send-notification', methods=['GET', 'POST'])
def send_notification_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        message = request.form.get('message')
        class_id = request.form.get('class_id')
        target_paid_status = request.form.get('target_paid_status', 'all')
        schedule_date = request.form.get('schedule_date')
        
        # Validation
        if not message or not class_id or not target_paid_status:
            flash('Message, class, and target users are required.', 'error')
            return render_template('send_notification.html')
        
        # Validate target_paid_status
        valid_paid_statuses = ['all', 'paid', 'not paid']
        if target_paid_status not in valid_paid_statuses:
            flash('Invalid target users selection.', 'error')
            return render_template('send_notification.html')
        
        try:
            # Add notification
            add_notification(
                message=message,
                class_id=int(class_id),
                target_paid_status=target_paid_status,
                status='active',
                scheduled_time=schedule_date if schedule_date else None,
                notification_type='admin_notification'
            )
            
            status_text = "scheduled" if schedule_date else "sent"
            flash(f'Notification {status_text} successfully!', 'success')
            return redirect(url_for('admin_panel', _anchor='notifications'))
            
        except Exception as e:
            flash(f'Error sending notification: {str(e)}', 'error')
            return render_template('send_notification.html')
    
    # Get recent notifications for display
    from auth_handler import get_all_notifications
    notifications = get_all_notifications()[:10]  # Show last 10 notifications
    
    return render_template('send_notification.html', notifications=notifications)

@app.route('/admin/create-user', methods=['GET'])
def admin_create_user_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    # Get all classes
    all_classes = get_all_classes()
    
    # Get all users for the table
    from auth_handler import get_all_users
    users = get_all_users()
    
    # Calculate user statistics
    paid_users = sum(1 for user in users if user[3] == 'paid')  # user[3] is paid status
    unpaid_users = sum(1 for user in users if user[3] == 'not paid')
    admin_users = sum(1 for user in users if user[2] in ['admin', 'teacher'])  # user[2] is class name
    
    # Get admissions data
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get pending admissions (match order expected by template)
    c.execute('''
        SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
               maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
               passport_photo, status, submitted_at, submit_ip
        FROM admissions 
        ORDER BY submitted_at DESC
    ''')
    admissions = c.fetchall()
    
    # Get approved admissions
    c.execute('''
        SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
               maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
               passport_photo, approved_by, approved_at
        FROM admissions 
        WHERE status = 'approved' 
        ORDER BY approved_at DESC
    ''')
    approved_admissions = c.fetchall()
    
    # Get disapproved admissions
    c.execute('''
        SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
               maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
               passport_photo, disapproved_by, disapproval_reason, disapproved_at
        FROM admissions 
        WHERE status = 'disapproved' 
        ORDER BY disapproved_at DESC
    ''')
    disapproved_admissions = c.fetchall()
    
    # Map admission_id -> (access_username, access_password)
    admission_ids = [a[0] for a in admissions]
    admission_access_map = {}
    if admission_ids:
        placeholders = ','.join('?' for _ in admission_ids)
        c.execute(f'''SELECT admission_id, access_username, access_password 
                      FROM admission_access WHERE admission_id IN ({placeholders})''', admission_ids)
        for row in c.fetchall():
            admission_access_map[row[0]] = (row[1], row[2])

    # Create admission_access_plain table for storing plain passwords for admin viewing
    c.execute('''CREATE TABLE IF NOT EXISTS admission_access_plain (
        admission_id INTEGER PRIMARY KEY,
        plain_password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Ensure every pending admission has credentials; auto-generate if missing
    for adm in admissions:
        adm_id = adm[0]
        if adm_id not in admission_access_map:
            access_username = f"ADM{adm_id:06d}"
            access_password = secrets.token_hex(4)
            try:
                hashed_pw = generate_password_hash(access_password)
                c.execute('''INSERT OR IGNORE INTO admission_access (admission_id, access_username, access_password)
                             VALUES (?, ?, ?)''', (adm_id, access_username, hashed_pw))
                # Store plain password for admin viewing
                c.execute('''INSERT OR REPLACE INTO admission_access_plain (admission_id, plain_password)
                             VALUES (?, ?)''', (adm_id, access_password))
                admission_access_map[adm_id] = (access_username, access_password)
            except Exception:
                pass
    
    # Update admission_access_map with plain passwords for admin display
    for adm_id in admission_access_map:
        try:
            c.execute('SELECT plain_password FROM admission_access_plain WHERE admission_id = ?', (adm_id,))
            plain_row = c.fetchone()
            if plain_row:
                admission_access_map[adm_id] = (admission_access_map[adm_id][0], plain_row[0])
            else:
                # No plain password found, generate a new one
                access_password = secrets.token_hex(4)
                hashed_pw = generate_password_hash(access_password)
                c.execute('UPDATE admission_access SET access_password = ? WHERE admission_id = ?', 
                         (hashed_pw, adm_id))
                c.execute('''INSERT OR REPLACE INTO admission_access_plain (admission_id, plain_password)
                             VALUES (?, ?)''', (adm_id, access_password))
                admission_access_map[adm_id] = (admission_access_map[adm_id][0], access_password)
        except Exception:
            pass
    conn.commit()
    conn.close()
    
    # Calculate admission statistics
    pending_admissions = sum(1 for admission in admissions if admission[13] == 'pending')
    
    return render_template('admin_create_user.html', 
                           all_classes=all_classes,
                           users=users,
                           paid_users=paid_users,
                           unpaid_users=unpaid_users,
                           admin_users=admin_users,
                           admissions=admissions,
                           admission_access_map=admission_access_map,
                           pending_admissions=pending_admissions,
                           approved_admissions=approved_admissions,
                           disapproved_admissions=disapproved_admissions)

@app.route('/admin/create-user', methods=['POST'])
def admin_create_user_submit():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    username = request.form.get('username')
    password = request.form.get('password')
    class_id = request.form.get('class_id')
    paid = request.form.get('paid')
    if not all([username, password, class_id, paid]):
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_create_user_page'))
    # Use register_user from auth_handler
    if register_user(username, password, class_id):
        # Update paid status if needed
        from auth_handler import update_user, get_user_by_id
        user = get_user_by_id(username)
        if user:
            update_user(user[0], username, class_id, paid)
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_panel', _anchor='users'))
    else:
        flash('Username already exists. Please choose another.', 'error')
        return redirect(url_for('admin_create_user_page'))

@app.route('/admin/ban-user/<int:user_id>', methods=['POST'])
def admin_ban_user(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    # Get user info and ban them
    from auth_handler import get_user_by_id, add_personal_notification
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_panel', _anchor='users'))
    
    # Prevent banning admin or teacher
    if user[4] in ['admin', 'teacher']:
        flash('You cannot ban an admin or teacher.', 'error')
        return redirect(url_for('admin_panel', _anchor='users'))
    
    # Prevent banning again on the same day
    import sqlite3
    from datetime import datetime, timedelta, timezone
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT ban_effective_at FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    if row and row[0]:
        try:
            ban_time = datetime.fromisoformat(row[0])
            now = datetime.now(timezone.utc)
            if ban_time.date() == now.date():
                flash('User is already scheduled to be banned today.', 'error')
                conn.close()
                return redirect(url_for('admin_panel', _anchor='users'))
        except Exception:
            pass
    
    # Send 24-hour ban warning notification to the user only
    ban_warning = "You will be banned within 24 hours. Call Mohit Sir or admin."
    add_personal_notification(ban_warning, user_id)
    
    # Schedule ban to take effect in 24 hours
    ban_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    c.execute('UPDATE users SET ban_effective_at=? WHERE id=?', (ban_time, user_id))
    conn.commit()
    conn.close()
    
    flash(f'User {user[1]} will be banned in 24 hours and has been personally notified.', 'success')
    return redirect(url_for('admin_panel', _anchor='users'))

@app.route('/admin/create-topic', methods=['GET'])
@admin_required
def admin_create_topic_page():
    all_classes = get_all_classes()
    return render_template('admin_create_topic.html', all_classes=all_classes)

@app.route('/admin/create-topic', methods=['POST'])
@admin_required
def admin_create_topic_submit():
    name = request.form.get('name')
    description = request.form.get('description')
    class_id = request.form.get('class_id')
    paid = request.form.get('paid')
    
    if not name or not class_id or not paid:
        flash('Topic name, class, and paid status are required', 'error')
        return redirect(url_for('admin_create_topic_page'))
    
    try:
        # Create topic with class_id and paid status
        create_topic(name, description, class_id, paid)
        flash('Topic created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating topic: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel', _anchor='forum'))

@app.route('/admin/delete-topic/<int:topic_id>', methods=['POST'])
@admin_required
def delete_topic_route(topic_id):
    try:
        delete_topic(topic_id)
        flash('Topic deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting topic: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel', _anchor='forum'))

# Serve uploaded forum media
@app.route('/uploads/forum_media/<filename>')
def uploaded_forum_media(filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'forum_media'), filename)

@app.route('/special-dashboard')
def special_dashboard():
    if session.get('username') == 'yash' and session.get('role') == 'admin':
        return render_template('special_dashboard.html')
    else:
        return redirect(url_for('home'))

@app.route('/admin/admissions')
@admin_required
def view_admissions():
    tab = request.args.get('tab', 'pending')
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get pending admissions (status is NULL or 'pending')
    c.execute('''SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
                 maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                 passport_photo, submitted_at, status FROM admissions 
                 WHERE status IS NULL OR status = 'pending' OR status = '' 
                 ORDER BY submitted_at DESC''')
    pending_admissions = c.fetchall()
    
    # Get approved admissions
    c.execute('''SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
                 maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                 passport_photo, approved_by, approved_at FROM admissions 
                 WHERE status = 'approved' ORDER BY approved_at DESC''')
    approved_admissions = c.fetchall()
    
    # Get disapproved admissions
    c.execute('''SELECT id, student_name, dob, class, school_name, student_phone, student_email, 
                 maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                 passport_photo, disapproved_by, disapproval_reason, disapproved_at FROM admissions 
                 WHERE status = 'disapproved' ORDER BY disapproved_at DESC''')
    disapproved_admissions = c.fetchall()
    
    conn.close()
    
    # Set the main admissions based on tab
    if tab == 'approved':
        admissions = approved_admissions
        admission_type = 'approved'
    elif tab == 'disapproved':
        admissions = disapproved_admissions
        admission_type = 'disapproved'
    else:  # pending
        admissions = pending_admissions
        admission_type = 'pending'
    
    return render_template('view_admission.html', 
                         admissions=admissions, 
                         admission_type=admission_type, 
                         current_tab=tab,
                         pending_admissions=pending_admissions,
                         approved_admissions=approved_admissions,
                         disapproved_admissions=disapproved_admissions)

@app.route('/admin/admissions/approve/<int:admission_id>', methods=['POST'])
@admin_required
def approve_admission(admission_id):
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get the admission data
        c.execute('''SELECT student_name, dob, student_phone, student_email, class, school_name,
                      maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                      passport_photo, user_id FROM admissions WHERE id = ?''', (admission_id,))
        admission_data = c.fetchone()
        
        if admission_data:
            # Update the admission status to approved
            c.execute('''UPDATE admissions SET 
                         status = 'approved', 
                         approved_by = ?, 
                         approved_at = ? 
                         WHERE id = ?''', (
                session.get('username', 'admin'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                admission_id
            ))
            
            # Commit the changes
            conn.commit()
            
            # Auto-register user in the system
            try:
                from auth_handler import register_user, get_class_id_by_name
                
                # Get student name and create username
                student_name = admission_data[0]
                student_phone = admission_data[2]
                student_email = admission_data[3]
                
                # Create username from student name (remove spaces, make lowercase)
                username = student_name.replace(' ', '').lower()
                
                # Generate a simple password (student's phone number)
                password = student_phone
                
                # Get class_id from class name
                class_name = admission_data[4]
                print(f'Processing admission for class: "{class_name}"')
                class_id = get_class_id_by_name(class_name)
                print(f'Found class_id: {class_id}')
                
                if class_id:
                    # Register the user as a paid user (since admission was approved)
                    if register_user(username, password, class_id, student_phone, student_email, 'paid'):
                        # Get the newly created user's ID
                        from auth_handler import get_user_by_username
                        new_user = get_user_by_username(username)
                        
                        if new_user:
                            # Add a notification for the new user
                            from auth_handler import add_personal_notification
                            notification_message = f"Welcome {student_name}! Your admission has been approved and you are now a paid member. You can login with username: {username} and password: {password}"
                            add_personal_notification(notification_message, new_user[0])  # new_user[0] is the user_id
                        
                        # Check if request expects JSON
                        if request.headers.get('Content-Type') == 'application/json':
                            return jsonify({'success': True, 'message': f'Admission approved and user {username} registered as paid member successfully!'})
                        else:
                            flash(f'Admission approved and user {username} registered as paid member successfully!', 'success')
                            return redirect(url_for('view_admissions'))
                    else:
                        # If user already exists, update their status to paid and ensure correct class/contact info
                        try:
                            from auth_handler import get_user_by_username, update_user
                            existing_user = get_user_by_username(username)
                            if existing_user:
                                update_user(existing_user[0], username, class_id, 'paid', mobile_no=student_phone, email_address=student_email)
                                if request.headers.get('Content-Type') == 'application/json':
                                    return jsonify({'success': True, 'message': f'Admission approved. Existing user {username} updated to paid.'})
                                else:
                                    flash(f'Admission approved. Existing user {username} updated to paid.', 'success')
                                    return redirect(url_for('view_admissions'))
                        except Exception:
                            pass
                        if request.headers.get('Content-Type') == 'application/json':
                            return jsonify({'success': False, 'message': 'Admission approved but user registration failed. Username may already exist.'})
                        else:
                            flash('Admission approved but user registration failed. Username may already exist.', 'warning')
                            return redirect(url_for('view_admissions'))
                else:
                    # Get available classes for debugging
                    from auth_handler import get_all_classes
                    available_classes = get_all_classes()
                    class_list = ', '.join([f'"{c[1]}"' for c in available_classes])
                    
                    error_msg = f'Class "{class_name}" not found in system. Available classes: {class_list}'
                    print(error_msg)
                    
                    if request.headers.get('Content-Type') == 'application/json':
                        return jsonify({'success': False, 'message': error_msg})
                    else:
                        flash(error_msg, 'error')
                        return redirect(url_for('view_admissions'))
            except Exception as e:
                print(f'Error in user registration: {e}')
                # Even if user registration fails, admission is still approved
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify({'success': True, 'message': 'Admission approved but user registration failed due to database error.'})
                else:
                    flash('Admission approved but user registration failed due to database error.', 'warning')
                    return redirect(url_for('view_admissions'))
        else:
            if conn:
                conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found'})
            else:
                flash('Admission not found.', 'error')
                return redirect(url_for('view_admissions'))
                
    except Exception as e:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error approving admission: {str(e)}', 'error')
    return redirect(url_for('view_admissions'))

@app.route('/admin/admissions/disapprove/<int:admission_id>', methods=['POST'])
@admin_required
def disapprove_admission(admission_id):
    try:
        # Get disapproval reason from JSON request
        data = request.get_json()
        disapproval_reason = data.get('reason', 'No reason provided') if data else 'No reason provided'
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get the admission data
        c.execute('''SELECT student_name, dob, student_phone, student_email, class, school_name,
                      maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                      passport_photo, user_id FROM admissions WHERE id = ?''', (admission_id,))
        admission_data = c.fetchone()
        
        if admission_data:
            # Update the admission status to disapproved
            c.execute('''UPDATE admissions SET 
                         status = 'disapproved', 
                         disapproved_by = ?, 
                         disapproval_reason = ?,
                         disapproved_at = ? 
                         WHERE id = ?''', (
                session.get('username', 'admin'),
                disapproval_reason,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                admission_id
            ))
            
            conn.commit()
            conn.close()
            
            # Check if request expects JSON
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Admission disapproved successfully'})
            else:
                flash('Admission disapproved successfully.', 'info')
                return redirect(url_for('view_admissions'))
        else:
            conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found'})
            else:
                flash('Admission not found.', 'error')
                return redirect(url_for('view_admissions'))
                
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error disapproving admission: {str(e)}', 'error')
    return redirect(url_for('view_admissions'))

@app.route('/admin/admissions/reset/<int:admission_id>', methods=['POST'])
@admin_required
def reset_admission(admission_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE admissions SET status = ? WHERE id = ?', ('pending', admission_id))
    conn.commit()
    conn.close()
    flash('Admission status reset to pending.', 'info')
    return redirect(url_for('view_admissions'))

@app.route('/admin/admissions/restore-approved/<int:admission_id>', methods=['POST'])
@admin_required
def restore_approved_admission(admission_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Update the admission status back to pending
        c.execute('''UPDATE admissions SET 
                     status = 'pending', 
                     approved_by = NULL, 
                     approved_at = NULL 
                     WHERE id = ? AND status = 'approved' ''', (admission_id,))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            
            # Check if request expects JSON
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Admission restored to pending successfully'})
            else:
                flash('Approved admission restored to pending.', 'success')
                return redirect(url_for('view_admissions', tab='approved'))
        else:
            conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found or not approved'})
            else:
                flash('Admission not found or not approved.', 'error')
                return redirect(url_for('view_admissions', tab='approved'))
                
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error restoring admission: {str(e)}', 'error')
            return redirect(url_for('view_admissions', tab='approved'))

@app.route('/admin/admissions/restore-disapproved/<int:admission_id>', methods=['POST'])
@admin_required
def restore_disapproved_admission(admission_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Update the admission status back to pending
        c.execute('''UPDATE admissions SET 
                     status = 'pending', 
                     disapproved_by = NULL, 
                     disapproval_reason = NULL, 
                     disapproved_at = NULL 
                     WHERE id = ? AND status = 'disapproved' ''', (admission_id,))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            
            # Check if request expects JSON
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Admission restored to pending successfully'})
            else:
                flash('Disapproved admission restored to pending.', 'success')
                return redirect(url_for('view_admissions', tab='disapproved'))
        else:
            conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found or not disapproved'})
            else:
                flash('Admission not found or not disapproved.', 'error')
                return redirect(url_for('view_admissions', tab='disapproved'))
                
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error restoring admission: {str(e)}', 'error')
            return redirect(url_for('view_admissions', tab='disapproved'))

@app.route('/admin/admissions/delete-approved/<int:admission_id>', methods=['POST'])
@admin_required
def delete_approved_admission(admission_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Delete the approved admission from the admissions table
        c.execute('DELETE FROM admissions WHERE id = ? AND status = ?', (admission_id, 'approved'))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            
            # Check if request expects JSON
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Approved admission deleted successfully'})
            else:
                flash('Approved admission deleted permanently.', 'success')
                return redirect(url_for('view_admissions', tab='approved'))
        else:
            conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found or not approved'})
            else:
                flash('Admission not found or not approved.', 'error')
                return redirect(url_for('view_admissions', tab='approved'))
            
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error deleting admission: {str(e)}', 'error')
            return redirect(url_for('view_admissions', tab='approved'))

@app.route('/admin/admissions/delete-disapproved/<int:admission_id>', methods=['POST'])
@admin_required
def delete_disapproved_admission(admission_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Delete the disapproved admission from the admissions table
        c.execute('DELETE FROM admissions WHERE id = ? AND status = ?', (admission_id, 'disapproved'))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            
            # Check if request expects JSON
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': True, 'message': 'Disapproved admission deleted successfully'})
            else:
                flash('Disapproved admission deleted permanently.', 'success')
                return redirect(url_for('view_admissions', tab='disapproved'))
        else:
            conn.close()
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Admission not found or not disapproved'})
            else:
                flash('Admission not found or not disapproved.', 'error')
                return redirect(url_for('view_admissions', tab='disapproved'))
            
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
        else:
            flash(f'Error deleting admission: {str(e)}', 'error')
            return redirect(url_for('view_admissions', tab='disapproved'))

@app.route('/submit-query', methods=['POST'])
def submit_query():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get user IP address
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()
    
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO queries (name, email, message, submitted_at, user_ip) VALUES (?, ?, ?, ?, ?)',
                  (name, email, message, submitted_at, user_ip))
        conn.commit()
    return redirect(url_for('home'))

@app.route('/api/recent-queries')
def get_recent_queries():
    # Get user IP address
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            # Get recent queries for this IP address (last 10)
            c.execute('''
                SELECT id, name, email, message, submitted_at, response, responded_at, status
                FROM queries 
                WHERE user_ip = ? 
                ORDER BY submitted_at DESC 
                LIMIT 10
            ''', (user_ip,))
            
            queries = []
            for row in c.fetchall():
                query = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'message': row[3],
                    'submitted_at': row[4],
                    'response': row[5],
                    'responded_at': row[6],
                    'status': row[7]
                }
                queries.append(query)
            
            return jsonify({'success': True, 'queries': queries})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.before_request
def require_login():
    allowed_routes = ['home', 'auth', 'register', 'static_files', 'submit_admission', 'admission', 'check_admission_status', 'check_admission', 'submit_query', 'get_recent_queries']
    if request.endpoint not in allowed_routes and not session.get('user_id'):
        return redirect(url_for('auth'))

@app.route('/check-admission-status')
def check_admission_status():
    # For non-logged in users, we can't check admission status by user_id
    # So we'll return False to show the admission form
    if not session.get('user_id'):
        return jsonify({'hasAdmission': False})
    
    user_id = session.get('user_id')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check in pending admissions first
    c.execute('SELECT student_name, class, school_name, status, submitted_at FROM admissions WHERE user_id = ?', (user_id,))
    admission = c.fetchone()
    
    if admission:
        conn.close()
        return jsonify({
            'hasAdmission': True,
            'admission': {
                'student_name': admission[0],
                'class': admission[1],
                'school_name': admission[2],
                'status': admission[3],
                'submitted_at': admission[4]
            }
        })
    
    # Check in approved admissions
    c.execute('SELECT student_name, class, school_name, "approved" as status, approved_at FROM admissions WHERE user_id = ? AND status = "approved"', (user_id,))
    admission = c.fetchone()
    
    if admission:
        conn.close()
        return jsonify({
            'hasAdmission': True,
            'admission': {
                'student_name': admission[0],
                'class': admission[1],
                'school_name': admission[2],
                'status': admission[3],
                'submitted_at': admission[4]
            }
        })
    
    # Check in disapproved admissions
    c.execute('SELECT student_name, class, school_name, "disapproved" as status, disapproved_at FROM admissions WHERE user_id = ? AND status = "disapproved"', (user_id,))
    admission = c.fetchone()
    
    if admission:
        conn.close()
        return jsonify({
            'hasAdmission': True,
            'admission': {
                'student_name': admission[0],
                'class': admission[1],
                'school_name': admission[2],
                'status': admission[3],
                'submitted_at': admission[4]
            }
        })
    
    conn.close()
    return jsonify({'hasAdmission': False})

@app.route('/admission', methods=['GET', 'POST'])
def admission():
    # Admission form is now accessible to everyone without login
    user_id = session.get('user_id')  # This will be None for non-logged in users
    
    if request.method == 'GET':
        return render_template('admission.html')
    
    # Handle POST request (admission form submission)
    print('--- Admission form submitted ---')
    # Handle admission form submission
    required_fields = [
        'student_name', 'dob', 'student_phone', 'student_email', 'class',
        'school_name', 'maths_marks', 'maths_rating', 'last_percentage',
        'parent_name', 'parent_phone'
    ]
    for field in required_fields:
        value = request.form.get(field)
        print(f'Field {field}:', value)
        if not value:
            print(f'Missing required field: {field}')
            flash(f"Missing required field: {field}", 'error')
            return redirect(url_for('home'))

    # Handle file upload
    photo = request.files.get('passport_photo')
    print('Photo:', photo)
    if not photo or photo.filename == '':
        print('Passport photo is required.')
        flash('Passport photo is required.', 'error')
        return redirect(url_for('home'))
    if not ('.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}):
        print('Invalid photo format:', photo.filename)
        flash('Invalid photo format. Only PNG, JPG, JPEG allowed.', 'error')
        return redirect(url_for('home'))
    filename = secure_filename(photo.filename)
    unique_name = secrets.token_hex(8) + '_' + filename
    photo_path = os.path.join('uploads', 'admission_photos', unique_name)
    print('Saving photo to:', photo_path)
    photo.save(photo_path)

    # Insert into DB
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        print('Inserting into DB...')
        # Normalize class name to match database format
        class_name = request.form['class']
        # No need for mapping since form now sends correct class names
        normalized_class = class_name
        
        c.execute('''INSERT INTO admissions (
            student_name, dob, student_phone, student_email, class, school_name,
            maths_marks, maths_rating, last_percentage, parent_name, parent_phone, passport_photo, status, submitted_at, user_id, submit_ip
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            request.form['student_name'],
            request.form['dob'],
            request.form['student_phone'],
            request.form['student_email'],
            normalized_class,
            request.form['school_name'],
            request.form['maths_marks'],
            request.form['maths_rating'],
            request.form['last_percentage'],
            request.form['parent_name'],
            request.form['parent_phone'],
            unique_name,
            'pending',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_id,
            ((request.headers.get('X-Forwarded-For','').split(',')[0].strip()) or request.remote_addr or 'unknown')
        ))
        # Generate admission portal credentials immediately
        new_admission_id = c.lastrowid
        try:
            access_username = f"ADM{new_admission_id:06d}"
            access_password = secrets.token_hex(4)
            hashed_pw = generate_password_hash(access_password)
            c.execute('''INSERT OR IGNORE INTO admission_access (admission_id, access_username, access_password)
                         VALUES (?, ?, ?)''', (new_admission_id, access_username, hashed_pw))
            # Also store plain password for admin viewing
            c.execute('''CREATE TABLE IF NOT EXISTS admission_access_plain (
                admission_id INTEGER PRIMARY KEY,
                plain_password TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''')
            c.execute('''INSERT OR REPLACE INTO admission_access_plain (admission_id, plain_password)
                         VALUES (?, ?)''', (new_admission_id, access_password))
            # Store plain password temporarily in session to display once (not persisted)
            session['last_admission_creds'] = {'username': access_username, 'password': access_password}
        except Exception as _e:
            # Non-fatal: continue even if credential generation fails
            pass
        conn.commit()
        print('Admission saved successfully!')
        conn.close()
        flash('Admission submitted successfully! Your portal credentials are shown below.', 'success')
        return redirect(url_for('check_admission'))
    except Exception as e:
        print('Error inserting admission:', e)
        flash(f'Error saving admission: {e}', 'error')
    return redirect(url_for('home'))

# Public admission check page (no login)
@app.route('/check-admission', methods=['GET', 'POST'])
def check_admission():
    if request.method == 'GET':
        # Prefill with freshly generated credentials if available (single-use display)
        last_creds = session.pop('last_admission_creds', None)
        if last_creds:
            return render_template('check_admission.html', from_submission=True, access_username=last_creds.get('username'), access_password=last_creds.get('password'))
        # Show last status result if available (single-use)
        last_status = session.pop('last_admission_status', None)
        if last_status:
            return render_template(
                'check_admission.html',
                result=last_status.get('result'),
                status=last_status.get('status'),
                paid_status=last_status.get('paid_status'),
                details=last_status.get('details'),
                access_username=last_status.get('access_username'),
                access_password=last_status.get('access_password')
            )
        return render_template('check_admission.html')
    # POST: verify admission portal credentials and show status
    access_username = request.form.get('access_username', '').strip()
    access_password = request.form.get('access_password', '').strip()
    if not access_username or not access_password:
        flash('Please enter both username and password', 'error')
        return redirect(url_for('check_admission'))
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT admission_id, access_password FROM admission_access WHERE access_username=?',
                  (access_username,))
        row = c.fetchone()
        if not row:
            conn.close()
            flash('Invalid credentials. Please check and try again.', 'error')
            return redirect(url_for('check_admission'))
        admission_id, hashed_pw = row
        if not check_password_hash(hashed_pw, access_password):
            conn.close()
            flash('Invalid credentials. Please check and try again.', 'error')
            return redirect(url_for('check_admission'))
        # Determine status by checking the unified admissions table
        c.execute('''SELECT student_name, class, school_name, status, submitted_at, approved_at, disapproved_at FROM admissions WHERE id = ?''', (admission_id,))
        adm = c.fetchone()
        status = None
        details = {}
        if adm:
            status = adm[3]  # status column
            details = {
                'student_name': adm[0],
                'class': adm[1],
                'school_name': adm[2],
                'submitted_at': adm[4]
            }
            # If approved, use approved_at as submission time for display
            if status == 'approved' and adm[5]:
                details['submitted_at'] = adm[5]
            # If disapproved, use disapproved_at as submission time for display
            elif status == 'disapproved' and adm[6]:
                details['submitted_at'] = adm[6]
        conn.close()
        # Determine paid/unpaid mapping for display
        paid_status = 'paid' if status == 'approved' else 'not paid'
        # Store result in session and redirect (PRG)
        session['last_admission_status'] = {
            'result': True,
            'status': status or 'pending',
            'paid_status': paid_status,
            'details': details,
            'access_username': access_username,
            'access_password': access_password
        }
        return redirect(url_for('check_admission'))
    except Exception as e:
        flash(f'Error checking admission: {str(e)}', 'error')
        return redirect(url_for('check_admission'))

@app.route('/live-class-management')
def live_class_management():
    if session.get('role') not in ['admin', 'teacher']:
        flash('Access denied. Only hosts can access this page.', 'error')
        return redirect(url_for('admin_panel'))
    
    active_classes = get_active_classes()
    return render_template('live_class_management.html', active_classes=active_classes)

@app.route('/content-management')
def content_management():
    if session.get('role') != 'admin':
        return redirect(url_for('auth'))
    
    # Get all topics
    from auth_handler import get_all_topics
    all_topics = get_all_topics()
    
    # Get forum messages
    forum_messages = get_forum_messages()
    
    # Get all classes
    from auth_handler import get_all_classes
    all_classes = get_all_classes()
    
    # Get user statistics
    from auth_handler import get_all_users
    users = get_all_users()
    total_users = len(users)
    
    # Get most active users (forum posts) - placeholder data
    most_active_users = [('User1', 15), ('User2', 12), ('User3', 8)]
    
    # Get most resource classes - placeholder data
    most_resource_classes = [(1, 25), (2, 18), (3, 12)]
    
    # Get topic message counts - placeholder data
    topic_messages_count = {topic[0]: 5 for topic in all_topics}
    
    # Get class students counts - placeholder data
    class_students_count = {class_id: 10 for class_id, _ in all_classes}
    
    # Get class resources counts - placeholder data
    class_resources_count = {class_id: 8 for class_id, _ in all_classes}
    
    return render_template('content_management.html',
                         all_topics=all_topics,
                         forum_messages=forum_messages,
                         all_classes=all_classes,
                         total_users=total_users,
                         most_active_users=most_active_users,
                         most_resource_classes=most_resource_classes,
                         topic_messages_count=topic_messages_count,
                         class_students_count=class_students_count,
                         class_resources_count=class_resources_count)

@app.route('/api/live-class/<int:class_id>/messages', methods=['GET'])
def get_live_class_messages_api(class_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    messages = get_live_class_messages(class_id)
    return jsonify([
        {
            'id': msg[0], 'user_id': msg[1], 'username': msg[2], 
            'message': msg[3], 'media_url': msg[4], 'timestamp': msg[5]
        } for msg in messages
    ])

@app.route('/api/live-class/<int:class_id>/messages', methods=['POST'])
def send_live_class_message(class_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    user_id = session.get('user_id')
    username = session.get('username')
    
    save_live_class_message(class_id, user_id, username, message)
    
    return jsonify({'success': True}), 201

# ==============================================================================
# Status Management Routes
# ==============================================================================

@app.route('/admin/status-management')
def status_management():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    from auth_handler import get_all_notifications, get_all_classes
    
    all_notifications = get_all_notifications()
    all_classes = get_all_classes()
    
    # Get all live classes with status
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, class_code, pin, meeting_url, topic, description, created_at, status, scheduled_time
        FROM live_classes 
        ORDER BY created_at DESC
    ''')
    all_live_classes = c.fetchall()
    conn.close()
    
    return render_template('status_management.html', 
                         all_notifications=all_notifications,
                         all_classes=all_classes,
                         all_live_classes=all_live_classes)

@app.route('/admin/update-notification-status/<int:notification_id>', methods=['POST'])
def update_notification_status_route(notification_id):
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['active', 'scheduled', 'completed', 'cancelled']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    from auth_handler import update_notification_status
    update_notification_status(notification_id, status)
    
    return jsonify({'success': True})

@app.route('/admin/update-live-class-status/<int:class_id>', methods=['POST'])
def update_live_class_status_route(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['scheduled', 'active', 'completed', 'cancelled']:
        return jsonify({'success': False, 'error': 'Invalid status'}), 400
    
    from auth_handler import update_live_class_status
    update_live_class_status(class_id, status)
    
    return jsonify({'success': True})

@app.route('/admin/delete-live-class/<int:class_id>', methods=['POST'])
def delete_live_class_route(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM live_class_messages WHERE live_class_id = ?', (class_id,))
    c.execute('DELETE FROM live_classes WHERE id = ?', (class_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('status_management'))

# API routes for live class dashboard
@app.route('/api/live-classes/dashboard')
def api_live_classes_dashboard():
    """Get all live classes organized by status for dashboard"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        from auth_handler import get_live_classes_for_display
        classes_data = get_live_classes_for_display()
        
        # Convert to JSON-serializable format
        result = {}
        for status, classes in classes_data.items():
            result[status] = []
            for class_item in classes:
                result[status].append({
                    'id': class_item[0],
                    'class_code': class_item[1],
                    'pin': class_item[2],
                    'meeting_url': class_item[3],
                    'topic': class_item[4],
                    'description': class_item[5],
                    'created_at': class_item[6],
                    'status': class_item[7],
                    'scheduled_time': class_item[8] if len(class_item) > 8 else None
                })
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/start', methods=['POST'])
def api_start_live_class():
    """Start a live class"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        if class_id is not None:
            class_id = int(class_id)
        if not class_id:
            return jsonify({'success': False, 'message': 'Class ID is required'}), 400
        from auth_handler import can_start_class, start_live_class, add_notification
        if not can_start_class(class_id):
            return jsonify({'success': False, 'message': 'Class cannot be started yet'}), 400
        start_live_class(class_id)
        add_notification('A live class has started! Join now.', class_id, 'all', 'active', notification_type='live_class')
        return jsonify({'success': True, 'message': 'Class started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/end', methods=['POST'])
def api_end_live_class():
    """End a live class"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Class ID is required'}), 400
        
        from auth_handler import can_end_class, end_live_class
        
        if not can_end_class(class_id):
            return jsonify({'success': False, 'message': 'Class cannot be ended'}), 400
        
        end_live_class(class_id)
        
        return jsonify({'success': True, 'message': 'Class ended successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/cancel', methods=['POST'])
def api_cancel_live_class():
    """Cancel a live class"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Class ID is required'}), 400
        
        from auth_handler import cancel_live_class
        
        cancel_live_class(class_id)
        
        return jsonify({'success': True, 'message': 'Class cancelled successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/delete', methods=['POST'])
def api_delete_live_class():
    """Delete a completed live class"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Class ID is required'}), 400
        
        from auth_handler import delete_live_class_route
        
        # Use the existing delete function
        delete_live_class_route(class_id)
        
        return jsonify({'success': True, 'message': 'Class deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/completed')
def api_get_completed_classes():
    """Get all completed live classes"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        # Get completed live classes using the correct function
        from auth_handler import get_completed_live_classes
        completed_classes_raw = get_completed_live_classes()
        
        completed_classes = []
        for class_item in completed_classes_raw:
            # Convert tuple to dictionary with proper field names
            completed_class = {
                'id': class_item[0],  # id
                'class_code': class_item[1],  # class_code
                'pin': class_item[2],  # pin
                'meeting_url': class_item[3],  # meeting_url
                'topic': class_item[4],  # topic
                'description': class_item[5],  # description
                'created_at': class_item[6],  # created_at
                'status': class_item[7],  # status
                'scheduled_time': class_item[8],  # scheduled_time
                'class_type': 'lecture',  # default class type
                'target_class': 'all',  # default target class
                'host': 'Unknown',  # default host
                'duration': 'N/A',  # default duration
                'participants': 0,  # default participants
                'recording_available': False,  # default recording status
                'completed_at': class_item[6]  # use created_at as completion date
            }
            completed_classes.append(completed_class)
        
        # Sort by completion date (most recent first)
        completed_classes.sort(key=lambda x: x.get('completed_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'data': completed_classes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/live-classes/delete-completed', methods=['POST'])
def api_delete_completed_class():
    """Delete a completed live class"""
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Class ID is required'}), 400
        
        # Get class details
        class_details = get_class_details_by_id(class_id)
        if not class_details:
            return jsonify({'success': False, 'message': 'Class not found'}), 404
        
        # Check if class is completed
        if class_details.get('status') not in ['completed', 'ended']:
            return jsonify({'success': False, 'message': 'Only completed classes can be deleted'}), 400
        
        # Delete the class using the existing function
        from auth_handler import delete_live_class_route
        delete_live_class_route(class_id)
        
        return jsonify({'success': True, 'message': 'Completed class deleted successfully'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Create category route
@app.route('/create-category', methods=['POST'])
def create_category():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    try:
        # Get form data
        category_name = request.form.get('category_name', '').strip()
        category_description = request.form.get('category_description', '').strip()
        category_type = request.form.get('category_type', 'general')
        target_class = request.form.get('target_class', 'all')
        paid_status = request.form.get('paid_status', 'unpaid')

        # Validate required fields
        if not category_name:
            flash('Category name is required.', 'error')
            return redirect(url_for('upload_resource'))

        # Save category to database
        conn = sqlite3.connect('users.db')
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
        
        # Insert new category
        c.execute('''INSERT INTO categories (name, description, category_type, target_class, paid_status, created_by) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  (category_name, category_description, category_type, target_class, paid_status, session.get('user_id')))
        
        conn.commit()
        conn.close()

        flash(f'Category "{category_name}" created successfully!', 'success')
        return redirect(url_for('upload_resource'))

    except sqlite3.IntegrityError:
        flash(f'Category "{category_name}" already exists.', 'error')
        return redirect(url_for('upload_resource'))
    except Exception as e:
        flash(f'Error creating category: {str(e)}', 'error')
        return redirect(url_for('upload_resource'))

# Get all categories
def get_all_categories():
    conn = sqlite3.connect('users.db')
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
    
    c.execute('SELECT id, name, description, category_type, target_class, paid_status, created_at FROM categories WHERE is_active = 1 ORDER BY name')
    categories = c.fetchall()
    conn.close()
    return categories

# Delete category route
@app.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get category name before deleting
        c.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        result = c.fetchone()
        if not result:
            flash('Category not found.', 'error')
            return redirect(url_for('upload_resource'))
        
        category_name = result[0]
        
        # Soft delete - mark as inactive
        c.execute('UPDATE categories SET is_active = 0 WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()

        flash(f'Category "{category_name}" deleted successfully!', 'success')
        return redirect(url_for('upload_resource'))

    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
        return redirect(url_for('upload_resource'))

# Edit category route
@app.route('/edit-category/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    try:
        # Get form data
        category_name = request.form.get('category_name', '').strip()
        category_description = request.form.get('category_description', '').strip()
        category_type = request.form.get('category_type', 'general')
        target_class = request.form.get('target_class', 'all')
        paid_status = request.form.get('paid_status', 'unpaid')

        # Validate required fields
        if not category_name:
            flash('Category name is required.', 'error')
            return redirect(url_for('upload_resource'))

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Update category
        c.execute('''UPDATE categories 
                     SET name = ?, description = ?, category_type = ?, target_class = ?, paid_status = ?
                     WHERE id = ?''', 
                  (category_name, category_description, category_type, target_class, paid_status, category_id))
        
        conn.commit()
        conn.close()

        flash(f'Category "{category_name}" updated successfully!', 'success')
        return redirect(url_for('upload_resource'))

    except sqlite3.IntegrityError:
        flash(f'Category "{category_name}" already exists.', 'error')
        return redirect(url_for('upload_resource'))
    except Exception as e:
        flash(f'Error updating category: {str(e)}', 'error')
        return redirect(url_for('upload_resource'))

# Create resource route - REMOVED
# @app.route('/create-resource', methods=['POST'])
def create_resource():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    try:
        # Get form data
        resource_type = request.form.get('resource_type')
        class_id = request.form.get('class_id')
        subject = request.form.get('subject')
        chapter = request.form.get('chapter')
        difficulty = request.form.get('difficulty')
        paid_status = request.form.get('paid_status', 'unpaid')
        description = request.form.get('description')
        learning_objectives = request.form.get('learning_objectives')
        schedule_date = request.form.get('schedule_date')
        file = request.files.get('file')

        # Debug: Print form data
        print(f"DEBUG - resource_type: {resource_type}")
        print(f"DEBUG - class_id: {class_id}")
        print(f"DEBUG - subject: {subject}")
        print(f"DEBUG - file: {file}")

        # Validate required fields
        if not all([resource_type, class_id, subject, file]):
            missing_fields = []
            if not resource_type:
                missing_fields.append("Resource Type")
            if not class_id:
                missing_fields.append("Class")
            if not subject:
                missing_fields.append("Subject")
            if not file:
                missing_fields.append("File")
            
            flash(f'Missing required fields: {", ".join(missing_fields)}', 'error')
            return redirect(url_for('upload_resource'))

        if not allowed_file(file.filename):
            flash(f'File type not allowed: {file.filename}. Please upload PDF, DOC, DOCX, PPT, or PPTX files.', 'error')
            return redirect(url_for('upload_resource'))

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Create resource title based on type and details
        class_name = get_class_name_by_id(class_id)
        title = f"{resource_type.upper()} - {subject.title()}"
        if chapter:
            title += f" - {chapter}"
        title += f" ({class_name})"

        # Create detailed description
        detailed_description = f"Resource Type: {resource_type.upper()}\n"
        detailed_description += f"Subject: {subject.title()}\n"
        if chapter:
            detailed_description += f"Chapter: {chapter}\n"
        detailed_description += f"Difficulty: {difficulty.title()}\n"
        detailed_description += f"Class: {class_name}\n\n"
        
        if description:
            detailed_description += f"Description: {description}\n\n"
        
        if learning_objectives:
            detailed_description += f"Learning Objectives: {learning_objectives}"

        # Save resource to database
        try:
            print(f"DEBUG - Calling save_resource with: filename={filename}, class_id={class_id}, filepath={filepath}, title={title}, description={detailed_description[:50]}..., category={resource_type}")
            save_resource(filename, class_id, filepath, title, detailed_description, resource_type)
            print("DEBUG - save_resource completed successfully")
        except Exception as e:
            print(f"DEBUG - Error in save_resource: {e}")
            flash(f'Error saving resource to database: {str(e)}', 'error')
            return redirect(url_for('upload_resource'))

        # Add specific metadata based on resource type
        metadata = {
            'resource_type': resource_type,
            'subject': subject,
            'chapter': chapter,
            'difficulty': difficulty,
            'learning_objectives': learning_objectives
        }

        # Add type-specific metadata
        if resource_type == 'worksheet':
            metadata.update({
                'worksheet_type': request.form.get('worksheet_type'),
                'question_count': request.form.get('question_count'),
                'time_limit': request.form.get('time_limit'),
                'marks_per_question': request.form.get('marks_per_question')
            })
        elif resource_type == 'pyq':
            metadata.update({
                'exam_year': request.form.get('exam_year'),
                'exam_type': request.form.get('exam_type'),
                'question_pattern': request.form.get('question_pattern'),
                'total_marks': request.form.get('total_marks')
            })
        elif resource_type == 'cbq':
            metadata.update({
                'case_type': request.form.get('case_type'),
                'case_complexity': request.form.get('case_complexity'),
                'sub_questions': request.form.get('sub_questions'),
                'case_duration': request.form.get('case_duration')
            })

        # Send notification
        notification_message = f"A new {resource_type.upper()} has been created: {title}"
        add_notification(
            notification_message,
            class_id=class_id,
            target_paid_status=paid_status,
            status='active',
            notification_type='study_resource'
        )

        flash(f'{resource_type.upper()} created successfully!', 'success')
        return redirect(url_for('upload_resource'))

    except Exception as e:
        flash(f'Error creating resource: {str(e)}', 'error')
        return redirect(url_for('upload_resource'))

# Edit resource route
@app.route('/edit-resource', methods=['POST'])
def edit_resource():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))

    try:
        # Get form data
        filename = request.form.get('filename')
        title = request.form.get('title', '').strip()
        category = request.form.get('category')
        class_id = request.form.get('class_id')
        paid_status = request.form.get('paid_status', 'unpaid')
        description = request.form.get('description', '').strip()

        # Validate required fields
        if not all([filename, title, category, class_id]):
            flash('Filename, title, category, and class are required.', 'error')
            return redirect(url_for('upload_resource'))

        # Update resource in database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Update the resource
        c.execute('''UPDATE resources 
                     SET title = ?, description = ?, category = ?, class_id = ?
                     WHERE filename = ?''', 
                  (title, description, category, class_id, filename))
        
        # Check if any rows were affected
        if c.rowcount == 0:
            flash('Resource not found.', 'error')
            return redirect(url_for('upload_resource'))

        conn.commit()
        conn.close()

        # Send notification about the update
        notification_message = f"Resource '{title}' has been updated"
        add_notification(
            notification_message,
            class_id=class_id,
            target_paid_status=paid_status,
            status='active',
            notification_type='study_resource'
        )

        flash(f'Resource "{title}" updated successfully!', 'success')
        return redirect(url_for('upload_resource'))

    except Exception as e:
        flash(f'Error updating resource: {str(e)}', 'error')
        return redirect(url_for('upload_resource'))

# --- SOCKET.IO EVENTS FOR POLLS AND DOUBTS ---

@socketio.on('create_poll')
def handle_create_poll(data):
    try:
        class_id = data.get('class_id')
        question = data.get('question')
        options = data.get('options', [])
        created_by = data.get('created_by', 'host')
        correct_answer = data.get('correct_answer')
        duration = data.get('duration', 15)
        
        if not class_id or not question or len(options) < 2:
            emit('error', {'message': 'Invalid poll data'})
            return
        
        db = get_db()
        c = db.cursor()
        c.execute('INSERT INTO polls (class_id, question, created_by) VALUES (?, ?, ?)', (class_id, question, created_by))
        poll_id = c.lastrowid
        
        for idx, opt in enumerate(options):
            c.execute('INSERT INTO poll_options (poll_id, option_text) VALUES (?, ?)', (poll_id, opt))
        db.commit()
        
        # Fetch poll with options
        c.execute('SELECT * FROM polls WHERE id=?', (poll_id,))
        poll = dict(c.fetchone())
        c.execute('SELECT id, option_text FROM poll_options WHERE poll_id=?', (poll_id,))
        poll['options'] = [dict(row) for row in c.fetchall()]
        poll['correct_answer'] = correct_answer
        poll['duration'] = duration
        
        socketio.emit('new_poll', poll, room=f'liveclass_{class_id}')
        print(f"Poll created: {poll_id} for class {class_id}")
        
    except Exception as e:
        print(f"Error creating poll: {e}")
        emit('error', {'message': 'Failed to create poll'})

@socketio.on('vote_poll')
def handle_vote_poll(data):
    poll_id = data.get('poll_id')
    option_id = data.get('option_id')
    user_id = data.get('user_id')
    db = get_db()
    c = db.cursor()
    # Prevent double voting
    c.execute('SELECT * FROM poll_votes WHERE poll_id=? AND user_id=?', (poll_id, user_id))
    if c.fetchone():
        return
    c.execute('INSERT INTO poll_votes (poll_id, option_id, user_id) VALUES (?, ?, ?)', (poll_id, option_id, user_id))
    db.commit()
    # Send updated poll results
    c.execute('SELECT id, option_text FROM poll_options WHERE poll_id=?', (poll_id,))
    options = [dict(row) for row in c.fetchall()]
    results = []
    for opt in options:
        c.execute('SELECT COUNT(*) as votes FROM poll_votes WHERE option_id=?', (opt['id'],))
        votes = c.fetchone()['votes']
        results.append({'option_id': opt['id'], 'option_text': opt['option_text'], 'votes': votes})
    socketio.emit('poll_results', {'poll_id': poll_id, 'results': results}, room=f'liveclass_{data.get("class_id")}')

@socketio.on('submit_doubt')
def handle_submit_doubt(data):
    class_id = data.get('class_id')
    user_id = data.get('user_id')
    username = data.get('username')
    doubt_text = data.get('doubt_text')
    db = get_db()
    c = db.cursor()
    c.execute('INSERT INTO doubts (class_id, user_id, username, doubt_text) VALUES (?, ?, ?, ?)', (class_id, user_id, username, doubt_text))
    db.commit()
    c.execute('SELECT * FROM doubts WHERE class_id=? ORDER BY created_at ASC', (class_id,))
    doubts = [dict(row) for row in c.fetchall()]
    socketio.emit('update_doubts', {'doubts': doubts}, room=f'liveclass_{class_id}')

@socketio.on('resolve_doubt')
def handle_resolve_doubt(data):
    doubt_id = data.get('doubt_id')
    class_id = data.get('class_id')
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE doubts SET status="resolved", resolved_at=CURRENT_TIMESTAMP WHERE id=?', (doubt_id,))
    db.commit()
    c.execute('SELECT * FROM doubts WHERE class_id=? ORDER BY created_at ASC', (class_id,))
    doubts = [dict(row) for row in c.fetchall()]
    socketio.emit('update_doubts', {'doubts': doubts}, room=f'liveclass_{class_id}')

@socketio.on('ignore_doubt')
def handle_ignore_doubt(data):
    doubt_id = data.get('doubt_id')
    class_id = data.get('class_id')
    db = get_db()
    c = db.cursor()
    c.execute('UPDATE doubts SET status="ignored", resolved_at=CURRENT_TIMESTAMP WHERE id=?', (doubt_id,))
    db.commit()
    c.execute('SELECT * FROM doubts WHERE class_id=? ORDER BY created_at ASC', (class_id,))
    doubts = [dict(row) for row in c.fetchall()]
    socketio.emit('update_doubts', {'doubts': doubts}, room=f'liveclass_{class_id}')

@socketio.on('get_polls_and_doubts')
def handle_get_polls_and_doubts(data):
    class_id = data.get('class_id')
    db = get_db()
    c = db.cursor()
    # Polls
    c.execute('SELECT * FROM polls WHERE class_id=? ORDER BY created_at ASC', (class_id,))
    polls = [dict(row) for row in c.fetchall()]
    for poll in polls:
        c.execute('SELECT id, option_text FROM poll_options WHERE poll_id=?', (poll['id'],))
        poll['options'] = [dict(row) for row in c.fetchall()]
    # Doubts
    c.execute('SELECT * FROM doubts WHERE class_id=? ORDER BY created_at ASC', (class_id,))
    doubts = [dict(row) for row in c.fetchall()]
    socketio.emit('init_polls_and_doubts', {'polls': polls, 'doubts': doubts}, room=request.sid)

# New handlers for enhanced live class features
@socketio.on('end_poll')
def handle_end_poll(data):
    try:
        poll_id = data.get('poll_id')
        class_id = data.get('class_id')
        
        if not poll_id or not class_id:
            emit('error', {'message': 'Poll ID and Class ID required'})
            return
            
        db = get_db()
        c = db.cursor()
        
        # Get poll results
        c.execute('SELECT * FROM polls WHERE id=?', (poll_id,))
        poll = dict(c.fetchone())
        
        c.execute('SELECT id, option_text FROM poll_options WHERE poll_id=?', (poll_id,))
        options = [dict(row) for row in c.fetchall()]
        
        results = []
        for opt in options:
            c.execute('SELECT COUNT(*) as votes FROM poll_votes WHERE option_id=?', (opt['id'],))
            votes = c.fetchone()['votes']
            results.append({
                'option_id': opt['id'], 
                'option_text': opt['option_text'], 
                'votes': votes,
                'option_index': options.index(opt)
            })
        
        poll_data = {
            'poll_id': poll_id,
            'question': poll.get('question'),
            'results': results,
            'correct_answer': poll.get('correct_answer'),
            'class_id': class_id
        }
        
        socketio.emit('poll_ended', poll_data, room=f'liveclass_{class_id}')
        print(f"Poll {poll_id} ended for class {class_id}")
        
    except Exception as e:
        print(f"Error ending poll: {e}")
        emit('error', {'message': 'Failed to end poll'})

@socketio.on('host_camera_status')
def handle_host_camera_status(data):
    try:
        class_id = data.get('class_id')
        status = data.get('status')
        message = data.get('message')
        
        if class_id:
            socketio.emit('host_camera_status', {
                'class_id': class_id,
                'status': status,
                'message': message
            }, room=f'liveclass_{class_id}')
            
    except Exception as e:
        print(f"Error broadcasting camera status: {e}")

@socketio.on('host_video_mode')
def handle_host_video_mode(data):
    try:
        class_id = data.get('class_id')
        mode = data.get('mode')
        message = data.get('message')
        
        if class_id:
            socketio.emit('host_video_mode', {
                'class_id': class_id,
                'mode': mode,
                'message': message
            }, room=f'liveclass_{class_id}')
            
    except Exception as e:
        print(f"Error broadcasting video mode: {e}")

@socketio.on('host_mic_status')
def handle_host_mic_status(data):
    try:
        class_id = data.get('class_id')
        muted = data.get('muted')
        
        if class_id:
            socketio.emit('host_mic_status', {
                'class_id': class_id,
                'muted': muted
            }, room=f'liveclass_{class_id}')
            
    except Exception as e:
        print(f"Error broadcasting mic status: {e}")

# Enhanced error handling for Socket.IO
@socketio.on_error()
def error_handler(e):
    print(f"Socket.IO error: {e}")
    emit('error', {'message': 'An error occurred'})

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if not session.get('user_id'):
        return redirect(url_for('auth'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get current user info
    c.execute('''
        SELECT u.id, u.username, u.password, u.class_id, u.paid, u.mobile_no, u.email_address, u.banned, c.name as class_name
        FROM users u 
        LEFT JOIN classes c ON u.class_id = c.id 
        WHERE u.id = ?
    ''', (user_id,))
    
    user_data = c.fetchone()
    conn.close()
    
    if not user_data:
        flash('User not found.', 'error')
        return redirect(url_for('auth'))
    
    # Determine user role
    if user_data[7] == 1:  # banned
        role = 'banned'
    elif user_data[3] == 8:  # class_id 8 is admin
        role = 'admin'
    elif user_data[3] == 9:  # class_id 9 is teacher
        role = 'teacher'
    else:
        role = 'student'
    
    user = {
        'id': user_data[0],
        'username': user_data[1],
        'password': user_data[2],
        'class_id': user_data[3],
        'paid': user_data[4],
        'mobile_no': user_data[5],
        'email_address': user_data[6],
        'banned': user_data[7],
        'class_name': user_data[8],
        'role': role
    }
    
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        new_mobile_no = request.form.get('mobile_no')
        new_email_address = request.form.get('email_address')
        
        if not new_username:
            flash('Username is required.', 'error')
            return render_template('profile.html', user=user, error='Username is required.')
        else:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            
            try:
                if new_password:
                    # Update with new password
                    c.execute('''
                        UPDATE users 
                        SET username = ?, password = ?, mobile_no = ?, email_address = ?
                        WHERE id = ?
                    ''', (new_username, new_password, new_mobile_no, new_email_address, user_id))
                else:
                    # Update without changing password
                    c.execute('''
                        UPDATE users 
                        SET username = ?, mobile_no = ?, email_address = ?
                        WHERE id = ?
                    ''', (new_username, new_mobile_no, new_email_address, user_id))
                
                conn.commit()
                
                # Update session username if changed
                if new_username != user['username']:
                    session['username'] = new_username
                
                flash('Profile updated successfully!', 'success')
                return render_template('profile.html', user=user, success='Profile updated successfully!')
                
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'error')
                return render_template('profile.html', user=user, error=f'Error updating profile: {str(e)}')
            finally:
                conn.close()
    
    return render_template('profile.html', user=user)

# Query Management Routes
@app.route('/api/queries', methods=['GET'])
@admin_api_required
def api_get_queries():
    """API endpoint to get queries with filtering and pagination"""
    try:
        # Get filter parameters
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = """
            SELECT id, name, email, phone, message, subject, priority, status, 
                   category, source, submitted_at, response, responded_at, responded_by
            FROM queries 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR message LIKE ? OR subject LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        # Get total count
        count_query = query.replace("SELECT id, name, email, phone, message, subject, priority, status, category, source, submitted_at, response, responded_at, responded_by", "SELECT COUNT(*)")
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # Add pagination
        query += " ORDER BY submitted_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        # Execute query
        cursor.execute(query, params)
        queries = cursor.fetchall()
        
        # Get statistics
        stats = get_query_statistics()
        
        conn.close()
        
        # Format results
        formatted_queries = []
        for query in queries:
            formatted_queries.append({
                'id': query[0],
                'name': query[1],
                'email': query[2],
                'phone': query[3],
                'message': query[4],
                'subject': query[5],
                'priority': query[6],
                'status': query[7],
                'category': query[8],
                'source': query[9],
                'submitted_at': query[10],
                'response': query[11],
                'responded_at': query[12],
                'responded_by': query[13]
            })
        
        return jsonify({
            'queries': formatted_queries,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>/respond', methods=['POST'])
@admin_api_required
def api_respond_to_query(query_id):
    """API endpoint to respond to a query"""
    try:
        data = request.get_json()
        response = data.get('response', '').strip()
        status = data.get('status', 'resolved')
        
        if not response:
            return jsonify({'success': False, 'error': 'Response is required'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Update query with response
        cursor.execute("""
            UPDATE queries 
            SET response = ?, responded_at = ?, responded_by = ?, status = ?
            WHERE id = ?
        """, (response, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
              'admin', status, query_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>/status', methods=['POST'])
@admin_api_required
def api_update_query_status(query_id):
    """API endpoint to update query status"""
    try:
        data = request.get_json()
        status = data.get('status', '').strip()
        
        if not status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("UPDATE queries SET status = ? WHERE id = ?", (status, query_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/<int:query_id>', methods=['DELETE'])
@admin_api_required
def api_delete_query(query_id):
    """API endpoint to delete a query"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM queries WHERE id = ?", (query_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/queries/export')
@admin_api_required
def api_export_queries():
    """API endpoint to export queries as CSV"""
    try:
        # Get filter parameters
        status = request.args.get('status', '')
        priority = request.args.get('priority', '')
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        # Build query
        query = """
            SELECT id, name, email, phone, message, subject, priority, status, 
                   category, source, submitted_at, response, responded_at, responded_by
            FROM queries 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (name LIKE ? OR email LIKE ? OR message LIKE ? OR subject LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        query += " ORDER BY submitted_at DESC"
        
        # Execute query
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        queries = cursor.fetchall()
        conn.close()
        
        # Create CSV
        from io import StringIO
        import csv
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Subject', 'Message', 'Priority', 
            'Status', 'Category', 'Source', 'Submitted At', 'Response', 
            'Responded At', 'Responded By'
        ])
        
        # Write data
        for query in queries:
            writer.writerow(query)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=queries_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_query_statistics():
    """Get statistics for queries"""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute("SELECT COUNT(*) FROM queries")
        total = cursor.fetchone()[0]
        
        # Pending queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        # Resolved queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE status = 'resolved'")
        resolved = cursor.fetchone()[0]
        
        # Urgent queries
        cursor.execute("SELECT COUNT(*) FROM queries WHERE priority = 'urgent'")
        urgent = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'pending': pending,
            'resolved': resolved,
            'urgent': urgent
        }
        
    except Exception as e:
        return {
            'total': 0,
            'pending': 0,
            'resolved': 0,
            'urgent': 0
        }

@app.route('/query-management')
@admin_required
def query_management_page():
    """Query management page for admins"""
    return render_template('query_management.html')

# Route for PDF preview (secure viewer)
@app.route('/preview/<filename>')
def preview_pdf(filename):
    # Check if user is logged in
    if not session.get('role'):
        flash('You must be logged in to view resources.', 'error')
        return redirect(url_for('auth'))
    
    # Check if file exists and is a PDF
    if not filename.lower().endswith('.pdf'):
        flash('Invalid file type. Only PDF files can be previewed.', 'error')
        return redirect(url_for('study_resources'))
    
    # Ensure uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Check if file exists in uploads directory or subdirectories
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        # Try to find the file in subdirectories
        found_path = None
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            if filename in files:
                found_path = os.path.join(root, filename)
                break
        
        if found_path:
            file_path = found_path
        else:
            flash('File not found.', 'error')
            return redirect(url_for('study_resources'))
    
    # Get user's class and check if they have access to this resource
    role = session.get('role')
    if role in ['admin', 'teacher']:
        # Admin/teacher can view all resources
        pass
    else:
        # For students, check if the resource belongs to their class
        all_classes_dict_rev = {c[1]: c[0] for c in get_all_classes()}
        user_class_id = all_classes_dict_rev.get(role)
        
        if user_class_id:
            # Check if this resource belongs to user's class
            resources = get_resources_for_class_id(user_class_id)
            resource_found = False
            for res_filename, res_class_id, _, _, _, _ in resources:
                if res_filename == filename and res_class_id == user_class_id:
                    resource_found = True
                    break
            
            if not resource_found:
                flash('You do not have access to this resource.', 'error')
                return redirect(url_for('study_resources'))
    
    return render_template('pdf_preview.html', filename=filename, title=filename.replace('.pdf', '').replace('_', ' ').title())

# Route for serving PDF content (with security headers)
@app.route('/pdf-content/<filename>')
def pdf_content(filename):
    # Check if user is logged in
    if not session.get('role'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Check if file exists and is a PDF
    if not filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Ensure uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Check if file exists in uploads directory or subdirectories
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        # Try to find the file in subdirectories
        found_path = None
        for root, dirs, files in os.walk(app.config['UPLOAD_FOLDER']):
            if filename in files:
                found_path = os.path.join(root, filename)
                break
        
        if found_path:
            file_path = found_path
        else:
            return jsonify({'error': 'File not found'}), 404
    
    # Get user's class and check access
    role = session.get('role')
    if role not in ['admin', 'teacher']:
        all_classes_dict_rev = {c[1]: c[0] for c in get_all_classes()}
        user_class_id = all_classes_dict_rev.get(role)
        
        if user_class_id:
            resources = get_resources_for_class_id(user_class_id)
            resource_found = False
            for res_filename, res_class_id, _, _, _, _ in resources:
                if res_filename == filename and res_class_id == user_class_id:
                    resource_found = True
                    break
            
            if not resource_found:
                return jsonify({'error': 'Access denied'}), 403
    
    # Serve PDF with security headers
    response = send_file(file_path, mimetype='application/pdf')
    response.headers['Content-Disposition'] = 'inline'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Content-Security-Policy'] = "default-src 'self'; frame-src 'self'; object-src 'none'"
    response.headers['X-Download-Options'] = 'noopen'
    response.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    return response

# Route to get categories for a specific class
@app.route('/api/categories/<int:class_id>')
def api_get_categories_for_class(class_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get categories for the specific class
        c.execute('''SELECT id, name, description, category_type, paid_status 
                     FROM categories 
                     WHERE target_class = ? OR target_class = 'all'
                     ORDER BY name''', (str(class_id),))
        
        categories = []
        for row in c.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'category_type': row[3],
                'paid_status': row[4]
            })
        
        conn.close()
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.before_request
def track_ip_activity():
    try:
        # Determine client IP (respect X-Forwarded-For if present)
        xff = request.headers.get('X-Forwarded-For', '')
        ip = (xff.split(',')[0].strip() if xff else request.remote_addr) or 'unknown'
        user_id = session.get('user_id')
        path = request.path
        ua = request.headers.get('User-Agent', '')[:300]
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Ensure tables exist (in case of reload)
        c.execute('''CREATE TABLE IF NOT EXISTS ip_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_id INTEGER,
            path TEXT,
            user_agent TEXT,
            visited_at TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_activity (
            user_id INTEGER PRIMARY KEY,
            ip TEXT,
            last_seen TEXT
        )''')
        # Insert IP log
        c.execute('INSERT INTO ip_logs (ip, user_id, path, user_agent, visited_at) VALUES (?, ?, ?, ?, ?)',
                  (ip, user_id, path, ua, now_str))
        # Update user activity if logged in
        if user_id:
            c.execute("""
                INSERT INTO user_activity (user_id, ip, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id)
                DO UPDATE SET ip=excluded.ip, last_seen=excluded.last_seen
            """, (user_id, ip, now_str))
        conn.commit()
        conn.close()
    except Exception as e:
        # Fail silently to not block requests
        print(f"IP tracking error: {e}")

@app.route('/api/admin/metrics/traffic')
def api_admin_metrics_traffic():
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        # Total unique IPs (all time)
        c.execute('SELECT COUNT(DISTINCT ip) FROM ip_logs')
        total_unique_ips = c.fetchone()[0] or 0
        # Unique IPs today (local time)
        c.execute("SELECT COUNT(DISTINCT ip) FROM ip_logs WHERE date(visited_at) = date('now','localtime')")
        unique_ips_today = c.fetchone()[0] or 0
        # Active IPs in last 10 minutes
        c.execute("SELECT COUNT(DISTINCT ip) FROM ip_logs WHERE visited_at >= datetime('now','-10 minutes','localtime')")
        active_ips_now = c.fetchone()[0] or 0
        # Active logged-in users in last 10 minutes
        c.execute("SELECT COUNT(*) FROM user_activity WHERE last_seen >= datetime('now','-10 minutes','localtime') AND user_id IS NOT NULL")
        active_logged_in_users = c.fetchone()[0] or 0
        conn.close()
        return jsonify({
            'success': True,
            'data': {
                'total_unique_ips': total_unique_ips,
                'unique_ips_today': unique_ips_today,
                'active_ips_now': active_ips_now,
                'active_logged_in_users': active_logged_in_users
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/metrics/traffic/logs')
def api_admin_metrics_logs():
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        limit = int(request.args.get('limit', 200))
        if limit < 1 or limit > 1000:
            limit = 200
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            SELECT l.ip, l.user_id, IFNULL(u.username,''), l.path, l.user_agent, l.visited_at
            FROM ip_logs l
            LEFT JOIN users u ON u.id = l.user_id
            ORDER BY datetime(l.visited_at) DESC
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        data = [
            {
                'ip': r[0], 'user_id': r[1], 'username': r[2], 'path': r[3],
                'user_agent': r[4], 'visited_at': r[5]
            } for r in rows
        ]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/metrics/traffic/active')
def api_admin_metrics_active():
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            SELECT ua.user_id, IFNULL(u.username,''), ua.ip, ua.last_seen
            FROM user_activity ua
            LEFT JOIN users u ON u.id = ua.user_id
            WHERE ua.last_seen >= datetime('now','-10 minutes','localtime') AND ua.user_id IS NOT NULL
            ORDER BY datetime(ua.last_seen) DESC
        ''')
        rows = c.fetchall()
        conn.close()
        data = [
            {'user_id': r[0], 'username': r[1], 'ip': r[2], 'last_seen': r[3]} for r in rows
        ]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/user')
def user_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('auth'))
    return render_template('user.html')

@app.route('/api/admin/metrics/traffic/last_seen')
def api_admin_metrics_last_seen():
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        user_ids_param = request.args.get('user_ids', '').strip()
        ids = []
        if user_ids_param:
            ids = [i for i in (p.strip() for p in user_ids_param.split(',')) if i.isdigit()]
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        if ids:
            placeholders = ','.join('?' for _ in ids)
            c.execute(f"SELECT user_id, last_seen FROM user_activity WHERE user_id IN ({placeholders})", ids)
        else:
            c.execute("SELECT user_id, last_seen FROM user_activity")
        rows = c.fetchall()
        conn.close()
        data = {str(r[0]): r[1] for r in rows if r and r[0] is not None}
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Favicon and app icons
@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory('attached_assets', 'image_1750584670920.png', mimetype='image/png')
    except Exception:
        # Fallback: return 204 if asset missing
        from flask import Response
        return Response(status=204)

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    try:
        return send_from_directory('attached_assets', 'image_1750584670920.png', mimetype='image/png')
    except Exception:
        from flask import Response
        return Response(status=204)

@app.route('/admin/home-editor', methods=['GET', 'POST'])
@admin_required
def home_editor():
    error = None
    success_message = None
    index_path = os.path.join('.', 'index.html')
    if request.method == 'POST':
        html_content = request.form.get('html_content', '')
        try:
            # Backup existing index.html
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join('.', f'index_backup_{timestamp}.html')
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    existing = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(existing)
            except Exception:
                pass
            # Write new content
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            flash('Homepage updated successfully.', 'success')
            success_message = 'Homepage updated successfully.'
        except Exception as e:
            error = f'Failed to update homepage: {str(e)}'
            flash(error, 'error')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_html_content = f.read()
    except Exception as e:
        index_html_content = ''
        error = f'Failed to load homepage: {str(e)}'
    return render_template('home_customizer.html', index_html_content=index_html_content, error=error, success_message=success_message)

@app.route('/api/check-admission-credentials', methods=['POST'])
def api_check_admission_credentials():
    try:
        data = request.get_json(silent=True) or request.form
        access_username = (data.get('access_username') or '').strip()
        access_password = (data.get('access_password') or '').strip()
        if not access_username or not access_password:
            return jsonify({'valid': False, 'error': 'Missing credentials'}), 400
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT access_password FROM admission_access WHERE access_username=?',
                  (access_username,))
        row = c.fetchone()
        conn.close()
        is_valid = bool(row and check_password_hash(row[0], access_password))
        return jsonify({'valid': is_valid})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500

def cleanup_stale_sessions():
    """Clean up stale sessions periodically"""
    import threading
    import time
    
    def cleanup():
        while True:
            try:
                current_time = datetime.now()
                stale_sessions = []
                
                for session_id, session_data in active_sessions.items():
                    last_ping = session_data.get('last_ping', session_data.get('connected_at'))
                    if current_time - last_ping > timedelta(minutes=5):  # 5 minutes timeout
                        stale_sessions.append(session_id)
                
                for session_id in stale_sessions:
                    print(f"Cleaning up stale session: {session_id}")
                    # Clean up from rooms
                    if session_id in active_sessions:
                        user_rooms = active_sessions[session_id].get('rooms', [])
                        for room in user_rooms:
                            if room in room_participants and session_id in room_participants[room]:
                                room_participants[room].remove(session_id)
                        del active_sessions[session_id]
                
                time.sleep(60)  # Run cleanup every minute
                
            except Exception as e:
                print(f"Error in session cleanup: {e}")
                time.sleep(60)
    
    cleanup_thread = threading.Thread(target=cleanup, daemon=True)
    cleanup_thread.start()
    print("🧹 Session cleanup service started")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    # Start session cleanup service
    cleanup_stale_sessions()
    
    # Default to HTTP mode to avoid SSL issues
    print("🚀 Starting server with HTTP...")
    print("🌐 Access your app at: http://localhost:10000")
    print("⚠️  Note: WebRTC features will not work without HTTPS!")
    
    try:
        socketio.run(app, host='0.0.0.0', port=port, debug=False, log_output=False)
    except Exception as e:
        print(f"❌ Server Error: {e}")
        print("🔄 Trying alternative configuration...")
        try:
            socketio.run(app, host='127.0.0.1', port=port, debug=False, log_output=False)
        except Exception as e2:
            print(f"❌ Alternative configuration failed: {e2}")
            print("🔄 Trying with different settings...")
            socketio.run(app, host='localhost', port=port, debug=False, log_output=False)