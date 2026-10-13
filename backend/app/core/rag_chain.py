from typing import Dict, Any, List
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from app.core.instrumentation import RAGInstrument
from app.utils.logger import logger
from app.services.rerank_service import get_reranker
from app.config import settings
from app.services.hybrid_search_service import hybrid_search_service

debug_logger = logger.get_logger(__name__)

class RAGChain:
    """RAG pipeline with system prompt support"""
    
    def __init__(self, retriever, instrument: RAGInstrument, system_prompt: str = None):
        """
        Initialize RAG chain
        
        Args:
            retriever: FAISS retriever
            instrument: Instrumentation logger
            system_prompt: System prompt to constrain LLM behavior
        """
        self.retriever = retriever
        self.instrument = instrument
        self.system_prompt = system_prompt or "You are a helpful assistant."
        
        # Initialize Ollama
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            num_predict=1024,
            temperature=0.7,
            top_p=0.9,
            top_k=40
        )
    
    def generate_answer(self, query: str, top_k: int = 5, use_reranking: bool = True) -> Dict[str, Any]:
        """
        Generate answer using RAG pipeline with optional reranking
        
        Args:
            query: User query
            top_k: Final number of documents to use
            use_reranking: Whether to use cross-encoder reranking
            
        Returns:
            Dict with answer, context, and metadata
        """
        
        try:
            if logger.is_debug_enabled():
                debug_logger.info(f"🔄 Starting RAG chain (reranking: {use_reranking})")
            
            # Stage 1: RECALL - Retrieve more documents than needed
            retrieval_k = top_k * settings.RERANKER_RETRIEVAL_MULTIPLIER if use_reranking else top_k

            if logger.is_debug_enabled():
                debug_logger.info(f"🔍 Stage 1 RECALL: Hybrid search for {retrieval_k} documents...")

            # Use hybrid search instead of just FAISS
            hybrid_results = hybrid_search_service.hybrid_search(query, top_k=retrieval_k)
            retrieved_docs = [item['doc'] for item in hybrid_results]

            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Hybrid search retrieved {len(retrieved_docs)} documents")
                debug_logger.info(f"  Methods: {[item['method'] for item in hybrid_results[:3]]}")
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Retrieved {len(retrieved_docs)} documents")
                for i, doc in enumerate(retrieved_docs[:3]):
                    content_preview = doc.page_content[:80].replace('\n', ' ')
                    debug_logger.info(f"  Doc {i+1}: {content_preview}...")
            
            # Stage 2: PRECISION - Rerank to get best documents
            final_docs = retrieved_docs
            if use_reranking and len(retrieved_docs) > 0:
                if logger.is_debug_enabled():
                    debug_logger.info(f"🎯 Stage 2 PRECISION: Reranking with cross-encoder...")
                
                reranker = get_reranker()
                ranked_results = reranker.rerank(query, retrieved_docs, top_k=top_k)
                final_docs = [item['document'] for item in ranked_results]
                
                if logger.is_debug_enabled():
                    debug_logger.info(f"✓ Selected top-{top_k} documents after reranking")
            else:
                # If no reranking, just take top-k
                final_docs = retrieved_docs[:top_k]
                if logger.is_debug_enabled():
                    debug_logger.info(f"ℹ️  No reranking, using top-{top_k} from FAISS")
            
            # Extract similarity scores
            scores = [
                float(doc.metadata.get('score', 0.0))
                for doc in final_docs
            ]
            
            # Log retrieval
            self.instrument.log_retrieval(
                query,
                final_docs,
                scores,
                top_k
            )
            
            # Build context from final documents
            context = "\n\n".join([
                f"[Document {i+1}]\n{doc.page_content}"
                for i, doc in enumerate(final_docs)
            ])
            
            if logger.is_debug_enabled():
                debug_logger.info(f"📝 Built context: {len(context)} chars")
            
            # Build prompt with system prompt + context + question
            prompt = f"""{self.system_prompt}

            ---

            Context from documents:
            {context}

            ---

            User Question: {query}

            Answer in a clear, well-structured way. Use markdown formatting with headings, bullet points, and code blocks when appropriate."""

            if logger.is_debug_enabled():
                debug_logger.info(f"📤 Sending prompt to {self.llm.model} ({len(prompt)} chars)...")
            
            # Generate answer
            answer = self.llm.invoke(prompt)
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Received answer ({len(answer)} chars)")
                if len(answer) > 100:
                    debug_logger.info(f"  Preview: {answer[:100]}...")
            
            # Log generation
            self.instrument.log_generation(
                context=context,
                answer=answer,
                model=self.llm.model,
                tokens_used=len(answer.split())
            )
            
            return {
                "query": query,
                "answer": answer,
                "context": context,
                "retrieved_docs": final_docs,
                "num_docs_retrieved": len(final_docs),
                "tokens_used": len(answer.split())
            }
            
        except Exception as e:
            debug_logger.error(f"❌ Error in RAG chain: {str(e)}", exc_info=True)
            raise