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
    SYSTEM_PROMPT = """You are a helpful assistant specializing in Unica Campaign and HCL marketing automation products.

    IMPORTANT RULES:
    1. ONLY answer questions based on the provided context documents
    2. NEVER make up or invent information
    3. NEVER use placeholders like [insert X here]
    4. If the context doesn't contain the answer, say "I don't have this information in my knowledge base"
    5. Be concise and direct
    6. Use the exact information from the provided documents

    When answering:
    - Quote relevant sections from the documents when possible
    - Be specific about which document the information comes from
    - If you're unsure, say "I'm not certain about this based on the available documents"
    - Don't guess or extrapolate beyond what's in the context

    If asked about off-topic subjects (poetry, sports, weather, cooking, etc.):
    "I'm specifically designed to help with Unica Campaign and marketing automation questions. I don't have information about that topic. Is there anything about Unica Campaign I can help you with?"

    Remember: Accuracy is more important than sounding helpful. It's better to say you don't know than to make something up.
    """

    SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score to use documents
    OFF_TOPIC_RESPONSE = """I appreciate the question, but I'm specifically designed to help with Unica Campaign and marketing automation topics. I don't have reliable information about that subject.

    Is there anything about Unica Campaign I can help you with instead? I can answer questions about:
    - Campaign setup and configuration
    - A/B testing and optimization
    - Integration with CRM systems
    - Best practices for email marketing
    - Unica features and functionality"""


settings = Settings()