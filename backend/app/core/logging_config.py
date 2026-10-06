"""Structured logging configuration."""

import logging
import sys

from app.core.config import settings


class SafeFormatter(logging.Formatter):
    """
    Log formatter that redacts potentially sensitive patterns.
    Never log passwords, tokens, or API keys.
    """

    REDACT_KEYS = {
        "password", "token", "api_key", "secret", "key",
        "access_token", "refresh_token", "encrypted",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Redact sensitive kwargs if present
        if hasattr(record, "extra"):
            for k in list(record.extra.keys()):
                if any(rk in k.lower() for rk in self.REDACT_KEYS):
                    record.extra[k] = "***REDACTED***"
        return super().format(record)


def setup_logging() -> None:
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        SafeFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Suppress noisy third-party loggers
    for name in ("httpx", "httpcore", "urllib3", "passlib"):
        logging.getLogger(name).setLevel(logging.WARNING)


logger = logging.getLogger("aarogya")
