# Current ADA baseline

Recorded 2026-10-08. Read current source and tests before implementing a phase;
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

Migrations 0001–0003 are released. New work adds migrations. Baseline v3 is current;
v1/v2 conversations retain their saved prompt until explicitly upgraded.

## Current contract

Inspect `src/ada/api.py` and `contracts/openapi.json` for exact schemas. Existing
routes cover authenticated me/capabilities, personalities, conversations/events,
messages/request status/retrieval traces, scopes, notes/source versions, claims,
corrections and retrieval diagnostics. The browser API explorer is `/docs`.

Ownership comes from the bearer credential, not a submitted owner field. A
conversation selects one owned scope. Scopes are private; shared membership and
admin roles are not implemented. Source mapping proves provenance, not truth or
the semantic correctness of the model's sentence.

`GET /v1/conversations/{id}/events` returns event text, request ID/status and
source-version ID. Source cards are recovered from the matching request response;
they must not be reconstructed from today's claim list. Conversation/event reads
currently include some untyped response shapes that Phase 03 should formalize.

Chat returns a complete response. There is no streaming, cancellation endpoint,
automatic memory extraction, document upload, embedding search, tool executor,
admin API, mobile app, voice interface or local mobile model. Static warmth/style
configuration exists; dynamic affect and learned relationship preferences do not.

## Verification evidence

The original packaged Linux run recorded 60 passed/50 skipped. The user's Windows
PostgreSQL run reported 105 passed, 3 failed, 2 skipped. All three failures were
installer fixture tests: native Windows relative paths were serialized with `\\`
while manifest keys require `/`. This update changes fixture serialization to
`.as_posix()` and adds a test that simulates Windows path objects on Linux.
The production migration validation remains strict.

This update's Linux run recorded 61 passed/50 skipped/1 existing warning;
Ruff lint and format checks passed across src, tests, migrations and scripts.
The additional passing test is the portable Windows-path regression. No
disposable PostgreSQL was configured for this local run.

Do not record a clean Windows suite until the user or CI reruns it after this fix.
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

The phone's OS/RAM/SoC, the final remote connection method, admin credential
enrollment and a release distribution target still need implementation-time
decisions. The roadmap selects defaults without claiming these are already known.
