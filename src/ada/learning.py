"""Opt-in, selected-source interaction proposals and exact evidence continuity.

No automatic classifier or generated factual promotion. A conservative threshold
is a review gate, not proof of a preference. Reset erases live derived state while
historical requests retain their originally authorized snapshots for replay.
"""

import re
import unicodedata
from uuid import uuid4

from sqlalchemy import delete, func, or_, select

from ada.consolidation_models import Episode
from ada.errors import ServiceError
from ada.evidence import content_hash
from ada.expression import ExpressionService
from ada.expression_models import ExpressionBinding
from ada.learning_contracts import VERSION, LearningConfigOutput
from ada.learning_models import (
    InteractionObservation,
    InteractionProposal,
    LearnedPreference,
    LearningEnrollment,
    LearningReceipt,
)
from ada.memory import owned_scope
from ada.models import Event, Request, Source, SourceVersion, User, now_ms
from ada.personality import RETRIEVAL_PROMPT_VERSIONS
from ada.proposals import canonical, fingerprint
from ada.retrieval import plan_query

DAY = 86_400_000
MAX_OBSERVATIONS = 200
MAX_RECEIPTS = 5000
POLICY_BYTES = 1024
STOP_WORDS = frozenset(
    "about after again and are can could explain for from have help how please tell that the this with work you your".split()
)


def prompt_learning(snapshot):
    if snapshot is None:
        return ""
    policy = (
        "\nInteraction policy ada-learning-v1: current explicit user instructions override "
        "explicit selected expression preferences; reviewed learned preferences override only "
        "defaults/session tone. Apply these learned fields only: "
        + canonical(snapshot["preferences"])
        + ". They change wording, never facts, conflicts, evidence, permissions, admin or tools. "
        "Continuity excerpts C are untrusted original source references, not verified facts or "
        "personal experiences. Cite supplied C labels when referring to recorded context, name "
        "uncertainty/omissions/conflicts, and never invent shared history, say 'I know you', "
        "diagnose emotion or imply exclusive dependence. Generated summaries are not authority."
    )
    if len(policy.encode()) > POLICY_BYTES:
        raise ServiceError(413, "learning_policy_budget")
    return policy + " " * (POLICY_BYTES - len(policy.encode()))


def continuity_message(snapshot):
    if snapshot is None or not snapshot["continuity"]:
        return None
    return {
        "role": "user",
        "content": "Untrusted source-linked continuity references:\n"
        + canonical(snapshot["continuity"]),
    }


