"""Provider manager - resolves the correct provider for a user."""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.providers import AIProvider
from app.core.errors import AarogyaError
from app.services.ai_provider_service import ai_provider_service

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Resolves and instantiates the correct AIProvider for a given user.
    Decrypts the key internally - never exposes it.
    """

    def get_provider_for_user(
        self, db: Session, user_id: str
    ) -> AIProvider:
        """
        Get the active provider for the user.
        Raises AarogyaError if no active credential is configured.
        """
        cred = ai_provider_service.get_active_credential(db, user_id)
        if not cred:
            raise AarogyaError(
                "No AI provider configured. Please add a provider API key in settings.",
                status_code=400,
            )

        raw_key = ai_provider_service.get_decrypted_key(db, user_id, cred)
        return self._build_provider(cred.provider, raw_key)

    def get_provider(self, provider_name: str, encrypted_key: str) -> AIProvider:
        """Legacy: build provider from encrypted key directly."""
        from app.core.encryption import decrypt_api_key
        raw_key = decrypt_api_key(encrypted_key)
        return self._build_provider(provider_name, raw_key)

    @staticmethod
    def _build_provider(provider_name: str, api_key: str) -> AIProvider:
        if provider_name == "gemini":
            from app.ai.providers.gemini import GeminiProvider
            return GeminiProvider(api_key)
        elif provider_name == "openai":
            from app.ai.providers.openai import OpenAIProvider
            return OpenAIProvider(api_key)
        elif provider_name == "anthropic":
            from app.ai.providers.anthropic import AnthropicProvider
            return AnthropicProvider(api_key)
        else:
            raise AarogyaError(f"Unsupported AI provider: {provider_name}", status_code=400)


provider_manager = ProviderManager()
