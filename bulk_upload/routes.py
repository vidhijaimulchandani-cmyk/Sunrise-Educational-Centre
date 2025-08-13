from flask import Blueprint, request, jsonify, render_template, send_file, session
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from .bulk_upload_handler import BulkUploadHandler
from .study_resources_handler import StudyResourcesBulkUploadHandler
import logging
import glob
from .unified_bulk_upload_handler import UnifiedBulkUploadHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
bulk_upload_bp = Blueprint('bulk_upload', __name__, url_prefix='/bulk-upload')

# Initialize handlers
bulk_handler = BulkUploadHandler()
study_resources_handler = StudyResourcesBulkUploadHandler()
unified = UnifiedBulkUploadHandler()

@bulk_upload_bp.route('/')
def bulk_upload_page():
    """Render the bulk upload page"""
    return render_template('bulk_upload/bulk_upload.html')

@bulk_upload_bp.route('/upload-excel', methods=['POST'])
def upload_excel():
    """Handle Excel file upload and process bulk upload"""
    try:
        # Check if file was uploaded
        if 'excel_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['excel_file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Please upload an Excel file (.xlsx or .xls)'
            }), 400
        
        # Get uploaded by user (from session or request)
        uploaded_by = request.form.get('uploaded_by', 'admin')
        
        # Save uploaded Excel file temporarily
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(excel_path)
        
        try:
            # First, validate and preview the Excel file
            is_valid, message = study_resources_handler.validate_excel_file(excel_path)
            
            if not is_valid:
                # Clean up and return error
                os.remove(excel_path)
                os.rmdir(temp_dir)
                return jsonify({
                    'success': False,
                    'error': f'Excel validation failed: {message}'
                }), 400
            
            # Read Excel file for preview
            df = pd.read_excel(excel_path, sheet_name='Study Resources Upload')
            preview_data = df.head(10).to_dict('records')
            
            # Return preview data for user confirmation
            return jsonify({
                'success': True,
                'preview_data': preview_data,
                'total_files': len(df),
                'columns': list(df.columns),
                'excel_path': excel_path,  # Store path for later processing
                'message': f'Excel file validated successfully. Found {len(df)} files to upload.'
            })
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(excel_path):
                os.remove(excel_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            raise e
            
    except Exception as e:
        logger.error(f"Error in bulk upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@bulk_upload_bp.route('/confirm-upload', methods=['POST'])
def confirm_upload():
    """Confirm and process the upload after user review"""
    try:
        data = request.json
        # Accept both 'excel_path' (old) and 'file_path' (new)
        excel_path = data.get('excel_path') or data.get('file_path')
        uploaded_by = data.get('uploaded_by', 'admin')
        
        if not excel_path or not os.path.exists(excel_path):
            return jsonify({
                'success': False,
                'error': 'Excel file not found'
            }), 400
        
        # Process the Excel file
        options = data.get('options') or {}
        results = study_resources_handler.process_study_resources_excel(excel_path, uploaded_by, options)
        
        # Only delete the file if it is a temp file (not in xlsx folder)
        xlsx_folder = os.path.join(os.getcwd(), 'xlsx')
        try:
            if not excel_path.startswith(xlsx_folder):
                os.remove(excel_path)
                temp_dir = os.path.dirname(excel_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
        except:
            pass
        
        # Return results
        return jsonify({
            'success': True,
            'results': results,
            'message': f"Processed {results['total_files']} files. {results['successful_uploads']} successful, {results['failed_uploads']} failed."
        })
        
    except Exception as e:
        logger.error(f"Error in confirm upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

@bulk_upload_bp.route('/download-template')
def download_template():
    """Download Excel template for study resources bulk upload"""
    try:
        # Create template in temporary location
        temp_dir = tempfile.mkdtemp()
        template_path = os.path.join(temp_dir, 'study_resources_template.xlsx')
        
        # Generate template
        success = study_resources_handler.create_study_resources_template(template_path)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to create template'
            }), 500
        
        # Send file
        return send_file(
            template_path,
            as_attachment=True,
            download_name='study_resources_template.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error downloading template: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Template download failed: {str(e)}'
        }), 500

@bulk_upload_bp.route('/statistics')
def get_statistics():
    """Get upload statistics"""
    try:
        stats = bulk_handler.get_upload_statistics()
        
        if stats is None:
            return jsonify({
                'success': False,
                'error': 'Failed to get statistics'
            }), 500
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get statistics: {str(e)}'
        }), 500

