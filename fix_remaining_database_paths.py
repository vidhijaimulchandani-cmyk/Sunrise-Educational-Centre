#!/usr/bin/env python3
"""
Comprehensive script to fix all remaining hardcoded database paths in app.py
This script will replace all remaining instances of sqlite3.connect('users.db') with sqlite3.connect(DATABASE)
"""

import re

def fix_remaining_database_paths():
    print("🔧 Fixing all remaining hardcoded database paths in app.py...")
    
    # Read the file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current hardcoded paths
    old_count = content.count("sqlite3.connect('users.db')")
    print(f"Found {old_count} hardcoded database paths")
    
    if old_count == 0:
        print("✅ No hardcoded database paths found! All paths are already fixed.")
        return True
    
    # Replace all hardcoded paths with DATABASE variable
    new_content = content.replace("sqlite3.connect('users.db')", "sqlite3.connect(DATABASE)")
    
    # Count remaining hardcoded paths
    remaining = new_content.count("sqlite3.connect('users.db')")
    
    if remaining == 0:
        print(f"✅ Successfully fixed {old_count} hardcoded database paths!")
        
        # Write the fixed content back to the file
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("📝 File updated successfully!")
        return True
    else:
        print(f"❌ Still found {remaining} hardcoded paths after replacement")
        return False

def verify_fixes():
    """Verify that all hardcoded paths have been fixed"""
    print("\n🔍 Verifying fixes...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for any remaining hardcoded paths
    remaining = content.count("sqlite3.connect('users.db')")
    
    if remaining == 0:
        print("✅ Verification successful! All hardcoded database paths have been fixed.")
        
        # Count total DATABASE usage
        database_usage = content.count("sqlite3.connect(DATABASE)")
        print(f"📊 Total database connections using DATABASE variable: {database_usage}")
        
        return True
    else:
        print(f"❌ Verification failed! Found {remaining} remaining hardcoded paths:")
        
        # Find and display the remaining instances
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if "sqlite3.connect('users.db')" in line:
                print(f"   Line {i}: {line.strip()}")
        
        return False

def main():
    print("🚀 Starting comprehensive database path fix...")
    print("=" * 60)
    
    # Fix the paths
    if fix_remaining_database_paths():
        print("\n" + "=" * 60)
        
        # Verify the fixes
        if verify_fixes():
            print("\n🎉 All database path fixes completed successfully!")
            print("\n📋 Summary:")
            print("   ✅ All hardcoded 'users.db' paths replaced with DATABASE variable")
            print("   ✅ Admission system should now work correctly")
            print("   ✅ Database connections are now consistent")
            print("\n🔧 Next steps:")
            print("   1. Test the admission system")
            print("   2. Verify no database connection errors")
            print("   3. Check admin panel functionality")
        else:
            print("\n⚠️  Some fixes may not have been applied correctly")
    else:
        print("\n❌ Failed to fix all database paths")

if __name__ == "__main__":
    main()