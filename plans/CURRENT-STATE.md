# Current ADA baseline

Recorded 2026-10-11 UTC (2026-10-11 in America/Phoenix). Read current source and tests before implementing a phase;
this file is a planning snapshot, not a permanent claim about the repository.

## Implemented

Release 0.2.0 uses Python 3.12, FastAPI, SQLAlchemy/Alembic, PostgreSQL 17 on the
user's Windows host and native Ollama. SQLite is a migrated test backend.
One Uvicorn worker and bounded in-flight generation remain the deployment model.

Phase 0 established token-authenticated users, private personality profiles,
conversation/prompt snapshots, durable request IDs, history and retry/recovery.
Phase 1 added owned personal/project scopes, exact source versions, explicit
facts/preferences/decisions and transactional valid-time corrections.
Phase 2 added full-text/subject retrieval, a whole-prompt byte budget, exact
evidence checks, source labels and durable per-request retrieval snapshots.

Migrations 0001–0009 remain unchanged by Phase 13; current head is 0010. Baseline v4 is
current for new conversations. v3 retains claim retrieval; earlier conversations
retain their saved prompt until explicitly upgraded.

## Current contract

Inspect `src/ada/api.py` and `contracts/openapi.json` for exact schemas. Existing
routes cover authenticated me/capabilities, personalities, conversations/events,
messages/request status/retrieval traces, scopes, notes/source versions, claims,
corrections and retrieval diagnostics. The browser API explorer is `/docs`.

Ownership comes from the bearer credential, not a submitted owner field. A
conversation selects one owned scope. Scopes are private; shared membership and
cross-user private access is not implemented. Phase 05 explicit admin grants allow
only sanitized monitoring metadata. Source mapping proves provenance, not truth or
the semantic correctness of the model's sentence.

`GET /v1/conversations/{id}/events` returns event text, request ID/status and
source-version ID. Source cards are recovered from the matching request response;
they must not be reconstructed from today's claim list. Conversation/event reads
and the other client endpoints now have explicit output schemas exported to
OpenAPI, including sanitized errors and retrieval details.

Chat returns a complete response. There is no streaming, cancellation endpoint,
automatic memory extraction, PDF/OCR, external write executor,
voice interface or local mobile model. Static warmth/style
configuration exists; dynamic affect and learned relationship preferences do not.
Phase 08 implements bounded text/Markdown uploads and imported excerpt retrieval,
with separate document citations, exact versions and explicit request opt-in.
Phase 10 implements optional exact semantic retrieval; it is disabled by default
pending real-model evaluation and retains lexical fallback.

## Historical verification evidence — Phases 02A/03

The original packaged Linux run recorded 60 passed/50 skipped. The user's Windows
PostgreSQL run reported 105 passed, 3 failed, 2 skipped. All three failures were
installer fixture tests: native Windows relative paths were serialized with `\\`
while manifest keys require `/`. This update changes fixture serialization to
`.as_posix()` and adds a test that simulates Windows path objects on Linux.
The production migration validation remains strict.

The Phase 02A Linux run recorded 61 passed/50 skipped/1 existing warning;
Ruff lint and format checks passed across src, tests, migrations and scripts.
The additional passing test is the portable Windows-path regression. No
disposable PostgreSQL was configured for this local run.

The Phase 03 session reran the fixed suite on this Windows host: baseline pytest
61 passed/50 skipped; dedicated PostgreSQL suite 109 passed/2 expected SQLite
row-lock skips; Ruff lint and format passed. This closes the 02A target gate.
These local results supplement the earlier user and Linux evidence above.
The two SQLite copies of PostgreSQL-specific row-lock tests are expected to skip
when the PostgreSQL fixtures also run. The existing Starlette/httpx test-client
deprecation warning is separate from the failures; do not change pinned packages
merely to hide it during this update.

The user also reported a successful v3 prompt upgrade and real Ollama chat. This
is evidence that chat starts and replies on the target host. It does not by itself
measure citation correctness, retrieval quality, GPU placement or sustained latency.

## Boundaries to preserve

Exact UTF-8 source hashes; code-point evidence offsets; half-open validity
intervals; explicit user endorsements; immutable retry context/citations; no model
call in an open database transaction; server-controlled authorization; private
scope filtering before evidence is sent to a model; shared weights without shared
private memory; personality as expression configuration.

## Phase 03 foundations

`apps/android/` and `apps/admin-web/` contain development connection screens,
typed injected HTTP transports, explicit failure/screen state models, semantic
design tokens and reproducible build/test configurations. The Android app uses
Kotlin/Compose; the web app uses React/TypeScript/Vite. Test transports and
`scripts/client_test_server.py` are explicit test-only adapters; the latter uses
loopback, migrated disposable SQLite and a fake model.

The Phase 03 web foundation introduced no admin authority; Phase 06 now provides
read-only monitoring through the explicit Phase 05 grants. Its credential remains
in memory. Android Phase 04 adds owned conversation/history/chat/source
screens, manually issued credential enrollment, Keystore-encrypted pending
requests, identity-verified restart checks and explicit exact-payload retries.
Source/retry DTOs preserve the existing server contract. No schema migration is needed.
See STATUS/WORKLOG for actual checks and unresolved target verification.

The user confirmed a Samsung S24 FE running Android 16. Minimum SDK 26 is
compatible with that reported OS. Phase 04 physical-phone accessibility/connection,
real-model and release HTTPS checks remain pending target verification. A remote
connection/distribution setup and admin credential enrollment require later selected
work; phone inference is not implemented.

## Phase 05 monitoring

Migration 0004 follows the unchanged released head 0003. Empty grants, a fixed-field
rolling audit/state lock and monitoring indexes are implemented. Trusted local
`grant-admin`/`revoke-admin` commands use exact account UUIDs. All six `/v1/admin/`
GET routes require an existing bearer principal and current explicit grant; audit
and recheck happen before successful delivery. User endpoints remain owner-only.

Metadata queries exclude private text and credentials, preserve composite request
identity/null metrics/legacy traces and bound windows/pagination/polling/audit.
Readiness now requires 0004. Cached Ollama model-list health performs no generation
or network I/O within transactions. Admission is the actual one-worker process
semaphore; GPU and throughput remain unknown. Capabilities advertise availability
without granting access. See docs/ADMIN-MONITORING.md and STATUS/WORKLOG for exact
contracts, disposable PostgreSQL/HTTP/local-provider evidence and remaining target
installation/HTTPS/performance checks. No production migration, real grant,
admin dashboard or later backend feature was performed in this phase.

## Phase 06 admin web

The `/admin` SPA implements operator sign-in via admin-me, overview/provider
readiness, server-filtered request pagination, composite owner/request details,
retrieval budgets and audit metadata. Settings offers Oxford Blue #002147 by
default, Dark Red #350616 and Olive Green #3c4c24 with system/light/dark and larger
text. Only appearance preferences persist. Every monitoring read uses the actual
admin API; no direct database/provider access, raw chats or production fixtures.

Current-role loss/sign-out/switch clears all metadata and pending reads. Polling
is bounded/visible-only, respects Retry-After across views and marks transient
failures stale. Bigint time decoding, null/zero distinctions and legacy trace
labels preserve the server contract. No schema or API change was required.
Real Chromium/one-worker HTTP integration uses migrated disposable PostgreSQL
and actual grants/revocation. See STATUS/WORKLOG for checks, explicit test-fixture
health/error cases and remaining HTTPS/manual accessibility/performance evidence.
The intended application database and real account grants were not changed.

## Phase 07 Android explicit memory and personality

The Android Memory destination uses existing authenticated scope/source/claim
APIs for pagination, current/as-of/history, exact evidence and replacement links.
Remember and correction require a reviewed annotation/quote preview and explicit
Save. Encrypted immutable source/claim reservations and a durable note stage
support identical replay after interruption, while conflicts retain input for
review. UTF-16 selections become code-point spans without quote normalization;
model-generated sources cannot become user evidence. A future correction leaves
the old assertion visible until its half-open interval ends. Original chat
citations retain their saved validity/evidence snapshots.

Settings exposes the existing static personality enums and profile name, creating
a new owned profile for future conversations. Existing conversations retain frozen
personality/prompt snapshots. The additive encrypted v2 local record preserves
v1 chat recovery; logout/switch/401 clear both private journals and caches.
No server route, OpenAPI, migration, inference behavior or dependency was changed.
STATUS/WORKLOG distinguish local checks from physical S24 FE/Android 16, HTTPS,
TalkBack and actual model verification still needed on the target setup.

## Phase 08 text/Markdown documents and admin login repair

Authenticated raw uploads reserve immutable owner/scope/source/upload IDs and
exact bytes before parsing outside transactions. Atomic publication creates the
entire version, code-point chunks and rebuildable lexical projection together.
Ready/processing/failed receipts, exact text/raw/chunk reads and stable-source
version history use dedicated document routes. Imported/untrusted text cannot
support the existing explicit user-claim writer. Quotas count retained failed
receipts; no deletion or automatic cleanup service is implemented.

Opt-in document retrieval preserves original claim arrays and uses separate typed
D cards and frozen trace arrays. Owner/scope/publication/availability checks run
before candidates/context; historical requests cannot see later publications.
Claims and documents share prompt/item budgets. New conversations use v4; v3
claim retrieval and old completed replay remain supported. Prompt upgrades stay
explicit and audited. See docs/DOCUMENT-INGESTION.md for limits and compatibility.

Android now offers capability-gated Documents, file/paste preview and explicit
upload, status/version/chunk inspection and original request document cards.
Encrypted session format v3 retains v1/v2 recovery and adds an exact account-bound
document journal; restoration never submits a write automatically. The admin web
app remains a metadata dashboard.

The reported admin error was reproduced against the configured database at 0003.
After a verified private backup and the user's explicit account selection, the
login repair installed 0004 and granted that exact existing account admin access.
The browser now gives safe migration guidance for known readiness errors. No
live browser session was verified. Application migration 0005 is deliberately
uninstalled: running the new Phase 08 source requires its separate installation.
STATUS/WORKLOG record actual checks and remaining physical-phone/HTTPS/model
verification. PDF/OCR/embeddings/extraction/promotion and later phases remain
unimplemented; no Phase 08 deployment was performed.

## Phase 09 explicit scoped entities and aliases

Head 0006 adds owner/scope-constrained entities, historical aliases, optional
claim references, explicit self bindings, reversible merge lineage and audited
operation receipts. Existing claims remain unlinked until explicit user action.
No name, type or model suggestion establishes ownership or permission.

Exact NFKC/case/whitespace resolution exposes absent/resolved/ambiguous states and
explicit candidate selection. Alias expansion precedes retrieval ranking; ambiguous
linked assertions are withheld and alternatives remain in frozen request plans.
Historical canonical choices and original evidence survive rename, correction,
merge, failure retry and completed replay. Prompts remain v4/current and v3/claims.

Android's Memory screen offers a capability-gated entity editor with scope choice,
duplicate warning and explicit alias/link/self/rename/merge/undo review. Exact
operation recovery uses additive Keystore record v4, retaining v1–v3 journals.
The admin web remains metadata-only. See docs/ENTITIES-AND-ALIASES.md and
STATUS/WORKLOG for executable contracts, checks and remaining target verification.
The final read-only application check observed head 0005. Installing 0006 remains
separate and unperformed by this phase.
No automatic extraction or cross-user graph was implemented in Phase 09.

## Phase 10 optional exact semantic channel

Head 0007 adds only discardable derived embeddings. The server now has bounded
digest-checked Ollama embedding transport, atomic owner/scope rebuild, exact cosine
ranking and deterministic lexical-first channel fusion. Existing lexical behavior,
historical availability, ambiguous-entity exclusion, conflict groups, source
integrity, v3/v4 prompts and frozen failed/completed replay remain in force.
Embedding calls share chat admission and run outside transactions.

The selected embedding model is absent locally; semantic retrieval stays disabled
by default. Synthetic fixture comparison and 256-item/768-dimension capacity
checks are distinct from real-model benefit/resource measurements. Current
installation requires 0007, but this phase has not upgraded the application DB or
downloaded a model. See STATUS/WORKLOG and docs/EMBEDDINGS-AND-HYBRID-RETRIEVAL.md
for actual verification and pending activation. Later phases remain unimplemented.

## Phase 11 implementation

Migration 0008 adds owned selected-source extraction receipts, pending proposals,
audited revisions, explicit review receipts and original supporting evidence
mappings. Strict source/schema checks and bounded inference precede atomic
publication. No unreviewed proposal enters claim search or model context.
Explicit acceptance creates a new immutable user endorsement source and claim;
rejection creates no claim. Specific conflict correction and same-review-key
replay are atomic. Original model/imported trust and old mandatory evidence stay
intact. Optional review-v1/user_reviewed provenance distinguishes reviewed memory
without widening existing origin enums or refreshing historical request cards.

Android Memory hosts the inbox/detail/edit/accept/reject flow with encrypted v5
identity-bound draft/key recovery. Admin overview adds only state counts.
Capabilities distinguish selected-source proposals and explicit review from
still-disabled automatic extraction. Real qwen3.8:27b extraction and separately
labeled fixture evaluation ran on synthetic evidence; independent representative
quality evaluation remains pending. Read STATUS/WORKLOG for actual check counts.
The configured application remains at observed 0005, needs head 0008 installation,
and was not migrated. Semantic retrieval remains disabled by default. No later
phase or deployment is implemented.

## Phase 12 selected tool execution

Separate explicit ada-agent-v1 runs advertise calculator, memory_lookup and
source_lookup only. Typed native proposals require exact owner/scope-bound approval;
short fenced transactions, shared admission, bounded context/steps/time/calls and
durable receipts preserve historical plain chat. Model/provider calls occur outside
transactions. Recovery records unknown and never repeats ambiguous execution.
Android's Tools screen uses encrypted journal v6 (v1–v5 readable) and GET-only
restore; admin gets closed state counts only. Current application remains observed
0005; 0009 is not installed there. See
[the phase policy](../docs/TOOLS-AND-AGENT-LOOP.md) and actual checks in STATUS/WORKLOG.

## Phase 13 implemented boundary

Head 0010 adds exact source-linked generated episodes, bounded explicit summary,
pending-proposal and lexical-index jobs, and private request-ID navigation maps.
A single lifespan worker shares existing inference admission. Short reservation,
claim and fenced atomic publication transactions retain tracked lease/attempt
recovery without holding a connection during model inference. Generated episodes
remain separate from factual retrieval and ordinary chat; old snapshots/replay
remain unchanged. No automatic approval, deletion or later phase is implemented.

Android 0.13.0-episodes (versionCode 8) adds explicit history/source previews,
measured job states and encrypted v7 recovery (v1–v6 readable). Admin overview adds
closed state counts and newest-25 metadata only. Native summary evaluation uses
the configured Ollama model and a documented public synthetic corpus; quality
limits and actual checks are in STATUS/WORKLOG. Installation into the configured
application database and Samsung S24 FE/Android 16 checks remain separate tasks.
See [the Phase 13 policy](../docs/EPISODES-AND-CONSOLIDATION.md).
