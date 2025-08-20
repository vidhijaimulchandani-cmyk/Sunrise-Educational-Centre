from flask import Blueprint, request, jsonify, redirect, url_for
from datetime import datetime
import sqlite3


queries_bp = Blueprint('queries', __name__)


DATABASE = 'users.db'


@queries_bp.route('/submit-query', methods=['POST'])
def submit_query():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Determine requester IP
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute(
            'INSERT INTO queries (name, email, message, submitted_at, user_ip) VALUES (?, ?, ?, ?, ?)',
            (name, email, message, submitted_at, user_ip)
        )
        conn.commit()

    return redirect(url_for('home'))


@queries_bp.route('/api/recent-queries')
def get_recent_queries():
    # Determine requester IP
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()

    try:
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute(
                '''
                SELECT id, name, email, message, submitted_at, response, responded_at, status
                FROM queries
                WHERE user_ip = ?
                ORDER BY submitted_at DESC
                LIMIT 10
                ''',
                (user_ip,)
            )

            queries = []
            for row in c.fetchall():
                queries.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'message': row[3],
                    'submitted_at': row[4],
                    'response': row[5],
                    'responded_at': row[6],
                    'status': row[7],
                })

            return jsonify({'success': True, 'queries': queries})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

