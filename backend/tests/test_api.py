import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

# Host-run tests must use the host-published port, not Docker's service DNS name.
# Inside Docker, provide AAROGYA_TEST_DATABASE_URL explicitly (typically the
# compose DATABASE_URL with the test database name).
os.environ.setdefault(
    "UPLOAD_DIR", str(Path(__file__).resolve().parents[1] / ".test-uploads")
)

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.core.config import settings

# Test database
TEST_DATABASE_URL = os.getenv("AAROGYA_TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    test_url = make_url(settings.DATABASE_URL)
    if Path("/.dockerenv").exists():
        raise RuntimeError(
            "Set AAROGYA_TEST_DATABASE_URL explicitly when running tests inside Docker"
        )
    TEST_DATABASE_URL = test_url.set(
        host="127.0.0.1",
        port=55432,
        database=f"{test_url.database}_test",
    ).render_as_string(hide_password=False)
engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create test database if it doesn't exist
    from sqlalchemy import create_engine, text
    import psycopg
    try:
        test_url = make_url(TEST_DATABASE_URL)
        admin_url = test_url.set(database="postgres", drivername="postgresql").render_as_string(hide_password=False)
        conn = psycopg.connect(admin_url, autocommit=True)
        conn.execute(f'CREATE DATABASE "{test_url.database}"')
        conn.close()
    except psycopg.errors.DuplicateDatabase:
        pass
    except Exception as e:
        pytest.fail(f"Could not connect to/create the isolated test database: {type(e).__name__}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
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
