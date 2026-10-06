#!/usr/bin/env bash

set -Eeuo pipefail

ROOT="$HOME/Projects/aarogya"
BACKEND="$ROOT/backend"

echo "=================================================="
echo "        AAROGYA BACKEND SETUP + TEST BOOTSTRAP"
echo "=================================================="

cd "$ROOT"

# --------------------------------------------------
# 1. Verify required tools
# --------------------------------------------------

for cmd in docker curl python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: $cmd is required."
        exit 1
    fi
done

echo
echo "[1/8] Checking Docker Compose..."
docker compose config >/dev/null
echo "✓ docker-compose.yml is valid"

# --------------------------------------------------
# 2. Fix backend Dockerfile
# --------------------------------------------------

echo
echo "[2/8] Fixing backend Dockerfile..."

cat > "$BACKEND/Dockerfile" <<'EOF'
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "✓ backend/Dockerfile fixed"

# --------------------------------------------------
# 3. Make sure worker entrypoint exists
# --------------------------------------------------

echo
echo "Checking worker entrypoint..."

if [ ! -f "$BACKEND/app/worker/main.py" ]; then
    echo "Creating worker entrypoint..."

    mkdir -p "$BACKEND/app/worker"

    cat > "$BACKEND/app/worker/main.py" <<'EOF'
from app.worker.tasks import process_embeddings


def main():
    print("Aarogya worker started")


if __name__ == "__main__":
    main()
EOF
fi

echo "✓ worker entrypoint available"

# --------------------------------------------------
# 4. Fresh local infrastructure
# --------------------------------------------------

echo
echo "[3/8] Resetting local Docker infrastructure..."

docker compose down -v --remove-orphans || true

echo "✓ old local containers/volumes removed"

# --------------------------------------------------
# 5. Build everything
# --------------------------------------------------

echo
echo "[4/8] Building backend and worker..."

docker compose build --no-cache backend worker

echo "✓ images built"

# --------------------------------------------------
# 6. Start infrastructure
# --------------------------------------------------

echo
echo "[5/8] Starting PostgreSQL, Redis and Qdrant..."

docker compose up -d postgres redis qdrant

echo "Waiting for PostgreSQL..."

until docker compose exec -T postgres \
    pg_isready \
    -U "${POSTGRES_USER:-aarogya}" \
    -d "${POSTGRES_DB:-aarogya}" \
    >/dev/null 2>&1
do
    sleep 2
done

echo "✓ PostgreSQL ready"

echo "Waiting for Redis..."

until docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG
do
    sleep 2
done

echo "✓ Redis ready"

echo "Waiting for Qdrant..."

until curl -fsS http://localhost:6334/collections >/dev/null 2>&1
do
    sleep 2
done

echo "✓ Qdrant ready"

# --------------------------------------------------
# 7. Run Alembic + backend tests
# --------------------------------------------------

echo
echo "[6/8] Running Alembic migrations..."

docker compose run --rm backend alembic upgrade head

echo "✓ migrations completed"

echo
echo "Checking database tables..."

docker compose exec -T postgres \
    psql \
    -U "${POSTGRES_USER:-aarogya}" \
    -d "${POSTGRES_DB:-aarogya}" \
    -c "\dt"

echo
echo "[7/8] Starting backend + worker..."

docker compose up -d backend worker

sleep 5

echo
echo "Current services:"
docker compose ps

# --------------------------------------------------
# 8. Health check
# --------------------------------------------------

echo
echo "Checking FastAPI..."

until curl -fsS http://localhost:8000/health >/dev/null 2>&1
do
    sleep 2
done

echo "✓ FastAPI health check passed"

# --------------------------------------------------
# Run existing tests if present
# --------------------------------------------------

if [ -d "$BACKEND/tests" ]; then
    echo
    echo "Running existing backend tests..."

    docker compose run --rm backend \
        pytest -v tests \
        || echo "WARNING: Existing backend tests currently have failures."
