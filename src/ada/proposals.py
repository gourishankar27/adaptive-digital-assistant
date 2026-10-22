"""Selected-source extraction and explicit, atomic user endorsement.

No model can invoke review. Only authenticated API input creates an endorsement;
unreviewed proposals never join claim search or model context.
"""

import json
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from ada.entities import IdentityView, link_claim, owned_entity
from ada.errors import ServiceError
from ada.evidence import content_hash, record_source
from ada.extraction import EXTRACTOR_VERSION, MAX_OUTPUT_BYTES, extraction_messages
from ada.memory import MemoryService, owned_scope, time_ms
from ada.models import Claim, DocumentUpload, Source, SourceVersion, now_ms
from ada.proposal_contracts import Candidate, ExtractionResult, SourcePin
from ada.proposal_models import ClaimSupport, MemoryExtraction, MemoryProposal, MemoryReview
from ada.retrieval import iso_time
from ada.search import index_claim, normalize

MAX_SOURCE_BYTES = 6000
MAX_EXTRACTIONS = 100
MAX_PROPOSALS = 400


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return content_hash(canonical(value))


def stable_id(owner, key, suffix):
    return str(uuid5(NAMESPACE_URL, "ada-review-v1/" + owner + "/" + key + "/" + suffix))


class ProposalService:
    def __init__(self, sessions, provider, capacity):
        self.sessions, self.provider, self.capacity = sessions, provider, capacity

    def _support(self, db, owner, scope, pins):
        result = []
        for pin in pins:
            p = SourcePin.model_validate(pin) if isinstance(pin, dict) else pin
            row = db.execute(
                select(SourceVersion, Source.kind)
                .join(
                    Source,
                    (Source.id == SourceVersion.source_id)
                    & (Source.owner_id == SourceVersion.owner_id)
                    & (Source.scope_id == SourceVersion.scope_id),
                )
                .where(
                    SourceVersion.id == str(p.source_version_id),
                    SourceVersion.owner_id == owner,
                    SourceVersion.scope_id == scope,
                )
            ).first()
            if row is None:
                raise ServiceError(404, "proposal_source_not_found")
            source, kind = row
            if (
                source.version != p.version
                or source.content_hash != p.content_hash
                or content_hash(source.content) != p.content_hash
            ):
                raise ServiceError(409, "proposal_source_changed")
            if not 0 <= p.span_start < p.span_end <= len(source.content):
                raise ServiceError(422, "proposal_invalid_span")
            quote = source.content[p.span_start : p.span_end]
            if not quote.strip() or len(quote.encode("utf-8")) > MAX_SOURCE_BYTES:
                raise ServiceError(422, "proposal_invalid_span")
            if kind == "imported_document":
                upload = db.scalar(
                    select(DocumentUpload).where(
                        DocumentUpload.owner_id == owner,
                        DocumentUpload.scope_id == scope,
                        DocumentUpload.source_version_id == source.id,
                        DocumentUpload.state == "ready",
                    )
                )
                if upload is None:
                    raise ServiceError(409, "proposal_source_unpublished")
                if upload.media_type == "application/pdf":
                    from ada.pdfs import projection_hash

                    instant = now_ms()
                    if (
                        upload.published_at is None
                        or upload.published_at > instant
                        or upload.available_from > instant
                        or (upload.available_to is not None and upload.available_to <= instant)
                        or projection_hash(upload, source.content) != p.content_hash
                    ):
                        raise ServiceError(409, "proposal_source_changed")
            result.append(
                {
                    "source_id": source.source_id,
                    "source_version": source.version,
                    "source_origin": kind,
                    "trust_class": source.trust_class,
                    "evidence": {
                        "source_version_id": source.id,
                        "span_start": p.span_start,
                        "span_end": p.span_end,
                        "quote": quote,
                        "content_hash": source.content_hash,
                    },
                }
            )
        if sum(len(r["evidence"]["quote"].encode("utf-8")) for r in result) > MAX_SOURCE_BYTES:
            raise ServiceError(413, "proposal_source_bound")
        return result

    def _job_output(self, db, job):
        return {
            "id": job.id,
            "scope_id": job.scope_id,
            "state": job.state,
            "model": job.model,
            "extractor_version": job.extractor_version,
            "validation": job.validation,
            "error_code": job.error_code,
            "created_at": job.created_at,
            "proposal_ids": list(
                db.scalars(
                    select(MemoryProposal.id)
                    .where(
                        MemoryProposal.owner_id == job.owner_id,
                        MemoryProposal.scope_id == job.scope_id,
                        MemoryProposal.extraction_id == job.id,
                    )
                    .order_by(MemoryProposal.id)
                )
            ),
        }

    def extraction(self, owner, key):
        with self.sessions() as db:
            job = db.get(MemoryExtraction, (owner, key))
            if job is None:
                raise ServiceError(404, "extraction_not_found")
            return self._job_output(db, job)

    def extract(self, owner, scope, body):
        key = str(body.extraction_id)
        payload = body.model_dump(mode="json")
        hashed = fingerprint(payload)
        with self.sessions.begin() as db:
            owned_scope(db, owner, scope, lock=True)
            old = db.get(MemoryExtraction, (owner, key))
            if old:
                if old.scope_id != scope or old.input_hash != hashed:
                    raise ServiceError(409, "extraction_id_reused")
                if old.state == "processing":
                    if now_ms() - old.created_at < 120000:
                        raise ServiceError(409, "extraction_in_progress")
                    old.state, old.error_code = "failed", "extraction_interrupted"
                    old.validation = {"valid": False, "errors": [old.error_code]}
                return self._job_output(db, old), False
            # Authenticate and bound selected evidence before acquiring/inferencing.
            self._support(db, owner, scope, body.sources)
        if not self.capacity.acquire(blocking=False):
            raise ServiceError(503, "server_busy")
        try:
            with self.sessions.begin() as db:
                owned_scope(db, owner, scope, lock=True)
                if db.get(MemoryExtraction, (owner, key)):
                    raise ServiceError(409, "extraction_in_progress")
                if (
                    db.scalar(
                        select(func.count())
                        .select_from(MemoryExtraction)
                        .where(
                            MemoryExtraction.owner_id == owner, MemoryExtraction.scope_id == scope
                        )
                    )
                    >= MAX_EXTRACTIONS
                    or db.scalar(
                        select(func.count())
                        .select_from(MemoryProposal)
                        .where(MemoryProposal.owner_id == owner, MemoryProposal.scope_id == scope)
                    )
                    > MAX_PROPOSALS - 8
                ):
                    raise ServiceError(413, "proposal_retained_limit")
                support = self._support(db, owner, scope, body.sources)
                selected = [
                    pin
                    | {
                        "quote": item["evidence"]["quote"],
                        "trust_class": item["trust_class"],
                        "source_origin": item["source_origin"],
                    }
                    for pin, item in zip(payload["sources"], support)
                ]
                messages = extraction_messages(selected)
                # Conservative bytes plus framing/output reserve; never truncate excerpts.
                if (
                    sum(len(m["content"].encode("utf-8")) + 64 for m in messages) + 2048 + 512
                    > 8192
                ):
                    raise ServiceError(413, "proposal_context_bound")
                job = MemoryExtraction(
                    owner_id=owner,
                    id=key,
                    scope_id=scope,
                    input_hash=hashed,
                    sources=payload["sources"],
                    state="processing",
                    model=self.provider.model,
                    extractor_version=EXTRACTOR_VERSION,
                    validation={"valid": False, "errors": []},
                    error_code=None,
                    created_at=now_ms(),
                )
                db.add(job)
            error, candidates = None, []
            validation = {"schema_version": EXTRACTOR_VERSION, "valid": False, "errors": []}
            try:
                completion = self.provider.complete(messages)
                if (
                    completion.model != self.provider.model
                    or len(completion.text.encode("utf-8")) > MAX_OUTPUT_BYTES
                ):
                    raise ServiceError(422, "invalid_extraction_response")

                # Strict JSON: duplicate keys and nonfinite constants are never accepted.
                def pairs(items):
                    value = {}
                    for k, v in items:
                        if k in value:
                            raise ValueError("duplicate key")
                        value[k] = v
                    return value

                raw = json.loads(
                    completion.text,
                    object_pairs_hook=pairs,
                    parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
                )
                candidates = ExtractionResult.model_validate(raw).candidates
                for candidate in candidates:
                    if candidate.subject_entity_id is not None:
                        raise ServiceError(422, "extraction_entity_not_selected")
                    for pin in candidate.support:
                        if not any(
                            pin.source_version_id == p.source_version_id
                            and pin.content_hash == p.content_hash
                            and pin.version == p.version
                            and p.span_start <= pin.span_start < pin.span_end <= p.span_end
                            for p in body.sources
                        ):
                            raise ServiceError(422, "extraction_unselected_evidence")
                validation.update(valid=True, candidate_count=len(candidates))
            except ValidationError as exc:
                validation["issues"] = [
                    {"type": issue["type"], "loc": list(issue["loc"])} for issue in exc.errors()
                ]
                error = "invalid_extraction_schema"
            except (ValueError, TypeError, UnicodeError):
                error = "invalid_extraction_schema"
            except ServiceError as exc:
                error = exc.code
            except Exception as exc:
                code = getattr(exc, "code", "provider_unavailable")
                error = (
                    code
                    if code
                    in {
                        "model_not_found",
                        "provider_timeout",
                        "extraction_response_bound",
                        "invalid_extraction_response",
                        "provider_unavailable",
                    }
                    else "provider_unavailable"
                )
            with self.sessions.begin() as db:
                owned_scope(db, owner, scope, lock=True)
                job = db.get(MemoryExtraction, (owner, key))
                if job.state != "processing":
                    raise ServiceError(409, "extraction_superseded")
                if error is None:
                    try:
                        if self._support(db, owner, scope, body.sources) != support:
                            raise ServiceError(409, "proposal_source_changed")
                        staged = []
                        for index, candidate in enumerate(candidates):
                            evidence = self._support(db, owner, scope, candidate.support)
                            original = candidate.model_dump(mode="json")
                            final = dict(original)
                            if final["valid_from"] is None:
                                final["valid_from"] = iso_time(
                                    db.get(
                                        SourceVersion, evidence[0]["evidence"]["source_version_id"]
                                    ).created_at
                                )
                            final = Candidate.model_validate(final).model_dump(mode="json")
                            staged.append(
                                MemoryProposal(
                                    owner_id=owner,
                                    id=stable_id(owner, key, str(index)),
                                    scope_id=scope,
                                    extraction_id=key,
                                    status="pending",
                                    revision=1,
                                    original_candidate=original,
                                    candidate=final,
                                    edits=[],
                                    support=evidence,
                                    model=job.model,
                                    extractor_version=EXTRACTOR_VERSION,
                                    validation=validation,
                                    rejection_reason=None,
                                    created_at=now_ms(),
                                )
                            )
                        retained = db.scalar(
                            select(func.count())
                            .select_from(MemoryProposal)
                            .where(
                                MemoryProposal.owner_id == owner, MemoryProposal.scope_id == scope
                            )
                        )
                        if retained + len(staged) > MAX_PROPOSALS:
                            raise ServiceError(413, "proposal_retained_limit")
                        db.add_all(staged)
                    except (ServiceError, ValidationError) as exc:
                        # Validation finishes before any proposal is staged for publication.
                        error = getattr(exc, "code", "invalid_extraction_schema")
                job.state, job.error_code = ("failed" if error else "completed"), error
                job.validation = validation | ({"valid": False, "errors": [error]} if error else {})
                db.flush()
                return self._job_output(db, job), True
        except IntegrityError:
            raise ServiceError(409, "proposal_conflict") from None
        finally:
            self.capacity.release()

    def _owned(self, db, owner, key, *, lock=False):
        scope = db.scalar(
            select(MemoryProposal.scope_id).where(
                MemoryProposal.owner_id == owner, MemoryProposal.id == key
            )
        )
        if scope is None:
            raise ServiceError(404, "proposal_not_found")
        owned_scope(db, owner, scope, lock=lock)
        return db.get(MemoryProposal, (owner, key))

    def _conflicts(self, db, proposal, candidate):
        start = time_ms(candidate.valid_from)
        end = time_ms(candidate.valid_to) if candidate.valid_to else None
        rows = db.scalars(
            select(Claim)
            .where(
                Claim.owner_id == proposal.owner_id,
                Claim.scope_id == proposal.scope_id,
                or_(Claim.valid_to.is_(None), Claim.valid_to > start),
                Claim.valid_from < end if end is not None else True,
            )
            .order_by(Claim.id)
            .limit(1001)
        ).all()
        if len(rows) > 1000:
            raise ServiceError(413, "proposal_conflict_bound")
        view = IdentityView(db, proposal.owner_id, proposal.scope_id, start)
        entity = None
        if candidate.subject_entity_id:
            owned_entity(db, proposal.owner_id, proposal.scope_id, str(candidate.subject_entity_id))
            entity = view.root(str(candidate.subject_entity_id))
        conflicts = []
        for row in rows:
            same = (
                view.root(row.subject_entity_id) == entity
                if entity and row.subject_entity_id
                else not entity and normalize(row.subject) == normalize(candidate.subject)
            )
            if (
                same
                and normalize(row.predicate) == normalize(candidate.predicate)
                and row.kind == candidate.kind
            ):
                conflicts.append(
                    {
                        k: getattr(row, k)
                        for k in (
                            "id",
                            "value",
                            "valid_from",
                            "valid_to",
                            "status",
                            "write_hash",
                            "subject_entity_id",
                        )
                    }
                )
        return conflicts, entity

    def _preview(self, db, p):
        c = Candidate.model_validate(p.candidate)
        support = self._support(db, p.owner_id, p.scope_id, c.support)
        if support != p.support:
            raise ServiceError(409, "proposal_source_changed")
        conflicts, entity = self._conflicts(db, p, c)
        hashed = fingerprint(
            {
                "proposal_id": p.id,
                "revision": p.revision,
                "candidate": p.candidate,
                "support": support,
                "conflicts": conflicts,
                "canonical_entity": entity,
            }
        )
        receipt = db.scalar(
            select(MemoryReview.id).where(
                MemoryReview.owner_id == p.owner_id, MemoryReview.proposal_id == p.id
            )
        )
        return {
            "id": p.id,
            "scope_id": p.scope_id,
            "extraction_id": p.extraction_id,
            "status": p.status,
            "revision": p.revision,
            "candidate": p.candidate,
            "original_candidate": p.original_candidate,
            "support": support,
            "conflicts": conflicts,
            "review_hash": hashed,
            "model": p.model,
            "extractor_version": p.extractor_version,
            "validation": p.validation,
            "rejection_reason": p.rejection_reason,
            "review_id": receipt,
            "created_at": p.created_at,
        }

    def detail(self, owner, key):
        with self.sessions() as db:
            return self._preview(db, self._owned(db, owner, key))

    def list(self, owner, scope, status, limit, offset):
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            query = select(MemoryProposal).where(
                MemoryProposal.owner_id == owner, MemoryProposal.scope_id == scope
            )
            if status:
                query = query.where(MemoryProposal.status == status)
            return [
                self._preview(db, p)
                for p in db.scalars(
                    query.order_by(MemoryProposal.created_at, MemoryProposal.id)
                    .limit(limit)
                    .offset(offset)
                )
            ]

    def _validated_edit(self, db, p, candidate):
        if candidate.support != Candidate.model_validate(p.candidate).support:
            raise ServiceError(422, "proposal_support_immutable")
        if candidate.subject_entity_id:
            owned_entity(db, p.owner_id, p.scope_id, str(candidate.subject_entity_id))
        if candidate.valid_from is None:
            raise ServiceError(422, "proposal_effective_date_required")
        return candidate.model_dump(mode="json")

    def edit(self, owner, key, body):
        with self.sessions.begin() as db:
            p = self._owned(db, owner, key, lock=True)
            self._check_preview(db, p, body)
            final = self._validated_edit(db, p, body.candidate)
            if final == p.candidate:
                return self._preview(db, p)
            if p.revision >= 50:
                raise ServiceError(413, "proposal_revision_limit")
            p.edits = p.edits + [
                {
                    "revision": p.revision,
                    "candidate": p.candidate,
                    "principal_id": owner,
                    "edited_at": now_ms(),
                }
            ]
            p.candidate, p.revision = final, p.revision + 1
            db.flush()
            return self._preview(db, p)

    def _check_preview(self, db, p, body):
        if p.status != "pending" or p.revision != body.revision:
            raise ServiceError(409, "proposal_revision_changed")
        if self._preview(db, p)["review_hash"] != body.review_hash:
            raise ServiceError(409, "proposal_preview_changed")

    def receipt(self, owner, key):
        with self.sessions() as db:
            row = db.get(MemoryReview, (owner, key))
            if row is None:
                raise ServiceError(404, "review_not_found")
            return row.result

    def review(self, owner, key, body):
        payload = body.model_dump(mode="json")
        hashed = fingerprint({"proposal_id": key, "body": payload})
        review_id = str(body.review_id)
        try:
            with self.sessions.begin() as db:
                p = self._owned(db, owner, key, lock=True)
                old_receipt = db.get(MemoryReview, (owner, review_id))
                if old_receipt:
                    if old_receipt.input_hash != hashed or old_receipt.proposal_id != key:
                        raise ServiceError(409, "review_id_reused")
                    return old_receipt.result, False
                final = self._validated_edit(db, p, body.candidate)
                self._check_preview(db, p, body)
                if final != p.candidate:
                    raise ServiceError(409, "proposal_content_not_reviewed")
                timestamp = now_ms()
                result = {
                    "id": review_id,
                    "proposal_id": key,
                    "scope_id": p.scope_id,
                    "principal_id": owner,
                    "decision": body.decision,
                    "revision": p.revision,
                    "review_hash": body.review_hash,
                    "claim_id": None,
                    "endorsement_source_version_id": None,
                    "created_at": timestamp,
                }
                if body.decision == "accept":
                    endorsement = canonical(
                        {
                            "type": "ada_user_endorsement_v1",
                            "decision": "accept",
                            "annotation": body.annotation,
                            "subject": final["subject"],
                            "predicate": final["predicate"],
                            "value": final["value"],
                            "kind": final["kind"],
                            "valid_from": final["valid_from"],
                            "valid_to": final["valid_to"],
                            "subject_entity_id": final["subject_entity_id"],
                            "proposal_id": key,
                            "review_id": review_id,
                        }
                    )
                    source = record_source(
                        db,
                        owner=owner,
                        scope_id=p.scope_id,
                        content=endorsement,
                        kind="user_note",
                        source_id=stable_id(owner, review_id, "endorsement"),
                    )
                    start = time_ms(body.candidate.valid_from)
                    end = time_ms(body.candidate.valid_to) if body.candidate.valid_to else None
                    fields = {
                        "owner_id": owner,
                        "scope_id": p.scope_id,
                        "subject": final["subject"],
                        "predicate": final["predicate"],
                        "value": final["value"],
                        "kind": final["kind"],
                        "valid_from": start,
                        "valid_to": end,
                        "source_version_id": source.id,
                        "span_start": 0,
                        "span_end": len(endorsement),
                        "quote": endorsement,
                        "evidence_hash": source.content_hash,
                    }
                    if final["subject_entity_id"]:
                        fields["subject_entity_id"] = final["subject_entity_id"]
                    target = None
                    if body.replace_claim_id:
                        conflicts, _ = self._conflicts(db, p, body.candidate)
                        if str(body.replace_claim_id) not in {r["id"] for r in conflicts}:
                            raise ServiceError(409, "proposal_correction_changed")
                        target = db.get(Claim, str(body.replace_claim_id))
                        if target.status != "active":
                            raise ServiceError(409, "claim_already_superseded")
                        if start <= target.valid_from or (
                            target.valid_to is not None and start > target.valid_to
                        ):
                            raise ServiceError(422, "correction_outside_validity_interval")
                    claim = Claim(
                        id=stable_id(owner, review_id, "claim"),
                        write_hash=MemoryService._write_hash(fields, target.id if target else None),
                        provenance={
                            "version": "review-v1",
                            "origin": "user_reviewed",
                            "proposal_id": key,
                            "review_id": review_id,
                            "model": p.model,
                            "extractor_version": p.extractor_version,
                            "support": p.support,
                        },
                        **fields,
                    )
                    db.add(claim)
                    db.flush()
                    if final["subject_entity_id"]:
                        link_claim(
                            db,
                            owner,
                            p.scope_id,
                            claim,
                            final["subject_entity_id"],
                            stable_id(owner, review_id, "entity"),
                            timestamp,
                        )
                    index_claim(db, claim)
                    if target:
                        target.valid_to, target.status, target.superseded_by = (
                            start,
                            "superseded",
                            claim.id,
                        )
                    result.update(claim_id=claim.id, endorsement_source_version_id=source.id)
                elif body.replace_claim_id is not None:
                    raise ServiceError(422, "rejection_cannot_correct")
                receipt = MemoryReview(
                    owner_id=owner,
                    id=review_id,
                    scope_id=p.scope_id,
                    proposal_id=key,
                    input_hash=hashed,
                    decision=body.decision,
                    revision=p.revision,
                    review_hash=body.review_hash,
                    annotation=body.annotation,
                    claim_id=result["claim_id"],
                    endorsement_source_version_id=result["endorsement_source_version_id"],
                    result=result,
                    created_at=timestamp,
                )
                db.add(receipt)
                db.flush()
                if result["claim_id"]:
                    for index, item in enumerate(p.support):
                        e = item["evidence"]
                        db.add(
                            ClaimSupport(
                                owner_id=owner,
                                scope_id=p.scope_id,
                                claim_id=result["claim_id"],
                                ordinal=index,
                                review_id=review_id,
                                source_version_id=e["source_version_id"],
                                evidence_hash=e["content_hash"],
                                span_start=e["span_start"],
                                span_end=e["span_end"],
                                quote=e["quote"],
                            )
                        )
                p.status = "accepted" if body.decision == "accept" else "rejected"
                p.rejection_reason = body.annotation if body.decision == "reject" else None
                db.flush()
                return result, True
        except IntegrityError:
            raise ServiceError(409, "review_conflict") from None
