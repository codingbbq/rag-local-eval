from embedding_store import EmbeddingStore

print("="*70)
print("TESTING FAISS LOAD")
print("="*70)

# Create store
store = EmbeddingStore()

# Load from disk
success = store.load_vectorstore("faiss_index")

if success:
    # Get retriever
    retriever = store.get_retriever(k=5)
    
    # Test query
    query = "What are the key features?"
    print(f"\nTesting query: {query}")
    results = retriever.invoke(query)
    
    print(f"\nRetrieved {len(results)} documents:")
    for i, doc in enumerate(results, 1):
        print(f"\n[{i}] {doc.page_content[:150]}...")
    
    print("\n✓ Load test successful!")
else:
    print("\n❌ Load failed")