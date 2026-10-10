# Phase 05 — admin authorization and monitoring API

Status: checkpoints A–C implemented; Windows/disposable PostgreSQL verification
recorded in STATUS/WORKLOG. Prerequisite: Phase 03. Apply STANDARDS and CODEX-WORKFLOW.
This phase creates the server contract required by the separate admin UI.

## Goal

Allow an explicitly authorized operator to inspect sanitized operational metadata
without expanding the private user API's ownership rules. The Phase 03 baseline
had no admin role. A name, personality, first account or model instruction must never
grant one.

## Checkpoint A — explicit role and audit

Design a small server-side admin grant, default absent for existing/new users.
Add an Alembic migration after the actual head and preserve original users,
tokens, conversations and requests. Add local CLI grant/revoke commands with an
unambiguous account identifier, an audit record and documented operator use.
Do not grant anyone automatically as part of startup, migration or UI enrollment.

Use the existing bearer authentication, then check the current role on every
admin request. Revocation must affect subsequent requests immediately; client
cache/claims are not authority. Normal endpoints still require the authenticated
owner even for an admin. Test no token, ordinary token, granted token, revoked
grant, forged role/owner fields and a model response claiming administrator status.

Audit role changes and monitoring access with actor ID, action, target metadata,
outcome and UTC time. Bound audit-query size/retention and polling volume. Never
record token hashes, raw requests, source quotes or secret settings. This role
does not introduce arbitrary SQL, credential viewing or account impersonation.

## Checkpoint B — metadata endpoints

Proposed routes; finalize typed schemas and export OpenAPI when implemented:

| Route | Result |
|---|---|
| `GET /v1/admin/me` | Operator identity and granted monitoring permissions |
| `GET /v1/admin/overview` | Bounded-window counts, readiness, known capacity and update time |
| `GET /v1/admin/requests` | Bounded filters/pagination over request metadata |
| `GET /v1/admin/requests/{owner_id}/{request_id}` | One request's metadata and sanitized retrieval summary |
| `GET /v1/admin/providers` | Configured provider/model, safe limits and measured health if available |
| `GET /v1/admin/audit` | Bounded audited operation metadata |

Request IDs are unique per owner. Use the composite identity in links, filters,
DTOs and cache keys; never assume the UUID alone is globally unique. Query only
required columns. List/detail responses exclude message bodies, system prompts,
responses, evidence quotes, user names and document contents by default. Owner,
conversation and scope IDs are sufficient for diagnostic correlation.

Expose status, attempt, provider/model, created/started/finished timestamps,
sanitized error code and recorded token counts. Distinguish missing token values
from zero. Current timestamp-derived elapsed time is not pure provider latency;
new latency stages need actual measurement and honest names. Summarize stored
retrieval counts/budget decisions without exposing trace query text or quotations.
Missing legacy traces return an explicit unavailable summary.

## Checkpoint C — health and compatibility

Keep liveness cheap. Readiness must validate the current supported migration head
rather than retain the current hard-coded 0003 after a new migration. Separate
database readiness, provider reachability and generation admission; a provider
probe must not run a chat generation. Cache/rate-bound provider health checks.
Report unknown instead of inventing GPU utilization or model throughput.

Maintain one-worker admission, small aggregation queries and indexed filters.
Sanitize provider/DB failures. Expose safe configuration values only; no password,
secret connection string, filesystem credential path or token digest. Advertise
admin monitoring availability accurately without granting permission through
capabilities. Older clients/CLI and existing user responses remain compatible.

## Verification

Use PostgreSQL to test populated migration, role grants/revocation, composite
request identity, aggregation/index behavior and owner-only user APIs. Exercise
ordinary users against every admin route, including detail guesses. Validate
schema/OpenAPI, old completed replay and prompt compatibility. Test DB/provider
failure, missing metrics, legacy traces, malformed filters and pagination bounds.

Run all applicable backend/Ruff/migration checks. Scan representative responses
and operational logs for secret/body leakage. A real health probe must leave
generation counts unchanged. Test role changes through the actual local CLI.

## Exit

An explicitly granted operator can query real sanitized metadata; an ordinary or
revoked account cannot. Private user routes preserve ownership. The migration,
audit and current-head readiness work on the target PostgreSQL database. Record
results and any unresolved measurements. No admin UI, remote shell, token-management
page or destructive recovery endpoint is implemented in this phase.

## Implemented checkpoints

- A: migration 0004, absent-by-default grants, UUID-based local grant/revoke,
  transactional bounded audit, current-role checks and pre-delivery revocation.
- B: all six typed routes above, composite identity, bounded filters/envelopes,
  selected metadata/SQL JSON scalar summaries, explicit null/legacy handling.
- C: current-head readiness, generation-free cached/bounded Ollama metadata probe,
  actual process admission, unknown GPU/throughput and additive capabilities.

See [operator/API documentation](../docs/ADMIN-MONITORING.md) for finalized fields,
rate/retention policy, installation and failure semantics. Actual runs and remaining
intended-database installation/HTTPS/performance verification are in STATUS/WORKLOG.
The application database was not migrated and no real account received a grant
during validation. Phase 06 and all later feature implementations remain unstarted.
