FROM python:3.10-slim

# System deps needed by chromadb / sentence-transformers builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Ensure runtime folders exist even if empty on a fresh clone
RUN mkdir -p data/uploads data/processed logs app/storage/chroma_db

ENV ENVIRONMENT=production
EXPOSE 8000

# gunicorn manages uvicorn workers in production; adjust --workers to your CPU count
CMD ["gunicorn", "app.main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
