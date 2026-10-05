import os
from pathlib import Path

class Settings:
    """Application Settings"""

    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    FAISS_INDEX_PATH = DATA_DIR / "faiss_index"

    # API
    API_V1_PREFIX = "/api/v1"
    PROJECT_NAME = "RAG Chat API"
    DEBUG = True

    # CORS
    BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"] 

    # Ollama
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama2"

    # RAG

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    RETRIEVE_K = 5


settings = Settings()