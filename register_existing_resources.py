#!/usr/bin/env python3
"""
Script to register existing PDF files in the database
This script will scan the uploads directory and register all PDF files with proper categorization
"""

import os
import sqlite3
from auth_handler import save_resource, get_all_classes

def categorize_file(filename):
    """Categorize files based on their filename"""
    filename_lower = filename.lower()
    
    # Sample papers
    if any(keyword in filename_lower for keyword in ['sample', 'paper']):
        return 'sample_paper'
    
    # Worksheets
    if any(keyword in filename_lower for keyword in ['worksheet', 'worksheet-unlocked']):
        return 'worksheet'
    
    # Previous year questions
    if any(keyword in filename_lower for keyword in ['pyq', 'previous', 'year', 'question']):
        return 'pyq'
    
    # Case-based questions
    if any(keyword in filename_lower for keyword in ['case', 'case-study']):
        return 'case-base'
    
    # Assertion/Reasoning
    if any(keyword in filename_lower for keyword in ['assertion', 'reasoning']):
        return 'assertion-reasoning'
    
    # Formula sheets
    if any(keyword in filename_lower for keyword in ['formula', 'formulae']):
        return 'formula'
    
    # Notes
    if any(keyword in filename_lower for keyword in ['notes', 'chapter', 'ch-']):
        return 'notes'
    
    # Default to notes if no specific category is found
    return 'notes'

def get_title_from_filename(filename):
    """Generate a readable title from filename"""
    # Remove file extension
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    # Handle special cases
    if 'CH-' in name:
        # Format chapter names nicely
        name = name.replace('CH-', 'Chapter ')
        name = name.replace('-', ' ')
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name

def register_existing_resources():
    """Register all existing PDF files in the database"""
    
    # Get all classes
    classes = get_all_classes()
    print(f"Found {len(classes)} classes in database:")
    for class_id, class_name in classes:
        print(f"  {class_id}: {class_name}")
    
    # Define class mappings based on filename patterns
    class_mappings = {
        'class9': 1,  # Assuming class9 has ID 1
        'class10': 2,  # Assuming class10 has ID 2
        'class11': 3,  # Assuming class11 has ID 3
        'class12': 4,  # Assuming class12 has ID 4
        'applied': 3,  # Applied maths maps to class11
        'standard': 2,  # Standard maps to class10
        'basic': 2,     # Basic maps to class10
    }
    
    # Scan uploads directory
    uploads_dir = 'uploads'
    registered_count = 0
    skipped_count = 0
    
    print(f"\nScanning directory: {uploads_dir}")
    
    for root, dirs, files in os.walk(uploads_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, uploads_dir)
                
                # Determine class based on filename and path
                class_id = None
                filename_lower = file.lower()
                
                # Check for class indicators in filename
                for class_keyword, class_id_value in class_mappings.items():
                    if class_keyword in filename_lower:
                        class_id = class_id_value
                        break
                
                # If no class found, try to determine from path
                if class_id is None:
                    path_parts = root.split(os.sep)
                    for part in path_parts:
                        for class_keyword, class_id_value in class_mappings.items():
                            if class_keyword in part.lower():
                                class_id = class_id_value
                                break
                        if class_id:
                            break
                
                # Default to class 9 if no class found
                if class_id is None:
                    class_id = 1
                
                # Categorize the file
                category = categorize_file(file)
                
                # Generate title
                title = get_title_from_filename(file)
                
                # Check if resource already exists
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('SELECT id FROM resources WHERE filename = ?', (file,))
                existing = c.fetchone()
                conn.close()
                
                if existing:
                    print(f"  SKIPPED: {file} (already registered)")
                    skipped_count += 1
                else:
                    try:
                        # Save resource to database
                        save_resource(
                            filename=file,
                            class_id=class_id,
                            filepath=relative_path,
                            title=title,
                            description=f"PDF resource: {title}",
                            category=category
                        )
                        print(f"  REGISTERED: {file} -> Class {class_id}, Category: {category}")
                        registered_count += 1
                    except Exception as e:
                        print(f"  ERROR registering {file}: {e}")
    
    print(f"\nRegistration complete!")
    print(f"  Registered: {registered_count} files")
    print(f"  Skipped: {skipped_count} files (already registered)")
    
    # Show summary by class
    print(f"\nSummary by class:")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.class_id, c.name, COUNT(*) as count 
        FROM resources r 
        JOIN classes c ON r.class_id = c.id 
        GROUP BY r.class_id, c.name
        ORDER BY r.class_id
    ''')
    class_summary = c.fetchall()
    conn.close()
    
    for class_id, class_name, count in class_summary:
        print(f"  Class {class_id} ({class_name}): {count} resources")
    
    # Show summary by category
    print(f"\nSummary by category:")
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT category, COUNT(*) as count 
        FROM resources 
        GROUP BY category 
        ORDER BY count DESC
    ''')
    category_summary = c.fetchall()
    conn.close()
    
    for category, count in category_summary:
        print(f"  {category}: {count} resources")

if __name__ == "__main__":
    print("Registering existing PDF resources in database...")
    register_existing_resources()
    print("\nDone!") 