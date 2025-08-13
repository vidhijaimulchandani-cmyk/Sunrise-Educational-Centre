import os
import sqlite3
import pandas as pd
from datetime import datetime
import shutil
import logging
from typing import Optional, Tuple, List, Dict
import requests

try:
    from google.oauth2 import service_account  # type: ignore
    from googleapiclient.discovery import build  # type: ignore
    from googleapiclient.errors import HttpError  # type: ignore
    _GOOGLE_AVAILABLE = True
except Exception:
    _GOOGLE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

class UnifiedBulkUploadHandler:
    """
    Unified handler that supports both Study Resources uploads and Generic file uploads
    via a single interface. It can:
      - Validate Excel files (auto-detect supported sheet)
      - Process uploads with options (skip duplicates/missing, dry run)
      - Generate a master template (two sheets)
      - Export a master Excel workbook of existing records (two sheets)
    """
    def __init__(self, upload_folder='uploads', db_path='users.db'):
        self.upload_folder = upload_folder
        self.db_path = db_path
        # Lazily import existing handlers if available
        try:
            from .study_resources_handler import StudyResourcesBulkUploadHandler
            self.study = StudyResourcesBulkUploadHandler(upload_folder, db_path)
        except Exception:
            self.study = None
        try:
            from .bulk_upload_handler import BulkUploadHandler
            self.files = BulkUploadHandler(upload_folder, db_path)
        except Exception:
            self.files = None

    # ---------- Validation ----------
    def detect_sheet_type(self, excel_path):
        """Return ('study_resources'|'files'|None, sheet_name) based on columns/sheets."""
        try:
            xl = pd.ExcelFile(excel_path)
            # Prefer conventional sheet names
            sheet_candidates = list(xl.sheet_names)
            # Check for study resources sheet
            if 'Study Resources Upload' in sheet_candidates:
                df = pd.read_excel(excel_path, sheet_name='Study Resources Upload')
                if self._is_study_resources_df(df):
                    return 'study_resources', 'Study Resources Upload'
            # Otherwise inspect sheets to guess
            for sn in sheet_candidates:
                df = pd.read_excel(excel_path, sheet_name=sn)
                if self._is_study_resources_df(df):
                    return 'study_resources', sn
                if self._is_files_df(df):
                    return 'files', sn
            return None, None
        except Exception as e:
            logger.error(f"detect_sheet_type error: {e}")
            return None, None

    def _is_study_resources_df(self, df: pd.DataFrame) -> bool:
        required = {'File Name','File Path','Title','Category','Class'}
        return required.issubset(set(df.columns))

    def _is_files_df(self, df: pd.DataFrame) -> bool:
        required = {'File Name','Category','Description','File Path'}
        return required.issubset(set(df.columns))

    def validate_excel_file(self, excel_path):
        kind, sheet = self.detect_sheet_type(excel_path)
        if not kind:
            return False, 'Unsupported Excel format. Expected Study Resources or Files template.'
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet)
            if kind == 'study_resources':
                # basic validation
                if df.empty:
                    return False, 'Excel file is empty'
                for idx, row in df.iterrows():
                    if not str(row.get('File Name','')).strip():
                        return False, f"Row {idx+2}: File Name is required"
                    if not str(row.get('File Path','')).strip():
                        return False, f"Row {idx+2}: File Path is required"
                    if not str(row.get('Title','')).strip():
                        return False, f"Row {idx+2}: Title is required"
                    if not str(row.get('Category','')).strip():
                        return False, f"Row {idx+2}: Category is required"
                    if not str(row.get('Class','')).strip():
                        return False, f"Row {idx+2}: Class is required"
                return True, f"Valid Study Resources sheet '{sheet}' with {len(df)} rows"
            else:
                if df.empty:
                    return False, 'Excel file is empty'
                for idx, row in df.iterrows():
                    if not str(row.get('File Name','')).strip():
                        return False, f"Row {idx+2}: File Name is required"
                    if not str(row.get('Category','')).strip():
                        return False, f"Row {idx+2}: Category is required"
                    if not str(row.get('File Path','')).strip():
                        return False, f"Row {idx+2}: File Path is required"
                return True, f"Valid Files sheet '{sheet}' with {len(df)} rows"
        except Exception as e:
            return False, f"Error reading Excel: {e}"

    # ---------- Processing ----------
    def process_excel(self, excel_path, uploaded_by='admin', options=None):
        kind, sheet = self.detect_sheet_type(excel_path)
        if kind == 'study_resources':
            if not self.study:
                return {'success': [], 'errors': ["Study resources handler unavailable"], 'total_files': 0,
                        'successful_uploads': 0, 'failed_uploads': 0, 'skipped': [], 'skipped_duplicates': 0,
                        'skipped_missing': 0, 'dry_run': bool(options and options.get('dry_run'))}
            # Delegate with options
            return self.study.process_study_resources_excel(excel_path, uploaded_by, options or {})
        elif kind == 'files':
            if not self.files:
                return {'success': [], 'errors': ["Generic files handler unavailable"], 'total_files': 0,
                        'successful_uploads': 0, 'failed_uploads': 0}
            # Use existing generic handler
            return self.files.process_excel_upload(excel_path, uploaded_by)
        else:
            return {'success': [], 'errors': ["Unsupported Excel format"], 'total_files': 0,
                    'successful_uploads': 0, 'failed_uploads': 0}

    # ---------- Templates ----------
    def create_master_template(self, output_path):
        """Create a master workbook with two sheets: Study Resources Upload and Files Upload."""
        try:
            study_df = pd.DataFrame({
                'File Name': ['algebra_basics.pdf'],
                'File Path': ['/absolute/path/to/algebra_basics.pdf'],
                'Title': ['Algebra Basics - Chapter 1'],
                'Description': ['Introduction to algebraic expressions and equations'],
                'Category': ['Study Material'],
                'Class': ['10th']
            })
            files_df = pd.DataFrame({
                'File Name': ['example_document.pdf'],
                'Category': ['notes'],
                'Description': ['Sample notes file'],
                'File Path': ['/absolute/path/to/notes.txt']
            })
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                study_df.to_excel(writer, index=False, sheet_name='Study Resources Upload')
                files_df.to_excel(writer, index=False, sheet_name='Files Upload')
            return True
        except Exception as e:
            logger.error(f"Failed to create master template: {e}")
            return False

    # ---------- Export Master Records ----------
    def export_master_excel(self, output_path):
        """Export a master workbook with current DB records: resources and uploaded_files."""
        try:
            conn = sqlite3.connect(self.db_path)
            resources_df = pd.read_sql_query(
                'SELECT r.id, r.filename, r.filepath as file_path, r.title, r.description, r.category, c.name as class_name '
                'FROM resources r LEFT JOIN classes c ON c.id = r.class_id', conn)
            try:
                uploaded_files_df = pd.read_sql_query(
                    'SELECT id, filename, original_filename, category, description, file_path, file_size, upload_date, uploaded_by '
                    'FROM uploaded_files', conn)
            except Exception:
                uploaded_files_df = pd.DataFrame()
            conn.close()
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                resources_df.to_excel(writer, index=False, sheet_name='Study Resources')
                uploaded_files_df.to_excel(writer, index=False, sheet_name='Uploaded Files')
            return True
        except Exception as e:
            logger.error(f"Failed to export master excel: {e}")
            return False

    # =====================
    # Google Drive Utilities
    # =====================
    def get_drive_service(self):
        if not _GOOGLE_AVAILABLE:
            logger.warning('Google Drive libraries not available; Drive ops in dry-run mode')
            return None
        try:
            creds = None
            cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if cred_path and os.path.exists(cred_path):
                scopes = ['https://www.googleapis.com/auth/drive']
                creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
            if not creds:
                from google.auth import default  # type: ignore
                creds, _ = default(scopes=['https://www.googleapis.com/auth/drive'])
            service = build('drive', 'v3', credentials=creds, cache_discovery=False)
            return service
        except Exception as e:
            logger.warning(f'Google Drive service init failed: {e}. Drive ops in dry-run mode')
            return None

    def drive_find_folder(self, service, name: str, parent_id: str) -> Optional[str]:
        if not service:
            return None
        try:
            query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
            resp = service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
            files = resp.get('files', [])
            if files:
                return files[0]['id']
            return None
        except Exception as e:
            logger.error(f'drive_find_folder error: {e}')
            return None

    def drive_create_folder(self, service, name: str, parent_id: str) -> Optional[str]:
        if not service:
            return None
        try:
            file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            f = service.files().create(body=file_metadata, fields='id').execute()
            return f.get('id')
        except Exception as e:
            logger.error(f'drive_create_folder error: {e}')
            return None

    def ensure_drive_folder(self, service, name: str, parent_id: str, dry_run: bool) -> Tuple[str, bool]:
        name = (name or '').strip().replace('/', '-')
        if dry_run or not service:
            logger.info(f"[DRY] Ensure folder '{name}' under {parent_id}")
            return '', True
        found = self.drive_find_folder(service, name, parent_id)
        if found:
            return found, False
        created = self.drive_create_folder(service, name, parent_id)
        return created or '', True

    def sync_drive_structure(self, root_folder_id: str) -> Dict[str, int]:
        """Ensure class folders and category subfolders under a Drive root."""
        if not root_folder_id:
            raise ValueError('root_folder_id required')
        # Build class->categories from DB
        import sqlite3
        mapping: Dict[str, List[str]] = {}
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, name FROM classes')
        classes = c.fetchall()
        for class_id, class_name in classes:
            try:
                c2 = conn.cursor()
                c2.execute('SELECT DISTINCT category FROM resources WHERE class_id=?', (class_id,))
                cats = [row[0] for row in c2.fetchall() if row and row[0]] or ['Study Material','Assignments','Notes','Practice Tests','Reference Books','Videos']
                mapping[str(class_name)] = cats
            except Exception:
                mapping[str(class_name)] = ['Study Material','Assignments','Notes','Practice Tests','Reference Books','Videos']
        conn.close()
        service = self.get_drive_service()
        dry = service is None
        created_count = 0
        for class_name, categories in mapping.items():
            class_id_drive, created = self.ensure_drive_folder(service, class_name, root_folder_id, dry)
            if created:
                created_count += 1
                logger.info(f'Ensured class folder: {class_name}')
            parent = class_id_drive if class_id_drive else root_folder_id
            for cat in categories:
                _, created2 = self.ensure_drive_folder(service, cat, parent, dry)
                if created2:
                    created_count += 1
                    logger.info(f'Ensured category folder: {class_name}/{cat}')
        return {'created_or_ensured': created_count}

    def scan_drive_new_files(self, root_folder_id: str, since_token: Optional[str]=None) -> Dict:
        """Scan for new files under root. If Google API unavailable, returns empty list.
        For production, implement changes feed or search by modifiedTime.
        """
        service = self.get_drive_service()
        if not service:
            # Fallback: API key for PUBLIC folders/files only
            if GOOGLE_API_KEY:
                try:
                    resp = requests.get(
                        'https://www.googleapis.com/drive/v3/files',
                        params={
                            'q': f"'{root_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
                            'fields': 'files(id,name,mimeType,modifiedTime)',
                            'key': GOOGLE_API_KEY
                        }, timeout=20
                    )
                    data = resp.json()
                    files = data.get('files', []) if resp.ok else []
                    return {'files': files, 'next_token': since_token, 'mode': 'api_key'}
                except Exception as e:
                    logger.error(f'API key scan error: {e}')
                    return {'files': [], 'next_token': since_token, 'mode': 'api_key'}
            logger.info('Drive scan in dry-run (no Google API). Returning empty result.')
            return {'files': [], 'next_token': since_token}
        try:
            # Simplified: list files directly under root (non-recursive)
            resp = service.files().list(q=f"'{root_folder_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'",
                                        spaces='drive', fields='files(id, name, mimeType, modifiedTime)', pageSize=100).execute()
            files = resp.get('files', [])
            return {'files': files, 'next_token': since_token, 'mode': 'oauth'}
        except Exception as e:
            logger.error(f'Drive scan error: {e}')
            return {'files': [], 'next_token': since_token}

    def import_drive_files_via_excel(self, file_entries: List[Dict], class_hint: Optional[str]=None, category_hint: Optional[str]=None) -> Dict:
        """Given Drive file entries (with 'name' and 'local_path' provided), build an Excel and process via study resources."""
        import pandas as pd, tempfile
        rows = []
        for fe in file_entries:
            rows.append({
                'File Name': fe.get('name'),
                'File Path': fe.get('local_path'),
                'Title': fe.get('title') or fe.get('name'),
                'Description': fe.get('description',''),
                'Category': fe.get('category') or category_hint or 'Study Material',
                'Class': fe.get('class') or class_hint or ''
            })
        if not rows:
            return {'success': True, 'message': 'No files to import', 'results': {}}
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        pd.DataFrame(rows).to_excel(tmp.name, index=False, sheet_name='Study Resources Upload')
        results = self.process_excel(tmp.name, uploaded_by='drive_auto', options={'skip_duplicates': True, 'skip_missing': True})
        return {'success': True, 'results': results}