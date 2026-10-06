# Backend Status & Architecture

## Overview
The Aarogya backend implementation has been fully completed and configured. It is ready for the frontend application to consume. 

## Stack & Infrastructure
- **Framework**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL 16 (Source of Truth)
- **ORM**: SQLAlchemy 2.0 with Alembic for migrations
- **Vector Store**: Qdrant (RAG & contextual memory)
- **Caching & Queues**: Redis (RQ worker for background tasks)
- **AI Integration**: Multi-provider (Gemini, OpenAI, Anthropic) via LangChain abstraction

## Implemented Layers

### 1. Models & Database Schema (`app/models/`)
All models have been completely rewritten using SQLAlchemy 2.0 syntax, strict typing, and a shared `TimestampMixin`.
- `User` and `Profile` (One-to-One)
- `AuthSession` for Token Management
- `AIProviderCredential` (AES encrypted keys)
- Wellness: `WellnessGoal`, `Activity`, `ActivityLog`, `CheckIn`, `Insight`
- Plans: `Plan`, `PlanItem`
- Chat: `ChatSession`, `ChatMessage`
- Photos: `ProgressPhoto` (with file tracking)
- RAG: `MemoryRecord`

### 2. Core Config & Security (`app/core/`)
- `config.py` using `pydantic-settings` (loading `.env`).
- `security.py` with standard bcrypt hashing, JWT access/refresh token generation, and `get_current_active_user` dependency.
- `encryption.py` (Fernet) for securely storing AI provider API keys.
- `database.py` with async/sync abstractions and connection pooling.
- Custom structured error handling via `errors.py`.

### 3. Service Layer (`app/services/`)
Business logic strictly separated from routers:
- `auth_service.py` (Registration, Token Rotation, Password reset)
- `user_service.py` (Profile upserts, deterministic logic)
- `wellness_service.py` (CRUD for goals, logging activities, daily check-ins)
- `plan_service.py` (Multi-day plans with completion tracking)
- `ai_provider_service.py` (Encrypted credential management, never logs or exposes keys)
- `chat_service.py` (Conversation history with soft deletes)
- `photo_service.py` (Upload logic with MIME/Magic-byte validation, pluggable storage backend)
- `memory_service.py` (Tenant-isolated persistent knowledge)
- `coach_service.py` (Aaryu interaction - context gathering, RAG querying, prompt building, provider delegation)

### 4. AI & RAG Subsystem (`app/ai/`, `app/rag/`)
- **Providers**: Unified `AIProvider` interface. Implemented `GeminiProvider`, `OpenAIProvider`, `AnthropicProvider`.
- **RAG Retriever**: `WellnessRetriever` queries both general wellness knowledge and user-isolated memory.
- **RAG Ingestion**: Functions for embedding and upserting user memories into Qdrant (`Qdrant` collection auto-initializes on startup).
- **Worker**: Redis Queue (`rq`) integrated for processing heavy embeddings in the background without blocking the API.

### 5. API Routers (`app/api/`)
- `auth.py`, `users.py`, `wellness.py`, `progress.py`, `plans.py`, `photos.py`, `ai_provider.py`, `coach.py`, `roadmap.py` implemented with proper Pydantic schemas and `Depends(get_current_active_user)`.

## Setup & Running
1. `docker compose up -d postgres redis qdrant`
2. Configure `.env` with DB urls, Qdrant URL, Redis URL, JWT Secret, and Fernet Key.
3. Run `alembic upgrade head`
4. Start server: `uvicorn app.main:app --reload`
5. Start worker: `python app/worker/main.py`

*(Note: These are all automated via `docker-compose up`)*

## Tests
Basic end-to-end testing script `scripts/verify_backend.sh` created, and standard pytest suites implemented in `tests/test_api.py`.
