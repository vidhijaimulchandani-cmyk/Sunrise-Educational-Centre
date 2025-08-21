#!/usr/bin/env python3
import sys
from app import app

app.testing = True
client = app.test_client()

routes = [
    '/',
    '/auth',
    '/forum',
    '/api/recent-queries',
    '/upload-resource',
    '/study-resources',
    '/admin',
    '/preview/nonexistent.pdf',
    '/pdf-content/nonexistent.pdf',
    '/user',
    '/content-management',
    '/live-class-management',
    '/special-dashboard',
    '/admin/admissions',
]

any_fail = False
for path in routes:
    try:
        resp = client.get(path, follow_redirects=False)
        status = resp.status_code
        marker = 'OK'
        if status >= 500:
            marker = 'ERROR'
            any_fail = True
        elif status in (301, 302, 303, 307, 308):
            marker = f"REDIRECT -> {resp.headers.get('Location')}"
        print(f"{path}: {status} {marker}")
        if status >= 500:
            body = resp.get_data(as_text=True)[:500].replace('\n', ' ')
            print(f"  Body (first 500 chars): {body}")
    except Exception as e:
        any_fail = True
        print(f"{path}: EXCEPTION {e}")

sys.exit(1 if any_fail else 0)