from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

batch_bp = Blueprint('batch', __name__)

DATABASE = 'users.db'


def ensure_batch_meta_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS batch_meta (
            class_id INTEGER PRIMARY KEY,
            image TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()


def get_all_classes_with_meta():
    ensure_batch_meta_table()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, name FROM classes ORDER BY id')
    classes = c.fetchall()
    c.execute('SELECT class_id, image, start_date, end_date, description FROM batch_meta')
    meta_rows = c.fetchall()
    conn.close()
    meta_map = {row[0]: {'image': row[1], 'start_date': row[2], 'end_date': row[3], 'description': row[4]} for row in meta_rows}
    enriched = []
    for cid, name in classes:
        enriched.append({
            'id': cid,
            'name': name,
            'meta': meta_map.get(cid, {'image': '', 'start_date': '', 'end_date': '', 'description': ''})
        })
    return enriched


@batch_bp.route('/admin/batch-management', methods=['GET'])
def batch_management_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    classes = get_all_classes_with_meta()
    return render_template('batch_management.html', classes=classes)


@batch_bp.route('/admin/batch/create', methods=['POST'])
def create_batch_class():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    name = (request.form.get('name') or '').strip()
    if not name:
        flash('Class name is required.', 'error')
        return redirect(url_for('batch.batch_management_page'))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO classes (name) VALUES (?)', (name,))
        conn.commit()
        flash('Class created.', 'success')
    except sqlite3.IntegrityError:
        flash('Class already exists.', 'error')
    finally:
        conn.close()
    return redirect(url_for('batch.batch_management_page'))


@batch_bp.route('/admin/batch/update/<int:class_id>', methods=['POST'])
def update_batch_class(class_id: int):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    name = (request.form.get('name') or '').strip()
    image = (request.form.get('image') or '').strip()
    start_date = (request.form.get('start_date') or '').strip()
    end_date = (request.form.get('end_date') or '').strip()
    description = (request.form.get('description') or '').strip()

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        if name:
            c.execute('UPDATE classes SET name=? WHERE id=?', (name, class_id))
        ensure_batch_meta_table()
        # Upsert meta
        c.execute('SELECT class_id FROM batch_meta WHERE class_id=?', (class_id,))
        exists = c.fetchone()
        if exists:
            c.execute('''UPDATE batch_meta SET image=?, start_date=?, end_date=?, description=? WHERE class_id=?''',
                      (image, start_date, end_date, description, class_id))
        else:
            c.execute('''INSERT INTO batch_meta (class_id, image, start_date, end_date, description) VALUES (?,?,?,?,?)''',
                      (class_id, image, start_date, end_date, description))
        conn.commit()
        flash('Batch updated.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Update failed: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('batch.batch_management_page'))


@batch_bp.route('/admin/batch/delete/<int:class_id>', methods=['POST'])
def delete_batch_class(class_id: int):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('DELETE FROM batch_meta WHERE class_id=?', (class_id,))
        c.execute('DELETE FROM classes WHERE id=?', (class_id,))
        conn.commit()
        flash('Class deleted.', 'info')
    except Exception as e:
        conn.rollback()
        flash(f'Delete failed: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('batch.batch_management_page'))