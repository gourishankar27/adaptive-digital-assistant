# ADA

Phase31 adds selected text PDFs: isolated parsing, immutable original bytes and
extracted text/page maps, Android review and D source cards. Selected Phase19A
adds a device-draft study and signed proposal protocol. Both mobile candidates
failed reply quality: local drafting is disabled, `edge_inference=false`.
Current source: **0021 /76 tables /63 owner-content**, backup-v7;
Android25 /0.31.0-documents-drafts, encrypted journal18 (older versions readable).
PDF and device sync default off. Read [PDF setup/use](docs/PDF-INGESTION.md),
[the device study](docs/ON-DEVICE-DRAFTS.md) and [actual checks](plans/STATUS.md).
The bounded PDF implementation/automated exit is verified on SQLite/PostgreSQL,
actual Docker and the S24 FE/API36, including real HTTP/Keystore/restart recovery.
Public-sample readability is confirmed on the S24 FE. TalkBack and representative
personal-file acceptance remain pending.
No OCR, Phase19B integration, live migration or deployment. Earlier sections retain
their own milestone boundaries.

Phase30 adds **Projects & next actions**: explicit owner/scoped goals and tasks,
exact Save review from chat, immutable revisions, balanced selected-work briefs,
and separately consented questions/reminders. A due date never implies completion
or scheduling. Source requires **0020 / 74 tables**, owner-content61 and encrypted
backup-v6 (older formats remain readable). Android24 /0.30.0-work uses encrypted
journal17 and GET-only recovery; no private task reader was added to admin.
See [the usage/developer guide](docs/PROJECTS-AND-FOLLOW-THROUGH.md) and dated
[verification record](plans/STATUS.md). No installed database/app/service upgrade
or deployment occurred; Phase31 remains planned.

Phase29 adds a [local speech study and contract](docs/NATURAL-LOCAL-SPEECH.md),
explicit public voice preview and engine/model status. Platform on-device ASR and
offline TTS remain active; no new model/runtime is installed or selected. The
manifest byte checker does not install or activate models. Physical S24 FE quality,
resource and native focus/permission gates remain open. Server contracts, schema0019
and encrypted journal16 are unchanged; no deployment is included.

Phase28 adds **While you were away**: explicitly consented, source-pinned idle
reports and optional catalogue question drafts, with exact owner review/recovery.
Global work defaults off. Model summary support has a separate disabled safety
and usefulness gate; the initial job set performs no background GPU inference.
Current source requires **0019 /70 tables**, owner-content inventory57 and
backup-v5 (old formats remain readable). Read
[IDLE-REFLECTION-AND-DREAM-REVIEW](docs/IDLE-REFLECTION-AND-DREAM-REVIEW.md) for setup,
resource budgets, privacy, review, retention and remaining verification. This
source change does not migrate the live database, update the normal phone app or
deploy. Earlier phase summaries below retain their milestone boundaries.

Phase27 adds reviewed private reminders, bounded timezone schedules, durable
inbox delivery and explicit conversation opening. Dispatch and owner consent are
off by default; Android polls while foregrounded, with **no background push**.
That Phase27 milestone required **0018 / 65 tables** and supports versioned recovery-v4
alongside older artifacts. Read
[DURABLE-SCHEDULING-AND-REMINDERS](docs/DURABLE-SCHEDULING-AND-REMINDERS.md) for
setup, consent, time/DST behavior, recovery and validation limits. No live migration,
normal app installation, later phase or deployment is part of this source change.
Earlier phase summaries below retain their original implementation boundaries.

Phase26 adds reviewed Windows logon supervision, bounded recovery, protected-key
unattended backups and fixed local health metadata. Source and isolated rehearsals
do not install tasks, migrate the application database or change host policy.
Read [ALWAYS-ON-OPERATIONS](docs/ALWAYS-ON-OPERATIONS.md) for setup, restore,
rollback and remaining reboot/sleep/24-hour/large-data verification. After an
early failed attempt and receipt-sharing/startup corrections, the continuous
four-hour isolated rerun passed, including backup, restore and cleanup. This used
synthetic data and an explicit fake provider; installed-host and sustained native
inference verification remain separate. One API worker and the existing
authenticated contracts remain.

The Android presentation now follows **ADA Ambient Intelligence**: a dark-first
violet theme, state-driven presence, quieter chat and adaptive navigation. Existing
palette choices, authenticated APIs and encrypted recovery remain intact. See the
[redesign audit and guide](docs/ANDROID-UI-REDESIGN.md) and dated STATUS for actual
checks and remaining device verification. This source has not been installed on
the normal phone app or deployed.

