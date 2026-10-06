import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from redis import Redis

print("=== Testing Redis ===")
try:
    r = Redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
    r.set("test_key", "test_val")
    val = r.get("test_key")
    print(f"Redis result: {val.decode() if val else None}")
except Exception as e:
    print(f"Redis failed: {e}")

print("=== Testing Qdrant ===")
try:
    qc = QdrantClient(url=os.environ.get("QDRANT_URL", "http://qdrant:6333"))
    test_id = "123e4567-e89b-12d3-a456-426614174000"
    qc.upsert("wellness_knowledge", points=[
        PointStruct(id=test_id, vector=[0.5]*768, payload={"text": "Hello"})
    ])
    hits = qc.search("wellness_knowledge", query_vector=[0.5]*768, limit=1)
    if hits:
        print(f"Qdrant result: id={hits[0].id}, payload={hits[0].payload}")
    qc.delete("wellness_knowledge", points_selector=[test_id])
except Exception as e:
    print(f"Qdrant failed: {e}")
