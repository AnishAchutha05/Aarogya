"""Abstract AI provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class GenerationResult:
    content: str
    provider: str
    model: Optional[str] = None
    usage: Optional[dict] = None


class AIProvider(ABC):
    """
    Abstract provider interface.
    All concrete providers must implement this.
    Never store or expose the api_key through any public method.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        self._api_key = api_key  # Private - never expose
        self.model = model

    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        """Generate a response from the model."""

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test that the API key is valid and the model is reachable."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.model}>"
