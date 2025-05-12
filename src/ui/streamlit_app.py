"""
Streamlit-based UI for the Smart Knowledge Agent with automatic source detection.
Features a frosted glass dark theme, dynamic knowledge source discovery, and modular design.
"""
import os
import time
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
import glob
import json
import shutil
from datetime import datetime
import re
import hashlib
import uuid

# Import project modules
from src.data_ingestion.youtube import ingest_channel_videos
from src.embedding.embeddings import process_documents_for_embedding
from src.retrieval.document_store import DocumentRetriever, load_documents_from_directory
from src.retrieval.response_generator import generate_response
from config.config import YOUTUBE_DIR, DOCUMENT_DIR

# Define knowledge sources collection directory
KNOWLEDGE_COLLECTIONS_DIR = os.path.join(os.path.dirname(YOUTUBE_DIR), "knowledge_collections")
COLLECTIONS_INDEX_FILE = os.path.join(KNOWLEDGE_COLLECTIONS_DIR, "collections_index.json")

# Knowledge source types configuration - easily expandable for future source types
SOURCE_TYPES = {
    "youtube": {
        "icon": "🎬",
        "display_name": "YouTube",
        "file_extensions": [".txt"],
        "directory": YOUTUBE_DIR,
        "name_pattern": lambda filename: f"YouTube: {os.path.basename(filename).replace('.txt', '')}"
    },
    "news": {
        "icon": "📰",
        "display_name": "News Article",
        "file_extensions": [".txt"],
        "directory": DOCUMENT_DIR,
        "name_pattern": lambda filename: os.path.basename(filename).replace('.txt', '')
    },
    "collection": {
        "icon": "📚",
        "display_name": "Knowledge Collection",
        "file_extensions": [".txt"],
        "directory": KNOWLEDGE_COLLECTIONS_DIR,
        "name_pattern": lambda filename: os.path.basename(filename)
    }
}

