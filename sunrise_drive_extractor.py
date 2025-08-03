#!/usr/bin/env python3
"""
Specialized Google Drive Link Extractor for Sunrise Education Centre
Handles direct download URLs and link-lock URLs
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SunriseDriveExtractor:
    def __init__(self):
        self.session = requests.Session()
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_sunrise_links(self, linktree_url):
        """
        Extract all links from Sunrise Education Centre Linktree
        
        Args:
            linktree_url (str): The Linktree URL to scrape
            
        Returns:
            dict: Dictionary containing categorized links
        """
        try:
            logger.info(f"Scraping Sunrise Education Centre Linktree: {linktree_url}")
            
            # Fetch the page
            response = self.session.get(linktree_url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            categorized_links = {
                'google_drive_direct': [],
                'google_docs': [],
                'link_locked': [],
                'social_media': [],
                'other': []
            }
            
            # Google Drive direct download pattern
            drive_direct_pattern = r'https://drive\.google\.com/uc\?export=download&id=([a-zA-Z0-9_-]+)'
            
            # Google Docs patterns
            docs_patterns = [
                r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/forms/d/([a-zA-Z0-9_-]+)',
            ]
            
            # Link-lock pattern
            link_lock_pattern = r'https://jstrieb\.github\.io/link-lock/#([a-zA-Z0-9_-]+)'
            
            # Social media patterns
            social_patterns = [
                r'instagram\.com',
                r'youtube\.com',
                r'whatsapp\.com',
                r'api\.whatsapp\.com'
            ]
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                link_info = {
                    'url': href,
                    'text': text,
                    'file_id': None,
                    'type': 'unknown'
                }
                
                # Check for Google Drive direct download
                drive_match = re.search(drive_direct_pattern, href)
                if drive_match:
                    file_id = drive_match.group(1)
                    link_info['file_id'] = file_id
                    link_info['type'] = 'google_drive_direct'
                    categorized_links['google_drive_direct'].append(link_info)
                    continue
                
                # Check for Google Docs
                for pattern in docs_patterns:
                    docs_match = re.search(pattern, href)
                    if docs_match:
                        file_id = docs_match.group(1)
                        link_info['file_id'] = file_id
                        link_info['type'] = 'google_docs'
                        categorized_links['google_docs'].append(link_info)
                        break
                else:
                    # Check for link-lock
                    lock_match = re.search(link_lock_pattern, href)
                    if lock_match:
                        link_info['type'] = 'link_locked'
                        categorized_links['link_locked'].append(link_info)
                        continue
                    
                    # Check for social media
                    for pattern in social_patterns:
                        if re.search(pattern, href):
                            link_info['type'] = 'social_media'
                            categorized_links['social_media'].append(link_info)
                            break
                    else:
                        # Other links
                        categorized_links['other'].append(link_info)
            
            # Calculate totals
            total_links = sum(len(category) for category in categorized_links.values())
            google_drive_total = len(categorized_links['google_drive_direct']) + len(categorized_links['google_docs'])
            
            logger.info(f"Found {total_links} total links")
            logger.info(f"Google Drive links: {google_drive_total}")
            logger.info(f"Link-locked: {len(categorized_links['link_locked'])}")
            logger.info(f"Social media: {len(categorized_links['social_media'])}")
            
            return {
                'categorized_links': categorized_links,
                'total_links': total_links,
                'google_drive_total': google_drive_total,
                'link_locked_count': len(categorized_links['link_locked']),
                'social_media_count': len(categorized_links['social_media'])
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Linktree page: {e}")
            return {'categorized_links': {}, 'total_links': 0, 'google_drive_total': 0}
        except Exception as e:
            logger.error(f"Error parsing Linktree page: {e}")
            return {'categorized_links': {}, 'total_links': 0, 'google_drive_total': 0}
    
    def print_categorized_links(self, results):
        """Print links by category"""
        categories = results['categorized_links']
        
        print(f"\n{'='*70}")
        print(f"SUNRISE EDUCATION CENTRE - LINKTREE ANALYSIS")
        print(f"{'='*70}")
        
        # Google Drive Direct Downloads
        if categories['google_drive_direct']:
            print(f"\n📁 GOOGLE DRIVE DIRECT DOWNLOADS ({len(categories['google_drive_direct'])}):")
            print("-" * 50)
            for i, link in enumerate(categories['google_drive_direct'], 1):
                print(f"{i:2d}. {link['text']}")
                print(f"     File ID: {link['file_id']}")
                print(f"     URL: {link['url']}")
                print()
        
        # Google Docs
        if categories['google_docs']:
            print(f"\n📄 GOOGLE DOCS ({len(categories['google_docs'])}):")
            print("-" * 50)
            for i, link in enumerate(categories['google_docs'], 1):
                print(f"{i:2d}. {link['text']}")
                print(f"     File ID: {link['file_id']}")
                print(f"     URL: {link['url']}")
                print()
        
        # Link-locked content
        if categories['link_locked']:
            print(f"\n🔒 LINK-LOCKED CONTENT ({len(categories['link_locked'])}):")
            print("-" * 50)
            for i, link in enumerate(categories['link_locked'], 1):
                print(f"{i:2d}. {link['text']}")
                print(f"     URL: {link['url']}")
                print()
        
        # Social media
        if categories['social_media']:
            print(f"\n📱 SOCIAL MEDIA ({len(categories['social_media'])}):")
            print("-" * 50)
            for i, link in enumerate(categories['social_media'], 1):
                print(f"{i:2d}. {link['text']}")
                print(f"     URL: {link['url']}")
                print()
        
        # Other links
        if categories['other']:
            print(f"\n🔗 OTHER LINKS ({len(categories['other'])}):")
            print("-" * 50)
            for i, link in enumerate(categories['other'], 1):
                print(f"{i:2d}. {link['text']}")
                print(f"     URL: {link['url']}")
                print()
    
    def generate_download_script(self, results):
        """Generate a Python script to download all Google Drive files"""
        drive_links = results['categorized_links']['google_drive_direct']
        
        if not drive_links:
            print("No Google Drive direct download links found!")
            return
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated download script for Sunrise Education Centre resources
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import requests
import os
from urllib.parse import urlparse

def download_sunrise_resources():
    """Download all Google Drive resources from Sunrise Education Centre"""
    
    # Create download directory
    download_dir = "uploads/sunrise_education"
    os.makedirs(download_dir, exist_ok=True)
    
    # Resources to download
    resources = [
'''
        
        for link in drive_links:
            safe_filename = re.sub(r'[^\w\s-]', '', link['text']).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            safe_filename = f"{safe_filename}_{link['file_id']}.pdf"
            
            script_content += f'''        {{
            "filename": "{safe_filename}",
            "url": "{link['url']}",
            "title": "{link['text']}",
            "file_id": "{link['file_id']}"
        }},\n'''
        
        script_content += '''    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    successful = 0
    failed = 0
    
    for i, resource in enumerate(resources, 1):
        try:
            print(f"Downloading {{i}}/{{len(resources)}}: {{resource['title']}}")
            
            response = session.get(resource['url'], stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(download_dir, resource['filename'])
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            print(f"✅ Downloaded: {{resource['filename']}} ({{file_size}} bytes)")
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed to download {{resource['title']}}: {{e}}")
            failed += 1
    
    print(f"\\nDownload Summary:")
    print(f"✅ Successful: {{successful}}")
    print(f"❌ Failed: {{failed}}")
    print(f"📁 Files saved to: {{download_dir}}")

if __name__ == "__main__":
    download_sunrise_resources()
'''
        
        # Save the script
        script_filename = "download_sunrise_resources.py"
        with open(script_filename, 'w') as f:
            f.write(script_content)
        
        print(f"\n📥 Download script generated: {script_filename}")
        print(f"Run 'python3 {script_filename}' to download all resources")
    
    def save_results(self, results, filename='sunrise_education_analysis.json'):
        """Save results to JSON file"""
        try:
            data = {
                'extracted_at': datetime.now().isoformat(),
                'total_links': results['total_links'],
                'google_drive_total': results['google_drive_total'],
                'link_locked_count': results['link_locked_count'],
                'social_media_count': results['social_media_count'],
                'categorized_links': results['categorized_links']
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

def main():
    """Main function to run the Sunrise extractor"""
    extractor = SunriseDriveExtractor()
    
    print("Sunrise Education Centre - Google Drive Link Extractor")
    print("=" * 60)
    
    # Sunrise Education Centre Linktree URL
    linktree_url = "https://linktr.ee/sunrise_education_centre"
    
    print(f"Analyzing: {linktree_url}")
    print("-" * 60)
    
    # Extract links
    results = extractor.extract_sunrise_links(linktree_url)
    
    # Print results
    extractor.print_categorized_links(results)
    
    # Generate download script
    extractor.generate_download_script(results)
    
    # Save results
    extractor.save_results(results, "sunrise_education_detailed.json")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY:")
    print(f"Total links found: {results['total_links']}")
    print(f"Google Drive links: {results['google_drive_total']}")
    print(f"Link-locked content: {results['link_locked_count']}")
    print(f"Social media links: {results['social_media_count']}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main() 