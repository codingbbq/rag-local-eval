from pydantic import BaseModel
from typing import Optional, List

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
    """RAG response with theme checking"""
    query: str
    answer: str
    num_docs_retrieved: int
    tokens_used: int
    is_on_topic: bool  # NEW - indicates if query was on-topic
    evaluation: EvaluationScore

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vectors_in_index: int

class ProcessingSettings(BaseModel):
    """Document processing settings"""
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    retrieve_k: Optional[int] = 5

class UploadResponse(BaseModel):
    """Response after file upload"""
    files_uploaded: int
    file_names: List[str]
    total_size_mb: float
    ready_to_process: bool

class ProcessResponse(BaseModel):
    """Response after processing documents"""
    status: str
    documents_processed: int
    chunks_created: int
    embeddings_created: int
    total_vectors_in_index: int
    message: str