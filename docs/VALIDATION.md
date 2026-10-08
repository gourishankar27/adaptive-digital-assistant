# Phase 1 validation — 2026-10-08

Environment: Linux, Python 3.12.14, the included pinned dependencies. This is not
the target Windows/GPU machine.

## Completed

- `pytest -q`: **44 passed, 34 skipped**, one dependency deprecation warning.
  Skips: 33 PostgreSQL fixture variants (no test server available), plus the
  SQLite copy of a race test that specifically requires PostgreSQL row locks.
- Ruff lint and formatting passed for `src`, `tests`, `migrations` and `scripts`.
- Package 0.1.0 installs; CLI help exposes the implemented memory/scope commands.
- Fresh SQLite migration to 0002, repeat application at head and `alembic check` pass.
- A populated Phase 0 database upgrades with existing scope/event/request IDs,
  content, personality/prompt snapshots and successful request replay preserved.
- Original event-role constraints survive SQLite table rebuilds. Composite foreign
  keys reject cross-owner/cross-scope evidence and missing mandatory sources.
- Exact nonblank spans, Unicode code point offsets, hashes and source trust are
  checked. Missing evidence, model output, forged metadata, invalid timestamps,
  NUL and malformed Unicode fail at the boundary.
- Same-ID writes replay; changed payloads and duplicate assertions conflict.
- Corrections retain old evidence, have half-open validity boundaries, include
  future/expired behavior, and roll back completely on interrupted transactions.
- CLI add/correct/current/historical queries work without a model call.
- Prompt upgrades are authenticated, explicit, audited and rejected during inference.
  They preserve frozen styles and fence retries with obsolete context.
- The installer checks all files before copying, preserves local configuration,
  accepts CRLF, backs up originals, rejects local edits and safely replays.
- OpenAPI is regenerated from the API and describes UUIDs, evidence and int64 times.
- PostgreSQL migration SQL compiles with the composite constraints and built-in
  SHA-256 backfill. SQL compilation is not a PostgreSQL execution check.
- Real Uvicorn/HTTP process smoke passed with SQLite and the fake provider:
  start Phase 0, save a turn, stop, migrate to Phase 1, replay the old reply,
  read backfilled evidence, upgrade the prompt, add/correct memory, stop/restart,
  then recover current/historical values and replay the correction without duplicates.
- Original authentication, isolation, inference failure, admission control, context
  budgeting and interrupted-request recovery checks still pass.

## Remaining target-environment checks

- PostgreSQL runtime and row-lock races. This environment prevents switching to
  the database's required OS user, so a local PostgreSQL test server could not be
  prepared. Run `scripts/test-postgres.ps1` on your laptop. It creates/reuses the
  separate `ada_phase1_test` database and runs fixtures in isolated schemas.
- Native Windows PowerShell execution and Docker port handling.
- Actual Ollama inference, GPU/CPU placement, latency and adherence to the updated
  ADA identity/capability prompt. No real model was called during verification.

The existing Starlette/httpx test-client deprecation warning remains. It does not
fail the suite. Dependencies remain pinned to the Phase 0 versions.

Phase 1 does not implement retrieval in chat, automatic extraction, shared scopes,
tools, document ingestion, consolidation or mobile/edge inference. Capabilities
and the prompt state these boundaries explicitly.
