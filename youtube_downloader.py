import yt_dlp
import os
import re
import secrets
from urllib.parse import urlparse, parse_qs
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, download_folder='uploads/videos'):
        self.download_folder = download_folder
        os.makedirs(download_folder, exist_ok=True)
    
    def extract_video_id(self, url):
        """Extract video ID from various YouTube URL formats"""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def is_valid_youtube_url(self, url):
        """Check if the URL is a valid YouTube URL"""
        video_id = self.extract_video_id(url)
        return video_id is not None and len(video_id) == 11
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def download_video(self, url, quality='best'):
        """Download YouTube video and return the file path"""
        try:
            # Extract video ID for filename
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")
            
            # Get video info for better filename
            video_info = self.get_video_info(url)
            title = video_info['title'] if video_info else f"video_{video_id}"
            
            # Clean filename
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            safe_title = safe_title[:50]  # Limit length
            
            # Generate unique filename
            unique_id = secrets.token_hex(4)
            filename = f"{safe_title}_{video_id}_{unique_id}.mp4"
            filepath = os.path.join(self.download_folder, filename)
            
            # Configure download options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Prefer MP4, fallback to best
                'outtmpl': filepath,
                'quiet': False,
                'progress_hooks': [self._progress_hook],
            }
            
            logger.info(f"Starting download: {title}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Verify file was downloaded
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Download completed: {filename} ({file_size} bytes)")
                return {
                    'filename': filename,
                    'filepath': filepath,
                    'title': title,
                    'size': file_size,
                    'video_id': video_id
                }
            else:
                raise Exception("Download failed - file not found")
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            raise
    
    def _progress_hook(self, d):
        """Progress hook for download status"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                logger.info(f"Download progress: {percent:.1f}%")
        elif d['status'] == 'finished':
            logger.info("Download finished, processing...")
    
    def cleanup_old_videos(self, max_age_hours=24):
        """Clean up old downloaded videos to save space"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(self.download_folder):
                filepath = os.path.join(self.download_folder, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old video: {filename}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Utility functions
def download_youtube_video(url, quality='best'):
    """Convenience function to download a YouTube video"""
    downloader = YouTubeDownloader()
    return downloader.download_video(url, quality)

def validate_youtube_url(url):
    """Validate if URL is a proper YouTube URL"""
    downloader = YouTubeDownloader()
    return downloader.is_valid_youtube_url(url)

def get_youtube_video_info(url):
    """Get information about a YouTube video"""
    downloader = YouTubeDownloader()
    return downloader.get_video_info(url) 