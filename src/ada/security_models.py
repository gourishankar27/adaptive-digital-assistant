"""Digest-only credentials and minimal privacy-operation metadata; no source text."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class DeviceCredential(Base):
    __tablename__ = "device_credentials"
    __table_args__ = (
        UniqueConstraint("owner_id", "id"),
        ForeignKeyConstraint(["owner_id"], ["users.id"]),
        CheckConstraint("expires_at > created_at", name="device_credential_expiry"),
        Index("device_credential_owner", "owner_id", "created_at", "id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(36))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    label: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    last_used_at: Mapped[int | None] = mapped_column(BigInteger)
    revoked_at: Mapped[int | None] = mapped_column(BigInteger)
    rotated_from_id: Mapped[str | None] = mapped_column(String(36))


class DeletionPreview(Base):
    __tablename__ = "deletion_previews"
    __table_args__ = (ForeignKeyConstraint(["owner_id"], ["users.id"]),)
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    revision: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)
    counts: Mapped[dict] = mapped_column(JSON)


class DeletionJob(Base):
    __tablename__ = "deletion_jobs"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id"], ["users.id"]),
        CheckConstraint(
            "status IN ('queued','running','completed','failed')", name="deletion_status"
        ),
        CheckConstraint("attempt BETWEEN 0 AND 3", name="deletion_attempt"),
        Index("deletion_queue", "status", "created_at"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    preview_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    revision: Mapped[int] = mapped_column(BigInteger)
    counts: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
    attempt: Mapped[int] = mapped_column(BigInteger)
    lease_until: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[int] = mapped_column(BigInteger)
    finished_at: Mapped[int | None] = mapped_column(BigInteger)
    error_code: Mapped[str | None] = mapped_column(String(40))


class DeletedRequest(Base):
    __tablename__ = "deleted_requests"
    __table_args__ = (ForeignKeyConstraint(["owner_id"], ["users.id"]),)
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(36))
    deleted_at: Mapped[int] = mapped_column(BigInteger)
