#!/usr/bin/env python3
"""
Direct Upload Script
Directly copies files to uploads folder and updates the database
"""

import pandas as pd
import os
import shutil
import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectUpload:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
    
    def get_class_id(self, class_name):
        """Get class ID for database"""
        class_mapping = {
            'class_9': 1,
            'class_10_basic': 3,
            'class_10_standard': 2
        }
        return class_mapping.get(class_name, 2)  # Default to class 10 standard
    
    def copy_file_to_uploads(self, source_path, category):
        """Copy file to appropriate uploads folder"""
        try:
            # Determine destination folder based on category
            category_mapping = {
                'case_based_questions': 'study_materials',
                'previous_year_questions': 'study_materials',
                'sample_papers': 'study_materials',
                'worksheets': 'assignments',
                'formula_sheets': 'notes'
            }
            
            dest_folder = category_mapping.get(category, 'other')
            dest_dir = os.path.join('uploads', dest_folder)
            
            # Create destination directory if it doesn't exist
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            filename = os.path.basename(source_path)
            dest_path = os.path.join(dest_dir, filename)
            
            # Ensure unique filename
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(dest_dir, filename)
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied {source_path} to {dest_path}")
            
            return dest_path
            
        except Exception as e:
            logger.error(f"Error copying file {source_path}: {e}")
            return None
    
    def add_resource_to_database(self, filename, title, description, category, class_id):
        """Add resource to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert into resources table
            cursor.execute('''
                INSERT INTO resources (filename, filepath, title, description, category, class_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, f"uploads/study_materials/{filename}", title, description, category, class_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added resource to database: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding resource to database: {e}")
            return False
    
    def upload_all_resources(self):
        """Upload all resources from the Excel file"""
        try:
            print("🚀 Starting Direct Upload")
            print("=" * 50)
            
            # Read Excel file
            excel_file = 'xlsx/RESOURCE_UPLOADER.xlsx'
            if not os.path.exists(excel_file):
                print(f"❌ Excel file not found: {excel_file}")
                return False
            
            df = pd.read_excel(excel_file)
            print(f"📊 Found {len(df)} resources to upload")
            
            successful_uploads = 0
            failed_uploads = 0
            
            for index, row in df.iterrows():
                try:
                    print(f"\n[{index + 1}/{len(df)}] Processing: {row['Title']}")
                    
                    # Check if source file exists
                    source_path = row['File Path']
                    if not os.path.exists(source_path):
                        print(f"   ❌ Source file not found: {source_path}")
                        failed_uploads += 1
                        continue
                    
                    # Copy file to uploads folder
                    dest_path = self.copy_file_to_uploads(source_path, row['Category'])
                    if not dest_path:
                        print(f"   ❌ Failed to copy file")
                        failed_uploads += 1
                        continue
                    
                    # Get class ID
                    class_id = self.get_class_id(row['Class'])
                    
                    # Add to database
                    filename = os.path.basename(dest_path)
                    success = self.add_resource_to_database(
                        filename=filename,
                        title=row['Title'],
                        description=row['Description'],
                        category=row['Category'],
                        class_id=class_id
                    )
                    
                    if success:
                        print(f"   ✅ Successfully uploaded: {row['Title']}")
                        successful_uploads += 1
                    else:
                        print(f"   ❌ Failed to add to database")
                        failed_uploads += 1
                    
                except Exception as e:
                    print(f"   ❌ Error processing {row['Title']}: {e}")
                    failed_uploads += 1
            
            # Print summary
            print(f"\n{'='*50}")
            print(f"📊 UPLOAD SUMMARY")
            print(f"{'='*50}")
            print(f"✅ Successful uploads: {successful_uploads}")
            print(f"❌ Failed uploads: {failed_uploads}")
            print(f"📊 Total resources: {len(df)}")
            
            return successful_uploads > 0
            
        except Exception as e:
            print(f"❌ Error during upload process: {e}")
            return False

def main():
    """Main function to run the direct upload"""
    uploader = DirectUpload()
    
    print("Sunrise Education Centre - Direct Upload")
    print("=" * 50)
    print("This will directly copy files to uploads folder and update the database")
    print("=" * 50)
    
    # Upload all resources
    success = uploader.upload_all_resources()
    
    if success:
        print(f"\n🎉 Direct upload completed successfully!")
        print(f"📁 All resources have been copied to uploads folder and added to database.")
    else:
        print(f"\n❌ Direct upload failed!")
        print(f"📁 Check the logs above for details.")

if __name__ == "__main__":
    main() 