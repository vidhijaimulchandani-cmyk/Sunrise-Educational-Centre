#!/usr/bin/env python3
"""
Register Sunrise Education Centre PDFs in the database
"""

import sqlite3
import os
import json
from datetime import datetime

class SunrisePDFRegistrar:
    def __init__(self):
        self.db_file = 'users.db'
        self.uploads_dir = 'uploads/study_materials/class_12_applied_maths'
        self.class_id = 6  # Class 12 Applied Mathematics
        
    def get_class_id(self):
        """Get the class ID for Class 12 Applied Mathematics"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT id FROM classes WHERE name = ?', ('class 12 applied',))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    
    def register_pdf_in_database(self, filename, filepath, title, description, category):
        """Register a PDF file in the resources database"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            # Check if resource already exists
            c.execute('SELECT id FROM resources WHERE filename = ?', (filename,))
            existing = c.fetchone()
            
            if existing:
                print(f"⚠️  Resource already exists: {filename}")
                return False
            
            # Insert new resource (without uploaded_at column)
            c.execute('''
                INSERT INTO resources (filename, class_id, filepath, title, description, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, self.class_id, filepath, title, description, category))
            
            conn.commit()
            print(f"✅ Registered: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error registering {filename}: {e}")
            return False
        finally:
            conn.close()
    
    def process_sunrise_pdfs(self):
        """Process all Sunrise PDFs and register them in the database"""
        print("🚀 Registering Sunrise Education Centre PDFs in Database")
        print("=" * 60)
        
        # Get class ID
        self.class_id = self.get_class_id()
        if not self.class_id:
            print("❌ Class 12 Applied Mathematics not found in database")
            return
        
        print(f"📚 Class ID: {self.class_id} (Class 12 Applied Mathematics)")
        
        registered_count = 0
        
        # Process previous year questions
        prev_year_dir = os.path.join(self.uploads_dir, 'previous_year_questions')
        if os.path.exists(prev_year_dir):
            print(f"\n📁 Processing Previous Year Questions...")
            for filename in os.listdir(prev_year_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(prev_year_dir, filename)
                    title = filename.replace('.pdf', '').replace('_', ' ').title()
                    
                    # Determine if it's a question paper or solution
                    if 'question' in filename.lower():
                        category = 'Previous Year Questions'
                        description = f"Previous Year Question Paper - {title}"
                    elif 'solution' in filename.lower():
                        category = 'Previous Year Solutions'
                        description = f"Previous Year Solution - {title}"
                    else:
                        category = 'Previous Year Questions'
                        description = f"Previous Year Material - {title}"
                    
                    if self.register_pdf_in_database(filename, filepath, title, description, category):
                        registered_count += 1
        
        # Process sample papers
        sample_dir = os.path.join(self.uploads_dir, 'sample_papers')
        if os.path.exists(sample_dir):
            print(f"\n📁 Processing Sample Papers...")
            for filename in os.listdir(sample_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(sample_dir, filename)
                    title = filename.replace('.pdf', '').replace('_', ' ').title()
                    
                    # Determine if it's a sample paper or solution
                    if 'sample_paper' in filename.lower():
                        category = 'Sample Papers'
                        description = f"Sample Paper - {title}"
                    elif 'sample_solution' in filename.lower():
                        category = 'Sample Solutions'
                        description = f"Sample Solution - {title}"
                    else:
                        category = 'Sample Papers'
                        description = f"Sample Material - {title}"
                    
                    if self.register_pdf_in_database(filename, filepath, title, description, category):
                        registered_count += 1
        
        print(f"\n📊 Registration Summary:")
        print(f"✅ Successfully registered: {registered_count} files")
        
        # Verify registration
        self.verify_registration()
        
        return registered_count
    
    def verify_registration(self):
        """Verify that files are properly registered"""
        print(f"\n🔍 Verifying Registration...")
        
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Get all resources for Class 12 Applied
        c.execute('''
            SELECT filename, title, category, filepath 
            FROM resources 
            WHERE class_id = ? 
            ORDER BY category, title
        ''', (self.class_id,))
        
        resources = c.fetchall()
        conn.close()
        
        print(f"📋 Registered Resources for Class 12 Applied Mathematics:")
        current_category = None
        
        for resource in resources:
            filename, title, category, filepath = resource
            
            if category != current_category:
                print(f"\n📂 {category}:")
                current_category = category
            
            print(f"  - {title} ({filename})")
        
        print(f"\n📊 Total registered resources: {len(resources)}")
    
    def create_categories_if_needed(self):
        """Create categories if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        categories = [
            ('Previous Year Questions', 'Previous year question papers'),
            ('Previous Year Solutions', 'Previous year solutions'),
            ('Sample Papers', 'Sample question papers'),
            ('Sample Solutions', 'Sample paper solutions')
        ]
        
        for name, description in categories:
            try:
                c.execute('''
                    INSERT INTO categories (name, description, target_class, paid_status)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, str(self.class_id), 'unpaid'))
                print(f"✅ Created category: {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  Category already exists: {name}")
        
        conn.commit()
        conn.close()

def main():
    registrar = SunrisePDFRegistrar()
    
    # Create categories if needed
    registrar.create_categories_if_needed()
    
    # Register PDFs
    count = registrar.process_sunrise_pdfs()
    
    if count > 0:
        print(f"\n🎉 Successfully registered {count} Sunrise Education Centre PDFs!")
        print(f"📚 Files will now appear in Class 12 Applied Mathematics study resources")
        print(f"🌐 Students can access these files through the study resources page")
    else:
        print("❌ No files were registered")

if __name__ == "__main__":
    main() 