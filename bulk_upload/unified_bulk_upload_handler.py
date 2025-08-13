import os
import sqlite3
import pandas as pd
from datetime import datetime
import shutil
import logging
from typing import Optional, Tuple, List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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