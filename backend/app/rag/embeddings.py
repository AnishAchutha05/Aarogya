"""Embedding service using Google embedding-001 model."""

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_SIZE = settings.QDRANT_VECTOR_SIZE


class EmbeddingService:
    """
    Generates text embeddings.
    Uses Google embedding-001 (768 dimensions) by default.
    Falls back to a zero vector for graceful degradation in tests.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._embedder = None

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._embedder = GoogleGenerativeAIEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    google_api_key=self.api_key,
                )
            except Exception as e:
                logger.warning("Embedding service init failed: %s", e)
                self._embedder = None
        return self._embedder

    async def embed(self, text: str) -> list[float]:
        """Embed a single text string. Returns list of floats."""
        embedder = self._get_embedder()
        if embedder is None:
            logger.warning("Embedding service unavailable - returning zero vector")
            return [0.0] * EMBEDDING_SIZE
        try:
            vector = await embedder.aembed_query(text)
            return vector
        except Exception as e:
            logger.error("Embedding failed: %s", type(e).__name__)
            return [0.0] * EMBEDDING_SIZE

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts."""
        embedder = self._get_embedder()
        if embedder is None:
            return [[0.0] * EMBEDDING_SIZE for _ in texts]
        try:
            vectors = await embedder.aembed_documents(texts)
            return vectors
        except Exception as e:
            logger.error("Batch embedding failed: %s", type(e).__name__)
            return [[0.0] * EMBEDDING_SIZE for _ in texts]


# Default instance - no API key (uses env var or GOOGLE_API_KEY)
embedding_service = EmbeddingService()
