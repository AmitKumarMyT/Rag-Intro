"""
Collection management component
"""
import streamlit as st
from typing import List, Dict, Any

from src.ui.utils.source_utils import scan_knowledge_sources, create_knowledge_collection
from src.ui.components.youtube_ingestion import select_source_for_chat

def show_create_collection_page():
    """
    Display form to create a new collection from existing sources
    """
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
