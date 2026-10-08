"""Versioned, rebuildable lexical projection; no model-generated embeddings."""

import re

from sqlalchemy import delete, select

from ada.models import Claim, ClaimSearch, Scope

SEARCH_VERSION = "lexical-subject-v1"


def normalize(value: str) -> str:
    value = value.lower().replace("c++", "cpp").replace("c#", "csharp").replace("_", " ")
    return " ".join(re.sub(r"[^\w]+", " ", value).split())


def search_fields(claim):
    return {
        "claim_id": claim.id,
        "owner_id": claim.owner_id,
        "scope_id": claim.scope_id,
        "subject_key": normalize(claim.subject),
        "predicate_key": normalize(claim.predicate),
        "search_text": normalize(
            " ".join((claim.subject, claim.predicate, claim.value, claim.quote))
        ),
    }


def index_claim(db, claim):
    db.add(ClaimSearch(**search_fields(claim)))
    db.flush()


def rebuild_search(sessions):
    """Local administrator operation, locking scopes in the memory writer's order."""
    count = 0
    with sessions.begin() as db:
        scopes = db.scalars(select(Scope).order_by(Scope.id).with_for_update()).all()
        for scope in scopes:
            db.execute(
                delete(ClaimSearch).where(
                    ClaimSearch.owner_id == scope.owner_id, ClaimSearch.scope_id == scope.id
                )
            )
            rows = db.scalars(
                select(Claim).where(Claim.owner_id == scope.owner_id, Claim.scope_id == scope.id)
            )
            for claim in rows:
                index_claim(db, claim)
                count += 1
    return count
