"""
File and path utilities for knowledge sources
"""
import os
import json
import hashlib
import re
from typing import List, Dict, Any, Optional

def get_file_preview(file_path: str, max_length: int = 200) -> str:
    """
    Get a preview of a file's content
    
    Args:
        file_path: Path to the file
        max_length: Maximum length of the preview
        
    Returns:
        String containing file preview content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_length)
            if os.path.getsize(file_path) > max_length:
                content += "..."
            return content
    except Exception:
        return "Content preview unavailable"

def is_valid_url(url: str, url_type: str = "youtube") -> bool:
    """
    Validate if a URL is of the expected type
    
    Args:
        url: The URL to validate
        url_type: The expected URL type
        
    Returns:
        Boolean indicating if URL is valid
    """
    if url_type == "youtube":
        return "youtube.com" in url or "youtu.be" in url
    return False

def extract_youtube_id(url: str) -> str:
    """
    Extract ID information from a YouTube URL
    
    Args:
        url: YouTube URL to process
        
    Returns:
        Extracted ID string
    """
    # Extract playlist ID
    playlist_match = re.search(r'playlist\?list=([^&]+)', url)
    if playlist_match:
        return f"playlist_{playlist_match.group(1)}"
    
    # Extract channel ID
    channel_match = re.search(r'channel/([^/]+)', url)
    if channel_match:
        return f"channel_{channel_match.group(1)}"
    
    # Extract video ID
    video_match = re.search(r'v=([^&]+)', url) or re.search(r'youtu\.be/([^?&]+)', url)
    if video_match:
        return f"video_{video_match.group(1)}"
    
    # Generate a random ID if nothing matches
    import uuid
    return f"youtube_{uuid.uuid4().hex[:8]}"

def generate_source_id(source_type: str, file_path: str) -> str:
    """
    Generate a unique ID for a source
    
    Args:
        source_type: Type of the source
        file_path: Path to the source file
        
    Returns:
        Unique source ID
    """
    filename = os.path.basename(file_path)
    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
    return f"{source_type}_{filename}_{file_hash}"
