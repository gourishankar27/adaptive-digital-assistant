> Historical reference. For current setup use [HOW-TO-USE-ADA](../HOW-TO-USE-ADA.md).

# Archived: upgrade your existing Phase 0 project

This guide belongs to the original Phase 1 bundle. The current Phase 2 installer
targets an already upgraded Phase 1 project. Use [UPGRADE-PHASE2.md](UPGRADE-PHASE2.md)
for the current upgrade.

Extract the ZIP's `ada-phase1` folder separately from your repository. Stop the
running API with Ctrl+C; leave PostgreSQL running. The updater preserves `.env`,
`compose.yaml`, the virtual environment, Git metadata, original migration 0001,
accounts, conversations and database volumes.

From your existing project directory, if the bundle is extracted beside it:

```powershell
$bundle = '..\ada-phase1'
& "$bundle\scripts\upgrade.ps1" -ProjectPath $PWD.Path
.\scripts\start.ps1
```

Use a full path for `$bundle` if you extracted it elsewhere. The installer checks
all destinations before copying, accepts CRLF line endings, backs up replaced
files under `upgrade_backups/phase1-TIMESTAMP`, refreshes the editable package,
applies migration 0002, and runs `alembic check`. Add `-CheckOnly` for a copy preflight.

Unexpected local source edits stop the copy before overwriting any file. Merge
the listed files with their bundle versions, then rerun. Files already matching
Phase 1 are accepted. Re-running the installer is safe for matching files and an
already migrated database. The manifest is an integrity check, not a package signature.

If script execution is disabled, run these commands directly instead:

```powershell
.\.venv\Scripts\python.exe "$bundle\scripts\apply_upgrade.py" --project $PWD.Path
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m uvicorn ada.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Check each command succeeds before continuing. There are no new runtime dependencies.
The package version becomes 0.1.0; the database schema version becomes 0002.

## Update the prompt for your existing conversation

The migration preserves old prompt snapshots. With the API running and your
current token in `ADA_TOKEN`, explicitly upgrade your conversation:

```powershell
.\.venv\Scripts\ada.exe upgrade-prompt '11b492c2-2667-44a3-bd9c-9a532f63c00f'
.\.venv\Scripts\ada.exe chat --conversation '11b492c2-2667-44a3-bd9c-9a532f63c00f'
```

This archives the old baseline in `conversation_prompt_changes` and retains your
personality snapshot and events. It rejects changes during inference. Failed
requests made before an upgrade must be submitted afresh; successful old requests
still replay their saved answer.

The new prompt separates the ADA application from its replaceable language model
and states this release's capabilities. Check your real model's replies to “Who
are you?” and “Can we build tools for you?” Automated tests check the supplied
context, not whether your installed model follows every instruction.

The reply ending at “I can write” may have hit the output limit. For longer replies,
set `ADA_OUTPUT_TOKENS=1024` in your existing `.env` and restart. That fits the default
8192 context / 6000 prompt-byte settings. Streaming remains deferred.

Rotate the token you posted before reusing it:

```powershell
.\.venv\Scripts\ada.exe rotate-token Gourishankar
$env:ADA_TOKEN = 'the-newly-issued-token'
```

Your conversation ownership stays the same. The old token stops authorizing new requests.

## Verify on your laptop

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
```

For PostgreSQL verification, run:

```powershell
.\scripts\test-postgres.ps1
```

This uses your current database connection settings to create/reuse the separate
`ada_phase1_test` database, then runs the suite with that test URL. Credentials are
passed to the test process without printing them. Each test creates/drops a random
schema. The test database stays available for later phases.

For manual setup instead, create the test database with:

```powershell
docker compose exec -T db createdb -U ada ada_phase1_test
```

Set `ADA_TEST_DATABASE_URL` with the password/host port from your current database
URL and the database name changed to `ada_phase1_test`. URL-encode special password
characters as in the production URL:

```powershell
$env:ADA_TEST_DATABASE_URL = 'postgresql+psycopg://ada:YOUR_PASSWORD@127.0.0.1:YOUR_HOST_PORT/ada_phase1_test'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:ADA_TEST_DATABASE_URL
```

Every PostgreSQL fixture creates/drops its own random schema inside this database.
The SQLite copy of the row-lock race test intentionally skips; the PostgreSQL copy
must run. Keep the test database for future phases or explicitly drop it later.

Use the README memory example to verify a fact, its correction and a historical
query. `ada memory` writes structured memory; chat will use it in Phase 2.
