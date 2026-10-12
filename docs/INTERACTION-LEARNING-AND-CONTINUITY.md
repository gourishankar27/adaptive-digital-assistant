# Opt-in interaction learning and continuity

Phase 15 requires migration **0012**, after unchanged 0001–0011. Install into the
intended, backed-up application database separately using `alembic upgrade head`;
this implementation migrates disposable validation databases only. Existing
v3/v4 baselines and saved personality prompts remain unchanged. v1/v2 require the
existing explicit audited upgrade before expression/learning can affect replies.

## Consent and evidence

Learning is off per owned knowledge scope. Android Settings enrolls or resumes
only after an explicit choice. Pause retains inspectable state but stops new
observations, approvals and reuse. Off/reset removes live observations, proposals
and learned defaults from that scope, including account reuse derived from it.
Source messages, factual claims and original episodes are separate records.

The bounded first implementation collects **selected completed user chat
interactions**, not automatic background extraction. The user chooses an exact
source and one allowlisted wording value: verbosity, initiative, formality, humor
or cadence. The server validates owner/scope, completed request, immutable version,
hash, code-point span and user trust. Notes, imported documents, generated summaries,
assistant events and retries cannot manufacture independent interaction evidence.
No provider inference runs during collection or review.

An InteractionObservation records owner/context, exact source lineage/request,
time, confidence class, extraction/policy version and interaction-only purpose.
Explicit statements, repeated observations and weak inference stay distinguishable.
Annotations are **unreviewed interpretations**, even when their source is explicit
user text. Original trust is retained. There is no factual promotion or mood diagnosis.

Default `ADA_LEARNING_THRESHOLD=3`, configurable from 3 to 10, requires distinct
completed request IDs and distinct NFKC/case/whitespace-normalized selected-quote
hashes. This conservatively discounts identical wording across legitimate turns
too. A single explicit exchange cannot create a durable learned rule; a user can
instead choose an explicit Phase 14 setting. Weak guesses expire after seven days
and never count; other observations expire after 90 days. Expired records are
excluded, not automatically deleted. Quotas include retained expired rows.

The synthetic evaluation compares thresholds 3 and 4 using single statements,
copied exchanges, weak guesses and three/four independent interactions, on SQLite
and native PostgreSQL. It checks measured eligibility and zero automatic
promotions. It does **not** establish preference accuracy, independent real-world
events, model extraction quality or an empirically optimal threshold. Representative
consented usage evaluation remains a target gate; a number is not proof.

## Review, precedence and recovery

Pending suggestions never affect chat. Explicit principal-bound approve/reject
checks the original source lineage, policy, expiry and exact proposal revision.
Edits choose another allowlisted value for the same field without rewriting the
original proposal/evidence. Approval creates a separate reviewed learned default
and minimal receipt. Further evidence revises the proposal and requires fresh
review; stale previews, other owners and changed keys fail closed.
Receipts freeze the reviewed proposal revision and contributing observation IDs.
Approved evidence stays inspectable after observation expiry or additional
evidence arrives, until reset removes live learned state.

Account reuse is a separate checkbox, off by default. Both the originating scope
and destination scope must be enrolled. Only the reviewed wording enum and receipt
identifier are reused; source quotes, project facts and episode history never
cross scopes. Scope-specific learned values win over account reuse. Most recent
review breaks ties deterministically within each level.

Precedence: current explicit instruction, frozen explicitly selected Phase 14
settings, reviewed learned defaults, personality defaults/session tone. Learning
never changes factual ranking/conflicts, memory permissions, tools or admin roles.
An `ada-learning-v1` overlay reserves exactly 1,024 UTF-8 bytes within the existing
whole-prompt budget. Values do not change that fixed cost. Consent off produces
no overlay. Requests freeze policy, consent epoch/revision, applied fields/receipts
and selected continuity cards. Failed retries and completed replay reuse original
messages and source maps, including after reset; no fresh learning is selected.

