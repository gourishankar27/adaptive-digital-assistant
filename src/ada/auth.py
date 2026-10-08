import hashlib
import secrets

from sqlalchemy import select

from ada.models import User


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_user(sessions, name: str) -> tuple[str, str]:
    name = name.strip()
    if not 1 <= len(name) <= 80:
        raise ValueError("Name must contain 1–80 characters")
    token = secrets.token_urlsafe(32)
    with sessions.begin() as db:
        user = User(name=name, token_hash=token_hash(token))
        db.add(user)
        db.flush()
        return user.id, token


def rotate_token(sessions, name: str) -> str:
    token = secrets.token_urlsafe(32)
    with sessions.begin() as db:
        user = db.scalar(select(User).where(User.name == name).with_for_update())
        if user is None:
            raise ValueError("User not found")
        user.token_hash = token_hash(token)
    return token
