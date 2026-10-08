# Phase 1 memory contract

The authenticated user explicitly supplies and endorses an assertion. The server
validates its evidence and ownership without calling a model. Extraction jobs
and model memory-write tools are deferred.

| Record | Meaning |
|---|---|
| `scopes` | Private personal/project context owned by one user |
| `sources` | One user note or raw chat event, linked to its owner/scope |
| `source_versions` | Immutable content snapshot, SHA-256 hash, trust label, version |
| `claims` | User assertion, validity interval, one mandatory exact source span |
| `conversation_prompt_changes` | Previous/new baseline and time of an explicit upgrade |

A chat event, its source and its source version share an ID. A note's first source
version uses its source ID. Version 1 is currently the only version created. Source
edits and document reingestion are deferred. Corrections use new evidence/claims.
Migration 0002 backfills raw history without interpreting it as claims.

Conversations have explicit scopes. History/personality remain conversation-specific
when conversations share a project scope. Projects remain private to their owner;
sharing/membership grants are deferred.

Claims require a `user_explicit` source version in the same authorized scope.
`model_generated` versions are inspectable history, and cannot support these user
assertions. Quotes/hashes are computed by the server. Clients cannot set owner,
trust label, confidence or a fabricated quote.

Subject/predicate/value are user-supplied annotations. A quote establishes provenance,
not truth or semantic entailment. Quoting “We chose SQLite” does not mechanically
validate an annotation about a birthday. Automatic extraction will need separate
validation/evaluation before it can propose writes.

## Time and corrections

Intervals are half-open: `valid_from <= time < valid_to`. Null end means open-ended.
Input timestamps require a timezone and millisecond precision or coarser. Output
timestamps are UTC epoch milliseconds represented as 64-bit integers.

Queries default to now. `as_of` selects the valid-time interval; `history=true`
returns all versions. These options cannot be combined. Subject/predicate filters
use exact matches. List endpoints have bounded `limit`/`offset` pagination.

A correction preserves subject/predicate/kind and replaces value/evidence. Its
effective time must be after the old start and no later than an existing end.
The replacement must have a nonempty interval. In one transaction, insert the
replacement, close the old interval and set `superseded_by`.

`status=superseded` means a replacement exists. An old claim can remain current
before a future replacement starts. Current queries filter intervals rather than
excluding all superseded rows.

Backdated assertions are allowed. Historical queries reflect what is considered
valid then using today's stored state. They do not reconstruct “what ADA knew
then.” `created_at` records storage time; transaction-time queries, contradiction
detection and automatic reconciliation are deferred.

## Spans, retry and integrity

Spans are zero-based Unicode **code point** offsets with an exclusive end, rather
than bytes or UTF-16 code units. Slice the returned source exactly; no normalization
is applied. Whitespace alone is not evidence. NUL/malformed Unicode is rejected.

Caller-generated source/claim UUIDs bind to their write. Same-ID replay returns 200;
a new write returns 201. Different input with a used ID returns 409. A new claim ID
for identical fields/evidence/interval returns `claim_duplicate` (409); use the
original claim ID to replay the write.

The CLI saves a note before saving its claim. A failed second call may leave the
raw note, but no partial claim. Retry with the printed source/claim IDs and identical
input. A correction's claim changes are atomic.

PostgreSQL writes lock a scope row, serializing duplicate checks and competing
corrections. Composite foreign keys reject cross-owner/cross-scope links. Private
access still requires API authorization. SQLite does not prove row-lock behavior.

Sources are immutable through the API. Hashes detect drift during evidence checks;
they do not prevent an administrator rewriting content and hash together. Operators
remain trusted. Database immutability triggers/retention automation are deferred.

## API example

```powershell
$headers = @{ Authorization = "Bearer $env:ADA_TOKEN" }
$root = 'http://127.0.0.1:8000'
$scope = Invoke-RestMethod -Method Post -Uri "$root/v1/scopes" -Headers $headers -ContentType 'application/json' -Body '{"name":"ADA development","kind":"project"}'
$statement = 'We chose PostgreSQL for ADA.'
$noteBody = @{source_id=[guid]::NewGuid().ToString(); content=$statement} | ConvertTo-Json
$source = Invoke-RestMethod -Method Post -Uri "$root/v1/scopes/$($scope.id)/notes" -Headers $headers -ContentType 'application/json' -Body $noteBody
$claimBody = @{claim_id=[guid]::NewGuid().ToString(); subject='ADA'; predicate='database'; value='PostgreSQL'; kind='decision'; source_version_id=$source.id; span_start=0; span_end=$statement.Length} | ConvertTo-Json
$claim = Invoke-RestMethod -Method Post -Uri "$root/v1/scopes/$($scope.id)/claims" -Headers $headers -ContentType 'application/json' -Body $claimBody
Invoke-RestMethod -Uri "$root/v1/scopes/$($scope.id)/claims" -Headers $headers
```

This text has no supplementary characters, so PowerShell `.Length` matches the
code point count. With emoji, use the Python CLI or calculate code point offsets.
Keep generated IDs for retries.

| Route | Purpose |
|---|---|
| `POST/GET /v1/scopes` | Create/list private scopes |
| `GET /v1/scopes/{id}` | Inspect an owned scope |
| `POST /v1/scopes/{id}/notes` | Record user evidence |
| `GET /v1/scopes/{id}/source-versions` | List evidence snapshots |
| `GET /v1/source-versions/{id}` | Read exact evidence |
| `POST/GET /v1/scopes/{id}/claims` | Write/query explicit assertions |
| `GET /v1/claims/{id}` | Inspect a claim/citation |
| `POST /v1/claims/{id}/supersede` | Atomically correct an assertion |
| `GET /v1/conversations/{id}` | Scope/personality/baseline metadata |
| `POST /v1/conversations/{id}/prompt-upgrade` | Upgrade/archive a baseline |

`contracts/openapi.json` provides schemas, including 64-bit timestamps. Assistant
text cannot advertise additional authority or grant permissions.
