"""
YouTube content ingestion component
"""
import os
import json
import uuid
import streamlit as st
from typing import List, Dict, Any, Optional
import re

from config.config import YOUTUBE_DIR
from src.data_ingestion.youtube import ingest_channel_videos
from src.retrieval.document_store import load_documents_from_directory
from src.embedding.embeddings import process_documents_for_embedding  
from src.retrieval.document_store import DocumentRetriever
from src.ui.utils.file_utils import is_valid_url, extract_youtube_id
from src.ui.utils.source_utils import scan_knowledge_sources, create_knowledge_collection
from src.ui.models.retriever import initialize_source_retriever

def select_source_for_chat(source: Dict[str, Any]):
    """
    Set up chat with a selected source
    
    Args:
        source: The source metadata to select
    """
    st.session_state.active_source = source
    st.session_state.sidebar_view = "chat"
    
    # Create welcome message based on source type
    if source.get("is_collection", False):
        welcome_msg = f"Hello! I've analyzed the collection '{source['name']}'. What would you like to know about it?"
    else:
        welcome_msg = f"Hello! I've analyzed the content from {source['name']}. What would you like to know about it?"
    
    st.session_state.messages = [{
        "role": "assistant",
        "content": welcome_msg
    }]
    
    # Initialize the retriever for this source
    st.session_state.retriever = initialize_source_retriever(source)
    
    # Force rerun to update UI
    st.rerun()

def ingest_knowledge_source(url: str, name: str, source_type: str = "youtube"):
    """
    Process a new knowledge source with progress tracking
    
    Args:
        url: URL of the source to ingest
        name: Name for the source
        source_type: Type of source (e.g., "youtube")
        
    Returns:
        Boolean indicating success
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Starting ingestion process...")
    progress_bar.progress(10)
    
    try:
        if source_type == "youtube":
            # Create YouTube directory if it doesn't exist
            os.makedirs(YOUTUBE_DIR, exist_ok=True)
            
            # Extract source identifier for grouping
            source_id = extract_youtube_id(url)
            
            # Create a collection for this playlist/channel
            collection_name = name or f"YouTube Collection: {source_id}"
            collection_description = f"Content from YouTube URL: {url}"
            
            # Extract videos
            status_text.text("Extracting videos from the channel/playlist...")
            videos = ingest_channel_videos(url, YOUTUBE_DIR)
            status_text.text(f"Found {len(videos)} video entries.")
            progress_bar.progress(40)
            
            # Fallback: check transcripts.json if no videos returned
            transcripts_json = os.path.join(YOUTUBE_DIR, "transcripts.json")
            if not videos and os.path.exists(transcripts_json):
                status_text.text("No direct transcripts; loading from transcripts.json...")
                try:
                    with open(transcripts_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        videos = data
                        status_text.text(f"Loaded {len(videos)} entries from transcripts.json at {transcripts_json}")
                        progress_bar.progress(50)
                except Exception:
                    status_text.error("Failed to load transcripts.json fallback.")
                    progress_bar.progress(100)
                    return False
            
            if not videos:
                status_text.error("No video transcripts were created. Please check the channel URL or ensure transcripts exist.")
                progress_bar.progress(100)
                return False
            
            # Process videos
            status_text.text(f"Processing {len(videos)} videos for embedding...")
            youtube_docs = load_documents_from_directory(YOUTUBE_DIR)
            progress_bar.progress(50)
            
            if not youtube_docs:
                status_text.error("Failed to load document content from videos.")
                progress_bar.progress(100)
                return False
            
            # Get paths to the video transcript files
            video_file_paths = []
            for video in videos:
                vid = video.get("video_id")
                if not vid:
                    continue
                path = os.path.join(YOUTUBE_DIR, f"{vid}.txt")
                if os.path.exists(path):
                    video_file_paths.append(path)
            
            if not video_file_paths:
                status_text.error("No video transcript files were found on disk.")
                progress_bar.progress(100)
                return False
                
            # Create a collection for these videos
            status_text.text("Creating a knowledge collection for the videos...")
            collection = create_knowledge_collection(
                name=collection_name,
                description=collection_description,
                source_files=video_file_paths
            )
            progress_bar.progress(70)
            
            # Generate embeddings for the collection
            status_text.text("Generating embeddings for video content...")
            collection_docs = [{"id": collection["id"], "text": open(collection["combined_file"], 'r', encoding='utf-8').read()}]
            processed_docs = process_documents_for_embedding(collection_docs)
            progress_bar.progress(85)
            
            # Initialize retriever
            retriever = DocumentRetriever()
            retriever.add_documents(processed_docs)
            
            # Update session state
            st.session_state.retriever = retriever
            progress_bar.progress(100)
            status_text.text("✅ Ingestion complete! You can now chat with the collection.")
            
            # Force refresh of knowledge sources
            sources = scan_knowledge_sources(force_refresh=True)
            
            # Find the newly created collection
            collection_source = next((s for s in sources if s.get("collection_id") == collection["id"]), None)
            
            if collection_source:
                select_source_for_chat(collection_source)
            else:
                # Fallback if collection not found
                st.session_state.sidebar_view = "chat"
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": f"Hello! I've analyzed the YouTube videos from {url}. What would you like to know about them?"
                }]
                st.rerun()
            
            return True
        else:
            status_text.error(f"Source type '{source_type}' is not yet supported for ingestion.")
            progress_bar.progress(100)
            return False
            
    except Exception as e:
        status_text.error(f"Error during ingestion: {str(e)}")
        progress_bar.progress(100)
        return False

def show_add_source_page():
    """
    Display add knowledge source form
    """
    st.markdown("## Add New Knowledge Source")
    st.markdown("Enter a YouTube channel or playlist URL to extract and process its content")
    
    # YouTube URL input
    youtube_url = st.text_input("YouTube URL", key="url_input", 
                               placeholder="https://www.youtube.com/channel/... or https://www.youtube.com/playlist?list=...")
    
    # Collection name
    collection_name = st.text_input("Collection Name (optional)", key="collection_name", 
                                  placeholder="My YouTube Collection")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        start_button = st.button("Process YouTube", use_container_width=True)
    
    # Handle the start button click
    if start_button and youtube_url:
        if is_valid_url(youtube_url, "youtube"):
            st.session_state.youtube_url = youtube_url
            ingest_knowledge_source(youtube_url, collection_name, "youtube")
        else:
            st.error("Please enter a valid YouTube URL")
