#!/usr/bin/env python3
"""
Ultimate Bulk User Registration Script
- Reads Excel file and handles all data types
- Removes duplicate entries from database
- Ensures all fields are properly synchronized
- Handles class mapping intelligently
- Provides detailed reporting and rollback capability
"""

import pandas as pd
import sqlite3
import re
from auth_handler import init_db, get_all_classes
import os
from datetime import datetime

def normalize_class_name(name):
    """Normalize class name for mapping (case-insensitive, strip spaces)"""
    return re.sub(r'\s+', ' ', str(name).strip().lower())

def get_class_mapping():
    """Get comprehensive mapping between class names and database class IDs"""
    classes = get_all_classes()
    class_mapping = {}
    
    for class_id, class_name in classes:
        norm = normalize_class_name(class_name)
        class_mapping[norm] = class_id
        
        # Add mappings for the exact classes in Excel file
        if '9' in norm or 'ix' in norm:
            class_mapping['class 9th'] = class_id
            class_mapping['9th'] = class_id
            class_mapping['class ix'] = class_id
            class_mapping['ix'] = class_id
        if '10' in norm and 'standard' in norm:
            class_mapping['class 10th standard'] = class_id
            class_mapping['10th standard'] = class_id
            class_mapping['class 10 standard'] = class_id
        if '11' in norm and 'applied' in norm:
            class_mapping['class 11th applied'] = class_id
            class_mapping['11th applied'] = class_id
            class_mapping['class 11 applied'] = class_id
        if '12' in norm and 'applied' in norm:
            class_mapping['class 12th applied'] = class_id
            class_mapping['12th applied'] = class_id
            class_mapping['class 12 applied'] = class_id
    
    return class_mapping

def read_excel_file(file_path):
    """Read Excel file and extract user data with validation"""
    try:
        df = pd.read_excel(file_path)
        
        # Clean column names
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Find required columns
        username_col = next((c for c in df.columns if 'username' in c), None)
        class_col = next((c for c in df.columns if 'class' in c), None)
        password_col = next((c for c in df.columns if 'password' in c), None)
        status_col = next((c for c in df.columns if 'status' in c), None)
        
        if not all([username_col, class_col, password_col, status_col]):
            raise Exception(f"Missing required columns. Found: {df.columns}")
        
        users = []
        for idx, row in df.iterrows():
            username = str(row[username_col]).strip()
            class_name = str(row[class_col]).strip()
            password = str(row[password_col]).strip()
            status = str(row[status_col]).strip().lower()
            
            # Skip empty rows
            if username == 'nan' or username == '':
                continue
                
            # Normalize status
            if status in ['paid', 'yes', 'y', '1', 'true']:
                status = 'paid'
            else:
                status = 'not paid'
            
            users.append({
                'username': username,
                'class': class_name,
                'password': password,
                'status': status,
                'row_index': idx + 1
            })
        
        print(f"Found {len(users)} valid users in file")
        return users
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def get_all_user_ids():
    """Get all user IDs from database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, username FROM users')
    users = c.fetchall()
    conn.close()
    return {username: user_id for user_id, username in users}

def delete_duplicate_users():
    """Remove duplicate users from database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Find duplicates
    c.execute('''
        SELECT username, COUNT(*) as count, GROUP_CONCAT(id) as ids
        FROM users 
        GROUP BY username 
        HAVING COUNT(*) > 1
    ''')
    duplicates = c.fetchall()
    
    deleted_count = 0
    for username, count, ids in duplicates:
        id_list = [int(x) for x in ids.split(',')]
        # Keep the first ID, delete the rest
        ids_to_delete = id_list[1:]
        for user_id in ids_to_delete:
            c.execute('DELETE FROM users WHERE id = ?', (user_id,))
            deleted_count += 1
            print(f"Deleted duplicate user: {username} (ID: {user_id})")
    
    conn.commit()
    conn.close()
    return deleted_count

