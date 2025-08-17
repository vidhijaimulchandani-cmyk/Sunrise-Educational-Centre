import os
import pandas as pd
import sqlite3
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulkUploadHandler:
    def __init__(self, upload_folder='uploads', db_path='users.db'):
        self.upload_folder = upload_folder
        self.db_path = db_path
        self.allowed_extensions = {
            'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 
            'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar'
        }
        
        # Create upload folders if they don't exist
        self.create_upload_folders()
    
    def create_upload_folders(self):
        """Create necessary upload folders"""
        folders = [
            self.upload_folder,
            os.path.join(self.upload_folder, 'study_materials'),
            os.path.join(self.upload_folder, 'videos'),
            os.path.join(self.upload_folder, 'assignments'),
            os.path.join(self.upload_folder, 'notes'),
            os.path.join(self.upload_folder, 'other')
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                logger.info(f"Created folder: {folder}")
    
    def validate_excel_file(self, file_path):
        """Validate Excel file format and structure"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Check required columns
            required_columns = ['File Name', 'Category', 'Description', 'File Path']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Check if file is not empty
            if df.empty:
                return False, "Excel file is empty"
            
            # Validate data types and content
            for index, row in df.iterrows():
                if pd.isna(row['File Name']) or str(row['File Name']).strip() == '':
                    return False, f"Row {index + 2}: File Name is required"
                
                if pd.isna(row['Category']) or str(row['Category']).strip() == '':
                    return False, f"Row {index + 2}: Category is required"
                
                if pd.isna(row['File Path']) or str(row['File Path']).strip() == '':
                    return False, f"Row {index + 2}: File Path is required"
            
            return True, "Excel file is valid"
            
        except Exception as e:
            return False, f"Error reading Excel file: {str(e)}"
    
    def validate_file_exists(self, file_path):
        """Check if the file exists at the specified path"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    def get_file_extension(self, file_path):
        """Get file extension from file path"""
        return os.path.splitext(file_path)[1].lower().lstrip('.')
    
    def validate_file_extension(self, file_path):
        """Validate if file extension is allowed"""
        extension = self.get_file_extension(file_path)
        return extension in self.allowed_extensions
    
    def get_category_folder(self, category):
        """Get the appropriate folder for a category"""
        category_mapping = {
            'study material': 'study_materials',
            'study materials': 'study_materials',
            'video': 'videos',
            'videos': 'videos',
            'assignment': 'assignments',
            'assignments': 'assignments',
            'note': 'notes',
            'notes': 'notes'
        }
        
        category_lower = category.lower().strip()
        return category_mapping.get(category_lower, 'other')
    
    def copy_file_to_uploads(self, source_path, category, filename):
        """Copy file to appropriate upload folder"""
        try:
            category_folder = self.get_category_folder(category)
            destination_folder = os.path.join(self.upload_folder, category_folder)
            
            # Create category folder if it doesn't exist
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            # Generate unique filename if needed
            base_name, extension = os.path.splitext(filename)
            counter = 1
            final_filename = filename
            
            while os.path.exists(os.path.join(destination_folder, final_filename)):
                final_filename = f"{base_name}_{counter}{extension}"
                counter += 1
            
            destination_path = os.path.join(destination_folder, final_filename)
            
            # Copy file
            shutil.copy2(source_path, destination_path)
            
            return final_filename, destination_path
            
        except Exception as e:
            logger.error(f"Error copying file {source_path}: {str(e)}")
            return None, None
    
    def save_to_database(self, file_data):
        """Save file information to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create files table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Insert file data
            cursor.execute('''
                INSERT INTO uploaded_files 
                (filename, original_filename, category, description, file_path, file_size, uploaded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_data['filename'],
                file_data['original_filename'],
                file_data['category'],
                file_data['description'],
                file_data['file_path'],
                file_data['file_size'],
                file_data['uploaded_by']
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            return False
    
    def process_excel_upload(self, excel_file_path, uploaded_by='admin'):
        """Process Excel file for bulk upload"""
        results = {
            'success': [],
            'errors': [],
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0
        }
        
        try:
            # Validate Excel file
            is_valid, message = self.validate_excel_file(excel_file_path)
            if not is_valid:
                results['errors'].append(f"Excel validation failed: {message}")
                return results
            
            # Read Excel file
            df = pd.read_excel(excel_file_path)
            results['total_files'] = len(df)
            
            logger.info(f"Processing {results['total_files']} files from Excel")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    file_name = str(row['File Name']).strip()
                    category = str(row['Category']).strip()
                    description = str(row['Description']).strip() if pd.notna(row['Description']) else ''
                    file_path = str(row['File Path']).strip()
                    
                    # Validate file exists
                    if not self.validate_file_exists(file_path):
                        error_msg = f"Row {index + 2}: File not found at {file_path}"
                        results['errors'].append(error_msg)
                        results['failed_uploads'] += 1
                        continue
                    
                    # Validate file extension
                    if not self.validate_file_extension(file_path):
                        error_msg = f"Row {index + 2}: File type not allowed for {file_name}"
                        results['errors'].append(error_msg)
                        results['failed_uploads'] += 1
                        continue
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Copy file to uploads folder
                    new_filename, new_path = self.copy_file_to_uploads(file_path, category, file_name)
                    
                    if new_filename is None:
                        error_msg = f"Row {index + 2}: Failed to copy file {file_name}"
                        results['errors'].append(error_msg)
                        results['failed_uploads'] += 1
                        continue
                    
                    # Prepare file data for database
                    file_data = {
                        'filename': new_filename,
                        'original_filename': file_name,
                        'category': category,
                        'description': description,
                        'file_path': new_path,
                        'file_size': file_size,
                        'uploaded_by': uploaded_by
                    }
                    
                    # Save to database
                    if self.save_to_database(file_data):
                        success_msg = f"Successfully uploaded: {file_name}"
                        results['success'].append(success_msg)
                        results['successful_uploads'] += 1
                        logger.info(success_msg)
                    else:
                        error_msg = f"Row {index + 2}: Failed to save {file_name} to database"
                        results['errors'].append(error_msg)
                        results['failed_uploads'] += 1
                    
                except Exception as e:
                    error_msg = f"Row {index + 2}: Error processing {row.get('File Name', 'Unknown')}: {str(e)}"
                    results['errors'].append(error_msg)
                    results['failed_uploads'] += 1
                    logger.error(error_msg)
            
            logger.info(f"Bulk upload completed: {results['successful_uploads']} successful, {results['failed_uploads']} failed")
            
        except Exception as e:
            error_msg = f"Error processing Excel file: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def get_upload_statistics(self):
        """Get upload statistics from database. If the table doesn't exist yet, return empty stats."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure table exists; if not, return empty stats gracefully
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    category TEXT,
                    upload_date TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            conn.commit()
            
            # Get total files
            cursor.execute('SELECT COUNT(*) FROM uploaded_files WHERE status = "active"')
            total_files = cursor.fetchone()[0]
            
            # Get files by category
            cursor.execute('''
                SELECT category, COUNT(*) 
                FROM uploaded_files 
                WHERE status = "active" 
                GROUP BY category
            ''')
            category_stats = dict(cursor.fetchall())
            
            # Get recent uploads
            cursor.execute('''
                SELECT filename, category, upload_date 
                FROM uploaded_files 
                WHERE status = "active" 
                ORDER BY upload_date DESC 
                LIMIT 10
            ''')
            recent_uploads = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_files': total_files,
                'category_stats': category_stats,
                'recent_uploads': recent_uploads
            }
            
        except Exception as e:
            logger.error(f"Error getting upload statistics: {str(e)}")
            return {
                'total_files': 0,
                'category_stats': {},
                'recent_uploads': []
            }
    
    def create_excel_template(self, output_path='file_upload_template.xlsx'):
        """Create Excel template for file uploads"""
        try:
            # Sample data for template
            template_data = {
                'File Name': [
                    'example_document.pdf',
                    'lecture_video.mp4',
                    'assignment.docx',
                    'notes.txt'
                ],
                'Category': [
                    'Study Material',
                    'Video',
                    'Assignment',
                    'Notes'
                ],
                'Description': [
                    'Sample PDF document',
                    'Sample video lecture',
                    'Sample assignment file',
                    'Sample notes file'
                ],
                'File Path': [
                    '/path/to/example_document.pdf',
                    '/path/to/lecture_video.mp4',
                    '/path/to/assignment.docx',
                    '/path/to/notes.txt'
                ]
            }
            
            df = pd.DataFrame(template_data)
            df.to_excel(output_path, index=False)
            
            logger.info(f"Excel template created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Excel template: {str(e)}")
            return False

    def create_queries_table(self):
        """Create the queries table for 'Any More Query' submissions if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    message TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("'queries' table ensured in database.")
        except Exception as e:
            logger.error(f"Error creating queries table: {str(e)}")

    def save_query(self, name, email, message):
        """Save a new query to the queries table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO queries (name, email, message) VALUES (?, ?, ?)
            ''', (name, email, message))
            conn.commit()
            conn.close()
            logger.info(f"Saved query from {name} ({email})")
            return True
        except Exception as e:
            logger.error(f"Error saving query: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize handler
    handler = BulkUploadHandler()
    
    # Create template
    handler.create_excel_template()
    
    # Example: Process Excel file (uncomment to test)
    # results = handler.process_excel_upload('path/to/your/excel/file.xlsx')
    # print(f"Upload Results: {results}")
    
    # Get statistics
    stats = handler.get_upload_statistics()
    print(f"Upload Statistics: {stats}") 