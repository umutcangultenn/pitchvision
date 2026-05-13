from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.core.security import decode_mock_token
from app.db.session import get_session
from app.models import User


def get_current_user(
    session: Session = Depends(get_session),
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization:
        # Demo kolaylığı: ilk kullanıcıyı fallback olarak kullan.
        user = session.exec(select(User).order_by(User.id)).first()
        if user:
            return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı.")

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")

    token = authorization.split(" ", maxsplit=1)[1]
    user_id = decode_mock_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token çözümlenemedi.")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı.")
    return user
