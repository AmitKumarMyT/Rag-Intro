"""
Source detection and management utilities
"""
import os
import glob
import json
import shutil
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.ui.utils.file_utils import get_file_preview, generate_source_id
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

def ensure_collections_directory():
    """
    Initialize knowledge collections directory structure
    """
    os.makedirs(KNOWLEDGE_COLLECTIONS_DIR, exist_ok=True)
    
    # Create index file if it doesn't exist
    if not os.path.exists(COLLECTIONS_INDEX_FILE):
        with open(COLLECTIONS_INDEX_FILE, 'w') as f:
            json.dump({"collections": []}, f)

def detect_source_type(file_path: str) -> str:
    """
    Auto-detect knowledge source type based on file path
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected source type
    """
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

def get_collections_info() -> Dict[str, Any]:
    """
    Load collection information from index file
    
    Returns:
        Dictionary with collections data
    """
    if os.path.exists(COLLECTIONS_INDEX_FILE):
        try:
            with open(COLLECTIONS_INDEX_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"collections": []}
    return {"collections": []}

def save_collections_info(collections_data: Dict[str, Any]) -> None:
    """
    Save collection information to index file
    
    Args:
        collections_data: Collections data to save
    """
    with open(COLLECTIONS_INDEX_FILE, 'w') as f:
        json.dump(collections_data, f, indent=2)

@st.cache_data(ttl=30, show_spinner=False)
def scan_knowledge_sources(force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Scan for knowledge sources across all configured locations
    
    Args:
        force_refresh: Whether to force a refresh of the cache
        
    Returns:
        List of discovered knowledge sources
    """
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

def delete_all_knowledge_sources() -> bool:
    """
    Delete all knowledge sources
    
    Returns:
        Boolean indicating success
    """
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

def delete_knowledge_source(source: Dict[str, Any]) -> bool:
    """
    Delete a specific knowledge source
    
    Args:
        source: Source metadata to delete
        
    Returns:
        Boolean indicating success
    """
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

def delete_knowledge_collection(collection_id: str) -> bool:
    """
    Delete a knowledge collection
    
    Args:
        collection_id: ID of the collection to delete
        
    Returns:
        Boolean indicating success
    """
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

def update_knowledge_collection(collection_id: str, name: str = None, description: str = None) -> bool:
    """
    Update a knowledge collection's metadata
    
    Args:
        collection_id: ID of the collection to update
        name: New name for the collection
        description: New description for the collection
        
    Returns:
        Boolean indicating success
    """
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

def create_knowledge_collection(name: str, description: str, source_files: List[str]) -> Dict[str, Any]:
    """
    Create a new knowledge collection
    
    Args:
        name: Name of the collection
        description: Description of the collection
        source_files: List of source file paths to include
        
    Returns:
        Dictionary with collection metadata
    """
    # Ensure directories exist
    ensure_collections_directory()
    
    # Generate a unique ID for the collection
    import uuid
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
