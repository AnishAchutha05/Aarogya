"""AI provider credential service - encrypted key management."""

import logging
import asyncio
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_api_key, encrypt_api_key
from app.core.errors import ForbiddenError, NotFoundError
from app.models.ai_provider import AIProviderCredential

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = {"gemini", "openai", "anthropic"}


class AIProviderService:

    def add_or_replace_credential(
        self,
        db: Session,
        user_id: str,
        provider: str,
        raw_api_key: str,
    ) -> AIProviderCredential:
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        encrypted = encrypt_api_key(raw_api_key)

        existing = (
            db.query(AIProviderCredential)
            .filter(
                AIProviderCredential.user_id == user_id,
                AIProviderCredential.provider == provider,
            )
            .first()
        )

        if existing:
            existing.encrypted_api_key = encrypted
            existing.is_verified = False  # Reset - needs re-verification
            db.commit()
            db.refresh(existing)
            # NEVER log the key
            logger.info("AI credential replaced for user=%s provider=%s", user_id, provider)
            return existing

        # Deactivate any existing active credential
        db.query(AIProviderCredential).filter(
            AIProviderCredential.user_id == user_id,
            AIProviderCredential.is_active == True,  # noqa: E712
        ).update({"is_active": False})

        cred = AIProviderCredential(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=provider,
            encrypted_api_key=encrypted,
            is_active=True,
        )
        db.add(cred)
        db.commit()
        db.refresh(cred)
        logger.info("AI credential added for user=%s provider=%s", user_id, provider)
        return cred

    def set_active_provider(
        self, db: Session, user_id: str, provider: str
    ) -> AIProviderCredential:
        cred = (
            db.query(AIProviderCredential)
            .filter(
                AIProviderCredential.user_id == user_id,
                AIProviderCredential.provider == provider,
            )
            .first()
        )
        if not cred:
            raise NotFoundError("AI credential for that provider")

        # Deactivate others
        db.query(AIProviderCredential).filter(
            AIProviderCredential.user_id == user_id,
            AIProviderCredential.provider != provider,
        ).update({"is_active": False})

        cred.is_active = True
        db.commit()
        db.refresh(cred)
        return cred

    def list_credentials(
        self, db: Session, user_id: str
    ) -> list[AIProviderCredential]:
        return (
            db.query(AIProviderCredential)
            .filter(AIProviderCredential.user_id == user_id)
            .all()
        )

    def get_active_credential(
        self, db: Session, user_id: str
    ) -> Optional[AIProviderCredential]:
        return (
            db.query(AIProviderCredential)
            .filter(
                AIProviderCredential.user_id == user_id,
                AIProviderCredential.is_active == True,  # noqa: E712
            )
            .first()
        )

    def get_decrypted_key(
        self, db: Session, user_id: str, credential: AIProviderCredential
    ) -> str:
        """
        Decrypt and return the raw API key.
        ONLY called inside backend provider execution - never returned to frontend.
        Verifies ownership before decrypting.
        """
        if credential.user_id != user_id:
            raise ForbiddenError()
        return decrypt_api_key(credential.encrypted_api_key)

    def remove_credential(
        self, db: Session, user_id: str, provider: str
    ) -> None:
        cred = (
            db.query(AIProviderCredential)
            .filter(
                AIProviderCredential.user_id == user_id,
                AIProviderCredential.provider == provider,
            )
            .first()
        )
        if not cred:
            raise NotFoundError("AI credential")
        db.delete(cred)
        db.commit()

    def mark_verified(
        self, db: Session, credential: AIProviderCredential
    ) -> AIProviderCredential:
        credential.is_verified = True
        db.commit()
        db.refresh(credential)
        return credential

    async def verify_credential(
        self, db: Session, user_id: str, provider: Optional[str] = None
    ) -> dict[str, object]:
        credential = (
            self.get_credential(db, user_id, provider)
            if provider
            else self.get_active_credential(db, user_id)
        )
        if not credential:
            raise NotFoundError("AI provider credential")
        if credential.provider not in SUPPORTED_PROVIDERS:
            raise ValueError("Unsupported provider")

        verified = False
        try:
            from app.ai.provider_manager import provider_manager

            raw_key = self.get_decrypted_key(db, user_id, credential)
            provider_client = provider_manager._build_provider(credential.provider, raw_key)
            verified = await asyncio.wait_for(provider_client.test_connection(), timeout=15)
        except Exception as exc:
            logger.warning(
                "AI provider verification failed provider=%s error=%s",
                credential.provider,
                type(exc).__name__,
            )

        credential.is_verified = bool(verified)
        db.commit()
        return {
            "provider": credential.provider,
            "configured": True,
            "verified": bool(verified),
        }


ai_provider_service = AIProviderService()
