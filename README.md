# ADA — Phase 2

Python/FastAPI on your Windows laptop, with PostgreSQL and a configurable Ollama
model. Accounts share model weights. Personality, history and memory remain
private to each authenticated user.

Already running Phase 1? Start with [the upgrade guide](docs/UPGRADE-PHASE2.md).
It includes installation into your existing project and the prompt upgrade for
conversation `11b492c2-2667-44a3-bd9c-9a532f63c00f`.

## Added in this phase

- Scope-bound full-text and subject retrieval over explicitly saved claims.
- Current and dated lookups, with source hashes and exact quotes checked again at retrieval.
- A whole-prompt budget covering the baseline, history, memory and current input.
- Citation labels such as `[M1]`, mapped to the selected source snapshots.
- Durable request traces, preserved across retries, corrections and server restarts.
- Baseline v3, plus an explicit, audited upgrade for existing conversations.
- A reproducible relevance/isolation benchmark and a Phase 1 upgrade installer.

Each claim requires one user evidence version in its authorized scope. Its quote
and hash come from the server. Model output cannot support user assertions. A
quote establishes provenance; it does not verify truth or semantic entailment.
The user explicitly supplies the subject/predicate/value annotation.

Chat retrieves relevant saved claims from its conversation's scope. It also uses
complete recent turns from that conversation. It does not extract or write claims.
Tools, document ingestion,
consolidation, affect learning, Android/iOS apps and device inference are deferred.

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
use `ada-baseline-v3`. Existing conversations retain their old
baseline until `ada upgrade-prompt CONVERSATION_UUID` explicitly archives and
replaces it. The personality snapshot and events are preserved.
Baseline v1/v2 conversations keep retrieval disabled until explicitly upgraded.

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
`ada recover-stale --older-than-seconds 300`, `ada rebuild-search`. Tokens are random bearer secrets
stored as hashes. Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing
ownership, evidence or retry behavior.
