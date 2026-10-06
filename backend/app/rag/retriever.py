"""RAG retrieval service."""

import logging
from typing import Optional

from app.core.config import settings
from app.rag.embeddings import embedding_service
from app.rag.vector_store import get_qdrant_client

logger = logging.getLogger(__name__)


class WellnessRetriever:
    """Retrieves relevant semantic context from Qdrant."""

    def __init__(self):
        self.wellness_collection = settings.QDRANT_WELLNESS_COLLECTION
        self.memory_collection = settings.QDRANT_MEMORY_COLLECTION

    async def search(
        self, query: str, user_id: Optional[str] = None, limit: int = 5
    ) -> list[dict]:
        """
        Search both general wellness knowledge and user-specific memory.
        Returns a combined list of retrieved documents.
        """
        query_vector = await embedding_service.embed(query)
        if not any(query_vector):
            return []

        results = []
        try:
            client = get_qdrant_client()
            
            # 1. Search General Wellness Knowledge
            wellness_hits = client.search(
                collection_name=self.wellness_collection,
                query_vector=query_vector,
                limit=limit,
            )
            for hit in wellness_hits:
                results.append(
                    {
                        "source": "wellness_knowledge",
                        "content": hit.payload.get("text", ""),
                        "score": hit.score,
                    }
                )

            # 2. Search User Memory (Strictly isolated by user_id!)
            if user_id:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                
                memory_hits = client.search(
                    collection_name=self.memory_collection,
                    query_vector=query_vector,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="user_id", match=MatchValue(value=user_id)
                            )
                        ]
                    ),
                    limit=limit,
                )
                for hit in memory_hits:
                    results.append(
                        {
                            "source": "user_memory",
                            "content": hit.payload.get("text", ""),
                            "score": hit.score,
                        }
                    )

            # Sort combined results by score descending
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.warning("Qdrant retrieval failed: %s", e)
            return []


wellness_retriever = WellnessRetriever()
