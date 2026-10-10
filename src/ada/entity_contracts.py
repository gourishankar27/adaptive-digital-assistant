"""Explicit scoped identity HTTP contract, independent of authentication."""

from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, field_validator

from ada.memory import MemoryInput, Timestamp, time_ms

EntityKind = Literal["person", "project", "object", "other"]


class OperationInput(MemoryInput):
    operation_id: UUID


class EntityInput(OperationInput):
    entity_id: UUID
    label: str = Field(min_length=1, max_length=160)
    kind: EntityKind = "other"


class AliasInput(OperationInput):
    alias_id: UUID
    label: str = Field(min_length=1, max_length=160)


class RenameInput(OperationInput):
    label: str = Field(min_length=1, max_length=160)
    expected_revision: int = Field(ge=0, strict=True)


class MergeInput(OperationInput):
    target_id: UUID
    preview_token: str = Field(pattern=r"^[0-9a-f]{64}$")


class SelfInput(OperationInput):
    entity_id: UUID


class LinkInput(OperationInput):
    entity_id: UUID | None
    expected_entity_id: UUID | None


class ResolveInput(MemoryInput):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    self_reference: bool = Field(default=False, strict=True)
    selected_id: UUID | None = None
    as_of: AwareDatetime | None = None

    @field_validator("as_of")
    @classmethod
    def precise_time(cls, value):
        if value is not None:
            time_ms(value)
        return value


class EntityChoice(BaseModel):
    id: UUID
    label: str
    kind: EntityKind


class EntityOutput(EntityChoice):
    scope_id: UUID
    normalized_key: str
    revision: int
    redirect_id: UUID | None
    created_at: Timestamp
    is_self: bool
    origin: Literal["user_confirmed"] = "user_confirmed"


class AliasOutput(BaseModel):
    id: UUID
    scope_id: UUID
    entity_id: UUID
    label: str
    normalized_key: str
    canonical: bool
    created_at: Timestamp
    valid_to: Timestamp | None
    origin: Literal["user_confirmed"] = "user_confirmed"


class LinkOutput(BaseModel):
    claim_id: UUID
    entity_id: UUID | None
    original_subject: str


class EntityOperationOutput(BaseModel):
    id: UUID
    scope_id: UUID
    action: Literal[
        "create", "alias", "retire_alias", "rename", "self", "link", "merge", "undo_merge"
    ]
    created_at: Timestamp
    entity: EntityOutput | None = None
    alias: AliasOutput | None = None
    link: LinkOutput | None = None


class EntityResolutionOutput(BaseModel):
    state: Literal["resolved", "ambiguous", "absent"]
    name: str | None
    entity_id: UUID | None
    candidates: list[EntityChoice]
    alias_ids: list[UUID]
    explicitly_selected: bool = False
    truncated: bool = False
    policy: Literal["nfkc_casefold_whitespace_v1"] = "nfkc_casefold_whitespace_v1"


class MergePreviewOutput(BaseModel):
    source: EntityOutput
    target: EntityOutput
    alias_count: int
    claim_link_count: int
    self_binding_affected: bool
    preview_token: str
