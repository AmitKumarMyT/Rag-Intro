"""
Document retrieval functionality
"""
import os
import streamlit as st
from typing import Dict, Any, Optional

from src.retrieval.document_store import DocumentRetriever
from src.embedding.embeddings import process_documents_for_embedding

def initialize_source_retriever(source: Dict[str, Any]) -> Optional[DocumentRetriever]:
    """
    Initialize a retriever for a specific source
    
    Args:
        source: Source metadata
        
    Returns:
        DocumentRetriever instance or None if initialization fails
    """
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
