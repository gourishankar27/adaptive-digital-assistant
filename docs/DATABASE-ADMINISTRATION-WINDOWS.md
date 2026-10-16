# ADA database administration on Windows

This is the step-by-step operator guide for accessing, checking, upgrading and,
when deliberately selected, resetting ADA's PostgreSQL database on your laptop.
Run PowerShell commands in **Windows PowerShell or PowerShell 7**. Run SQL and
backslash commands only after opening the **psql** database terminal.

## 1. Know which service you are connecting to

The following installation was checked on **2026-10-16, America/Phoenix**:

| Item | This laptop's current installation |
|---|---|
| Project folder | `G:\Project\AgenticAIProject\Ada_Adaptive_Digital_Assistant\adaptive-digital-assistant` |
| Database engine | PostgreSQL **17.11**, Docker Compose service **db** |
| Windows database address | **127.0.0.1:5433** |
| Database name / database role | **ada / ada** |
| PostgreSQL port inside Docker | **5432** |
| Installed migration head | **0015**, 54 public tables |
| ADA API | **http://127.0.0.1:8000** |
| Built admin dashboard | **http://127.0.0.1:5173/admin/** |
| Ollama | **http://127.0.0.1:11434**, model `qwen3.8:27b` |
| Encrypted backup folder | `%LOCALAPPDATA%/ADA/backups` |

Another native PostgreSQL installation listens on Windows port **5432**. It is
separate from this project's Docker database. Use **5433** from Windows for ADA;
use **5432** only from inside ADA's Docker container. Recheck these values if you
change `.env`, Compose or computers.

Three credentials serve different purposes:

- **Database role/password:** trusted operator access to PostgreSQL; configured
  privately in `.env` as `POSTGRES_PASSWORD` and in `ADA_DATABASE_URL`.
- **ADA account/bearer token:** signing into Android, API clients and admin web.
  The account `Gourishankar` currently has an explicit enabled monitoring grant.
- **Backup passphrase:** separately chosen encryption secret, at least 16
  characters. Save it in a password manager; losing it prevents decryption.

An ADA bearer token is not a database password. Database role `ada` is not the
ADA account `Gourishankar`. The application still uses bearer login; password
login is a future feature. Keep the database password on the server laptop.

## 2. Open the project and start the database

1. Open **Docker Desktop** from the Start menu. Wait until its engine is running
   and make sure it is using **Linux containers**.
2. Open PowerShell and enter the project folder:

   ```powershell
   Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
   ```

3. Check Docker, then start this project's database:

   ```powershell
   docker version
   docker compose up -d --wait db
   if ($LASTEXITCODE -ne 0) { throw 'Database startup failed.' }
   docker compose ps db
   docker compose port db 5432
   docker compose exec -T db pg_isready -U ada -d ada
   ```

   Expect a healthy `db` container, host port `127.0.0.1:5433`, and “accepting
   connections.” `up` reuses the existing persistent volume; it does not initialize
   a new empty database each time.

4. Confirm the Python environment exists:

   ```powershell
   Test-Path .venv/Scripts/python.exe
   ```

   If this is a fresh clone and the result is `False`, follow
   [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md) for Python 3.12, the pinned setup script and
   private `.env` creation. Do not replace an existing `.env` with the example.

## 3. Open the database terminal: the simplest route

From the project folder in PowerShell:

```powershell
docker compose exec db psql -X -n -v ON_ERROR_STOP=1 -U ada -d ada
```

This uses the PostgreSQL client already inside the correct container. It avoids
installing another Windows database server. `-X` ignores personal psql startup
files; `-n` disables psql's interactive command history. Local container access is
trusted operator access; restrict access to your Windows account and Docker.

The prompt now resembles `ada=#`. Enter these **inside psql**, one at a time:

```sql
\conninfo
SELECT current_database(), current_user;
SHOW server_version;
SELECT version_num FROM public.alembic_version;
\dt public.*
\d public.users
\d public.requests
```

Expect database `ada`, role `ada`, PostgreSQL 17, and migration `0015`. `\dt`
lists tables; `\d` describes columns/constraints. Finish SQL with a semicolon.
Backslash commands do not need one. Exit to PowerShell with:

```text
\q
```

