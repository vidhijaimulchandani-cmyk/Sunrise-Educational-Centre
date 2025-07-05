import pandas as pd
import os
from datetime import datetime

def create_study_resources_template():
    """Create Excel template for bulk PDF uploads to study resources"""
    
    # Sample data for the template
    template_data = {
        'File Name': [
            'algebra_basics.pdf',
            'physics_mechanics.pdf',
            'chemistry_organic.pdf',
            'english_grammar.pdf',
            'history_india.pdf'
        ],
        'File Path': [
            '/path/to/algebra_basics.pdf',
            '/path/to/physics_mechanics.pdf',
            '/path/to/chemistry_organic.pdf',
            '/path/to/english_grammar.pdf',
            '/path/to/history_india.pdf'
        ],
        'Title': [
            'Algebra Basics - Chapter 1',
            'Physics Mechanics - Motion',
            'Organic Chemistry - Hydrocarbons',
            'English Grammar - Parts of Speech',
            'Indian History - Ancient Period'
        ],
        'Description': [
            'Introduction to algebraic expressions and equations',
            'Fundamentals of motion, velocity, and acceleration',
            'Study of hydrocarbons and their properties',
            'Understanding parts of speech and sentence structure',
            'Ancient Indian history and civilization'
        ],
        'Category': [
            'Study Material',
            'Study Material',
            'Study Material',
            'Study Material',
            'Study Material'
        ],
        'Class': [
            '10th',
            '11th',
            '12th',
            '9th',
            '10th'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(template_data)
    
    # Create templates directory if it doesn't exist
    templates_dir = 'bulk_upload/templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Save template
    template_path = os.path.join(templates_dir, 'study_resources_template.xlsx')
    df.to_excel(template_path, index=False, sheet_name='Study Resources Upload')
    
    # Add instructions sheet
    with pd.ExcelWriter(template_path, engine='openpyxl', mode='a') as writer:
        # Instructions sheet
        instructions_data = {
            'Column': [
                'File Name',
                'File Path',
                'Title',
                'Description',
                'Category',
                'Class'
            ],
            'Description': [
                'Name of the PDF file (e.g., algebra_basics.pdf)',
                'Full path to the PDF file on your system',
                'Display title for the resource',
                'Brief description of the content',
                'Category (Study Material, Assignment, Notes, etc.)',
                'Target class (9th, 10th, 11th, 12th)'
            ],
            'Required': [
                'Yes',
                'Yes',
                'Yes',
                'No',
                'Yes',
                'Yes'
            ],
            'Example': [
                'algebra_basics.pdf',
                '/home/user/documents/algebra_basics.pdf',
                'Algebra Basics - Chapter 1',
                'Introduction to algebraic expressions',
                'Study Material',
                '10th'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Available classes sheet
        classes_data = {
            'Available Classes': [
                '9th',
                '10th',
                '11th',
                '12th'
            ]
        }
        classes_df = pd.DataFrame(classes_data)
        classes_df.to_excel(writer, sheet_name='Available Classes', index=False)
        
        # Available categories sheet
        categories_data = {
            'Available Categories': [
                'Study Material',
                'Assignment',
                'Notes',
                'Practice Test',
                'Reference Book',
                'Video',
                'Other'
            ]
        }
        categories_df = pd.DataFrame(categories_data)
        categories_df.to_excel(writer, sheet_name='Available Categories', index=False)
    
    print(f"✅ Study Resources Template created: {template_path}")
    return template_path

if __name__ == "__main__":
    create_study_resources_template() 