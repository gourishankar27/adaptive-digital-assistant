"""Password authority and digest-only, revocable session families."""

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base, new_id


class PasswordCredential(Base):
    __tablename__ = "password_credentials"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    login: Mapped[str] = mapped_column(String(160), unique=True)
    verifier: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[int] = mapped_column(BigInteger)


class LoginSession(Base):
    __tablename__ = "login_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(80))
    access_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[int] = mapped_column(BigInteger)
    access_expires_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    idle_expires_at: Mapped[int] = mapped_column(BigInteger)
    revoked_at: Mapped[int | None] = mapped_column(BigInteger)
    generation: Mapped[int] = mapped_column(BigInteger)


class RefreshVerifier(Base):
    __tablename__ = "refresh_verifiers"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    family_id: Mapped[str] = mapped_column(ForeignKey("login_sessions.id"), index=True)
    used_at: Mapped[int | None] = mapped_column(BigInteger)
