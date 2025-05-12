"""
Sidebar navigation component for the Smart Knowledge Agent
"""
import streamlit as st

def show_sidebar():
    """
    Display the sidebar navigation menu
    """
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
