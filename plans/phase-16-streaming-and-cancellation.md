# Phase 16 — durable streaming and generation cancellation

Status: planned. Prerequisite: Phase 04; Phase 06 for monitoring additions.
This phase can be selected before higher-numbered memory/affect work. Apply
STANDARDS and CODEX-WORKFLOW; preserve the non-streaming API/CLI.

## Goal

Show incremental replies and support an explicit Stop operation without losing
idempotency, history/citation snapshots or capacity accounting after reconnect.
A transport disconnect does not automatically mean cancel server generation.

## Contract and data checkpoints

Design an authenticated submit/stream/status/cancel flow using the existing
request identity and bound payload. SSE or another framed HTTP stream must send
the bearer header; never use a credential in a query string. Events include
request/attempt identity, monotonic sequence, type and payload. Define started,
delta, status, completed, failed and cancellation events, replay cursor and bounded
event retention. Test the actual mobile/web transport rather than assuming a
streaming library can meet the authentication/reconnect contract.

Persist enough owned sequence/checkpoint data to resume or explicitly signal an
expired cursor. A repeated connection never resubmits a turn with a new ID.
Partial text is provisional, not a completed assistant event or endorsed claim.
Commit final response/event/citation mapping once. Clients deduplicate sequence
numbers and replace provisional state with the authoritative terminal result.

Preserve today's `running/completed/failed` response contract for old clients.
Use a compatible legacy mapping such as `failed` plus `request_cancelled` error
for a canceled attempt, with richer operation state in the new stream/status
extension. Do not silently add an unsupported enum to old RequestOutput. Define
whether a canceled request may be explicitly retried with its original snapshot.

## Execution and cancellation

Adapt the actual provider stream with bounded buffering/backpressure. No open
database transaction spans inference or the stream connection. A generation
attempt has an owned cancellation signal/lease and fencing so late chunks or a
stale worker cannot publish after a terminal state. Process restart produces a
recoverable documented status, not a forever-running phantom request.

An authorized cancel targets exactly one owned request/attempt. Persist intent,
signal the provider, finalize once and release admission exactly once. If provider
shutdown is delayed, show cancel requested until it stops; do not free capacity
while inference is still running. A concurrent completion/cancel has one defined
winner and receipt. Cancellation cannot undo a tool side effect from Phase 12.

Keep frozen retrieval context, prompt and labels for the whole attempt. Parse
final citations from the completed reply; provisional labels may be incomplete
and should not become confirmed cards early. If a canceled partial reply is
retained for display, label it incomplete and keep it outside factual memory.

## Clients and monitoring

Android adds honest incremental text, reconnect progress and a real Stop control.
Leaving/backgrounding a screen detaches its observer; it does not implicitly
cancel the server. Reattach using the same cursor/request, or recover terminal
status if the stream expired. Admin shows measured stream/cancel state metadata,
not raw deltas/private text. Update capabilities only after the flow works.

## Verification and exit

Test stream reconnect/duplicate/out-of-order events, disconnect at final commit,
slow consumer/backpressure, expired cursor, provider error, process restart,
revoked token, foreign request cancel, cancel/complete races and stale attempt
publication. PostgreSQL tests prove fencing/history uniqueness. Measure actual
capacity release and ensure old CLI/non-streaming requests still work.

Run Android/browser integration where relevant and real provider streaming/Stop
smoke, clearly separated from fake streams. Exit with resumable exactly-once
terminal publication and truthful cancellation behavior. No voice or background
autonomous tasks are introduced as part of this phase.
