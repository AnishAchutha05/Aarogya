"""RQ worker entrypoint."""

import logging
import os
import sys

# When running as `python app/worker/main.py` from /app,
# /app is already in sys.path (Python adds cwd). Ensure it's there.
app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

from rq import Worker, Queue

from app.core.redis_client import get_redis
from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("worker")

if __name__ == "__main__":
    redis_conn = get_redis()
    queue = Queue("default", connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    logger.info("Starting RQ worker on queue: default")
    worker.work()
