"""Qdrant client and collection management."""

import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def get_qdrant_client():
    """Get or create the shared Qdrant client."""
    global _client
    if _client is None:
        from qdrant_client import QdrantClient
        _client = QdrantClient(url=settings.QDRANT_URL, timeout=10)
    return _client


def check_qdrant_connection() -> bool:
    """Health check: verifies Qdrant connectivity."""
    try:
        client = get_qdrant_client()
        client.get_collections()
        return True
    except Exception:
        return False


def ensure_collections() -> None:
    """
    Create required Qdrant collections if they don't exist.
    Called on application startup.
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        client = get_qdrant_client()
        existing = {c.name for c in client.get_collections().collections}

        for collection_name in [
            settings.QDRANT_WELLNESS_COLLECTION,
            settings.QDRANT_MEMORY_COLLECTION,
        ]:
            if collection_name not in existing:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.QDRANT_VECTOR_SIZE,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info("Created Qdrant collection: %s", collection_name)
            else:
                logger.debug("Qdrant collection exists: %s", collection_name)

    except Exception as e:
        logger.warning("Failed to ensure Qdrant collections: %s", e)