Android 0.15.0-learning uses Keystore-encrypted session record **v9**, preserving
v1–v8 reads. Every mutation reserves its original owner/server/scope/key/body
before POST. Restart verifies identity and checks the receipt with GET only.
Check, identical retry and local discard remain explicit; logout/account switch
clears private state, stale results are fenced, and 401 stops recovery.

## Source-linked continuity

Continuity is a separate scope consent choice and obeys `use_memory=false` and
existing current/as-of/date-required semantics. It examines at most 20 authorized
episodes in that scope. Relevance requires two overlapping nontrivial query terms
in **original source text**, never generated summary wording. Exact job/source
lineage, hashes, publication and availability are revalidated before selection.
Assistant/model-generated sources are excluded from this context path.

At most one episode contributes two complete excerpts, each at most 600 UTF-8
bytes, after factual evidence receives its budget and before history pairs.
Excerpts that cannot fit are withheld, never truncated. C cards retain original
trust and exact evidence, generated-episode trust, uncertainty and omitted-source
counts. Only supplied C labels cited in the answer appear in its optional
`continuity_citations`; the private request-learning endpoint also shows uncited
selection. Android Sources displays the original cards from that request.

Generated sections/omission narratives remain separate navigation and **are not
put into ordinary chat**. The policy instructs uncertainty and conflict handling,
forbids invented shared experiences, “I know you,” diagnosis and exclusive dependence.
Synthetic cases test fabricated summaries, conflicting original references, known
omissions, scope isolation, historical dates and frozen replay. These are server
context/provenance checks, not proof that a native model follows every instruction.

## API and retained data

Authenticated routes:

- `GET /v1/scopes/{scope_id}/learning`: consent, exact observations, proposals and reviewed defaults.
- `POST /v1/scopes/{scope_id}/learning/config`: CAS enrollment/pause/off and continuity choice.
- `POST /v1/scopes/{scope_id}/learning/observations`: selected-source tentative annotation.
- `POST /v1/scopes/{scope_id}/learning/reviews`: reviewed approve/reject/edit and account choice.
- `POST /v1/scopes/{scope_id}/learning/reset`: disable and erase live derived state.
- `GET /v1/learning-receipts/{operation_id}`: original minimal operation receipt.
- `GET /v1/requests/{request_id}/learning`: original nullable selection snapshot.

Same key/input returns the original receipt (200); a new successful mutation is
201. Changed keys/input, stale consent/review and unready sources are 409; foreign
references are 404, unauthenticated reads 401, bounds 413, malformed input 422,
database/capacity failure 503. Private routes use `Cache-Control: no-store`.

Limits: 200 retained observations/scope, 12 enum-based proposals/scope, five
reviewed fields/scope and 5,000 normal operation receipts/owner. Existing active
scopes retain one terminal reset slot beyond normal quota; new enrollment is
blocked at quota, so extra audit capacity is bounded. No learning search index,
embedding or shared cache is created; reset deletes all live preference rows and
new request selection rechecks consent/epoch under the same owner row lock.

Receipts contain only operation/scope/action/revision/epoch/time and optional
observation/proposal IDs/decision plus a server input digest. They contain no source
quotes or private preferences. Review lineage contains only revision/observation
identifiers, not a copied profile or source text. Reset does not refresh/delete immutable historical
chat/request snapshots: those are retained to preserve existing replay contracts.
Complete account erasure, backup expiry and historical-snapshot retention still
need an explicitly selected policy. The reset dialog discloses this limit.

Admin overview reports aggregate config/observe/review/reset counts in the selected
time window only. No private relationship profile, learned values, source text or
observation detail is granted to admins. Ordinary private endpoints stay owner-only.

Use the normal pytest/Ruff and disposable PostgreSQL gates, Android Gradle checks
and `apps/android/scripts/verify-learning-emulator.ps1`. Actual runs and pending
installation, physical Samsung S24 FE/Android 16, HTTPS/TalkBack and native-model
quality/resource checks are recorded in [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md). No later phase or deployment is part of this work.
