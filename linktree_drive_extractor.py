import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinktreeDriveExtractor:
    def __init__(self):
        self.session = requests.Session()
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_google_drive_links(self, linktree_url):
        """
        Extract Google Drive links from a Linktree page
        
        Args:
            linktree_url (str): The Linktree URL to scrape
            
        Returns:
            list: List of dictionaries containing Google Drive link information
        """
        try:
            logger.info(f"Scraping Linktree page: {linktree_url}")
            
            # Fetch the page
            response = self.session.get(linktree_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            google_drive_links = []
            
            # Google Drive URL patterns
            drive_patterns = [
                r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)',
                r'https://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)',
                r'https://drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9_-]+)'
            ]
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
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
                        break
            
            logger.info(f"Found {len(google_drive_links)} Google Drive links")
            return google_drive_links
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Linktree page: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing Linktree page: {e}")
            return []
    
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
    
    def save_links_to_file(self, links, output_file='google_drive_links.json'):
        """Save extracted links to a JSON file"""
        try:
            data = {
                'extracted_at': datetime.now().isoformat(),
                'total_links': len(links),
                'links': links
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Links saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving links to file: {e}")
            return False
    
    def print_links(self, links):
        """Print extracted links in a formatted way"""
        if not links:
            print("No Google Drive links found!")
            return
        
        print(f"\n{'='*60}")
        print(f"Found {len(links)} Google Drive links:")
        print(f"{'='*60}")
        
        for i, link in enumerate(links, 1):
            print(f"\n{i}. {link['text']}")
            print(f"   Type: {link['type']}")
            print(f"   URL: {link['url']}")
            print(f"   File ID: {link['file_id']}")
            if link['direct_download_url'] != link['url']:
                print(f"   Direct Download: {link['direct_download_url']}")
            print("-" * 40)

def main():
    """Main function to run the extractor"""
    extractor = LinktreeDriveExtractor()
    
    print("Linktree Google Drive Link Extractor")
    print("=" * 40)
    
    # Get Linktree URL from user
    linktree_url = input("Enter the Linktree URL: ").strip()
    
    if not linktree_url:
        print("No URL provided!")
        return
    
    # Extract links
    links = extractor.extract_google_drive_links(linktree_url)
    
    if links:
        # Print results
        extractor.print_links(links)
        
        # Save to file
        save_to_file = input("\nSave links to file? (y/n): ").lower().strip()
        if save_to_file == 'y':
            filename = input("Enter filename (default: google_drive_links.json): ").strip()
            if not filename:
                filename = 'google_drive_links.json'
            extractor.save_links_to_file(links, filename)
    else:
        print("No Google Drive links found on this Linktree page.")

if __name__ == "__main__":
    main() 