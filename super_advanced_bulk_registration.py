#!/usr/bin/env python3
"""
Super Advanced Bulk User Registration Script
Reads student details from Excel file and ensures all user fields (password, class, paid status) are exactly as in the file.
Updates existing users or inserts new ones. Robust to column order and extra spaces.
"""

import pandas as pd
import sqlite3
import re
from auth_handler import init_db, get_all_classes
import os

def normalize_class_name(name):
    """Normalize class name for mapping (case-insensitive, strip spaces)"""
    return re.sub(r'\s+', ' ', str(name).strip().lower())

def get_class_mapping():
    """Get mapping between Excel class names and database class IDs"""
    classes = get_all_classes()
    class_mapping = {}
    
    # Create mapping for different class name variations
    for class_id, class_name in classes:
        class_name_lower = class_name.lower()
        class_mapping[class_name_lower] = class_id
        
        # Add variations
        if 'class 9' in class_name_lower or 'ix' in class_name_lower:
            class_mapping['class ix'] = class_id
            class_mapping['ix'] = class_id
            class_mapping['IX'] = class_id
            class_mapping['class 9th'] = class_id
            class_mapping['9th'] = class_id
            class_mapping['9th class'] = class_id
            class_mapping['9'] = class_id
        elif 'class 10' in class_name_lower:
            if 'basic' in class_name_lower:
                class_mapping['class x basic'] = class_id
                class_mapping['x basic'] = class_id
            else:
                class_mapping['class x'] = class_id
                class_mapping['x'] = class_id
                class_mapping['X'] = class_id
                class_mapping['class 10th'] = class_id
                class_mapping['10th'] = class_id
                class_mapping['10th class'] = class_id
                class_mapping['10'] = class_id
        elif '11' in class_name_lower and 'applied' in class_name_lower:
            class_mapping['xi applied'] = class_id
            class_mapping['XI Applied'] = class_id
            class_mapping['11 applied'] = class_id
            class_mapping['class 11th applied'] = class_id
            class_mapping['11th applied'] = class_id
            class_mapping['11th class applied'] = class_id
            class_mapping['11'] = class_id  # Default to applied for backward compatibility
        elif '11' in class_name_lower and 'core' in class_name_lower:
            class_mapping['xi core'] = class_id
            class_mapping['XI Core'] = class_id
            class_mapping['11 core'] = class_id
            class_mapping['class 11th core'] = class_id
            class_mapping['11th core'] = class_id
            class_mapping['11th class core'] = class_id
        elif '12' in class_name_lower and 'applied' in class_name_lower:
            class_mapping['xii applied'] = class_id
            class_mapping['XII Applied'] = class_id
            class_mapping['12 applied'] = class_id
            class_mapping['class 12th applied'] = class_id
            class_mapping['12th applied'] = class_id
            class_mapping['12th class applied'] = class_id
            class_mapping['12'] = class_id  # Default to applied for backward compatibility
        elif '12' in class_name_lower and 'core' in class_name_lower:
            class_mapping['xii core'] = class_id
            class_mapping['XII Core'] = class_id
            class_mapping['12 core'] = class_id
            class_mapping['class 12th core'] = class_id
            class_mapping['12th core'] = class_id
            class_mapping['12th class core'] = class_id
    
    return class_mapping

def read_excel_file(file_path):
    """Read the Excel file using headers and return a list of user dicts"""
    try:
        df = pd.read_excel(file_path)
        # Normalize column names
        df.columns = [str(col).strip().lower() for col in df.columns]
        # Try to find the right columns
        username_col = next((c for c in df.columns if 'username' in c), None)
        class_col = next((c for c in df.columns if 'class' in c), None)
        password_col = next((c for c in df.columns if 'password' in c), None)
        status_col = next((c for c in df.columns if 'status' in c or 'paid' in c), None)
        if not all([username_col, class_col, password_col, status_col]):
            raise Exception(f"Missing required columns. Found: {df.columns}")
        users = []
        for _, row in df.iterrows():
            username = str(row[username_col]).strip()
            class_name = str(row[class_col]).strip()
            password = str(row[password_col]).strip()
            status = str(row[status_col]).strip().lower()
            # Normalize status to 'paid' or 'not paid'
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
        print(f"Found {len(users)} users in file. Sample: {users[:3]}")
        return users
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def get_user_id(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def upsert_user(user, class_mapping):
    username = user['username']
    password = user['password']
    class_name = normalize_class_name(user['class'])
    status = user['status']
    class_id = class_mapping.get(class_name)
    if not class_id:
        # Try partial match
        for k, v in class_mapping.items():
            if class_name in k or k in class_name:
                class_id = v
                break
    if not class_id:
        print(f"✗ Could not map class '{user['class']}' for user {username}")
        return False, 'class mapping failed'
    user_id = get_user_id(username)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        if user_id:
            # Update existing user
            c.execute('UPDATE users SET password=?, class_id=?, paid=? WHERE id=?',
                      (password, class_id, status, user_id))
            print(f"✓ Updated: {username} (class: {user['class']}, paid: {status})")
        else:
            # Insert new user
            c.execute('INSERT INTO users (username, password, class_id, paid) VALUES (?, ?, ?, ?)',
                      (username, password, class_id, status))
            print(f"+ Inserted: {username} (class: {user['class']}, paid: {status})")
        conn.commit()
        return True, None
    except Exception as e:
        print(f"✗ Error for {username}: {e}")
        return False, str(e)
    finally:
        conn.close()

def main():
    print("=== Super Advanced Bulk User Registration ===")
    init_db()
    class_mapping = get_class_mapping()
    excel_file = "/home/yash/Downloads/Sunrise-Educational-Centre/STUDENT DETAILS(3).xlsx"
    if not os.path.exists(excel_file):
        print(f"Excel file not found: {excel_file}")
        return
    users = read_excel_file(excel_file)
    if not users:
        print("No users to process.")
        return
    success, failed = 0, 0
    for user in users:
        ok, err = upsert_user(user, class_mapping)
        if ok:
            success += 1
        else:
            failed += 1
    print(f"\nSummary: {success} succeeded, {failed} failed.")

if __name__ == "__main__":
    main() 