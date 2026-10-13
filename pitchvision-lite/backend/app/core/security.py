"""
JWT-based authentication utilities.

Replaces the Phase 1 base64 mock token with real HS256 JWT.
Password hashing via bcrypt (unchanged).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings


# ── Token payload schema ──────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    sub: str           # user_id as string
    org: int           # organization_id
    role: str          # UserRole value
    type: str          # "access"
    exp: int
    iat: int


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────────────────

def _settings():
    return get_settings()


def create_access_token(
    user_id: int,
    org_id: int,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = _settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    claims: dict[str, Any] = {
        "sub": str(user_id),
        "org": org_id,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(claims, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT access token.
    Raises jose.JWTError on invalid/expired tokens.
    """
    settings = _settings()
    raw = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    payload = TokenPayload(**raw)
    if payload.type != "access":
        raise JWTError("Invalid token type")
    return payload


# ── Legacy stubs (kept so any residual imports do not break) ──────────────────
# These are NOT used anywhere in Phase 2+ code. They will be removed in Phase 3.

def create_mock_token(user_id: int) -> str:  # noqa: ARG001
    raise RuntimeError(
        "create_mock_token is disabled in Phase 2. Use create_access_token()."
    )


def decode_mock_token(token: str) -> int | None:  # noqa: ARG001
    raise RuntimeError(
        "decode_mock_token is disabled in Phase 2. Use decode_access_token()."
    )
