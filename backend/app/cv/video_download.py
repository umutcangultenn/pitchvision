"""
Video download utility for YouTube and other sources.
"""
import os
import logging
from pathlib import Path
import yt_dlp

logger = logging.getLogger(__name__)


def download_video_from_url(url: str, output_dir: str = "./uploads") -> str:
    """
    Download video from YouTube or other sources using yt-dlp.
    
    Args:
        url: YouTube URL or other video URL
        output_dir: Directory to save the video
        
    Returns:
        Path to the downloaded video file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Prefer MP4
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
    }
    
    try:
        logger.info(f"Downloading video from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            logger.info(f"Video downloaded successfully: {video_path}")
            return video_path
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise


def is_valid_video_url(url: str) -> bool:
    """
    Check if URL is a valid video URL.
    """
    valid_domains = [
        'youtube.com',
        'youtu.be',
        'vimeo.com',
        'dailymotion.com',
        'twitch.tv',
    ]
    
    return any(domain in url.lower() for domain in valid_domains)