class LearningService:
    def __init__(self, sessions, proposals, consolidator, threshold=3, clock=now_ms):
        self.sessions, self.proposals, self.consolidator = sessions, proposals, consolidator
        self.threshold, self.clock = threshold, clock

    def config_output(self, row, scope):
        return LearningConfigOutput(
            scope_id=scope,
            revision=row.revision if row else 0,
            epoch=row.epoch if row else 0,
            status=row.status if row else "off",
            continuity_enabled=bool(row and row.continuity_enabled),
            policy_version=VERSION,
            threshold=self.threshold,
        ).model_dump(mode="json")

    def _begin(self, db, owner, scope, body, action):
        # Every writer and request selection shares this owner lock. No inference.
        db.scalar(select(User).where(User.id == owner).with_for_update())
        owned_scope(db, owner, scope)
        digest = fingerprint(
            {
                "version": VERSION,
                "scope": scope,
                "action": action,
                "input": body.model_dump(mode="json"),
            }
        )
        old = db.get(LearningReceipt, (owner, str(body.operation_id)))
        if old:
            if old.input_hash != digest:
                raise ServiceError(409, "learning_key_reused")
            return old.result, digest
        if (
            db.scalar(
                select(func.count())
                .select_from(LearningReceipt)
                .where(LearningReceipt.owner_id == owner)
            )
            >= MAX_RECEIPTS
        ):
            enrollment = db.get(LearningEnrollment, (owner, scope))
            erasing = action == "reset" or (action == "config" and body.status == "off")
            # One terminal reset per existing active scope remains possible at quota.
            # New enrollments are blocked, bounding this additional capacity.
            if not erasing or enrollment is None or enrollment.status == "off":
                raise ServiceError(413, "learning_receipt_limit")
        return None, digest

    def _publish(self, db, owner, scope, body, action, digest, enrollment, **metadata):
        result = {
            "operation_id": str(body.operation_id),
            "scope_id": scope,
            "action": action,
            "revision": enrollment.revision,
            "epoch": enrollment.epoch,
            "observation_id": None,
            "proposal_id": None,
            "decision": None,
            "created_at": self.clock(),
            "observation_ids": [],
            "proposal_revision": None,
            **metadata,
        }
        db.add(
            LearningReceipt(
                owner_id=owner,
                id=str(body.operation_id),
                scope_id=scope,
                input_hash=digest,
                result=result,
                created_at=result["created_at"],
            )
        )
        db.flush()
        return result, True

    @staticmethod
    def _erase(db, owner, scope):
        for model in (LearnedPreference, InteractionProposal, InteractionObservation):
            db.execute(delete(model).where(model.owner_id == owner, model.scope_id == scope))

    def configure(self, owner, scope, body, reset=False):
        action = "reset" if reset else "config"
        with self.sessions.begin() as db:
            old, digest = self._begin(db, owner, scope, body, action)
            if old:
                return old, False
            row = db.get(LearningEnrollment, (owner, scope))
            if (row.revision if row else 0) != body.expected_revision:
                raise ServiceError(409, "learning_revision_changed")
            if row is None:
                row = LearningEnrollment(
                    owner_id=owner,
                    scope_id=scope,
                    revision=0,
                    epoch=0,
                    status="off",
                    continuity_enabled=False,
                )
                db.add(row)
            status = "off" if reset else body.status
            if status == "off":
                self._erase(db, owner, scope)
                row.epoch += 1
            row.revision += 1
            row.status = status
            row.continuity_enabled = not reset and status == "enrolled" and body.continuity_enabled
            return self._publish(db, owner, scope, body, action, digest, row)

    @staticmethod
    def _enrolled(db, owner, scope):
        row = db.get(LearningEnrollment, (owner, scope))
        if row is None or row.status != "enrolled":
            raise ServiceError(409, "learning_not_enrolled")
        return row

    def _source(self, db, owner, scope, pin):
        evidence = self.proposals._support(db, owner, scope, [pin])[0]
        source = db.get(Source, evidence["source_id"])
        event = db.get(Event, source.event_id) if source.event_id else None
        request = db.get(Request, (owner, event.request_id)) if event else None
        if (
            source.kind != "chat_event"
            or event is None
            or event.role != "user"
            or event.owner_id != owner
            or request is None
            or request.status != "completed"
            or evidence["trust_class"] != "user_explicit"
        ):
            raise ServiceError(422, "learning_requires_completed_user_interaction")
        version = db.get(
            SourceVersion,
            str(pin.source_version_id) if not isinstance(pin, dict) else pin["source_version_id"],
        )
        if any(
            t is not None and t > self.clock()
            for t in (event.created_at, source.created_at, version.created_at, request.finished_at)
        ):
            raise ServiceError(409, "learning_future_source")
        return evidence, request.id

    def _observations(self, db, p):
        return db.scalars(
            select(InteractionObservation)
            .where(
                InteractionObservation.owner_id == p.owner_id,
                InteractionObservation.scope_id == p.scope_id,
                InteractionObservation.epoch == p.epoch,
                InteractionObservation.field == p.field,
                InteractionObservation.value == p.value,
                InteractionObservation.expires_at > self.clock(),
            )
            .order_by(InteractionObservation.created_at, InteractionObservation.id)
        ).all()

    def _proposal_output(self, db, p):
        observations = self._observations(db, p)
        # A retry, copied quote or summary cannot increment independence.
        requests, quotes = set(), set()
        for o in observations:
            if (
                o.confidence_class != "weak_inference"
                and o.source_request_id not in requests
                and o.quote_hash not in quotes
            ):
                requests.add(o.source_request_id)
                quotes.add(o.quote_hash)
        count = len(requests)
        return {
            "id": p.id,
            "revision": p.revision,
            "values": {p.field: p.value},
            "status": p.status,
            "independent_count": count,
            "eligible": count >= self.threshold and p.expires_at > self.clock(),
            "observations": [o.id for o in observations],
            "expires_at": p.expires_at,
            "trust_class": "unreviewed_interpretation",
        }

    def observe(self, owner, scope, body):
        with self.sessions.begin() as db:
            old, digest = self._begin(db, owner, scope, body, "observe")
            if old:
                return old, False
            enrollment = self._enrolled(db, owner, scope)
            evidence, request = self._source(db, owner, scope, body.source)
            field, value = next(iter(body.values.model_dump(exclude_none=True).items()))
            if db.scalar(
                select(InteractionObservation.id).where(
                    InteractionObservation.owner_id == owner,
                    InteractionObservation.scope_id == scope,
                    InteractionObservation.epoch == enrollment.epoch,
                    InteractionObservation.source_request_id == request,
                    InteractionObservation.field == field,
                )
            ):
                raise ServiceError(409, "interaction_already_observed")
            if (
                db.scalar(
                    select(func.count())
                    .select_from(InteractionObservation)
                    .where(
                        InteractionObservation.owner_id == owner,
                        InteractionObservation.scope_id == scope,
                    )
                )
                >= MAX_OBSERVATIONS
            ):
                raise ServiceError(413, "learning_observation_limit")
            instant = self.clock()
            expiry = instant + (7 if body.confidence_class == "weak_inference" else 90) * DAY
            quote = unicodedata.normalize("NFKC", evidence["evidence"]["quote"]).casefold()
            observation = InteractionObservation(
                owner_id=owner,
                id=str(uuid4()),
                scope_id=scope,
                epoch=enrollment.epoch,
                source_request_id=request,
                source_version_id=str(body.source.source_version_id),
                field=field,
                value=value,
                quote_hash=content_hash(" ".join(quote.split())),
                confidence_class=body.confidence_class,
                extraction_version=VERSION,
                purpose="interaction_preference",
                source=body.source.model_dump(mode="json"),
                evidence=evidence,
                created_at=instant,
                expires_at=expiry,
            )
            db.add(observation)
            proposal = db.scalar(
                select(InteractionProposal).where(
                    InteractionProposal.owner_id == owner,
                    InteractionProposal.scope_id == scope,
                    InteractionProposal.epoch == enrollment.epoch,
                    InteractionProposal.field == field,
                    InteractionProposal.value == value,
                )
            )
            if proposal is None:
                proposal = InteractionProposal(
                    owner_id=owner,
                    id=str(uuid4()),
                    scope_id=scope,
                    epoch=enrollment.epoch,
                    field=field,
                    value=value,
                    revision=0,
                    status="pending",
                    expires_at=expiry,
                )
                db.add(proposal)
            proposal.revision += 1
            proposal.status = "pending"
            proposal.expires_at = max(proposal.expires_at, expiry)
            return self._publish(
                db,
                owner,
                scope,
                body,
                "observe",
                digest,
                enrollment,
                observation_id=observation.id,
                proposal_id=proposal.id,
                proposal_revision=proposal.revision,
            )

    def review(self, owner, scope, body):
        with self.sessions.begin() as db:
            old, digest = self._begin(db, owner, scope, body, "review")
            if old:
                return old, False
            enrollment = self._enrolled(db, owner, scope)
            p = db.get(InteractionProposal, (owner, str(body.proposal_id)))
            if p is None or p.scope_id != scope:
                raise ServiceError(404, "interaction_proposal_not_found")
            if (
                p.epoch != enrollment.epoch
                or p.revision != body.expected_revision
                or p.status != "pending"
                or p.expires_at <= self.clock()
            ):
                raise ServiceError(409, "learning_proposal_changed")
            if body.decision == "approve":
                if not self._proposal_output(db, p)["eligible"]:
                    raise ServiceError(409, "learning_insufficient_independent_evidence")
                for o in self._observations(db, p):
                    if o.extraction_version != VERSION or o.purpose != "interaction_preference":
                        raise ServiceError(409, "learning_policy_changed")
                    evidence, request = self._source(db, owner, scope, o.source)
                    if evidence != o.evidence or request != o.source_request_id:
                        raise ServiceError(409, "learning_source_changed")
                values = (
                    body.values.model_dump(exclude_none=True) if body.values else {p.field: p.value}
                )
                if set(values) != {p.field}:
                    raise ServiceError(422, "learning_edit_requires_same_field")
                previous = db.scalar(
                    select(LearnedPreference).where(
                        LearnedPreference.owner_id == owner,
                        LearnedPreference.scope_id == scope,
                        LearnedPreference.field == p.field,
                    )
                )
                if previous:
                    db.delete(previous)
                    db.flush()
                db.add(
                    LearnedPreference(
                        owner_id=owner,
                        id=str(uuid4()),
                        scope_id=scope,
                        epoch=enrollment.epoch,
                        field=p.field,
                        value=values[p.field],
                        account_wide=body.account_wide,
                        receipt_id=str(body.operation_id),
                        proposal_id=p.id,
                        created_at=self.clock(),
                    )
                )
            observations = self._observations(db, p) if body.decision == "approve" else []
            ids, hashes = [], set()
            for item in observations:
                if item.confidence_class != "weak_inference" and item.quote_hash not in hashes:
                    ids.append(item.id)
                    hashes.add(item.quote_hash)
            p.status = "approved" if body.decision == "approve" else "rejected"
            p.revision += 1
            return self._publish(
                db,
                owner,
                scope,
                body,
                "review",
                digest,
                enrollment,
                proposal_id=p.id,
                decision=body.decision,
                proposal_revision=body.expected_revision,
                observation_ids=ids,
            )

    def state(self, owner, scope):
        with self.sessions() as db:
            owned_scope(db, owner, scope)
            learned = db.scalars(
                select(LearnedPreference).where(
                    LearnedPreference.owner_id == owner, LearnedPreference.scope_id == scope
                )
            ).all()
            reviews = {}
            for p in learned:
                receipt = db.get(LearningReceipt, (owner, p.receipt_id))
                if (
                    receipt is None
                    or receipt.scope_id != scope
                    or receipt.result.get("decision") != "approve"
                ):
                    raise ServiceError(409, "learning_review_history_unavailable")
                reviews[p.receipt_id] = receipt.result
            reviewed_ids = {
                id_ for review in reviews.values() for id_ in review.get("observation_ids", [])
            }
            observations = db.scalars(
                select(InteractionObservation)
                .where(
                    InteractionObservation.owner_id == owner,
                    InteractionObservation.scope_id == scope,
                    or_(
                        InteractionObservation.expires_at > self.clock(),
                        InteractionObservation.id.in_(reviewed_ids),
                    ),
                )
                .order_by(InteractionObservation.created_at, InteractionObservation.id)
            ).all()
            proposals = db.scalars(
                select(InteractionProposal)
                .where(
                    InteractionProposal.owner_id == owner,
                    InteractionProposal.scope_id == scope,
                    InteractionProposal.expires_at > self.clock(),
                )
                .order_by(InteractionProposal.id)
            ).all()
            return {
                "config": self.config_output(db.get(LearningEnrollment, (owner, scope)), scope),
                "observations": [
                    {
                        "id": o.id,
                        "owner_id": owner,
                        "scope_id": scope,
                        "source_request_id": o.source_request_id,
                        "source": o.source,
                        "evidence": o.evidence,
                        "values": {o.field: o.value},
                        "confidence_class": o.confidence_class,
                        "interpretation_trust": "unreviewed_interpretation",
                        "extraction_version": o.extraction_version,
                        "purpose": o.purpose,
                        "created_at": o.created_at,
                        "expires_at": o.expires_at,
                    }
                    for o in observations
                ],
                "proposals": [self._proposal_output(db, p) for p in proposals],
                "learned": [
                    {
                        "id": p.id,
                        "values": {p.field: p.value},
                        "account_wide": p.account_wide,
                        "receipt_id": p.receipt_id,
                        "proposal_id": p.proposal_id,
                        "created_at": p.created_at,
                        "observation_ids": reviews[p.receipt_id].get("observation_ids", []),
                        "reviewed_revision": reviews[p.receipt_id].get("proposal_revision"),
                    }
                    for p in learned
                ],
            }

    def receipt(self, owner, key):
        with self.sessions() as db:
            row = db.get(LearningReceipt, (owner, key))
            if row is None:
                raise ServiceError(404, "learning_receipt_not_found")
            return row.result

    def request_snapshot(self, owner, key):
        with self.sessions() as db:
            row = db.get(Request, (owner, key))
            if row is None:
                raise ServiceError(404, "request_not_found")
            return {"request_id": key, "learning": row.learning_snapshot}

    def reserve_snapshot(self, db, conversation, content, expression, as_of, use_memory):
        owner, scope = conversation.owner_id, conversation.scope_id
        db.scalar(select(User).where(User.id == owner).with_for_update())
        enrollment = db.get(LearningEnrollment, (owner, scope))
        if (
            not enrollment
            or enrollment.status != "enrolled"
            or conversation.prompt_version not in RETRIEVAL_PROMPT_VERSIONS
        ):
            return None
        # All explicit fields override learned defaults, including frozen inherited settings.
        if expression:
            origins = expression["origins"]
        else:
            binding = db.get(ExpressionBinding, (owner, conversation.id))
            origins = (
                binding.origins if binding else ExpressionService.effective(db, conversation)[1]
            )
        rows = db.scalars(
            select(LearnedPreference)
            .join(
                LearningEnrollment,
                (LearnedPreference.owner_id == LearningEnrollment.owner_id)
                & (LearnedPreference.scope_id == LearningEnrollment.scope_id),
            )
            .where(
                LearnedPreference.owner_id == owner,
                LearningEnrollment.status == "enrolled",
                LearnedPreference.epoch == LearningEnrollment.epoch,
                LearnedPreference.created_at <= self.clock(),
                or_(LearnedPreference.scope_id == scope, LearnedPreference.account_wide),
            )
            .order_by(LearnedPreference.created_at, LearnedPreference.id)
        ).all()
        # Scope-specific learned settings override account reuse, regardless of recency.
        rows.sort(key=lambda p: p.scope_id == scope)
        preferences, receipts = {}, {}
        for row in rows:
            if origins[row.field] == "personality":
                preferences[row.field], receipts[row.field] = row.value, row.receipt_id
        snapshot = {
            "policy_version": VERSION,
            "scope_id": scope,
            "epoch": enrollment.epoch,
            "revision": enrollment.revision,
            "preferences": preferences,
            "receipts": receipts,
            "continuity": [],
            "continuity_reason": "disabled",
        }
        if not enrollment.continuity_enabled or not use_memory:
            return snapshot
        plan = plan_query(content, as_of)
        if plan["time_mode"] == "needs_date":
            snapshot["continuity_reason"] = "date_required"
            return snapshot
        cutoff = min(self.clock(), plan["as_of"])
        terms = set(re.findall(r"\w{3,}", content.casefold())) - STOP_WORDS
        snapshot["continuity_reason"] = "no_relevant_authorized_episode"
        episodes = db.scalars(
            select(Episode)
            .where(
                Episode.owner_id == owner,
                Episode.scope_id == scope,
                Episode.created_at <= cutoff,
                Episode.range_end <= cutoff + 1,
            )
            .order_by(Episode.created_at.desc(), Episode.id)
            .limit(20)
        ).all()
        for e in episodes:
            try:
                job = self.consolidator._owned(db, owner, e.job_id)
                self.consolidator._fresh(db, job)
                if e.sources != job.snapshot:
                    continue
                self.consolidator._sources(db, owner, scope, job.input["sources"], cutoff)
            except ServiceError:
                continue
            # Match original source text; generated summaries cannot create relevance.
            evidence = [
                s
                for s in e.sources
                if s["created_at"] <= cutoff
                and s["trust_class"] != "model_generated"
                and len(s["evidence"]["quote"].encode()) <= 600
            ]
            selected = [
                s
                for s in evidence
                if len(terms & set(re.findall(r"\w{3,}", s["evidence"]["quote"].casefold()))) >= 2
            ][:2]
            if not selected:
                continue
            snapshot["continuity"] = [
                {
                    k: s[k]
                    for k in (
                        "source_id",
                        "source_version",
                        "source_origin",
                        "trust_class",
                        "evidence",
                    )
                }
                | {
                    "label": "C" + str(i + 1),
                    "episode_id": e.id,
                    "summary_trust": "model_generated",
                    "uncertainty": "source_reference_not_verified_recollection",
                    "omitted_source_count": len(e.sources) - len(selected),
                }
                for i, s in enumerate(selected)
            ]
            snapshot["continuity_reason"] = "exact_original_sources"
            break
        return snapshot
