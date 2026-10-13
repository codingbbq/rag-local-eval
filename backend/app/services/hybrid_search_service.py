from typing import List, Dict
from rank_bm25 import BM25Okapi
from app.core.embedding_store import EmbeddingStore
from app.utils.logger import logger
import numpy as np

debug_logger = logger.get_logger(__name__)

class HybridSearchService:
    """
    Hybrid search combining semantic (FAISS) + keyword (BM25)
    
    Why hybrid?
    - Semantic: Great for natural language, concepts, paraphrasing
      Example: "optimize campaigns" matches "improve marketing"
    - Keyword: Great for exact terms, technical parameters, rare words
      Example: "timeout=5000" only matches documents with "timeout"
    - Combined: Best of both worlds!
    
    Use cases:
    - Semantic: "How do I make better campaigns?"
    - Keyword: "Configure timeout in settings"
    - Both: "Best practices for A/B testing"
    
    Algorithm: Reciprocal Rank Fusion (RRF)
    - Merges ranked lists from both search methods
    - Normalized scoring (doesn't matter if one method returns 0.8, other 8.5)
    - Proven effective in production search systems
    """
    
    def __init__(self, embedding_store=None):
        """
        Initialize hybrid search service
        
        Args:
            embedding_store: Existing EmbeddingStore instance (optional)
        """
        # Use passed-in embedding store or create new one
        if embedding_store:
            self.embedding_store = embedding_store
            debug_logger.info("✓ Using provided embedding store")
        else:
            self.embedding_store = EmbeddingStore()
            debug_logger.info("✓ Created new embedding store")
        
        self.bm25 = None
        self.documents = None
        self.documents_text = None
    
    def initialize(self, documents: List):
        """
        Initialize BM25 index with documents
        
        Args:
            documents: List of document objects
            
        Process:
        1. Extract text from documents
        2. Tokenize (split into words)
        3. Create BM25 index
        """
        debug_logger.info(f"📚 Initializing BM25 with {len(documents)} documents...")
        
        try:
            # Extract document texts
            doc_texts = [doc.page_content for doc in documents]
            
            # Tokenize documents for BM25
            # BM25 works on tokens, not raw text
            tokenized_docs = [
                doc.lower().split()  # Simple tokenization
                for doc in doc_texts
            ]
            
            # Create BM25 index
            # This learns term frequencies and document lengths
            self.bm25 = BM25Okapi(tokenized_docs)
            self.documents = documents
            self.documents_text = doc_texts
            
            debug_logger.info(f"✓ BM25 index ready with {len(tokenized_docs)} documents")
            
        except Exception as e:
            debug_logger.error(f"❌ Error initializing BM25: {str(e)}", exc_info=True)
            raise
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search using embeddings (FAISS)
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of {doc, score, method}
        """
        if logger.is_debug_enabled():
            debug_logger.info(f"🧠 Semantic search (FAISS)...")
        
        try:
            # Check if embedding store has vectorstore
            if not self.embedding_store.vectorstore:
                debug_logger.warning("⚠️  FAISS not loaded, using RAG service's instance")
                from app.services.rag_service import rag_service
                self.embedding_store = rag_service.embedding_store
            
            retriever = self.embedding_store.get_retriever(k=top_k)
            results = retriever.invoke(query)
            
            semantic_results = [
                {
                    'doc': doc,
                    'score': doc.metadata.get('score', 0.0),
                    'method': 'semantic',
                    'rank': i + 1
                }
                for i, doc in enumerate(results)
            ]
            
            if logger.is_debug_enabled():
                debug_logger.info(f"  ✓ Found {len(semantic_results)} semantic results")
            
            return semantic_results
            
        except Exception as e:
            debug_logger.error(f"❌ Error in semantic search: {str(e)}", exc_info=True)
            return []
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Keyword search using BM25
        
        BM25 Algorithm:
        - TF-IDF based scoring
        - Learns from document corpus
        - Penalizes very common terms
        - Rewards matching rare terms
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of {doc, score, method}
        """
        if not self.bm25 or not self.documents:
            debug_logger.warning("⚠️  BM25 not initialized, skipping keyword search")
            return []
        
        if logger.is_debug_enabled():
            debug_logger.info(f"🔑 Keyword search (BM25)...")
        
        try:
            # Tokenize query
            tokenized_query = query.lower().split()
            
            # Get BM25 scores for all documents
            # Returns array of floats, one per document
            scores = self.bm25.get_scores(tokenized_query)
            
            # Get indices of top-k scores
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            keyword_results = []
            for rank, idx in enumerate(top_indices):
                score = float(scores[idx])
                if score > 0:  # Only include docs with positive score
                    keyword_results.append({
                        'doc': self.documents[idx],
                        'score': score,
                        'method': 'keyword',
                        'rank': rank + 1
                    })
            
            if logger.is_debug_enabled():
                debug_logger.info(f"  ✓ Found {len(keyword_results)} keyword results")
            
            return keyword_results
            
        except Exception as e:
            debug_logger.error(f"❌ Error in keyword search: {str(e)}", exc_info=True)
            return []
    
    def reciprocal_rank_fusion(self, semantic_results: List[Dict],
                               keyword_results: List[Dict],
                               top_k: int = 20) -> List[Dict]:
        """
        Combine results using Reciprocal Rank Fusion (RRF)
        
        Formula: RRF_score = 1 / (k + rank)
        where k = 60 (standard parameter)
        
        Why RRF?
        - Rank-based (not score-based), so works across different scoring systems
        - Proven effective in information retrieval
        - Used by major search engines
        - Normalized: 1/(60+1) ≈ 0.016 for first result
        
        Example:
        Semantic search ranks Doc A at position 1 → RRF = 1/61 = 0.0164
        Keyword search ranks Doc A at position 3 → RRF = 1/63 = 0.0159
        Combined score for Doc A = 0.0164 + 0.0159 = 0.0323
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from BM25
            top_k: Number of final results
            
        Returns:
            Fused and ranked results
        """
        if logger.is_debug_enabled():
            debug_logger.info("🔀 Fusing results with RRF...")
        
        k = 60  # RRF parameter (standard value)
        fused_scores = {}
        doc_to_item = {}
        
        # Process semantic results
        for item in semantic_results:
            doc_content = item['doc'].page_content
            rank = item['rank']
            rrf_score = 1 / (k + rank)
            
            if doc_content not in fused_scores:
                fused_scores[doc_content] = 0
                doc_to_item[doc_content] = item
            
            # Weight: 50% semantic, 50% keyword (equal importance)
            fused_scores[doc_content] += rrf_score * 0.5
            
            if logger.is_debug_enabled():
                debug_logger.info(
                    f"  Semantic: {doc_content[:50]}... rank={rank}, rrf={rrf_score:.4f}"
                )
        
        # Process keyword results
        for item in keyword_results:
            doc_content = item['doc'].page_content
            rank = item['rank']
            rrf_score = 1 / (k + rank)
            
            if doc_content not in fused_scores:
                fused_scores[doc_content] = 0
                doc_to_item[doc_content] = item
            
            # Weight: 50% semantic, 50% keyword
            fused_scores[doc_content] += rrf_score * 0.5
            
            if logger.is_debug_enabled():
                debug_logger.info(
                    f"  Keyword: {doc_content[:50]}... rank={rank}, rrf={rrf_score:.4f}"
                )
        
        # Sort by fused score (highest first)
        sorted_results = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        fused_results = [
            {
                **doc_to_item[doc_content],
                'fused_score': score,
                'method': 'hybrid'
            }
            for doc_content, score in sorted_results
        ]
        
        if logger.is_debug_enabled():
            debug_logger.info(f"✓ Fused into {len(fused_results)} results")
            for i, item in enumerate(fused_results[:3]):
                debug_logger.info(
                    f"  {i+1}. Score: {item['fused_score']:.4f}, Method: {item['method']}"
                )
        
        return fused_results
    
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Full hybrid search pipeline
        
        Pipeline:
        1. Semantic search (FAISS) → 10 results
        2. Keyword search (BM25) → 10 results
        3. Fuse with RRF → 15-20 results
        4. Return top-k best
        
        Args:
            query: User query
            top_k: Final number of results
            
        Returns:
            List of best documents
        """
        if logger.is_debug_enabled():
            debug_logger.info(f"🔍 Starting HYBRID search for: {query}")
        
        try:
            # Stage 1: Semantic search
            semantic_results = self.semantic_search(query, top_k=10)
            
            # Stage 2: Keyword search
            keyword_results = self.keyword_search(query, top_k=10)
            
            # Stage 3: Fuse results
            fused = self.reciprocal_rank_fusion(
                semantic_results,
                keyword_results,
                top_k=top_k * 3  # Get more for later reranking
            )
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Hybrid search complete: {len(fused)} results")
            
            return fused
            
        except Exception as e:
            debug_logger.error(f"❌ Error in hybrid search: {str(e)}", exc_info=True)
            # Fallback to semantic search only
            debug_logger.warning("⚠️  Falling back to semantic search only")
            return self.semantic_search(query, top_k=top_k)

# Global instance
hybrid_search_service = HybridSearchService()
