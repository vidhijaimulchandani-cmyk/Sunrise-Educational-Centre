#!/usr/bin/env python3
"""
Script to fix all hardcoded database paths in app.py
Replaces 'users.db' with DATABASE variable
"""

import re

def fix_database_paths():
    """Fix all hardcoded database paths in app.py"""
    
    # Read the file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences
    old_count = content.count("sqlite3.connect('users.db')")
    print(f"Found {old_count} hardcoded database paths")
    
    # Replace all occurrences
    new_content = content.replace("sqlite3.connect('users.db')", "sqlite3.connect(DATABASE)")
    
    # Count new occurrences
    new_count = new_content.count("sqlite3.connect(DATABASE)")
    print(f"After replacement: {new_count} DATABASE variable usages")
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Database paths fixed successfully!")
    
    # Also check for any remaining hardcoded paths
    remaining = new_content.count("sqlite3.connect('users.db')")
    if remaining == 0:
        print("✅ All hardcoded paths have been replaced!")
    else:
        print(f"⚠️  {remaining} hardcoded paths remain")

if __name__ == "__main__":
    fix_database_paths()