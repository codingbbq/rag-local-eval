from typing import List
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
    
    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Load documents from various file types
        
        Args:
            file_paths: List of file paths (supports .txt, .pdf, .md)
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load based on file extension
            if path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(path))
            elif path.suffix.lower() in ['.txt', '.md']:
                loader = TextLoader(str(path), encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
            
            docs = loader.load()
            documents.extend(docs)
            print(f"📄 Loaded {path.name}: {len(docs)} pages")
        
        return documents
    
    def chunk_documents(self, documents: List[Document], 
                       chunk_size: int = None, 
                       chunk_overlap: int = None) -> List[Document]:
        """
        Split documents into chunks
        
        Args:
            documents: List of documents
            chunk_size: Override chunk size
            chunk_overlap: Override chunk overlap
            
        Returns:
            List of chunked documents
        """
        if chunk_size:
            self.chunk_size = chunk_size
        if chunk_overlap:
            self.chunk_overlap = chunk_overlap
        
        # Recreate splitter with new settings
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
        
        chunks = self.splitter.split_documents(documents)
        print(f"🔪 Created {len(chunks)} chunks")
        return chunks
    
    def preview_chunk(self, chunks: List[Document], index: int = 0) -> str:
        """Preview a specific chunk"""
        if index >= len(chunks):
            return "Index out of range"
        return chunks[index].page_content