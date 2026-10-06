"""Aaryu coach AI service."""

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.provider_manager import provider_manager
from app.ai.providers import Message
from app.ai.prompts.coach import COACH_SYSTEM_PROMPT, ROADMAP_SYSTEM_PROMPT
from app.core.errors import AarogyaError, ProviderError
from app.models.conversation import ChatMessage, ChatSession
from app.services.chat_service import chat_service
from app.services.personalization_service import personalization_service

logger = logging.getLogger(__name__)


class CoachService:
    """
    Aaryu - the AI wellness coach.
    Orchestrates: user context → RAG retrieval → provider → response storage.
    """

    async def send_message(
        self,
        db: Session,
        user_id: str,
        session_id: str,
        user_message: str,
    ) -> ChatMessage:
        """
        Process a user message and generate Aaryu's response.
        - Always stores the user message first (never lost even on AI failure)
        - Retrieves user context from application layer (NOT from LLM)
        - Calls the user's configured AI provider
        - Stores assistant response
        """
        # 1. Validate session ownership
        session = chat_service.get_session(db, session_id, user_id)

        # 2. Store user message immediately - never lost
        user_msg = chat_service.add_message(
            db=db,
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=user_message,
        )

        # 3. Load user context deterministically
        try:
            user_context = personalization_service.get_user_context(db, user_id)
        except Exception as e:
            logger.warning("Failed to load user context user=%s: %s", user_id, e)
            user_context = {}

        # 4. Retrieve relevant wellness knowledge via RAG
        rag_context = []
        try:
            from app.rag.retriever import wellness_retriever
            rag_context = await wellness_retriever.search(user_message, user_id=user_id)
        except Exception as e:
            logger.warning("RAG retrieval failed: %s", e)

        # 5. Build conversation history
        history = chat_service.get_messages(db, session_id, user_id, limit=20)
        # Exclude the just-stored user message from history (it's at the end)
        prior_messages = history[:-1] if history else []

        # 6. Build prompt with context
        system_with_context = self._build_system_prompt(user_context, rag_context)

        lc_messages = [
            Message(role=m.role, content=m.content)
            for m in prior_messages
            if m.role in {"user", "assistant"}
        ]
        lc_messages.append(Message(role="user", content=user_message))

        # 7. Get user's configured AI provider and generate response
        try:
            provider = provider_manager.get_provider_for_user(db, user_id)
            result = await provider.generate(
                messages=lc_messages,
                system_prompt=system_with_context,
                temperature=0.7,
                max_tokens=1024,
            )
            response_content = result.content

        except AarogyaError:
            # Re-raise application errors (e.g., no provider configured)
            raise
        except Exception as e:
            logger.error(
                "Provider generation failed for user=%s session=%s: %s",
                user_id,
                session_id,
                type(e).__name__,
            )
            raise ProviderError(
                "Unable to generate response from AI provider. "
                "Please check your API key configuration."
            )

        # 8. Store assistant response
        assistant_msg = chat_service.add_message(
            db=db,
            session_id=session_id,
            user_id=user_id,
            role="assistant",
            content=response_content,
        )

        # 9. Auto-title session on first exchange
        if not session.title or session.title == "New Conversation":
            try:
                preview = user_message[:60].strip()
                session.title = preview + ("..." if len(user_message) > 60 else "")
                db.commit()
            except Exception:
                pass

        return assistant_msg

    async def generate_roadmap(
        self, db: Session, user_id: str, session_id: str
    ) -> str:
        """
        Analyze a conversation and generate an Obsidian-compatible Markdown roadmap.
        The session must belong to the requesting user.
        """
        # Validate ownership
        chat_service.get_session(db, session_id, user_id)

        messages = chat_service.get_messages(db, session_id, user_id)
        if not messages:
            raise AarogyaError("Session has no messages to analyze", status_code=400)

        # Build conversation text for analysis
        conversation_text = "\n\n".join(
            f"**{m.role.title()}**: {m.content}" for m in messages
        )

        analysis_prompt = (
            f"Please analyze the following wellness conversation and create a structured "
            f"Obsidian-compatible roadmap:\n\n---\n\n{conversation_text}\n\n---"
        )

        try:
            provider = provider_manager.get_provider_for_user(db, user_id)
            result = await provider.generate(
                messages=[Message(role="user", content=analysis_prompt)],
                system_prompt=ROADMAP_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=2048,
            )
            return result.content

        except AarogyaError:
            raise
        except Exception as e:
            logger.error(
                "Roadmap generation failed for user=%s session=%s: %s",
                user_id, session_id, type(e).__name__,
            )
            raise ProviderError("Failed to generate roadmap from AI provider.")

    @staticmethod
    def _build_system_prompt(user_context: dict, rag_context: list) -> str:
        """Build an enriched system prompt with user context and retrieved knowledge."""
        parts = [COACH_SYSTEM_PROMPT]

        if user_context:
            parts.append(
                f"\n\n## User Context\n```json\n{json.dumps(user_context, indent=2, default=str)}\n```"
            )

        if rag_context:
            knowledge_text = "\n\n".join(
                f"- {item.get('content', str(item))}" for item in rag_context[:5]
            )
            parts.append(
                f"\n\n## Relevant Wellness Knowledge\n{knowledge_text}"
            )

        return "\n".join(parts)


coach_service = CoachService()
