"""Background worker tasks."""

import asyncio
import logging

from app.core.database import SessionLocal
from app.rag.ingestion import ingest_wellness_document, ingest_user_memory
from app.services.memory_service import memory_service

logger = logging.getLogger(__name__)


def process_wellness_document(text: str, metadata: dict = None) -> str:
    """Sync wrapper for async document ingestion."""
    return asyncio.run(ingest_wellness_document(text, metadata))


def process_user_memory(user_id: str, content: str, category: str = None) -> None:
    """
    Ingests a memory into Qdrant and saves a record in PostgreSQL.
    """
    logger.info("Processing user memory for user: %s", user_id)
    
    # 1. Ingest to Qdrant
    try:
        qdrant_id = asyncio.run(ingest_user_memory(user_id, content, category))
    except Exception as e:
        logger.error("Failed to vectorize memory: %s", e)
        qdrant_id = None
        # Still proceed to save in DB even if vectorization fails

    # 2. Save to DB
    db = SessionLocal()
    try:
        memory_service.add_memory(
            db=db,
            user_id=user_id,
            content=content,
            category=category,
            source="worker",
            qdrant_id=qdrant_id,
        )
    finally:
        db.close()
