"""
API dependencies — authentication and authorization.

Phase 2: Real JWT validation. No fallback to first user.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlmodel import Session

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models import User

_bearer = HTTPBearer(auto_error=False)

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Geçerli bir kimlik doğrulama token'ı gerekli.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    """
    Validate Bearer JWT and return the authenticated User.

    Raises HTTP 401 for:
    - Missing Authorization header
    - Invalid / malformed token
    - Expired token
    - User not found in DB
    - Inactive user
    """
    if credentials is None:
        raise _401

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise _401

    user_id = int(payload.sub)
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise _401

    return user
