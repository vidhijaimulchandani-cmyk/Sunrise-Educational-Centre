#!/usr/bin/env python3
"""
Script to fix category names in the database to match expected template categories
"""

import sqlite3

def fix_categories():
    """Fix category names in the database"""
    
    # Category mapping
    category_mapping = {
        'Sample Paper': 'sample_paper',
        'Sample Papers': 'sample_paper',
        'Sample Solutions': 'sample_paper',
        'Previous Year Questions': 'pyq',
        'Previous Year Solutions': 'pyq',
        'others': 'notes',
        'imp': 'notes'
    }
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Get all unique categories
    c.execute('SELECT DISTINCT category FROM resources')
    categories = c.fetchall()
    
    print("Current categories in database:")
    for (category,) in categories:
        print(f"  {category}")
    
    # Update categories
    updated_count = 0
    for (old_category,) in categories:
        if old_category in category_mapping:
            new_category = category_mapping[old_category]
            c.execute('UPDATE resources SET category = ? WHERE category = ?', (new_category, old_category))
            updated_count += c.rowcount
            print(f"  Updated '{old_category}' -> '{new_category}' ({c.rowcount} resources)")
    
    conn.commit()
    conn.close()
    
    print(f"\nUpdated {updated_count} resources")
    
    # Show final summary
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT category, COUNT(*) as count 
        FROM resources 
        GROUP BY category 
        ORDER BY count DESC
    ''')
    category_summary = c.fetchall()
    conn.close()
    
    print(f"\nFinal summary by category:")
    for category, count in category_summary:
        print(f"  {category}: {count} resources")

if __name__ == "__main__":
    print("Fixing category names in database...")
    fix_categories()
    print("\nDone!") 