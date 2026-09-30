# Local Llama RAG POC

A **Retrieval-Augmented Generation (RAG)** system using local Llama2 LLM for document question-answering with quality evaluation.

## What This Project Does

Builds an intelligent chatbot that:
1. **Loads your documents** (TXT files)
2. **Indexes them** using embeddings and FAISS vector database
3. **Retrieves relevant passages** when you ask questions
4. **Generates grounded answers** using local Llama2 (no API keys)
5. **Evaluates answer quality** with metrics (faithfulness, relevancy, precision)

**Key insight**: Answers are grounded in your documents, not hallucinated by the LLM.

## Quick Start

```bash
# 1. Install Ollama and download model
ollama pull llama2
ollama serve

# 2. Setup (one-time)
python setup_rag.py

# 3. Test
python test_evaluator.py

# 4. Deploy
python app.py
# Open frontend.html in browser
```

## What I'm Learning

### Core Concepts
- **Retrieval-Augmented Generation** — How to ground LLM outputs in documents
- **Embeddings** — Converting text to vectors for semantic search
- **Vector Databases** — Fast similarity search with FAISS
- **LangChain** — Building composable AI applications
- **Evaluation Metrics** — Measuring AI system quality objectively
- **Local LLMs** — Running large models offline without API costs

### Engineering Skills
- **System Architecture** — Designing multi-component AI systems
- **Observability** — Logging and monitoring ML pipelines
- **API Design** — Building REST interfaces
- **Persistent Storage** — Saving/loading FAISS indices
- **Evaluation Framework** — Measuring quality at each stage

### Practical Implementation
- How embedding models work and why similarity matters
- How to chunk documents intelligently
- How to design prompts for grounded generation
- How to measure and improve RAG quality
- How to structure code for iterative improvement

## Project Structure

```
rag_local_llama/
├── Core modules (your implementation)
│   ├── document_processor.py      # Load & chunk docs
│   ├── embedding_store.py         # Embeddings + FAISS
│   ├── rag_chain.py              # RAG pipeline + Llama2
│   ├── evaluator.py              # Quality metrics
│   └── instrumentation.py        # Logging
│
├── Setup & Testing
│   ├── setup_rag.py              # One-time doc processing
│   ├── test_*.py                 # Unit & integration tests
│   └── debug_faiss.py            # Inspect FAISS index
│
├── Application
│   ├── app.py                    # Flask backend
│   ├── frontend.html             # Web UI
│
└── Data
    ├── unica_*.txt               # Sample documents
    └── faiss_index/              # Persistent vectors
```

## Evaluation Metrics

System quality is measured by:

| Metric | Meaning | Target |
|--------|---------|--------|
| **Faithfulness** | Is answer grounded in context? | 0.8+ |
| **Answer Relevancy** | Does it answer the question? | 0.8+ |
| **Context Precision** | Are retrieved docs useful? | 0.7+ |

## Technology Stack

- **LLM**: Llama2 (via Ollama) — local, no costs
- **Embeddings**: sentence-transformers — local, free
- **Vector DB**: FAISS — fast, simple
- **Framework**: LangChain — composable, flexible
- **Backend**: Flask — lightweight
- **Frontend**: HTML/JS — no build step

## Why Each Component?

**Document Processor**: Intelligently chunks documents (1000 chars, 200 char overlap) to balance precision and context.

**Embedding Store**: Uses pre-trained embeddings locally. Saves/loads FAISS index for persistence.

**RAG Chain**: Retrieves top-5 similar documents, builds augmented prompt, calls Llama2. Returns grounded answer.

**Evaluator**: Measures quality with word overlap heuristics (fast, deterministic, no extra LLM calls).

**Instrumentation**: Logs everything to JSON for debugging and optimization.

## How It Works

```
Setup Phase (One-Time):
Documents → Chunk → Embed → FAISS Index (saved to disk)

Query Phase (Every Request):
User Question → Embed → Search FAISS → Retrieve → 
Build Prompt → Call Llama2 → Generate Answer → Evaluate
```

## Expected Performance

- **Setup time**: ~10 seconds (sample docs)
- **Query latency**: ~20-30 seconds (Llama2 is CPU-bound)
- **Quality scores**: Typically 0.75-0.85 overall
- **Storage**: ~100 KB per 1000 chunks

## Next Improvements

- [ ] Add PDF support (currently TXT only)
- [ ] Implement reranking (better retrieval)
- [ ] Add caching (faster repeated queries)
- [ ] Support multi-turn conversations
- [ ] Migrate to production vector DB (Pinecone/Weaviate)
- [ ] Use better evaluation metrics
- [ ] Optimize prompts for better answers

## Learning Resources

- **RAG**: [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401)
- **Embeddings**: [Sentence Transformers](https://www.sbert.net/)
- **FAISS**: [GitHub](https://github.com/facebookresearch/faiss)
- **LangChain**: [Official Docs](https://python.langchain.com/)

## Running the Project

```bash
# One-time setup
python setup_rag.py

# Test the pipeline
python test_evaluator.py

# Run backend
python app.py

# Use the system
# → Open frontend.html in browser
```

## Notes

- **Ollama must be running**: Keep `ollama serve` in a separate terminal
- **First run is slow**: Llama2 generation takes 10-30 seconds per query
- **CPU-bound**: Local inference is slower than cloud APIs but no costs
- **Evaluation is heuristic-based**: Word overlap, not LLM as judge (for speed)

---

**Built to understand RAG engineering from first principles.**

This is a learning project. As I improve the architecture and implement better components, this README will evolve.
