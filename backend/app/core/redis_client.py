"""Redis client and utilities."""

from typing import Optional

import redis as _redis

from app.core.config import settings

_pool: Optional[_redis.ConnectionPool] = None


def get_redis_pool() -> _redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = _redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def get_redis() -> _redis.Redis:
    """Return a Redis client from the shared pool."""
    return _redis.Redis(connection_pool=get_redis_pool())


def check_redis_connection() -> bool:
    """Health check: verifies Redis connectivity."""
    try:
        client = get_redis()
        client.ping()
        return True
    except Exception:
        return False
