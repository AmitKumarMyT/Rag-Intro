import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = "models/text-embedding-004"
CHAT_MODEL = "models/gemini-1.5-flash"
CHROMA_PERSIST_DIR = "chroma_persistent_storage"
COLLECTION_NAME = "document_qa_collection"
DOCUMENT_DIR = "./news_articles"
YOUTUBE_DIR = "./youtube_transcripts"