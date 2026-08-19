from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or defaults.
    """
    APP_NAME: str = "RAG-Chatbot"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"

    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]

    # Model & Storage Settings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    VECTOR_DB_DIR: str = "app/storage/chroma_db"
    COLLECTION_NAME: str = "rag_documents"

    # LLM Settings (Groq API)
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL_NAME: str = "llama-3.3-70b-versatile"
    LLM_MAX_TOKENS: int = 800  # response length cap -> fewer output tokens per call

    # RAG Retrieval / Context Budget Settings
    # These exist to keep every chat call's token usage predictable, since
    # Groq (and most providers) bill/rate-limit on total tokens per day.
    RAG_TOP_K: int = 3              # chunks retrieved per query
    RAG_SCORE_THRESHOLD: float = 0.15  # drop barely-relevant chunks before they reach the LLM
    RAG_RELATIVE_SCORE_CUTOFF: float = 0.6  # also drop chunks scoring below 60% of the top match's score, so a source that's only loosely related to THIS question doesn't tag along just because it cleared the absolute floor
    RAG_MAX_CONTEXT_CHARS: int = 3000  # hard cap on combined chunk text sent to the LLM (~750 tokens)
    CHAT_HISTORY_MAX_MESSAGES: int = 6      # how many past turns to keep (was 10)
    CHAT_HISTORY_MAX_CHARS_PER_MSG: int = 300  # truncate each past message before re-sending it

    # Ingestion Defaults
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 200

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOADS_DIR: str = "data/uploads"
    PROCESSED_DIR: str = "data/processed"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