def backup_database():
    """Create a backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"users_backup_{timestamp}.db"
    
    import shutil
    shutil.copy2('users.db', backup_file)
    print(f"Database backed up as: {backup_file}")
    return backup_file

def process_users(users, class_mapping):
    """Process all users with comprehensive error handling"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    stats = {
        'inserted': 0,
        'updated': 0,
        'failed': 0,
        'errors': []
    }
    
    # Get existing users
    c.execute('SELECT username FROM users')
    existing_users = {row[0] for row in c.fetchall()}
    
    for user in users:
        try:
            username = user['username']
            password = user['password']
            class_name = normalize_class_name(user['class'])
            status = user['status']
            
            # Find class_id
            class_id = class_mapping.get(class_name)
            if not class_id:
                # Try partial matching
                for k, v in class_mapping.items():
                    if class_name in k or k in class_name:
                        class_id = v
                        break
            
            if not class_id:
                error_msg = f"Could not map class '{user['class']}' for user {username}"
                stats['errors'].append(error_msg)
                stats['failed'] += 1
                print(f"✗ {error_msg}")
                continue
            
            if username in existing_users:
                # Update existing user
                c.execute('''
                    UPDATE users 
                    SET password=?, class_id=?, paid=?, mobile_no=NULL, email_address=NULL 
                    WHERE username=?
                ''', (password, class_id, status, username))
                stats['updated'] += 1
                print(f"✓ Updated: {username} (class: {user['class']}, paid: {status})")
            else:
                # Insert new user
                c.execute('''
                    INSERT INTO users (username, password, class_id, paid, mobile_no, email_address) 
                    VALUES (?, ?, ?, ?, NULL, NULL)
                ''', (username, password, class_id, status))
                stats['inserted'] += 1
                print(f"+ Inserted: {username} (class: {user['class']}, paid: {status})")
                
        except Exception as e:
            error_msg = f"Error processing {username}: {str(e)}"
            stats['errors'].append(error_msg)
            stats['failed'] += 1
            print(f"✗ {error_msg}")
    
    conn.commit()
    conn.close()
    return stats

def generate_report(stats, total_users, deleted_duplicates):
    """Generate comprehensive report"""
    print("\n" + "="*60)
    print("ULTIMATE BULK REGISTRATION REPORT")
    print("="*60)
    print(f"Total users in Excel file: {total_users}")
    print(f"Duplicate users removed: {deleted_duplicates}")
    print(f"New users inserted: {stats['inserted']}")
    print(f"Existing users updated: {stats['updated']}")
    print(f"Failed operations: {stats['failed']}")
    print(f"Success rate: {((stats['inserted'] + stats['updated']) / total_users * 100):.1f}%")
    
    if stats['errors']:
        print(f"\nErrors encountered:")
        for error in stats['errors']:
            print(f"  - {error}")
    
    print("="*60)

def main():
    """Main function with comprehensive error handling"""
    print("=== ULTIMATE BULK USER REGISTRATION ===")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Create backup
    backup_file = backup_database()
    
    # Remove duplicates
    print("\nChecking for duplicate users...")
    deleted_count = delete_duplicate_users()
    if deleted_count > 0:
        print(f"Removed {deleted_count} duplicate users")
    
    # Get class mapping
    class_mapping = get_class_mapping()
    print(f"Available classes: {len(class_mapping)} mappings configured")
    
    # Read Excel file
    excel_file = "/home/yash/Downloads/yash.xlsx"
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    users = read_excel_file(excel_file)
    if not users:
        print("No users to process.")
        return
    
    # Confirm before proceeding
    print(f"\nAbout to process {len(users)} users")
    confirm = input("Proceed? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Process users
    print(f"\nProcessing users...")
    stats = process_users(users, class_mapping)
    
    # Generate report
    generate_report(stats, len(users), deleted_count)
    
    print(f"\nBackup available at: {backup_file}")
    print("Ultimate bulk registration complete!")

if __name__ == "__main__":
    main() 