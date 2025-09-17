#!/usr/bin/env python3
"""
Automated checks for admin uploading features:
- Bulk upload endpoints (/bulk-upload)
- Single resource upload (/upload-resource)

Uses Flask test_client with an admin session.
"""
import io
import json
import os
import sqlite3
from contextlib import contextmanager

from app import app


@contextmanager
def admin_client():
    app.testing = True
    client = app.test_client()
    # Set admin role in session
    with client.session_transaction() as sess:
        sess['role'] = 'admin'
        sess['user_id'] = 1
        sess['username'] = 'admin-test'
    yield client


def pick_any_class_id(db_path: str = 'users.db') -> int | None:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('SELECT id FROM classes ORDER BY id LIMIT 1')
        row = cur.fetchone()
        conn.close()
        return int(row[0]) if row else None
    except Exception:
        return None


def check_bulk_upload(client) -> dict:
    results: dict = {'page': None, 'validate': None, 'preview': None, 'upload': None, 'confirm': None}

    # 1) Page
    resp = client.get('/bulk-upload/')
    results['page'] = resp.status_code

    # Find an xlsx to test with
    candidate_files: list[str] = []
    for name in (
        'class11_bulk_upload_ready.xlsx',
        os.path.join('xlsx', 'class11_bulk_upload_ready.xlsx'),
    ):
        if os.path.exists(name):
            candidate_files.append(name)

    # Also scan xlsx/ folder for any .xlsx
    xlsx_dir = 'xlsx'
    if os.path.isdir(xlsx_dir):
        for fn in os.listdir(xlsx_dir):
            if fn.lower().endswith(('.xlsx', '.xls')):
                candidate_files.append(os.path.join(xlsx_dir, fn))

    candidate_path = None
    for path in candidate_files:
        if os.path.isfile(path):
            candidate_path = path
            break

    if not candidate_path:
        results['validate'] = 'skipped (no xlsx file found)'
        results['preview'] = 'skipped'
        results['upload'] = 'skipped'
        results['confirm'] = 'skipped'
        return results

    # 2) Validate
    with open(candidate_path, 'rb') as f:
        data = {
            'excel_file': (f, os.path.basename(candidate_path)),
        }
        resp = client.post('/bulk-upload/validate-excel', data=data, content_type='multipart/form-data')
        results['validate'] = {'status': resp.status_code, 'json': safe_json(resp)}

    # 3) Preview
    with open(candidate_path, 'rb') as f:
        data = {
            'excel_file': (f, os.path.basename(candidate_path)),
        }
        resp = client.post('/bulk-upload/preview-excel', data=data, content_type='multipart/form-data')
        results['preview'] = {'status': resp.status_code, 'json': safe_json(resp)}

    # 4) Upload (returns excel_path for confirm)
    with open(candidate_path, 'rb') as f:
        data = {
            'excel_file': (f, os.path.basename(candidate_path)),
            'uploaded_by': 'admin-test',
        }
        resp = client.post('/bulk-upload/upload-excel', data=data, content_type='multipart/form-data')
        results['upload'] = {'status': resp.status_code, 'json': safe_json(resp)}

    excel_path = None
    try:
        excel_path = results['upload']['json'].get('excel_path')
    except Exception:
        excel_path = None

    # 5) Confirm
    if excel_path and os.path.exists(excel_path):
        payload = {'excel_path': excel_path, 'uploaded_by': 'admin-test', 'options': {}}
        resp = client.post('/bulk-upload/confirm-upload', data=json.dumps(payload), content_type='application/json')
        results['confirm'] = {'status': resp.status_code, 'json': safe_json(resp)}
    else:
        results['confirm'] = 'skipped (no excel_path)'

    return results


def check_single_resource_upload(client) -> dict:
    results: dict = {'page': None, 'post': None}

    # GET page
    resp = client.get('/upload-resource')
    results['page'] = resp.status_code

    class_id = pick_any_class_id()
    if not class_id:
        results['post'] = 'skipped (no class in DB)'
        return results

    # Prepare a tiny PNG file in memory
    png_bytes = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
                 b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
    data = {
        'class_id': str(class_id),
        'title': 'Admin Test Upload',
        'description': 'Automated test upload',
        'category': 'worksheet',
        'paid_status': 'unpaid',
    }
    file_data = {
        'file': (io.BytesIO(png_bytes), 'test.png')
    }
    # Merge form data and file
    multipart = {}
    multipart.update(data)
    multipart.update(file_data)

    resp = client.post('/upload-resource', data=multipart, content_type='multipart/form-data', follow_redirects=False)
    results['post'] = resp.status_code
    return results


def safe_json(resp):
    try:
        return resp.get_json(silent=True) or {}
    except Exception:
        return {}


def main():
    print('=== Admin Upload Feature Checks ===')
    with admin_client() as client:
        # Bulk upload checks
        bulk = check_bulk_upload(client)
        print('\n[Bulk Upload]')
        print(json.dumps(bulk, indent=2))

        # Single resource upload
        single = check_single_resource_upload(client)
        print('\n[Single Resource Upload]')
        print(json.dumps(single, indent=2))


if __name__ == '__main__':
    main()


