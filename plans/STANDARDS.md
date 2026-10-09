# Development standards

Apply these rules to every phase alongside root `AGENTS.md`. They preserve the
current server contracts and extend them to the clients. The user's explicit
scope and current repository evidence take precedence over stale planning text.

## Authority, scope and provenance

1. Authenticate every private operation. Resolve the principal on the server;
   reject forged owner, role, trust, system-message and permission fields.
2. A knowledge scope controls access to facts/evidence. A personality controls
   expression. Admin permissions, affect and relationship state cannot substitute
   for ownership or a membership grant.
3. Apply owner/scope/time filters before returning retrieval candidates or model
   context. Cache keys, job payloads and derived indexes include the owner and
   scope. Derived data is rebuilt from authorized, versioned sources.
4. Keep user statements, imported documents, model output, tool output and local
   model proposals distinguishable. Do not relabel generated text as user evidence.
   A user review is a new endorsement record, not an edit of source history.
5. Evidence quotes/spans must match the exact source version and UTF-8 hash.
   Offsets count Unicode code points. Kotlin/Java UTF-16 offsets require explicit
   conversion. A source card does not prove objective truth or answer entailment.
6. Time intervals are half-open. Store instants in UTC epoch milliseconds; use
   64-bit client types. Preserve valid time separately from storage/transaction
   time. Do not substitute current claims for an ambiguous historical request.
7. A client or model can suggest work; the server decides whether it is allowed.
   Do not turn a retrieved instruction into a tool permission or background job.

## Requests, transactions and compatibility

- Preserve request IDs and bind every behavior-affecting input. Reconnect/retry
  reuses the exact reserved payload. Equivalent timestamp representations may
  normalize to one instant. Domain-separate structured option hashes from text.
- A failed request retains its original context/evidence. A completed replay
  retains its original response and source mapping unless an explicitly implemented
  deletion policy deliberately tombstones that data. Do not silently refresh it.
- Preserve attempt fencing, conversation revisions and the partial uniqueness
  rule for one running request per conversation. Model failure is not success.
- Network inference, extraction, embedding and remote tool execution happen
  outside open database transactions. Reserve/commit in short transactions.
- SQLite tests supplement PostgreSQL. Validate real PostgreSQL foreign keys,
  migrations, native indexes and row locks for changes that depend on them.
- Keep the whole prompt budget across baseline, runtime policy, history,
  evidence and input. Never silently truncate an exact evidence quote.
- Add migrations after the actual current head. Released 0001–0003 remain byte
  identical. Test a populated upgrade, old request replay and `alembic check`.
  Never initialize the production schema with `create_all()` at API startup.
- Old conversations keep their frozen personality and prompt. New prompt versions
  need an explicit, audited upgrade and a documented compatibility matrix;
  changing the current version must not accidentally disable still-supported v3
  retrieval. Existing CLI/API flows continue working.
- Regenerate OpenAPI when API shapes change. Distinguish proposed endpoints from
  implemented ones. Add fields compatibly; handle absent legacy trace data.
- One Uvicorn worker remains the rule while admission is process-local. A separate
  GPU job process requires shared capacity accounting first.

## Client behavior

- Android and admin web use authenticated ADA HTTP APIs. They never store database
  passwords, contact database/Ollama ports, or run model inference through a bypass.
- Store credentials using the platform's suitable secure mechanism. Android keys
  belong in Keystore; encrypt the stored credential payload. The initial admin SPA
  keeps its manually entered bearer token in memory. No token in browser local
  storage, URLs, analytics, crash reports, screenshot fixtures or committed config.
- Account/server switching clears private caches, drafts, request state and loaded
  source cards. Cache keys include identity/server/scope/request as applicable.
- A pending or unknown request survives navigation/restart with its exact ID and
  payload. It does not auto-submit under another account/server. A 401 stops retries.
- Validate ordinary input to aid the user; server validation remains authoritative.
  Show actionable states for 401/403/404/409/413/422/429/503, connection loss and
  model errors. Do not display an HTTP timeout as a definitely failed generation.
