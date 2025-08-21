from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os

# Create Flask app
app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Optionally register blueprints if present
try:
    from batch_routes import batch_bp
    app.register_blueprint(batch_bp)
except Exception:
    pass

try:
    from notifications_routes import notifications_bp
    app.register_blueprint(notifications_bp)
except Exception:
    pass

try:
    from live_class_routes import live_classes_bp
    app.register_blueprint(live_classes_bp)
except Exception:
    pass

try:
    from query_routes import queries_bp
    app.register_blueprint(queries_bp)
except Exception:
    pass

# Minimal auth route for testing admin-only pages
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()
        class_id = (request.form.get('class_id') or '').strip()
        admin_code = (request.form.get('admin_code') or '').strip()
        # Simple dev login: yash + admin code => admin; otherwise student
        if username == 'yash' and password == 'yash' and class_id == '8' and admin_code == 'sec@011':
            session['user_id'] = 1
            session['username'] = 'yash'
            session['role'] = 'admin'
            return redirect(url_for('batch.batch_management_page'))
        # Student fallback
        session['user_id'] = 2
        session['username'] = username or 'student'
        session['role'] = 'class 9'
        return redirect(url_for('home'))
    return render_template('auth.html', error=None)

# Home route serves index.html if present
@app.route('/')
def home():
    if os.path.exists(os.path.join(app.template_folder or '.', 'index.html')):
        return render_template('index.html')
    return 'OK'

# Serve static files
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# Countdown preview using countdown settings
@app.route('/countdown-preview')
def countdown_preview():
    try:
        from countdown_manager import get_countdown_settings
        settings = get_countdown_settings() or {
            'launch_date': '2025-12-31T00:00:00',
            'launch_message': '🚀 Our website will be live soon! Get ready for an amazing learning experience.',
            'background_type': 'gradient',
            'background_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'background_color': '#667eea',
            'logo_text': 'S',
            'logo_color': '#ff6b6b',
            'gate_animation_enabled': True,
            'gate_message': '🚀 Welcome to Sunrise Educational Centre! 🚀',
            'is_active': True
        }
        return render_template('countdown_dynamic.html', settings=settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Simple route to view the static launch countdown page
@app.route('/launch')
def launch_page():
    return render_template('launch_countdown.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))