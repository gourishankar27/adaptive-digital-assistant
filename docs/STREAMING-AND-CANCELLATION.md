# Durable streaming and explicit Stop

Phase 16 adds `ada-stream-v1` over the unchanged chat reservation, frozen prompt,
retrieval/source snapshots and `running/completed/failed` request contract. Native
clients still call ADA, never Ollama or PostgreSQL. One Uvicorn worker remains
required: generation admission and provider signals are process-local.

## HTTP flow

Every operation requires the current bearer header. Credentials never belong in
the URL. Ownership comes from authentication; even an admin cannot use these
routes to read or cancel another owner's private request.

| Operation | Behavior |
| --- | --- |
| `POST /v1/conversations/{id}/stream-requests` | The existing `ChatInput`; returns 202 with the owned checkpoint. Reserve the exact request UUID/payload before calling. An identical running/completed replay does not start another generation. |
| `GET /v1/requests/{id}/stream-status` | Current attempt, rich state, sequence, replay floor, full provisional text and the unchanged authoritative `RequestOutput` under `result`. Also represents legacy requests with `available=false`. |
| `GET /v1/requests/{id}/stream?attempt=N&after=S` | Authenticated SSE; optional `Last-Event-ID: N:S` must agree with the attempt and any supplied nonzero cursor. A connection only observes; it never submits. |
| `POST /v1/requests/{id}/cancel` | Strict `{ "attempt": N }`; an immutable same-attempt receipt says `requested` or `already_terminal`. It is intent/observation, not proof that inference already stopped. |

SSE data frames contain `request_id`, `attempt`, increasing `sequence`, `type`,
`payload` and epoch-millisecond `created_at`; SSE `id` is `attempt:sequence`.
The event schema is exported as `x-ada-event-schema` on the OpenAPI operation.
`started` initializes an attempt, `delta` carries text, and `cancel_requested`,
`completed`, `failed`, `cancelled` or `interrupted` records its state change.
The protocol also defines `status` for a state checkpoint; current full checkpoints
come from GET. Heartbeats are SSE comments, not durable events. `access_lost` and
`reset_required` are safe transport control frames, outside the sequenced envelope.

The observer validates the current principal before each bounded batch/heartbeat.
Token rotation closes the observer with `access_lost`; it does not implicitly
cancel already authorized server generation. Expired/superseded cursors produce
409 before headers or `reset_required` after headers. Fetch the checkpoint and
replace provisional text, then attach after its sequence. Ignore duplicates; a
gap or mismatched request/attempt cannot append text. Terminal events trigger GET
of the authoritative result, including the original citation mapping.

## Publication, failure and retries

User evidence, retrieval selections, labels, expression/learning state and prompt
are reserved exactly once in the existing short transaction. Provider inference
and the observer connection run outside database transactions. Delta checkpoints
use separate short transactions. Only final publication commits the complete
response, one assistant source/event, conversation revision and terminal stream
event together. Partial labels never create citation cards or factual memory.
The non-streaming messages endpoint, CLI, old request enums and hashes stay intact.

| Stream state | Legacy mapping | Meaning |
| --- | --- | --- |
| `running` | `running` | Generation owns admission. |
| `cancel_requested` | `running` | Durable intent exists; provider shutdown is still pending. |
| `completed` | `completed` | Exactly one authoritative response and original source mapping. |
| `cancelled` | `failed`, `request_cancelled` | Iterator/connection shutdown observed; no assistant event. |
| `failed` | `failed`, sanitized provider/error code | No completed response was fabricated. |
| `interrupted` | `failed`, normally `interrupted` | Restart, failed terminal publication or operator recovery fences abandoned work. |

Completion and Stop serialize through the same owned conversation/request/attempt
locks. If completion commits first, Stop returns `already_terminal`; if intent
commits first, cancellation wins. Repeating Stop returns the original receipt
even after the final state changes. A Stop for an old attempt returns
`attempt_superseded`; it cannot cancel a newer attempt. Worker instance, exact
attempt and request state fence every delta/final publication.

The provider iterator is closed before finalization and admission release. Delayed
shutdown keeps its slot and shows `cancel_requested`. Closing a client observer
never releases the generation slot. Startup marks old-instance attempts
`interrupted`. An owned status read also reconciles a worker whose final database
write failed or a request fenced by the existing operator recovery command.
An operator-fenced live provider still holds capacity until its iterator stops.
Graceful application shutdown signals workers; it does not fabricate completion.

