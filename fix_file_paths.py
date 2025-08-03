#!/usr/bin/env python3
"""
Script to fix file paths in the database to ensure they point to correct locations
"""

import sqlite3
import os

def fix_file_paths():
    """Fix file paths in the database"""
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get all resources
    c.execute('SELECT id, filename, filepath FROM resources')
    resources = c.fetchall()
    
    print("Checking and fixing file paths...")
    updated_count = 0
    
    for resource_id, filename, current_filepath in resources:
        # Check if file exists at current path
        full_path = os.path.join('uploads', current_filepath)
        
        if not os.path.exists(full_path):
            # Try to find the file in subdirectories
            found_path = None
            for root, dirs, files in os.walk('uploads'):
                if filename in files:
                    found_path = os.path.relpath(os.path.join(root, filename), 'uploads')
                    break
            
            if found_path and found_path != current_filepath:
                c.execute('UPDATE resources SET filepath = ? WHERE id = ?', (found_path, resource_id))
                print(f"  Fixed path for {filename}: {current_filepath} -> {found_path}")
                updated_count += 1
            else:
                print(f"  WARNING: Could not find file {filename}")
        else:
            print(f"  OK: {filename} exists at {current_filepath}")
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdated {updated_count} file paths")

if __name__ == "__main__":
    print("Fixing file paths in database...")
    fix_file_paths()
    print("\nDone!") 