else
    echo
    echo "No backend tests directory found."
fi

# --------------------------------------------------
# Create autonomous IDE verification prompt
# --------------------------------------------------

echo
echo "[8/8] Creating autonomous verification prompt..."

mkdir -p "$ROOT/docs"

cat > "$ROOT/docs/AI_BACKEND_VERIFICATION_PROMPT.md" <<'PROMPT'
# Aarogya — Autonomous Backend Verification

You are now responsible for completely verifying the Aarogya backend.

IMPORTANT:
- Do NOT build or redesign the frontend.
- Do NOT claim success because files exist.
- Actually execute the tests.
- If a test fails, debug it, fix it, and rerun it.
- Do not skip failures.
- Do not fake external API success.
- Continue until all locally verifiable backend functionality passes.

==================================================
OBJECTIVE
==================================================

Prove that Aarogya's backend and infrastructure are genuinely ready for frontend development.

==================================================
1. INFRASTRUCTURE
==================================================

Run:

docker compose ps

Verify:

- postgres
- redis
- qdrant
- backend
- worker

are running correctly.

Inspect logs:

docker compose logs --tail=200 backend
docker compose logs --tail=200 worker
docker compose logs --tail=200 postgres
docker compose logs --tail=200 redis
docker compose logs --tail=200 qdrant

Fix all infrastructure errors.

==================================================
2. DATABASE
==================================================

Verify PostgreSQL connectivity.

Run:

alembic current
alembic upgrade head

Verify that all expected tables exist.

Verify:

- foreign keys
- uniqueness
- indexes
- timestamps
- relationships
- ownership

Verify the database can be recreated from migrations alone.

==================================================
3. AUTHENTICATION
==================================================

Test:

- registration
- duplicate registration
- login
- invalid password
- protected endpoints
- access token
- refresh token
- logout
- revoked refresh token
- password change

Passwords must be hashed.

Raw refresh tokens must not be stored.

==================================================
4. AUTHORIZATION
==================================================

Create User A and User B.

Test cross-user access.

User A MUST NOT access User B:

- profile
- goals
- plans
- activity history
- check-ins
- insights
- conversations
- messages
- memories
- photos
- AI credentials

Try direct ID substitution.

Expected result:
403 or 404.

Never 200.

==================================================
5. PROFILE
==================================================

Test create/update/retrieve for:

- name
- DOB
- age
- gender
- height
- weight
- nationality/region
- food preferences
- wellness goals
- lifestyle/activity data

Verify validation and persistence.

==================================================
6. WELLNESS
==================================================

Test:

- goals
- activities
- check-ins
- plans
- plan items
- activity completion
- history
- progress
- insights

Verify deterministic personalization logic.

Example:

10-minute availability
→ recommendations should respect available time.

==================================================
7. AARYU CHAT
==================================================

Test complete flow:

create session
→ send user message
→ build user context
→ retrieve relevant data
→ invoke AI
→ store assistant response
→ retrieve conversation

Verify chat persistence.

Verify user isolation.

==================================================
8. AI PROVIDER ABSTRACTION
==================================================

Test the provider abstraction.

Verify:

Gemini
OpenAI
Anthropic

are represented through a common interface.

Verify:

- provider selection
- provider resolution
- timeout handling
- invalid credentials
- provider errors
- malformed responses

If real credentials are available, make a REAL provider call.

If credentials are not available, run mocked/provider-level tests and report clearly that external verification remains pending.

==================================================
9. API KEY SECURITY
==================================================

Create a provider credential.

Inspect the database.

Verify the API key is encrypted at rest.

Verify APIs NEVER return plaintext API keys.

Verify logs NEVER contain keys.

Verify keys are not stored in Redis or Qdrant.

==================================================
10. RAG
==================================================

Test:

document
→ loader
→ chunking
→ embedding
→ Qdrant
→ retrieval
→ Aaryu context

