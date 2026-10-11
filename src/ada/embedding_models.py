"""Discardable exact vectors, with composite authority and evidence references."""

from sqlalchemy import JSON, BigInteger, CheckConstraint, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base, now_ms


class EmbeddingEntry(Base):
    __tablename__ = "embedding_entries"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "claim_id"],
            ["claims.owner_id", "claims.scope_id", "claims.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "chunk_id"],
            ["document_chunks.owner_id", "document_chunks.scope_id", "document_chunks.id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        CheckConstraint(
            "(kind = 'claim' AND claim_id IS NOT NULL AND chunk_id IS NULL AND item_id = claim_id) OR "
            "(kind = 'document' AND chunk_id IS NOT NULL AND claim_id IS NULL AND item_id = chunk_id)",
            name="embedding_item_reference",
        ),
        CheckConstraint(
            "dimensions >= 1 AND dimensions <= 768", name="embedding_dimensions_bounded"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    namespace: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(10), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    claim_id: Mapped[str | None] = mapped_column(String(36))
    chunk_id: Mapped[str | None] = mapped_column(String(36))
    source_version_id: Mapped[str] = mapped_column(String(36))
    source_hash: Mapped[str] = mapped_column(String(64))
    text_hash: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(100))
    model_digest: Mapped[str] = mapped_column(String(64))
    index_version: Mapped[str] = mapped_column(String(40))
    dimensions: Mapped[int] = mapped_column(Integer)
    vector: Mapped[list] = mapped_column(JSON)
    built_at: Mapped[int] = mapped_column(BigInteger, default=now_ms)
