#!/usr/bin/env python3
"""
Final upload script to upload Sunrise Education Centre PDFs to website bulk upload system
"""

import os
import json
import shutil
import requests
from datetime import datetime

class WebsiteUploader:
    def __init__(self):
        self.bulk_upload_dir = "bulk_upload"
        self.uploads_dir = "uploads/study_materials"
        self.manifest_file = "bulk_upload/bulk_upload_manifest.json"
        
    def load_manifest(self):
        """Load the bulk upload manifest"""
        try:
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Manifest file not found: {self.manifest_file}")
            return None
    
    def copy_to_uploads(self):
        """Copy organized files to uploads directory"""
        print("📁 Copying files to uploads directory...")
        
        # Create uploads directory if it doesn't exist
        os.makedirs(self.uploads_dir, exist_ok=True)
        
        # Copy all PDFs from bulk_upload to uploads/study_materials
        copied_files = []
        
        for root, dirs, files in os.walk(self.bulk_upload_dir):
            for file in files:
                if file.endswith('.pdf'):
                    source_path = os.path.join(root, file)
                    
                    # Create destination path in uploads
                    relative_path = os.path.relpath(root, self.bulk_upload_dir)
                    dest_dir = os.path.join(self.uploads_dir, relative_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    dest_path = os.path.join(dest_dir, file)
                    shutil.copy2(source_path, dest_path)
                    
                    copied_files.append({
                        'source': source_path,
                        'destination': dest_path,
                        'filename': file
                    })
                    
                    print(f"✅ Copied: {file} → uploads/study_materials/{relative_path}/")
        
        return copied_files
    
    def create_upload_summary(self, copied_files):
        """Create a summary of uploaded files"""
        summary = {
            "upload_timestamp": datetime.now().isoformat(),
            "source": "Sunrise Education Centre Linktree",
            "total_files": len(copied_files),
            "categories": {},
            "files": []
        }
        
        for file_info in copied_files:
            filename = file_info['filename']
            
            # Determine category
            if 'question' in filename.lower():
                category = "Previous Year Questions"
            elif 'sample' in filename.lower():
                category = "Sample Papers"
            else:
                category = "Study Materials"
            
            # Count by category
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            
            # Add file info
            summary["files"].append({
                "filename": filename,
                "category": category,
                "upload_path": file_info['destination'],
                "size": os.path.getsize(file_info['destination'])
            })
        
        # Save summary
        summary_file = "sunrise_upload_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Upload summary created: {summary_file}")
        return summary
    
    def create_database_entries(self, summary):
        """Create database entries for the uploaded files"""
        print("🗄️  Creating database entries...")
        
        # This would integrate with your existing database system
        # For now, we'll create a JSON file that can be imported
        
        db_entries = []
        
        for file_info in summary["files"]:
            db_entry = {
                "title": file_info["filename"].replace('.pdf', '').replace('_', ' ').title(),
                "description": f"{file_info['category']} - Class 12 Applied Mathematics",
                "category": file_info["category"],
                "class": "Class 12 Applied Mathematics",
                "file_path": file_info["upload_path"],
                "file_size": file_info["size"],
                "upload_date": summary["upload_timestamp"],
                "source": "Sunrise Education Centre",
                "tags": [file_info["category"], "Class 12", "Applied Mathematics"]
            }
            
            db_entries.append(db_entry)
        
        # Save database entries
        db_file = "sunrise_database_entries.json"
        with open(db_file, 'w') as f:
            json.dump(db_entries, f, indent=2)
        
        print(f"✅ Database entries created: {db_file}")
        return db_entries
    
    def run_final_upload(self):
        """Main upload process"""
        print("🚀 Final Upload to Website System")
        print("=" * 50)
        
        # Load manifest
        manifest = self.load_manifest()
        if not manifest:
            return None
        
        print(f"📄 Loaded manifest with {manifest['upload_metadata']['total_files']} files")
        
        # Copy files to uploads directory
        copied_files = self.copy_to_uploads()
        
        if not copied_files:
            print("❌ No files were copied")
            return None
        
        # Create upload summary
        summary = self.create_upload_summary(copied_files)
        
        # Create database entries
        db_entries = self.create_database_entries(summary)
        
        # Final summary
        print(f"\n🎉 Upload Complete!")
        print(f"📁 Files uploaded to: {self.uploads_dir}/")
        print(f"📊 Total files: {summary['total_files']}")
        
        print(f"\n📋 Files by Category:")
        for category, count in summary["categories"].items():
            print(f"  - {category}: {count} files")
        
        print(f"\n📄 Generated Files:")
        print(f"  - sunrise_upload_summary.json")
        print(f"  - sunrise_database_entries.json")
        
        return {
            "summary": summary,
            "db_entries": db_entries,
            "uploaded_files": copied_files
        }

def main():
    uploader = WebsiteUploader()
    result = uploader.run_final_upload()
    
    if result:
        print(f"\n✅ Successfully uploaded {result['summary']['total_files']} files from Sunrise Education Centre!")
        print(f"📁 All files are now available in your uploads directory")
        print(f"🗄️  Database entries are ready for import")
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Files are ready in uploads/study_materials/")
        print(f"2. Import database entries to your system")
        print(f"3. Files will be available on your website")
    else:
        print("❌ Upload failed")

if __name__ == "__main__":
    main() 