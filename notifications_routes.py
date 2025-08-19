from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

notifications_bp = Blueprint('notifications', __name__)

DATABASE = 'users.db'

from auth_handler import (
	add_notification,
	delete_notification,
	get_all_notifications,
	get_unread_notifications_for_user,
	mark_notification_as_read,
	mark_messages_as_read
)

@notifications_bp.route('/add-notification', methods=['POST'])
def add_notification_route():
	if session.get('role') not in ['admin', 'teacher']:
		return redirect(url_for('auth'))
	message = request.form.get('message')
	class_id = request.form.get('class_id')
	if message and class_id:
		add_notification(message, class_id)
		flash('Notification sent!', 'success')
	return redirect(url_for('admin_panel'))

@notifications_bp.route('/mark-notification-seen', methods=['POST'])
def mark_notification_seen_route():
	user_id = session.get('user_id')
	if not user_id:
		return {'status': 'error', 'message': 'User not logged in'}, 401
	data = request.json or {}
	notification_id = data.get('notification_id')
	if not notification_id:
		return {'status': 'error', 'message': 'Notification ID is required'}, 400
	mark_notification_as_read(user_id, notification_id, 'general')
	return {'status': 'success'}

@notifications_bp.route('/delete-notification/<int:notification_id>', methods=['POST'])
def delete_notification_route(notification_id):
	if session.get('role') not in ['admin', 'teacher']:
		return redirect(url_for('auth'))
	delete_notification(notification_id)
	flash('Notification deleted!', 'success')
	return redirect(url_for('admin_panel'))

@notifications_bp.route('/admin/delete-notification/<int:notification_id>', methods=['POST'])
def admin_delete_notification(notification_id):
	if session.get('role') not in ['admin', 'teacher']:
		return redirect(url_for('auth'))
	delete_notification(notification_id)
	return redirect(url_for('admin_panel', _anchor='notifications'))

@notifications_bp.route('/send-notification', methods=['GET', 'POST'])
def send_notification_page():
	if session.get('role') not in ['admin', 'teacher']:
		return redirect(url_for('auth'))
	if request.method == 'POST':
		message = request.form.get('message')
		class_id = request.form.get('class_id')
		target_paid_status = request.form.get('target_paid_status', 'all')
		schedule_date = request.form.get('schedule_date')
		if not message or not class_id or not target_paid_status:
			flash('Message, class, and target users are required.', 'error')
			return render_template('send_notification.html')
		valid_paid_statuses = ['all', 'paid', 'not paid']
		if target_paid_status not in valid_paid_statuses:
			flash('Invalid target users selection.', 'error')
			return render_template('send_notification.html')
		try:
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
	notifications = get_all_notifications()[:10]
	return render_template('send_notification.html', notifications=notifications)

@notifications_bp.route('/admin/update-notification-status/<int:notification_id>', methods=['POST'])
def update_notification_status_route(notification_id):
	if session.get('role') not in ['admin', 'teacher']:
		return jsonify({'success': False, 'error': 'Unauthorized'}), 401
	data = request.get_json() or {}
	status = data.get('status')
	if status not in ['active', 'scheduled', 'completed', 'cancelled']:
		return jsonify({'success': False, 'error': 'Invalid status'}), 400
	from auth_handler import update_notification_status
	update_notification_status(notification_id, status)
	return jsonify({'success': True})

@notifications_bp.route('/api/mark-notification-seen/<int:notification_id>', methods=['POST'])
def mark_notification_seen_api(notification_id):
	if 'user_id' not in session:
		return jsonify({'error': 'Not authenticated'}), 401
	data = request.get_json() or {}
	notification_type = data.get('type', 'notification')
	user_id = session['user_id']
	if notification_type == 'personal_chat':
		success = mark_messages_as_read(user_id, notification_id)
	else:
		success = mark_notification_as_read(user_id, notification_id, 'general')
	if success:
		return jsonify({'success': True, 'message': 'Item marked as seen'})
	else:
		return jsonify({'error': 'Failed to mark item as seen'}), 500

@notifications_bp.route('/api/notifications', methods=['GET'])
def api_get_user_notifications():
	user_id = session.get('user_id')
	if not user_id:
		return jsonify({'success': False, 'error': 'Not logged in'})
	try:
		notifications = get_unread_notifications_for_user(user_id)
		return jsonify({'success': True, 'notifications': notifications, 'count': len(notifications)})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})