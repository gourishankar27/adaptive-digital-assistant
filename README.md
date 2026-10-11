# ADA
Python/FastAPI on your Windows laptop, with PostgreSQL and a configurable Ollama
model. Accounts share model weights. Personality, history and memory remain
private to each authenticated user.

Already running Phase 1? Start with [the upgrade guide](docs/UPGRADE-PHASE2.md).
It includes installation into your existing project and the prompt upgrade for
conversation `11b492c2-2667-44a3-bd9c-9a532f63c00f`.

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
requires head 0010 after Phase 13; the application database was not migrated by these phases.

Phase 11 adds migration **0008**, selected-source model suggestions, a private
Android review inbox and explicit accept/edit/reject receipts. Acceptance creates
new immutable user endorsement evidence and separate original support links;
unreviewed proposals never enter factual retrieval. Optional versioned
`user_reviewed` provenance preserves old origin enums and saved request cards.
Admin overview adds operational counts only. Automatic extraction/approval stays
off. See [MEMORY-PROPOSALS-AND-REVIEW.md](docs/MEMORY-PROPOSALS-AND-REVIEW.md)
for API, bounds, migration, recovery and real-versus-fixture evaluation limits.
The configured application remains at observed 0005; installation of head 0008
and physical S24 FE/Android 16 checks are pending. No deployment occurred.

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
Conversation prompt upgrades remain explicit. Oxford Blue is the default palette;
Dark Red and Olive Green are available in Settings, each with light/dark colors.

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
bounds, compatibility and verification. Application head 0005 remains unchanged;
explicit installation of head 0009 and target-phone verification are pending.

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
