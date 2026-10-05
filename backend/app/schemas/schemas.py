from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    """User query request"""
    query: str
    top_k: Optional[int] = 5

class EvaluationScore(BaseModel):
    """Evaluation metrics"""
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    overall: float

class QueryResponse(BaseModel):
    """RAG response"""
    query: str
    answer: str
    num_docs_retrieved: int
    tokens_used: int
    evaluation: EvaluationScore

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vectors_in_index: int