@bulk_upload_bp.route('/validate-excel', methods=['POST'])
def validate_excel():
    """Validate Excel file before processing"""
    try:
        # Check if file was uploaded
        if 'excel_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['excel_file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Please upload an Excel file (.xlsx or .xls)'
            }), 400
        
        # Save uploaded Excel file temporarily
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(excel_path)
        
        try:
            # Validate the Excel file
            is_valid, message = study_resources_handler.validate_excel_file(excel_path)
            
            # Clean up temporary file
            os.remove(excel_path)
            os.rmdir(temp_dir)
            
            return jsonify({
                'success': True,
                'is_valid': is_valid,
                'message': message
            })
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(excel_path):
                os.remove(excel_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            raise e
            
    except Exception as e:
        logger.error(f"Error validating Excel: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500

@bulk_upload_bp.route('/preview-excel', methods=['POST'])
def preview_excel():
    """Preview Excel file contents"""
    try:
        # Check if file was uploaded
        if 'excel_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['excel_file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'error': 'Please upload an Excel file (.xlsx or .xls)'
            }), 400
        
        # Save uploaded Excel file temporarily
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(excel_path)
        
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(excel_path, sheet_name='Study Resources Upload')
            
            # Convert to list of dictionaries for JSON response
            preview_data = df.head(10).to_dict('records')
            
            # Clean up temporary file
            os.remove(excel_path)
            os.rmdir(temp_dir)
            
            return jsonify({
                'success': True,
                'preview_data': preview_data,
                'total_rows': len(df),
                'columns': list(df.columns)
            })
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(excel_path):
                os.remove(excel_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            raise e
            
    except Exception as e:
        logger.error(f"Error previewing Excel: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Preview failed: {str(e)}'
        }), 500

@bulk_upload_bp.route('/list-xlsx-files')
def list_xlsx_files():
    xlsx_folder = os.path.join(os.getcwd(), 'xlsx')
    if not os.path.exists(xlsx_folder):
        return jsonify({'success': True, 'files': [], 'message': 'xlsx folder does not exist'})
    files = sorted([
        os.path.basename(f)
        for f in glob.glob(os.path.join(xlsx_folder, '*.xlsx')) + glob.glob(os.path.join(xlsx_folder, '*.xls'))
        if os.path.isfile(f)
    ])
    return jsonify({'success': True, 'files': files, 'message': f'Found {len(files)} file(s).' if files else 'No Excel files found.'})

