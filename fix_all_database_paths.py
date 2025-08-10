#!/usr/bin/env python3
"""
Comprehensive script to fix all remaining hardcoded database paths in app.py
"""

import re

def fix_all_database_paths():
    print("🔧 Fixing all remaining hardcoded database paths in app.py...")
    
    # Read the file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current hardcoded paths
    old_count = content.count("sqlite3.connect('users.db')")
    print(f"Found {old_count} hardcoded database paths")
    
    # Replace all hardcoded paths with DATABASE variable
    new_content = content.replace("sqlite3.connect('users.db')", "sqlite3.connect(DATABASE)")
    
    # Count remaining hardcoded paths
    remaining = new_content.count("sqlite3.connect('users.db')")
    
    if remaining == 0:
        print("✅ All hardcoded database paths have been fixed!")
        
        # Write the updated content back
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"📝 Updated app.py - replaced {old_count} hardcoded paths")
        return True
    else:
        print(f"❌ Still found {remaining} hardcoded paths")
        return False

if __name__ == "__main__":
    try:
        success = fix_all_database_paths()
        if success:
            print("\n🎉 Database path fixing completed successfully!")
            print("💡 The admission system should now work properly with the correct database path.")
        else:
            print("\n⚠️  Some database paths could not be fixed.")
    except Exception as e:
        print(f"❌ Error: {e}")