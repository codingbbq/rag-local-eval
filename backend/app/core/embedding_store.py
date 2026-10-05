import os
import faiss
import pickle
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS as FAISSVectorStore
# Create langchain FAISS wrapper
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore

class EmbeddingStore:
    """
    Manages embeddings and vector storage.
    
    Process:
    1. Initialize embedding model
    2. Embed chunks (text → vectors)
    3. Store in FAISS index
    4. Retrieve similar chunks on query
    """
    
    def __init__(self):
        """
        Initialize the embedding model.
        
        First run: Downloads model (~22 MB)
        Future runs: Uses cached model (fast)
        """
        print("🔧 Initializing embeddings...")
        print("   Model: sentence-transformers/all-MiniLM-L6-v2")
        print("   (First run downloads ~22 MB, then cached)")
        
        try:
            # HuggingFaceEmbeddings creates embeddings locally
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}  # Use CPU (not GPU)
            )
            print("   ✓ Embeddings model loaded")
            self.vectorstore = None  # Will be created later
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise


    def create_vectorstore(self, chunks: List[Document]) -> FAISS:
        """
        Create FAISS index from chunks.
        
        What happens:
        1. Embed each chunk (text → 384-dim vector)
        2. Index vectors for fast retrieval
        3. Store metadata (which chunk came from which doc)
        
        Args:
            chunks: List of Document chunks (from DocumentProcessor)
        
        Returns:
            FAISS vectorstore object
        """
        print(f"\n🗂️  Creating vector store from {len(chunks)} chunks...")
        
        try:
            # This embeds all chunks and creates FAISS index
            # Might take 30 seconds - 2 minutes depending on chunk count
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            print(f"   ✓ Vector store created with {len(chunks)} documents")
            return self.vectorstore
        
        except Exception as e:
            print(f"   ❌ Error creating vector store: {e}")
            raise

    
    def get_retriever(self, k: int = 5):
        """
        Get a retriever for similarity search.
        
        What it does:
        1. Take user query
        2. Embed the query (text → vector)
        3. Find k nearest vectors in FAISS
        4. Return top-k most similar chunks
        
        Args:
            k: Number of chunks to retrieve (default 5)
        
        Returns:
            LangChain retriever object
        
        Typical k values:
        - k=3: Fast, concise context
        - k=5: Balanced (default)
        - k=10: More context, slower
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not created yet. Call create_vectorstore first.")
        
        print(f"\n🔍 Creating retriever (k={k})...")
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        print(f"   ✓ Retriever ready (will return top-{k} similar chunks)")
        return retriever

    
    def test_retrieval(self, retriever, test_query: str):
        """
        Test retrieval on a sample query.
        
        Useful to verify:
        - Are retrieved chunks relevant?
        - Is embedding/retrieval working?
        
        Args:
            retriever: The retriever object
            test_query: A test question to search for
        """
        print(f"\n🧪 Testing retrieval with query: '{test_query}'")
        
        try:
            # Invoke retriever with the query
            docs = retriever.invoke(test_query)
            
            print(f"   Retrieved {len(docs)} documents:")
            
            for i, doc in enumerate(docs, 1):
                # Show first 300 chars of each result
                preview = doc.page_content[:300].replace('\n', ' ')
                print(f"\n   [{i}] {preview}...")
            
            return docs
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []



    def save_vectorstore(self, path: str = "faiss_index"):
        """
        Save FAISS index to disk for later use.
        
        Args:
            path: Directory to save index files
        """
        if self.vectorstore is None:
            print("❌ No vectorstore to save")
            return
        
        os.makedirs(path, exist_ok=True)
        
        print(f"\n💾 Saving FAISS index to {path}/...")
        
        try:
            # Save the FAISS index
            faiss.write_index(
                self.vectorstore.index,
                os.path.join(path, "index.faiss")
            )
            print(f"   ✓ FAISS index saved")
            
            # Save the docstore (chunk content and metadata)
            with open(os.path.join(path, "docstore.pkl"), "wb") as f:
                pickle.dump(self.vectorstore.docstore._dict, f)
            print(f"   ✓ Docstore saved")
            
            # Save the index to docstore mapping
            with open(os.path.join(path, "index_to_docstore_id.pkl"), "wb") as f:
                pickle.dump(self.vectorstore.index_to_docstore_id, f)
            print(f"   ✓ Index mapping saved")
            
            num_vectors = self.vectorstore.index.ntotal
            print(f"\n✓ Saved {num_vectors} vectors to {path}/")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()


    
    def load_vectorstore(self, path: str = "faiss_index"):
        """
        Load FAISS index from disk.
        
        Args:
            path: Directory where index files are saved
        
        Returns:
            True if successful, False otherwise
        """
        
        print(f"\n📂 Loading FAISS index from {path}/...")
        
        try:
            # Check if files exist
            index_path = os.path.join(path, "index.faiss")
            docstore_path = os.path.join(path, "docstore.pkl")
            mapping_path = os.path.join(path, "index_to_docstore_id.pkl")
            
            if not os.path.exists(index_path):
                print(f"   ❌ Index file not found: {index_path}")
                return False
            
            # Load FAISS index
            index = faiss.read_index(index_path)
            print(f"   ✓ Index loaded ({index.ntotal} vectors)")
            
            # Load docstore
            with open(docstore_path, "rb") as f:
                docstore_dict = pickle.load(f)
            print(f"   ✓ Docstore loaded")
            
            # Load mapping
            with open(mapping_path, "rb") as f:
                index_to_docstore_id = pickle.load(f)
            print(f"   ✓ Index mapping loaded")
            
            # Recreate docstore
            docstore = InMemoryDocstore()
            for key, content in docstore_dict.items():
                if isinstance(content, dict):
                    docstore.add({key: Document(page_content=content.get("page_content", ""))})
                else:
                    docstore.add({key: content})
            
            # Create FAISS vectorstore
            self.vectorstore = FAISSVectorStore(
                embedding_function=self.embeddings.embed_query,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id
            )
            
            print(f"\n✓ Successfully loaded {index.ntotal} vectors from {path}/")
            return True
            
        except Exception as e:
            print(f"   ❌ Error loading: {e}")
            import traceback
            traceback.print_exc()
            return False