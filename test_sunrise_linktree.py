#!/usr/bin/env python3
"""
Test script to extract Google Drive links from Sunrise Education Centre Linktree
"""

from linktree_drive_extractor import LinktreeDriveExtractor
import json

def test_sunrise_linktree():
    """Test the extractor with the Sunrise Education Centre Linktree"""
    
    print("Testing Linktree Google Drive Extractor")
    print("=" * 50)
    
    # Sunrise Education Centre Linktree URL
    linktree_url = "https://linktr.ee/sunrise_education_centre"
    
    print(f"Extracting links from: {linktree_url}")
    print("-" * 50)
    
    # Create extractor
    extractor = LinktreeDriveExtractor()
    
    # Extract links
    links = extractor.extract_google_drive_links(linktree_url)
    
    # Print results
    extractor.print_links(links)
    
    # Save to file
    filename = "sunrise_education_links.json"
    extractor.save_links_to_file(links, filename)
    
    print(f"\nResults saved to: {filename}")
    
    # Show summary
    if links:
        print(f"\nSummary:")
        print(f"- Total Google Drive links found: {len(links)}")
        
        # Count by type
        types = {}
        for link in links:
            link_type = link['type']
            types[link_type] = types.get(link_type, 0) + 1
        
        print(f"- By type:")
        for link_type, count in types.items():
            print(f"  • {link_type.title()}: {count}")
    else:
        print("\nNo Google Drive links found on this Linktree page.")
        print("This could mean:")
        print("- The links are not Google Drive links")
        print("- The page uses JavaScript to load content")
        print("- The links are in a different format")

if __name__ == "__main__":
    test_sunrise_linktree() 