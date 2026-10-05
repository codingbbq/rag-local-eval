from document_processor import DocumentProcessor
from embedding_store import EmbeddingStore

print("="*70)
print("RAG SETUP - ONE-TIME DOCUMENT PROCESSING")
print("="*70)

# Load and chunk documents
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = ["unica_overview.txt", "unica_best_practices.txt"]
documents = processor.load_documents(files)
chunks = processor.chunk_documents(documents)

# Create embeddings
store = EmbeddingStore()
store.create_vectorstore(chunks)

# Save to disk (important!)
store.save_vectorstore("faiss_index")

print("\n✓ Setup complete! Index saved to faiss_index/")
print("\nNext time, you can just load it:")
print("  store = EmbeddingStore()")
print("  store.load_vectorstore('faiss_index')")