Phase25 adds **opt-in conversational curiosity**: topic/depth/cadence controls,
optional questions after replies, a private later inbox and explicit conversation
opening/answers. No scheduler, notification or automatic factual memory is added.
That Phase25 milestone requires **0017 / 60 tables**; curiosity stays off until each owner
opts in. Read [CONVERSATIONAL-CURIOSITY](docs/CONVERSATIONAL-CURIOSITY.md) for usage,
retention, recovery and validation limits. The live database/service and normal
phone app were not migrated, installed or deployed during this implementation.

Phase24 adds owner-approved public web research with a verified isolated Docker
broker, exact outgoing-request previews, saved untrusted W citations and Android
approval/recovery controls. It is **disabled by default**, stays on schema0016
and has not been deployed. Read
[SECURE-WEB-RESEARCH](docs/SECURE-WEB-RESEARCH.md) for setup, privacy boundaries,
the Python documentation/Wikipedia pilot and remaining target checks.

Phase23 adds explicit calendar-window memory exploration, clearer proposal review
and an optional audited v5 context policy. New chats retain v4, semantic retrieval
stays disabled and schema head remains0016. Read
[ANSWER-QUALITY-AND-MEMORY-RELEVANCE](docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md)
for controls, measured native-model results and remaining limits. These source
changes have not been deployed to the previously installed private service.

Phase22 adds username/password sign-in on Android and HTTPS admin, rotating
revocable sessions and hidden-prompt local enrollment. Current source needs
**0016**; existing accounts remain password-disabled until an operator enrolls
them. Legacy CLI/device tokens and explicit admin grants are preserved. Read
[PASSWORD-LOGIN-AND-SESSIONS](docs/PASSWORD-LOGIN-AND-SESSIONS.md) before installation.
This implementation does not migrate the live database or deploy services.

For the separately authorized Windows/Tailscale setup, corrected dotenv values,
managed HTTPS, password enrollment and phone/iPad connection steps, use
[PRIVATE-SETUP-WINDOWS-TAILSCALE](docs/PRIVATE-SETUP-WINDOWS-TAILSCALE.md).
Its dated STATUS/WORKLOG follow-up distinguishes live setup from earlier tests.

Python/FastAPI on your Windows laptop, with PostgreSQL and a configurable Ollama
model. Accounts share model weights. Personality, history and memory remain
private to each authenticated user.

For the developer walkthrough, read
[HOW-TO-USE-ADA](docs/HOW-TO-USE-ADA.md), together with the current Phase27 guide above:
Android/USB and admin login, feature use, daily startup and troubleshooting.

For step-by-step Windows database access, queries, supported changes, migration,
encrypted recovery and an optional reset, read
[DATABASE-ADMINISTRATION-WINDOWS](docs/DATABASE-ADMINISTRATION-WINDOWS.md).
The separately authorized local startup on 2026-10-16 verified the configured
Docker database already at **0015** on **127.0.0.1:5433**, then started the API,
Ollama and built admin preview. No reset or existing credential change was needed;
the dated installation checks and remaining gates are in [STATUS](plans/STATUS.md).

Already running Phase 1? Start with [the upgrade guide](docs/UPGRADE-PHASE2.md).
It includes installation into your existing project and the prompt upgrade for
conversation `11b492c2-2667-44a3-bd9c-9a532f63c00f`.

Phase18 adds digest-only device credentials, explicit saved-content deletion and
encrypted PostgreSQL recovery. Read [SECURITY-AND-OPERATIONS](docs/SECURITY-AND-OPERATIONS.md)
and [VOICE-VALIDATION](docs/VOICE-VALIDATION.md). Enrollment and erasure processing
are opt-in; content is retained until explicit owner deletion. One worker remains
required. No application database migration or deployment is performed by a checkout.

Future development proposals, starting at Phase 20, are in
[the roadmap](plans/FUTURE-ROADMAP.md). Approved public research and opt-in chat/
inbox curiosity and consented scheduled inbox delivery are implemented locally.
Idle reports are implemented with summaries disabled; additional speech models
remain unselected pending the Phase29 device gate.

Phase 20's [release-readiness guide](docs/RELEASE-READINESS.md) covers the separate
encrypted schema-0005 recovery tool, current recovery policy, frozen quality
scorecard and a tested installation checklist. No live upgrade is implied.

