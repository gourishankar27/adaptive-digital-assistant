"""Deterministic, explicit owner/scope identity links; never authentication."""

import json
import unicodedata
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from ada.entity_models import (
    ClaimEntityLink,
    Entity,
    EntityAlias,
    EntityMerge,
    EntityOperation,
    EntitySelfLink,
)
from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.memory import owned_scope, time_ms
from ada.models import Claim, now_ms

MAX_ENTITIES = 500
MAX_ALIASES = 20
MAX_LINKS = 1000
MAX_OPERATIONS = 10000


def entity_query_keys(query):
    # Query limits stay independent of the shorter display-name limit.
    words = " ".join(unicodedata.normalize("NFKC", query).casefold().split()).split()[:64]
    return sorted(
        {
            " ".join(words[i : i + size])
            for size in range(1, 7)
            for i in range(len(words))
            if len(" ".join(words[i : i + size])) <= 640
        }
    )[:200]


def entity_key(label):
    key = " ".join(unicodedata.normalize("NFKC", label).casefold().split())
    if not key or len(key) > 640:
        raise ServiceError(422, "invalid_entity_label")
    return key


def owned_entity(db, owner, scope, eid):
    row = db.scalar(
        select(Entity).where(Entity.id == eid, Entity.owner_id == owner, Entity.scope_id == scope)
    )
    if row is None:
        raise ServiceError(404, "entity_not_found")
    return row


class IdentityView:
    """One bounded as-known-at view; redirects and labels remain historical."""

    def __init__(self, db, owner, scope, at):
        self.db, self.owner, self.scope, self.at = db, owner, scope, at
        self.entities = {
            r.id: r
            for r in db.scalars(
                select(Entity).where(
                    Entity.owner_id == owner, Entity.scope_id == scope, Entity.created_at <= at
                )
            )
        }
        self.redirects = {
            r.source_id: r.target_id
            for r in db.scalars(
                select(EntityMerge).where(
                    EntityMerge.owner_id == owner,
                    EntityMerge.scope_id == scope,
                    EntityMerge.created_at <= at,
                    or_(EntityMerge.valid_to.is_(None), EntityMerge.valid_to > at),
                )
            )
        }
        self.self_id = db.scalar(
            select(EntitySelfLink.entity_id).where(
                EntitySelfLink.owner_id == owner,
                EntitySelfLink.scope_id == scope,
                EntitySelfLink.created_at <= at,
                or_(EntitySelfLink.valid_to.is_(None), EntitySelfLink.valid_to > at),
            )
        )

    def root(self, eid):
        seen = set()
        while eid in self.redirects:
            if eid in seen or len(seen) >= 16:
                raise ServiceError(409, "entity_redirect_cycle")
            seen.add(eid)
            eid = self.redirects[eid]
        if eid not in self.entities:
            raise ServiceError(409, "entity_history_invalid")
        return eid

    def choice(self, eid):
        root = self.root(eid)
        label = self.db.scalar(
            select(EntityAlias.label).where(
                EntityAlias.owner_id == self.owner,
                EntityAlias.scope_id == self.scope,
                EntityAlias.entity_id == root,
                EntityAlias.canonical.is_(True),
                EntityAlias.created_at <= self.at,
                or_(EntityAlias.valid_to.is_(None), EntityAlias.valid_to > self.at),
            )
        )
        if label is None:
            raise ServiceError(409, "entity_history_invalid")
        return {"id": root, "label": label, "kind": self.entities[root].kind}

    def resolve(self, name=None, *, self_reference=False, selected_id=None):
        aliases = []
        if self_reference:
            ids = {self.root(self.self_id)} if self.self_id else set()
        else:
            if name is None:
                raise ServiceError(422, "entity_name_required")
            aliases = self.db.scalars(
                select(EntityAlias)
                .where(
                    EntityAlias.owner_id == self.owner,
                    EntityAlias.scope_id == self.scope,
                    EntityAlias.normalized_key == entity_key(name),
                    EntityAlias.created_at <= self.at,
                    or_(EntityAlias.valid_to.is_(None), EntityAlias.valid_to > self.at),
                )
                .order_by(EntityAlias.id)
                .limit(65)
            ).all()
            ids = {self.root(r.entity_id) for r in aliases[:64]}
        truncated = len(aliases) > 64
        if selected_id is not None and selected_id not in ids:
            raise ServiceError(422, "entity_selection_not_candidate")
        state = (
            "resolved"
            if selected_id or (len(ids) == 1 and not truncated)
            else ("ambiguous" if ids else "absent")
        )
        return {
            "state": state,
            "name": name,
            "entity_id": selected_id or (next(iter(ids)) if state == "resolved" else None),
            "candidates": [self.choice(eid) for eid in sorted(ids)],
            "alias_ids": [r.id for r in aliases[:64]],
            "explicitly_selected": selected_id is not None,
            "truncated": truncated,
            "policy": "nfkc_casefold_whitespace_v1",
        }


