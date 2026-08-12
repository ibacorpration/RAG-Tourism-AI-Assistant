# RAG System Architecture & Technical Specifications

## Overview
This document provides a technical walkthrough of the Enterprise RAG-Chatbot architecture.

```
+----------------+      +-------------------+      +------------------+
|  User Query    | ---> | Context Retriever | ---> |  Top-K Context   |
| (API / Web UI) |      | (Similarity/MMR)  |      |     Chunks       |
+----------------+      +-------------------+      +------------------+
        |                         |                         |
        v                         v                         v
+----------------+      +-------------------+      +------------------+
| Groq LLM Engine| <--- | Prompt Generator  | <--- |   ChromaDB Store |
|  (Llama 3.3)   |      |  & System Prompt  |      |   (Embeddings)   |
+----------------+      +-------------------+      +------------------+
```

## Data Ingestion Pipeline
1. **Document Loading**: `LoaderFactory` detects file extension (`.pdf`, `.txt`, `.md`, `.json`) and delegates parsing to specialized loaders (`PDFLoader`, `TextLoader`).
2. **Text Chunking**: `TextSplitter` recursively splits documents based on paragraph, sentence, and word boundaries with specified `chunk_size` and `chunk_overlap`.
3. **Embedding Generation**: `SentenceTransformerEmbedding` generates 384-dimensional vector embeddings using `all-MiniLM-L6-v2`.
4. **Vector Upsert**: `ChromaVectorStore` stores vector embeddings, document text, and metadata inside persistent collection `rag_documents`.

## Retrieval & Generation Pipeline
1. **Query Embedding**: The query is converted into a vector embedding.
2. **Context Retrieval**: The retriever executes similarity or MMR search against ChromaDB.
3. **Prompt Construction**: `RAGChatService` injects the retrieved context chunks and conversation history into the RAG system prompt.
4. **Groq LLM Generation**: `GroqLLMProvider` calls the Groq API for sub-second text or stream generation.
5. **Session Memory**: Updates sliding window memory for the active `conversation_id`.

## Key API Endpoints
- `GET /api/v1/health`: System health status.
- `POST /api/v1/upload`: Upload and index document files.
- `POST /api/v1/embeddings/search`: Query raw vector index and inspect retrieved chunks.
- `GET /api/v1/embeddings/stats`: Inspect vector store metrics.
- `POST /api/v1/chat`: Synchronous RAG chat completion.
- `POST /api/v1/chat/stream`: SSE Streaming RAG chat completion.
- `DELETE /api/v1/chat/history/{conversation_id}`: Clear session conversation history.
