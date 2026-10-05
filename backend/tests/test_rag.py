import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.core.rag_chain import RAGChain
from app.core.instrumentation import RAGInstrument
from app.config import settings

print("="*70)
print("SETTING UP RAG PIPELINE")
print("="*70)

# Step 1: Load and chunk documents
print("\n[1/5] Loading documents...")
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = [str(settings.DATA_DIR / "unica_overview.txt"), str(settings.DATA_DIR / "unica_best_practices.txt")]
documents = processor.load_documents(files)

# Step 2: Create embeddings
print("\n[2/5] Creating embeddings...")
store = EmbeddingStore()
store.create_vectorstore(processor.chunk_documents(documents))

# Step 3: Create retriever
print("\n[3/5] Creating retriever...")
retriever = store.get_retriever(k=5)

# Step 4: Initialize instrumentation
print("\n[4/5] Initializing logging...")
instrument = RAGInstrument("rag_logs.json")

# Step 5: Create RAG chain
print("\n[5/5] Creating RAG chain...")
rag_chain = RAGChain(retriever, instrument)

# Test query
print("\n" + "="*70)
print("TESTING RAG PIPELINE")
print("="*70)

test_query = "What are the key features of Unica Campaign?"
result = rag_chain.generate_answer(test_query, top_k=5)

# Save logs
print("\n[FINAL] Saving logs...")
instrument.save()
instrument.summary()

print("\n✓ RAG Pipeline test completed!")