def public_entity(db, row):
    view = IdentityView(db, row.owner_id, row.scope_id, now_ms())
    return {
        "id": row.id,
        "scope_id": row.scope_id,
        "label": row.label,
        "normalized_key": row.normalized_key,
        "kind": row.kind,
        "revision": row.revision,
        "redirect_id": row.redirect_id,
        "created_at": row.created_at,
        "is_self": row.redirect_id is None
        and view.self_id is not None
        and view.root(view.self_id) == row.id,
        "origin": "user_confirmed",
    }


def public_alias(row):
    return {
        k: getattr(row, k)
        for k in (
            "id",
            "scope_id",
            "entity_id",
            "label",
            "normalized_key",
            "canonical",
            "created_at",
            "valid_to",
        )
    } | {"origin": "user_confirmed"}


def link_claim(db, owner, scope, claim, eid, link_id, at):
    if eid is not None:
        owned_entity(db, owner, scope, eid)
    count = db.scalar(
        select(func.count())
        .select_from(ClaimEntityLink)
        .where(ClaimEntityLink.owner_id == owner, ClaimEntityLink.scope_id == scope)
    )
    if count >= MAX_LINKS:
        raise ServiceError(413, "entity_link_quota")
    old = db.scalar(
        select(ClaimEntityLink).where(
            ClaimEntityLink.owner_id == owner,
            ClaimEntityLink.scope_id == scope,
            ClaimEntityLink.claim_id == claim.id,
            ClaimEntityLink.valid_to.is_(None),
        )
    )
    previous = claim.subject_entity_id
    if old:
        old.valid_to = at
        db.flush()
    db.add(
        ClaimEntityLink(
            id=link_id,
            owner_id=owner,
            scope_id=scope,
            claim_id=claim.id,
            entity_id=eid,
            created_at=at,
        )
    )
    claim.subject_entity_id = eid
    for item in {previous, eid} - {None}:
        owned_entity(db, owner, scope, item).revision += 1
    return {"claim_id": claim.id, "entity_id": eid, "original_subject": claim.subject}


