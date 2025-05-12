"""
Session state and initialization related utilities
"""
import streamlit as st
from datetime import datetime
from src.ui.utils.source_utils import scan_knowledge_sources
from src.ui.models.retriever import initialize_source_retriever

def init_session_state():
    """Initialize session state with default values"""
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
        'collection_sources': {},  # Mapping of collection ID to source files
        'streaming': False,  # Flag to indicate if we're currently streaming a response
        'stream_container': None  # Container for streaming text
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

def add_message(role, content):
    """Add a message to the chat history with timestamp"""
    from datetime import datetime
    st.session_state.messages.append({
        "role": role, 
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
