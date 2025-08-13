#!/usr/bin/env python3
import os
import time
import json
import tempfile
import requests
from datetime import datetime

"""
Polling-based watcher for a Google Drive folder.
- Lists files recursively under the provided folder ID
- Detects new files (by ID) and prints to terminal
- For each new file, attempts to infer class/category from its Drive path
- Generates a temporary Excel (Study Resources Upload sheet) and posts to unified confirm

Note: This script uses Drive API via requests as a placeholder. Replace list_folder_files() with
actual Google Drive API calls using google-api-python-client for production use.
"""

DRIVE_FOLDER_ID = os.environ.get('GDRIVE_ROOT_FOLDER', '1BTLUDbDjRd0oTdezQXyC_9F_3fTXWHET')
API_BASE = os.environ.get('APP_BASE', 'http://localhost:10000')
STATE_FILE = os.environ.get('DRIVE_WATCH_STATE', 'drive_watch_state.json')
POLL_SEC = int(os.environ.get('DRIVE_POLL_SEC', '60'))

# Placeholder: in real use, wire Google API here

def list_folder_files(folder_id):
    # TODO: implement using Google Drive API (Files: list with parents=folder_id)
    # Returning empty list as placeholder
    return []


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'seen_ids': []}


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def infer_class_and_category_from_path(drive_path_parts):
    # Heuristic: [Class]/[Category]/filename
    class_name = drive_path_parts[0] if len(drive_path_parts) >= 1 else ''
    category = drive_path_parts[1] if len(drive_path_parts) >= 2 else 'Study Material'
    return class_name, category


def build_temp_excel_for_files(file_records):
    # file_records: list of dict with keys: file_name, local_path, title, description, category, class
    import pandas as pd
    df = pd.DataFrame([
        {
            'File Name': r['file_name'],
            'File Path': r['local_path'],
            'Title': r.get('title') or r['file_name'],
            'Description': r.get('description',''),
            'Category': r.get('category','Study Material'),
            'Class': r.get('class','')
        }
        for r in file_records
    ])
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(tmp.name, index=False, sheet_name='Study Resources Upload')
    return tmp.name


def process_new_files(new_files):
    if not new_files:
        return
    # Download files to a temp dir and create excel
    file_records = []
    temp_dir = tempfile.mkdtemp()
    for f in new_files:
        # f expected keys: id, name, path_parts, download_url
        class_name, category = infer_class_and_category_from_path(f.get('path_parts', []))
        local_path = os.path.join(temp_dir, f['name'])
        # Placeholder download: in real use, fetch from Drive download URL
        # with open(local_path,'wb') as out: out.write(requests.get(f['download_url']).content)
        # For now, skip download and log only
        print(f"[INFO] New Drive file detected: {f['name']} | class={class_name} category={category}")
        # Without real file download, we cannot push to bulk upload. Keep just terminal log for now.
        file_records.append({
            'file_name': f['name'],
            'local_path': local_path,
            'title': f['name'],
            'description': '',
            'category': category,
            'class': class_name
        })
    # Build excel and call unified confirm (disabled until download implemented)
    # excel_path = build_temp_excel_for_files(file_records)
    # payload = {'excel_path': excel_path, 'uploaded_by': 'drive_watcher', 'options': {'skip_duplicates': True, 'skip_missing': True}}
    # r = requests.post(f"{API_BASE}/bulk-upload/unified/confirm", json=payload, timeout=30)
    # print('[INFO] Bulk upload response:', r.status_code, r.text[:200])


def main():
    state = load_state()
    print('[Drive Watcher] Watching folder', DRIVE_FOLDER_ID)
    while True:
        try:
            items = list_folder_files(DRIVE_FOLDER_ID)
            # Expect each item: id, name, path_parts, download_url
            new_files = [it for it in items if it['id'] not in state['seen_ids']]
            if new_files:
                process_new_files(new_files)
                state['seen_ids'].extend([it['id'] for it in new_files])
                save_state(state)
            else:
                print(f"[{datetime.now().isoformat()}] No new files.")
        except Exception as e:
            print('[ERROR] Drive watcher error:', e)
        time.sleep(POLL_SEC)

if __name__ == '__main__':
    main()