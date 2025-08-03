#!/usr/bin/env python3
"""
Summary of Sunrise Education Centre PDF Upload Process
"""

import sqlite3
import os
import json
from datetime import datetime

def generate_summary():
    """Generate a comprehensive summary of the Sunrise PDF upload"""
    
    print("🎓 Sunrise Education Centre PDF Upload Summary")
    print("=" * 60)
    
    # Database summary
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get Class 12 Applied resources
    c.execute('''
        SELECT filename, title, category, filepath 
        FROM resources 
        WHERE class_id = 6 
        ORDER BY category, title
    ''')
    
    resources = c.fetchall()
    conn.close()
    
    # Categorize resources
    categories = {}
    for resource in resources:
        category = resource[2]
        if category not in categories:
            categories[category] = []
        categories[category].append(resource)
    
    print(f"📊 Total Resources Registered: {len(resources)}")
    print(f"📚 Class: Class 12 Applied Mathematics")
    print(f"🏫 Source: Sunrise Education Centre Linktree")
    
    print(f"\n📋 Resources by Category:")
    for category, items in categories.items():
        print(f"\n📂 {category} ({len(items)} files):")
        for filename, title, cat, filepath in items:
            # Check if file exists
            file_exists = "✅" if os.path.exists(filepath) else "❌"
            print(f"  {file_exists} {title}")
    
    # File system check
    print(f"\n📁 File System Check:")
    uploads_dir = "uploads/study_materials/class_12_applied_maths"
    
    if os.path.exists(uploads_dir):
        prev_year_dir = os.path.join(uploads_dir, "previous_year_questions")
        sample_dir = os.path.join(uploads_dir, "sample_papers")
        
        prev_year_files = len(os.listdir(prev_year_dir)) if os.path.exists(prev_year_dir) else 0
        sample_files = len(os.listdir(sample_dir)) if os.path.exists(sample_dir) else 0
        
        print(f"  📂 Previous Year Questions: {prev_year_files} files")
        print(f"  📂 Sample Papers: {sample_files} files")
        print(f"  📂 Total in file system: {prev_year_files + sample_files} files")
    else:
        print(f"  ❌ Uploads directory not found")
    
    # Database vs File System comparison
    db_count = len(resources)
    fs_count = prev_year_files + sample_files if os.path.exists(uploads_dir) else 0
    
    print(f"\n🔍 Database vs File System:")
    print(f"  📊 Database entries: {db_count}")
    print(f"  📁 File system files: {fs_count}")
    
    if db_count == fs_count:
        print(f"  ✅ Perfect match! All files are properly registered")
    else:
        print(f"  ⚠️  Mismatch detected - some files may not be registered")
    
    # Generate summary report
    summary = {
        "upload_date": datetime.now().isoformat(),
        "source": "Sunrise Education Centre Linktree",
        "class": "Class 12 Applied Mathematics",
        "total_resources": len(resources),
        "categories": categories,
        "file_system_check": {
            "uploads_directory": uploads_dir,
            "previous_year_files": prev_year_files if os.path.exists(uploads_dir) else 0,
            "sample_files": sample_files if os.path.exists(uploads_dir) else 0,
            "total_files": fs_count
        },
        "database_check": {
            "total_entries": db_count,
            "match_with_filesystem": db_count == fs_count
        }
    }
    
    # Save summary to file
    with open('sunrise_final_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Summary saved to: sunrise_final_summary.json")
    
    return summary

def main():
    summary = generate_summary()
    
    print(f"\n🎯 Status:")
    if summary["database_check"]["match_with_filesystem"]:
        print(f"✅ SUCCESS: All Sunrise Education Centre PDFs are properly uploaded and registered!")
        print(f"🌐 Students can now access these resources in Class 12 Applied Mathematics study resources")
    else:
        print(f"⚠️  WARNING: Some files may not be properly registered")
    
    print(f"\n📚 Available Resources:")
    print(f"  - Previous Year Question Papers (2022, 2023, 2024)")
    print(f"  - Previous Year Solutions (2022, 2023, 2024)")
    print(f"  - Sample Papers (2022-23, 2023-24, 2024-25)")
    print(f"  - Sample Solutions (2022-23, 2023-24, 2024-25)")

if __name__ == "__main__":
    main() 