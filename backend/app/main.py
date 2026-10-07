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
    debug_logger.info("Starting up RAG service...")
    rag_service.initialize()
    debug_logger.info("✓ RAG service initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)