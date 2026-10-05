from typing import Dict
from langchain_community.llms import Ollama
from app.core.instrumentation import RAGInstrument
import re

class RAGEvaluator:
    """
    Evaluate RAG answer quality using Llama2 as judge.
    
    Three metrics:
    1. Faithfulness: Is answer grounded in context?
    2. Answer Relevancy: Does it address the question?
    3. Context Precision: Is retrieved context useful?
    """
    
    def __init__(self, instrument: RAGInstrument):
        """
        Initialize evaluator with Llama2.
        
        Args:
            instrument: RAGInstrument for logging
        """
        print("\n📊 Initializing RAG Evaluator...")
        
        self.instrument = instrument
        
        try:
            # Same Llama2 instance we use for generation
            self.llm = Ollama(
                model="llama2",
                base_url="http://localhost:11434",
                num_predict=256,  # Allow longer responses
                temperature=0.1,  # Lower temperature for consistent scoring
                top_p=0.9,
                top_k=40
            )
            print("   ✓ Llama2 loaded for evaluation")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise

    
    def evaluate_faithfulness(self, answer: str, context: str) -> float:
        """
        Evaluate Faithfulness (0-1).
        Simpler approach: Ask if claims are grounded.
        """
        print(f"\n   📊 Evaluating Faithfulness...")
        
        # Count sentences in answer
        answer_sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        if not answer_sentences:
            return 0.5
        
        # Simple heuristic: check if answer text appears in context
        answer_lower = answer.lower()
        context_lower = context.lower()
        
        # Count how much of answer is in context
        answer_words = answer_lower.split()
        matching_words = sum(1 for word in answer_words if word in context_lower)
        
        if len(answer_words) > 0:
            # Score = percentage of answer words that appear in context
            score = matching_words / len(answer_words)
            score = min(1.0, score * 1.2)  # Boost score a bit (not every word needs to match)
        else:
            score = 0.5
        
        # Clamp to [0, 1]
        score = max(0, min(1, score))
        
        self.instrument.log_evaluation("faithfulness", score)
        print(f"      Score: {score:.3f} (based on word overlap)")
        
        return score


    def evaluate_answer_relevancy(self, query: str, answer: str) -> float:
        """
        Evaluate Answer Relevancy (0-1).
        Simple: Check if answer mentions key query words.
        """
        print(f"\n   📊 Evaluating Answer Relevancy...")
        
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        
        # Remove common words
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'and', 'or', 'but', 'if', 'in', 'on', 'at', 'to', 'for'}
        query_words = query_words - stop_words
        
        if not query_words:
            return 0.5
        
        # How many query words appear in answer?
        overlap = len(query_words & answer_words)
        score = overlap / len(query_words)
        
        # Boost if answer is long (more likely to be detailed)
        if len(answer) > 200:
            score = min(1.0, score * 1.3)
        
        score = max(0, min(1, score))
        
        self.instrument.log_evaluation("answer_relevancy", score)
        print(f"      Score: {score:.3f} (based on keyword overlap)")
        
        return score

    

    def evaluate_context_precision(self, context: str, answer: str) -> float:
        """
        Evaluate Context Precision (0-1).
        Simple: Check how much context is referenced in answer.
        """
        print(f"\n   📊 Evaluating Context Precision...")
        
        # Split context into documents
        documents = context.split("Document")
        
        if len(documents) <= 1:
            return 0.5
        
        # Count which documents are actually used in answer
        answer_lower = answer.lower()
        
        used_docs = 0
        for i, doc in enumerate(documents[1:], 1):
            # Check if this document's content appears in answer
            doc_lines = doc.split('\n')
            for line in doc_lines[:3]:  # Check first 3 lines
                if line.strip().lower() in answer_lower:
                    used_docs += 1
                    break
        
        # Score = fraction of documents actually used
        score = used_docs / (len(documents) - 1) if len(documents) > 1 else 0.5
        score = max(0, min(1, score))
        
        self.instrument.log_evaluation("context_precision", score)
        print(f"      Score: {score:.3f} (based on doc usage)")
        
        return score

    

    def evaluate_all(self, query: str, answer: str, context: str) -> Dict[str, float]:
        """
        Run all evaluations and return scores.
        
        Args:
            query: User's question
            answer: Generated answer
            context: Retrieved context
        
        Returns:
            Dict with all three metric scores
        """
        print(f"\n{'='*70}")
        print(f"EVALUATION: {query[:50]}...")
        print(f"{'='*70}")
        
        # Run all three evaluations
        faithfulness = self.evaluate_faithfulness(answer, context)
        relevancy = self.evaluate_answer_relevancy(query, answer)
        precision = self.evaluate_context_precision(context, answer)
        
        # Calculate average
        avg_score = (faithfulness + relevancy + precision) / 3
        
        print(f"\n   📈 Overall Score: {avg_score:.3f} (average)")
        
        return {
            "faithfulness": faithfulness,
            "answer_relevancy": relevancy,
            "context_precision": precision,
            "overall": avg_score
        }


    def processScore(self, score_text: str) -> float:
        # DEBUG: Print what we received
        print(f"      [DEBUG] Raw response: {score_text[:100]}")
        
        try:
            numbers = re.findall(r'0\.\d+|1\.0', score_text)
            print(f"      [DEBUG] Numbers found: {numbers}")
            
            if numbers:
                score = float(numbers[-1])  # Take last number
            else:
                score = 0.5
            
            # Clamp to [0, 1]
            score = max(0, min(1, score))
            
        except ValueError:
            print(f"      Error converting score '{score_text}', defaulting to 0.5")
            score = 0.5
        
        return score