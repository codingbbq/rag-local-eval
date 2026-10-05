from document_processor import DocumentProcessor

# Initialize processor with default chunk size
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

# Load the documents you created earlier
files = ["unica_overview.txt", "unica_best_practices.txt"]
documents = processor.load_documents(files)

# Chunk them
chunks = processor.chunk_documents(documents)

# Preview first chunk
if chunks:
    processor.preview_chunk(chunks[0], index=0)
    print("\n✓ Test completed successfully!")