Phase 21 adds Android named HTTPS server addresses and reviewed metadata import,
readiness checks before credential transmission, native TLS/DNS diagnostics and
Tailscale Serve/LAN proxy templates. Read
[PRIVATE-NETWORK-CONNECTIVITY](docs/PRIVATE-NETWORK-CONNECTIVITY.md) for Windows
setup, certificate/DNS responsibilities and remaining target checks. Source and
isolated rehearsals do not enroll a VPN, expose the server or deploy these routes.

## Implemented server and clients

- Scope-bound full-text and subject retrieval over explicitly saved claims.
- Current and dated lookups, with source hashes and exact quotes checked again at retrieval.
- A whole-prompt budget covering the baseline, history, memory and current input.
- Citation labels such as `[M1]`, mapped to the selected source snapshots.
- Durable request traces, preserved across retries, corrections and server restarts.
- Baseline v4 for new conversations, with existing v3 claim retrieval and explicit audited upgrades.
- Immutable text/Markdown document uploads, exact chunks and separate `[D1]` imported excerpt cards.
- Explicit scoped entities/aliases, ambiguous choices and audited reversible identity links.
- Optional bounded exact hybrid retrieval with digest-bound derived indexes and lexical fallback.
- A reproducible relevance/isolation benchmark and a Phase 1 upgrade installer.

Each claim requires one user evidence version in its authorized scope. Its quote
and hash come from the server. Model output cannot support user assertions. A
quote establishes provenance; it does not verify truth or semantic entailment.
The user explicitly supplies the subject/predicate/value annotation.

Chat retrieves relevant saved claims from its conversation's scope. It also uses
complete recent turns from that conversation. It does not extract or write claims.
External writes, PDF/OCR, affect learning, iOS and device
inference are deferred. Phase 03 adds Android/web foundations; Phase 04 adds an
Android authenticated chat client for these existing server APIs. Phase 05 adds
explicitly granted, audited admin metadata APIs. Phase 06 adds a read-only admin
dashboard with selectable palettes. Phase 07 adds Android explicit memory,
exact evidence, valid-time corrections and new static personality profiles.
Phase 08 adds bounded document ingestion/retrieval and Android upload/version/source
screens. Imported documents remain untrusted evidence, separate from user claims.
See [DOCUMENT-INGESTION.md](docs/DOCUMENT-INGESTION.md) for migration 0005,
capabilities, limits, explicit document opt-in and prompt compatibility.
Phase 09 adds owned entities/aliases, reviewed Android identity editing and frozen
canonical interpretations alongside exact original evidence. See
[ENTITIES-AND-ALIASES.md](docs/ENTITIES-AND-ALIASES.md) for migration **0006**,
resolution policy, limits and recovery. Installing this source requires head 0006;
the configured application database has not been upgraded by this implementation.

Phase 10 adds migration **0007**, a server-only embedding adapter, atomic scoped
index rebuild and exact semantic ranking alongside the original baseline.
**Embeddings stay disabled by default**: synthetic comparison/capacity checks do
not establish real-model benefit. See
[EMBEDDINGS-AND-HYBRID-RETRIEVAL.md](docs/EMBEDDINGS-AND-HYBRID-RETRIEVAL.md)
for bounds, fallback, activation/evaluation and installation. Current source
requires head 0016 after Phase22; the application database was not migrated by these phases.

Phase 11 adds migration **0008**, selected-source model suggestions, a private
Android review inbox and explicit accept/edit/reject receipts. Acceptance creates
new immutable user endorsement evidence and separate original support links;
unreviewed proposals never enter factual retrieval. Optional versioned
`user_reviewed` provenance preserves old origin enums and saved request cards.
Admin overview adds operational counts only. Automatic extraction/approval stays
off. See [MEMORY-PROPOSALS-AND-REVIEW.md](docs/MEMORY-PROPOSALS-AND-REVIEW.md)
for API, bounds, migration, recovery and real-versus-fixture evaluation limits.
The Phase 11 record observed application head0005 without migrating it; that is
historical evidence, not a fresh live-state check. Current source needs0016;
intended installation and remaining physical checks are separate. No deployment occurred.

## New Windows installation

Prerequisites: Python 3.12, Ollama, Docker Desktop with Linux containers (or native
PostgreSQL). From the extracted `ada-phase2` folder:

```powershell
.\scripts\setup.ps1
docker compose up -d --wait db
.\.venv\Scripts\python.exe -m alembic upgrade head
ollama pull qwen3.8:27b
.\.venv\Scripts\ada.exe doctor
.\.venv\Scripts\ada.exe create-user Gourishankar
.\scripts\start.ps1
```

