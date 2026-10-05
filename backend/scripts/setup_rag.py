import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.config import settings

print("="*70)
print("RAG SETUP - ONE-TIME DOCUMENT PROCESSING")
print("="*70)

# Load and chunk documents
processor = DocumentProcessor(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

doc_files = [
    str(settings.DATA_DIR / "unica_overview.txt"),
    str(settings.DATA_DIR / "unica_best_practices.txt")
]

print("\n[STEP 1] Loading documents...")
documents = processor.load_documents(doc_files)

print("\n[STEP 2] Chunking documents...")
chunks = processor.chunk_documents(documents)

# Create embeddings
print("\n[STEP 3] Creating embeddings and vector store...")
embedding_store = EmbeddingStore()
embedding_store.create_vectorstore(chunks)

# Save to disk
print("\n[STEP 4] Saving FAISS index...")
embedding_store.save_vectorstore(str(settings.FAISS_INDEX_PATH))

print("\n✓ Setup complete! Index saved to", str(settings.FAISS_INDEX_PATH))
print("\nNext steps:")
print("  1. Start backend: python backend/run.py")
print("  2. Start frontend: cd frontend && npm start")
print("  3. Use the RAG system with the saved FAISS index at", str(settings.FAISS_INDEX_PATH))