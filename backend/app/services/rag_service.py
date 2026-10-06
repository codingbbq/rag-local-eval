
from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.core.rag_chain import RAGChain
from app.core.evaluator import RAGEvaluator
from app.core.instrumentation import RAGInstrument
from app.config import settings

class RAGService:
    """Orchestrates RAG pipeline"""
    
    def __init__(self):
        """Initialize RAG components"""
        self.instrument = RAGInstrument(str(settings.LOGS_DIR / "rag_logs.json"))
        self.embedding_store = EmbeddingStore()
        self.evaluator = RAGEvaluator(self.instrument)
        self.rag_chain = None
        
    def initialize(self):
        """Load FAISS index and create RAG chain"""
        print("Loading FAISS index...")
        self.embedding_store.load_vectorstore(str(settings.FAISS_INDEX_PATH))
        retriever = self.embedding_store.get_retriever(k=settings.RETRIEVE_K)
        self.rag_chain = RAGChain(retriever, self.instrument)
        print("✓ RAG service initialized")
    
    def query(self, user_query: str, top_k: int = 5):
        """Process user query and return answer with evaluation"""
        if not self.rag_chain:
            raise RuntimeError("RAG service not initialized")
        
        # Generate answer
        result = self.rag_chain.generate_answer(user_query, top_k=top_k)
        
        # Evaluate
        scores = self.evaluator.evaluate_all(
            query=result["query"],
            answer=result["answer"],
            context=result["context"]
        )
        
        return {
            "query": result["query"],
            "answer": result["answer"],
            "num_docs_retrieved": result["num_docs_retrieved"],
            "tokens_used": result["tokens_used"],
            "evaluation": {
                "faithfulness": scores["faithfulness"],
                "answer_relevancy": scores["answer_relevancy"],
                "context_precision": scores["context_precision"],
                "overall": scores["overall"]
            }
        }
    
    def get_stats(self):
        """Get system statistics"""
        return {
            "vectors_in_index": self.embedding_store.vectorstore.index.ntotal if self.embedding_store.vectorstore else 0
        }

# Global service instance
rag_service = RAGService()