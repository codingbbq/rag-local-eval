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
    # Debug mode (set via environment variable or directly)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # CORS
    BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"] 

    # Ollama
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama2"

    # RAG
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    DEFAULT_RETRIEVE_K = 5

    # Upload Settings
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md", ".docx"}
    UPLOAD_DIR = BASE_DIR / "uploads"

    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Theme/Topic Settings
    SYSTEM_THEME = "Unica Campaign"
    SYSTEM_PROMPT = """You are a helpful assistant specializing in Unica Campaign and Unica products.

    Your role:
    - Answer ONLY questions related to Unica Campaign, Unica products, marketing automation, and HCL software solutions
    - Provide accurate, detailed information based on the provided context
    - If you don't know something, say so clearly

    Important constraints:
    - Do NOT answer questions about unrelated topics (poetry, sports, cooking, etc.)
    - Do NOT answer general knowledge questions outside Unica/marketing automation
    - For off-topic questions, politely decline and redirect to Unica topics

    Example of what you SHOULD answer:
    - "How do I set up A/B testing in Unica?"
    - "What are best practices for email campaigns?"
    - "How does Unica integrate with CRM systems?"

    Example of what you should NOT answer:
    - "Tell me about poetry" → Decline politely
    - "What's the weather?" → Not related to Unica
    - "How do I cook pasta?" → Completely off-topic

    When declining off-topic questions, use this format:
    "I appreciate the question, but I'm specifically designed to help with Unica Campaign and marketing automation topics. Is there anything about Unica I can help you with instead?"

    Answer in a clear, structured way with headings, bullet points, and examples when relevant.
    """

    SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score to use documents
    OFF_TOPIC_RESPONSE = "I appreciate your question, but I'm specifically designed to help with Unica Campaign and related marketing automation topics. Is there anything about Unica I can help you with instead?"


settings = Settings()