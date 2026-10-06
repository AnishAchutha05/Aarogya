"""Anthropic Claude provider."""

import logging
from typing import Optional

from app.ai.providers import AIProvider, GenerationResult, Message

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-3-5-haiku-20241022"


class AnthropicProvider(AIProvider):

    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model or DEFAULT_MODEL)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate(
        self,
        messages: list[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

            lc_messages = []
            if system_prompt:
                lc_messages.append(SystemMessage(content=system_prompt))
            for m in messages:
                if m.role == "user":
                    lc_messages.append(HumanMessage(content=m.content))
                elif m.role == "assistant":
                    lc_messages.append(AIMessage(content=m.content))

            llm = ChatAnthropic(
                model=self.model,
                anthropic_api_key=self._api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response = await llm.ainvoke(lc_messages)
            return GenerationResult(
                content=response.content,
                provider="anthropic",
                model=self.model,
            )

        except Exception as e:
            logger.error("Anthropic generation error: %s", type(e).__name__)
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