@bulk_upload_bp.route('/preview-xlsx-file', methods=['POST'])
def preview_xlsx_file():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'success': False, 'error': 'No filename provided'})
    xlsx_folder = os.path.join(os.getcwd(), 'xlsx')
    file_path = os.path.join(xlsx_folder, filename)
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'})
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        preview_data = df.head(10).to_dict('records')
        return jsonify({
            'success': True,
            'preview_data': preview_data,
            'total_rows': len(df),
            'columns': list(df.columns),
            'file_path': file_path,
            'message': f'Excel file loaded. Found {len(df)} rows.'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error reading Excel file: {str(e)}'})

@bulk_upload_bp.route('/check-duplicates', methods=['POST'])
def check_duplicates():
    """Check for potential duplicates and file existence before confirming upload"""
    try:
        data = request.get_json(force=True)
        excel_path = data.get('excel_path') or data.get('file_path')
        if not excel_path or not os.path.exists(excel_path):
            return jsonify({'success': False, 'error': 'Excel file path invalid'}), 400

        import pandas as pd
        df = pd.read_excel(excel_path, sheet_name='Study Resources Upload')

        # Open DB connection
        import sqlite3
        conn = sqlite3.connect(study_resources_handler.db_path)
        c = conn.cursor()

        # Build class name -> id map without creating new classes
        classes = {}
        c.execute('SELECT id, name FROM classes')
        for row in c.fetchall():
            classes[row[1]] = row[0]

        results = []
        for idx, row in df.iterrows():
            title = str(row.get('Title') or '').strip()
            class_name = str(row.get('Class') or '').strip()
            category = str(row.get('Category') or '').strip()
            file_path = str(row.get('File Path') or '').strip()

            class_id = classes.get(class_name)

            is_duplicate = False
            duplicate_reason = ''
            if class_id and title:
                # Check duplicate by title+class (and optionally category)
                try:
                    c.execute('SELECT COUNT(1) FROM resources WHERE title = ? AND class_id = ?', (title, class_id))
                    count = c.fetchone()[0] or 0
                    if count > 0:
                        is_duplicate = True
                        duplicate_reason = f"Title already exists in class '{class_name}'"
                except Exception:
                    pass

            file_exists = bool(file_path) and os.path.exists(file_path) and os.path.isfile(file_path)

            results.append({
                'index': int(idx),
                'title': title,
                'class': class_name,
                'category': category,
                'file_path': file_path,
                'file_exists': file_exists,
                'is_duplicate': is_duplicate,
                'duplicate_reason': duplicate_reason
            })

        conn.close()
        total = len(results)
        dup_count = sum(1 for r in results if r['is_duplicate'])
        missing_count = sum(1 for r in results if not r['file_exists'])

        return jsonify({
            'success': True,
            'summary': {
                'total_rows': total,
                'duplicates': dup_count,
                'missing_files': missing_count
            },
            'rows': results
        })
    except Exception as e:
        logger.error(f"Error checking duplicates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bulk_upload_bp.route('/unified/validate', methods=['POST'])
def unified_validate():
    try:
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        f = request.files['excel_file']
        if f.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        import tempfile
        from werkzeug.utils import secure_filename
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, secure_filename(f.filename))
        f.save(excel_path)
        ok, msg = unified.validate_excel_file(excel_path)
        try:
            os.remove(excel_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
        return jsonify({'success': ok, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bulk_upload_bp.route('/unified/preview', methods=['POST'])
def unified_preview():
    try:
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        f = request.files['excel_file']
        if f.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        import tempfile, pandas as pd
        from werkzeug.utils import secure_filename
        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, secure_filename(f.filename))
        f.save(excel_path)
        kind, sheet = unified.detect_sheet_type(excel_path)
        if not kind:
            return jsonify({'success': False, 'error': 'Unsupported Excel format'}), 400
        df = pd.read_excel(excel_path, sheet_name=sheet)
        preview_data = df.head(10).to_dict('records')
        return jsonify({'success': True, 'kind': kind, 'sheet': sheet, 'columns': list(df.columns), 'total_rows': len(df), 'preview_data': preview_data, 'excel_path': excel_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bulk_upload_bp.route('/unified/confirm', methods=['POST'])
def unified_confirm():
    try:
        data = request.get_json(force=True)
        excel_path = data.get('excel_path') or data.get('file_path')
        if not excel_path or not os.path.exists(excel_path):
            return jsonify({'success': False, 'error': 'Excel file not found'}), 400
        uploaded_by = data.get('uploaded_by', 'admin')
        options = data.get('options') or {}
        results = unified.process_excel(excel_path, uploaded_by, options)
        # Clean temp if not xlsx folder
        xlsx_folder = os.path.join(os.getcwd(), 'xlsx')
        try:
            if not excel_path.startswith(xlsx_folder):
                os.remove(excel_path)
                temp_dir = os.path.dirname(excel_path)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
        except Exception:
            pass
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bulk_upload_bp.route('/unified/template')
def download_master_template():
    try:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        out = os.path.join(temp_dir, 'bulk_master_template.xlsx')
        if unified.create_master_template(out):
            return send_file(out, as_attachment=True, download_name='bulk_master_template.xlsx')
        return jsonify({'success': False, 'error': 'Failed to create template'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bulk_upload_bp.route('/unified/export')
def export_master_records():
    try:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        out = os.path.join(temp_dir, 'bulk_master_export.xlsx')
        if unified.export_master_excel(out):
            return send_file(out, as_attachment=True, download_name='bulk_master_export.xlsx')
        return jsonify({'success': False, 'error': 'Failed to export'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handlers
@bulk_upload_bp.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large'
    }), 413

@bulk_upload_bp.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500 