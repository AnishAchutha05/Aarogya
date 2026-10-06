"""Server-side Google and Yahoo OpenID Connect flows."""

import base64
import hashlib
import hmac
import json
import logging
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx
from jose import JWTError, jwt

from app.core.config import settings
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)
OAUTH_STATE_TTL_SECONDS = 600


@dataclass(frozen=True)
class OAuthProvider:
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str
    issuer: str
    redirect_uri: str
    scopes: tuple[str, ...] = ("openid", "profile", "email")


def _provider_config(provider: str) -> OAuthProvider:
    if provider == "google":
        return OAuthProvider(
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
            jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
            issuer="https://accounts.google.com",
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )
    if provider == "yahoo":
        return OAuthProvider(
            client_id=settings.YAHOO_CLIENT_ID,
            client_secret=settings.YAHOO_CLIENT_SECRET,
            authorization_endpoint="https://api.login.yahoo.com/oauth2/request_auth",
            token_endpoint="https://api.login.yahoo.com/oauth2/get_token",
            jwks_uri="https://login.yahoo.com/openid/v1/certs",
            issuer="https://login.yahoo.com",
            redirect_uri=settings.YAHOO_REDIRECT_URI,
        )
    raise ValueError("Unsupported OAuth provider")


class OAuthService:
    """Performs stateful authorization-code exchange and validates signed ID tokens."""

    def authorization_url(self, provider: str, link_user_id: str | None = None) -> str:
        config = _provider_config(provider)
        if not config.client_id or not config.client_secret:
            raise RuntimeError("OAuth provider is not configured")

        redis = get_redis()
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip("=")
        state_payload = json.dumps(
            {
                "provider": provider,
                "nonce": nonce,
                "verifier": verifier,
                "link_user_id": link_user_id,
            },
            separators=(",", ":"),
        )
        if not redis.set(f"oauth:state:{state}", state_payload, ex=OAUTH_STATE_TTL_SECONDS, nx=True):
            raise RuntimeError("Could not initialize OAuth state")

        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "state": state,
            "nonce": nonce,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        if provider == "google":
            params["prompt"] = "select_account"
        return f"{config.authorization_endpoint}?{urlencode(params)}"

    async def exchange_and_validate(self, provider: str, code: str, state: str) -> dict[str, Any]:
        config = _provider_config(provider)
        if not config.client_id or not config.client_secret:
            raise RuntimeError("OAuth provider is not configured")
        if not code or not state:
            raise ValueError("OAuth callback is missing required parameters")

        try:
            state_data = get_redis().getdel(f"oauth:state:{state}")
        except Exception as exc:
            logger.error("OAuth state store unavailable (%s)", type(exc).__name__)
            raise RuntimeError("OAuth state verification is unavailable") from None
        if not state_data:
            raise ValueError("OAuth state is invalid or expired")
        try:
            state_payload = json.loads(state_data)
        except (TypeError, json.JSONDecodeError):
            raise ValueError("OAuth state is invalid or expired") from None
        if state_payload.get("provider") != provider:
            raise ValueError("OAuth state does not match provider")

        timeout = httpx.Timeout(10.0, connect=5.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            try:
                token_response = await client.post(
                    config.token_endpoint,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": config.redirect_uri,
                        "code_verifier": state_payload["verifier"],
                    },
                    auth=(config.client_id, config.client_secret),
                    headers={"Accept": "application/json"},
                )
                token_response.raise_for_status()
                token_data = token_response.json()
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                logger.warning("OAuth token exchange failed provider=%s error=%s", provider, type(exc).__name__)
                raise RuntimeError("OAuth authorization could not be completed") from None

            identity = await self._validate_identity(
                client,
                config,
                token_data.get("id_token"),
                state_payload.get("nonce", ""),
            )
            identity["link_user_id"] = state_payload.get("link_user_id")
            return identity

    async def _validate_identity(
        self,
        client: httpx.AsyncClient,
        config: OAuthProvider,
        id_token: str | None,
        expected_nonce: str,
    ) -> dict[str, Any]:
        if not id_token:
            raise ValueError("OAuth provider did not return an ID token")
        try:
            header = jwt.get_unverified_header(id_token)
            if header.get("alg") != "RS256" or not header.get("kid"):
                raise ValueError("OAuth ID token used an unexpected signing algorithm")

            jwks_response = await client.get(config.jwks_uri)
            jwks_response.raise_for_status()
            jwks_data = jwks_response.json()
            matching_key = next(
                (
                    key
                    for key in jwks_data.get("keys", [])
                    if key.get("kid") == header["kid"]
                    and key.get("kty") == "RSA"
                    and key.get("use", "sig") == "sig"
                ),
                None,
            )
            if not matching_key:
                raise ValueError("OAuth ID token signing key was not found")

            claims = jwt.decode(
                id_token,
                matching_key,
                algorithms=["RS256"],
                audience=config.client_id,
                options={
                    "verify_iss": False,
                    "verify_aud": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require_sub": True,
                    "require_exp": True,
                    "require_iat": True,
                },
            )

            # Google emits both documented issuer spellings; Yahoo has its own
            # exact issuer. Compare only after signature and time/audience checks.
            valid_issuers = (
                {"https://accounts.google.com", "accounts.google.com"}
                if config.issuer == "https://accounts.google.com"
                else {config.issuer}
            )
            if claims.get("iss") not in valid_issuers:
                raise ValueError("OAuth ID token issuer did not match provider")
        except (httpx.HTTPError, ValueError, JWTError, TypeError, KeyError) as exc:
            logger.warning("OAuth identity validation failed reason=%s", type(exc).__name__)
            raise ValueError("OAuth identity could not be validated") from None

        nonce = claims.get("nonce", "")
        if not nonce or not hmac.compare_digest(str(nonce), expected_nonce):
            raise ValueError("OAuth nonce is invalid")
        email = claims.get("email")
        email_verified = claims.get("email_verified")
        if not email or str(email_verified).lower() != "true":
            raise ValueError("OAuth provider did not verify the email address")
        subject = claims.get("sub")
        if not subject:
            raise ValueError("OAuth identity has no subject")

        picture = claims.get("picture")
        if picture and not str(picture).startswith("https://"):
            picture = None
        return {
            "provider_user_id": str(subject),
            "email": str(email).lower().strip(),
            "name": claims.get("name"),
            "avatar_url": picture,
        }


oauth_service = OAuthService()