Use an installed compatible model via `ADA_OLLAMA_MODEL` in `.env`. Actual quality,
GPU/CPU placement and speed need testing on your RTX 4090 Laptop GPU / i9-14900HX /
32 GB RAM machine. Start with one Uvicorn worker and one in-flight generation.
The setup script creates the virtual environment, installs the pinned dependencies
and generates a database password for a new `.env`.

For a new Docker install, `POSTGRES_PORT` controls the host port; use the same port
in `ADA_DATABASE_URL`. PostgreSQL inside the container stays on 5432. The upgrade
preserves your existing Compose file and port settings.

The API defaults to `127.0.0.1:8000`. Remote mobile clients need authenticated HTTPS
or an encrypted private network; PostgreSQL/Ollama remain private to the server.

## Chat

In another PowerShell window:

```powershell
$env:ADA_TOKEN = 'your-current-token'
.\.venv\Scripts\ada.exe chat --title 'ADA development'
```

The CLI prints conversation and scope IDs. Resume with `chat --conversation UUID`.
`/retry` reuses the last request ID. Completed retries return the saved answer.
`/sources` shows evidence actually cited in the last answer; `/trace` shows all
selected evidence and omission decisions for the last request. New conversations
use `ada-baseline-v4`. Existing conversations retain their old
baseline until `ada upgrade-prompt CONVERSATION_UUID` explicitly archives and
replaces it. The personality snapshot and events are preserved.
Baseline v1/v2 conversations keep retrieval disabled until explicitly upgraded.
Baseline v3 keeps claim retrieval; document retrieval needs the explicit v4 upgrade
and `use_documents=true` with memory enabled. Completed replay preserves its sources.

The prompt distinguishes ADA from the backend model and states this version's
capabilities. Model compliance needs a real-model check. Prompts do not enforce
permissions or write memory.

## Try explicit memory

Use the scope ID printed by chat, or create a private project:

```powershell
$scope = .\.venv\Scripts\ada.exe scopes create 'ADA development' | ConvertFrom-Json
$scopeId = $scope.id
.\.venv\Scripts\ada.exe chat --scope $scopeId --title 'Architecture discussion'
```

In another terminal, add a dated example decision:

```powershell
.\.venv\Scripts\ada.exe memory remember --scope $scopeId --subject ADA --predicate database --value SQLite --kind decision --text 'We chose SQLite for ADA.' --valid-from '2026-10-01T00:00:00Z'
```

Save its returned claim ID and correct it:

```powershell
$oldClaim = 'the-returned-claim-uuid'
.\.venv\Scripts\ada.exe memory correct $oldClaim --value PostgreSQL --text 'We now use PostgreSQL for ADA.' --effective-at '2026-10-08T00:00:00Z'
.\.venv\Scripts\ada.exe memory list --scope $scopeId
.\.venv\Scripts\ada.exe memory list --scope $scopeId --at '2026-10-05T00:00:00Z'
.\.venv\Scripts\ada.exe memory list --scope $scopeId --history
.\.venv\Scripts\ada.exe memory show $oldClaim
```

The historical query returns SQLite, the current query returns PostgreSQL, and
history retains both. These are examples, not automatically imported facts.

Ask the conversation in this scope, "Which database did we choose for ADA?".
Then try "Which database did we choose for ADA as of 2026-10-05?".
The model is instructed to cite supplied evidence with `[M1]` labels. Use `/trace`
to check what it received and `/sources` to inspect the cited quotes. Source cards
verify provenance; the model can still misinterpret a quote or omit a citation.

For a retrieval check without inference:

```powershell
.\.venv\Scripts\ada.exe memory search 'ADA database' --scope $scopeId
.\.venv\Scripts\ada.exe memory search 'ADA database' --scope $scopeId --at '2026-10-05T00:00:00Z'
```

`chat --at '2026-10-05T00:00:00Z'` uses a fixed memory time. `chat --no-memory`
disables fresh retrieval. Relative dates need clarification; natural date parsing
supports the exact phrase `as of YYYY-MM-DD` at UTC midnight. Use `--at` for a
precise instant. See [retrieval semantics](docs/PHASE2-RETRIEVAL.md).

