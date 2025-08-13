#!/usr/bin/env python3
import os
import sqlite3
import sys
from typing import Dict, List, Optional, Tuple

"""
Google Drive Class/Category Folder Sync

- Reads classes and their categories from users.db
- Ensures Drive folder structure under ROOT_FOLDER (class folders -> category folders)
- Uses service account/OAuth via GOOGLE_APPLICATION_CREDENTIALS when available

Usage:
  ROOT_FOLDER_ID=your_drive_folder_id python3 google_drive_sync_structure.py

Notes:
- Requires google-api-python-client and google-auth if you want real Drive ops
- If credentials are missing, runs in dry-run mode and prints planned actions
"""

DEFAULT_DB = os.environ.get('DB_PATH', 'users.db')
ROOT_FOLDER_ID = os.environ.get('ROOT_FOLDER_ID') or os.environ.get('GDRIVE_ROOT_FOLDER')

# Default categories if none found for a class
FALLBACK_CATEGORIES = [
    'Study Material',
    'Assignments',
    'Notes',
    'Practice Tests',
    'Reference Books',
    'Videos'
]


def sanitize_name(name: str) -> str:
    name = (name or '').strip()
    return name.replace('/', '-').replace('\n', ' ').strip()


def fetch_classes_and_categories(db_path: str) -> Dict[str, List[str]]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('SELECT id, name FROM classes')
        classes = c.fetchall()
        result: Dict[str, List[str]] = {}
        for class_id, class_name in classes:
            class_name = sanitize_name(class_name)
            try:
                c2 = conn.cursor()
                c2.execute('SELECT DISTINCT category FROM resources WHERE class_id = ?', (class_id,))
                cats = [sanitize_name(r[0]) for r in c2.fetchall() if r and r[0]]
                if not cats:
                    cats = FALLBACK_CATEGORIES
                result[class_name] = cats
            except Exception:
                result[class_name] = FALLBACK_CATEGORIES
        return result
    finally:
        conn.close()


def get_drive_service():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = None
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if cred_path and os.path.exists(cred_path):
            scopes = ['https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
        if not creds:
            # Try default credentials (ADC)
            from google.auth import default
            creds, _ = default(scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        print('[WARN] Google Drive API not available or credentials missing. Running in dry-run mode.', e)
        return None


def drive_find_folder(service, name: str, parent_id: str) -> Optional[str]:
    if not service:
        return None
    from googleapiclient.errors import HttpError
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
    try:
        resp = service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
        files = resp.get('files', [])
        if files:
            return files[0]['id']
        return None
    except HttpError as e:
        print('[ERROR] drive_find_folder:', e)
        return None


def drive_create_folder(service, name: str, parent_id: str) -> Optional[str]:
    if not service:
        return None
    from googleapiclient.errors import HttpError
    try:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        f = service.files().create(body=file_metadata, fields='id').execute()
        return f.get('id')
    except HttpError as e:
        print('[ERROR] drive_create_folder:', e)
        return None


def ensure_folder(service, name: str, parent_id: str, dry_run: bool) -> Tuple[str, bool]:
    """Return (folder_id or '', created_flag)"""
    name = sanitize_name(name)
    if dry_run or not service:
        print(f"[DRY] Ensure folder '{name}' under {parent_id}")
        return '', True
    found = drive_find_folder(service, name, parent_id)
    if found:
        return found, False
    created = drive_create_folder(service, name, parent_id)
    return created or '', True


def sync_structure(root_folder_id: str, db_path: str):
    if not root_folder_id:
        print('[ERROR] ROOT_FOLDER_ID not provided. Set env ROOT_FOLDER_ID or GDRIVE_ROOT_FOLDER.')
        sys.exit(1)
    mapping = fetch_classes_and_categories(db_path)
    service = get_drive_service()
    dry_run = service is None
    total_created = 0

    for class_name, categories in mapping.items():
        class_folder_id, created = ensure_folder(service, class_name, root_folder_id, dry_run)
        if created:
            total_created += 1
            print(f"[INFO] Class folder ensured: {class_name}")
        parent = class_folder_id if class_folder_id else root_folder_id
        for cat in categories:
            _, created2 = ensure_folder(service, cat, parent, dry_run)
            if created2:
                total_created += 1
                print(f"[INFO] Category folder ensured: {class_name}/{cat}")
    print(f"[DONE] Sync complete. Folders created/ensured: {total_created}")


if __name__ == '__main__':
    sync_structure(ROOT_FOLDER_ID, DEFAULT_DB)