class EntityService:
    def __init__(self, sessions):
        self.sessions = sessions

    def _scope(self, owner, eid):
        with self.sessions() as db:
            scope = db.scalar(
                select(Entity.scope_id).where(Entity.owner_id == owner, Entity.id == eid)
            )
            if scope is None:
                raise ServiceError(404, "entity_not_found")
            return scope

    def _write(self, owner, scope, action, body, subject, callback):
        payload = body.model_dump(mode="json")
        fingerprint = content_hash(
            json.dumps(
                {"scope": scope, "action": action, "subject": subject, "input": payload},
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        try:
            with self.sessions.begin() as db:
                owned_scope(db, owner, scope, lock=True)
                old = db.get(EntityOperation, (owner, str(body.operation_id)))
                if old:
                    if old.scope_id != scope or old.input_hash != fingerprint:
                        raise ServiceError(409, "entity_operation_id_reused")
                    return old.result, False
                count = db.scalar(
                    select(func.count())
                    .select_from(EntityOperation)
                    .where(EntityOperation.owner_id == owner, EntityOperation.scope_id == scope)
                )
                if count >= MAX_OPERATIONS:
                    raise ServiceError(413, "entity_operation_quota")
                at = now_ms()
                result = {
                    "id": str(body.operation_id),
                    "scope_id": scope,
                    "action": action,
                    "created_at": at,
                } | callback(db, at)
                db.add(
                    EntityOperation(
                        owner_id=owner,
                        id=str(body.operation_id),
                        scope_id=scope,
                        action=action,
                        input_hash=fingerprint,
                        result=result,
                        created_at=at,
                    )
                )
                db.flush()
                return result, True
        except IntegrityError as exc:
            raise ServiceError(409, "entity_conflict") from exc

    def create(self, owner, scope, body):
        def write(db, at):
            count = db.scalar(
                select(func.count())
                .select_from(Entity)
                .where(Entity.owner_id == owner, Entity.scope_id == scope)
            )
            if count >= MAX_ENTITIES:
                raise ServiceError(413, "entity_quota")
            row = Entity(
                id=str(body.entity_id),
                owner_id=owner,
                scope_id=scope,
                label=body.label,
                normalized_key=entity_key(body.label),
                kind=body.kind,
                revision=0,
                created_at=at,
            )
            db.add(row)
            db.flush()
            db.add(
                EntityAlias(
                    id=str(uuid5(NAMESPACE_URL, row.id + "/canonical")),
                    owner_id=owner,
                    scope_id=scope,
                    entity_id=row.id,
                    label=row.label,
                    normalized_key=row.normalized_key,
                    canonical=True,
                    created_at=at,
                )
            )
            db.flush()
            return {"entity": public_entity(db, row)}

        return self._write(owner, scope, "create", body, None, write)

    def mutate(self, owner, eid, action, body):
        scope = self._scope(owner, eid)

        def write(db, at):
            row = owned_entity(db, owner, scope, eid)
            if action != "undo_merge" and row.redirect_id:
                raise ServiceError(409, "entity_retired")
            if action == "alias":
                count = db.scalar(
                    select(func.count())
                    .select_from(EntityAlias)
                    .where(
                        EntityAlias.entity_id == eid,
                        EntityAlias.owner_id == owner,
                        EntityAlias.scope_id == scope,
                    )
                )
                if count >= MAX_ALIASES:
                    raise ServiceError(413, "entity_alias_quota")
                alias = EntityAlias(
                    id=str(body.alias_id),
                    owner_id=owner,
                    scope_id=scope,
                    entity_id=eid,
                    label=body.label,
                    normalized_key=entity_key(body.label),
                    canonical=False,
                    created_at=at,
                )
                db.add(alias)
                db.flush()
                row.revision += 1
                return {"alias": public_alias(alias), "entity": public_entity(db, row)}
            if action == "rename":
                if row.revision != body.expected_revision:
                    raise ServiceError(409, "entity_revision_changed")
                count = db.scalar(
                    select(func.count())
                    .select_from(EntityAlias)
                    .where(
                        EntityAlias.entity_id == eid,
                        EntityAlias.owner_id == owner,
                        EntityAlias.scope_id == scope,
                    )
                )
                if count >= MAX_ALIASES:
                    raise ServiceError(413, "entity_alias_quota")
                key = entity_key(body.label)
                for old in db.scalars(
                    select(EntityAlias).where(
                        EntityAlias.entity_id == eid,
                        EntityAlias.owner_id == owner,
                        EntityAlias.scope_id == scope,
                        EntityAlias.valid_to.is_(None),
                        or_(EntityAlias.canonical.is_(True), EntityAlias.normalized_key == key),
                    )
                ):
                    old.valid_to = at
                db.flush()
                row.label, row.normalized_key = body.label, key
                row.revision += 1
                db.add(
                    EntityAlias(
                        id=str(body.operation_id),
                        owner_id=owner,
                        scope_id=scope,
                        entity_id=eid,
                        label=body.label,
                        normalized_key=key,
                        canonical=True,
                        created_at=at,
                    )
                )
                db.flush()
                return {"entity": public_entity(db, row)}
            if action == "merge":
                preview = self._preview(db, owner, scope, eid, str(body.target_id))
                if preview["preview_token"] != body.preview_token:
                    raise ServiceError(409, "entity_merge_preview_changed")
                row.redirect_id = str(body.target_id)
                row.revision += 1
                owned_entity(db, owner, scope, str(body.target_id)).revision += 1
                db.add(
                    EntityMerge(
                        id=str(body.operation_id),
                        owner_id=owner,
                        scope_id=scope,
                        source_id=eid,
                        target_id=str(body.target_id),
                        created_at=at,
                    )
                )
                db.flush()
                return {"entity": public_entity(db, row)}
            if action == "undo_merge":
                merge = db.scalar(
                    select(EntityMerge).where(
                        EntityMerge.owner_id == owner,
                        EntityMerge.scope_id == scope,
                        EntityMerge.source_id == eid,
                        EntityMerge.valid_to.is_(None),
                    )
                )
                if merge is None:
                    raise ServiceError(409, "entity_not_merged")
                merge.valid_to = at
                row.redirect_id = None
                row.revision += 1
                owned_entity(db, owner, scope, merge.target_id).revision += 1
                db.flush()
                return {"entity": public_entity(db, row)}
            raise ServiceError(422, "invalid_entity_action")

        return self._write(owner, scope, action, body, eid, write)

    def retire_alias(self, owner, aid, body):
        with self.sessions() as db:
            alias = db.scalar(
                select(EntityAlias).where(EntityAlias.owner_id == owner, EntityAlias.id == aid)
            )
            if alias is None:
                raise ServiceError(404, "entity_alias_not_found")
            scope = alias.scope_id

        def write(db, at):
            alias = db.scalar(
                select(EntityAlias).where(
                    EntityAlias.owner_id == owner,
                    EntityAlias.scope_id == scope,
                    EntityAlias.id == aid,
                )
            )
            if alias.canonical or alias.valid_to is not None:
                raise ServiceError(409, "entity_alias_not_retirable")
            alias.valid_to = at
            owned_entity(db, owner, scope, alias.entity_id).revision += 1
            return {"alias": public_alias(alias)}

        return self._write(owner, scope, "retire_alias", body, aid, write)

    def self_link(self, owner, scope, body):
        def write(db, at):
            row = owned_entity(db, owner, scope, str(body.entity_id))
            if row.kind != "person" or row.redirect_id:
                raise ServiceError(422, "invalid_self_entity")
            old = db.scalar(
                select(EntitySelfLink).where(
                    EntitySelfLink.owner_id == owner,
                    EntitySelfLink.scope_id == scope,
                    EntitySelfLink.valid_to.is_(None),
                )
            )
            if old:
                old.valid_to = at
                db.flush()
            db.add(
                EntitySelfLink(
                    id=str(body.operation_id),
                    owner_id=owner,
                    scope_id=scope,
                    entity_id=row.id,
                    created_at=at,
                )
            )
            row.revision += 1
            db.flush()
            return {"entity": public_entity(db, row)}

        return self._write(owner, scope, "self", body, None, write)

    def claim_link(self, owner, cid, body):
        with self.sessions() as db:
            scope = db.scalar(
                select(Claim.scope_id).where(Claim.owner_id == owner, Claim.id == cid)
            )
            if scope is None:
                raise ServiceError(404, "claim_not_found")

        def write(db, at):
            row = db.scalar(
                select(Claim).where(
                    Claim.owner_id == owner, Claim.scope_id == scope, Claim.id == cid
                )
            )
            if row.subject_entity_id != (
                str(body.expected_entity_id) if body.expected_entity_id else None
            ):
                raise ServiceError(409, "claim_entity_link_changed")
            return {
                "link": link_claim(
                    db,
                    owner,
                    scope,
                    row,
                    str(body.entity_id) if body.entity_id else None,
                    str(body.operation_id),
                    at,
                )
            }

        return self._write(owner, scope, "link", body, cid, write)

    def _preview(self, db, owner, scope, source, target):
        a, b = owned_entity(db, owner, scope, source), owned_entity(db, owner, scope, target)
        if a.id == b.id or a.redirect_id or b.redirect_id or a.kind != b.kind:
            raise ServiceError(409, "invalid_entity_merge")
        view = IdentityView(db, owner, scope, now_ms())
        affected = {eid for eid in view.entities if view.root(eid) in {source, target}}
        view.redirects[source] = target
        for eid in affected:
            view.root(eid)
        del view.redirects[source]
        aliases = db.scalars(
            select(EntityAlias.id)
            .where(
                EntityAlias.owner_id == owner,
                EntityAlias.scope_id == scope,
                EntityAlias.entity_id.in_(affected),
                EntityAlias.valid_to.is_(None),
            )
            .order_by(EntityAlias.id)
        ).all()
        links = db.scalars(
            select(ClaimEntityLink.id)
            .where(
                ClaimEntityLink.owner_id == owner,
                ClaimEntityLink.scope_id == scope,
                ClaimEntityLink.entity_id.in_(affected),
                ClaimEntityLink.valid_to.is_(None),
            )
            .order_by(ClaimEntityLink.id)
        ).all()
        self_affected = view.self_id is not None and view.root(view.self_id) in {source, target}
        token = content_hash(
            json.dumps(
                [
                    owner,
                    scope,
                    source,
                    target,
                    a.revision,
                    b.revision,
                    sorted(affected),
                    aliases,
                    links,
                    self_affected,
                ],
                separators=(",", ":"),
            )
        )
        return {
            "source": public_entity(db, a),
            "target": public_entity(db, b),
            "alias_count": len(aliases),
            "claim_link_count": len(links),
            "self_binding_affected": self_affected,
            "preview_token": token,
        }

    def preview(self, owner, eid, target):
        scope = self._scope(owner, eid)
        with self.sessions.begin() as db:
            owned_scope(db, owner, scope, lock=True)
            return self._preview(db, owner, scope, eid, target)

    def list(self, owner, scope, limit=50, offset=0):
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            return [
                public_entity(db, r)
                for r in db.scalars(
                    select(Entity)
                    .where(Entity.owner_id == owner, Entity.scope_id == scope)
                    .order_by(Entity.created_at, Entity.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]

    def get(self, owner, eid):
        scope = self._scope(owner, eid)
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            return public_entity(db, owned_entity(db, owner, scope, eid))

    def aliases(self, owner, eid, limit=50, offset=0):
        scope = self._scope(owner, eid)
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            return [
                public_alias(r)
                for r in db.scalars(
                    select(EntityAlias)
                    .where(
                        EntityAlias.owner_id == owner,
                        EntityAlias.scope_id == scope,
                        EntityAlias.entity_id == eid,
                    )
                    .order_by(EntityAlias.created_at, EntityAlias.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]

    def resolve(self, owner, scope, body):
        with self.sessions.begin() as db:
            owned_scope(db, owner, scope, lock=True)
            return IdentityView(
                db, owner, scope, time_ms(body.as_of) if body.as_of else now_ms()
            ).resolve(
                body.name,
                self_reference=body.self_reference,
                selected_id=str(body.selected_id) if body.selected_id else None,
            )

    def operation(self, owner, oid):
        with self.sessions() as db:
            row = db.get(EntityOperation, (owner, oid))
            if row is None:
                raise ServiceError(404, "entity_operation_not_found")
            owned_scope(db, owner, row.scope_id)
            return row.result

    def audit(self, owner, scope, limit=50, offset=0):
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            return [
                r.result
                for r in db.scalars(
                    select(EntityOperation)
                    .where(EntityOperation.owner_id == owner, EntityOperation.scope_id == scope)
                    .order_by(EntityOperation.created_at.desc(), EntityOperation.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]
