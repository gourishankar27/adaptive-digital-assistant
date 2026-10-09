# Phase 04 — Android authenticated chat MVP

Status: checkpoints A–D implemented; local verification passed (2026-10-09 UTC).
Prerequisite: Phase 03 verified against current source, OpenAPI and test baseline.
Physical S24 FE/Android 16, release HTTPS, manual accessibility/IME and real-Ollama
checks remain pending target verification; this is not a completed release.
Apply UI-SPEC, STANDARDS and CODEX-WORKFLOW. This phase builds a real mobile client
for existing ADA chat. Memory editing, streaming, voice and tools remain later.

## Goal and user journey

Connect a phone to ADA with an issued bearer token, choose/create an owned
conversation, send a message, recover after interruption and inspect its sources.
Use a warm, readable chat screen with honest request states. The API/model stays
on the backend; the phone does not contact Ollama or become an authority store.

## Checkpoint A — enrollment and connection

Build Connect with normalized server URL, masked token entry, Connect action and
sanitized connection errors. Call me and capabilities, show the authenticated
account/server and reject an unsupported API contract. Do not infer identity from
an editable local name. Keep token out of logs, URLs, backups and screenshots.

Encrypt the stored token and pending-message journal with an Android Keystore
key. Define key-loss/reinstall behavior: reconnect instead of restoring unusable
secret state. Prefer bounded, minimal private persistence; explicitly configure
backup exclusion. Implement logout and account/server switching with complete
cache/journal/draft cleanup and no background submission under another account.

Document emulator host access and USB reverse to the Windows API. Exercise the
real HTTP adapter. Release connection accepts properly verified HTTPS; debug-only
HTTP exceptions must not leak into the release variant. A VPN/remote distribution
setup is outside this phase unless explicitly selected.

## Checkpoint B — conversation selection and history

Load paginated profiles/scopes/conversations. Create a conversation with the
chosen owned profile and optional existing scope; label the automatic new
personal-scope path clearly. Since creation POSTs currently lack idempotency keys,
handle ambiguous timeouts by list refresh/reconciliation, not automatic repeats.

Resume an existing conversation and show its scope, saved style and prompt
version. Page events using server ordering and stable event/request IDs. Merge
pages and pending entries without duplication; do not sort solely by local time.
Keep failed/running turns distinct. Large history must load incrementally without
blocking the composer or replaying old user messages.

If a saved prompt is older, show an explicit update action and explain that it
changes future replies. Call the actual upgrade endpoint only after user action;
respect running-request/revision conflicts. Do not mutate saved profile snapshots
or automatically upgrade all conversations.

## Checkpoint C — request state machine

Implement a ViewModel/repository flow with separate draft, submitted payload,
server status and rendered history. Allocate UUID before submission; persist the
exact request ID, conversation, content, `as_of`, memory option and verified
account/server before sending. A text limit uses Unicode code points to match the
server; emoji must not be counted as two characters for this purpose.

Send actual messages and show complete responses. Use a progress indicator for
unknown/running state, not fake typing tokens. Prevent duplicate Send caused by
double tap, rotation or navigation. Keep the composer usable after completion or
an editable validation error. No Stop generation button until Phase 16.

On timeout/process restart, query the same request. Running means wait; completed
means reconcile once; failed means explicit retry of its original payload;
missing means offer the same-ID submission after verifying identity. Preserve
all retry options and citations. A changed draft is a consciously new request,
not a retry with altered bytes/options. Respect Retry-After and use bounded
backoff. Stop automatic attempts on invalid/revoked authentication.

Handle stale-history conflicts with a history refresh and clear choices. Distinguish
busy/provider failure, too-large prompt/input, unsupported fields, inaccessible
resources and network loss. Show sanitized product wording, with optional request
ID/error detail for debugging. Never replace a failed request with a successful
fixture reply.

Support the existing memory option and an advanced historical instant control,
preserving UTC millisecond semantics. Keep ordinary chat defaults simple. Do not
change those options while retrying a reserved request.

## Checkpoint D — source display

Render safe selectable text/Markdown, allowlisted external links and code blocks
as text. Display `[M#]` source chips only against the same request's cards. For
history, lazily fetch status/cards by its request ID; cache with account/server
identity. Show exact quote, origin/version, validity and an optional Details panel.

Unknown labels and missing legacy trace are explicit unavailable states. Show
selected-but-uncited context only in a separate retrieval details screen. Do not
resolve old source labels against a current claim list or rewrite historical
citations after a correction. Long source text needs accessible scrolling and
copy selection. Source cards document provenance, not a truth guarantee.

## Data and API boundary

Use current routes typed in Phase 03. No backend schema or prompt change is
expected. Local persistence is client recovery state only, keyed by verified
identity and server. If a real mobile blocker requires a small API adjustment,
document/test it compatibly; do not implement streaming/admin/automatic memory
as an incidental workaround.

## Verification and failure cases

Unit/transport tests cover serialization, Unicode limits, status/error mapping,
exact-payload retries, bounded polling and identity-isolated persistence. Test
double tap, rotation, process recreation before/after POST response, response lost
after server commit, running-to-completed recovery, token revocation, server
switch, duplicate history pages, legacy traces and unknown source labels.

Compose/instrumented checks cover focus/keyboard, TalkBack labels, large text,
small screen, long reply/source quote, light/dark mode and navigation with a
pending request. Run unit/lint/build tasks and emulator integration with a real
ADA HTTP backend. Separate fake-provider determinism from a manual real Ollama
conversation and source-card demonstration with known explicit memory.

Run a physical-phone smoke: connect, list/create/resume, send, interrupt network,
recover the same request, inspect citations, rotate/reconnect token and logout.
Record phone/OS, connection method and checks actually performed. No unmeasured
latency or battery promises.

## Exit and handoff

A usable Android APK can perform the complete authenticated flow without mocked
production data or duplicate turns. Required backend checks still pass. Pending
recovery, identity switching and sources have evidence. Record unresolved device
checks as pending release verification, not a completed release.

Update app README, STATUS/WORKLOG and capabilities only if backend features
changed. Phase 07 can add memory forms; Phase 16 can add real streaming. Stop
here. Suggested Codex scope: “Implement only phase-04-android-chat-mvp.md after
verifying Phase 03. Preserve current retry/evidence contracts and complete the
emulator/device validation, recording any unavailable target checks.”
