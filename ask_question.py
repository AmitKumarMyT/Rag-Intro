"""
Command line interface for asking questions to the RAG system.
"""
from app import ask_question

if __name__ == "__main__":
    question = input("Enter your question: ")
    if not question:
        # Use default question for testing
        question = "What role do machine learning and AI play in Pando's fulfillment management platform?"
        
    ask_question(question, n_results=2)
