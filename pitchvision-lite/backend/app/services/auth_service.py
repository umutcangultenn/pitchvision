"""
Authentication business logic — register, login.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.core.security import create_access_token, hash_password, verify_password
from app.models import Organization, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead


def register(session: Session, payload: RegisterRequest) -> TokenResponse:
    # Check duplicate email
    existing = session.exec(select(User).where(User.email == str(payload.email))).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")

    # Verify org exists
    org = session.get(Organization, payload.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizasyon bulunamadı.")

    user = User(
        email=str(payload.email),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        organization_id=payload.organization_id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token(
        user_id=user.id,
        org_id=user.organization_id,
        role=user.role.value,
    )
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))


def login(session: Session, payload: LoginRequest) -> TokenResponse:
    user = session.exec(select(User).where(User.email == str(payload.email))).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya parola hatalı.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesap devre dışı bırakılmış.",
        )

    token = create_access_token(
        user_id=user.id,
        org_id=user.organization_id,
        role=user.role.value,
    )
    return TokenResponse(access_token=token, user=UserRead.model_validate(user))
