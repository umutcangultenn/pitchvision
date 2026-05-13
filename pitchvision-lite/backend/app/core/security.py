import base64

import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_mock_token(user_id: int) -> str:
    raw = f"user:{user_id}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_mock_token(token: str) -> int | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        if not decoded.startswith("user:"):
            return None
        return int(decoded.split(":", maxsplit=1)[1])
    except Exception:
        return None
