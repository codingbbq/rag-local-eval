import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.document_processor import DocumentProcessor
from app.config import settings

# Initialize processor with default chunk size
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

# Load the documents you created earlier
files = [str(settings.DATA_DIR / "unica_overview.txt"), str(settings.DATA_DIR / "unica_best_practices.txt")]
documents = processor.load_documents(files)

# Chunk them
chunks = processor.chunk_documents(documents)

# Preview first chunk
if chunks:
    processor.preview_chunk(chunks[0], index=0)
    print("\n✓ Test completed successfully!")