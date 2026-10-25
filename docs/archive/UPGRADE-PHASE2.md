> Historical reference. For current setup use [HOW-TO-USE-ADA](../HOW-TO-USE-ADA.md).

# Upgrade the existing Windows Phase 1 project

This bundle installs source version 0.2.0 and adds migration 0003. It preserves
your database, users, scopes, events, claims, source IDs, personality snapshots and
completed request replay. It keeps `.env`, Compose/port settings and pinned
dependencies. It does not rewrite conversation prompts automatically.

## Apply the source and database upgrade

Stop the API with Ctrl+C. Make a PostgreSQL backup using your normal backup
procedure before a schema upgrade. Keep PostgreSQL and Ollama running. Extract
`ADA-Phase2.zip` separately from your existing project, for example into the
adjacent folder `ada-phase2`.

From your existing project directory:

```powershell
Set-Location 'G:\Project\AgenticAIProject\Ada_Adaptive_Digital_Assistant\adaptive-digital-assistant'
..\ada-phase2\scripts\upgrade.ps1 -ProjectPath . -CheckOnly
..\ada-phase2\scripts\upgrade.ps1 -ProjectPath .
.\.venv\Scripts\ada.exe doctor
```

If you extracted elsewhere, change the path to the bundle's `scripts\upgrade.ps1`.
The installer pins both original migration files, checks every source/destination
hash before copying, accepts Windows CRLF and rejects unrecognized local edits.
It backs up changed files under `upgrade_backups\phase2-TIMESTAMP`. Already
installed files are accepted on rerun. If preflight reports a local edit, merge it
against the bundle deliberately rather than overwriting your changes.

The wrapper refreshes the editable package without upgrading dependencies, runs
`alembic upgrade head`, and runs `alembic check`. Migration 0003 backfills the search
projection from existing claims and creates the native full-text index and trace
table. Normal online upgrades use the frozen projection normalizer. If executing
an exported offline PostgreSQL migration instead, run `ada rebuild-search` afterward
to replace locale-dependent SQL normalization with the application's projection.
Downgrading 0003 discards the derived index and all retrieval traces, so it is not
the supported path for preserving Phase 2 citation history.

## Run the local checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
.\scripts\test-postgres.ps1
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
.\scripts\start.ps1
```

The PostgreSQL wrapper creates/reuses `ada_phase2_test`, separate from production,
then tests in disposable schemas. It needs CREATEDB for initial setup; alternatively
create that test database manually and set `ADA_TEST_DATABASE_URL` to its full URL
before `pytest`. Do not set the test URL to production. This environment ran SQLite
and compiled PostgreSQL SQL; actual PostgreSQL and PowerShell execution need these
local checks. No real Ollama model was called during bundle verification.

## Enable retrieval in your existing conversation

After starting the API, use another PowerShell window in the existing project.
Set `ADA_TOKEN` to your current locally issued token without sharing its value.

```powershell
.\.venv\Scripts\ada.exe upgrade-prompt '11b492c2-2667-44a3-bd9c-9a532f63c00f'
.\.venv\Scripts\ada.exe chat --conversation '11b492c2-2667-44a3-bd9c-9a532f63c00f'
```

The first command explicitly upgrades v2 to `ada-baseline-v3`. It archives old/new
prompts, retains personality/history, and increments the revision. Repeating it is
a no-op. A new v3 chat request will select authorized memories; completed older
requests retain their saved replies. Failed retries from before the prompt upgrade
are rejected because their context revision has changed.

Copy the scope ID printed by chat. If it has no claims yet, save one explicitly:

```powershell
$scopeId = 'the-scope-uuid-printed-by-chat'
.\.venv\Scripts\ada.exe memory remember --scope $scopeId --subject user --predicate preferred_language --value Python --kind preference --text 'I prefer Python.'
.\.venv\Scripts\ada.exe memory search 'What programming language do I prefer?' --scope $scopeId
```

Then ask that question in chat. Inspect `/trace` for the chosen claim and exact
quote, and `/sources` for cards cited by the answer. A source card validates label
mapping; evaluate the model's wording against the quote. `memory trace REQUEST_UUID`
can inspect the same snapshot from another terminal.

If you saved claims in a different private project, resume or create a conversation
in that scope; scopes are deliberately separate. Chat itself does not save new
claims. Try a correction and an exact `as of YYYY-MM-DD` question to check historical
behavior. See PHASE2-RETRIEVAL.md for time/budget rules and PHASE1-MEMORY.md for writes.
