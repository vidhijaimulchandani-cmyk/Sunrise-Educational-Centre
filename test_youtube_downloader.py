#!/usr/bin/env python3
"""
Test script for YouTube downloader functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_downloader import validate_youtube_url, get_youtube_video_info, download_youtube_video

def test_youtube_downloader():
    """Test the YouTube downloader functionality"""
    
    print("🧪 Testing YouTube Downloader...")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (short video)
        "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
        "https://www.youtube.com/embed/dQw4w9WgXcQ",  # Embed format
        "https://www.youtube.com/watch?v=invalid",  # Invalid URL
        "https://google.com",  # Non-YouTube URL
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing URL: {url}")
        print("-" * 40)
        
        # Test URL validation
        is_valid = validate_youtube_url(url)
        print(f"   Valid YouTube URL: {is_valid}")
        
        if is_valid:
            # Test getting video info
            try:
                info = get_youtube_video_info(url)
                if info:
                    print(f"   Video Title: {info['title']}")
                    print(f"   Duration: {info['duration']} seconds")
                    print(f"   Uploader: {info['uploader']}")
                else:
                    print("   ❌ Failed to get video info")
            except Exception as e:
                print(f"   ❌ Error getting video info: {e}")
            
            # Test downloading (only for the first valid URL to avoid too many downloads)
            if i == 1:
                print("\n   🎬 Testing video download...")
                try:
                    result = download_youtube_video(url)
                    print(f"   ✅ Download successful!")
                    print(f"   📁 File: {result['filename']}")
                    print(f"   📏 Size: {result['size']} bytes")
                    print(f"   🎯 Title: {result['title']}")
                    
                    # Clean up test file
                    if os.path.exists(result['filepath']):
                        os.remove(result['filepath'])
                        print(f"   🗑️  Test file cleaned up")
                        
                except Exception as e:
                    print(f"   ❌ Download failed: {e}")
        else:
            print("   ⏭️  Skipping download test for invalid URL")
    
    print("\n" + "=" * 50)
    print("✅ YouTube Downloader Test Complete!")
    print("\nTo use in the application:")
    print("1. Go to Create Live Class page")
    print("2. Select 'YouTube Link' option")
    print("3. Paste a YouTube URL")
    print("4. Submit the form")
    print("5. The video will be downloaded and available in the live class")

if __name__ == "__main__":
    test_youtube_downloader() 