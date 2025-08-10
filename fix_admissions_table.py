#!/usr/bin/env python3
import sqlite3

def fix_admissions_table():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get current columns
        c.execute("PRAGMA table_info(admissions)")
        existing_columns = [row[1] for row in c.fetchall()]
        print("Existing columns:", existing_columns)
        
        # Add missing columns if they don't exist
        missing_columns = [
            ('user_id', 'INTEGER'),
            ('submit_ip', 'TEXT'),
            ('approved_at', 'TEXT'),
            ('approved_by', 'TEXT'),
            ('disapproved_at', 'TEXT'),
            ('disapproved_by', 'TEXT'),
            ('disapproval_reason', 'TEXT')
        ]
        
        for col_name, col_type in missing_columns:
            if col_name not in existing_columns:
                try:
                    c.execute(f'ALTER TABLE admissions ADD COLUMN {col_name} {col_type}')
                    print(f"Added column: {col_name}")
                except Exception as e:
                    print(f"Error adding {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists")
        
        conn.commit()
        
        # Show final schema
        c.execute("PRAGMA table_info(admissions)")
        final_columns = [row[1] for row in c.fetchall()]
        print("\nFinal columns:", final_columns)
        
        conn.close()
        print("\nAdmissions table fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing table: {e}")

if __name__ == "__main__":
    fix_admissions_table()