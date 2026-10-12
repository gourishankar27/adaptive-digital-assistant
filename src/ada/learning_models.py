"""Live learned state is resettable; receipts contain identifiers/counts only."""

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from ada.models import Base

PREFERENCE_CHECK = "(field='verbosity' AND value IN ('concise','balanced','detailed')) OR (field='initiative' AND value IN ('respond','suggest')) OR (field='formality' AND value IN ('casual','neutral','formal')) OR (field='humor' AND value IN ('none','light')) OR (field='cadence' AND value IN ('direct','stepwise'))"


class LearningEnrollment(Base):
    __tablename__ = "learning_enrollments"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        CheckConstraint("status IN ('off','enrolled','paused')", name="learning_consent"),
        CheckConstraint("revision >= 1 AND epoch >= 0", name="learning_revision"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    revision: Mapped[int] = mapped_column(Integer)
    epoch: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    continuity_enabled: Mapped[bool] = mapped_column(Boolean)


class InteractionObservation(Base):
    __tablename__ = "interaction_observations"
    __table_args__ = (
        CheckConstraint(PREFERENCE_CHECK, name="learning_observation_values"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "scope_id", "source_version_id"],
            ["source_versions.owner_id", "source_versions.scope_id", "source_versions.id"],
        ),
        ForeignKeyConstraint(
            ["owner_id", "source_request_id"], ["requests.owner_id", "requests.id"]
        ),
        UniqueConstraint("owner_id", "scope_id", "epoch", "source_request_id", "field"),
        CheckConstraint(
            "confidence_class IN ('explicit_statement','repeated_observation','weak_inference')",
            name="learning_confidence",
        ),
        CheckConstraint("expires_at > created_at", name="learning_observation_expiry"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(Integer)
    source_request_id: Mapped[str] = mapped_column(String(36))
    source_version_id: Mapped[str] = mapped_column(String(36))
    field: Mapped[str] = mapped_column(String(20))
    value: Mapped[str] = mapped_column(String(20))
    quote_hash: Mapped[str] = mapped_column(String(64))
    confidence_class: Mapped[str] = mapped_column(String(30))
    extraction_version: Mapped[str] = mapped_column(String(40))
    purpose: Mapped[str] = mapped_column(String(30))
    source: Mapped[dict] = mapped_column(JSON)
    evidence: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
    expires_at: Mapped[int] = mapped_column(BigInteger)


class InteractionProposal(Base):
    __tablename__ = "interaction_proposals"
    __table_args__ = (
        CheckConstraint(PREFERENCE_CHECK, name="learning_proposal_values"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        UniqueConstraint("owner_id", "scope_id", "epoch", "field", "value"),
        CheckConstraint(
            "status IN ('pending','approved','rejected') AND revision >= 1",
            name="learning_proposal_state",
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(20))
    value: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    expires_at: Mapped[int] = mapped_column(BigInteger)


class LearnedPreference(Base):
    __tablename__ = "learned_preferences"
    __table_args__ = (
        CheckConstraint(PREFERENCE_CHECK, name="learning_reviewed_values"),
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
        ForeignKeyConstraint(
            ["owner_id", "proposal_id"],
            ["interaction_proposals.owner_id", "interaction_proposals.id"],
        ),
        UniqueConstraint("owner_id", "scope_id", "field"),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    epoch: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(20))
    value: Mapped[str] = mapped_column(String(20))
    account_wide: Mapped[bool] = mapped_column(Boolean)
    receipt_id: Mapped[str] = mapped_column(String(36))
    proposal_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[int] = mapped_column(BigInteger)


class LearningReceipt(Base):
    __tablename__ = "learning_receipts"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id", "scope_id"], ["scopes.owner_id", "scopes.id"]),
    )
    owner_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope_id: Mapped[str] = mapped_column(String(36))
    input_hash: Mapped[str] = mapped_column(String(64))
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[int] = mapped_column(BigInteger)