`memory remember` can cite `--source-version UUID` from a chat event instead of
`--text`. Use `--quote 'an exact unique passage'` or `--start`/`--end` Unicode code
point offsets. IDs print before writes. Reuse `--claim-id` and `--source-id` with
identical input after connection loss. A used ID with different input returns 409.
A new ID for an identical claim also returns 409; replay with the original ID.
See [memory semantics and API examples](docs/PHASE1-MEMORY.md).

## API and verification

API explorer: http://127.0.0.1:8000/docs. Authorize with your bearer token.
`/v1/capabilities` reports implemented features. `contracts/openapi.json` is generated
from the actual routes, including evidence schemas and 64-bit timestamps.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

Default tests use migrated SQLite databases. PostgreSQL fixtures require a
disposable test database; see the upgrade guide. [VALIDATION.md](docs/VALIDATION.md)
records completed checks and remaining Windows/PostgreSQL/model checks.

Local administration: `ada create-user NAME`, `ada rotate-token NAME`, `ada doctor`,
`ada recover-stale --older-than-seconds 300`, `ada rebuild-search`,
`ada grant-admin ACCOUNT_UUID`, `ada revoke-admin ACCOUNT_UUID`. Tokens are random bearer secrets
stored as hashes. Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing
ownership, evidence or retry behavior.

## Phase 05 admin monitoring API

Migration **0004** adds empty explicit grants, bounded metadata audit and monitoring
indexes. Upgrade the intended database with `alembic upgrade head` during installation;
the API's readiness now requires 0004. No existing/new user is automatically granted.
The local operator uses account UUIDs to grant/revoke monitoring. Existing bearer
tokens remain valid; ordinary private APIs remain owner-only even for admins.

Six read-only `/v1/admin/` routes expose request metadata, bounded aggregates,
retrieval counts/budgets, current schema/provider health, real process admission
and audit metadata. They exclude private text/credentials, throttle polling and
audit access before returning results. Cached Ollama health uses only model-list
metadata; GPU/throughput remain unknown. See [operator and API documentation](docs/ADMIN-MONITORING.md)
for commands, schemas, retention, errors and validation. The Phase 06 dashboard
uses those six routes; see [admin web setup](apps/admin-web/README.md).

## Phase 03 client foundations

[Android](apps/android/README.md) and [admin web](apps/admin-web/README.md) contain
the pinned toolchains, Windows build commands, authenticated connection adapters,
test setup and explicit deferred screen maps. Both connect through ADA HTTP APIs.
The web token is held in memory. Android Phase 04 encrypts its verified account
credential and pending-message journal with an Android Keystore key.

[The client contract](contracts/README.md) documents typed responses, sanitized
errors, UTC milliseconds, evidence offsets, legacy traces and retry compatibility.
No database migration, prompt upgrade or server configuration change is required
for these foundations. Keep the API on loopback with one worker; use the web
development proxy or the documented emulator/USB connection for local development.
See [phase status](plans/STATUS.md) for checks actually run and remaining device
verification. Phase 06 adds authorized overview, request/detail, provider and audit
views at `/admin`, plus Oxford Blue (default), Dark Red and Olive Green Settings.
Web credentials remain in memory; current server grants are required on every read.

## Android chat and explicit memory (Phases 04/07)

The [Android app](apps/android/README.md) connects with an issued token, loads owned
styles/scopes/conversations, creates or resumes a conversation, sends complete
replies and displays the original request's source cards. It preserves an exact
encrypted request reservation before sending, checks that ID after interruption,
and offers explicit same-payload retry instead of silently sending a new turn.
Conversation prompt upgrades remain explicit. ADA Ambient in dark mode is the
fresh-install default. Oxford Blue, Dark Red and Olive Green remain available;
all four palettes support light/dark colors and optional system appearance.

Memory offers owned scopes, paginated current/dated/history views, exact source
versions, explicitly reviewed assertions and atomic corrections through the
existing API. Source and claim IDs are encrypted before submission; interrupted
note/claim writes resume identical input. Settings creates static profiles for
new conversations without rewriting an existing conversation's saved personality.

No backend migration, prompt upgrade or changed API contract is required to install
the client. Physical S24 FE/Android 16, release HTTPS and manual real-Ollama/source
checks remain target verification. No release signing, distribution or deployment
is performed by this phase.

## Phase 12 read-only tools

