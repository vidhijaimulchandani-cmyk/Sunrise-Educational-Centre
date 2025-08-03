#!/usr/bin/env python3
"""
Upload Sunrise Education Centre PDFs to bulk upload system
"""

import os
import json
import shutil
import requests
from datetime import datetime

class SunrisePDFUploader:
    def __init__(self):
        self.sunrise_pdfs_dir = "sunrise_pdfs"
        self.bulk_upload_dir = "bulk_upload"
        self.upload_report_file = "sunrise_upload_report.json"
        
        # Create bulk upload directory structure
        self.setup_bulk_upload_structure()
    
    def setup_bulk_upload_structure(self):
        """Setup the bulk upload directory structure"""
        # Create main bulk upload directory
        os.makedirs(self.bulk_upload_dir, exist_ok=True)
        
        # Create subdirectories for different resource types
        subdirs = [
            "class_12_applied_maths/previous_year_questions",
            "class_12_applied_maths/sample_papers",
            "class_12_applied_maths/formula_sheets"
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(self.bulk_upload_dir, subdir), exist_ok=True)
    
    def categorize_and_copy_files(self):
        """Categorize PDFs and copy them to appropriate bulk upload directories"""
        
        upload_data = []
        
        # Get list of downloaded PDFs
        pdf_files = [f for f in os.listdir(self.sunrise_pdfs_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            source_path = os.path.join(self.sunrise_pdfs_dir, pdf_file)
            
            # Determine category and destination
            category, subcategory, dest_path = self.categorize_file(pdf_file)
            
            # Copy file to bulk upload directory
            dest_full_path = os.path.join(self.bulk_upload_dir, dest_path)
            shutil.copy2(source_path, dest_full_path)
            
            # Create upload data entry
            upload_entry = {
                "original_filename": pdf_file,
                "bulk_upload_path": dest_path,
                "category": category,
                "subcategory": subcategory,
                "class": "Class 12 Applied Mathematics",
                "title": self.generate_title(pdf_file),
                "description": self.generate_description(pdf_file, category, subcategory),
                "tags": self.generate_tags(pdf_file, category),
                "source": "Sunrise Education Centre Linktree",
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": os.path.getsize(source_path)
            }
            
            upload_data.append(upload_entry)
            
            print(f"✅ Copied: {pdf_file} → {dest_path}")
        
        return upload_data
    
    def categorize_file(self, filename):
        """Categorize file based on filename"""
        filename_lower = filename.lower()
        
        if 'question' in filename_lower:
            category = "Previous Year Questions"
            subcategory = "Question Papers"
            dest_path = "class_12_applied_maths/previous_year_questions"
        elif 'solution' in filename_lower and 'sample' in filename_lower:
            category = "Sample Papers"
            subcategory = "Sample Solutions"
            dest_path = "class_12_applied_maths/sample_papers"
        elif 'solution' in filename_lower:
            category = "Previous Year Questions"
            subcategory = "Solutions"
            dest_path = "class_12_applied_maths/previous_year_questions"
        elif 'sample' in filename_lower:
            category = "Sample Papers"
            subcategory = "Sample Papers"
            dest_path = "class_12_applied_maths/sample_papers"
        else:
            category = "Study Materials"
            subcategory = "General"
            dest_path = "class_12_applied_maths/formula_sheets"
        
        return category, subcategory, dest_path
    
    def generate_title(self, filename):
        """Generate a proper title from filename"""
        # Remove .pdf extension and replace underscores with spaces
        title = filename.replace('.pdf', '').replace('_', ' ')
        
        # Capitalize properly
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title
    
    def generate_description(self, filename, category, subcategory):
        """Generate description for the file"""
        year = self.extract_year(filename)
        year_text = f" ({year})" if year else ""
        
        return f"{category} - {subcategory}{year_text} for Class 12 Applied Mathematics from Sunrise Education Centre"
    
    def generate_tags(self, filename, category):
        """Generate tags for the file"""
        tags = [category, "Class 12", "Applied Mathematics", "Sunrise Education"]
        
        # Add year tag if found
        year = self.extract_year(filename)
        if year:
            tags.append(year)
        
        # Add specific tags based on content
        filename_lower = filename.lower()
        if 'question' in filename_lower:
            tags.append("Question Papers")
        elif 'solution' in filename_lower:
            tags.append("Solutions")
        elif 'sample' in filename_lower:
            tags.append("Sample Papers")
        
        return tags
    
    def extract_year(self, filename):
        """Extract year from filename"""
        import re
        year_match = re.search(r'20\d{2}', filename)
        return year_match.group() if year_match else None
    
    def create_bulk_upload_json(self, upload_data):
        """Create JSON file for bulk upload system"""
        
        bulk_upload_json = {
            "upload_metadata": {
                "source": "Sunrise Education Centre Linktree",
                "upload_date": datetime.now().isoformat(),
                "total_files": len(upload_data),
                "categories": list(set(item['category'] for item in upload_data))
            },
            "files": upload_data
        }
        
        # Save to JSON file
        json_filepath = os.path.join(self.bulk_upload_dir, "bulk_upload_manifest.json")
        with open(json_filepath, 'w') as f:
            json.dump(bulk_upload_json, f, indent=2)
        
        print(f"✅ Bulk upload manifest created: {json_filepath}")
        return json_filepath
    
    def create_excel_template(self, upload_data):
        """Create Excel template for bulk upload"""
        try:
            import pandas as pd
            
            # Create DataFrame for Excel
            excel_data = []
            for item in upload_data:
                excel_data.append({
                    "Title": item['title'],
                    "Description": item['description'],
                    "Category": item['category'],
                    "Subcategory": item['subcategory'],
                    "Class": item['class'],
                    "Tags": ", ".join(item['tags']),
                    "File Path": item['bulk_upload_path'],
                    "Source": item['source']
                })
            
            df = pd.DataFrame(excel_data)
            excel_filepath = os.path.join(self.bulk_upload_dir, "sunrise_bulk_upload_template.xlsx")
            df.to_excel(excel_filepath, index=False)
            
            print(f"✅ Excel template created: {excel_filepath}")
            return excel_filepath
            
        except ImportError:
            print("⚠️  pandas not available, skipping Excel template creation")
            return None
    
    def run_upload_preparation(self):
        """Main upload preparation process"""
        print("🚀 Sunrise Education Centre PDF Upload Preparation")
        print("=" * 60)
        
        # Check if PDFs exist
        if not os.path.exists(self.sunrise_pdfs_dir):
            print(f"❌ PDF directory not found: {self.sunrise_pdfs_dir}")
            print("Please run download_sunrise_pdfs.py first")
            return None
        
        # Categorize and copy files
        print("📁 Organizing files for bulk upload...")
        upload_data = self.categorize_and_copy_files()
        
        if not upload_data:
            print("❌ No files to upload")
            return None
        
        # Create bulk upload JSON
        json_filepath = self.create_bulk_upload_json(upload_data)
        
        # Create Excel template
        excel_filepath = self.create_excel_template(upload_data)
        
        # Generate summary
        print(f"\n📊 Upload Preparation Summary:")
        print(f"📁 Files organized in: {self.bulk_upload_dir}/")
        print(f"📄 Bulk upload manifest: {json_filepath}")
        if excel_filepath:
            print(f"📊 Excel template: {excel_filepath}")
        
        # Category summary
        categories = {}
        for item in upload_data:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📋 Files by Category:")
        for category, count in categories.items():
            print(f"  - {category}: {count} files")
        
        return {
            "upload_data": upload_data,
            "json_filepath": json_filepath,
            "excel_filepath": excel_filepath,
            "bulk_upload_dir": self.bulk_upload_dir
        }

def main():
    uploader = SunrisePDFUploader()
    result = uploader.run_upload_preparation()
    
    if result:
        print(f"\n🎯 Ready for Bulk Upload!")
        print(f"📁 All files are organized in: {result['bulk_upload_dir']}/")
        print(f"📄 Use the manifest file for automated upload")
        print(f"📊 Or use the Excel template for manual review")
        
        print(f"\n📝 Next Steps:")
        print(f"1. Review files in {result['bulk_upload_dir']}/")
        print(f"2. Use the bulk upload system to upload these files")
        print(f"3. Files are categorized and ready for your website")
    else:
        print("❌ Upload preparation failed")

if __name__ == "__main__":
    main() 