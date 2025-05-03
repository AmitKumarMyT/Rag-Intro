"""
Script to ingest YouTube videos from a channel.
"""
from app import ingest_youtube_channel

if __name__ == "__main__":
    channel_url = input("Enter YouTube channel URL (or press Enter for default): ")
    if not channel_url:
        # Use default channel for testing
        channel_url = "https://www.youtube.com/@dzylo2861/videos"
        print(f"Using default channel: {channel_url}")
        
    ingest_youtube_channel(channel_url)