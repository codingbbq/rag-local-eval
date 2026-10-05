
from fastapi import APIRouter, HTTPException
from app.schemas.schemas import QueryRequest, QueryResponse, HealthResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/v1", tags=["RAG"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    stats = rag_service.get_stats()
    return {
        "status": "ok",
        "vectors_in_index": stats["vectors_in_index"]
    }

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query and return RAG response"""
    try:
        result = rag_service.query(request.query, top_k=request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))