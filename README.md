# 🚀 RAG System Tourism AI Assistant [Full Production]

<img src="https://github.com/user-attachments/assets/fef43936-73eb-4353-9ff2-6219edd62061" alt="Tourism AI Assistant" width="100%" />

A production-ready **Retrieval-Augmented Generation (RAG) System** built with **FastAPI**, **ChromaDB**, **SentenceTransformers**, and **Groq API** (`llama-3.3-70b-versatile`).

---

## 🌐 Live

The project is deployed and running live on **Railway**:

🔗 **[https://rag-system-production-bb18.up.railway.app/](https://tourism-ai-assistant-production.up.railway.app/)**

---

## 🌟 Main Features

- **⚡ Fast Inference**: Exclusively powered by **Groq API** for sub-second Llama-3 LLM responses.
- **📄 Multi-Format Ingestion**: Supports PDF (`.pdf`), Plain Text (`.txt`), Markdown (`.md`), and JSON documents.
- **🧩 Smart Text Chunking**: Recursive character splitting with configurable chunk sizes and overlap.
- **🔍 Dual Retrieval Engine**: Supports standard **Cosine Similarity Search** and **Maximal Marginal Relevance (MMR)** for context diversity.
- **💾 Persistent Vector Store**: Local persistent ChromaDB vector store saved in `app/storage/chroma_db/`.
- **💬 Session Memory**: Sliding window conversation history per `conversation_id`.
- **🖥️ Interactive Dashboard**: Dark glassmorphism web UI at `http://localhost:8000/` for uploading documents and live chatting with source citations.
- **📡 Real-Time Streaming**: Server-Sent Events (SSE) streaming API at `/api/v1/chat/stream`.

---

## 📂 Project Architecture

```
RAG_System/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py        # GET /api/v1/health
│   │   │   ├── upload.py        # POST /api/v1/upload
│   │   │   ├── embeddings.py    # POST /api/v1/embeddings/search & GET /stats
│   │   │   └── chat.py          # POST /api/v1/chat & POST /api/v1/chat/stream
│   │   ├── dependencies.py      # FastAPI Dependency Injection
│   │   └── router.py            # Aggregate API v1 Router
│   │
│   ├── core/
│   │   ├── config.py            # App settings (Pydantic BaseSettings)
│   │   ├── logger.py            # Console & File logger (`logs/app.log`)
│   │   ├── security.py          # CORS setup
│   │   ├── constants.py         # Extensions & default values
│   │   └── exceptions.py        # Custom RAG application exceptions
│   │
│   ├── schemas/
│   │   ├── health.py            # Health status schema
│   │   ├── upload.py            # File upload response schema
│   │   ├── embeddings.py        # Vector search schemas
│   │   └── chat.py              # Chat completion request/response schemas
│   │
│   ├── services/
│   │   ├── documents/           # Document & DocumentChunk entities
│   │   ├── loaders/             # PDF, Text, Markdown parsers & factory
│   │   ├── splitters/           # Recursive text chunking
│   │   ├── embeddings/          # SentenceTransformers (`all-MiniLM-L6-v2`)
│   │   ├── vector_store/        # ChromaDB persistent store
│   │   ├── retrievers/          # Similarity & MMR retrievers
│   │   ├── llms/                # Dedicated Groq LLM Provider
│   │   ├── memory/              # Sliding window session memory
│   │   └── rag/                 # RAG & Chat orchestrators
│   │
│   ├── static/                  # Web Dashboard UI (`index.html`)
│   ├── storage/                 # Persistent ChromaDB data
│   └── main.py                  # FastAPI Application Entrypoint
│
├── data/                        # Uploads & sample documents
├── logs/                        # System log files
├── scripts/                     # CLI tools (`ingest.py`)
├── tests/                       # Automated Pytest suite
├── requirements/                # Project dependencies (`base.txt`)
├── .env                         # Active environment configuration
└── README.md                    # Documentation
```

---

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Groq API Key
Edit `.env` and insert your Groq API key:
```env
GROQ_API_KEY="gsk_your_groq_api_key_here"
GROQ_MODEL_NAME="llama-3.3-70b-versatile"
```

### 3. Run the Application
Launch the FastAPI server:
```bash
python app/main.py
```
Or with uvicorn:
```bash
uvicorn app.main:app --reload --reload-exclude "data/*" --reload-exclude "logs/*" --reload-exclude "app/storage/*" --host 0.0.0.0 --port 8000
```

### 4. Access Interfaces
- **Web UI Dashboard**: Open [http://localhost:8000/](http://localhost:8000/) in your browser.
- **Swagger Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ CLI Ingestion Script

To index documents directly from the command line:
```bash
python scripts/ingest.py --path data/samples/
```

---

## 🧪 Running Tests

Run the automated test suite:
```bash
python -m pytest tests/ -v
```

---

## 🚢 Deployment (Server / Railway)

### ✅ Currently Deployed On Railway
This project is **live** at: [https://rag-system-production-bb18.up.railway.app/](https://rag-system-production-bb18.up.railway.app/)

### Option A — Railway (recommended, fastest)
Railway builds straight from the `Dockerfile` already in this repo — no extra config needed.

1. Push this repo to GitHub (see steps above).
2. On [railway.app](https://railway.app), create a **New Project → Deploy from GitHub repo** and pick this repo.
3. Railway detects the `Dockerfile` and builds automatically.
4. Under **Variables**, add your environment variables (copy them from `.env.example`), at minimum:
   ```
   GROQ_API_KEY=your_real_key
   GROQ_MODEL_NAME=llama-3.3-70b-versatile
   ENVIRONMENT=production
   ```
5. Railway injects `PORT` automatically — the app already reads it via `app/main.py`, and the `Dockerfile`'s `gunicorn` command binds to `0.0.0.0:8000`, which Railway maps for you. No changes needed.
6. Add a **Volume** mounted at `/app/app/storage` (and optionally `/app/data/uploads`) so your ChromaDB vector store and uploaded documents persist across redeploys.
7. Once deployed, Railway gives you a public URL — that's your live API and dashboard.

### Option B — Any other server (VPS / Docker)
```bash
# build & run, with .env providing GROQ_API_KEY etc.
docker compose up -d --build
```
This mounts `data/uploads`, `data/processed`, `app/storage`, and `logs` as volumes so your vector DB and uploaded documents survive container restarts.

Or without Docker, straight on a VPS:
```bash
pip install -r requirements.txt
export ENVIRONMENT=production
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 2
```
Put Nginx (or Caddy) in front as a reverse proxy for TLS and a domain name. Set `ENVIRONMENT=production` so the app disables the dev auto-reloader.

### Notes
- Never commit `.env` — only `.env.example` is tracked. Set the real values as environment variables on whichever platform you deploy to.
- On PaaS platforms that assign a dynamic port (Railway, Render, Fly.io), the app reads `$PORT` automatically.
- `CORS_ORIGINS=["*"]` is fine for local development; for a public deployment, restrict it to your actual frontend domain(s) via the `CORS_ORIGINS` environment variable.
