"""
Main Streamlit application for the Smart Knowledge Agent
"""
import streamlit as st
import os
import json
import re
import glob
import uuid
import hashlib
import shutil
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Import from components
from src.ui.components.styles import apply_custom_css
from src.ui.components.sidebar import show_sidebar
from src.ui.components.chat_interface import show_chat_interface
from src.ui.components.sources_manager import show_sources_page, show_edit_source_page
from src.ui.components.youtube_ingestion import show_add_source_page
from src.ui.components.collection_manager import show_create_collection_page

# Import utilities
from src.ui.utils.session_state import init_session_state
from src.ui.utils.source_utils import ensure_collections_directory

# Set up project paths
from config.config import YOUTUBE_DIR, DOCUMENT_DIR

# Set page configuration
st.set_page_config(
    page_title="Smart Knowledge Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
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
