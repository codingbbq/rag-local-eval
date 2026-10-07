from typing import Dict, Any, List
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from app.core.instrumentation import RAGInstrument
from app.utils.logger import logger

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
            model="llama2",
            base_url="http://localhost:11434",
            num_predict=512,
            temperature=0.7,
            top_p=0.9,
            top_k=40
        )
    
    def generate_answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Generate answer using RAG pipeline with system prompt"""
        
        try:
            if logger.is_debug_enabled():
                debug_logger.info(f"🔄 Starting RAG chain for query: {query[:50]}...")
            
            # Retrieve documents
            if logger.is_debug_enabled():
                debug_logger.info("🔍 Retrieving documents from FAISS...")
            
            retrieved_docs = self.retriever.invoke(query)
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Retrieved {len(retrieved_docs)} documents")
                for i, doc in enumerate(retrieved_docs[:3]):
                    debug_logger.info(f"  Doc {i+1}: {doc.page_content[:100]}...")
            
            # Log retrieval
            self.instrument.log_retrieval(
                query=query,
                num_docs=len(retrieved_docs),
                doc_ids=[doc.metadata.get('id', 'unknown') for doc in retrieved_docs]
            )
            
            # Build context from retrieved documents
            context = "\n\n".join([
                f"[Document {i+1}]\n{doc.page_content}"
                for i, doc in enumerate(retrieved_docs[:top_k])
            ])
            
            if logger.is_debug_enabled():
                debug_logger.info(f"📝 Context length: {len(context)} chars")
            
            # Build prompt
            prompt = f"""{self.system_prompt}

    ---

    Context from documents:
    {context}

    ---

    User Question: {query}

    Answer in a clear, well-structured way. Use markdown formatting with headings, bullet points, and code blocks when appropriate."""

            if logger.is_debug_enabled():
                debug_logger.info(f"📤 Sending prompt to Ollama (length: {len(prompt)} chars)...")
            
            # Generate answer
            answer = self.llm.invoke(prompt)
            
            if logger.is_debug_enabled():
                debug_logger.info(f"✓ Received answer (length: {len(answer)} chars)")
                debug_logger.info(f"  First 100 chars: {answer[:100]}...")
            
            # Log generation
            self.instrument.log_generation(
                query=query,
                answer=answer,
                num_docs=len(retrieved_docs),
                tokens_used=len(answer.split())
            )
            
            return {
                "query": query,
                "answer": answer,
                "context": context,
                "retrieved_docs": retrieved_docs,
                "num_docs_retrieved": len(retrieved_docs),
                "tokens_used": len(answer.split())
            }
            
        except Exception as e:
            debug_logger.error(f"❌ Error in RAG chain: {str(e)}", exc_info=True)
            raise