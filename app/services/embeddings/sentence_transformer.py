from typing import List
from sentence_transformers import SentenceTransformer
from app.services.embeddings.base import BaseEmbeddingProvider
from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logger import logger


class SentenceTransformerEmbedding(BaseEmbeddingProvider):
    """
    Embedding Provider wrapping HuggingFace SentenceTransformers models.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        try:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model '{self.model_name}': {e}")
            raise EmbeddingError(f"Embedding model initialization failed: {e}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings for documents: {e}")
            raise EmbeddingError(f"Document embedding generation failed: {e}")

    def embed_query(self, query: str) -> List[float]:
        if not query:
            return []
        try:
            embedding = self.model.encode(query, show_progress_bar=False, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            raise EmbeddnigError(f"Query embedding generation failed: {e}")
