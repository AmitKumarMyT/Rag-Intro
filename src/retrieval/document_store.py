import os
import chromadb
from typing import List, Dict, Any

from config.config import CHROMA_PERSIST_DIR, COLLECTION_NAME
from src.embedding.embeddings import get_gemini_embedding


class DocumentRetriever:
    """Class for storing and retrieving documents from a vector database"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents with embeddings to ChromaDB.
        
        Args:
            documents: List of document dictionaries with 'id', 'text', and 'embedding' keys
        """
        for doc in documents:
            self.collection.upsert(
                ids=[doc["id"]], 
                documents=[doc["text"]], 
                embeddings=[doc["embedding"]]
            )
    
    def query_documents(self, question: str, n_results: int = 2) -> List[str]:
        """
        Query documents based on a question.
        
        Args:
            question: Question to search for
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        # Generate the query embedding
        query_embedding = get_gemini_embedding(question)
        
        # Query the collection using the embedding
        results = self.collection.query(
            query_embeddings=[query_embedding], 
            n_results=n_results
        )
        
        # Extract the relevant chunks
        relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
        return relevant_chunks


def load_documents_from_directory(directory_path: str) -> List[Dict[str, str]]:
    """
    Load documents from a directory of text files.
    
    Args:
        directory_path: Path to directory containing text files
        
    Returns:
        List of document dictionaries with 'id' and 'text' keys
    """
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            with open(os.path.join(directory_path, filename), "r", encoding="utf-8") as file:
                documents.append({"id": filename, "text": file.read()})
    return documents