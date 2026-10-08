import os
from pathlib import Path
from typing import List, Tuple
import shutil
from app.config import settings
from app.core.document_processor import DocumentProcessor
from app.core.embedding_store import EmbeddingStore
from app.utils.logger import logger

debug_logger = logger.get_logger(__name__)

class UploadService:
    """Handles document upload and processing"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.processor = DocumentProcessor()
        self.embedding_store = EmbeddingStore()
        self.uploaded_files = []
    
    def save_uploaded_files(self, files: List) -> Tuple[List[str], float]:
        """
        Save uploaded files to disk
        
        Args:
            files: List of uploaded files from FastAPI
            
        Returns:
            Tuple of (file_names, total_size_mb)
        """
        file_names = []
        total_size = 0
        
        for file in files:
            # Validate file extension
            file_path = Path(file.filename)
            if file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
                debug_logger.warning(f"⚠️  Skipping invalid file: {file.filename}")
                continue
            
            # Save file
            save_path = self.upload_dir / file.filename
            try:
                with open(save_path, 'wb') as f:
                    content = file.file.read()
                    f.write(content)
                    total_size += len(content)
                    file_names.append(file.filename)
                    self.uploaded_files.append(str(save_path))
                    debug_logger.info(f"✓ Saved file: {file.filename} ({len(content) / 1024 / 1024:.2f} MB)")
            except Exception as e:
                debug_logger.error(f"❌ Error saving file {file.filename}: {str(e)}")
                raise
        
        return file_names, total_size / 1024 / 1024  # Convert to MB
    
    def process_documents(self, chunk_size: int = 1000, 
                         chunk_overlap: int = 200,
                         reload_faiss: bool = True) -> dict:
        """
        Process uploaded documents and create embeddings
        
        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks
            reload_faiss: Whether to reload FAISS after processing
            
        Returns:
            Dict with processing results
        """
        if not self.uploaded_files:
            raise ValueError("No files uploaded for processing")
        
        try:
            # Step 1: Load documents
            debug_logger.info(f"📄 Loading {len(self.uploaded_files)} documents...")
            documents = self.processor.load_documents(self.uploaded_files)
            debug_logger.info(f"✓ Loaded {len(documents)} pages")
            
            # Step 2: Chunk documents
            debug_logger.info(f"🔪 Chunking with size={chunk_size}, overlap={chunk_overlap}...")
            chunks = self.processor.chunk_documents(
                documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            debug_logger.info(f"✓ Created {len(chunks)} chunks")
            
            # Step 3: Create embeddings
            debug_logger.info("🧠 Creating embeddings...")
            self.embedding_store.create_vectorstore(chunks)
            debug_logger.info("✓ Embeddings created")
            
            # Step 4: Save to disk
            debug_logger.info("💾 Saving FAISS index...")
            self.embedding_store.save_vectorstore(str(settings.FAISS_INDEX_PATH))
            debug_logger.info("✓ FAISS index saved")
            
            # Step 5: Get stats
            total_vectors = self.embedding_store.vectorstore.index.ntotal
            debug_logger.info(f"✅ Processing complete! {total_vectors} vectors in index")
            
            # Clear uploaded files list
            self.uploaded_files = []
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(chunks),
                "embeddings_created": total_vectors,
                "total_vectors_in_index": total_vectors,
                "message": f"Successfully indexed {len(documents)} documents into {len(chunks)} chunks"
            }
            
        except Exception as e:
            debug_logger.error(f"❌ Error processing documents: {str(e)}", exc_info=True)
            raise
    
    def get_uploaded_files_info(self) -> dict:
        """Get info about currently uploaded files"""
        total_size = 0
        for file_path in self.uploaded_files:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        return {
            "files_uploaded": len(self.uploaded_files),
            "file_names": [Path(f).name for f in self.uploaded_files],
            "total_size_mb": total_size / 1024 / 1024
        }
    
    def clear_uploads(self):
        """Clear uploaded files"""
        for file_path in self.uploaded_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                debug_logger.warning(f"Could not delete {file_path}: {str(e)}")
        
        self.uploaded_files = []
        debug_logger.info("Cleared uploaded files")

# Global service instance
upload_service = UploadService()