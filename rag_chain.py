from typing import Dict, Any, List
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from instrumentation import RAGInstrument

class RAGChain:
    """
    RAG chain using local Llama2 model.
    
    Process:
    1. User asks question
    2. Retrieve top-k relevant chunks
    3. Build context from chunks
    4. Create prompt with context + question
    5. Call Llama2 to generate answer
    6. Log everything
    """
    
    def __init__(self, retriever, instrument: RAGInstrument):
        """
        Initialize RAG chain.
        
        Args:
            retriever: LangChain retriever (from EmbeddingStore)
            instrument: RAGInstrument for logging
        """
        self.retriever = retriever
        self.instrument = instrument
        
        # Initialize Ollama LLM
        print("\n🤖 Initializing Llama2 via Ollama...")
        try:
            self.llm = Ollama(
                model="llama2",
                base_url="http://localhost:11434",
                num_predict=512,  # Longer response for answers
                temperature=0.7,  # More creative for answers
                top_p=0.9,
                top_k=40
            )
            print("   ✓ Ollama connected (llama2 model)")
            print("   Make sure 'ollama serve' is running in another terminal!")
        except Exception as e:
            print(f"   ❌ Error connecting to Ollama: {e}")
            print("   Did you run 'ollama serve' in another terminal?")
            raise

    
    def generate_answer(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Generate answer using RAG with local Llama2.
        
        This is the main RAG pipeline:
        1. Retrieve documents
        2. Create context
        3. Build prompt
        4. Generate answer
        5. Log everything
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with query, answer, context, retrieved docs
        """
        
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print(f"{'='*70}")
        
        # =====================================================
        # STEP 1: RETRIEVE DOCUMENTS
        # =====================================================
        print(f"\n[STEP 1] Retrieving relevant documents...")
        
        try:
            # Use retriever to find similar chunks
            retrieved_docs = self.retriever.invoke(query)
            scores = [0.85] * len(retrieved_docs)  # Placeholder scores
            print(f"   ✓ Retrieved {len(retrieved_docs)} documents")
            
        except Exception as e:
            print(f"   ❌ Error retrieving: {e}")
            retrieved_docs = []
            scores = []
        
        # Log retrieval
        self.instrument.log_retrieval(query, retrieved_docs, scores, top_k)
        
        # =====================================================
        # STEP 2: PREPARE CONTEXT
        # =====================================================
        print(f"\n[STEP 2] Preparing context...")
        
        # Combine all retrieved documents into one context string
        context = "\n\n".join([
            f"Document {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        print(f"   ✓ Context prepared ({len(context)} chars)")
        
        # =====================================================
        # STEP 3: BUILD PROMPT
        # =====================================================
        print(f"\n[STEP 3] Building prompt for Llama2...")
        
        # This is the key to good RAG - clear instructions
        prompt = f"""You are a helpful assistant answering questions based on provided context.

        IMPORTANT RULES:
        1. Answer ONLY based on the provided context
        2. If the answer is not in the context, say "I don't have enough information to answer this question."
        3. Be concise and direct
        4. Quote relevant passages when helpful

        === CONTEXT ===
        {context}

        === QUESTION ===
        {query}

        === ANSWER ==="""
        
        print(f"   Prompt size: {len(prompt)} chars")
        
        # =====================================================
        # STEP 4: GENERATE WITH LLAMA2
        # =====================================================
        print(f"\n[STEP 4] Generating answer with Llama2...")
        print(f"   (This may take 30-60 seconds on first run)...")
        
        try:
            # Call Llama2 via Ollama
            answer = self.llm.invoke(prompt)
            
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            tokens_estimate = (len(prompt) + len(answer)) // 4
            
            print(f"   ✓ Answer generated")
            print(f"   • Estimated tokens: ~{tokens_estimate}")
            print(f"   • Answer length: {len(answer)} chars")
            
        except Exception as e:
            print(f"   ❌ Error generating answer: {e}")
            answer = f"Error generating answer: {e}"
            tokens_estimate = 0
        
        # Log generation
        self.instrument.log_generation(context, answer, "llama2-local", tokens_estimate)
        
        # =====================================================
        # STEP 5: DISPLAY ANSWER
        # =====================================================
        print(f"\n{'─'*70}")
        print(f"ANSWER:")
        print(f"{'─'*70}")
        print(answer)
        print(f"{'─'*70}\n")
        
        # =====================================================
        # RETURN RESULT
        # =====================================================
        return {
            "query": query,
            "answer": answer,
            "context": context,
            "retrieved_docs": [doc.page_content for doc in retrieved_docs],
            "num_docs_retrieved": len(retrieved_docs),
            "tokens_used": tokens_estimate
        }