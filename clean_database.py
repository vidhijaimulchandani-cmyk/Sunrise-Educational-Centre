#!/usr/bin/env python3
"""
Database Cleanup Script
Removes all users and reinserts only the 100 users from Excel file
"""

import pandas as pd
import sqlite3
import re
from auth_handler import init_db, get_all_classes
import os
from datetime import datetime

def normalize_class_name(name):
    """Normalize class name for mapping"""
    return re.sub(r'\s+', ' ', str(name).strip().lower())

def get_class_mapping():
    """Get mapping between class names and database class IDs"""
    classes = get_all_classes()
    class_mapping = {}
    
    for class_id, class_name in classes:
        norm = normalize_class_name(class_name)
        class_mapping[norm] = class_id
        
        # Add mappings for the exact classes in Excel file
        if '9' in norm or 'ix' in norm:
            class_mapping['class 9th'] = class_id
        if '10' in norm and 'standard' in norm:
            class_mapping['class 10th standard'] = class_id
        if '11' in norm and 'applied' in norm:
            class_mapping['class 11th applied'] = class_id
        if '12' in norm and 'applied' in norm:
            class_mapping['class 12th applied'] = class_id
    
    return class_mapping

def read_excel_file(file_path):
    """Read Excel file and extract user data"""
    try:
        df = pd.read_excel(file_path)
        df.columns = [str(col).strip().lower() for col in df.columns]
        
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
            
            if username == 'nan' or username == '':
                continue
                
            if status in ['paid', 'yes', 'y', '1', 'true']:
                status = 'paid'
            else:
                status = 'not paid'
            
            users.append({
                'username': username,
                'class': class_name,
                'password': password,
                'status': status
            })
        
        print(f"Found {len(users)} valid users in Excel file")
        return users
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def backup_database():
    """Create a backup of the current database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"users_backup_{timestamp}.db"
    
    import shutil
    shutil.copy2('users.db', backup_file)
    print(f"Database backed up as: {backup_file}")
    return backup_file

def clean_and_rebuild_database(users, class_mapping):
    """Remove all users and rebuild with only Excel data"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Count existing users
    c.execute('SELECT COUNT(*) FROM users')
    existing_count = c.fetchone()[0]
    print(f"Found {existing_count} existing users in database")
    
    # Remove all users except admin users (class_id = 8)
    c.execute('DELETE FROM users WHERE class_id != 8')
    deleted_count = c.fetchone()[0] if c.fetchone() else 0
    print(f"Removed {deleted_count} non-admin users")
    
    # Insert new users from Excel
    inserted_count = 0
    failed_count = 0
    
    for user in users:
        try:
            username = user['username']
            password = user['password']
            class_name = normalize_class_name(user['class'])
            status = user['status']
            
            # Find class_id
            class_id = class_mapping.get(class_name)
            if not class_id:
                for k, v in class_mapping.items():
                    if class_name in k or k in class_name:
                        class_id = v
                        break
            
            if not class_id:
                print(f"✗ Could not map class '{user['class']}' for user {username}")
                failed_count += 1
                continue
            
            # Insert user
            c.execute('''
                INSERT INTO users (username, password, class_id, paid, mobile_no, email_address) 
                VALUES (?, ?, ?, ?, NULL, NULL)
            ''', (username, password, class_id, status))
            inserted_count += 1
            print(f"+ Inserted: {username} (class: {user['class']}, paid: {status})")
                
        except Exception as e:
            print(f"✗ Error inserting {username}: {e}")
            failed_count += 1
    
    conn.commit()
    conn.close()
    
    return inserted_count, failed_count

def main():
    print("=== DATABASE CLEANUP AND REBUILD ===")
    
    # Initialize database
    init_db()
    
    # Create backup
    backup_file = backup_database()
    
    # Get class mapping
    class_mapping = get_class_mapping()
    
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
    print(f"\nAbout to rebuild database with {len(users)} users from Excel")
    print("This will remove all existing non-admin users!")
    confirm = input("Proceed? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    # Clean and rebuild
    inserted_count, failed_count = clean_and_rebuild_database(users, class_mapping)
    
    # Final count
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    final_count = c.fetchone()[0]
    conn.close()
    
    print(f"\n=== CLEANUP COMPLETE ===")
    print(f"Users inserted: {inserted_count}")
    print(f"Failed insertions: {failed_count}")
    print(f"Total users in database: {final_count}")
    print(f"Backup available at: {backup_file}")

if __name__ == "__main__":
    main() 