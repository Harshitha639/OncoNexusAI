"""
JWT access-token and opaque refresh-token utilities.

Access tokens are short-lived, stateless JWTs (signed with `SECRET_KEY`)
carrying the user id and role names. Refresh tokens are long-lived,
cryptographically random opaque strings; only their SHA-256 hash is
persisted (see `app.models.refresh_token.RefreshToken`), so a database
leak never exposes a usable refresh token.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.exceptions.base import UnauthorizedException

ACCESS_TOKEN_TYPE = "access"


def create_access_token(subject: uuid.UUID | str, roles: list[str]) -> tuple[str, datetime]:
    """Create a signed JWT access token for `subject` (the user id)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "roles": roles,
        "type": ACCESS_TOKEN_TYPE,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expire


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token. Raises UnauthorizedException on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedException(message="Invalid or expired access token.") from exc

    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise UnauthorizedException(message="Invalid token type.")
    return payload


def generate_refresh_token() -> tuple[str, str, datetime]:
    """Generate a new opaque refresh token.

    Returns (raw_token, token_hash, expires_at). Only `token_hash` is
    ever persisted; `raw_token` is returned to the client exactly once.
    """
    raw_token = secrets.token_urlsafe(64)
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    return raw_token, token_hash, expires_at


def hash_refresh_token(raw_token: str) -> str:
    """Deterministically hash a raw refresh token for storage/lookup."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
