"""
Main application module that ties together all components of the RAG system.
"""
import os
from typing import List, Dict

from config.config import DOCUMENT_DIR, YOUTUBE_DIR
from src.data_ingestion.youtube import ingest_channel_videos
from src.embedding.embeddings import process_documents_for_embedding
from src.retrieval.document_store import DocumentRetriever, load_documents_from_directory
from src.retrieval.response_generator import generate_response
from src.ui.display import display_qa_results

import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Gemini API key from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")

# Configure the Gemini API
genai.configure(api_key=google_api_key)

# Embedding model for Gemini
embedding_model = "models/text-embedding-004"
# Chat model for Gemini
chat_model = genai.GenerativeModel("models/gemini-1.5-flash")

# Function to generate embeddings using Gemini API
def get_gemini_embedding(text):
    response = genai.embed_content(
        model=embedding_model,
        content=text,
        task_type="RETRIEVAL_DOCUMENT"
    )
    embedding = response["embedding"]
    print("==== Generating embeddings... ====")
    return embedding

# Initialize the Chroma client with persistence
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(name=collection_name)

# Function to split text into chunks
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

def initialize_document_store():
    """
    Initialize the document store with documents from the specified directories.
    """
    # Create the document retriever
    retriever = DocumentRetriever()
    
    # Load documents from the news articles directory
    if os.path.exists(DOCUMENT_DIR):
        print(f"Loading documents from {DOCUMENT_DIR}")
        documents = load_documents_from_directory(DOCUMENT_DIR)
        print(f"Loaded {len(documents)} documents")
        
        # Process documents for embedding
        processed_docs = process_documents_for_embedding(documents)
        
        # Add documents to the retriever
        retriever.add_documents(processed_docs)
    
    # Load documents from the YouTube transcripts directory if it exists
    if os.path.exists(YOUTUBE_DIR):
        print(f"Loading YouTube transcripts from {YOUTUBE_DIR}")
        youtube_docs = load_documents_from_directory(YOUTUBE_DIR)
        print(f"Loaded {len(youtube_docs)} YouTube transcripts")
        
        # Process YouTube documents for embedding
        processed_youtube_docs = process_documents_for_embedding(youtube_docs)
        
        # Add YouTube documents to the retriever
        retriever.add_documents(processed_youtube_docs)
    
    return retriever

def ingest_youtube_channel(channel_url: str):
    """
    Ingest videos from a YouTube channel.
    
    Args:
        channel_url: URL of the YouTube channel
    """
    # Create the YouTube directory if it doesn't exist
    os.makedirs(YOUTUBE_DIR, exist_ok=True)
    
    # Ingest videos from the channel
    videos = ingest_channel_videos(channel_url, YOUTUBE_DIR)
    
    print(f"Ingested {len(videos)} videos from {channel_url}")
    
    # After ingestion, reinitialize the document store
    initialize_document_store()

def ask_question(question: str, n_results: int = 2):
    """
    Ask a question and get a response.
    
    Args:
        question: The question to ask
        n_results: Number of relevant chunks to retrieve
    """
    # Create the document retriever
    retriever = DocumentRetriever()
    
    # Query for relevant documents
    relevant_chunks = retriever.query_documents(question, n_results=n_results)
    
    # Generate a response
    answer = generate_response(question, relevant_chunks)
    
    # Display the results
    display_qa_results(question, answer, relevant_chunks)
    
    return answer, relevant_chunks

if __name__ == "__main__":
    # Example usage
    # Initialize the document store
    initialize_document_store()
    
    # Ask a question
    question = "What role do machine learning and AI play in Pando's fulfillment management platform?"
    ask_question(question)