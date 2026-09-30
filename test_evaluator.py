from document_processor import DocumentProcessor
from embedding_store import EmbeddingStore
from rag_chain import RAGChain
from evaluator import RAGEvaluator
from instrumentation import RAGInstrument

print("="*70)
print("FULL RAG + EVALUATION PIPELINE TEST")
print("="*70)

# Setup
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
files = ["unica_overview.txt", "unica_best_practices.txt"]
documents = processor.load_documents(files)

store = EmbeddingStore()
store.create_vectorstore(processor.chunk_documents(documents))

retriever = store.get_retriever(k=5)
instrument = RAGInstrument("rag_logs.json")
rag_chain = RAGChain(retriever, instrument)

# Generate answer
print("\n[1] Generating RAG answer...")
result = rag_chain.generate_answer("What are the key features of Unica Campaign?", top_k=5)

# Evaluate
print("\n[2] Evaluating answer quality...")
evaluator = RAGEvaluator(instrument)
scores = evaluator.evaluate_all(
    query=result["query"],
    answer=result["answer"],
    context=result["context"]
)

# Save and summarize
print("\n[3] Saving logs...")
instrument.save()
instrument.summary()

print("\n✓ Full RAG + Evaluation pipeline completed!")
print(f"\nFinal Scores:")
print(f"  • Faithfulness: {scores['faithfulness']:.3f}")
print(f"  • Answer Relevancy: {scores['answer_relevancy']:.3f}")
print(f"  • Context Precision: {scores['context_precision']:.3f}")
print(f"  • Overall: {scores['overall']:.3f}")