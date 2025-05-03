import google.generativeai as genai
from typing import List, Dict, Any

from config.config import GOOGLE_API_KEY, EMBEDDING_MODEL


# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)


def get_gemini_embedding(text: str) -> List[float]:
    """
    Generate embeddings for text using Gemini API.
    
    Args:
        text: The text to generate embeddings for
        
    Returns:
        List of embedding values
    """
    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    embedding = response["embedding"]
    return embedding


def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 20) -> List[str]:
    """
    Split text into chunks of specified size with overlap.
    
    Args:
        text: Text to split
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def process_documents_for_embedding(documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Process documents by splitting them into chunks and generating embeddings.
    
    Args:
        documents: List of document dictionaries with 'id' and 'text' keys
        
    Returns:
        List of chunked documents with embeddings
    """
    chunked_documents = []
    
    # Split documents into chunks
    for doc in documents:
        chunks = split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_documents.append({
                "id": f"{doc['id']}_chunk{i+1}", 
                "text": chunk
            })
    
    # Generate embeddings for the document chunks
    for doc in chunked_documents:
        doc["embedding"] = get_gemini_embedding(doc["text"])
        
    return chunked_documents