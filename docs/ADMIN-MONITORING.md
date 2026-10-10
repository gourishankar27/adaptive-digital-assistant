# Admin monitoring API — Phase 05

The API exposes operational metadata to explicitly granted accounts. It does not
expose private chat, prompt, response, source or document text. The Phase 06 browser
dashboard reads these metadata APIs using the existing explicit admin policy.

## Migration and local operator commands

Back up the intended database using your existing operator process, stop ADA and
run the migration from the repository root when installing this change:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
```

The current supported head is **0006**. Admin monitoring was introduced by
migration **0004**, which adds empty `admin_grants`, metadata audit/state tables
and request-monitoring indexes. Phase 08 adds document ingestion in **0005**;
Phase 09 adds explicit scoped identity in **0006**. Running the current source
requires 0006 for readiness. It preserves populated users,
credential hashes, requests, prompts and retrieval snapshots. Released migrations
0001–0003 stay unchanged. Neither migration nor startup grants an account access.
`/health/ready` rejects an old/unknown schema with sanitized 503; `/health/live`
does not access the database or provider. Validation runs use disposable schemas;
they do not migrate the user's configured application database.

The reported admin login issue was repaired through a separately authorized
**0004** application-database upgrade and an explicit grant for the user-selected
account. That repair targets the pre-Phase 08 backend. Phase 08's **0005** migration
was validated in disposable databases and remains a separate installation step,
as does Phase 09's **0006**;
it is not applied by the document implementation or browser tests. Restarting
the new source against an application database still on 0004 will report not ready.

Use the **account UUID** issued by `create-user` or returned by that account's
authenticated `/v1/me`, not its display name:

```powershell
.\.venv\Scripts\ada.exe grant-admin ACCOUNT_UUID
.\.venv\Scripts\ada.exe revoke-admin ACCOUNT_UUID
```

These are local commands for the trusted database operator. They require the
server's configured database access, have no remote grant/revoke endpoint and
print only the target UUID and resulting monitoring flag. Each valid target
attempt records granted/revoked/unchanged/not_found; changing a role and recording
its audit commit together. Invalid UUID arguments are rejected before DB access.
Missing users never receive a grant. Revoking an absent grant is an audited no-op.

Local audit actions use `actor_kind=local_operator` and the reserved actor UUID
`00000000-0000-0000-0000-000000000000`. This identifies the trusted local authority;
it does not identify an individual human sharing the server account. HTTP actions
record the authenticated user's UUID. Individual operator enrollment is deferred.

The account continues using its existing bearer token. Every admin request checks
the current database grant; successful reads recheck it and commit the audit before
the response is sent. Revocation also blocks an in-flight probe before delivery.
Role claims, account/profile names, model output and capabilities confer no grant.
An admin's normal conversation, event, request, retrieval, source and memory routes
remain restricted to that admin's own records. Tokens and DB credentials never
belong in command arguments, plans or monitoring response/log captures.

## Read-only contract

All routes require bearer authentication and return `Cache-Control: no-store`.
The exported definitions are in [OpenAPI](../contracts/openapi.json).

| GET route | Data |
|---|---|
| `/v1/admin/me` | Account UUID and `monitoring:read` permission only |
| `/v1/admin/overview` | Request counts/token totals in a selected 1–168 hour window (default 24), database schema readiness, provider health and process admission |
| `/v1/admin/requests` | Selected request metadata, bounded filters and pagination |
| `/v1/admin/requests/{owner_id}/{request_id}` | Composite request metadata plus counts and selected retrieval budget fields |
| `/v1/admin/providers` | Configured provider/model tags, context/output/timeout limits, cached metadata health and process admission |
| `/v1/admin/audit` | Fixed-field role/access audit metadata |

Monitoring lists return envelopes containing `items`, `limit`, `offset`,
`has_more` and `updated_at`. Limits default to 50, maximum 100; offsets are
0–10,000. Request filters are `owner_id`, `request_id`, `status`, `provider`,
`created_from` and `created_to`. Times are UTC epoch milliseconds, with a
half-open creation interval; the default is the last 24 hours, maximum interval
seven days. A request-ID filter requires its owner ID. Returned interval bounds
can be reused on subsequent pages. Ordering is descending creation time, owner ID,
request ID; audit ordering is descending audit ID. No unbounded total is queried.
Audit filters are `actor_id`, `action` and `outcome`. Unknown list filter keys,
invalid UUIDs/states/bounds and excessive windows return sanitized 422.

Request correlation always uses `(owner_id, request_id)`; a UUID alone can match
different owners. DTOs contain owner/conversation/scope UUIDs, state/attempt,
provider/model tags, created/started/finished/observed milliseconds, nullable token
counts and an allowlisted error code (`unknown_error` for an unknown stored code).
`elapsed_ms` is finished-or-observed minus the current attempt's start; it includes
context/database overhead and is **not provider latency**. Failed records without
a finish time have null elapsed time. Token null means unrecorded, whereas zero
is a recorded value. Overview includes the number of requests with recorded token
metrics; all-unknown/empty totals are null.

Retrieval summaries select array lengths, recorded retrieval duration and specific
numeric/boolean budget keys in SQL. They do not fetch the stored query, candidate
objects, selected evidence/quotes or whole budget JSON. Legacy requests return
`available=false` and null summary values. Additional private snapshot fields do
not expand this allowlist. No monitoring query selects usernames, token digests,
messages, responses, system prompts, evidence text or secret configuration.

## Health, capacity and audit bounds

Provider health uses **GET `/api/tags`**, never a generation. It reports metadata
endpoint reachability and configured-model presence separately. Both success and
failure results are cached for 30 seconds, with one refresh at a time, 3-second
network timeouts, a streaming deadline check and a 256,000-byte response bound.
HTTP client probe logging is suppressed within the probing thread to avoid URL,
credential/header or response leakage. Network I/O happens outside DB transactions.
Provider failures return fixed codes; the API never returns raw response bodies,
provider URLs, database URLs, credential paths or connection errors. Fake/custom
providers without this health adapter report unknown, not invented live health.

Generation admission is a snapshot of ADA's current semaphore: maximum, available
and active **process slots**, for **one worker**. It neither reserves a slot nor
counts other Ollama clients. GPU utilization and tokens/second remain null.
Database loss returns sanitized 503 and cannot produce a successful audited read;
if the audit database is unavailable, that attempt cannot be durably recorded.

Monitoring admits at most 60 authenticated calls per principal and 600 globally
per sliding minute. Excess calls return 429 with `Retry-After: 60`. The bounded
in-process limiter keeps at most 4,096 recent principals and resets on restart.
Repeated throttled polls are suppressed from the audit; a globally bounded first
throttle event is recorded once per minute. Missing/invalid tokens have no known
actor and receive 401 without an invented audit identity. Known ordinary/revoked
accounts receive audited 403 within these same volume bounds.

Audit rows have fixed actor/action/target-owner/target-request/outcome/UTC fields.
The singleton audit-state row serializes role changes and audit insertion/pruning
across the server and CLI. Every write prunes records older than 30 days and caps
logical rows at 10,000; queries hide expired rows even after downtime. Expired
storage is removed on the next audited operation, rather than by a background
scheduler. Audit is an operational rolling record, not immutable external
compliance storage. Existing chat/evidence retention is unchanged.

`admin_monitoring=true` in capabilities advertises the implemented API to ordinary
clients too. It is an additive availability flag, never an authorization decision.
Existing user paths, response fields, fingerprints, frozen prompts, completed
replay, Android themes/chat and web foundation behavior remain compatible.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
.\scripts\test-postgres.ps1
```

Opt in to the local **non-generating** Ollama health test by setting
`ADA_TEST_OLLAMA_HEALTH=1` for the dedicated test run and restoring it afterward.
Those tests grant only synthetic disposable accounts, call the real local model
metadata endpoint and verify unchanged ADA request counts. The actual socket/CLI
test starts/stops a loopback one-worker server with a fake model, then grants,
reads cross-owner metadata, checks owner-only private routes and revokes access.
Tests also exercise PostgreSQL populated upgrades, Alembic drift, index use,
concurrent grants, audit rollback/retention, provider/DB/audit failures, null
metrics, legacy traces, payload/log leakage and OpenAPI response schemas.

Actual runs, skipped checks and remaining target installation/performance/HTTPS
verification are recorded in [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md). The Phase 06 [web dashboard](../apps/admin-web/README.md)
uses these existing contracts. No deployment or operational write UI is included.
