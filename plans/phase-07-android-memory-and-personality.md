# Phase 07 — Android memory, evidence and personality screens

Status: checkpoints A–D implemented; local Android/PostgreSQL/emulator checks
passed (2026-10-09). Physical phone/HTTPS/manual accessibility
and real-model verification remain separate. See [STATUS.md](STATUS.md) and
[WORKLOG.md](WORKLOG.md) for actual checks. Prerequisite: Phase 04. Existing Phase 1/2 APIs provide the core
memory contract. Apply UI-SPEC, STANDARDS and CODEX-WORKFLOW.

## Goal

Let the user inspect and explicitly record facts/preferences/decisions, correct
them with preserved history, inspect exact evidence and choose static ADA
expression. These controls do not silently extract knowledge from a conversation
or learn a relationship. Scope and personality stay separate.

## Checkpoint A — browse owned memory

Add Memory navigation with an owned scope picker and paginated claim list.
Support current, explicit `as_of` and all-history modes using the implemented API;
do not combine `as_of` with history when the server forbids it. Show subject,
predicate, value, kind and effective interval. A superseded status does not mean
the old claim was never valid, including before a future correction starts.

Detail shows exact source version/quote and the replacement link when present.
Preserve stable IDs and account/server/scope-bound caches. Present competing
assertions as conflicting information; neither recency nor UI color decides the
truth. An optional search/retrieval preview calls the current scoped retrieval
endpoint and keeps diagnostic candidates separate from durable claims.

## Checkpoint B — explicit write and recovery

Build a Remember form: scope, user's statement/note, subject, predicate, value,
kind and optional effective interval. Preview the annotation and supporting quote
before a user presses Save. Explain that the user endorses the assertion; an
exact quotation alone does not verify its meaning.

Allocate and protect source/claim IDs and exact payloads before submitting.
Save a note first, then save the claim using its returned version. If the second
call fails, the raw note may exist; resume with the original IDs and input rather
than creating duplicates. Same-ID replay is safe only for identical bound input.
Handle duplicate-claim and ID-reuse conflicts with reconciliation and useful
choices, not a random new UUID loop.

For existing-source selection, use the exact returned content. Convert UTF-16
selection bounds to Unicode code-point offsets, reject split surrogate boundaries
and preserve the selected quote without normalization. Test emoji, combining
marks, multiline CRLF text and non-Latin scripts. Never allow the client to set
trust/owner/confidence or promote an assistant source as explicit user evidence.

## Checkpoint C — correction and historical view

Correction previews old/new value, effective time and new evidence. Use the real
supersede endpoint with a persisted replacement ID; the server atomically closes
the old interval and links the replacement. Display validation for an effective
time at/before the old start, after an existing end or a zero-length replacement.
Resolve competing corrections by refresh; do not mutate the old row locally and
claim a save succeeded.

After success refresh current/history/detail views, but retain previously saved
request citation mappings. Historical views explain valid time versus storage
time; they are not a reconstruction of what ADA knew at that date. Deletion and
source editing are absent from current APIs: do not create fake Delete/Edit
actions. The future retention/deletion design is Phase 18.

## Checkpoint D — static personality and settings

Expose the current allowed enums: style direct/conversational/formal, warmth
reserved/warm, detail concise/balanced/detailed and profile name. Create a new
profile through the existing API; select it for a new conversation. Changing a
setting must not rewrite an existing conversation's frozen personality/prompt.
Use the explicit prompt-upgrade action only for supported baseline upgrades.

Theme/font preferences can be local UI settings. Do not interpret these as
knowledge permissions, permanent relationship facts or dynamic mood. Show the
active saved profile and scope when starting/resuming a chat. Automatic memory
extraction, affect gauges and relationship learning remain capability-gated later.

## Data, failure behavior and verification

No backend migration is expected. Use exact Phase 03 DTOs and current memory
semantics. Keep pending write journals encrypted and identity-bound; clear them
on account/server change. 401 halts writes; uncertain outcomes recover original
IDs; 409/422 preserve user input while showing actionable conflicts.

Test note-success/claim-failure restart, duplicate replay, mismatched ID input,
unauthorized source/claim guesses, model-generated source rejection, code-point
conversion, UTC millisecond precision and correction boundaries. Verify future
correction history and stale original chat citations. Android unit/lint/build,
Compose instrumentation and real API/phone smoke must include empty/error/offline
and accessible long-evidence forms. Existing backend tests must remain green.

## Exit

The user can browse, explicitly remember, inspect sources and correct memory
without losing evidence/time history or creating duplicate records after retry.
Personality changes affect only the documented conversation creation/upgrade
flow. Record manual checks and stop before document uploads or model proposals.
