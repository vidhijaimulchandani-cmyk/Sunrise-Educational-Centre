#!/usr/bin/env python3
"""
Advanced Bulk User Registration Script
Reads student details from Excel file and registers them in the website database
with support for different class assignments and paid status updates
"""

import pandas as pd
import sqlite3
import re
from auth_handler import init_db, get_all_classes, register_user, update_user
import os

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
            class_mapping['class 9th'] = class_id
            class_mapping['9th'] = class_id
        elif 'class 10' in class_name_lower:
            if 'basic' in class_name_lower:
                class_mapping['class x basic'] = class_id
                class_mapping['x basic'] = class_id
            else:
                class_mapping['class x'] = class_id
                class_mapping['x'] = class_id
                class_mapping['class 10th'] = class_id
                class_mapping['10th'] = class_id
        elif '11' in class_name_lower and 'applied' in class_name_lower:
            class_mapping['xi applied'] = class_id
            class_mapping['11 applied'] = class_id
            class_mapping['class 11th applied'] = class_id
        elif '12' in class_name_lower and 'applied' in class_name_lower:
            class_mapping['xii applied'] = class_id
            class_mapping['12 applied'] = class_id
            class_mapping['class 12th applied'] = class_id
    
    return class_mapping

def read_excel_file(file_path):
    """Read the Excel file and extract student data"""
    try:
        # Read Excel file without header
        df = pd.read_excel(file_path, header=None)
        
        # Skip the header row (first row)
        data_df = df.iloc[1:].copy()
        
        # Extract columns
        usernames = data_df.iloc[:, 0].dropna().tolist()
        classes = data_df.iloc[:, 1].dropna().tolist()
        passwords = data_df.iloc[:, 2].dropna().tolist()
        statuses = data_df.iloc[:, 3].dropna().tolist()
        
        # Create list of student data
        students = []
        for i in range(len(usernames)):
            if i < len(classes) and i < len(passwords) and i < len(statuses):
                students.append({
                    'username': usernames[i],
                    'class': classes[i],
                    'password': passwords[i],
                    'status': statuses[i]
                })
        
        print(f"Found {len(students)} students")
        print(f"Sample data: {students[:3]}")
        
        return students
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def check_user_exists(username):
    """Check if a user already exists in the database"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_user_status(username, class_id, paid_status):
    """Update existing user's class and paid status"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE users SET class_id=?, paid=? WHERE username=?', 
                  (class_id, paid_status, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user {username}: {e}")
        return False
    finally:
        conn.close()

def register_students_bulk(students, class_mapping, update_existing=True):
    """Register students in bulk with option to update existing users"""
    success_count = 0
    failed_count = 0
    updated_count = 0
    failed_students = []
    
    print(f"\nStarting bulk registration for {len(students)} students...")
    
    for i, student in enumerate(students, 1):
        try:
            username = student['username']
            class_name = student['class']
            password = student['password']
            status = student['status']
            
            # Find class_id from mapping
            class_id = None
            class_name_lower = class_name.lower()
            
            # Try exact match first
            if class_name_lower in class_mapping:
                class_id = class_mapping[class_name_lower]
            else:
                # Try partial matches
                for key, value in class_mapping.items():
                    if key in class_name_lower or class_name_lower in key:
                        class_id = value
                        break
            
            if class_id is None:
                print(f"✗ Could not find class mapping for: {class_name}")
                failed_count += 1
                failed_students.append(f"{username} (class: {class_name})")
                continue
            
            # Check if user already exists
            if check_user_exists(username):
                if update_existing:
                    # Update existing user
                    if update_user_status(username, class_id, status):
                        updated_count += 1
                        print(f"✓ Updated: {username} -> Class ID: {class_id}, Status: {status}")
                    else:
                        failed_count += 1
                        failed_students.append(f"{username} (update failed)")
                else:
                    print(f"⚠ Skipped existing user: {username}")
                    continue
            else:
                # Register new user
                if register_user(username, password, class_id):
                    success_count += 1
                    print(f"✓ Registered: {username} -> Class ID: {class_id}, Status: {status}")
                else:
                    failed_count += 1
                    failed_students.append(f"{username} (registration failed)")
                
        except Exception as e:
            failed_count += 1
            failed_students.append(f"{username} (error: {str(e)})")
            print(f"✗ Error processing {username}: {e}")
    
    return success_count, failed_count, updated_count, failed_students

def generate_report(students, class_mapping):
    """Generate a report of what will be processed"""
    class_counts = {}
    status_counts = {}
    
    for student in students:
        class_name = student['class']
        status = student['status']
        
        # Count by class
        if class_name not in class_counts:
            class_counts[class_name] = 0
        class_counts[class_name] += 1
        
        # Count by status
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    print("\n=== Processing Report ===")
    print(f"Total students: {len(students)}")
    print("\nBy Class:")
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count} students")
    
    print("\nBy Status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count} students")

def main():
    """Main function to run bulk registration"""
    print("=== Advanced Bulk User Registration Script ===")
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Get class mapping
    class_mapping = get_class_mapping()
    print(f"Available classes: {dict(class_mapping)}")
    
    # Read Excel file
    excel_file = "/home/yash/Downloads/Sunrise-Educational-Centre/STUDENT DETAILS(3).xlsx"
    if not os.path.exists(excel_file):
        print(f"Error: Excel file not found at {excel_file}")
        return
    
    students = read_excel_file(excel_file)
    
    if not students:
        print("No students found in the Excel file")
        return
    
    # Generate report
    generate_report(students, class_mapping)
    
    # Ask about updating existing users
    update_existing = input("\nUpdate existing users? (y/N): ").lower().strip() == 'y'
    
    # Confirm before proceeding
    action = "register/update" if update_existing else "register"
    print(f"\nAbout to {action} {len(students)} students")
    confirm = input("Proceed? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("Registration cancelled.")
        return
    
    # Register students
    success_count, failed_count, updated_count, failed_students = register_students_bulk(
        students, class_mapping, update_existing
    )
    
    # Print summary
    print(f"\n=== Registration Summary ===")
    print(f"Successfully registered: {success_count} new students")
    print(f"Updated existing users: {updated_count} students")
    print(f"Failed to process: {failed_count} students")
    
    if failed_students:
        print(f"\nFailed students:")
        for student in failed_students:
            print(f"  - {student}")
    
    print(f"\nRegistration complete!")

if __name__ == "__main__":
    main() 