If you see `ada-#`, psql is waiting for the rest of an unfinished SQL statement.
Press **Ctrl+C** to cancel it, then enter the complete statement again. If an
explicit transaction has failed and the prompt contains `!`, enter `ROLLBACK;`.
See PostgreSQL's [psql reference](https://www.postgresql.org/docs/17/app-psql.html)
and Docker's [Compose exec reference](https://docs.docker.com/reference/cli/docker/compose/exec/).

### Access from a Windows PostgreSQL client

This laptop also has a Windows psql executable. It can be used for interactive
queries against the Docker server:

```powershell
& 'C:/Program Files/PostgreSQL/18/bin/psql.exe' -X -n -h 127.0.0.1 -p 5433 -U ada -d ada -W
```

At the hidden password prompt, enter the **database password**, read privately
from your local `.env`. Do not put it in the command or a screenshot. A Windows
18 query client does not change the server to version 18. ADA's **backup tool**
has a stricter matching-major requirement, explained in section 7.

### Optional graphical access with pgAdmin

If you already use pgAdmin, register a server named **ADA local Docker**. Under
Connection enter host `127.0.0.1`, port `5433`, maintenance database `ada`, username
`ada`, and the database password privately. Avoid saving the password on a shared
Windows account. Open **Databases → ada → Schemas → public → Tables** or the Query
Tool. Use the explicit-column queries below rather than opening every private row.
The [PostgreSQL Windows download page](https://www.postgresql.org/download/windows/)
links to the installer including pgAdmin and to a separate binary archive.

## 4. Inspect operational data without dumping private content

Inside psql or pgAdmin Query Tool:

```sql
BEGIN READ ONLY;

SELECT u.id, u.name, COALESCE(a.enabled, false) AS admin_monitoring
FROM public.users u
LEFT JOIN public.admin_grants a ON a.user_id = u.id
ORDER BY u.name;

SELECT status, count(*) AS requests
FROM public.requests
GROUP BY status
ORDER BY status;

SELECT count(*) AS conversations FROM public.conversations;
SELECT count(*) AS saved_claims FROM public.claims;
SELECT count(*) AS documents FROM public.document_uploads;

COMMIT;
```

These queries report account/operational metadata. `users.token_hash` is a secret
digest, not a recoverable token. Do not dump it. Requests, events, source versions,
documents and snapshots can contain private content; avoid `SELECT *`, CSV exports
or attaching whole query results to support messages.

To run one metadata query directly from PowerShell without opening a terminal:

```powershell
docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ada -d ada -c 'SELECT version_num FROM public.alembic_version;'
```

`-T` disables the interactive Docker terminal for scripted input/output. It does
not change the database or user.

## 5. Make supported account and application changes

For normal application data, use Android or authenticated ADA APIs. For account
administration, use the existing local CLI. These routes preserve the application's
ownership checks, evidence hashes, receipt/replay rules and audit behavior.

### Grant or revoke admin monitoring

1. Run the account query in section 4 and copy the **exact account UUID**.
2. Exit psql. In PowerShell, set the UUID and use the local operator command:

   ```powershell
   $adaAccountId = Read-Host 'Exact account UUID from the users query'
   ./.venv/Scripts/ada.exe grant-admin $adaAccountId
   if ($LASTEXITCODE -ne 0) { throw 'Admin grant failed.' }
   ```

3. Sign out and sign back into admin web with that account's current bearer token.
   A name alone never grants permission. This laptop's existing `Gourishankar`
   grant was verified enabled; it does not need granting again.
4. To remove monitoring access later:

   ```powershell
   ./.venv/Scripts/ada.exe revoke-admin $adaAccountId
   ```

### Create an account or recover a lost legacy token

Use a private local PowerShell window with terminal transcription/recording off:

```powershell
./.venv/Scripts/ada.exe create-user NewDeveloper
```

Save the once-issued token directly into your password manager. Do not paste the
output into this guide, a plan, a log or a support chat. The database cannot reveal
the original token. If an existing account has lost its legacy token, deliberately
rotate it using its exact, case-sensitive stored name:

```powershell
./.venv/Scripts/ada.exe rotate-token Gourishankar
```

Rotation invalidates the old **legacy** bearer token. Reconnect clients with the
new one. Separately enrolled device credentials have their own revocation flow;
this command does not revoke those. No existing token was rotated for the local
startup recorded in this guide.

### Change memory, documents or saved content

Use Android Memory, Sources, Documents and Settings, or the authenticated routes
in **http://127.0.0.1:8000/docs**. Correct claims through the correction API; do not
edit source text/hashes, old responses, snapshots, trust labels or ownership IDs
with SQL. Saved-content deletion uses preview/confirmation and requires the
explicitly enabled deletion worker; it retains the account and security receipts.
See [SECURITY-AND-OPERATIONS](SECURITY-AND-OPERATIONS.md) for that policy.

## 6. Apply required schema changes with Alembic

Schema changes are migrations in `migrations/versions`, separate from ordinary
data changes. The installed source currently requires **0015**. Preserve released
migrations and add new ones for future schema work.

1. Read the selected release notes. Make an encrypted recovery point and rehearse
   its isolated restore as in section 7 **before an actual migration or data edit**.
2. Stop ADA's API so clients/workers cannot write during the maintenance window.
   In its foreground PowerShell window, press **Ctrl+C**. Section 9 covers the
   background process started during this installation.
3. From the project root, run each command and stop if it fails:

   ```powershell
   ./.venv/Scripts/python.exe -m alembic current
   if ($LASTEXITCODE -ne 0) { throw 'Cannot read installed revision.' }
   ./.venv/Scripts/python.exe -m alembic heads
   if ($LASTEXITCODE -ne 0) { throw 'Cannot read source revisions.' }
   ./.venv/Scripts/python.exe -m alembic upgrade head
   if ($LASTEXITCODE -ne 0) { throw 'Migration failed; do not start ADA.' }
   ./.venv/Scripts/python.exe -m alembic check
   if ($LASTEXITCODE -ne 0) { throw 'Schema differs from source; investigate before startup.' }
   ```

4. Expect `0015 (head)` and `No new upgrade operations detected.` for this source.
   `upgrade head` is a no-op when already current. `alembic check` compares schema
   to model metadata; it is not a private-data integrity or model-quality test.
5. Restart one API worker with `./scripts/start.ps1`, then check readiness as in
   section 9. Keep old conversation prompts unchanged unless you explicitly use
   the supported prompt-upgrade command.

Do not fix a mismatch by stamping a revision, changing `alembic_version`, calling
`create_all()` or editing an old migration. A failed upgrade needs diagnosis or
isolated recovery. Downgrades can be lossy/refused and are not a general undo.

## 7. Create encrypted backups and rehearse recovery

### Prepare matching Windows tools once

ADA's recovery preflight requires **pg_dump and pg_restore with the same major
version as the server**. This Docker server is 17. The already installed Windows
18 tools were used for disposable Phase20 tests; they are not the matching tools
for this Docker installation.

1. Confirm the server and container tools:

   ```powershell
   docker compose exec -T db psql -X -U ada -d ada -Atc 'SHOW server_version;'
   docker compose exec -T db pg_dump --version
   ```

2. Obtain Windows x64 **PostgreSQL 17** tools using the installer or binary archive
   linked by the [official Windows download page](https://www.postgresql.org/download/windows/).
   With an archive, keep its complete extracted directory and dependent DLLs.
   You need client executables, not another running database service. Do not run
   `initdb` or replace Docker's data directory. This download was not performed
   during the local startup documented here.
3. Set `$adaPgBin` to the actual folder containing the Windows executables, then
   verify both. The following path is an example to replace if different:

   ```powershell
   $adaPgBin = 'C:/Program Files/PostgreSQL/17/bin'
   & (Join-Path $adaPgBin 'pg_dump.exe') --version
   & (Join-Path $adaPgBin 'pg_restore.exe') --version
   ```

   Both must report **17.x**. The Linux programs inside Docker cannot be passed
   as a Windows `--pg-bin` directory. Never bypass the application's version check.
   This same-major rule is ADA's conservative recovery policy; PostgreSQL's more
   general dump compatibility is described in its
   [pg_dump reference](https://www.postgresql.org/docs/17/app-pgdump.html).

### Back up current schema0015

From the project root, after setting the matching `$adaPgBin`:

```powershell
$adaBackups = Join-Path $env:LOCALAPPDATA 'ADA/backups'
./.venv/Scripts/python.exe -m ada.operations --pg-bin $adaPgBin backup --destination $adaBackups
if ($LASTEXITCODE -ne 0) { throw 'Backup failed; do not proceed with maintenance.' }
```

Enter your password-manager passphrase at the hidden prompt. Keep the returned
encrypted artifact path. The receipt reports metadata, not the key. Default
destination is the selected local backup folder; there is no automatic scheduled
backup or age-based pruning. This is a local recovery copy, not protection against
loss of the entire laptop. It excludes `.env`, TLS keys, model files and client
caches; preserve configuration/key material separately in protected storage.

### Rehearse an isolated restore

1. Obtain a **fresh authoritative deletion ledger after the backup**, especially
   if content has since been erased. Use the same encryption passphrase for the
   artifact and ledger used in this restore:

   ```powershell
   $adaLedger = Join-Path $adaBackups ('deletion-ledger-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.adaenc')
   ./.venv/Scripts/python.exe -m ada.operations --pg-bin $adaPgBin deletion-ledger --output $adaLedger
   if ($LASTEXITCODE -ne 0) { throw 'Ledger export failed.' }
   ```

2. Select the artifact path from the backup receipt and a **new, unused** isolated
   database name. The supported prefix is `ada_restore_`:

   ```powershell
   $adaArtifact = Read-Host 'Full encrypted artifact path from backup receipt'
   $adaRestoreName = 'ada_restore_manual_' + (Get-Date -Format 'yyyyMMddHHmmss')
   ./.venv/Scripts/python.exe -m ada.operations --pg-bin $adaPgBin restore --database $adaRestoreName --artifact $adaArtifact --deletion-ledger $adaLedger
   if ($LASTEXITCODE -ne 0) { throw 'Restore failed; keep the source installation unchanged.' }
   ```

3. Review the receipt, schema and reconciliation results. The tool checks inventory,
   row hashes and later deletions, and invalidates restored credentials. A restore
   does not start ADA, change `.env`, overwrite `ada`, or automatically issue new
   access. Keep it isolated until access/reconciliation are deliberately resolved.
   Do not route existing clients to a restored copy with old credentials.

For an actual **0005** installation, use `ada.legacy_recovery`, not this0015-only
command. [RELEASE-READINESS](RELEASE-READINESS.md) describes that distinct format,
quarantine and the additional erasure-reconciliation boundary. Unknown heads need
their own supported recovery path. Plain `pg_dump > file` is not an ADA encrypted
artifact, and raw restore does not enforce ADA's credential/erasure policy.

No new live backup was created during the startup recorded here: the database
was already current, the upgrade was a no-op, and matching Windows17 recovery
tools are not yet installed. Existing disposable recovery drills are recorded
separately in STATUS/WORKLOG; they are not backups of this live database.

## 8. Practice SQL changes, then choose the correct real change path

To learn transactions without changing saved application data, open psql and run:

```sql
BEGIN;
CREATE TEMP TABLE ada_operator_practice (id integer PRIMARY KEY, note text);
INSERT INTO ada_operator_practice VALUES (1, 'synthetic practice row');
SELECT id, note FROM ada_operator_practice WHERE id = 1;
UPDATE ada_operator_practice SET note = 'changed practice row' WHERE id = 1;
SELECT id, note FROM ada_operator_practice WHERE id = 1;
ROLLBACK;
```

This rolls back both the temporary table and its rows. It does not edit any ADA
table. For a deliberate real operator edit: back up/rehearse first, stop writers,
verify the exact database and target UUID, use `BEGIN`, inspect the selected rows,
apply an exact `WHERE` condition, check `RETURNING` and affected row count, then
choose `COMMIT` or `ROLLBACK`. If the result is unexpected, roll back before leaving
the terminal. After commit, rollback is no longer available; recovery is separate.
See PostgreSQL's [transaction tutorial](https://www.postgresql.org/docs/17/tutorial-transactions.html).

Use a new migration for a schema change and the supported CLI/API for application
changes. Do not disable foreign keys/triggers, mass-update ownership, rewrite
source evidence or truncate tables to bypass an error.

### Optional full reset of only the disposable ADA application database

**This was not needed or performed during this installation.** A reset deletes
all ADA accounts, grants and saved content in `ada`. Tokens cease working and
clients need fresh setup. It also removes the security/deletion history; it is
not the saved-content retention API. Leave other databases and Docker volumes alone.

Only use this branch when you deliberately choose to discard this local database:

1. Stop ADA's API and admin preview as described in section 9. Disconnect clients.
   If preserving anything, complete section 7 first. Confirm `docker compose ps db`
   belongs to this project, then check the exact target:

   ```powershell
   docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ada -d postgres -c "SELECT datname FROM pg_database WHERE datname = 'ada';"
   if ($LASTEXITCODE -ne 0) { throw 'Target inspection failed.' }
   ```

2. In PowerShell, type the acknowledgement when deliberately executing this branch:

   ```powershell
   $adaResetAck = Read-Host 'Type RESET ADA LOCAL DATABASE to delete all data in ada'
   if ($adaResetAck -cne 'RESET ADA LOCAL DATABASE') { throw 'Reset cancelled.' }
   docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ada -d postgres -c 'DROP DATABASE "ada" WITH (FORCE);'
   if ($LASTEXITCODE -ne 0) { throw 'Drop failed; stop and inspect.' }
   docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ada -d postgres -c 'CREATE DATABASE "ada" OWNER "ada";'
   if ($LASTEXITCODE -ne 0) { throw 'Create failed; do not start ADA.' }
   ./.venv/Scripts/python.exe -m alembic upgrade head
   if ($LASTEXITCODE -ne 0) { throw 'Initialization failed.' }
   ./.venv/Scripts/python.exe -m alembic check
   if ($LASTEXITCODE -ne 0) { throw 'New schema check failed.' }
   ```

   These are separate commands because database drop/create cannot run inside a
   normal transaction. There is no rollback after dropping `ada`. The named
   `ada_phase2_test` database and unrelated native PostgreSQL are not reset.

3. Create a fresh ADA account with `ada.exe create-user Gourishankar` in a private
   terminal, securely save its new bearer token, and explicitly grant admin using
   the **new UUID** if desired. Start the services; sign out/clear the old server's
   client state and reconnect. Reusing the old bearer token cannot restore access.

Do not use `docker compose down -v` as routine maintenance: it removes this
Compose project's persistent volumes, a broader action than resetting `ada`.
Never delete files from a live PostgreSQL data directory or point PostgreSQL18
at the PostgreSQL17 volume.

## 9. Start, verify and stop the local application

The local installation started during this work has the API, Ollama and a built
admin preview running on loopback. They are ordinary processes, **not installed
Windows services or scheduled tasks**. They need restarting after logout/reboot;
the laptop must remain awake for ADA to respond.

For subsequent manual startup, use separate PowerShell windows:

1. Start Docker/database as in section 2.
2. Start the installed Ollama application, or, if it is not already running:

   ```powershell
   $env:OLLAMA_HOST = '127.0.0.1:11434'
   ollama serve
   ```

   Do not launch a second instance if that port is already occupied by Ollama.
   The configured model is already installed; no download is required here.
3. From the project root in another window:

   ```powershell
   ./.venv/Scripts/ada.exe doctor
   ./scripts/start.ps1
   ```

   Keep one worker. `doctor` checks schema and model presence; readiness alone
   does not prove inference works.
4. In another window, serve the built admin application:

   ```powershell
   Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/apps/admin-web'
   npm run build
   if ($LASTEXITCODE -ne 0) { throw 'Admin build failed.' }
   $env:ADA_API_TARGET = 'http://127.0.0.1:8000'
   npm run preview -- --port 5173 --strictPort
   ```

   Open **http://127.0.0.1:5173/admin/**. Browser server origin is
   **http://127.0.0.1:5173**, without `/admin/`. Enter your existing bearer token.
   Admin web is monitoring; Android is the chat client. Do not enter the
   PostgreSQL address, Ollama address or database password into either client.
5. From another PowerShell window check:

   ```powershell
   Invoke-RestMethod 'http://127.0.0.1:8000/health/live'
   Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
   ```

   Expect `ok`, then `ready` with schema `0015`. Private routes should reject
   missing credentials. `127.0.0.1` is this laptop; on a phone it means the phone.
   For USB debug access use the existing Android instructions in HOW-TO-USE-ADA.
   Wi-Fi/Tailscale trusted HTTPS setup remains a separately planned feature.

For foreground servers, press **Ctrl+C** in their windows to stop them. To stop a
background API or preview from this installation, first inspect the listener and
the executable. Repeat for port5173 when stopping the admin preview:

```powershell
$adaPort = 8000
$adaListener = Get-NetTCPConnection -State Listen -LocalAddress 127.0.0.1 -LocalPort $adaPort -ErrorAction SilentlyContinue
$adaProcessIds = @($adaListener.OwningProcess | Sort-Object -Unique)
if ($adaProcessIds.Count -gt 0) {
    Get-Process -Id $adaProcessIds | Select-Object Id, ProcessName, Path
}
```

After verifying those are this installation's ADA Python process (or Node for
5173), stop only the inspected process IDs:

```powershell
if ($adaProcessIds.Count -gt 0) { Stop-Process -Id $adaProcessIds }
```

Do not kill every Python, Node or PostgreSQL process. For planned maintenance,
let active generation finish first. If an abrupt stop leaves requests running,
use the documented stale-request recovery after its safe timeout, preserving the
original request IDs. Background runtime logs are under
`%LOCALAPPDATA%/ADA/logs`; inspect privately and redact before sharing. Access
logging is disabled for the API. To stop only the Docker database after stopping
the API, run `docker compose stop db`; its data remains on the persistent volume.

## 10. Troubleshooting

| Symptom | Check and action |
|---|---|
| Docker cannot connect to its engine | Open Docker Desktop, wait for engine readiness and confirm Linux containers. Run `docker version` again. |
| Compose says it cannot find a configuration file | Return to the repository root containing `compose.yaml`. |
| Port5432 returns different data or rejects the role | This laptop's ADA container uses host **5433**. Do not change/stop the unrelated native service to compensate. |
| `connection refused` on5433 | Check `docker compose ps db`, `docker compose port db 5432` and `pg_isready`; confirm `.env` uses the same host port. |
| Password authentication failed | Use the database password privately. Changing `POSTGRES_PASSWORD` in `.env` does not change an already initialized volume's role password. Coordinate a deliberate password change with `ADA_DATABASE_URL`; do not reinitialize the volume as a first fix. |
| `psql` is not recognized | Use `docker compose exec db psql ...` or the explicit Windows executable path. |
| `relation ... does not exist` | Check database/schema/revision; exit psql and follow Alembic upgrade steps. Do not create missing application tables by hand. |
| `alembic check` finds differences | Verify the configured target and source version, inspect the difference and stop startup. Do not stamp away drift. |
| `database_not_ready` / HTTP503 | Check DB connectivity and head0015; a running Uvicorn process alone does not establish readiness. |
| Admin says server unavailable | Verify API readiness, then the5173 preview and its fixed8000 proxy. Origin must match the current browser origin. |
| HTTP401 | Use the correct current ADA bearer token for this database; reset/rotation/expiration/revocation can invalidate it. |
| HTTP403 / Access denied | Verify the exact account UUID has `admin_grants.enabled = true`; use the local audited grant command if deliberately authorized. |
| API ready but chat fails | Run `ada.exe doctor`; verify Ollama11434, the configured model tag and local memory/capacity. Retry with the same request UUID/payload when outcome is unknown. |
| Address already in use | Inspect the specific listening port and executable first. Reuse the intended service or stop only your verified old process. |
| Backup says client/server major versions must match | Use Windows17 pg_dump **and** pg_restore for this server17. Native18 tools are not the matching recovery pair. |
| Restore target already exists or has a rejected name | Choose a new isolated `ada_restore_*` name; the tool intentionally refuses existing/live targets. |
| Artifact authentication fails | Verify artifact/passphrase; a wrong key must not trigger an overwrite or an unencrypted fallback. |
| Missing/stale deletion ledger | Obtain a fresh authoritative ledger. Do not invent an empty one to resurrect erased content. |

## 11. What was actually verified for this local startup

The live Docker database was freshly inspected at **0015**, so
`alembic upgrade head` completed without pending changes and `alembic check`
reported no drift. No reset, token rotation or existing-account grant change was
needed. API readiness and the built admin proxy worked. A temporary synthetic
account exercised authentication, ordinary-user admin denial, explicit admin
grant, monitoring reads, real Ollama chat and identical completed replay. The
temporary account/content/grant were removed afterward; original account,
credential, conversation, request and source records were checked unchanged.
Normal minimal monitoring audit entries were retained.

This is local loopback operation. It does not establish physical-phone audio,
LAN/VPN/HTTPS, unattended restart or broad real-model answer quality. The complete
dated checks, validation-harness correction and remaining gates are in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md).
