"""
UI components for the RAG application.

This module will be expanded in the future to include a Streamlit interface.
"""
from typing import List, Dict, Any

# Placeholder for future Streamlit UI
def display_qa_results(question: str, answer: str, sources: List[str] = None):
    """
    Display the question, answer, and sources (placeholder for future UI).
    
    Args:
        question: The question that was asked
        answer: The generated answer
        sources: List of source documents used to generate the answer
    """
    print("\n" + "=" * 50)
    print(f"Question: {question}")
    print("-" * 50)
    print(f"Answer: {answer}")
    
    if sources:
        print("-" * 50)
        print("Sources:")
        for i, source in enumerate(sources):
            # Print a preview of each source
            preview = source[:100] + "..." if len(source) > 100 else source
            print(f"{i+1}. {preview}")
    print("=" * 50)