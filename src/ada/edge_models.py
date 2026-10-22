"""Installation-signed, untrusted device drafts; no chat/fact/tool write authority."""

from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base


class EdgeDevice(Base):
    __tablename__ = "edge_devices"
    __table_args__ = (
        CheckConstraint(
            "revision>=1 AND last_sequence>=0 AND epoch>=0", name="edge_device_counters"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    epoch: Mapped[int] = mapped_column(BigInteger)
    revision: Mapped[int] = mapped_column(Integer)
    last_sequence: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(80))
    public_key: Mapped[str] = mapped_column(String(256))
    enrollment_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    revoked_at: Mapped[int | None] = mapped_column(BigInteger)
    revocation_id: Mapped[str | None] = mapped_column(String(36))
    revocation_hash: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[int] = mapped_column(BigInteger)


class EdgeProposal(Base):
    __tablename__ = "edge_proposals"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "device_id"], ["edge_devices.owner_id", "edge_devices.id"]
        ),
        UniqueConstraint("owner_id", "device_id", "sequence", name="edge_proposal_sequence"),
        CheckConstraint("sequence>=1 AND epoch>=0", name="edge_proposal_counters"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    device_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(BigInteger)
    sequence: Mapped[int] = mapped_column(Integer)
    input_hash: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    output: Mapped[str] = mapped_column(Text)
    created_at: Mapped[int] = mapped_column(BigInteger)
