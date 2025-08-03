#!/usr/bin/env python3
"""
Extract PDF links from Sunrise Education Centre Linktree
"""

import requests
import re
import json
from bs4 import BeautifulSoup
import time

def extract_linktree_links():
    """Extract PDF links from the Sunrise Education Centre Linktree"""
    
    url = "https://linktr.ee/sunrise_educationcentre"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("🔍 Fetching Sunrise Education Centre Linktree...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        pdf_links = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for PDF links or educational content
            if any(keyword in text.lower() for keyword in [
                'question paper', 'solution', 'sample paper', 'formula sheet',
                '2024', '2023', '2022', 'pdf', 'download'
            ]):
                pdf_links.append({
                    'text': text,
                    'url': href,
                    'type': 'pdf_link'
                })
        
        # Also look for any links that might be PDFs
        for link in links:
            href = link.get('href', '')
            if href.endswith('.pdf') or 'drive.google.com' in href or 'dropbox.com' in href:
                text = link.get_text(strip=True)
                pdf_links.append({
                    'text': text,
                    'url': href,
                    'type': 'direct_pdf'
                })
        
        print(f"✅ Found {len(pdf_links)} potential PDF links")
        
        # Save the extracted links
        with open('sunrise_linktree_links.json', 'w') as f:
            json.dump(pdf_links, f, indent=2)
        
        print("📄 Saved links to: sunrise_linktree_links.json")
        
        # Display found links
        print("\n📋 Found Links:")
        for i, link in enumerate(pdf_links, 1):
            print(f"{i}. {link['text']} - {link['url']}")
        
        return pdf_links
        
    except Exception as e:
        print(f"❌ Error extracting links: {e}")
        return []

def create_download_script(links):
    """Create a download script based on extracted links"""
    
    script_content = '''#!/usr/bin/env python3
"""
Download PDFs from Sunrise Education Centre Linktree
Generated from extracted links
"""

import requests
import os
import time
from urllib.parse import urlparse

def download_pdfs():
    """Download PDFs from the extracted links"""
    
    # Extracted links from Linktree
    pdf_links = ''' + json.dumps(links, indent=2) + '''
    
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
            filename = re.sub(r'[^a-zA-Z0-9\\s]', '', link['text'])
            filename = filename.replace(' ', '_') + '.pdf'
            
            response = requests.get(link['url'], headers=headers, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            downloaded_files.append({
                'original_text': link['text'],
                'filename': filename,
                'filepath': filepath,
                'url': link['url']
            })
            
            print(f"✅ Downloaded: {filename}")
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"❌ Error downloading {link['text']}: {e}")
    
    # Save download report
    with open('download_report.json', 'w') as f:
        json.dump(downloaded_files, f, indent=2)
    
    print(f"\\n📊 Download Summary:")
    print(f"Successfully downloaded: {len(downloaded_files)} files")
    print(f"Files saved in: {download_dir}")
    print(f"Report saved as: download_report.json")
    
    return downloaded_files

if __name__ == "__main__":
    import re
    import json
    download_pdfs()
'''
    
    with open('download_sunrise_pdfs.py', 'w') as f:
        f.write(script_content)
    
    print("📝 Created download script: download_sunrise_pdfs.py")

def main():
    print("🚀 Sunrise Education Centre Linktree PDF Extractor")
    print("=" * 50)
    
    # Extract links from Linktree
    links = extract_linktree_links()
    
    if links:
        # Create download script
        create_download_script(links)
        
        print("\n🎯 Next Steps:")
        print("1. Review the extracted links in 'sunrise_linktree_links.json'")
        print("2. Run 'python download_sunrise_pdfs.py' to download PDFs")
        print("3. Upload the downloaded PDFs to your bulk upload system")
    else:
        print("❌ No links found. Please check the Linktree URL.")

if __name__ == "__main__":
    main() 