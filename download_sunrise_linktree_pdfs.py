#!/usr/bin/env python3
"""
Download PDFs from Sunrise Education Centre Linktree and organize for bulk upload
"""

import requests
import os
import json
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime

class SunriseLinktreeDownloader:
    def __init__(self):
        self.base_url = "https://linktr.ee/sunrise_educationcentre"
        self.download_dir = "sunrise_linktree_downloads"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create download directory
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Define the PDF resources from the linktree
        self.pdf_resources = {
            "previous_years": {
                "2024_question_paper": "Question Paper 2024",
                "2024_solution": "Solution 2024", 
                "2023_question_paper": "Question Paper 2023",
                "2023_solution": "Solution 2023",
                "2022_question_paper": "Question Paper 2022", 
                "2022_solution": "Solution 2022"
            },
            "sample_papers": {
                "2024_25_sample_paper": "Sample Paper 2024-25",
                "2024_25_sample_solution": "Sample Solution 2024-25",
                "2023_24_sample_paper": "Sample Paper 2023-24",
                "2023_24_sample_solution": "Sample Solution 2023-24", 
                "2022_23_sample_paper": "Sample Paper 2022 - 23",
                "2022_23_sample_solution": "Sample Solution 2022-23"
            },
            "formula_sheets": {
                "formula_sheet_all_chapters": "FORMULA SHEET (All Chapters)"
            }
        }
    
    def get_linktree_data(self):
        """Fetch the linktree page to extract PDF links"""
        try:
            print("Fetching Linktree data...")
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            # Parse the page to find PDF links
            # This is a simplified approach - in practice you'd need to parse the actual HTML
            # For now, we'll work with the known structure
            
            return response.text
        except Exception as e:
            print(f"Error fetching linktree: {e}")
            return None
    
    def extract_pdf_links(self, html_content):
        """Extract PDF download links from the linktree HTML"""
        # This is a placeholder - you'd need to implement proper HTML parsing
        # For now, we'll create a mapping of expected links
        pdf_links = {
            "2024_question_paper": "https://linktr.ee/sunrise_educationcentre/question-paper-2024",
            "2024_solution": "https://linktr.ee/sunrise_educationcentre/solution-2024",
            "2023_question_paper": "https://linktr.ee/sunrise_educationcentre/question-paper-2023", 
            "2023_solution": "https://linktr.ee/sunrise_educationcentre/solution-2023",
            "2022_question_paper": "https://linktr.ee/sunrise_educationcentre/question-paper-2022",
            "2022_solution": "https://linktr.ee/sunrise_educationcentre/solution-2022",
            "2024_25_sample_paper": "https://linktr.ee/sunrise_educationcentre/sample-paper-2024-25",
            "2024_25_sample_solution": "https://linktr.ee/sunrise_educationcentre/sample-solution-2024-25",
            "2023_24_sample_paper": "https://linktr.ee/sunrise_educationcentre/sample-paper-2023-24",
            "2023_24_sample_solution": "https://linktr.ee/sunrise_educationcentre/sample-solution-2023-24",
            "2022_23_sample_paper": "https://linktr.ee/sunrise_educationcentre/sample-paper-2022-23",
            "2022_23_sample_solution": "https://linktr.ee/sunrise_educationcentre/sample-solution-2022-23",
            "formula_sheet_all_chapters": "https://linktr.ee/sunrise_educationcentre/formula-sheet-all-chapters"
        }
        return pdf_links
    
    def download_pdf(self, url, filename):
        """Download a PDF file"""
        try:
            print(f"Downloading: {filename}")
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")
            return None
    
    def organize_for_bulk_upload(self):
        """Organize downloaded PDFs for bulk upload"""
        bulk_upload_structure = {
            "class_12_applied_maths": {
                "previous_year_questions": [],
                "sample_papers": [],
                "formula_sheets": []
            }
        }
        
        # Scan downloaded files and organize them
        for filename in os.listdir(self.download_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.download_dir, filename)
                
                # Categorize based on filename
                if 'question' in filename.lower() or 'solution' in filename.lower():
                    bulk_upload_structure["class_12_applied_maths"]["previous_year_questions"].append({
                        "filename": filename,
                        "filepath": filepath,
                        "title": filename.replace('.pdf', '').replace('_', ' ').title(),
                        "category": "Previous Year Questions",
                        "class": "Class 12 Applied Maths"
                    })
                elif 'sample' in filename.lower():
                    bulk_upload_structure["class_12_applied_maths"]["sample_papers"].append({
                        "filename": filename,
                        "filepath": filepath,
                        "title": filename.replace('.pdf', '').replace('_', ' ').title(),
                        "category": "Sample Papers",
                        "class": "Class 12 Applied Maths"
                    })
                elif 'formula' in filename.lower():
                    bulk_upload_structure["class_12_applied_maths"]["formula_sheets"].append({
                        "filename": filename,
                        "filepath": filepath,
                        "title": filename.replace('.pdf', '').replace('_', ' ').title(),
                        "category": "Formula Sheets",
                        "class": "Class 12 Applied Maths"
                    })
        
        return bulk_upload_structure
    
    def create_bulk_upload_json(self, organized_files):
        """Create JSON file for bulk upload"""
        bulk_upload_data = []
        
        for class_name, categories in organized_files.items():
            for category_name, files in categories.items():
                for file_info in files:
                    bulk_upload_data.append({
                        "title": file_info["title"],
                        "description": f"{file_info['category']} - {file_info['class']}",
                        "category": file_info["category"],
                        "class": file_info["class"],
                        "file_path": file_info["filepath"],
                        "tags": [file_info["category"], file_info["class"], "Sunrise Education"],
                        "source": "Sunrise Education Centre Linktree"
                    })
        
        # Save to JSON file
        json_filepath = os.path.join(self.download_dir, "bulk_upload_data.json")
        with open(json_filepath, 'w') as f:
            json.dump(bulk_upload_data, f, indent=2)
        
        print(f"✅ Bulk upload JSON created: {json_filepath}")
        return json_filepath
    
    def run_download(self):
        """Main download process"""
        print("🚀 Starting Sunrise Education Centre PDF Download")
        print("=" * 50)
        
        # Get linktree data
        html_content = self.get_linktree_data()
        if not html_content:
            print("❌ Failed to fetch linktree data")
            return
        
        # Extract PDF links
        pdf_links = self.extract_pdf_links(html_content)
        
        # Download PDFs
        downloaded_files = []
        for resource_id, url in pdf_links.items():
            filename = f"{resource_id}.pdf"
            filepath = self.download_pdf(url, filename)
            if filepath:
                downloaded_files.append(filepath)
            time.sleep(1)  # Be respectful with requests
        
        print(f"\n📊 Download Summary:")
        print(f"Total files downloaded: {len(downloaded_files)}")
        
        # Organize for bulk upload
        organized_files = self.organize_for_bulk_upload()
        
        # Create bulk upload JSON
        json_filepath = self.create_bulk_upload_json(organized_files)
        
        print(f"\n✅ Download complete! Files ready for bulk upload:")
        print(f"📁 Download directory: {self.download_dir}")
        print(f"📄 Bulk upload JSON: {json_filepath}")
        
        return {
            "download_dir": self.download_dir,
            "json_filepath": json_filepath,
            "organized_files": organized_files
        }

def main():
    downloader = SunriseLinktreeDownloader()
    result = downloader.run_download()
    
    if result:
        print("\n🎯 Next Steps:")
        print("1. Review downloaded PDFs in the 'sunrise_linktree_downloads' folder")
        print("2. Use the bulk_upload_data.json for automated upload")
        print("3. Upload to your website's bulk upload system")

if __name__ == "__main__":
    main() 