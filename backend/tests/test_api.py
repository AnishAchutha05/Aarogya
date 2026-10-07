import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault(
    "UPLOAD_DIR", str(Path(__file__).resolve().parents[1] / ".test-uploads")
)

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.core.config import settings

# Test database - use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Mock OAuth credentials for tests
settings.GOOGLE_CLIENT_ID = "test-google-client-id"
settings.GOOGLE_CLIENT_SECRET = "test-google-client-secret"
settings.YAHOO_CLIENT_ID = "test-yahoo-client-id"
settings.YAHOO_CLIENT_SECRET = "test-yahoo-client-secret"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_production_cors_allows_vercel_register_origin(client):
    response = client.options(
        "/auth/register",
        headers={
            "Origin": "https://aarogya-amber.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://aarogya-amber.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "authorization" in response.headers.get("access-control-allow-headers", "").lower()


def test_register_and_login(client):
    # Register
    res = client.post("/auth/register", json={
        "email": "test@aarogya.com",
        "password": "strongpassword123",
        "name": "Test User"
    })
    assert res.status_code == 201
    assert res.json()["email"] == "test@aarogya.com"

    # Login
    res = client.post("/auth/login", json={
        "email": "test@aarogya.com",
        "password": "strongpassword123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert "aarogya_refresh" in res.cookies
    assert "httponly" in res.headers.get("set-cookie", "").lower()

    # Get Profile
    access_token = res.json()["access_token"]
    res = client.get("/users/me/profile", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    assert res.json()["user_id"] is not None


def test_refresh_cookie_rotates_and_replay_window_is_idempotent(client):
    client.post("/auth/register", json={
        "email": "refresh-test@aarogya.com",
        "password": "strongpassword123",
        "name": "Refresh Test",
    })
    login = client.post("/auth/login", json={
        "email": "refresh-test@aarogya.com",
        "password": "strongpassword123",
    })
    old_refresh = login.json()["refresh_token"]

    first = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert first.status_code == 200
    first_data = first.json()
    assert first_data["refresh_token"] != old_refresh

    parallel_retry = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert parallel_retry.status_code == 200
    assert parallel_retry.json()["refresh_token"] == first_data["refresh_token"]


def test_oauth_routes_are_registered_and_start_authorization(client, monkeypatch):
    from app.api import auth as auth_api

    monkeypatch.setattr(
        auth_api.oauth_service,
        "authorization_url",
        lambda provider, link_user_id=None: f"https://identity.example/{provider}",
    )
    for provider in ("google", "yahoo"):
        response = client.get(f"/auth/{provider}", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == f"https://identity.example/{provider}"