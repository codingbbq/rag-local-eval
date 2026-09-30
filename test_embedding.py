from document_processor import DocumentProcessor
from embedding_store import EmbeddingStore

# Step 1: Load and chunk documents
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = ["unica_overview.txt", "unica_best_practices.txt"]
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