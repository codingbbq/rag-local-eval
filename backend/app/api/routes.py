from fastapi import APIRouter, HTTPException
from app.schemas.schemas import QueryRequest, QueryResponse, HealthResponse
from app.services.rag_service import rag_service
from app.utils.logger import logger

debug_logger = logger.get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["RAG"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    debug_logger.info("🏥 Health check requested")
    stats = rag_service.get_stats()
    return {
        "status": "ok",
        "vectors_in_index": stats["vectors_in_index"]
    }

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query with theme-based filtering.
    Only answers questions related to the configured theme.
    """
    debug_logger.info(f"🎯 Processing query: {request.query}")
    
    try:
        result = rag_service.query(request.query, top_k=request.top_k)
        debug_logger.info("✅ Query processed successfully")
        return result
        
    except Exception as e:
        debug_logger.error(f"❌ Exception in /query endpoint: {str(e)}", exc_info=True)
        
        # Return more detailed error in debug mode
        from app.config import settings
        if settings.DEBUG:
            error_detail = f"Error: {str(e)}\n\nCheck debug.log for details."
        else:
            error_detail = "An error occurred processing your query. Please try again."
        
        raise HTTPException(status_code=500, detail=error_detail)