"""
RAG Query Routes - Using Correct RAGService Methods
"""

import logging
import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional, List

# ============================================
# SETUP
# ============================================

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["query"])

# Global RAG service instance (set by main.py)
rag_service = None

def set_rag_service(service):
    """Set the RAG service instance"""
    global rag_service
    rag_service = service
    logger.info("✅ RAG service set in routes")

# ============================================
# SCHEMAS
# ============================================

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    use_history: Optional[bool] = True

class QueryResponse(BaseModel):
    answer: str
    relevant_docs: List[dict]
    request_id: str

# ============================================
# UPLOAD ENDPOINT
# ============================================

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents for RAG
    
    Supported formats: PDF, TXT, DOCX, etc.
    
    Note: Documents are automatically processed and indexed by RAGService
    """
    try:
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not initialized")
        
        upload_dir = "backend/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_files = []
        
        for file in files:
            file_path = os.path.join(upload_dir, file.filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": os.path.getsize(file_path),
                "path": file_path
            })
            
            logger.info(f"✅ Uploaded: {file.filename}")
        
        return {
            "success": True,
            "message": f"{len(uploaded_files)} files uploaded successfully",
            "files": uploaded_files,
            "note": "Documents will be processed on first query"
        }
    
    except Exception as e:
        logger.error(f"❌ Error uploading files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PROCESS ENDPOINT (No-op for this RAGService)
# ============================================

@router.post("/process")
async def process_documents():
    """
    Process uploaded documents
    
    Note: This RAGService processes documents automatically.
    This endpoint is kept for API compatibility.
    Documents are indexed on first query.
    """
    try:
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not initialized")
        
        logger.info("📄 Initializing RAG service (if not already done)...")
        
        upload_dir = "backend/uploads"
        if not os.path.exists(upload_dir):
            return {
                "success": True,
                "message": "No documents to process, but RAG service is ready",
                "processed_files": 0,
                "note": "Upload documents first with /upload"
            }
        
        # Get uploaded files
        files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
        
        if not files:
            return {
                "success": True,
                "message": "No documents found in uploads directory",
                "processed_files": 0
            }
        
        logger.info(f"✅ Found {len(files)} documents ready for indexing")
        logger.info(f"✅ Documents will be indexed automatically on first query")
        
        return {
            "success": True,
            "message": f"Found {len(files)} documents. Ready to query.",
            "processed_files": len(files),
            "total_files": len(files),
            "status": "ready"
        }
    
    except Exception as e:
        logger.error(f"❌ Error processing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# QUERY ENDPOINT - MAIN FUNCTIONALITY
# ============================================

@router.post("/query")
async def process_query(request: QueryRequest):
    """
    Send a query to the RAG system
    
    Returns relevant documents and generated answer using LLM
    
    Parameters:
    - query: Your question
    - top_k: Number of relevant documents to retrieve (default: 5)
    - use_history: Use conversation history (default: True)
    """
    try:
        if not rag_service:
            raise HTTPException(
                status_code=500,
                detail="RAG service not initialized. Please upload documents first."
            )
        
        logger.info(f"🔍 Query: {request.query}")
        logger.info(f"   top_k: {request.top_k}")
        logger.info(f"   use_history: {request.use_history}")
        
        # Call the RAGService query method with correct parameters
        result = rag_service.query(
            user_query=request.query,
            top_k=request.top_k,
            use_history=request.use_history
        )
        
        logger.info(f"✅ Query processed successfully")
        
        # Extract response data
        answer = result.get("answer", "No answer generated")
        relevant_docs = result.get("relevant_docs", [])
        request_id = result.get("request_id", "unknown")
        
        return {
            "success": True,
            "query": request.query,
            "answer": answer,
            "relevant_docs": relevant_docs,
            "num_docs_retrieved": len(relevant_docs),
            "request_id": request_id
        }
    
    except RuntimeError as e:
        logger.error(f"❌ RAG Service Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"RAG service error: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"❌ Exception in /query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CLEAR UPLOADS ENDPOINT
# ============================================

@router.delete("/uploads/clear")
async def clear_uploads():
    """Clear uploaded documents"""
    try:
        upload_dir = "backend/uploads"
        
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            os.makedirs(upload_dir, exist_ok=True)
            logger.info("✅ Uploads cleared")
        
        return {
            "success": True,
            "message": "All uploads cleared"
        }
    
    except Exception as e:
        logger.error(f"❌ Error clearing uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CONVERSATION ENDPOINTS
# ============================================

@router.get("/conversation/history")
async def get_conversation_history():
    """Get conversation history"""
    try:
        if not rag_service:
            return {
                "history": [],
                "total_turns": 0
            }
        
        # Use the get_conversation_history method
        history = rag_service.get_conversation_history()
        
        return {
            "success": True,
            "history": history,
            "total_turns": len(history) if history else 0
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/clear")
async def clear_conversation():
    """Clear conversation history"""
    try:
        if rag_service:
            # Use the clear_conversation method
            rag_service.clear_conversation()
            logger.info("✅ Conversation history cleared")
        
        return {
            "success": True,
            "message": "Conversation history cleared"
        }
    
    except Exception as e:
        logger.error(f"❌ Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# STATS ENDPOINT
# ============================================

@router.get("/stats")
async def get_stats():
    """Get RAG service statistics"""
    try:
        if not rag_service:
            return {
                "status": "not_initialized",
                "stats": {}
            }
        
        # Use the get_stats method
        stats = rag_service.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# DEBUG ENDPOINTS
# ============================================

@router.get("/debug/status")
async def debug_status():
    """Check overall RAG system status"""
    try:
        if not rag_service:
            return {
                "status": "not_initialized",
                "message": "RAG service not initialized"
            }
        
        stats = rag_service.get_stats()
        
        return {
            "status": "initialized",
            "rag_service_active": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"❌ Error checking status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# ============================================
# RELEVANCE CHECK ENDPOINT
# ============================================

@router.post("/check-relevance")
async def check_relevance(request: QueryRequest):
    """
    Check relevance of retrieved documents for a query
    
    This is useful for evaluating query quality
    """
    try:
        if not rag_service:
            raise HTTPException(status_code=500, detail="RAG service not initialized")
        
        # First query to get documents
        result = rag_service.query(
            user_query=request.query,
            top_k=request.top_k,
            use_history=False
        )
        
        retrieved_docs = result.get("relevant_docs", [])
        
        # Check relevance using RAGService method
        relevance_scores = rag_service.check_relevance(
            retrieved_docs=retrieved_docs,
            top_k=request.top_k
        )
        
        return {
            "success": True,
            "query": request.query,
            "num_docs": len(retrieved_docs),
            "relevance_scores": relevance_scores
        }
    
    except Exception as e:
        logger.error(f"❌ Error checking relevance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def health_check():
    """Health check for query service"""
    return {
        "service": "RAG Query Service",
        "status": "healthy",
        "rag_service_ready": rag_service is not None
    }