A cancelled/failed/interrupted request may be explicitly retried with the same
UUID and exact payload/options. Existing revision/prompt checks still apply;
changed history can make retry conflict. The original reservation is reused with
a new fenced attempt. Restore/reconnect never performs this POST automatically.
Completed replay remains immutable. Stop applies to ordinary chat generation;
it does not cancel Phase 12 agent runs or undo a committed tool side effect.

## Bounds and retained data

The native Ollama adapter requests streaming `/api/chat`, disables thinking and
uses the same model/context/output settings as ordinary chat. It validates
fragmented UTF-8 NDJSON, bounded frames, tool-free content and a mandatory terminal
frame; final provider token counts remain null when unavailable. Cancellation
closes its HTTP connection. Local iterator shutdown/admission release is observed;
Ollama supplies no independent remote GPU-stop acknowledgement in this contract.

| Bound | Limit |
| --- | --- |
| Provisional/final streamed UTF-8 text | 65,536 bytes per attempt |
| Durable delta | At most 1,024 code points / 4,096 UTF-8 bytes |
| Native NDJSON frame / received block | 16,384 / 65,536 bytes |
| Retained stream events | Newest 256 per attempt; older sequence cursors expire |
| Finished cursor availability | 24 hours after terminal publication |
| Retained attempts | 8 per request; 1,000 per owner; quota rejection rolls back reservation |
| Concurrent observers / database batch | 16 per process / 16 events |
| Android observer buffer | One frame; bounded line/frame parsing |

Durable writes provide producer backpressure; observers read bounded batches and
await HTTP sends rather than accumulating a per-observer generation queue. A slow
observer cannot force unbounded retention or hold open an inference transaction.
Generation also has the configured native timeout and a checkpoint deadline.

The 24-hour limit expires cursor access, **not physical data**. Checkpoints,
provisional text, terminal snapshots and up to 256 rows per retained attempt remain
stored under the count limits; this phase adds no timed erasure or account-wide
deletion. Provisional text is private/incomplete, excluded from assistant history,
ordinary source evidence and factual retrieval. Backups/account erasure require a
separately selected retention policy; no automatic cleanup is claimed.

## Android and admin

Android enables incremental replies/Stop only when capabilities advertise
`streaming=true`, `stream_protocol=ada-stream-v1` and
`generation_cancellation=true`. Older capabilities retain ordinary chat/polling.
The Keystore journal stays v9: its existing owner/server/conversation/request and
exact payload are sufficient to recover a checkpoint by GET after restart.

Chat labels partial output provisional/incomplete and disables provisional source
cards/links. Stop remains visibly pending until canonical terminal status. Leaving
Chat, switching conversations or backgrounding detaches its observer. Returning
to the original conversation/foreground attaches to the same attempt after GET.
Retries use bounded reconnect delays and Retry-After; 401 clears private state.
Unknown outcome remains recoverable without another request UUID or implicit Stop.

Admin request detail adds only stream state, sequence, replay floor and measured
creation/finish times. Its server query/closed client decoder excludes provisional
text, events, messages, receipts and provider content. No admin cancellation or
private stream viewer is introduced.

## Installation and validation

Source requires additive migration **0013**. Migrations 0001–0012 and saved prompt
versions remain unchanged. A populated downgrade refuses to delete streaming
history, including preflight checks for lower retained histories. Disposable
SQLite/PostgreSQL upgrade/check/replay tests exercise this; the application database
has not been migrated or deployed by this phase. Back up and validate the intended
installation in a separately authorized task.

Run the normal pytest/Ruff, Android unit/lint/build and web contract/type/lint/test/
build gates. `apps/android/scripts/verify-streaming-emulator.ps1` uses an explicit
synthetic HTTP provider, five focused UI cases, two stages across a real force-stop
and strict cold launch. Its private fixture credential is supplied through app
stdin storage, never logged. Real TCP tests exercise detach/reconnect/revocation;
native Ollama completion/Stop measurements are recorded separately from fixtures.
See [STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md) for actual results,
skips, compact-screen coverage and remaining physical/HTTPS/load verification.
