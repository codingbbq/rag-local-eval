from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import routes
from app.services.rag_service import rag_service
from app.utils.logger import logger

# Initialize debug logging based on config
if settings.DEBUG:
    logger.enable_debug(True)

app = FastAPI(title=settings.PROJECT_NAME)

# Get logger for main module
debug_logger = logger.get_logger(__name__)

if settings.DEBUG:
    debug_logger.info("🔧 Debug mode ENABLED")
else:
    debug_logger.info("Debug mode disabled")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    """Initialize RAG service on startup"""
    debug_logger.info("🚀 Starting up RAG service...")
    
    try:
        # Step 1: Initialize RAG service (loads FAISS)
        debug_logger.info("📚 Step 1: Loading FAISS index...")
        rag_service.initialize()
        debug_logger.info("✓ FAISS index loaded")
        
        # Step 2: Initialize hybrid search with FAISS documents
        debug_logger.info("🔑 Step 2: Initializing BM25 for keyword search...")
        from app.services.hybrid_search_service import hybrid_search_service
        from app.config import settings
        
        # Share the embedding store (FAISS)
        hybrid_search_service.embedding_store = rag_service.embedding_store
        
        # Load documents from FAISS to initialize BM25
        try:
            # Get all documents from FAISS docstore
            vectorstore = rag_service.embedding_store.vectorstore
            if vectorstore and hasattr(vectorstore, 'docstore'):
                # Extract documents from FAISS docstore
                docstore = vectorstore.docstore._dict
                documents = list(docstore.values())
                
                if documents:
                    debug_logger.info(f"📖 Found {len(documents)} documents in FAISS")
                    debug_logger.info("⏳ Initializing BM25 index...")
                    hybrid_search_service.initialize(documents)
                    debug_logger.info(f"✓ BM25 initialized with {len(documents)} documents")
                else:
                    debug_logger.warning("⚠️  No documents found in FAISS docstore")
            else:
                debug_logger.warning("⚠️  Could not access FAISS docstore")
        except Exception as e:
            debug_logger.error(f"❌ Error initializing BM25: {str(e)}", exc_info=True)
            debug_logger.warning("⚠️  BM25 initialization failed, will use semantic search only")
        
        debug_logger.info("✅ RAG service fully initialized!")
        
    except Exception as e:
        debug_logger.error(f"❌ Startup error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)