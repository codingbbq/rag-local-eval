from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

class DocumentProcessor:
    """
    Loads documents and splits them into chunks.
    
    Why a class?
    - Reusable: create once, use many times
    - State: remembers chunk_size and chunk_overlap
    - Methods: separate concerns (load vs chunk)
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the processor with chunk parameters.
        
        Args:
            chunk_size: How many characters per chunk (default 1000)
            chunk_overlap: How many chars to repeat in next chunk (default 200)
        
        Why these defaults?
        - 1000 chars ≈ 150-200 words ≈ 250 tokens
        - 200 chars overlap ≈ 30 words (ensures context continuity)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create the splitter with recursive strategy
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]  # Order matters!
        )
        
        print(f"✓ DocumentProcessor initialized")
        print(f"  • chunk_size: {chunk_size} chars")
        print(f"  • chunk_overlap: {chunk_overlap} chars")


    

    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Load documents from TXT files.
        
        Args:
            file_paths: List of file paths to load
                Example: ["doc1.txt", "doc2.txt"]
        
        Returns:
            List of Document objects with content and metadata
        
        Note: For PDF, use PyPDFLoader instead of TextLoader
        """
        documents = []
        
        for file_path in file_paths:
            print(f"\n📄 Loading {file_path}...")
            
            try:
                # TextLoader reads the entire file as one document
                loader = TextLoader(file_path)
                docs = loader.load()
                documents.extend(docs)  # Add to our list
                print(f"   ✓ Loaded {len(docs)} document(s)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        total_chars = sum(len(d.page_content) for d in documents)
        print(f"\n✓ Loaded {len(documents)} documents ({total_chars} chars total)")
        return documents


    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks.
        
        Args:
            documents: List of Document objects (from load_documents)
        
        Returns:
            List of chunks (each chunk is a Document)
        
        Why return List[Document]?
        - Each chunk needs metadata (which file it came from)
        - Document objects preserve this info
        """
        print(f"\n🔪 Chunking {len(documents)} document(s)...")
        print(f"   Parameters: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
        
        # Use the splitter to break documents into chunks
        chunks = self.splitter.split_documents(documents)
        
        print(f"   ✓ Created {len(chunks)} chunks")
        
        # Show statistics
        chunk_sizes = [len(c.page_content) for c in chunks]
        print(f"\n   📊 Chunk Statistics:")
        print(f"      • Smallest: {min(chunk_sizes)} chars")
        print(f"      • Largest: {max(chunk_sizes)} chars")
        print(f"      • Average: {sum(chunk_sizes)//len(chunk_sizes)} chars")
        
        return chunks

    def preview_chunk(self, chunk: Document, index: int = 0):
        """
        Print a preview of a single chunk (useful for debugging).
        
        Args:
            chunk: The Document chunk to preview
            index: Which chunk number (for display)
        """
        print(f"\n📝 Chunk {index} Preview:")
        print(f"   Size: {len(chunk.page_content)} chars")
        print(f"   Content:")
        print(f"   {chunk.page_content[:300]}...")  # First 300 chars