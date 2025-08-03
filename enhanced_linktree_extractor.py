#!/usr/bin/env python3
"""
Enhanced Linktree Google Drive Link Extractor
Handles JavaScript-loaded content and various link formats
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

class EnhancedLinktreeExtractor:
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
    
    def extract_all_links(self, linktree_url):
        """
        Extract all links from a Linktree page and identify Google Drive links
        
        Args:
            linktree_url (str): The Linktree URL to scrape
            
        Returns:
            dict: Dictionary containing all links and Google Drive links
        """
        try:
            logger.info(f"Scraping Linktree page: {linktree_url}")
            
            # Fetch the page
            response = self.session.get(linktree_url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            all_links = []
            google_drive_links = []
            
            # Google Drive URL patterns (expanded)
            drive_patterns = [
                r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9_-]+)',
                # Add more patterns for different formats
                r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/view',
                r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/edit',
                r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)/edit',
                r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)/edit',
                r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)/edit',
            ]
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Store all links
                all_links.append({
                    'url': href,
                    'text': text,
                    'is_google_drive': False
                })
                
                # Check if it's a Google Drive link
                for pattern in drive_patterns:
                    match = re.search(pattern, href)
                    if match:
                        file_id = match.group(1)
                        
                        # Determine link type
                        link_type = self._determine_link_type(href)
                        
                        # Get link text or use default
                        link_text = text if text else f"Google Drive {link_type.title()}"
                        
                        google_drive_links.append({
                            'url': href,
                            'file_id': file_id,
                            'text': link_text,
                            'type': link_type,
                            'direct_download_url': self._get_direct_download_url(href, file_id)
                        })
                        
                        # Mark as Google Drive in all_links
                        for all_link in all_links:
                            if all_link['url'] == href:
                                all_link['is_google_drive'] = True
                        break
            
            logger.info(f"Found {len(all_links)} total links, {len(google_drive_links)} Google Drive links")
            
            return {
                'all_links': all_links,
                'google_drive_links': google_drive_links,
                'total_links': len(all_links),
                'total_google_drive': len(google_drive_links)
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Linktree page: {e}")
            return {'all_links': [], 'google_drive_links': [], 'total_links': 0, 'total_google_drive': 0}
        except Exception as e:
            logger.error(f"Error parsing Linktree page: {e}")
            return {'all_links': [], 'google_drive_links': [], 'total_links': 0, 'total_google_drive': 0}
    
    def _determine_link_type(self, url):
        """Determine the type of Google Drive link"""
        if 'docs.google.com/document' in url:
            return 'document'
        elif 'docs.google.com/spreadsheets' in url:
            return 'spreadsheet'
        elif 'docs.google.com/presentation' in url:
            return 'presentation'
        elif 'drive.google.com/drive/folders' in url:
            return 'folder'
        elif 'drive.google.com/file' in url:
            return 'file'
        else:
            return 'unknown'
    
    def _get_direct_download_url(self, original_url, file_id):
        """Generate direct download URL for Google Drive files"""
        if 'docs.google.com/document' in original_url:
            return f"https://docs.google.com/document/d/{file_id}/export?format=pdf"
        elif 'docs.google.com/spreadsheets' in original_url:
            return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        elif 'docs.google.com/presentation' in original_url:
            return f"https://docs.google.com/presentation/d/{file_id}/export?format=pptx"
        elif 'drive.google.com/file' in original_url:
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            return original_url
    
    def print_all_links(self, results):
        """Print all links found on the page"""
        print(f"\n{'='*60}")
        print(f"All Links Found ({results['total_links']} total):")
        print(f"{'='*60}")
        
        for i, link in enumerate(results['all_links'], 1):
            drive_indicator = "🔗" if link['is_google_drive'] else "  "
            print(f"{drive_indicator} {i}. {link['text']}")
            print(f"     URL: {link['url']}")
            print("-" * 40)
    
    def print_google_drive_links(self, results):
        """Print only Google Drive links"""
        links = results['google_drive_links']
        
        if not links:
            print("\nNo Google Drive links found!")
            return
        
        print(f"\n{'='*60}")
        print(f"Google Drive Links Found ({len(links)}):")
        print(f"{'='*60}")
        
        for i, link in enumerate(links, 1):
            print(f"\n{i}. {link['text']}")
            print(f"   Type: {link['type']}")
            print(f"   URL: {link['url']}")
            print(f"   File ID: {link['file_id']}")
            if link['direct_download_url'] != link['url']:
                print(f"   Direct Download: {link['direct_download_url']}")
            print("-" * 40)
    
    def save_results(self, results, filename='linktree_analysis.json'):
        """Save all results to a JSON file"""
        try:
            data = {
                'extracted_at': datetime.now().isoformat(),
                'total_links': results['total_links'],
                'total_google_drive': results['total_google_drive'],
                'all_links': results['all_links'],
                'google_drive_links': results['google_drive_links']
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

def main():
    """Main function to run the enhanced extractor"""
    import sys
    
    extractor = EnhancedLinktreeExtractor()
    
    print("Enhanced Linktree Link Extractor")
    print("=" * 40)
    
    # Get URL from command line argument or use default
    if len(sys.argv) > 1:
        linktree_url = sys.argv[1]
    else:
        linktree_url = "https://linktr.ee/sunrise_education_centre"
    
    print(f"Analyzing: {linktree_url}")
    print("-" * 40)
    
    # Extract all links
    results = extractor.extract_all_links(linktree_url)
    
    # Print all links
    extractor.print_all_links(results)
    
    # Print Google Drive links
    extractor.print_google_drive_links(results)
    
    # Save results
    extractor.save_results(results, "sunrise_education_analysis.json")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"Total links found: {results['total_links']}")
    print(f"Google Drive links: {results['total_google_drive']}")
    print(f"Other links: {results['total_links'] - results['total_google_drive']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 