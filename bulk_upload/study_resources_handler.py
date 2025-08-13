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

class StudyResourcesBulkUploadHandler:
    def __init__(self, upload_folder='uploads', db_path='users.db'):
        self.upload_folder = upload_folder
        self.db_path = db_path
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'txt'}
        
        # Create upload folders if they don't exist
        self.create_upload_folders()
    
    def create_upload_folders(self):
        """Create necessary upload folders for study resources"""
        folders = [
            self.upload_folder,
            os.path.join(self.upload_folder, 'study_materials'),
            os.path.join(self.upload_folder, 'assignments'),
            os.path.join(self.upload_folder, 'notes'),
            os.path.join(self.upload_folder, 'practice_tests'),
            os.path.join(self.upload_folder, 'reference_books'),
            os.path.join(self.upload_folder, 'videos'),
            os.path.join(self.upload_folder, 'other')
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                logger.info(f"Created folder: {folder}")
    
    def validate_excel_file(self, file_path):
        """Validate Excel file format and structure for study resources"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name='Study Resources Upload')
            
            # Check required columns
            required_columns = ['File Name', 'File Path', 'Title', 'Category', 'Class']
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
                
                if pd.isna(row['File Path']) or str(row['File Path']).strip() == '':
                    return False, f"Row {index + 2}: File Path is required"
                
                if pd.isna(row['Title']) or str(row['Title']).strip() == '':
                    return False, f"Row {index + 2}: Title is required"
                
                if pd.isna(row['Category']) or str(row['Category']).strip() == '':
                    return False, f"Row {index + 2}: Category is required"
                
                if pd.isna(row['Class']) or str(row['Class']).strip() == '':
                    return False, f"Row {index + 2}: Class is required"
            
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
            'assignment': 'assignments',
            'assignments': 'assignments',
            'note': 'notes',
            'notes': 'notes',
            'practice test': 'practice_tests',
            'practice tests': 'practice_tests',
            'reference book': 'reference_books',
            'reference books': 'reference_books',
            'video': 'videos',
            'videos': 'videos'
        }
        
        category_lower = category.lower().strip()
        return category_mapping.get(category_lower, 'other')
    
    def get_class_id(self, class_name):
        """Get class ID from class name"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM classes WHERE name = ?', (class_name,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            else:
                # If class doesn't exist, create it
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('INSERT INTO classes (name) VALUES (?)', (class_name,))
                class_id = cursor.lastrowid
                
                conn.commit()
                conn.close()
                
                logger.info(f"Created new class: {class_name} with ID: {class_id}")
                return class_id
                
        except Exception as e:
            logger.error(f"Error getting class ID: {str(e)}")
            return None
    
    def copy_file_to_uploads(self, source_path, category, filename, class_name=None):
        """Copy file to appropriate upload folder; nest by class/category if class_name provided"""
        try:
            category_folder = self.get_category_folder(category)
            safe_class = None
            if class_name:
                safe_class = ''.join(c for c in class_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            # Build nested path uploads/<class>/<category> if class provided else uploads/<category>
            if safe_class:
                destination_folder = os.path.join(self.upload_folder, safe_class, category_folder)
            else:
                destination_folder = os.path.join(self.upload_folder, category_folder)
            
            # Create folder if it doesn't exist
            os.makedirs(destination_folder, exist_ok=True)
            
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
    
    def save_to_study_resources(self, file_data):
        """Save file information to study resources database and send notification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Get class ID
            class_id = self.get_class_id(file_data['class'])
            if class_id is None:
                return False
            # Insert into resources table
            cursor.execute('''
                INSERT INTO resources 
                (filename, class_id, filepath, title, description, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_data['filename'],
                class_id,
                file_data['file_path'],
                file_data['title'],
                file_data['description'],
                file_data['category']
            ))
            # Send notification to all users of the class
            try:
                from auth_handler import add_notification
                paid_categories = ['worksheet', 'formula', 'formula sheet']
                target_paid_status = 'paid' if file_data['category'].lower() in paid_categories else 'all'
                add_notification(
                    f'New {file_data["category"]} uploaded: {file_data["title"]}', 
                    class_id, 
                    target_paid_status,
                    status='active',
                    notification_type='study_resource'
                )
            except Exception as e:
                logger.error(f"Error sending notification: {str(e)}")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving to study resources: {str(e)}")
            return False
    
    def is_duplicate_resource(self, title, class_name):
        """Return True if a resource with same title exists in the class"""
        try:
            if not title or not class_name:
                return False
            class_id = self.get_class_id(class_name)
            if class_id is None:
                return False
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(1) FROM resources WHERE title = ? AND class_id = ?', (title, class_id))
            count = cursor.fetchone()[0] or 0
            conn.close()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking duplicate resource: {str(e)}")
            return False
    
    def process_study_resources_excel(self, excel_file_path, uploaded_by='admin', options=None):
        """Process Excel file for bulk study resources upload with options"""
        results = {
            'success': [],
            'errors': [],
            'skipped': [],
            'total_files': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'skipped_duplicates': 0,
            'skipped_missing': 0,
            'dry_run': False
        }
        
        opts = options or {}
        skip_duplicates = bool(opts.get('skip_duplicates'))
        skip_missing = bool(opts.get('skip_missing'))
        dry_run = bool(opts.get('dry_run'))
        results['dry_run'] = dry_run
        
        try:
            # Validate Excel file
            is_valid, message = self.validate_excel_file(excel_file_path)
            if not is_valid:
                results['errors'].append(f"Excel validation failed: {message}")
                return results
            
            # Read Excel file
            df = pd.read_excel(excel_file_path, sheet_name='Study Resources Upload')
            results['total_files'] = len(df)
            
            logger.info(f"Processing {results['total_files']} study resources from Excel (dry_run={dry_run})")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    file_name = str(row['File Name']).strip()
                    file_path = str(row['File Path']).strip()
                    title = str(row['Title']).strip()
                    description = str(row['Description']).strip() if pd.notna(row['Description']) else ''
                    category = str(row['Category']).strip()
                    class_name = str(row['Class']).strip()
                    
                    # Validate file exists
                    if not self.validate_file_exists(file_path):
                        if skip_missing:
                            msg = f"Row {index + 2}: Skipped missing file at {file_path}"
                            results['skipped'].append(msg)
                            results['skipped_missing'] += 1
                            continue
                        else:
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
                    
                    # Duplicate check
                    if self.is_duplicate_resource(title, class_name):
                        if skip_duplicates:
                            msg = f"Row {index + 2}: Skipped duplicate '{title}' in class {class_name}"
                            results['skipped'].append(msg)
                            results['skipped_duplicates'] += 1
                            continue
                        else:
                            # Treat as error
                            error_msg = f"Row {index + 2}: Duplicate resource '{title}' already exists in class {class_name}"
                            results['errors'].append(error_msg)
                            results['failed_uploads'] += 1
                            continue
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Copy file to uploads folder (unless dry run)
                    if not dry_run:
                        new_filename, new_path = self.copy_file_to_uploads(file_path, category, file_name, class_name)
                        if new_filename is None:
                            error_msg = f"Row {index + 2}: Failed to copy file {file_name}"
                            results['errors'].append(error_msg)
                            results['failed_uploads'] += 1
                            continue
                    else:
                        # Simulate destination path
                        category_folder = self.get_category_folder(category)
                        safe_class = ''.join(c for c in class_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_') if class_name else None
                        if safe_class:
                            new_path = os.path.join(self.upload_folder, safe_class, category_folder, file_name)
                        else:
                            new_path = os.path.join(self.upload_folder, category_folder, file_name)
                        new_filename = file_name
                    
                    # Prepare file data for database
                    file_data = {
                        'filename': new_filename,
                        'file_path': new_path,
                        'title': title,
                        'description': description,
                        'category': category,
                        'class': class_name
                    }
                    
                    if not dry_run:
                        # Save to study resources database
                        if self.save_to_study_resources(file_data):
                            success_msg = f"Successfully uploaded: {file_name} to {class_name} class"
                            results['success'].append(success_msg)
                            results['successful_uploads'] += 1
                            logger.info(success_msg)
                        else:
                            error_msg = f"Row {index + 2}: Failed to save {file_name} to database"
                            results['errors'].append(error_msg)
                            results['failed_uploads'] += 1
                    else:
                        success_msg = f"DRY RUN: Would upload {file_name} to {class_name} class"
                        results['success'].append(success_msg)
                
                except Exception as e:
                    error_msg = f"Row {index + 2}: Error processing {row.get('File Name', 'Unknown')}: {str(e)}"
                    results['errors'].append(error_msg)
                    results['failed_uploads'] += 1
                    logger.error(error_msg)
            
            logger.info(
                f"Study resources bulk upload completed: {results['successful_uploads']} successful, {results['failed_uploads']} failed, "
                f"{results['skipped_duplicates']} duplicates skipped, {results['skipped_missing']} missing skipped (dry_run={dry_run})"
            )
            
        except Exception as e:
            error_msg = f"Error processing Excel file: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def create_study_resources_template(self, output_path='study_resources_template.xlsx'):
        """Create Excel template for study resources upload"""
        try:
            # Sample data for template
            template_data = {
                'File Name': [
                    'algebra_basics.pdf',
                    'physics_mechanics.pdf',
                    'chemistry_organic.pdf'
                ],
                'File Path': [
                    '/path/to/algebra_basics.pdf',
                    '/path/to/physics_mechanics.pdf',
                    '/path/to/chemistry_organic.pdf'
                ],
                'Title': [
                    'Algebra Basics - Chapter 1',
                    'Physics Mechanics - Motion',
                    'Organic Chemistry - Hydrocarbons'
                ],
                'Description': [
                    'Introduction to algebraic expressions and equations',
                    'Fundamentals of motion, velocity, and acceleration',
                    'Study of hydrocarbons and their properties'
                ],
                'Category': [
                    'Study Material',
                    'Study Material',
                    'Study Material'
                ],
                'Class': [
                    '10th',
                    '11th',
                    '12th'
                ]
            }
            
            df = pd.DataFrame(template_data)
            df.to_excel(output_path, index=False, sheet_name='Study Resources Upload')
            
            logger.info(f"Study resources template created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating study resources template: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize handler
    handler = StudyResourcesBulkUploadHandler()
    
    # Create template
    handler.create_study_resources_template()
    
    # Example: Process Excel file (uncomment to test)
    # results = handler.process_study_resources_excel('path/to/your/excel/file.xlsx')
    # print(f"Upload Results: {results}") 