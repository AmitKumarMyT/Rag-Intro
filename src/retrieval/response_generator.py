import google.generativeai as genai
from typing import List

from config.config import GOOGLE_API_KEY, CHAT_MODEL


# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(CHAT_MODEL)


def generate_response(question: str, relevant_chunks: List[str]) -> str:
    """
    Generate a response to a question using retrieved context chunks.
    
    Args:
        question: The question to answer
        relevant_chunks: List of relevant text chunks for context
        
    Returns:
        Generated answer as a string
    """
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = model.generate_content(prompt)
    answer = response.text.strip()
    return answer