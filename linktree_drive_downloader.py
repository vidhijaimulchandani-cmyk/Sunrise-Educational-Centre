import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
import time
import mimetypes

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LinktreeDriveDownloader:
    def __init__(self, download_folder='uploads/from_linktree'):
        self.session = requests.Session()
        self.download_folder = download_folder
        
        # Create download folder
        os.makedirs(download_folder, exist_ok=True)
        
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_and_download(self, linktree_url, download_files=True):
        """
        Extract Google Drive links and optionally download them
        
        Args:
            linktree_url (str): The Linktree URL to scrape
            download_files (bool): Whether to download the files
            
        Returns:
            dict: Results of extraction and download
        """
        # Extract links first
        links = self._extract_google_drive_links(linktree_url)
        
        results = {
            'extracted_at': datetime.now().isoformat(),
            'linktree_url': linktree_url,
            'total_links': len(links),
            'links': links,
            'downloads': []
        }
        
        if download_files and links:
            results['downloads'] = self._download_files(links)
        
        return results
    
    def _extract_google_drive_links(self, linktree_url):
        """Extract Google Drive links from Linktree page"""
        try:
            logger.info(f"Scraping Linktree page: {linktree_url}")
            
            # Fetch the page
            response = self.session.get(linktree_url, timeout=15)
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
    
    def _download_files(self, links):
        """Download files from Google Drive links"""
        downloads = []
        
        for i, link in enumerate(links, 1):
            try:
                logger.info(f"Downloading {i}/{len(links)}: {link['text']}")
                
                # Skip folders for now (would need special handling)
                if link['type'] == 'folder':
                    logger.warning(f"Skipping folder: {link['text']}")
                    downloads.append({
                        'filename': None,
                        'status': 'skipped',
                        'reason': 'Folder download not supported',
                        'link': link
                    })
                    continue
                
                # Download the file
                result = self._download_single_file(link)
                downloads.append(result)
                
                # Add delay to avoid overwhelming the server
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error downloading {link['text']}: {e}")
                downloads.append({
                    'filename': None,
                    'status': 'error',
                    'error': str(e),
                    'link': link
                })
        
        return downloads
    
    def _download_single_file(self, link):
        """Download a single file from Google Drive"""
        try:
            download_url = link['direct_download_url']
            
            # Get file info first
            response = self.session.head(download_url, allow_redirects=True)
            
            # Get filename from content-disposition or use default
            filename = self._get_filename_from_response(response, link)
            
            # Download the file
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_folder, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            
            logger.info(f"Downloaded: {filename} ({file_size} bytes)")
            
            return {
                'filename': filename,
                'filepath': filepath,
                'size': file_size,
                'status': 'success',
                'link': link
            }
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {
                'filename': None,
                'status': 'error',
                'error': str(e),
                'link': link
            }
    
    def _get_filename_from_response(self, response, link):
        """Extract filename from response headers or generate one"""
        # Try to get filename from content-disposition header
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename:
                return filename.group(1)
        
        # Generate filename based on link info
        safe_text = re.sub(r'[^\w\s-]', '', link['text']).strip()
        safe_text = re.sub(r'[-\s]+', '-', safe_text)
        safe_text = safe_text[:50]  # Limit length
        
        # Add appropriate extension based on type
        extension_map = {
            'document': '.pdf',
            'spreadsheet': '.xlsx',
            'presentation': '.pptx',
            'file': '.pdf'  # Default for files
        }
        
        extension = extension_map.get(link['type'], '.pdf')
        filename = f"{safe_text}_{link['file_id']}{extension}"
        
        return filename
    
    def save_results(self, results, output_file='linktree_download_results.json'):
        """Save results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def print_results(self, results):
        """Print results in a formatted way"""
        print(f"\n{'='*60}")
        print(f"Linktree Google Drive Download Results")
        print(f"{'='*60}")
        print(f"Linktree URL: {results['linktree_url']}")
        print(f"Total Links Found: {results['total_links']}")
        print(f"Extracted At: {results['extracted_at']}")
        
        if results['downloads']:
            print(f"\nDownload Results:")
            print(f"{'='*40}")
            
            successful = 0
            failed = 0
            skipped = 0
            
            for download in results['downloads']:
                if download['status'] == 'success':
                    successful += 1
                    print(f"✅ {download['filename']} ({download['size']} bytes)")
                elif download['status'] == 'error':
                    failed += 1
                    print(f"❌ Failed: {download['link']['text']} - {download['error']}")
                elif download['status'] == 'skipped':
                    skipped += 1
                    print(f"⏭️  Skipped: {download['link']['text']} - {download['reason']}")
            
            print(f"\nSummary: {successful} successful, {failed} failed, {skipped} skipped")
        else:
            print("\nNo downloads attempted.")

def main():
    """Main function to run the downloader"""
    downloader = LinktreeDriveDownloader()
    
    print("Linktree Google Drive Downloader")
    print("=" * 40)
    
    # Get Linktree URL from user
    linktree_url = input("Enter the Linktree URL: ").strip()
    
    if not linktree_url:
        print("No URL provided!")
        return
    
    # Ask if user wants to download files
    download_files = input("Download files? (y/n): ").lower().strip() == 'y'
    
    # Extract and download
    results = downloader.extract_and_download(linktree_url, download_files)
    
    # Print results
    downloader.print_results(results)
    
    # Save results
    save_results = input("\nSave results to file? (y/n): ").lower().strip()
    if save_results == 'y':
        filename = input("Enter filename (default: linktree_download_results.json): ").strip()
        if not filename:
            filename = 'linktree_download_results.json'
        downloader.save_results(results, filename)

if __name__ == "__main__":
    main() 