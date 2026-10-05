import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
    
from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.config import settings
import numpy as np

# Setup
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = [str(settings.DATA_DIR / "unica_overview.txt"), str(settings.DATA_DIR / "unica_best_practices.txt")]
documents = processor.load_documents(files)
chunks = processor.chunk_documents(documents)

store = EmbeddingStore()
store.create_vectorstore(chunks)

# Now inspect the FAISS index
print("\n" + "="*70)
print("FAISS INDEX INSPECTION")
print("="*70)

vectorstore = store.vectorstore

# 1. How many vectors are stored?
num_vectors = vectorstore.index.ntotal
print(f"\n📊 Total vectors in FAISS: {num_vectors}")

# 2. Vector dimensions
vector_dim = vectorstore.index.d
print(f"📏 Vector dimensions: {vector_dim}")

# 3. Inspect first few vectors
print(f"\n📈 First 3 vectors:")
for i in range(min(3, num_vectors)):
    vector = vectorstore.index.reconstruct(i)
    print(f"\n   Vector {i}:")
    print(f"      Dimensions: {len(vector)}")
    print(f"      First 5 values: {vector[:5]}")
    print(f"      Vector norm: {np.linalg.norm(vector):.3f}")

# 4. Check metadata
print(f"\n📝 Metadata for each vector:")
if hasattr(vectorstore, 'docstore'):
    docs = vectorstore.docstore._dict
    for doc_id, doc in list(docs.items())[:3]:
        print(f"\n   Doc {doc_id}:")
        print(f"      Content: {doc.page_content[:100]}...")

# 5. Show chunk info
print(f"\n📚 Chunks in vector store:")
all_docs = vectorstore.docstore._dict
for idx, (key, doc) in enumerate(list(all_docs.items())[:5]):
    print(f"\n   [{idx}] {key}")
    print(f"       Length: {len(doc.page_content)} chars")
    print(f"       Preview: {doc.page_content[:80]}...")