# Set page configuration
st.set_page_config(
    page_title="Smart Knowledge Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for frosted glass dark theme
def apply_custom_css():
    st.markdown("""
    <style>
        /* Main background with subtle gradient animation */
        .stApp {
            background: linear-gradient(-45deg, #0f0f1a, #1a1a2e, #21213a, #262645);
            background-size: 400% 400%;
            animation: gradient-shift 15s ease infinite;
            color: rgba(255, 255, 255, 0.9);
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50% }
            50% { background-position: 100% 50% }
            100% { background-position: 0% 50% }
        }
        
        /* Frosted glass card styling */
        .glass-card {
            background: rgba(30, 30, 50, 0.35);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 22px;
            margin: 12px 0;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        /* Knowledge source card styling */
        .source-card {
            background: rgba(40, 40, 70, 0.35);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 16px;
            margin: 8px;
            box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .source-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px 0 rgba(69, 104, 220, 0.3);
            border: 1px solid rgba(106, 48, 147, 0.3);
            background: rgba(45, 45, 75, 0.45);
        }
        
        .source-icon {
            font-size: 30px;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .source-title {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 16px;
        }
        
        .source-info {
            font-size: 12px;
            opacity: 0.7;
            margin-top: auto;
        }
        
        /* Chat input field styling */
        .stTextInput > div > div > input {
            background-color: rgba(60, 60, 80, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 16px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border: 1px solid rgba(106, 48, 147, 0.5);
            box-shadow: 0 4px 20px rgba(69, 104, 220, 0.3);
            background-color: rgba(60, 60, 80, 0.3);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            color: white;
            border: none;
            border-radius: 24px;
            padding: 10px 24px;
            transition: all 0.3s ease;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(106, 48, 147, 0.4);
            background: linear-gradient(90deg, #4568dc, #7a359f);
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #6a3093;
        }
        
        /* Message container styling */
        .user-message {
            background: rgba(69, 104, 220, 0.15);
            border-radius: 18px 18px 0 18px;
            padding: 16px;
            margin: 12px 0;
            border-left: 3px solid #4568dc;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            animation: slide-in-right 0.3s ease;
            max-width: 90%;
            margin-left: auto;
            color: rgba(255, 255, 255, 0.95);
        }
        
        .assistant-message {
            background: rgba(106, 48, 147, 0.15);
            border-radius: 18px 18px 18px 0;
            padding: 16px;
            margin: 12px 0;
            border-right: 3px solid #6a3093;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            animation: slide-in-left 0.3s ease;
            max-width: 90%;
            margin-right: auto;
            color: rgba(255, 255, 255, 0.95);
        }
        
        @keyframes slide-in-right {
            from { transform: translateX(20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slide-in-left {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Section title styling */
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0 15px 0;
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        /* Source preview container */
        .source-preview {
            background: rgba(20, 20, 35, 0.3);
            padding: 12px;
            border-radius: 12px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 12px;
            max-height: 100px;
            overflow-y: auto;
            white-space: pre-wrap;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-1wrcr25, .st-c8, .st-bq, section[data-testid="stSidebar"] {
            background: rgba(20, 20, 35, 0.4) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
        }
        
        /* Sidebar header */
        .sidebar-header {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 24px;
            letter-spacing: 0.5px;
        }
        
        /* Sidebar nav item */
        .sidebar-nav-item {
            background: rgba(30, 30, 50, 0.4);
            border-radius: 12px;
            padding: 12px 16px;
            margin: 6px 0;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
        }
        
        .sidebar-nav-item:hover {
            background: rgba(40, 40, 60, 0.6);
            transform: translateX(3px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .sidebar-nav-icon {
            margin-right: 10px;
            font-size: 18px;
        }
        
        /* Selected source highlight */
        .selected-source {
            border-left: 4px solid #6a3093;
            background: rgba(50, 50, 80, 0.4);
            box-shadow: 0 4px 15px rgba(106, 48, 147, 0.2);
        }
        
        /* Action buttons for sources */
        .source-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 8px;
        }
        
        .action-btn {
            background: rgba(40, 40, 70, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .action-btn:hover {
            background: rgba(70, 70, 100, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Source items in collection */
        .collection-items {
            margin-top: 10px;
            padding: 10px;
            background: rgba(20, 20, 35, 0.2);
            border-radius: 10px;
            font-size: 12px;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .collection-item {
            padding: 4px 8px;
            margin: 3px 0;
            border-radius: 6px;
            background: rgba(60, 60, 90, 0.2);
            transition: all 0.2s ease;
        }
        
        .collection-item:hover {
            background: rgba(60, 60, 90, 0.4);
        }
        
        /* Form elements */
        .stTextInput, .stTextArea, .stSelectbox {
            filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
        }
        
        /* Chat welcome message styling */
        .stMarkdown h3 {
            background: linear-gradient(90deg, #4568dc, #6a3093);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Typing indicator animation */
        @keyframes typing-dot {
            0%, 20% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            80%, 100% { transform: translateY(0); }
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.7);
            margin: 0 2px;
        }
        
        .typing-indicator span:nth-child(1) {
            animation: typing-dot 1s infinite 0s;
        }
        
        .typing-indicator span:nth-child(2) {
            animation: typing-dot 1s infinite 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation: typing-dot 1s infinite 0.4s;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize knowledge collections directory
def ensure_collections_directory():
    os.makedirs(KNOWLEDGE_COLLECTIONS_DIR, exist_ok=True)
    
    # Create index file if it doesn't exist
    if not os.path.exists(COLLECTIONS_INDEX_FILE):
        with open(COLLECTIONS_INDEX_FILE, 'w') as f:
            json.dump({"collections": []}, f)

# Initialize session state with default values
def init_session_state():
    defaults = {
        'chat_history': [],
        'youtube_url': "",
        'retriever': None,
        'messages': [],
        'current_view': "chat",  # Default to chat view
        'active_source': None,
        'knowledge_cache': {},  # Cache of detected knowledge sources
        'last_cache_update': None,  # Timestamp of last cache update
        'sidebar_view': "chat",  # Current sidebar selection
        'editing_source': None,  # Source currently being edited
        'collection_sources': {}  # Mapping of collection ID to source files
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # If no active source is selected, try to set a default one
    if st.session_state.active_source is None:
        sources = scan_knowledge_sources()
        if sources:
            # Get the first source from the list
            source = sources[0]
            # Initialize the retriever for this source
            st.session_state.retriever = initialize_source_retriever(source)
            st.session_state.active_source = source
            
            # Add a welcome message if none exists
            if not st.session_state.messages:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Hello! I've analyzed the content from {source['name']}. What would you like to know about it?"
                })

# Function to display a message in the chat
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Function to validate URLs
def is_valid_url(url: str, url_type: str = "youtube") -> bool:
    if url_type == "youtube":
        return "youtube.com" in url or "youtu.be" in url
    return False

# Function to extract playlist or channel ID from YouTube URL
def extract_youtube_id(url: str) -> str:
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
    return f"youtube_{uuid.uuid4().hex[:8]}"

# Function to get file preview
def get_file_preview(file_path: str, max_length: int = 200) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(max_length)
            if os.path.getsize(file_path) > max_length:
                content += "..."
            return content
    except Exception:
        return "Content preview unavailable"

# Function to detect and generate source ID
def generate_source_id(source_type: str, file_path: str) -> str:
    filename = os.path.basename(file_path)
    file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
    return f"{source_type}_{filename}_{file_hash}"

# Function to auto-detect knowledge source type
def detect_source_type(file_path: str) -> str:
    filename = os.path.basename(file_path).lower()
    
    # Check parent directory
    parent_dir = os.path.basename(os.path.dirname(file_path))
    
    for source_type, config in SOURCE_TYPES.items():
        # Check if it's a collection
        if parent_dir == os.path.basename(KNOWLEDGE_COLLECTIONS_DIR):
            return "collection"
        
        # Check by directory
        if config.get("directory") and os.path.normpath(config["directory"]) in os.path.normpath(file_path):
            return source_type
            
        # Check by extension
        for ext in config.get("file_extensions", []):
            if filename.endswith(ext):
                return source_type
    
    # Default to generic text if no match
    return "text"

# Load collection information from index file
def get_collections_info() -> Dict[str, Any]:
    if os.path.exists(COLLECTIONS_INDEX_FILE):
        try:
            with open(COLLECTIONS_INDEX_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"collections": []}
    return {"collections": []}

# Save collection information to index file
def save_collections_info(collections_data: Dict[str, Any]) -> None:
    with open(COLLECTIONS_INDEX_FILE, 'w') as f:
        json.dump(collections_data, f, indent=2)

# Create a new knowledge collection
def create_knowledge_collection(name: str, description: str, source_files: List[str]) -> Dict[str, Any]:
    # Ensure directories exist
    ensure_collections_directory()
    
    # Generate a unique ID for the collection
    collection_id = f"collection_{uuid.uuid4().hex[:8]}"
    collection_dir = os.path.join(KNOWLEDGE_COLLECTIONS_DIR, collection_id)
    os.makedirs(collection_dir, exist_ok=True)
    
    # Generate a combined file with all content
    combined_path = os.path.join(collection_dir, f"{collection_id}.txt")
    
    with open(combined_path, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# {name}\n\n")
        outfile.write(f"Description: {description}\n\n")
        
        # Copy all source files into the collection
        for src_path in source_files:
            if os.path.exists(src_path):
                filename = os.path.basename(src_path)
                outfile.write(f"## Source: {filename}\n\n")
                
                try:
                    with open(src_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        outfile.write("\n\n")
                except Exception as e:
                    outfile.write(f"[Error reading content: {str(e)}]\n\n")
    
    # Create collection metadata
    collection_data = {
        "id": collection_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "source_files": source_files,
        "combined_file": combined_path
    }
    
    # Update collections index
    collections_info = get_collections_info()
    collections_info["collections"].append(collection_data)
    save_collections_info(collections_info)
    
    return collection_data

# Delete a knowledge collection
def delete_knowledge_collection(collection_id: str) -> bool:
    # Load collections data
    collections_info = get_collections_info()
    
    # Find the collection by ID
    updated_collections = []
    deleted = False
    
    for collection in collections_info["collections"]:
        if collection["id"] == collection_id:
            # Delete the collection directory
            collection_dir = os.path.dirname(collection["combined_file"])
            if os.path.exists(collection_dir):
                try:
                    shutil.rmtree(collection_dir)
                    deleted = True
                except Exception as e:
                    st.error(f"Failed to delete collection directory: {str(e)}")
                    return False
        else:
            updated_collections.append(collection)
    
    if deleted:
        # Update the index file
        collections_info["collections"] = updated_collections
        save_collections_info(collections_info)
        return True
    
    return False

# Update a knowledge collection's name or description
def update_knowledge_collection(collection_id: str, name: str = None, description: str = None) -> bool:
    # Load collections data
    collections_info = get_collections_info()
    
    # Find the collection by ID
    for i, collection in enumerate(collections_info["collections"]):
        if collection["id"] == collection_id:
            # Update fields
            if name is not None:
                collections_info["collections"][i]["name"] = name
            if description is not None:
                collections_info["collections"][i]["description"] = description
            
            collections_info["collections"][i]["updated_at"] = datetime.now().isoformat()
            
            # Save updated data
            save_collections_info(collections_info)
            
            # Update the combined file to reflect changes
            combined_path = collection["combined_file"]
            if os.path.exists(combined_path):
                # Read existing content after the description
                try:
                    with open(combined_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Find the position after the description
                        desc_pos = content.find("Description:")
                        if desc_pos >= 0:
                            next_section = content.find("##", desc_pos)
                            if next_section >= 0:
                                after_desc_content = content[next_section:]
                            else:
                                after_desc_content = ""
                        else:
                            after_desc_content = content
                    
                    # Write updated header
                    with open(combined_path, 'w', encoding='utf-8') as f:
                        current_name = name or collection["name"]
                        current_desc = description or collection["description"]
                        f.write(f"# {current_name}\n\n")
                        f.write(f"Description: {current_desc}\n\n")
                        f.write(after_desc_content)
                except Exception as e:
                    st.error(f"Failed to update collection file: {str(e)}")
            
            return True
    
    return False

# Cache source scanning to reduce repeated filesystem operations
@st.cache_data(ttl=30, show_spinner=False)
# Function to scan for knowledge sources across all configured locations
def scan_knowledge_sources(force_refresh: bool = False) -> List[Dict[str, Any]]:
    # Use cached results if available and not forcing refresh
    current_time = datetime.now()
    if (not force_refresh and 
        st.session_state.last_cache_update and 
        (current_time - st.session_state.last_cache_update).total_seconds() < 30 and
        st.session_state.knowledge_cache):
        return st.session_state.knowledge_cache
    
    # Ensure collections directory exists
    ensure_collections_directory()
    
    sources = []
    scanned_paths = set()
    
    # First, add any collections
    collections_info = get_collections_info()
    for collection in collections_info["collections"]:
        if os.path.exists(collection["combined_file"]):
            source_id = collection["id"]
            sources.append({
                "id": source_id,
                "name": collection["name"],
                "description": collection.get("description", ""),
                "type": "collection",
                "icon": SOURCE_TYPES["collection"]["icon"],
                "path": collection["combined_file"],
                "size": os.path.getsize(collection["combined_file"]),
                "preview": get_file_preview(collection["combined_file"]),
                "last_modified": os.path.getmtime(collection["combined_file"]),
                "source_files": collection.get("source_files", []),
                "is_collection": True,
                "collection_id": collection["id"]
            })
            
            # Mark the combined file as already scanned
            scanned_paths.add(collection["combined_file"])
    
    # Scan all directories defined in SOURCE_TYPES
    for source_type, config in SOURCE_TYPES.items():
        dir_path = config.get("directory")
        if dir_path and os.path.exists(dir_path) and dir_path != KNOWLEDGE_COLLECTIONS_DIR:
            for ext in config.get("file_extensions", []):
                file_pattern = os.path.join(dir_path, f"*{ext}")
                for file_path in glob.glob(file_pattern):
                    # Skip files that are already part of collections
                    if file_path in scanned_paths:
                        continue
                    
                    # Skip duplicate files
                    if any(s["path"] == file_path for s in sources):
                        continue
                        
                    # Get source type
                    detected_type = detect_source_type(file_path)
                    type_config = SOURCE_TYPES.get(detected_type, SOURCE_TYPES.get("text", {}))
                    
                    # Create source metadata
                    source_id = generate_source_id(detected_type, file_path)
                    source_name = type_config.get("name_pattern", lambda f: os.path.basename(f))(file_path)
                    
                    sources.append({
                        "id": source_id,
                        "name": source_name,
                        "type": detected_type,
                        "icon": type_config.get("icon", "📝"),
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "preview": get_file_preview(file_path),
                        "last_modified": os.path.getmtime(file_path),
                        "is_collection": False
                    })
    
    # Sort by last modified date (newest first)
    sources.sort(key=lambda x: x.get("last_modified", 0), reverse=True)
    
    # Update cache
    st.session_state.knowledge_cache = sources
    st.session_state.last_cache_update = current_time
    
    return sources

# Delete all knowledge sources
def delete_all_knowledge_sources() -> bool:
    try:
        # Delete all collections first
        collections_info = get_collections_info()
        
        # Delete each collection directory
        for collection in collections_info["collections"]:
            collection_dir = os.path.dirname(collection["combined_file"])
            if os.path.exists(collection_dir):
                try:
                    shutil.rmtree(collection_dir)
                except Exception as e:
                    st.error(f"Failed to delete collection directory: {str(e)}")
        
        # Reset collections index
        save_collections_info({"collections": []})
        
        # Delete individual files in youtube directory
        if os.path.exists(YOUTUBE_DIR):
            for file in glob.glob(os.path.join(YOUTUBE_DIR, "*.txt")):
                try:
                    os.remove(file)
                except Exception as e:
                    st.error(f"Failed to delete file {file}: {str(e)}")
        
        # Delete files in document directory
        if os.path.exists(DOCUMENT_DIR):
            for file in glob.glob(os.path.join(DOCUMENT_DIR, "*.txt")):
                try:
                    os.remove(file)
                except Exception as e:
                    st.error(f"Failed to delete file {file}: {str(e)}")
        
        # Reset session state
        st.session_state.active_source = None
        st.session_state.retriever = None
        st.session_state.messages = []
        st.session_state.knowledge_cache = {}
        st.session_state.last_cache_update = None
        
        return True
    except Exception as e:
        st.error(f"Error deleting all knowledge sources: {str(e)}")
        return False

# Function to initialize a retriever for a specific source
def initialize_source_retriever(source: Dict[str, Any]) -> Optional[DocumentRetriever]:
    try:
        if not os.path.exists(source["path"]):
            return None
            
        documents = [{"id": source["id"], "text": open(source["path"], 'r', encoding='utf-8').read()}]
        
        # Process documents for embedding
        processed_docs = process_documents_for_embedding(documents)
        
        # Initialize retriever and add documents
        retriever = DocumentRetriever()
        retriever.add_documents(processed_docs)
        
        return retriever
    except Exception as e:
        st.error(f"Error initializing retriever: {str(e)}")
        return None

# Function to create and display a source card
def display_source_card(source: Dict[str, Any], container):
    with container:
        # Generate a unique key for this source
        unique_key = f"src_{source['id']}"
        
        # Format the file size nicely
        size_kb = round(source["size"]/1024, 1)
        size_display = f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 1)} MB"
        
        # Format the last modified date
        last_modified = datetime.fromtimestamp(source.get("last_modified", 0))
        time_display = last_modified.strftime("%b %d, 2023")
        
        # Get collection specific info
        is_collection = source.get("is_collection", False)
        collection_info = ""
        if is_collection and "source_files" in source:
            num_files = len(source["source_files"])
            file_names = [os.path.basename(f) for f in source["source_files"]]
            collection_info = f"""
            <div class="collection-items">
                <strong>{num_files} sources in this collection</strong><br>
            """
            for i, name in enumerate(file_names[:3]):  # Show first 3 files
                collection_info += f'<div class="collection-item">{name}</div>'
            if num_files > 3:
                collection_info += f'<div class="collection-item">+{num_files-3} more files...</div>'
            collection_info += "</div>"
        
        # Create the card HTML
        description = source.get("description", "")
        card_html = f"""
        <div class="source-card" onclick="parent.postMessage({{source: '{source["id"]}'}}, '*')">
            <div class="source-icon">{source["icon"]}</div>
            <div class="source-title">{source["name"]}</div>
            {f'<div style="font-size:12px;opacity:0.8;margin-top:5px">{description}</div>' if description else ''}
            <div class="source-preview">{source["preview"]}</div>
            {collection_info if is_collection else ''}
            <div class="source-info">{source["type"].capitalize()} • {size_display} • {time_display}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Add action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Chat", key=f"chat_{unique_key}", help="Chat with this knowledge source"):
                select_source_for_chat(source)
        
        with col2:
            if st.button("Rename", key=f"rename_{unique_key}", help="Rename this knowledge source"):
                st.session_state.editing_source = source
                st.session_state.sidebar_view = "edit"
                st.rerun()
        
        with col3:
            if st.button("Delete", key=f"delete_{unique_key}", help="Delete this knowledge source"):
                if delete_knowledge_source(source):
                    st.success(f"Deleted {source['name']}")
                    # Force refresh the source list
                    scan_knowledge_sources(force_refresh=True)
                    # If this was the active source, reset it
                    if st.session_state.active_source and st.session_state.active_source["id"] == source["id"]:
                        st.session_state.active_source = None
                        st.session_state.retriever = None
                    st.rerun()

# Function to delete a knowledge source
def delete_knowledge_source(source: Dict[str, Any]) -> bool:
    if source.get("is_collection", False):
        # Delete collection using collection ID
        return delete_knowledge_collection(source.get("collection_id", source["id"]))
    else:
        # For individual files, just delete the file
        try:
            if os.path.exists(source["path"]):
                os.remove(source["path"])
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
            return False

# Function to set up chat with a selected source
def select_source_for_chat(source: Dict[str, Any]):
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

# Function to ingest a new knowledge source with progress tracking
def ingest_knowledge_source(url: str, name: str, source_type: str = "youtube"):
    """Process a new knowledge source with progress tracking"""
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
            
            # Process videos (prepare document list)
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
        with st.expander("Delete All Knowledge Sources", expanded=False):
            st.warning("This action will permanently delete all knowledge sources and cannot be undone.")
            delete_all = st.button("Delete All Knowledge Sources", key="delete_all_sources", 
                              help="Permanently delete all knowledge sources")
            
            if delete_all:
                confirmation = st.text_input("Type 'DELETE' to confirm", key="confirm_delete",
                                         placeholder="DELETE")
                if confirmation == "DELETE" and st.button("Confirm Deletion", key="confirm_delete_btn"):
                    if delete_all_knowledge_sources():
                        st.success("All knowledge sources have been deleted.")
                        st.session_state.knowledge_cache = {}
                        st.session_state.last_cache_update = None
                        st.rerun()
                    else:
                        st.error("Failed to delete all knowledge sources.")
    
    if sources:
        # Create display grid - responsive columns
        num_cols = 3
        cols = st.columns(num_cols)
        
        # Display cards in the columns
        for i, source in enumerate(sources):
            col_idx = i % num_cols
            display_source_card(source, cols[col_idx])
    else:
        st.info("No knowledge sources found. Add a YouTube channel to get started!")

# Display add knowledge source form
def show_add_source_page():
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

# Display form to create a new collection from existing sources
def show_create_collection_page():
    st.markdown("## Create Knowledge Collection")
    st.markdown("Group multiple knowledge sources into a single collection for easier access")
    
    # Get all individual sources (non-collections)
    all_sources = scan_knowledge_sources()
    individual_sources = [s for s in all_sources if not s.get("is_collection", False)]
    
    if not individual_sources:
        st.warning("No individual knowledge sources found. Add some YouTube content or other sources first.")
        return
    
    # Collection name and description
    collection_name = st.text_input("Collection Name", key="new_collection_name", 
                                  placeholder="My Knowledge Collection")
    
    collection_desc = st.text_area("Collection Description", key="new_collection_desc", 
                                 placeholder="A description of what this collection contains...")
    
    # Source selector
    st.markdown("### Select Sources to Include")
    selected_sources = []
    
    # Display sources with checkboxes
    for source in individual_sources:
        source_key = f"select_{source['id']}"
        if st.checkbox(f"{source['icon']} {source['name']}", key=source_key):
            selected_sources.append(source)
    
    # Create button
    if st.button("Create Collection", disabled=len(selected_sources) == 0 or not collection_name):
        if len(selected_sources) > 0 and collection_name:
            # Extract file paths
            source_paths = [s["path"] for s in selected_sources]
            
            # Create the collection
            collection = create_knowledge_collection(
                name=collection_name,
                description=collection_desc,
                source_files=source_paths
            )
            
            st.success(f"Collection '{collection_name}' created successfully!")
            
            # Force refresh the source list
            sources = scan_knowledge_sources(force_refresh=True)
            
            # Find the new collection and select it
            collection_source = next((s for s in sources if s.get("collection_id") == collection["id"]), None)
            if collection_source:
                select_source_for_chat(collection_source)
            else:
                st.session_state.sidebar_view = "sources"
                st.rerun()
        else:
            if not collection_name:
                st.error("Please enter a name for the collection")
            else:
                st.error("Please select at least one source to include in the collection")

# Display edit interface for renaming sources
def show_edit_source_page():
    if not st.session_state.editing_source:
        st.error("No source selected for editing")
        if st.button("Back to Sources"):
            st.session_state.sidebar_view = "sources"
            st.rerun()
        return
    
    source = st.session_state.editing_source
    st.markdown(f"## Edit {source['type'].capitalize()}: {source['name']}")
    
    # Source name field
    new_name = st.text_input("Name", value=source['name'], key="edit_name")
    
    # Description field (for collections)
    new_description = None
    if source.get("is_collection", False):
        current_desc = source.get("description", "")
        new_description = st.text_area("Description", value=current_desc, key="edit_desc")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Save Changes"):
            if source.get("is_collection", False):
                # Update collection
                if update_knowledge_collection(source["collection_id"], new_name, new_description):
                    st.success("Collection updated successfully!")
                    # Force refresh sources
                    scan_knowledge_sources(force_refresh=True)
                    # Return to sources page
                    st.session_state.editing_source = None
                    st.session_state.sidebar_view = "sources"
                    st.rerun()
                else:
                    st.error("Failed to update collection")
            else:
                # For individual files, we would need a different approach
                # This is a placeholder for future implementation
                st.error("Renaming individual files is not yet implemented")
    
    with col2:
        if st.button("Cancel"):
            st.session_state.editing_source = None
            st.session_state.sidebar_view = "sources"
            st.rerun()

# Display chat interface for active knowledge source
def show_chat_interface():
    # Source info header if available
    if st.session_state.active_source:
        source = st.session_state.active_source
        st.markdown(
            f"<div style='margin-bottom:15px;'>Chatting with: "
            f"<b>{source['name']}</b> "
            f"<span style='opacity:0.7;'>({source['type']})</span>"
            f"</div>", 
            unsafe_allow_html=True
        )
    else:
        st.markdown("### Smart Knowledge Agent")
    
    # Chat history container
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown("""
        ### 👋 Hello there!
        
        I'm your Smart Agent. I've analyzed the available content.
        Feel free to ask me any questions about it.
        
        You can also add new content sources or browse existing ones using the sidebar.
        """)
    
    # Display existing messages
    for message in st.session_state.messages:
        role = message.get("role", "")
        content = message.get("content", "")
        
        if role == "user":
            st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{content}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area for new messages
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Create a form for user input to better handle submission
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Ask a question",
            key="user_input",
            placeholder="What would you like to know about this content?"
        )
        submit_button = st.form_submit_button("Send")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process user input when the form is submitted
    if submit_button and user_input:
        # Add user message to chat
        add_message("user", user_input)
        
        # Generate response
        with st.spinner("Thinking..."):
            if st.session_state.retriever:
                # Query for relevant documents
                relevant_chunks = st.session_state.retriever.query_documents(user_input, n_results=3)
                
                # Generate a response
                answer = generate_response(user_input, relevant_chunks)
                
                # Add assistant response to chat
                add_message("assistant", answer)
            else:
                add_message("assistant", "I don't have any knowledge sources loaded yet. Please add a YouTube channel or select an existing knowledge source from the sidebar.")
        
        # Force a rerun to update the UI
        st.rerun()

# Display available knowledge sources
def show_sources_page():
    st.markdown("## Knowledge Sources")
    st.markdown("Browse and manage your available knowledge sources")
    
    # Scan for sources
    sources = scan_knowledge_sources()
    
    # Add refresh button
    if st.button("Refresh Sources", key="refresh_sources"):
        sources = scan_knowledge_sources(force_refresh=True)
        st.success("Knowledge sources refreshed!")
    
    # Delete all sources option (hidden in expander)
    with st.expander("Delete All Knowledge Sources", expanded=False):
        st.warning("This action will permanently delete all knowledge sources and cannot be undone.")
        delete_all = st.button("Delete All Knowledge Sources", key="delete_all_sources", 
                          help="Permanently delete all knowledge sources")
        
        if delete_all:
            confirmation = st.text_input("Type 'DELETE' to confirm", key="confirm_delete",
                                     placeholder="DELETE")
            if confirmation == "DELETE" and st.button("Confirm Deletion", key="confirm_delete_btn"):
                if delete_all_knowledge_sources():
                    st.success("All knowledge sources have been deleted.")
                    st.session_state.knowledge_cache = {}
                    st.session_state.last_cache_update = None
                    st.rerun()
                else:
                    st.error("Failed to delete all knowledge sources.")
    
    if sources:
        # Create display grid - responsive columns
        num_cols = 3
        cols = st.columns(num_cols)
        
        # Display cards in the columns
        for i, source in enumerate(sources):
            col_idx = i % num_cols
            display_source_card(source, cols[col_idx])
    else:
        st.info("No knowledge sources found. Add a YouTube channel to get started!")

# Show sidebar navigation
def show_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Smart Knowledge Agent</div>', unsafe_allow_html=True)
        
        # Navigation items
        nav_items = [
            {"id": "chat", "icon": "💬", "label": "Chat"},
            {"id": "sources", "icon": "📚", "label": "Knowledge Sources"},
            {"id": "add", "icon": "➕", "label": "Add YouTube Content"},
            {"id": "create_collection", "icon": "🔄", "label": "Create Collection"}
        ]
        
        # Display navigation items
        for item in nav_items:
            is_active = st.session_state.sidebar_view == item["id"]
            active_class = "selected-source" if is_active else ""
            
            # Create a container for each nav item
            clicked = st.button(
                f"{item['icon']} {item['label']}", 
                key=f"nav_{item['id']}",
                use_container_width=True,
                help=f"Go to {item['label']}"
            )
            
            if clicked:
                # If editing, clear editing state
                if st.session_state.sidebar_view == "edit":
                    st.session_state.editing_source = None
                
                # Update current view
                st.session_state.sidebar_view = item["id"]
                st.rerun()
        
        # Display active source info if available
        if st.session_state.active_source:
            source = st.session_state.active_source
            st.markdown("---")
            st.markdown(f"**Active Source:**")
            st.markdown(f"{source['icon']} {source['name']}")
            
            if st.button("Clear Source", key="clear_source"):
                st.session_state.active_source = None
                st.session_state.retriever = None
                st.session_state.messages = []
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown("Made with ❤️ by RAG-Intro Team")

# Main app layout and logic
def main():
    # Ensure knowledge collections directory exists
    ensure_collections_directory()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Show the sidebar
    show_sidebar()
    
    # Determine which view to show based on sidebar selection
    if st.session_state.sidebar_view == "chat":
        show_chat_interface()
    elif st.session_state.sidebar_view == "sources":
        show_sources_page()
    elif st.session_state.sidebar_view == "add":
        show_add_source_page()
    elif st.session_state.sidebar_view == "create_collection":
        show_create_collection_page()
    elif st.session_state.sidebar_view == "edit":
        show_edit_source_page()

# Run the main function
if __name__ == "__main__":
    main()