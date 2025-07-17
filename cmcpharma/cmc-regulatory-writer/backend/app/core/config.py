import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()

class Settings:
    """Loads settings from environment variables."""
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # GraphRAG Configuration
    USE_GRAPH_RAG: bool = os.getenv("USE_GRAPH_RAG", "false").lower() == "true"
    GRAPH_RAG_WORKING_DIR: str = os.getenv("GRAPH_RAG_WORKING_DIR", "./rag_storage")
    GRAPH_RAG_CHUNK_SIZE: int = int(os.getenv("GRAPH_RAG_CHUNK_SIZE", "1200"))
    GRAPH_RAG_CHUNK_OVERLAP: int = int(os.getenv("GRAPH_RAG_CHUNK_OVERLAP", "200"))
    GRAPH_RAG_EMBEDDING_BATCH_NUM: int = int(os.getenv("GRAPH_RAG_EMBEDDING_BATCH_NUM", "32"))
    GRAPH_RAG_MAX_ASYNC: int = int(os.getenv("GRAPH_RAG_MAX_ASYNC", "16"))
    GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY: int = int(os.getenv("GRAPH_RAG_GLOBAL_MAX_CONSIDER_COMMUNITY", "512"))
    GRAPH_RAG_LOCAL_SEARCH_TOP_K: int = int(os.getenv("GRAPH_RAG_LOCAL_SEARCH_TOP_K", "20"))

settings = Settings()
