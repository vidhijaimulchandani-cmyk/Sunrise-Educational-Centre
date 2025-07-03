from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify
import os
import secrets
from werkzeug.utils import secure_filename
from auth_handler import (
    init_db, register_user, authenticate_user, save_resource, get_all_resources,
    delete_resource, get_all_users, delete_user, search_users, get_user_by_id,
    update_user, add_notification, get_unread_notifications_for_user, get_all_notifications,
    create_live_class, get_live_class, get_active_classes, deactivate_class,
    get_class_details_by_id, get_all_classes, get_resources_for_class_id,
    mark_notification_as_seen, delete_notification,
    save_forum_message, get_forum_messages, vote_on_message, delete_forum_message,
    create_topic, delete_topic, get_all_topics, get_topics_for_user, can_user_access_topic,
    update_user_with_password
)
import csv
from io import StringIO
from collections import Counter
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__, static_folder='.', template_folder='.')
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value in production

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_global_variables():
    user_id = session.get('user_id')
    username = session.get('username')
    role = session.get('role')
    notifications = []
    if user_id:
        notifications = get_unread_notifications_for_user(user_id)
            
    all_classes = get_all_classes()
    return dict(user_notifications=notifications, all_classes=all_classes, username=username, role=role)

# Route for the main page
@app.route('/')
def home():
    return render_template('index.html')

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

    user_id = session.get('user_id')
    paid_status = None
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            paid_status = user[3]  # Assuming user[3] is the paid status

    return render_template('study-resources.html', resources=resources, class_name=role, paid_status=paid_status)

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
    return render_template('forum.html', username=username, all_topics=all_topics, role=role, user_paid_status=user_paid_status)

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
        if not can_user_access_topic(user_role, user_paid_status, int(topic_id)):
            return jsonify({'error': 'Access denied to this topic'}), 403
        messages = get_forum_messages(topic_id=int(topic_id))
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
            'parent_id': m[4], 'upvotes': m[5], 'downvotes': m[6], 'timestamp': m[7], 'topic_id': m[8] if len(m) > 8 else None
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
    vote_on_message(message_id, vote_type)
    return jsonify({'success': True})

@app.route('/api/forum/messages/<int:message_id>', methods=['DELETE'])
def api_delete_forum_message(message_id):
    user_id = session.get('user_id')
    user_role = session.get('role')
    # Only allow delete if admin or the message belongs to the user
    from auth_handler import get_forum_messages
    messages = get_forum_messages()
    msg = next((m for m in messages if m[0] == message_id), None)
    if not msg:
        return jsonify({'error': 'Message not found'}), 404
    if user_role != 'admin' and msg[1] != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    delete_forum_message(message_id)
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

    # Teacher/admin: show start/end controls and active class info
    if role in ['admin', 'teacher']:
        active_classes = get_active_classes()
        all_classes = get_all_classes()
        return render_template('online-class.html', role=role, active_classes=active_classes, all_classes=all_classes, username=username)

    # Student: check if a live class is active for their class
    all_classes_dict_rev = {c[1]: c[0] for c in get_all_classes()}
    class_id = all_classes_dict_rev.get(role)
    active_classes = get_active_classes()
    meeting_url = None
    for c in active_classes:
        if c[5] == class_id:  # c[5] is target_class_id
            meeting_url = c[2]  # c[2] is meeting_url
            break
    return render_template('online-class.html', role=role, meeting_url=meeting_url, username=username)

@app.route('/start-live-class', methods=['POST'])
def start_live_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    class_id = request.form.get('class_id')
    topic = request.form.get('topic', 'Live Class')
    description = request.form.get('description', '')
    room_name = f"SunriseEducation-{secrets.token_hex(8)}"
    meeting_url = f"https://meet.jit.si/{room_name}"
    # Only one live class per class_id
    create_live_class(class_id, meeting_url, topic, description)
    flash('Live class started!', 'success')
    return redirect(url_for('online_class'))

@app.route('/end-live-class', methods=['POST'])
def end_live_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    class_id = request.form.get('class_id')
    deactivate_class(class_id)
    flash('Live class ended.', 'info')
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
                if user_role in ['admin', 'teacher']:
                    return redirect(url_for('admin_panel'))
                else:
                    return redirect(url_for('home'))
        error = 'Invalid username, password, or role.'
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
        
        return render_template('admin.html', resources=resources, users=users, search_query=q, all_notifications=all_notifications, active_classes=active_classes, forum_messages=forum_messages, forum_search_query=forum_q, all_classes=all_classes, total_users=total_users, total_forum_posts=total_forum_posts, total_resources=total_resources, total_classes=total_classes, most_active_users=most_active_users, most_resource_classes=most_resource_classes, all_topics=all_topics)
    else:
        return redirect(url_for('auth'))

@app.route('/admin/delete-forum-message/<int:message_id>', methods=['POST'])
def admin_delete_forum_message(message_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_forum_message(message_id)
    # Preserve forum search if present
    forum_q = request.args.get('forum_q', '')
    if forum_q:
        return redirect(url_for('admin_panel', forum_q=forum_q, _anchor='forum'))
    return redirect(url_for('admin_panel', _anchor='forum'))

@app.route('/create-live-class', methods=['GET', 'POST'])
def create_live_class_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        topic = request.form.get('topic')
        description = request.form.get('description')
        room_name = f"SunriseEducation-{secrets.token_hex(8)}"
        meeting_url = f"https://meet.jit.si/{room_name}"
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
        if not file or file.filename == '' or not class_id or not category:
            flash('File, class, and category selection are required.', 'error')
        elif not allowed_file(file.filename):
            flash('File type not allowed.', 'error')
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            save_resource(filename, class_id, filepath, title, description, category)
            flash('Resource uploaded successfully!', 'success')
            return redirect(url_for('admin_panel'))
    return render_template('upload_resource.html')

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
    all_classes = get_all_classes()
    if request.method == 'POST':
        message = request.form.get('message')
        description = request.form.get('description')
        class_id = request.form.get('class_id')
        target_paid_status = request.form.get('target_paid_status', 'all')
        if message and class_id:
            add_notification(message, class_id, target_paid_status)
            flash('Notification sent!', 'success')
            return redirect(url_for('admin_panel', _anchor='notifications'))
    return render_template('send_notification.html', all_classes=all_classes)

@app.route('/admin/create-user', methods=['GET'])
def admin_create_user_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    all_classes = get_all_classes()
    return render_template('admin_create_user.html', all_classes=all_classes)

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
    from auth_handler import get_user_by_id, add_notification
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin_panel', _anchor='users'))
    
    # Set user as banned using direct SQL
    import sqlite3
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET banned=1 WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    
    # Send notification to the banned user
    ban_message = "You are banned. Call Mohit Sir or admin to be unbanned."
    add_notification(ban_message, user[2])  # user[2] is class_id
    
    flash(f'User {user[1]} has been banned and notified.', 'success')
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 