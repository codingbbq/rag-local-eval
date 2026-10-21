"""
FastAPI Backend for RAG Chat with Chat Persistence
Updated to call RAGService.initialize()
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================
# SETUP LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# IMPORTS - Chat Persistence
# ============================================

from app.core.chat_persistence_service import SQLiteBackend
from app.api.chat_persistence_routes import router as chat_router

# ============================================
# IMPORTS - RAG Service & Routes
# ============================================

try:
    from app.services.rag_service import RAGService
    from app.api.routes import router as rag_router, set_rag_service
    logger.info("✅ RAG service and routes imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import RAG service: {e}")
    raise

# ============================================
# CREATE DATA DIRECTORY
# ============================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FAISS_INDEX_DIR = os.path.join(DATA_DIR, 'faiss_index')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
logger.info(f"📁 Data directory: {DATA_DIR}")

# ============================================
# INITIALIZE FASTAPI APP
# ============================================

app = FastAPI(
    title="RAG Chat API",
    description="Retrieval-Augmented Generation Chat with Persistence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================
# CORS MIDDLEWARE
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STARTUP EVENT - Initialize Services
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    logger.info("\n" + "="*70)
    logger.info("🚀 Starting RAG Chat API...")
    logger.info("="*70)
    
    # ============================================
    # 1. INITIALIZE SQLITE DATABASE
    # ============================================
    
    db_path = os.path.join(DATA_DIR, 'chat_history.db')
    
    logger.info(f"\n📦 Step 1: Initializing SQLite Backend...")
    logger.info(f"   Database path: {db_path}")
    
    try:
        sqlite_backend = SQLiteBackend(db_path=db_path)
        logger.info(f"✅ SQLite backend initialized")
        
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            logger.info(f"✅ Database file created ({file_size} bytes)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize SQLite backend: {str(e)}")
        raise
    
    # ============================================
    # 2. INITIALIZE RAG SERVICE
    # ============================================
    
    logger.info(f"\n🔍 Step 2: Initializing RAG Service...")
    
    try:
        # Create RAG service instance
        rag_service = RAGService()
        logger.info(f"✅ RAG Service instance created")
        
        # Call initialize() method
        logger.info(f"   Calling initialize()...")
        rag_service.initialize()
        logger.info(f"✅ RAG Service initialized successfully")
        
        # Set RAG service in routes
        set_rag_service(rag_service)
        logger.info(f"✅ RAG Service set globally for all endpoints")
        
    except AttributeError as e:
        logger.error(f"❌ RAGService method not found: {str(e)}")
        logger.error(f"   Make sure RAGService has initialize() method")
        raise
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {str(e)}")
        raise
    
    # ============================================
    # 3. SUMMARY
    # ============================================
    
    logger.info(f"\n✅ All services initialized successfully!")
    logger.info("="*70)
    logger.info("Ready to handle requests:")
    logger.info("  - POST /api/v1/upload         → Upload documents")
    logger.info("  - POST /api/v1/process        → Process documents (optional)")
    logger.info("  - POST /api/v1/query          → Ask questions (documents indexed on first query)")
    logger.info("  - POST /api/v1/chat/session/create  → Create chat session")
    logger.info("="*70 + "\n")

# ============================================
# SHUTDOWN EVENT
# ============================================

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down RAG Chat API...")

# ============================================
# INCLUDE ROUTERS
# ============================================

logger.info("📡 Including routers...")
app.include_router(chat_router)
app.include_router(rag_router)
logger.info("✅ All routers included")

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    db_path = os.path.join(DATA_DIR, 'chat_history.db')
    
    return {
        "status": "ok",
        "service": "RAG Chat API",
        "database": {
            "type": "SQLite",
            "exists": os.path.exists(db_path)
        },
        "rag_service": {
            "initialized": True
        },
        "version": "1.0.0"
    }

# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Chat API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# ============================================
# STATUS ENDPOINTS
# ============================================

@app.get("/api/v1/status/database")
async def database_status():
    """Check database status"""
    db_path = os.path.join(DATA_DIR, 'chat_history.db')
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        return {
            "status": "ready",
            "database": "SQLite",
            "exists": True,
            "size_bytes": file_size
        }
    else:
        return {
            "status": "not_initialized",
            "database": "SQLite",
            "exists": False
        }

@app.get("/api/v1/status/rag")
async def rag_status():
    """Check RAG service status"""
    return {
        "status": "ready",
        "rag_service": "initialized",
        "note": "Documents are processed automatically on first query"
    }

# ============================================
# ENDPOINTS LIST
# ============================================

@app.get("/api/v1/endpoints")
async def list_endpoints():
    """List all available endpoints"""
    return {
        "query_endpoints": {
            "POST /api/v1/upload": "Upload documents",
            "POST /api/v1/process": "Process documents (compatibility endpoint)",
            "POST /api/v1/query": "Send a question to RAG",
            "DELETE /api/v1/conversation/clear": "Clear conversation history",
            "GET /api/v1/conversation/history": "Get conversation history",
            "GET /api/v1/stats": "Get RAG statistics"
        },
        "chat_persistence": {
            "POST /api/v1/chat/session/create": "Create new chat session",
            "GET /api/v1/chat/sessions/list": "List all sessions",
            "POST /api/v1/chat/message/add": "Add message to session"
        },
        "system": {
            "GET /api/v1/health": "Health check",
            "GET /api/v1/status/rag": "RAG service status",
            "GET /api/v1/status/database": "Database status"
        }
    }

# ============================================
# ERROR HANDLER
# ============================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "detail": str(exc)
    }

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )