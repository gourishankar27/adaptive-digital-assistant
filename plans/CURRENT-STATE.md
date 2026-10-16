# Current ADA baseline

Recorded 2026-10-12 UTC (2026-10-12 in America/Phoenix). Read current source and tests before implementing a phase;
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

Migrations 0001–0014 remain unchanged by Phase18; current head is 0015. Baseline v4 is
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

Legacy chat returns a complete response. Phase 16 adds authenticated durable
streaming/checkpoint recovery and explicit generation cancellation. There is no
automatic memory extraction, PDF/OCR, external write executor,
or local mobile language model. Phase 17 adds explicit on-device Android voice input
with separate review/endorsement lineage and optional offline TTS. Static warmth/style
configuration exists. Phase 14 adds opt-in bounded session expression; automatic
affect inference remains unimplemented. Phase 15 adds opted-in reviewed interaction
preferences and exact source-linked continuity, with reset and retained replay.
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

## Phase 14 implemented boundary

Head 0011 adds owner-target preferences, immutable reviewed receipts, frozen
conversation bindings, one bounded current session per conversation and nullable
historical request expression snapshots. Explicit precedence is personality,
account, scope, profile, then conversation. Defaults never propagate behind
existing conversation history. A separate expression-v1 policy preserves saved
v3/v4 prompts and factual retrieval; retries preserve exact state/messages.

Tone is disabled by default, strictly typed, limited per turn, decaying and
expiring. Reviewed model vectors remain proposals without explicit authenticated
acceptance. No normal model text is parsed into state and no mood classifier or
learning was added. Android 0.14.0-expression (versionCode 9) adds scoped Settings
and encrypted v8 GET-only receipt recovery with v1–v7 compatibility. Installation
into the application database is unperformed; its configured server was
unavailable during this phase. Native PostgreSQL 18 disposable validation is
distinct from earlier PostgreSQL 17/application evidence. See
[policy](../docs/INTERACTION-PREFERENCES-AND-AFFECT.md), STATUS and WORKLOG.

## Phase 15 implemented boundary

Head 0012 adds scope consent, exact source-linked interaction observations,
deduplicated tentative suggestions, explicit approve/edit/reject receipts,
reviewed wording defaults and request-frozen learning/continuity snapshots.
Explicit settings override learned defaults. Account reuse needs both scopes'
consent and exports only allowlisted wording enums. Pause disables new learning
and reuse; reset removes live derived state, including account reuse, while minimal
audit and immutable historical request replay remain. Generated summaries and
assistant text cannot become interaction evidence or factual authority.

Android 0.15.0-learning (versionCode 10) provides Settings consent, evidence/review,
pause/reset and encrypted v9 exact recovery with v1–v8 compatibility. Admin reports
aggregate operation counts only. See
[policy](../docs/INTERACTION-LEARNING-AND-CONTINUITY.md), STATUS and WORKLOG for
actual SQLite/native PostgreSQL/HTTP/emulator/browser/evaluation evidence and
pending intended installation, physical phone, HTTPS/accessibility and native-model
quality/resource checks. No application migration, later phase or deployment.

## Phase 16 implemented boundary

Head 0013 adds ordinary-chat durable streaming/checkpoints/SSE and explicitly
owned generation Stop. The original reservation, request UUID/options, frozen
retrieval/expression/continuity and legacy running/completed/failed schema remain.
Cancelled attempts are failed/request_cancelled and can be explicitly retried
against their original snapshot subject to revision checks. Partial text never
becomes a completed assistant event, factual evidence or source card.

Android 0.16.0-streaming uses the real authenticated HTTP transport, detaches on
navigation/conversation/background transitions and restores by GET under journal
v9. Admin exposes measured metadata only. Native Ollama completion/Stop and legacy
follow-up were measured separately from fake TCP/emulator fixtures. Local gates,
actual skips and pending installation/physical verification are in STATUS/WORKLOG.
The fresh application read still observes 0005; it was not migrated. One worker,
count-bounded private stream retention and separate cursor expiry remain limits.
See [the policy](../docs/STREAMING-AND-CANCELLATION.md). Stop at Phase 16.

## Phase 17 implemented boundary

Head 0014 adds immutable reviewed-voice lineage, with generated original ASR text
kept separate from approved user evidence. The Android 0.17.0-voice app uses only
on-device SpeechRecognizer on supported API31+ devices, defaults to en-US and
checks installed language support. Record/stop/discard and encrypted v10 review
are explicit; approval is required before one exact voice request is journaled.
GET-only recovery, frozen retries and owned Phase16 cancellation are reused.
There is no server audio/ASR, audio hash, system/network fallback or model download.
Only installed offline TTS voices read completed safe reply text. Playback stop,
focus/device interruptions and backgrounding never implicitly cancel generation.

See [the policy](../docs/VOICE-INTERFACE.md). S24 FE/Android16 physical audio,
en-US availability/quality, offline audio, resources/battery, permission dialogs,
headsets/calls, older APIs, release HTTPS and manual accessibility remain target
verification. A fresh read found the configured application database at 0005;
it was not installed/upgraded. Stop at Phase17; no later phase or deployment.

## Phase 17-A physical audit boundary — 2026-10-13 UTC

Samsung S24 FE/Android16 now has partial target evidence: installed en-US, actual
quiet/offline recognition, offline speaker/rates, capture/playback lifecycle,
owned HTTP lineage, Keystore/force-stop recovery and portrait/landscape font150%.
The existing implementation loses the recording intent across actual permission
dialogs. A separate foreground UID received audio focus while the isolated native
playback interruption callback did not fire; root cause/audible behavior remain
to investigate. [Phase 17-A](phase-17-a-s24-fe-validation-and-hardening.md) plans
these changes and a portable physical runner. No product code/contract/schema
was changed. Battery, speech-service resources, representative noise/accent
quality, accessories/calls, older APIs, release HTTPS/manual accessibility and
intended installation remain pending. Historical configured database 0005 was
not refreshed or migrated in this audit. Phases18–19 remain planned.


## Phase18 implementation — 2026-10-14 UTC

Supported head0015 adds configured digest-only device lifecycle, owner rate/body/
HTTP bounds, explicit retain-until-owner-deletion policy, all45-table saved-content
preview/confirmed leased erasure with tombstones/epochs, Android v11 recovery/settings
and admin privacy cache fencing. One Uvicorn worker remains required. Legacy tokens,
old prompts/requests, source trust and released0001–0014 migrations are preserved.
AES256-GCM/scrypt backups use the selected local folder and a consistent PostgreSQL
snapshot; isolated new-database restoration validates hashes and quarantines tokens,
then reconciles a current encrypted deletion ledger. Concrete runbooks and target
verification are in [SECURITY-AND-OPERATIONS](../docs/SECURITY-AND-OPERATIONS.md).
Phase17-A permission/focus lifecycle hardening and a separate-package physical runner
are implemented; new physical outcomes and unresolved gates are recorded in STATUS.
Prior phone/audit evidence above is historical. Phase19 remains unimplemented and
no live database backup/migration/deletion or deployment occurred in this task.
