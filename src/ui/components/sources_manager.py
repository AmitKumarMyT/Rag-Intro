"""
Knowledge sources management component
"""
import os
import streamlit as st
from datetime import datetime
from typing import Dict, Any

from src.ui.utils.source_utils import scan_knowledge_sources, delete_all_knowledge_sources, delete_knowledge_source, update_knowledge_collection
from src.ui.components.youtube_ingestion import select_source_for_chat

def display_source_card(source: Dict[str, Any], container):
    """
    Create and display a source card
    
    Args:
        source: Source metadata to display
        container: Streamlit container to render the card in
    """
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

def show_sources_page():
    """
    Display available knowledge sources
    """
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

def show_edit_source_page():
    """
    Display edit interface for renaming sources
    """
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