Migration **0009** adds bounded, explicitly approved calculator, owned memory
lookup and exact source lookup through separate `ada-agent-v1` runs. Android
shows exact intent, approval/denial, state, result trust and durable receipts;
encrypted journal v6 restores without automatic submission. Admin shows aggregate
run counts only. Normal chat, saved v3/v4 prompts and completed replay are unchanged.
No shell, external write, automatic approval or schedule is implemented. See
[TOOLS-AND-AGENT-LOOP.md](docs/TOOLS-AND-AGENT-LOOP.md) for routes, versions,
bounds, compatibility and verification. Phase12 recorded application head0005
without installation; this phase summary is historical, not a current DB query.
Current installation requirements and remaining target gates are in STATUS.

## Phase 13 episodes and consolidation

Migration **0010** adds bounded durable summary, pending-proposal and lexical
rebuild jobs, source-linked generated episodes and private navigation snapshots.
One in-process worker shares existing admission and uses leased, fenced, atomic
publication. Android adds explicit history/episode previews and encrypted v7
GET-only job recovery; admin adds private-input-free job metadata. Normal chat,
factual evidence, saved prompts and completed replay remain unchanged. See
[EPISODES-AND-CONSOLIDATION.md](docs/EPISODES-AND-CONSOLIDATION.md) for routes,
bounds and evaluation. Application installation and physical-phone verification
remain separate; no automatic approval, deletion or later phase is implemented.

## Phase 14 interaction preferences and session tone

Migration **0011** adds explicitly reviewed account/scope/profile/conversation
preferences, immutable receipts and opt-in bounded session tone. New conversations
freeze inherited defaults; changing an existing conversation requires an explicit
audited update for future replies. Dynamic tone can be disabled/reset, decays and
expires. Requests freeze the exact expression used, including provenance, so
failed/completed retries preserve their original messages and evidence.

Android Settings provides scoped preferences and encrypted v8 exact receipt
recovery (v1–v7 readable). The separate `ada-expression-v1` policy preserves saved
v3/v4 baselines, retrieval and permissions. No automatic mood classifier, learned
relationship preference or psychological score is implemented. See
[the expression policy](docs/INTERACTION-PREFERENCES-AND-AFFECT.md) and
[actual checks](plans/STATUS.md). Intended application installation, physical-phone,
HTTPS/accessibility and native-model wording checks remain separate. No deployment
or later phase was performed.

## Phase 15 reviewed interaction learning and continuity

Migration **0012** adds scope-specific opt-in/pause/reset, selected-source
interaction observations and revision-checked approve/edit/reject decisions.
Three independent interactions are the configurable default review gate; a single
exchange or weak guess cannot create an enduring rule. Explicit preferences win.
Optional account reuse carries only wording enums into other opted-in scopes.

Continuity selects bounded exact original excerpts through authorized episodes,
with uncertainty and request-frozen C source cards. Generated summaries remain
separate navigation. Android Settings provides evidence/review controls and
encrypted v9 GET-only receipt recovery; admin gets aggregate operation counts only.
Reset removes live learned state while preserving minimal audit and historical
request replay. See [the Phase 15 policy](docs/INTERACTION-LEARNING-AND-CONTINUITY.md)
and [actual checks and remaining targets](plans/STATUS.md). No automatic classifier,
factual promotion, later phase or deployment is included.

## Phase 16 streaming and Stop

Migration **0013** adds owned durable attempts/events, authenticated SSE, GET
checkpoints and an explicit same-attempt Stop receipt. Android **0.16.0-streaming**
shows provisional replies, detaches observers on navigation/backgrounding and
recovers the original request without resubmission. Completed history/citations
publish once; cancellation maps to the existing `failed/request_cancelled`
contract. Admin adds measured stream metadata only. Legacy API/CLI chat remains
available. See [the stream policy](docs/STREAMING-AND-CANCELLATION.md) for races,
capacity, limits, cursor expiry and retained private partial text. No application
migration, voice, later phase or deployment is included.


## Phase 17 reviewed Android voice

Android **0.17.0-voice** adds explicit on-device recording on supported Android
12+ devices, en-US by default, editable generated transcripts and required
approval before Send. Migration **0014** stores original ASR interpretation
separately from the approved event/source endorsement. No audio is uploaded or
retained by the app. The encrypted v10 journal reserves one exact voice request
before POST; restore reads and never automatically sends a reviewed draft.

Optional installed offline TTS voices read completed safe replies with voice,
speed and independent Stop playback controls. Text chat remains available without
microphone permission, an ASR engine or TTS. See [the voice policy](docs/VOICE-INTERFACE.md)
for engine/language requirements, client-reported provenance, retention and target
checks. The intended S24 FE/Android16 audio/quality/battery checks and application
installation remain pending. No later phase or deployment is included.
