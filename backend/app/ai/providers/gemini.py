"""Google Gemini AI provider."""

import logging
from typing import Optional

from app.ai.providers import AIProvider, GenerationResult, Message

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiProvider(AIProvider):
    """
    Gemini provider using langchain-google-genai.
    Falls back gracefully if google-genai is unavailable.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model or DEFAULT_MODEL)

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            if system_prompt:
                lc_messages.append(SystemMessage(content=system_prompt))
            for m in messages:
                if m.role == "user":
                    lc_messages.append(HumanMessage(content=m.content))
                elif m.role == "assistant":
                    lc_messages.append(AIMessage(content=m.content))
                elif m.role == "system":
                    lc_messages.append(SystemMessage(content=m.content))

            llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self._api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = await llm.ainvoke(lc_messages)
            return GenerationResult(
                content=response.content,
                provider="gemini",
                model=self.model,
                usage=getattr(response, "usage_metadata", None),
            )

        except Exception as e:
            logger.error("Gemini generation error: %s", type(e).__name__)
            raise

    async def test_connection(self) -> bool:
        try:
            result = await self.generate(
                [Message(role="user", content="Reply with only: ok")],
                max_tokens=10,
            )
            return bool(result.content)
        except Exception:
            return False
