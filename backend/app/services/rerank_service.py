from typing import List, Dict, Tuple
from sentence_transformers import CrossEncoder
from app.utils.logger import logger

debug_logger = logger.get_logger(__name__)

class RerankerService:
    """
    Reranks documents using Cross-Encoder model.
    
    Two-stage retrieval:
    1. Stage 1 (RECALL): FAISS retrieves many documents (20)
    2. Stage 2 (PRECISION): Cross-Encoder reranks to best (5)
    
    Why this works:
    - FAISS is fast but not perfect (recall stage)
    - Cross-Encoder is slower but accurate (precision stage)
    - Combined: Fast + Accurate
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """
        Initialize cross-encoder model
        
        Args:
            model_name: HuggingFace model ID
            
        Cross-Encoder benefits:
        - Trained on MS MARCO dataset (millions of query-document pairs)
        - Understands relevance better than embeddings
        - Returns single score per query-document pair
        """
        debug_logger.info(f"🧠 Loading cross-encoder model: {model_name}...")
        try:
            self.model = CrossEncoder(model_name)
            debug_logger.info("✓ Cross-encoder loaded successfully")
        except Exception as e:
            debug_logger.error(f"❌ Error loading cross-encoder: {str(e)}")
            raise
    
    def rerank(self, query: str, documents: List, top_k: int = 5) -> List[Dict]:
        """
        Rerank documents by relevance to query
        
        Args:
            query: User query
            documents: List of document objects (from FAISS)
            top_k: Number of top documents to return
            
        Returns:
            List of ranked documents: [
                {
                    'document': doc_object,
                    'score': float,
                    'rank': int
                },
                ...
            ]
        """
        if not documents:
            debug_logger.warning("⚠️  No documents to rerank")
            return []
        
        debug_logger.info(f"🔄 Reranking {len(documents)} documents...")
        
        try:
            # Prepare document texts
            doc_texts = [doc.page_content for doc in documents]
            
            # Create query-document pairs for cross-encoder
            # Format: [[query, doc1], [query, doc2], ...]
            pairs = [[query, doc_text] for doc_text in doc_texts]
            
            if logger.is_debug_enabled():
                debug_logger.info(f"📊 Created {len(pairs)} query-document pairs")
            
            # Get relevance scores from cross-encoder
            # Returns array of floats (higher = more relevant)
            scores = self.model.predict(pairs)
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Got scores for all documents")
            
            # Create list of (document, score, rank)
            ranked_docs = []
            for i, (doc, score) in enumerate(zip(documents, scores)):
                ranked_docs.append({
                    'document': doc,
                    'score': float(score),
                    'rank': i + 1,
                })
            
            # Sort by score (descending) - highest score first
            ranked_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # Keep top-k
            top_ranked = ranked_docs[:top_k]
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Reranked {len(documents)} → top-{top_k}")
                debug_logger.info(f"  Top scores:")
                for item in top_ranked[:3]:
                    debug_logger.info(f"    Rank {item['rank']}: Score {item['score']:.4f}")
            
            return top_ranked
            
        except Exception as e:
            debug_logger.error(f"❌ Error in reranking: {str(e)}", exc_info=True)
            raise

# Global instance (lazy loaded on first use)
_reranker = None

def get_reranker() -> RerankerService:
    """Get or create global reranker instance"""
    global _reranker
    if _reranker is None:
        _reranker = RerankerService()
    return _reranker
