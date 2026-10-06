"""Redis client and utilities."""

import time
import threading
from typing import Any, Optional

from app.core.config import settings


class MockRedis:
    """In-memory Redis mock for local development."""

    def __init__(self):
        self._data: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def _cleanup_expired(self):
        now = time.time()
        with self._lock:
            expired = [k for k, (_, exp) in self._data.items() if exp > 0 and exp < now]
            for k in expired:
                del self._data[k]

    def set(self, key: str, value: str, ex: int = None, nx: bool = False) -> bool:
        self._cleanup_expired()
        with self._lock:
            if nx and key in self._data:
                return False
            exp = time.time() + ex if ex else -1
            self._data[key] = (value, exp)
            return True

    def get(self, key: str) -> Optional[str]:
        self._cleanup_expired()
        with self._lock:
            if key in self._data:
                value, exp = self._data[key]
                if exp < 0 or exp > time.time():
                    return value
                else:
                    del self._data[key]
        return None

    def getdel(self, key: str) -> Optional[str]:
        self._cleanup_expired()
        with self._lock:
            if key in self._data:
                value, exp = self._data[key]
                if exp < 0 or exp > time.time():
                    del self._data[key]
                    return value
                else:
                    del self._data[key]
        return None

    def ping(self) -> bool:
        return True

    def close(self):
        pass


_redis_pool: Optional[Any] = None
_mock_redis = MockRedis()


def get_redis_pool():
    """Return a mock Redis pool for local development."""
    return None


def get_redis() -> MockRedis:
    """Return a mock Redis client for local development."""
    return _mock_redis


def check_redis_connection() -> bool:
    """Health check: always returns True for mock."""
    return True