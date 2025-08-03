#!/usr/bin/env python3
"""
Download PDFs from Sunrise Education Centre Linktree
Generated from extracted links
"""

import requests
import os
import time
import json
import re
from urllib.parse import urlparse

def download_pdfs():
    """Download PDFs from the extracted links"""
    
    # Extracted links from Linktree
    pdf_links = [
        {
            "text": "Question Paper 2024",
            "url": "https://drive.google.com/file/d/1gSUy9T2nV4xYVfJEg6rmz7vUNnkRPMWe/view?usp=sharing",
            "type": "pdf_link"
        },
        {
            "text": "Solution 2024",
            "url": "https://drive.google.com/uc?export=download&id=1K0GbzTTdS3p_7kyZRdzEfmTf1kdYCsKe",
            "type": "direct_pdf"
        },
        {
            "text": "Question Paper 2023",
            "url": "https://drive.google.com/uc?export=download&id=1E1mLxJKLCxqBx_R8q3qjc1bQ9aiyG3Xt",
            "type": "direct_pdf"
        },
        {
            "text": "Solution 2023",
            "url": "https://drive.google.com/uc?export=download&id=10GWQGbhBzjJUfCA4OPU3zucfp9Tq2jQX",
            "type": "direct_pdf"
        },
        {
            "text": "Question Paper 2022",
            "url": "https://drive.google.com/uc?export=download&id=1iVXIYRNjiQwF3z3a9TiQqgVXmyykxtwH",
            "type": "direct_pdf"
        },
        {
            "text": "Solution 2022",
            "url": "https://drive.google.com/uc?export=download&id=1TueVlrd4yDbiii041-jb6D9KOacXTnfo",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Paper 2024-25",
            "url": "https://drive.google.com/uc?export=download&id=1iQWnAbtA5fPCX-BlxHah8QNqUw6CVnCS",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Solution 2024-25",
            "url": "https://drive.google.com/uc?export=download&id=1ausc_MOKNT3x2dJa-XkUPDwcQTYR-Ay9",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Paper 2023-24",
            "url": "https://drive.google.com/uc?export=download&id=1Z-hjkOH8TJYj6EZlv_i6Jak47WUjcYAt",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Solution 2023-24",
            "url": "https://drive.google.com/uc?export=download&id=1GmvRW5uEYzxIvgbGrrUXgTshDTTsKUra",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Paper 2022-23",
            "url": "https://drive.google.com/uc?export=download&id=1FrPxFiXhrRWxFwJXJZw6OBrYMFDEBZRX",
            "type": "direct_pdf"
        },
        {
            "text": "Sample Solution 2022-23",
            "url": "https://drive.google.com/uc?export=download&id=1dKJXdv-hMwHRs5rc6bEPB7V7WYy5Kucn",
            "type": "direct_pdf"
        }
    ]
    
    download_dir = "sunrise_pdfs"
    os.makedirs(download_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    downloaded_files = []
    
    for i, link in enumerate(pdf_links):
        try:
            print(f"Downloading {i+1}/{len(pdf_links)}: {link['text']}")
            
            # Clean filename
            filename = re.sub(r'[^a-zA-Z0-9\s]', '', link['text'])
            filename = filename.replace(' ', '_') + '.pdf'
            
            # Handle Google Drive links
            if 'drive.google.com' in link['url']:
                if '/file/d/' in link['url']:
                    # Convert view link to download link
                    file_id = link['url'].split('/file/d/')[1].split('/')[0]
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                else:
                    download_url = link['url']
            else:
                download_url = link['url']
            
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            downloaded_files.append({
                'original_text': link['text'],
                'filename': filename,
                'filepath': filepath,
                'url': link['url'],
                'size': os.path.getsize(filepath)
            })
            
            print(f"✅ Downloaded: {filename} ({os.path.getsize(filepath)} bytes)")
            time.sleep(2)  # Be respectful with requests
            
        except Exception as e:
            print(f"❌ Error downloading {link['text']}: {e}")
    
    # Save download report
    with open('sunrise_download_report.json', 'w') as f:
        json.dump(downloaded_files, f, indent=2)
    
    print(f"\n📊 Download Summary:")
    print(f"Successfully downloaded: {len(downloaded_files)} files")
    print(f"Files saved in: {download_dir}")
    print(f"Report saved as: sunrise_download_report.json")
    
    return downloaded_files

def create_bulk_upload_structure(downloaded_files):
    """Create structure for bulk upload"""
    
    bulk_upload_data = []
    
    for file_info in downloaded_files:
        # Determine category based on filename
        filename = file_info['filename'].lower()
        
        if 'question' in filename:
            category = "Previous Year Questions"
            subcategory = "Question Papers"
        elif 'solution' in filename and 'sample' in filename:
            category = "Sample Papers"
            subcategory = "Sample Solutions"
        elif 'solution' in filename:
            category = "Previous Year Questions"
            subcategory = "Solutions"
        elif 'sample' in filename:
            category = "Sample Papers"
            subcategory = "Sample Papers"
        else:
            category = "Study Materials"
            subcategory = "General"
        
        bulk_upload_data.append({
            "title": file_info['original_text'],
            "description": f"{category} - {subcategory} for Class 12 Applied Mathematics",
            "category": category,
            "subcategory": subcategory,
            "class": "Class 12 Applied Mathematics",
            "file_path": file_info['filepath'],
            "file_size": file_info['size'],
            "tags": [category, subcategory, "Class 12", "Applied Mathematics", "Sunrise Education"],
            "source": "Sunrise Education Centre Linktree",
            "year": extract_year(file_info['original_text'])
        })
    
    # Save bulk upload data
    with open('sunrise_bulk_upload_data.json', 'w') as f:
        json.dump(bulk_upload_data, f, indent=2)
    
    print(f"✅ Bulk upload data created: sunrise_bulk_upload_data.json")
    return bulk_upload_data

def extract_year(text):
    """Extract year from text"""
    import re
    year_match = re.search(r'20\d{2}', text)
    return year_match.group() if year_match else None

if __name__ == "__main__":
    print("🚀 Sunrise Education Centre PDF Downloader")
    print("=" * 50)
    
    # Download PDFs
    downloaded_files = download_pdfs()
    
    if downloaded_files:
        # Create bulk upload structure
        bulk_data = create_bulk_upload_structure(downloaded_files)
        
        print(f"\n🎯 Ready for Bulk Upload:")
        print(f"📁 PDFs downloaded to: sunrise_pdfs/")
        print(f"📄 Bulk upload data: sunrise_bulk_upload_data.json")
        print(f"📊 Download report: sunrise_download_report.json")
        
        print(f"\n📋 Categories found:")
        categories = set(item['category'] for item in bulk_data)
        for category in categories:
            count = len([item for item in bulk_data if item['category'] == category])
            print(f"  - {category}: {count} files")
    else:
        print("❌ No files were downloaded successfully.")
