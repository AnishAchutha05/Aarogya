#!/usr/bin/env bash

set -e

echo "======================================"
echo "       AAROGYA BACKEND SETUP"
echo "======================================"

cd ~/Projects/aarogya

echo
echo "[1/7] Checking Docker Compose..."
docker compose config >/dev/null
echo "✓ docker-compose configuration valid"

echo
echo "[2/7] Removing old Docker containers/volumes..."
docker compose down -v --remove-orphans

echo
echo "[3/7] Building backend and worker images..."
docker compose build backend worker

echo
echo "[4/7] Starting PostgreSQL, Redis and Qdrant..."
docker compose up -d postgres redis qdrant

echo
echo "[5/7] Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-aarogya}" -d "${POSTGRES_DB:-aarogya}" >/dev/null 2>&1
do
    sleep 2
done

echo "✓ PostgreSQL is ready"

echo
echo "Checking Redis..."
until docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG
do
    sleep 2
done

echo "✓ Redis is ready"

echo
echo "Checking Qdrant..."
until curl -fsS http://localhost:6334/collections >/dev/null 2>&1
do
    sleep 2
done

echo "✓ Qdrant is ready"

echo
echo "[6/7] Running Alembic migrations..."
docker compose run --rm backend alembic upgrade head

echo "✓ Alembic migrations completed"

echo
echo "Checking database tables..."
docker compose exec -T postgres \
    psql -U "${POSTGRES_USER:-aarogya}" \
    -d "${POSTGRES_DB:-aarogya}" \
    -c "\dt"

echo
echo "[7/7] Starting complete Aarogya stack..."
docker compose up -d

echo
echo "Waiting for backend..."
sleep 5

echo
echo "Checking services..."
docker compose ps

echo
echo "Checking backend health..."
curl -fsS http://localhost:8000/health

echo
echo
echo "======================================"
echo "       AAROGYA SETUP COMPLETE"
echo "======================================"
echo
echo "Frontend:   http://localhost:3000"
echo "Backend:    http://localhost:8000"
echo "API Docs:   http://localhost:8000/docs"
echo "Postgres:   localhost:55432"
echo "Redis:      localhost:6380"
echo "Qdrant:     localhost:6334"
echo
echo "Your database has been initialized through Alembic."
echo "Now the AI agent can perform the full backend verification."
echo
