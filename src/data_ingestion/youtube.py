import json
import os
from typing import List, Dict, Optional

import youtube_dl
from youtube_transcript_api import YouTubeTranscriptApi

from config import config


def get_all_video_links(channel_url: str) -> List[str]:
    """
    Extract all video links from a YouTube channel.
    
    Args:
        channel_url: URL of the YouTube channel
        
    Returns:
        List of video URLs
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
        "extractor_args": {"youtube:tab": "videos"},
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if "entries" in result:
            return [entry["url"] for entry in result["entries"]]
        else:
            return []


def process_video(link: str, languages: List[str] = ["en"]) -> Optional[Dict]:
    """
    Process a YouTube video by extracting its transcript.
    
    Args:
        link: YouTube video URL or ID
        languages: List of language codes to try for transcript
        
    Returns:
        Dictionary with video URL and text, or None if processing failed
    """
    try:
        # Extract video ID from URL if necessary
        video_id = link.split("v=")[-1] if "v=" in link else link
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        combined_text = " ".join(item["text"] for item in transcript)
        return {"video_url": link, "text": combined_text, "video_id": video_id}
    except Exception as e:
        print(f"Error processing {link}: {e}")
        return None


def ingest_channel_videos(channel_url: str, output_dir: str = None) -> List[Dict]:
    """
    Ingest all videos from a YouTube channel.
    
    Args:
        channel_url: URL of the YouTube channel
        output_dir: Directory to save the transcript data
        
    Returns:
        List of processed videos (dictionaries with video_url and text)
    """
    video_data = []
    failed_list = []

    video_links = get_all_video_links(channel_url)
    print(f"Found {len(video_links)} videos")
    
    for link in video_links:
        result = process_video(link)
        if result:
            video_data.append(result)
        else:
            failed_list.append(link)

    # Create output directory if it doesn't exist and if output_dir is specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        # Save results to JSON file
        with open(os.path.join(output_dir, "transcripts.json"), "w", encoding="utf-8") as json_file:
            json.dump(video_data, json_file, ensure_ascii=False, indent=2)
        
        # Save individual transcript files
        for video in video_data:
            filename = f"{video['video_id']}.txt"
            with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
                f.write(video['text'])
                
        # Log failed videos
        if failed_list:
            with open(os.path.join(output_dir, "failed_videos.txt"), "w") as f:
                for link in failed_list:
                    f.write(f"{link}\n")

    print(f"Successfully processed {len(video_data)} videos")
    if failed_list:
        print(f"Failed to process {len(failed_list)} videos")
        
    return video_data