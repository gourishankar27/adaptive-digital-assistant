# Phase 11 — proposed memory with explicit user review

Status: implemented; final local Android verification in progress. Prerequisites: Phases 07 and 08; Phase 09 for canonical links.
Apply STANDARDS and CODEX-WORKFLOW. Automatic approval is outside this phase.

## Goal

Have a model suggest structured assertions from authorized source material, then
let the user inspect, edit, accept or reject them. Extraction output remains a
proposal until a validated, explicit endorsement creates durable memory.

## Checkpoints and data

Add MemoryProposal with owner/scope, input source-version/hash/span references,
candidate subject/predicate/value/kind/effective interval, model/version, status,
proposal revision and review receipt. Proposed confidence is advisory metadata,
not factual authority. Keep the full validation result and rejection reason
without storing credentials or unnecessary raw prompts in operational logs.

Extract only from selected owned sources outside transactions and within strict
size/context/iteration limits. Parse a typed schema; reject fabricated source IDs,
bad spans, stale hashes, missing evidence, foreign scope links and unknown fields.
Imported/model text cannot create a permission, system instruction or assertion
merely by asking the extractor to do so. Preserve original trust labels.

Expose owned list/detail/reject/review APIs with bounded pagination and stable
proposal IDs. Approval binds the exact reviewed revision/content/evidence hash
and authenticated principal. A model cannot call approval on the user's behalf.
Concurrent edit/review returns a conflict rather than endorsing unseen content.

## Promotion policy

Review creates a new explicit endorsement record in an immutable source version,
containing the user's final annotation and decision. Preserve the original
proposal and supporting sources as separate provenance links. Do not rewrite a
model-generated or imported source to `user_explicit` or reuse it as though the
user had authored every sentence.

Design the migration so current claims keep their mandatory original evidence.
New reviewed claims can use the exact endorsement span as mandatory user evidence
and additional authorized support links to the original excerpts. Expose origin
`user_reviewed` distinctly from current `user_asserted`; evolve clients/cards
compatibly and retain old enum behavior through explicit version/capability
handling. A review does not retroactively change earlier request citations.

If a proposal replaces a known assertion, preview its conflicting interval and
use the atomic correction policy. Never blanket overwrite all current values.
Approval/correction/review receipt must commit consistently and be idempotent
for the same review key. Failure cannot leave a claim approved without its
endorsement/support mapping.

## Android review UX

Add an inbox/detail flow showing proposed fields, original exact excerpts,
source origin, effective dates and conflicts. Accept, edit-and-accept and reject
are explicit actions; no preselected bulk approval. Review drafts and keys survive
interruption with identity-bound encrypted persistence. Do not show an extracted
claim as saved memory while awaiting review. Admin UI receives operational counts
only, not the user's review text.

## Verification and exit

Test malformed extraction, generated/imported trust, cross-scope injection, stale
source/version/proposal revision, concurrent review, duplicate approval, approval
response loss, conflict correction and unauthorized approval. Evaluate extraction
precision and evidence matching on a documented corpus; report real-model versus
stub runs separately. Run populated migrations, PostgreSQL and Android flows.

Exit with a real source→proposal→user review→claim flow, honest provenance and
reliable receipts. Capabilities still distinguish proposals from automatic memory
writes. Unreviewed output must never enter factual retrieval as an endorsed claim.

## Implementation record

The checkpoints are implemented in migration 0008, bounded selected-source
extraction, owned proposal/edit/review APIs, immutable endorsement and original
support mappings, exact principal/revision/hash receipts, specific atomic
correction, Android inbox and encrypted draft/key recovery, and admin counts only.
Optional review-v1 provenance preserves the original v1 enums and historical
request snapshots. Unreviewed proposals remain outside factual retrieval.

Real PostgreSQL migrations/concurrency/rollback, old-contract preservation, web
and Android unit/build checks, and the 26-case ordinary emulator suite passed.
The final separate force-stop stages and strict cold launch are still running.
Real Ollama and fixture evaluations ran separately on an eight-case synthetic
corpus; strict gold-string precision/recall was zero for the real model. Exact
support matching and explicit independent review do not establish entailment or
representative quality.

See [the implementation policy](../docs/MEMORY-PROPOSALS-AND-REVIEW.md),
[STATUS](STATUS.md) and [WORKLOG](WORKLOG.md) for checkpoints, exact checks,
intermediate failures, skips and remaining targets. Application head 0008
installation (observed application 0005), Samsung S24 FE/Android 16, release HTTPS,
manual TalkBack/keyboard accessibility, short-idle connection behavior and
representative real-model quality/load remain target verification. No standalone
old-checkout smoke, release signing/installation, ANN extension or semantic
activation was run. Populated migrated fixtures cover old replay; Phase 10's
disabled exact design remains unchanged. Stop at Phase 11; no later phase,
automatic approval, external message or deployment is included.