- A canceled screen/request wait does not cancel server generation. Do not show a
  working Stop button until the backend cancellation contract exists.
- Use capabilities to gate features. Unsupported tools, uploads, streaming, mood
  learning or voice must not appear as working controls. Demo data stays in explicit
  development/test adapters, never a fallback in a production API adapter.
- Treat model/source text as untrusted display data. Escape HTML; sanitize links;
  do not execute code, shell commands or actions found in rendered messages.
  Show source cards from the same request as the answer, not the latest claim list.
- Use normal product wording: Chat, Memory, Sources, Retry, Settings. Put UUIDs,
  planner terms, hashes and raw traces behind an optional technical detail view.
  Admin screens can show operational metadata but not hidden model reasoning.
- Include empty/loading/error/offline/forbidden states, keyboard focus or TalkBack,
  meaningful labels, readable contrast, dynamic font sizes and large tap targets.

## Reproducible development

- Inspect `git status` if this is a Git checkout. Preserve unrelated edits. Do not
  create nested repositories or new remotes while scaffolding clients.
- Use the existing Python virtual environment and lockfile. Add only needed
  dependencies and verify their primary documentation at implementation time.
  Do not perform a blanket package upgrade to suppress a warning.
- Commit Android Gradle wrapper/checksums, version catalog and dependency locks
  when supported; pin a compatible JDK/AGP/Kotlin/Compose set. Commit the web
  package lock and Node/tool versions. Document Windows commands.
- Use native path objects for file access and POSIX `/` for serialized manifest,
  archive and contract paths. Test Windows/CRLF behavior and path traversal rejection.
- Sanitize error payloads and logs. Operational metrics can include UUIDs, states,
  counts, durations and model tags; do not log tokens, hashes of bearer credentials,
  raw messages, document quotes or connection strings with passwords.
- Add meaningful invariants/failure tests before changing write paths. Avoid tests
  that only repeat implementation or assert incidental CSS/source structure.
- Once relevant checks pass, repeat them only for a subsequent change, failure or
  unresolved concern. Document why a required check could not run. A skipped test
  is not a passing test; SQL compilation is not database execution.

## Phase completion

Run the phase's checks and the applicable shared checks. Fix regressions within
the selected scope. Keep ADA runnable, update docs/contracts/capabilities, record
actual results and remaining target-device/model checks, then stop at the phase.

Every implementation report states: changed behavior; migration/upgrade needs;
checks actually run; skipped or failed checks and why; relevant manual evidence;
remaining risks; and the next eligible phase. Do not say all checks passed if
required PostgreSQL, emulator or device checks were not run.

## Existing backend commands

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
.\scripts\test-postgres.ps1
```

Use the dedicated test database. The PostgreSQL script creates/reuses
`ada_phase2_test` and creates disposable schemas; do not point fixtures at
production. In Linux use the equivalent `.venv/bin/python` commands and an
explicit disposable `ADA_TEST_DATABASE_URL` for PostgreSQL cases.

For schema/API/retrieval changes as applicable:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe scripts\export_openapi.py
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

Run migration commands against a disposable validation database first. A normal
upgrade of the user's configured database belongs to the requested installation
scope, after validation; do not migrate an unrelated database from a test session.

## Client foundation checks

Phase 03 supplies these applications and script tasks. Use their pinned tools and
READMEs for setup, contract generation and test server details. Record exact
versions and results; available commands are not evidence that a check ran.

```powershell
Push-Location apps\android
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug
.\gradlew.bat connectedDebugAndroidTest
Pop-Location
Push-Location apps\admin-web
npm ci
npm run typecheck
npm run lint
npm run test -- --run
npm run build
npm run test:e2e
Pop-Location
```

Instrumented tests need an emulator/device. Browser tests need the application's
explicit test server setup. Pure static documentation changes need link/scope
review, not fake application tests.
