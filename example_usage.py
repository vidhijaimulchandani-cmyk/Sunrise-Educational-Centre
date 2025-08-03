#!/usr/bin/env python3
"""
Example usage of the Linktree Google Drive Extractor
"""

from linktree_drive_extractor import LinktreeDriveExtractor
from linktree_drive_downloader import LinktreeDriveDownloader

def example_extract_only():
    """Example: Extract links only (no download)"""
    print("=== Example: Extract Links Only ===")
    
    extractor = LinktreeDriveExtractor()
    
    # Example Linktree URL (replace with actual URL)
    linktree_url = "https://linktr.ee/example"
    
    # Extract links
    links = extractor.extract_google_drive_links(linktree_url)
    
    # Print results
    extractor.print_links(links)
    
    # Save to file
    extractor.save_links_to_file(links, "extracted_links.json")

def example_extract_and_download():
    """Example: Extract links and download files"""
    print("=== Example: Extract and Download ===")
    
    downloader = LinktreeDriveDownloader()
    
    # Example Linktree URL (replace with actual URL)
    linktree_url = "https://linktr.ee/example"
    
    # Extract and download
    results = downloader.extract_and_download(linktree_url, download_files=True)
    
    # Print results
    downloader.print_results(results)
    
    # Save results
    downloader.save_results(results, "download_results.json")

def example_batch_process():
    """Example: Process multiple Linktree URLs"""
    print("=== Example: Batch Process ===")
    
    # List of Linktree URLs to process
    linktree_urls = [
        "https://linktr.ee/example1",
        "https://linktr.ee/example2",
        # Add more URLs here
    ]
    
    extractor = LinktreeDriveExtractor()
    all_links = []
    
    for url in linktree_urls:
        print(f"\nProcessing: {url}")
        links = extractor.extract_google_drive_links(url)
        all_links.extend(links)
        print(f"Found {len(links)} links")
    
    print(f"\nTotal links found: {len(all_links)}")
    extractor.save_links_to_file(all_links, "batch_extracted_links.json")

if __name__ == "__main__":
    print("Linktree Google Drive Extractor - Examples")
    print("=" * 50)
    
    # Run examples
    example_extract_only()
    print("\n" + "="*50 + "\n")
    example_extract_and_download()
    print("\n" + "="*50 + "\n")
    example_batch_process() 