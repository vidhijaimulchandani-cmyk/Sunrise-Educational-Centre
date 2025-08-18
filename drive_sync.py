"""
Google Drive sync helper for Study Resources

Usage patterns supported:
1) Hierarchical mapping by folder structure:
   ROOT_FOLDER
     ├─ ClassNameA
     │    ├─ notes
     │    ├─ worksheet
     │    └─ other
     └─ ClassNameB
          ├─ notes
          └─ other

2) Explicit mapping of Google Drive folder ID -> (class_id, category)

The sync function downloads new files from Google Drive to local 'uploads/' and
registers them into the study resources database using save_resource().
"""

from __future__ import annotations

import os
import io
from typing import Dict, Tuple, Optional, Set

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google.oauth2.service_account import Credentials
    GOOGLE_LIBS_AVAILABLE = True
except Exception:
    GOOGLE_LIBS_AVAILABLE = False

try:
    from werkzeug.utils import secure_filename
except Exception:
    def secure_filename(filename: str) -> str:
        import re
        return re.sub(r'[^a-zA-Z0-9._-]', '', filename)

from study_resources import (
    save_resource,
    get_resource_by_filename,
    get_all_classes,
    allowed_file,
    get_file_type,
)

UPLOADS_DIR = 'uploads'


def _ensure_uploads_dir() -> None:
    os.makedirs(UPLOADS_DIR, exist_ok=True)


def build_drive_service_from_service_account(json_credentials_path: str, scopes: Optional[Set[str]] = None):
    """Build a Drive API service using a Service Account JSON key file.

    Args:
        json_credentials_path: Path to the service account JSON key.
        scopes: Optional set of OAuth scopes. Defaults to Drive read-only.

    Returns:
        Google Drive service instance.
    """
    if not GOOGLE_LIBS_AVAILABLE:
        raise RuntimeError('Google API libraries not installed. Please install google-api-python-client and google-auth.')
    if scopes is None:
        scopes = {'https://www.googleapis.com/auth/drive.readonly'}
    creds = Credentials.from_service_account_file(json_credentials_path, scopes=list(scopes))
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


def _list_folder_children(service, folder_id: str):
    """List children (files/folders) under a given Drive folder ID."""
    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None
    items = []
    while True:
        resp = service.files().list(
            q=query,
            fields='nextPageToken, files(id, name, mimeType, modifiedTime)',
            pageToken=page_token
        ).execute()
        items.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return items


def _download_drive_file(service, file_id: str, target_path: str) -> None:
    """Download a Drive file to a local path."""
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(target_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()


def _get_class_name_to_id() -> Dict[str, int]:
    classes = get_all_classes()  # List[(id, name)]
    return {name: cid for cid, name in classes}


def sync_by_structure(
    service,
    root_folder_id: str,
    default_category: str = 'other',
    allowed_extensions: Optional[Set[str]] = None,
) -> Dict[str, int]:
    """Sync Drive files by folder structure mapping to (class -> category -> files).

    - Top-level folders under root map to class names (must match DB `classes.name`).
    - Second-level subfolders map to resource categories.
    - Files inside category folders are downloaded and registered.

    Args:
        service: Google Drive API service
        root_folder_id: ID of the root folder containing class folders
        default_category: Fallback category name if none found
        allowed_extensions: Optional set of allowed extensions (e.g., {'pdf'})

    Returns:
        Summary dict with counts: {'processed': N, 'skipped': M}
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf'}

    _ensure_uploads_dir()
    class_name_to_id = _get_class_name_to_id()

    summary = {'processed': 0, 'skipped': 0}

    class_folders = _list_folder_children(service, root_folder_id)
    for class_folder in class_folders:
        if class_folder.get('mimeType') != 'application/vnd.google-apps.folder':
            continue
        class_name = class_folder['name']
        class_id = class_name_to_id.get(class_name)
        if not class_id:
            summary['skipped'] += 1
            continue

        category_folders = _list_folder_children(service, class_folder['id'])
        for cat_folder in category_folders:
            if cat_folder.get('mimeType') != 'application/vnd.google-apps.folder':
                continue
            category_name = (cat_folder['name'] or default_category).strip().lower()

            files = _list_folder_children(service, cat_folder['id'])
            for f in files:
                if f.get('mimeType', '').startswith('application/vnd.google-apps.'):
                    # Skip Google Docs native formats in this basic sync; export logic can be added later
                    summary['skipped'] += 1
                    continue
                filename = secure_filename(f['name'])
                ext_ok = ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in allowed_extensions)
                if not ext_ok:
                    summary['skipped'] += 1
                    continue
                # Skip if already present by filename
                if get_resource_by_filename(filename):
                    summary['skipped'] += 1
                    continue
                # Download
                target_path = os.path.join(UPLOADS_DIR, filename)
                _download_drive_file(service, f['id'], target_path)
                # Save in DB
                title = os.path.splitext(filename)[0].replace('_', ' ').title()
                save_resource(
                    filename=filename,
                    class_id=class_id,
                    filepath=target_path,
                    title=title,
                    description=f"Imported from Google Drive: {class_name}/{category_name}",
                    category=category_name,
                    paid_status='unpaid',
                )
                summary['processed'] += 1

    return summary


def sync_by_mapping(
    service,
    folder_to_class_category: Dict[str, Tuple[int, str]],
    allowed_extensions: Optional[Set[str]] = None,
) -> Dict[str, int]:
    """Sync Drive files using explicit mapping: folder_id -> (class_id, category).

    Args:
        service: Google Drive API service
        folder_to_class_category: Dict mapping Drive folder ID to (class_id, category)
        allowed_extensions: Optional set like {'pdf'}

    Returns:
        Summary dict with counts.
    """
    if allowed_extensions is None:
        allowed_extensions = {'pdf'}

    _ensure_uploads_dir()
    summary = {'processed': 0, 'skipped': 0}

    for folder_id, (class_id, category) in folder_to_class_category.items():
        files = _list_folder_children(service, folder_id)
        for f in files:
            if f.get('mimeType', '').startswith('application/vnd.google-apps.'):
                summary['skipped'] += 1
                continue
            filename = secure_filename(f['name'])
            ext_ok = ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in allowed_extensions)
            if not ext_ok:
                summary['skipped'] += 1
                continue
            if get_resource_by_filename(filename):
                summary['skipped'] += 1
                continue
            target_path = os.path.join(UPLOADS_DIR, filename)
            _download_drive_file(service, f['id'], target_path)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()
            save_resource(
                filename=filename,
                class_id=class_id,
                filepath=target_path,
                title=title,
                description=f"Imported from Google Drive folder {folder_id}",
                category=category,
                paid_status='unpaid',
            )
            summary['processed'] += 1

    return summary

