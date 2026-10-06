import asyncio
import json
from urllib.parse import parse_qs, urlparse

import pytest

from app.services.oauth_service import OAuthService


@pytest.mark.parametrize(
    ("provider", "expected_host", "expected_scheme", "expected_redirect"),
    [
        (
            "google",
            "accounts.google.com",
            "https",
            "http://localhost:8000/auth/google/callback",
        ),
        (
            "yahoo",
            "api.login.yahoo.com",
            "https",
            "https://localhost:8000/auth/yahoo/callback",
        ),
    ],
)
def test_authorization_url_uses_configured_provider_and_scopes(
    monkeypatch, provider, expected_host, expected_scheme, expected_redirect
):
    values = {}

    class FakeRedis:
        def set(self, key, value, ex, nx):
            values.update(key=key, value=value, ex=ex, nx=nx)
            return True

    monkeypatch.setattr("app.services.oauth_service.get_redis", lambda: FakeRedis())
    url = OAuthService().authorization_url(provider)
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    assert parsed.hostname == expected_host
    assert parsed.scheme == expected_scheme
    assert params["redirect_uri"] == [expected_redirect]
    assert params["scope"] == ["openid profile email"]
    assert params["response_type"] == ["code"]
    assert params["code_challenge_method"] == ["S256"]
    assert params["state"] and params["nonce"]
    assert values["key"] == f"oauth:state:{params['state'][0]}"
    assert values["ex"] == 600 and values["nx"] is True


def test_callback_rejects_invalid_or_expired_state(monkeypatch):
    class FakeRedis:
        def getdel(self, key):
            return None

    monkeypatch.setattr("app.services.oauth_service.get_redis", lambda: FakeRedis())
    with pytest.raises(ValueError, match="invalid or expired"):
        asyncio.run(OAuthService().exchange_and_validate("google", "some-code", "bad-state"))

def test_callback_rejects_state_for_wrong_provider(monkeypatch):
    class FakeRedis:
        def getdel(self, key):
            return json.dumps({"provider": "yahoo", "nonce": "n", "verifier": "v"})

    monkeypatch.setattr("app.services.oauth_service.get_redis", lambda: FakeRedis())
    with pytest.raises(ValueError, match="does not match provider"):
        asyncio.run(OAuthService().exchange_and_validate("google", "some-code", "state"))


@pytest.mark.parametrize("issuer", ["https://accounts.google.com", "accounts.google.com"])
def test_google_accepts_documented_issuer_variants(monkeypatch, issuer):
    from app.services.oauth_service import _provider_config

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"keys": [{"kid": "google-key", "kty": "RSA", "use": "sig"}]}

    class FakeClient:
        async def get(self, url):
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.oauth_service.jwt.get_unverified_header",
        lambda token: {"alg": "RS256", "kid": "google-key"},
    )
    monkeypatch.setattr(
        "app.services.oauth_service.jwt.decode",
        lambda *args, **kwargs: {
            "iss": issuer,
            "aud": _provider_config("google").client_id,
            "exp": 2_000_000_000,
            "iat": 1_700_000_000,
            "sub": "google-subject",
            "nonce": "expected-nonce",
            "email": "user@example.com",
            "email_verified": True,
            "name": "Test User",
        },
    )

    result = asyncio.run(
        OAuthService()._validate_identity(
            FakeClient(), _provider_config("google"), "signed-id-token", "expected-nonce"
        )
    )
    assert result["provider_user_id"] == "google-subject"
    assert result["email"] == "user@example.com"


def test_yahoo_issuer_remains_exact(monkeypatch):
    from app.services.oauth_service import _provider_config

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"keys": [{"kid": "yahoo-key", "kty": "RSA", "use": "sig"}]}

    class FakeClient:
        async def get(self, url):
            return FakeResponse()

    monkeypatch.setattr(
        "app.services.oauth_service.jwt.get_unverified_header",
        lambda token: {"alg": "RS256", "kid": "yahoo-key"},
    )
    monkeypatch.setattr(
        "app.services.oauth_service.jwt.decode",
        lambda *args, **kwargs: {
            "iss": "accounts.login.yahoo.com",
            "aud": _provider_config("yahoo").client_id,
            "exp": 2_000_000_000,
            "iat": 1_700_000_000,
            "sub": "yahoo-subject",
            "nonce": "expected-nonce",
            "email": "user@example.com",
            "email_verified": True,
        },
    )

    with pytest.raises(ValueError, match="could not be validated"):
        asyncio.run(
            OAuthService()._validate_identity(
                FakeClient(), _provider_config("yahoo"), "signed-id-token", "expected-nonce"
            )
        )