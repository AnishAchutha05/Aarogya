"""RAG document ingestion service."""

import logging
import uuid

from app.core.config import settings
from app.rag.embeddings import embedding_service
from app.rag.vector_store import get_qdrant_client

logger = logging.getLogger(__name__)


async def ingest_wellness_document(text: str, metadata: dict = None) -> str:
    """
    Embeds and stores a general wellness document.
    Should be called via background worker.
    """
    vector = await embedding_service.embed(text)
    if not any(vector):
        raise ValueError("Failed to generate embedding")

    doc_id = str(uuid.uuid4())
    payload = {"text": text}
    if metadata:
        payload.update(metadata)

    try:
        from qdrant_client.models import PointStruct
        client = get_qdrant_client()
        client.upsert(
            collection_name=settings.QDRANT_WELLNESS_COLLECTION,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload,
                )
            ]
        )
        logger.info("Ingested wellness document %s", doc_id)
        return doc_id
    except Exception as e:
        logger.error("Failed to ingest document to Qdrant: %s", e)
        raise


async def ingest_user_memory(user_id: str, text: str, category: str = None) -> str:
    """
    Embeds and stores a user-specific memory.
    Must include user_id in payload for strict filtering during retrieval.
    """
    vector = await embedding_service.embed(text)
    if not any(vector):
        raise ValueError("Failed to generate embedding")

    mem_id = str(uuid.uuid4())
    payload = {
        "text": text,
        "user_id": user_id,  # CRITICAL for tenant isolation
        "category": category,
    }

    try:
        from qdrant_client.models import PointStruct
        client = get_qdrant_client()
        client.upsert(
            collection_name=settings.QDRANT_MEMORY_COLLECTION,
            points=[
                PointStruct(
                    id=mem_id,
                    vector=vector,
                    payload=payload,
                )
            ]
        )
        logger.info("Ingested memory %s for user %s", mem_id, user_id)
        return mem_id
    except Exception as e:
        logger.error("Failed to ingest user memory to Qdrant: %s", e)
        raise
