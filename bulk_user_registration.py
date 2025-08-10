#!/usr/bin/env python3
"""
Bulk User Registration Script
Reads student details from Excel file and registers them in the website database
"""

import pandas as pd
import sqlite3
import re
from auth_handler import init_db, get_all_classes, register_user
import os

def clean_username(name):
    """Convert full name to username format"""
    # Remove extra spaces and convert to lowercase
    name = re.sub(r'\s+', ' ', name.strip()).lower()
    # Replace spaces with underscores
    username = name.replace(' ', '_')
    # Remove special characters except underscores
    username = re.sub(r'[^a-z0-9_]', '', username)
    return username

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

def register_students_bulk(students, class_mapping):
    """Register students in bulk"""
    success_count = 0
    failed_count = 0
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
            
            # Register the user
            if register_user(username, password, class_id):
                success_count += 1
                print(f"✓ Registered: {username} -> Class ID: {class_id}, Status: {status}")
            else:
                failed_count += 1
                failed_students.append(f"{username} (username may already exist)")
                print(f"✗ Failed to register: {username} (username may already exist)")
                
        except Exception as e:
            failed_count += 1
            failed_students.append(f"{username} (error: {str(e)})")
            print(f"✗ Error registering {username}: {e}")
    
    return success_count, failed_count, failed_students

def main():
    """Main function to run bulk registration"""
    print("=== Bulk User Registration Script ===")
    
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
    
    # Confirm before proceeding
    print(f"\nAbout to register {len(students)} students")
    confirm = input("Proceed? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("Registration cancelled.")
        return
    
    # Register students
    success_count, failed_count, failed_students = register_students_bulk(
        students, class_mapping
    )
    
    # Print summary
    print(f"\n=== Registration Summary ===")
    print(f"Successfully registered: {success_count} students")
    print(f"Failed to register: {failed_count} students")
    
    if failed_students:
        print(f"\nFailed students:")
        for student in failed_students:
            print(f"  - {student}")
    
    print(f"\nRegistration complete!")

if __name__ == "__main__":
    main() 