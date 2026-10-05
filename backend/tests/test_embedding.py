import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.config import settings

# Step 1: Load and chunk documents
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = [str(settings.DATA_DIR / "unica_overview.txt"), str(settings.DATA_DIR / "unica_best_practices.txt")]
documents = processor.load_documents(files)
chunks = processor.chunk_documents(documents)

# Step 2: Create embeddings and vector store
store = EmbeddingStore()
store.create_vectorstore(chunks)

# Step 3: Get retriever
retriever = store.get_retriever(k=5)

# Step 4: Test retrieval
test_query = "What are the key features of Unica Campaign?"
results = store.test_retrieval(retriever, test_query)

if results:
    print("\n✓ Embedding and retrieval working!")
else:
    print("\n❌ Retrieval failed or returned no results.")