Verify semantic retrieval works.

Verify metadata filtering.

Verify user memory isolation.

User A must never receive User B memory.

==================================================
11. MEMORY
==================================================

Test:

important user information
→ memory storage
→ later chat
→ memory retrieval

Do not blindly inject every historical message.

Verify ownership isolation.

==================================================
12. ROADMAP
==================================================

Create a chat session.

Generate roadmap from that session.

Verify:

- ownership
- conversation retrieval
- roadmap generation
- valid Markdown
- Obsidian-compatible structure
- actionable content

Do not persist unless the architecture requires it.

==================================================
13. PROGRESS PHOTOS
==================================================

Test:

- valid upload
- invalid image
- oversized file
- filename sanitization
- listing
- retrieval
- deletion

Verify:

PostgreSQL metadata
+
filesystem/object-storage abstraction

Verify ownership isolation.

==================================================
14. REDIS
==================================================

Test:

- connectivity
- read/write
- expiration
- queue/background-job behavior
- rate limiting where implemented

==================================================
15. WORKER
==================================================

Verify worker starts.

Submit background job.

Verify:

job accepted
→ worker receives
→ executes
→ completes

Force a test failure.

Verify worker handles failure without permanently crashing.

==================================================
16. QDRANT
==================================================

Verify:

- collection creation
- vector insert
- vector search
- metadata filter
- connection recovery

==================================================
17. ERROR HANDLING
==================================================

Test:

400
401
403
404
409
422
429
500

Errors must not expose:

- stack traces
- passwords
- API keys
- JWT secrets
- database credentials

==================================================
18. SECURITY SCAN
==================================================

Search repository for:

- hardcoded secrets
- API keys
- passwords
- tokens

Check:

.env
.gitignore
logs
exceptions
API responses

Rotate/remove anything accidentally exposed.

==================================================
19. END-TO-END FLOW
==================================================

Perform:

Register
↓
Login
↓
Create profile
↓
Create goal
↓
Check-in
↓
Generate plan
↓
Complete activity
↓
Start Aaryu chat
↓
Retrieve user context
↓
Retrieve RAG context
↓
Generate response
↓
Persist conversation
↓
Generate roadmap
↓
Upload progress photo
↓
Retrieve progress

Repeat ownership-sensitive portions using User B.

==================================================
20. TEST SUITE
==================================================

Run:

pytest -v

Do not stop at the first failure.

Fix failures.

Run again.

Continue until the suite is clean or an external dependency genuinely prevents verification.

==================================================
21. DOCKER VALIDATION
==================================================

Verify:

docker compose build
docker compose up -d
docker compose ps

Verify every service.

==================================================
22. FINAL REPORT
==================================================

Create:

docs/backend-verification.md

For each subsystem write:

PASS
FAIL
PARTIAL

Include:

- infrastructure
- database
- migrations
- auth
- OAuth
- authorization
- profiles
- wellness
- Aaryu
- AI providers
- API-key security
- RAG
- memory
- roadmap
- photos
- Redis
- worker
- Qdrant
- security
- automated tests

For every FAIL/PARTIAL item:
- explain the exact reason
- fix it if possible
- rerun the relevant test

At the end provide:

BACKEND READINESS:
READY / NOT READY

Only mark READY after actual verification.

==================================================
FINAL RULE
==================================================

Do not touch the frontend UI.

The objective is to leave the backend and infrastructure fully tested and ready for frontend development.
PROMPT

echo "✓ verification prompt created"

echo
echo "=================================================="
echo "             SETUP FINISHED"
echo "=================================================="
echo
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Verification prompt:"
echo "$ROOT/docs/AI_BACKEND_VERIFICATION_PROMPT.md"
echo
echo "Open that file in your IDE and give it to the Agent."
echo
echo "The Agent must now perform the complete backend test/fix cycle."
echo
