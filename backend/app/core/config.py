"""Application configuration via environment variables."""

from pathlib import Path
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Aarogya"
    DEBUG: bool = False

    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Encryption for API keys
    AI_KEY_ENCRYPTION_KEY: str

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # OAuth - Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # OAuth - Yahoo
    YAHOO_CLIENT_ID: str = ""
    YAHOO_CLIENT_SECRET: str = ""
    YAHOO_REDIRECT_URI: str = "https://localhost:8000/auth/yahoo/callback"

    # Photo storage
    UPLOAD_DIR: str = str(Path(__file__).resolve().parents[2] / "uploads")
    MAX_PHOTO_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # Worker
    WORKER_CONCURRENCY: int = 4

    # Embedding model
    EMBEDDING_MODEL: str = "models/embedding-001"  # Google embedding
    QDRANT_WELLNESS_COLLECTION: str = "wellness_knowledge"
    QDRANT_MEMORY_COLLECTION: str = "user_memory"
    QDRANT_VECTOR_SIZE: int = 768  # Google embedding-001 dimension

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ENV_FILE if _PROJECT_ENV_FILE.is_file() else ".env",
        extra="ignore",
    )

    @field_validator("AI_KEY_ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        if v == "replace_me" or len(v) < 32:
            raise ValueError(
                "AI_KEY_ENCRYPTION_KEY must be set to a secure random value (>=32 chars)"
            )
        return v

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if v == "replace_me" or len(v) < 32:
            raise ValueError(
                "JWT_SECRET must be set to a secure random value (>=32 chars)"
            )
        return v

    @field_validator("YAHOO_REDIRECT_URI")
    @classmethod
    def validate_yahoo_redirect_uri(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("YAHOO_REDIRECT_URI must be an HTTPS URL")
        return v


settings = Settings()
