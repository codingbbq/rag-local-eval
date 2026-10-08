from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.core.rag_chain import RAGChain
from app.core.evaluator import RAGEvaluator
from app.core.instrumentation import RAGInstrument
from app.config import settings
from app.utils.logger import logger
import numpy as np

debug_logger = logger.get_logger(__name__)

class RAGService:
    """Orchestrates RAG pipeline with theme-based filtering"""
    
    def __init__(self):
        """Initialize RAG components"""
        self.instrument = RAGInstrument(str(settings.LOGS_DIR / "rag_logs.json"))
        self.embedding_store = EmbeddingStore()
        self.evaluator = RAGEvaluator(self.instrument)
        self.rag_chain = None
        
    def initialize(self):
        """Load FAISS index and create RAG chain"""
        debug_logger.info("Loading FAISS index...")
        self.embedding_store.load_vectorstore(str(settings.FAISS_INDEX_PATH))
        retriever = self.embedding_store.get_retriever(k=settings.DEFAULT_RETRIEVE_K)
        self.rag_chain = RAGChain(
            retriever, 
            self.instrument,
            system_prompt=settings.SYSTEM_PROMPT
        )
        debug_logger.info("✓ RAG service initialized")
    
    def check_relevance(self, retrieved_docs, top_k=5):
        """
        Check if retrieved documents are relevant to the query.
        Returns True if at least one doc has high similarity.
        """
        if not retrieved_docs or len(retrieved_docs) == 0:
            return False
        
        # Get similarity scores (if available in metadata)
        scores = [
            doc.metadata.get('score', 0) 
            for doc in retrieved_docs[:top_k]
        ]
        
        max_score = max(scores) if scores else 0
        return max_score >= settings.SIMILARITY_THRESHOLD
    
    def query(self, user_query: str, top_k: int = 5):
        """
        Process user query with theme-based filtering.
        Returns answer with evaluation metrics.
        """
        if logger.is_debug_enabled():
            debug_logger.info(f"📨 Query received: {user_query}")
        
        if not self.rag_chain:
            debug_logger.error("❌ RAG chain not initialized")
            raise RuntimeError("RAG service not initialized")
        
        try:
            if logger.is_debug_enabled():
                debug_logger.info(f"🔍 Retrieving top-{top_k} documents...")
            
            # Generate answer with system prompt
            result = self.rag_chain.generate_answer(user_query, top_k=top_k)
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Retrieved {result.get('num_docs_retrieved')} documents")
                debug_logger.info(f"Answer length: {len(result.get('answer', ''))} chars")
            
            # Check if retrieved docs are relevant
            num_docs = result.get("num_docs_retrieved", 0)
            
            if num_docs == 0:
                if logger.is_debug_enabled():
                    debug_logger.warning("⚠️  No relevant documents found - likely off-topic")
                
                return {
                    "query": user_query,
                    "answer": settings.OFF_TOPIC_RESPONSE,
                    "num_docs_retrieved": 0,
                    "tokens_used": 0,
                    "is_on_topic": False,
                    "evaluation": {
                        "faithfulness": 0.0,
                        "answer_relevancy": 0.0,
                        "context_precision": 0.0,
                        "overall": 0.0
                    }
                }
            
            if logger.is_debug_enabled():
                debug_logger.info("📊 Evaluating answer quality...")
            
            # Evaluate quality
            scores = self.evaluator.evaluate_all(
                query=result["query"],
                answer=result["answer"],
                context=result["context"]
            )
            
            if logger.is_debug_enabled():
                debug_logger.info(f"Evaluation scores - Overall: {scores['overall']:.2f}, Faithfulness: {scores['faithfulness']:.2f}, Relevancy: {scores['answer_relevancy']:.2f}")
            
            response = {
                "query": result["query"],
                "answer": result["answer"],
                "num_docs_retrieved": result["num_docs_retrieved"],
                "tokens_used": result["tokens_used"],
                "is_on_topic": True,
                "evaluation": {
                    "faithfulness": scores["faithfulness"],
                    "answer_relevancy": scores["answer_relevancy"],
                    "context_precision": scores["context_precision"],
                    "overall": scores["overall"]
                }
            }
            
            if logger.is_debug_enabled():
                debug_logger.info("✅ Query processing complete")
            
            return response
            
        except Exception as e:
            debug_logger.error(f"❌ Error processing query: {str(e)}", exc_info=True)
            raise
    
    def get_stats(self):
        """Get system statistics"""
        return {
            "vectors_in_index": self.embedding_store.vectorstore.index.ntotal if self.embedding_store.vectorstore else 0,
            "theme": settings.SYSTEM_THEME
        }

# Global service instance
rag_service = RAGService()