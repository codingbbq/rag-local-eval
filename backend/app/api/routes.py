from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.schemas.schemas import (
    QueryRequest, QueryResponse, HealthResponse,
    ProcessingSettings, UploadResponse, ProcessResponse
)
from app.services.upload_service import upload_service
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


@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents (PDF or TXT)
    
    Args:
        files: List of files to upload
        
    Returns:
        Upload response with file info
    """
    debug_logger.info(f"📤 Uploading {len(files)} files")
    
    try:
        file_names, total_size = upload_service.save_uploaded_files(files)
        
        info = upload_service.get_uploaded_files_info()
        
        return {
            "files_uploaded": info["files_uploaded"],
            "file_names": info["file_names"],
            "total_size_mb": info["total_size_mb"],
            "ready_to_process": len(file_names) > 0
        }
        
    except Exception as e:
        debug_logger.error(f"❌ Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/process", response_model=ProcessResponse)
async def process_documents(settings: ProcessingSettings):
    """
    Process uploaded documents with custom settings
    
    Args:
        settings: Processing settings (chunk size, overlap, k)
        
    Returns:
        Processing result with statistics
    """
    debug_logger.info(f"🔄 Processing documents with settings: {settings}")
    
    try:
        result = upload_service.process_documents(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        # Reload RAG service with new FAISS index
        debug_logger.info("🔄 Reloading RAG service...")
        rag_service.initialize()
        debug_logger.info("✓ RAG service reloaded")
        
        return ProcessResponse(**result)
        
    except Exception as e:
        debug_logger.error(f"❌ Processing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/uploads/clear")
async def clear_uploads():
    """Clear all uploaded files"""
    debug_logger.info("🗑️  Clearing uploaded files")
    upload_service.clear_uploads()
    return {"status": "cleared"}