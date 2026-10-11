# Selected-source proposals and explicit review

Phase 11 adds user-initiated suggestions and a private Android review inbox.
Unreviewed proposals never enter claim search, semantic ranking or chat context.
Automatic extraction and automatic approval remain disabled. Clients call ADA
HTTP; only the server calls Ollama, outside database transactions and under the
same process-local admission limit as chat. Use one Uvicorn worker.

## Extraction and integrity

The owner explicitly selects one to four immutable source-version/hash/code-point
spans in one owned scope. Notes, model events and ready imported document versions
retain their original trust. The server verifies complete source hashes and exact
nonempty excerpts before inference and again before publishing a proposal batch.
Publication is all-or-nothing. Historical versions remain eligible when their exact
owned source exists; they are never substituted with the newest version.

The typed result permits at most eight candidates with subject, predicate, value,
fact/preference/decision kind, effective dates, supporting pins and optional finite
confidence. Confidence is advisory. Unknown fields, duplicate JSON keys, nonfinite
numbers, invented source references, invalid spans and model-selected canonical
entity IDs fail validation. A user can explicitly select an owned canonical entity
while editing. Source instructions cannot authorize actions or grant permissions.

Selected quotes total at most 6,000 UTF-8 bytes. The complete serialized prompt,
message framing, 2,048 output allowance and conservative overhead fit an 8,192
context bound. The adapter limits content to 16 KiB, HTTP response to 64 KiB and
inference to the smaller of configured timeout and 60 seconds. It requests strict
JSON schema, temperature zero, no tools, no thinking output and no streaming to
clients. There is one extraction attempt per key; no autonomous iteration or retry.
Ollama request options follow its [chat API](https://docs.ollama.com/api/chat) and
[structured output documentation](https://docs.ollama.com/capabilities/structured-outputs).

Each scope retains at most 100 extraction receipts and 400 proposals, including
failures and reviewed history. Publication rechecks retained counts under the
scope lock, so concurrent model calls cannot overrun the proposal bound. A
proposal permits 50 audited edits. Conflict
inspection is bounded at 1,000 overlapping claims and fails closed on overflow.
Processing receipts become interrupted on an explicit same-key POST replay after 120
seconds; starting another attempt requires a new explicit extraction key. No
background task, deletion or automatic cleanup is implemented.

## Implemented HTTP surface

Every operation requires a bearer owner. Foreign resources return sanitized 404.
Input does not accept owner, principal, trust or permission fields.

| Method and path | Behavior |
|---|---|
| POST `/v1/scopes/{scope_id}/memory-extractions` | Exact extraction UUID and selected pins; 201 new, 200 terminal replay, 409 changed key/input or active processing. |
| GET `/v1/memory-extractions/{id}` | Owned state, safe validation/model metadata and stable proposal IDs. |
| GET `/v1/scopes/{scope_id}/memory-proposals` | Status-filtered array, default 25/max 50, bounded offset 10,000. |
| GET `/v1/memory-proposals/{id}` | Original/current candidate, exact support, model/version, validation, revision, conflicts and current review hash. |
| POST `/v1/memory-proposals/{id}/edit` | Exact pending revision/hash, immutable support, audited candidate change and new preview. |
| POST `/v1/memory-proposals/{id}/review` | Explicit accept/reject, final annotation, exact candidate/revision/hash and review UUID; optional specific replacement claim. |
| GET `/v1/memory-reviews/{id}` | Original durable principal-bound decision and claim/endorsement receipt. |

The server locks the owned scope for edit/review. The review hash includes the
candidate, exact support, conflicting claims and canonical mapping. A racing edit,
source change, claim change or identity mapping change returns 409. Reusing a review
UUID with identical input returns the saved receipt, even after later changes;
different input returns 409. Derived resource IDs include the authenticated
owner, so the same client nonce can be used independently by different accounts.
Safe validation results contain issue locations/types,
not raw model prompts, validator inputs or operational source logs.

## Endorsement, correction and compatible provenance

Acceptance creates a new immutable `user_explicit` note containing the user's
final structured annotation, dates, decision and proposal/review references. Its
exact full endorsement span is the claim's mandatory evidence. Separate scoped
support mappings retain the original model/imported/user excerpts and trust.
Acceptance does not relabel, modify or replace the original source. Rejection
stores the user's private reason and receipt without creating a claim or source.

Correction requires one explicitly selected, previewed overlapping active claim.
Its half-open interval closes under the existing correction policy; other values
are preserved. Claim, endorsement, support mappings, correction and review receipt
commit together. Any storage/index failure rolls everything back.

Capabilities add `memory_proposals=selected_sources_v1`, `memory_review=true` and
`memory_provenance=review-v1`; `automatic_memory_extraction` remains false. Existing
v1 `origin` enums and fields remain unchanged. An optional `provenance` object
identifies reviewed claims/cards with `version=review-v1`, `origin=user_reviewed`,
proposal/review IDs, model/extractor version and exact supporting source origins.
The legacy claim envelope remains `origin=user_asserted` because its mandatory
evidence is the new explicit endorsement. Updated clients display User reviewed;
older clients still receive an actual explicit assertion rather than model text
misrepresented as user-authored. Legacy claims have no reviewed provenance.

Fresh retrieval validates the receipt/proposal/support mapping and exact original
source integrity before admitting a reviewed claim. An invalid mapping excludes
the claim. Existing request fingerprints, v3/v4 prompts and completed/failed
frozen context are unchanged; historical cards are never rebuilt from current data.

## Android and administration

Memory opens a capability-gated inbox with scope selection, proposed fields,
literal exact excerpts, trust/model metadata, dates, canonical links and conflict
preview. The user saves edits and inspects the new revision before confirming
acceptance or rejection with their annotation. There is no bulk approval.
The source/document/entity pickers initially show at most 50 items each; inbox and
scope lists offer pagination. The native UI selects one excerpt per extraction;
the API supports four. Large notes require a shorter source or document excerpt.

The existing Keystore AES-GCM no-backup record advances to v5, retaining the
256 KiB bound and compatibility with v1–v4 chat/memory/document/entity journals.
One unsent proposal draft and one exact pending operation are bound to normalized
server/owner/scope. Save precedes HTTP. Restore never POSTs. Check receipt or retry
identical input explicitly after verifying identity; logout/account change/key
loss clears private state. Lost approval delivery preserves the original review
key; server replay cannot create a second endorsement or claim.

Admin overview adds only windowed pending/accepted/rejected counts. Its closed
decoder never displays proposal fields, decision annotations or supporting quotes.
Administration still requires an explicit server grant; it grants no review right
over another user's private proposal.

## Migration and verification boundaries

New head **0008** adds proposal/extraction/review/support tables with scoped native
foreign keys, indexes and decision consistency checks, plus nullable claim
provenance. Migrations 0001–0007 and mandatory original evidence remain unchanged.
Populated review history refuses downgrade; use a verified backup restoration plan.
An empty review schema can downgrade and re-upgrade. The configured application was
observed at 0005 and is deliberately not upgraded by this implementation task.
Back up and run the existing migration procedure before operational use of head
0008. This document does not authorize installation or deployment.

The checked-in eight-case corpus is entirely synthetic: five annotated positive
cases across user/imported/model sources, Unicode and decisions, plus instruction,
question and ambiguous-identity negatives. Evaluate with:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_extraction.py --provider fixture
.\.venv\Scripts\python.exe scripts/evaluate_extraction.py --provider ollama
```

Both commands use disposable migrated SQLite, not private application evidence.
The benchmark also runs against dedicated PostgreSQL through pytest. Reports live
under ignored `.pytest_cache`; do not copy raw private evidence into plans or logs.
The explicit gold fixture yielded five exact supported proposals and five explicit
endorsements on both databases; its precision/recall of 1 is tautological fixture
verification. Real local `qwen3.8:27b` yielded four proposals with four exact support
matches, zero extraction failures and four independently edited, explicitly
confirmed synthetic endorsements. It abstained on the tentative model-output case
and all three negatives. Strict subject/predicate/value/kind gold-string precision
and recall were both zero because the four annotations used different field wording. Exact
evidence does not measure semantic entailment or factual accuracy. Representative
authorized corpus evaluation and independent manual annotation remain target work.

Actual checks, failures, final device results and installation limits are recorded
in [STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md). Physical Samsung
S24 FE/Android 16, release HTTPS and manual TalkBack verification remain pending.
No later phase, automatic memory writer or deployment is included.
