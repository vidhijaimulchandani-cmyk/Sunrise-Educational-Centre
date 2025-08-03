from flask import Blueprint, request, jsonify, render_template, send_file, session
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from .bulk_upload_handler import BulkUploadHandler
from .study_resources_handler import StudyResourcesBulkUploadHandler
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
bulk_upload_bp = Blueprint('bulk_upload', __name__, url_prefix='/bulk-upload')

# Initialize handlers
bulk_handler = BulkUploadHandler()
study_resources_handler = StudyResourcesBulkUploadHandler()

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
        results = study_resources_handler.process_study_resources_excel(excel_path, uploaded_by)
        
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