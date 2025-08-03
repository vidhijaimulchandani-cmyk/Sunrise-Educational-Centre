#!/usr/bin/env python3
"""
Organize Sunrise Education Centre Resources for Bulk Upload
Downloads and organizes all Google Drive content into structured folders
"""

import requests
import os
import re
import json
import shutil
from datetime import datetime
import logging
from urllib.parse import urlparse
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SunriseResourceOrganizer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Define the folder structure
        self.folder_structure = {
            'class_9': {
                'case_based_questions': [],
                'previous_year_questions': [],
                'sample_papers': [],
                'worksheets': [],
                'formula_sheets': []
            },
            'class_10_basic': {
                'case_based_questions': [],
                'previous_year_questions': [],
                'sample_papers': [],
                'worksheets': [],
                'formula_sheets': []
            },
            'class_10_standard': {
                'case_based_questions': [],
                'previous_year_questions': [],
                'sample_papers': [],
                'worksheets': [],
                'formula_sheets': []
            }
        }
        
        # Define resource categories and their keywords
        self.resource_categories = {
            'case_based_questions': ['case study', 'case based', 'case study (all chapters)'],
            'previous_year_questions': ['ch 1', 'ch 2', 'ch 3', 'ch 4', 'ch 5', 'ch 6', 'ch 7', 'ch 8', 'ch 9', 'ch 10', 'ch 11', 'ch 12', 'ch 13', 'ch 14', 'real number', 'polynomials', 'linear equations', 'quadratic equation', 'arithmetic progression', 'triangles', 'coordinate geometry', 'trigonometry', 'applications of trigonometry', 'circles', 'areas related to circles', 'surface areas', 'volumes', 'statistics', 'probability'],
            'sample_papers': ['basic', 'standard', 'sample paper', 'solution'],
            'worksheets': ['worksheet'],
            'formula_sheets': ['formula sheet', 'formula']
        }
    
    def categorize_resource(self, title):
        """Categorize a resource based on its title"""
        title_lower = title.lower()
        
        for category, keywords in self.resource_categories.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category
        
        # Default categorization
        if 'worksheet' in title_lower:
            return 'worksheets'
        elif any(chapter in title_lower for chapter in ['ch ', 'chapter']):
            return 'previous_year_questions'
        elif 'case' in title_lower:
            return 'case_based_questions'
        elif 'formula' in title_lower:
            return 'formula_sheets'
        else:
            return 'sample_papers'
    
    def determine_class(self, title):
        """Determine which class the resource belongs to"""
        title_lower = title.lower()
        
        # Class 10 resources (most common)
        if any(keyword in title_lower for keyword in ['real number', 'polynomials', 'linear equations', 'quadratic', 'arithmetic progression', 'triangles', 'coordinate geometry', 'trigonometry', 'circles', 'surface areas', 'statistics', 'probability']):
            if 'basic' in title_lower:
                return 'class_10_basic'
            elif 'standard' in title_lower:
                return 'class_10_standard'
            else:
                return 'class_10_standard'  # Default to standard
        
        # Class 9 resources (if any)
        elif any(keyword in title_lower for keyword in ['class 9', 'ix', '9th']):
            return 'class_9'
        
        # Default to class 10 standard
        return 'class_10_standard'
    
    def create_folder_structure(self, base_path='bulk_upload_resources'):
        """Create the folder structure for organizing resources"""
        try:
            # Create base directory
            os.makedirs(base_path, exist_ok=True)
            
            # Create class folders
            for class_name in self.folder_structure.keys():
                class_path = os.path.join(base_path, class_name)
                os.makedirs(class_path, exist_ok=True)
                
                # Create category folders within each class
                for category in self.folder_structure[class_name].keys():
                    category_path = os.path.join(class_path, category)
                    os.makedirs(category_path, exist_ok=True)
                    logger.info(f"Created folder: {category_path}")
            
            logger.info(f"Folder structure created successfully in: {base_path}")
            return base_path
            
        except Exception as e:
            logger.error(f"Error creating folder structure: {e}")
            return None
    
    def download_and_organize_resources(self, base_path='bulk_upload_resources'):
        """Download and organize all resources from Sunrise Linktree"""
        
        # Create folder structure
        base_path = self.create_folder_structure(base_path)
        if not base_path:
            return False
        
        # Define all resources from the Linktree
        resources = [
            # Case Based Questions
            {
                "title": "Case Study (All Chapters)",
                "url": "https://drive.google.com/uc?export=download&id=1mTuOHG3ah_AJ6kfdLciyumFMTOj50b78",
                "file_id": "1mTuOHG3ah_AJ6kfdLciyumFMTOj50b78"
            },
            
            # Sample Papers
            {
                "title": "Basic (2024-2025) with Solution",
                "url": "https://drive.google.com/uc?export=download&id=1AKPa-z8EfdV6zrV7iLBrlJ_PYlZh1nMX",
                "file_id": "1AKPa-z8EfdV6zrV7iLBrlJ_PYlZh1nMX"
            },
            {
                "title": "Standard (2024-2025) with solution",
                "url": "https://drive.google.com/uc?export=download&id=13vras5PqieLebe_nLadoHUr6dlGksPK7",
                "file_id": "13vras5PqieLebe_nLadoHUr6dlGksPK7"
            },
            
            # Chapter-wise PYQs (Previous Year Questions)
            {
                "title": "CH 1 - Real Number",
                "url": "https://drive.google.com/uc?export=download&id=1KEjd1PtHmhECYmtIVAIMzdCmLCfRS0jT",
                "file_id": "1KEjd1PtHmhECYmtIVAIMzdCmLCfRS0jT"
            },
            {
                "title": "CH 2 - Polynomials",
                "url": "https://drive.google.com/uc?export=download&id=1a_AQAjO0fnGB_tASwoy7QbvVqv8ypo2M",
                "file_id": "1a_AQAjO0fnGB_tASwoy7QbvVqv8ypo2M"
            },
            {
                "title": "CH 3 - Pair of Linear Equations in Two Variables",
                "url": "https://drive.google.com/uc?export=download&id=13rZw4nDD7LV9hXhYi5J-2uCvsrRWU7ZZ",
                "file_id": "13rZw4nDD7LV9hXhYi5J-2uCvsrRWU7ZZ"
            },
            {
                "title": "CH 4 - Quadratic Equation",
                "url": "https://drive.google.com/uc?export=download&id=1vhZG00hT90c2-0FEWU2C57EpQlb4pLSa",
                "file_id": "1vhZG00hT90c2-0FEWU2C57EpQlb4pLSa"
            },
            {
                "title": "CH 5 - Arithmetic Progression",
                "url": "https://drive.google.com/uc?export=download&id=11V7i3_2sJ7RZNstTXbjlFrX0sanN3MZ9",
                "file_id": "11V7i3_2sJ7RZNstTXbjlFrX0sanN3MZ9"
            },
            {
                "title": "CH 6 - Triangles",
                "url": "https://drive.google.com/uc?export=download&id=1dP3TFuMNxz9I25O1s2RDbeG0GKQ_Y_Nf",
                "file_id": "1dP3TFuMNxz9I25O1s2RDbeG0GKQ_Y_Nf"
            },
            {
                "title": "CH 7 - Coordinate Geometry",
                "url": "https://drive.google.com/uc?export=download&id=1e-dNaC2Skk9-dta6SNLvof-kpZC3Aswd",
                "file_id": "1e-dNaC2Skk9-dta6SNLvof-kpZC3Aswd"
            },
            {
                "title": "CH 8 - Trigonometry",
                "url": "https://drive.google.com/uc?export=download&id=1nsH_Go7nxXasSX0HWoYSad9aUCl-vDfO",
                "file_id": "1nsH_Go7nxXasSX0HWoYSad9aUCl-vDfO"
            },
            {
                "title": "CH 9 - Applications of Trigonometry",
                "url": "https://drive.google.com/uc?export=download&id=1oTnQH30HPoBKEHOicZ0c7MXrDP4GduGg",
                "file_id": "1oTnQH30HPoBKEHOicZ0c7MXrDP4GduGg"
            },
            {
                "title": "CH 10 - Circles",
                "url": "https://drive.google.com/uc?export=download&id=1CC5TaIgJTR3ZuB6BHUDmWIXYDmZ2_VAo",
                "file_id": "1CC5TaIgJTR3ZuB6BHUDmWIXYDmZ2_VAo"
            },
            {
                "title": "CH 11 - Areas Related to Circles",
                "url": "https://drive.google.com/uc?export=download&id=1NGuipqjtxnpArlQZtddD88C1rC2dyFzB",
                "file_id": "1NGuipqjtxnpArlQZtddD88C1rC2dyFzB"
            },
            {
                "title": "CH 12 - Surface Areas & Volumes",
                "url": "https://drive.google.com/uc?export=download&id=1oS693cOTkYhY8PUn5w-NDBf9mL_mCa86",
                "file_id": "1oS693cOTkYhY8PUn5w-NDBf9mL_mCa86"
            },
            {
                "title": "CH 13 - Statistics",
                "url": "https://drive.google.com/uc?export=download&id=1WblRmjMTLvxwsF-y3_9KECE8Xh51qIpu",
                "file_id": "1WblRmjMTLvxwsF-y3_9KECE8Xh51qIpu"
            },
            {
                "title": "CH 14 - Probability",
                "url": "https://drive.google.com/uc?export=download&id=1jRVyAa184Jz-FxxuDDguZMJPkxCZymUf",
                "file_id": "1jRVyAa184Jz-FxxuDDguZMJPkxCZymUf"
            },
            
            # Worksheets
            {
                "title": "Polynomials - Worksheet (UNLOCKED)",
                "url": "https://drive.google.com/uc?export=download&id=1ZgUSqxEoH3KnobfrlOKtsQGzCHfoC_cM",
                "file_id": "1ZgUSqxEoH3KnobfrlOKtsQGzCHfoC_cM"
            },
            {
                "title": "Triangles - Worksheet (UNLOCKED)",
                "url": "https://drive.google.com/uc?export=download&id=11SIma-Eu2ljYlWAKSFpS04tCyqAjij7z",
                "file_id": "11SIma-Eu2ljYlWAKSFpS04tCyqAjij7z"
            },
            {
                "title": "Probability - Worksheet (UNLOCKED)",
                "url": "https://drive.google.com/uc?export=download&id=1iluMHbcoJX73DZe-oe7-a500yv7OHiAB",
                "file_id": "1iluMHbcoJX73DZe-oe7-a500yv7OHiAB"
            }
        ]
        
        successful_downloads = 0
        failed_downloads = 0
        download_results = []
        
        print(f"\n{'='*70}")
        print(f"DOWNLOADING AND ORGANIZING SUNRISE EDUCATION RESOURCES")
        print(f"{'='*70}")
        
        for i, resource in enumerate(resources, 1):
            try:
                print(f"\n[{i}/{len(resources)}] Processing: {resource['title']}")
                
                # Determine class and category
                class_name = self.determine_class(resource['title'])
                category = self.categorize_resource(resource['title'])
                
                print(f"   Class: {class_name}")
                print(f"   Category: {category}")
                
                # Create safe filename
                safe_title = re.sub(r'[^\w\s-]', '', resource['title']).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)
                filename = f"{safe_title}_{resource['file_id']}.pdf"
                
                # Determine destination path
                dest_path = os.path.join(base_path, class_name, category, filename)
                
                # Download the file
                print(f"   Downloading...")
                response = self.session.get(resource['url'], stream=True)
                response.raise_for_status()
                
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(dest_path)
                print(f"   ✅ Downloaded: {filename} ({file_size} bytes)")
                print(f"   📁 Saved to: {dest_path}")
                
                successful_downloads += 1
                
                # Store result for Excel generation
                download_results.append({
                    'filename': filename,
                    'title': resource['title'],
                    'class': class_name,
                    'category': category,
                    'filepath': dest_path,
                    'size': file_size,
                    'status': 'success'
                })
                
            except Exception as e:
                print(f"   ❌ Failed to download {resource['title']}: {e}")
                failed_downloads += 1
                download_results.append({
                    'filename': None,
                    'title': resource['title'],
                    'class': class_name,
                    'category': category,
                    'filepath': None,
                    'size': 0,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Save results
        self.save_download_results(download_results, base_path)
        
        # Populate Excel file
        self.populate_excel_file(download_results)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"DOWNLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"❌ Failed downloads: {failed_downloads}")
        print(f"📁 Resources organized in: {base_path}")
        
        # Show folder structure
        self.print_folder_structure(base_path)
        
        return download_results
    
    def save_download_results(self, results, base_path):
        """Save download results to JSON file"""
        try:
            data = {
                'download_date': datetime.now().isoformat(),
                'total_resources': len(results),
                'successful_downloads': len([r for r in results if r['status'] == 'success']),
                'failed_downloads': len([r for r in results if r['status'] == 'failed']),
                'results': results
            }
            
            results_file = os.path.join(base_path, 'download_results.json')
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Download results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Error saving download results: {e}")
    
    def print_folder_structure(self, base_path):
        """Print the organized folder structure"""
        print(f"\n{'='*70}")
        print(f"ORGANIZED FOLDER STRUCTURE")
        print(f"{'='*70}")
        
        for root, dirs, files in os.walk(base_path):
            level = root.replace(base_path, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root)
            
            if level == 0:
                print(f"{indent}📁 {folder_name}/")
            elif level == 1:
                print(f"{indent}📂 {folder_name}/")
            elif level == 2:
                print(f"{indent}📁 {folder_name}/")
                # Show files in this folder
                for file in files:
                    if file.endswith('.pdf'):
                        file_size = os.path.getsize(os.path.join(root, file))
                        print(f"{indent}  📄 {file} ({file_size} bytes)")
        
        print(f"\n💡 Ready for bulk upload Excel file!")
        print(f"   Use the file paths above to fill your Excel template.")
    
    def generate_excel_template_data(self, base_path):
        """Generate data for Excel template based on downloaded files"""
        excel_data = []
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.pdf'):
                    filepath = os.path.join(root, file)
                    relative_path = os.path.relpath(filepath, base_path)
                    
                    # Parse class and category from path
                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) >= 3:
                        class_name = path_parts[0]
                        category = path_parts[1]
                        
                        # Generate title from filename
                        title = file.replace('.pdf', '').replace('_', ' ').title()
                        
                        excel_data.append({
                            'filename': file,
                            'title': title,
                            'description': f"{category.replace('_', ' ').title()} for {class_name.replace('_', ' ').title()}",
                            'category': category,
                            'class_id': self.get_class_id(class_name),
                            'filepath': filepath
                        })
        
        return excel_data
    
    def get_class_id(self, class_name):
        """Get class ID for database"""
        class_mapping = {
            'class_9': 1,
            'class_10_basic': 2,
            'class_10_standard': 3
        }
        return class_mapping.get(class_name, 3)  # Default to class 10 standard
    
    def populate_excel_file(self, download_results):
        """Populate the Excel file with all downloaded resources"""
        try:
            excel_file = 'xlsx/RESOURCE_UPLOADER.xlsx'
            
            # Create DataFrame from download results
            excel_data = []
            
            for result in download_results:
                if result['status'] == 'success':
                    # Parse class and category from filepath
                    filepath = result['filepath']
                    filename = result['filename']
                    title = result['title']
                    
                    # Extract class and category from path
                    path_parts = filepath.split(os.sep)
                    class_name = path_parts[1]  # e.g., class_10_standard
                    category = path_parts[2]    # e.g., previous_year_questions
                    
                    # Generate description
                    description = f"{category.replace('_', ' ').title()} for {class_name.replace('_', ' ').title()}"
                    
                    # Clean title for display
                    display_title = title.replace('_', ' ').title()
                    
                    excel_data.append({
                        'File Name': filename,
                        'File Path': filepath,
                        'Title': display_title,
                        'Description': description,
                        'Category': category,
                        'Class': class_name
                    })
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Save to Excel file
            df.to_excel(excel_file, index=False)
            
            print(f"\n{'='*70}")
            print(f"EXCEL FILE POPULATED")
            print(f"{'='*70}")
            print(f"📊 Excel file updated: {excel_file}")
            print(f"📝 Total resources added: {len(excel_data)}")
            print(f"📋 Columns: {list(df.columns)}")
            
            # Show sample data
            print(f"\n📋 Sample entries:")
            for i, row in df.head(5).iterrows():
                print(f"  {i+1}. {row['Title']} ({row['Category']} - {row['Class']})")
            
            if len(df) > 5:
                print(f"  ... and {len(df) - 5} more resources")
            
            logger.info(f"Excel file populated with {len(excel_data)} resources")
            return True
            
        except Exception as e:
            logger.error(f"Error populating Excel file: {e}")
            print(f"❌ Error populating Excel file: {e}")
            return False

def main():
    """Main function to organize Sunrise resources"""
    organizer = SunriseResourceOrganizer()
    
    print("Sunrise Education Centre - Resource Organizer")
    print("=" * 60)
    print("This will download and organize all resources into folders")
    print("for easy bulk upload to your educational platform.")
    print("=" * 60)
    
    # Download and organize resources
    results = organizer.download_and_organize_resources('bulk_upload_resources')
    
    if results:
        print(f"\n🎉 Organization complete!")
        print(f"📁 Check the 'bulk_upload_resources' folder for organized files.")
        print(f"📊 Use the download_results.json file for Excel template data.")
    else:
        print(f"\n❌ Organization failed. Check logs for details.")

if __name__ == "__main__":
    main() 