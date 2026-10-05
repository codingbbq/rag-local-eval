# instrumentation.py
import json
from datetime import datetime
from typing import List

class RAGInstrument:
    """Logs RAG pipeline events to JSON"""
    
    def __init__(self, log_file: str = "rag_logs.json"):
        self.log_file = log_file
        self.logs = []
        print(f"✓ Instrumentation ready (logs → {log_file})")
    
    def log_retrieval(self, query: str, retrieved_docs: List, 
                      scores: List[float], top_k: int):
        """Log retrieval stage"""
        self.logs.append({
            "stage": "retrieval",
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_docs_retrieved": len(retrieved_docs),
            "retrieval_scores": [float(s) for s in scores],
            "max_score": max(scores) if scores else 0,
            "docs_preview": [
                {
                    "content": (doc.page_content[:200] 
                               if hasattr(doc, 'page_content') 
                               else str(doc)[:200]),
                    "score": float(scores[i]) if i < len(scores) else None
                }
                for i, doc in enumerate(retrieved_docs[:top_k])
            ]
        })
        print(f"  [Log] Retrieved {len(retrieved_docs)} docs")
    
    def log_generation(self, context: str, answer: str, 
                      model: str, tokens_used: int):
        """Log generation stage"""
        self.logs.append({
            "stage": "generation",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "context_length": len(context),
            "answer_length": len(answer),
            "tokens_estimate": tokens_used,
            "answer_preview": answer[:300]
        })
        print(f"  [Log] Generated {tokens_used} tokens")
    
    def log_evaluation(self, metric_name: str, score: float):
        """Log evaluation metric"""
        self.logs.append({
            "stage": "evaluation",
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "score": float(score)
        })
        print(f"  [Log] {metric_name}: {score:.3f}")
    
    def save(self):
        """Save logs to JSON"""
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
        print(f"\n✓ Logs saved to {self.log_file}")
    
    def summary(self):
        """Print summary"""
        print("\n" + "="*60)
        print("RAG EXECUTION SUMMARY")
        print("="*60)
        
        retrievals = [l for l in self.logs if l["stage"] == "retrieval"]
        generations = [l for l in self.logs if l["stage"] == "generation"]
        evaluations = [l for l in self.logs if l["stage"] == "evaluation"]
        
        print(f"\n📊 Retrievals: {len(retrievals)}")
        print(f"🤖 Generations: {len(generations)}")
        print(f"✅ Evaluations: {len(evaluations)}")
        
        for eval_log in evaluations:
            print(f"   • {eval_log['metric']}: {eval_log['score']:.3f}")
        
        print("\n" + "="*60 + "\n")