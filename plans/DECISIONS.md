# Architecture decisions and open inputs

Recorded 2026-10-08. Change a decision with rationale, compatibility impact and
verification; do not silently rewrite the historical reason.

## Adopted defaults

| Decision | Reason and boundary |
|---|---|
| Keep Phase 0–2 as the baseline | The user's server and real chat work. Fix the fixture without weakening migration validation. |
| Ship interfaces before broader memory/agent work | The user wants a phone client and a separate operator UI. Existing HTTP APIs support a useful chat client. |
| Native Kotlin/Compose Android | Direct Android lifecycle, accessibility and secure-storage integration; no iOS requirement yet. |
| React/TypeScript/Vite admin SPA | Existing FastAPI owns data/auth; a small operator SPA can use typed adapters and same-origin deployment. |
| Server-enforced admin role; metadata-first monitoring | No role currently exists. A normal account token must not expose cross-user private content. |
| Manual token enrollment initially | Compatible with today's CLI-issued bearer tokens. Multi-device enrollment/revocation is Phase 18. |
| Single worker remains | Capacity is process-local today. More processes/jobs require a shared admission design. |
| Static warm persona now; dynamic state later | Existing style config is usable. Affect/learning needs bounded validation and opt-in provenance. |
| Proposed routes are not capabilities | OpenAPI/current code define the implemented contract; clients gate unsupported features. |
| Phase numbers are identifiers | Dependencies, not arbitrary numbering, determine eligible work. Streaming may follow the first Android release. |

## Resolve during the relevant phase

- Phase 03: actual phone OS, development JDK/Android SDK/Node availability,
  compatible pinned tool versions, app package identifier and debug connection.
- Phase 04: physical-phone test access and the desired private remote access
  method. Use emulator/USB development without exposing database/provider ports.
- Phases 05–06: which account receives an explicit locally granted admin role,
  monitoring retention and any approved metadata beyond the minimum.
- Phase 08: first accepted document formats and content/storage quotas. Begin
  with text/Markdown; PDF parsing is a separate checkpoint.
- Phase 10: available embedding model/resources, exact versus approximate search
  tradeoff, evaluation dataset and measured recall/capacity.
- Phase 12: first selected tools; read-only built-ins before external writes.
- Phases 14–15: user-selected preference controls and consent/reset behavior.
- Phase 18: device credential lifecycle, retention/deletion policy, backup target
  and release exposure. Operational policy needs explicit user choices.
- Phase 19: whether local mobile inference or any particular integration is
  needed at all, using actual phone hardware and authorized accounts.

These inputs do not block writing the plans. A Codex implementation should
progress with the documented defaults where reversible, and ask only for a
material missing product choice instead of inventing credentials or hardware.

## 2026-10-08 — Phase 03 decisions

- The user confirmed a Samsung S24 FE running Android 16. Keep minimum SDK 26;
  compile/target SDK 36 matches Android 16. This confirms OS compatibility only,
  not a physical-phone, TalkBack or real-backend test.
- Use `dev.ada.assistant` as the Android application ID, with `.debug` for local
  builds. Release signing/distribution remains unselected. Keep one app module
  with data/UI boundaries until feature work justifies more modules.
- Pin Gradle 8.13 (distribution checksum), AGP 8.11.1, Kotlin/Compose compiler
  2.2.21 and Compose BOM 2025.10.00. Pin JDK 21.0.12.1 and use JVM 17 bytecode; the local
  Temurin runtime reports 21.0.12.1+1. Version catalog and Gradle locks capture the
  library graph. Compatibility references and Windows setup live in Android README.
- Pin web Node 24.12.0/npm 11.6.2 to the installed supported toolchain; lock the
  React/TypeScript/Vite/router/Query graph in package-lock.json. Generate web DTOs
  from the actual OpenAPI; decode int64 timestamps losslessly to `bigint` and
  preserve Android timestamps as `Long`. Do not serialize a timestamp through a
  JavaScript floating-point value before validating its range.
- Preserve historical snapshot fields when typing output: personality snapshots
  and retrieval detail records retain additive keys; optional ranked/budget keys
  remain absent when originally absent. This is an output contract refinement,
  with no migration, request fingerprint or prompt upgrade.
- Both foundations verify the ordinary account/capabilities only. They grant no
  admin authority. Credentials are volatile; Android's storage interface has no
  insecure fallback. Keystore enrollment/journaling is Phase 04, server admin
  authorization Phase 05, and monitoring screens Phase 06.
- Keep backend/dev servers on loopback. Web uses a fixed same-origin development
  proxy; Android debug HTTP allows only emulator/loopback hosts and release
  requires verified TLS. Disable credential-bearing redirects and ambiguous POST
  retries. No permissive CORS, TLS bypass or provider/database client is added.

Actual checks and outstanding target verification are recorded in STATUS/WORKLOG;
tool choices alone are not evidence that a device or product flow passed.

## 2026-10-09 UTC — Phase 04 decisions

- Keep the existing server routes, authentication, capabilities, prompt snapshots
  and released migrations. Enrollment accepts an already issued bearer token;
  this phase adds no device-credential service or new server authority.
- Use one bounded atomic AES-256-GCM record under Android `noBackupFilesDir`, with
  its key in Keystore, for the verified credential and one exact pending message.
  Commit before POST. Key loss or corruption discards unusable state and requires
  reconnect. Drafts and loaded history/source caches remain in ViewModel memory.
- Restore only after `/me` verifies the stored owner/server. An ordinary Connect
  clears old private state; explicit same-account token replacement re-verifies
  identity before retaining a journal. Logout fences results immediately and
  waits for durable cleanup before allowing another connection.
- Use bounded GET recovery with explicit same-ID, same-payload retry/submission.
  Mark each POST body one-shot so OkHttp cannot silently replay a creation or
  chat write after `503` with `Retry-After: 0`. An explicit retry creates a fresh
  body with the original bytes/options; it is not a new request ID.
- Render selectable literal replies/source quotes and explicit HTTP(S) link
  buttons without adding a Markdown/HTML renderer. Original request cards remain
  separate from selected-but-uncited retrieval detail and unknown labels.
- Retain Oxford Blue as the default and the existing Dark Red/Olive light/dark
  choices. No new dependencies, local database or later-phase controls are needed.

These choices stay within Phase 04. STATUS/WORKLOG distinguish deterministic
fake-provider HTTP/emulator checks from pending physical-phone, HTTPS and real
Ollama verification; there is no deployment or release distribution.

## 2026-10-09 UTC — Phase 05 decisions

- Use a separate absent-by-default grant keyed by account UUID, with no remote
  enrollment. The trusted local operator uses a reserved audit actor UUID; HTTP
  actions use the authenticated user's UUID. No name/persona/model/claim grants
  authority, and private user routes never inherit cross-owner access.
- Serialize role changes and audit insert/prune with a singleton row. Audit and
  role changes commit together; audited successful reads recheck grants before
  delivery. Prune on operations at 30 days/10,000 logical rows, hide expired query
  rows and throttle authenticated polling at 60/principal and 600/global/minute.
  This is a rolling operational record, not individual human/compliance attribution.
- Select metadata columns and JSON scalar lengths/budget keys. Preserve composite
  request identity, nullable metrics and absent legacy traces; elapsed timestamps
  include overhead and are not claimed as provider latency. Admin pagination uses
  bounded envelopes without changing existing user arrays.
- Probe only Ollama model-list metadata with bounded response/time and a serialized
  30-second success/failure cache outside database transactions. Unknown adapters,
  GPU utilization and throughput remain unknown. Expose actual process semaphore
  slots and keep one worker. Provider client logs are suppressed only in probe threads.
- Supported schema head is 0004, checked against Alembic by a regression test.
  Preserve released migration bytes, request inputs/replay, prompt snapshots and
  existing paths. Regenerate web DTOs only; no dashboard workflow is introduced.

These choices implement Phase 05, not Phase 06 or later authentication/operations
features. See docs/ADMIN-MONITORING.md and STATUS/WORKLOG for limits and actual runs.

## 2026-10-10 UTC — Phase 08 decisions

- Keep bounded raw files in owner-bound private database BYTEA/BLOB storage rather
  than introducing a filesystem/object-store service. This preserves exact bytes
  without filename paths or cross-account deduplication; backup size and retained
  failed receipts count toward documented storage limits. No deletion/retention
  service is added in this phase.
- Use strict UTF-8 identity parsing and exact code-point chunks with inclusive
  first/last-character line anchors. Raw and parsed hashes are equal; only the
  separate lexical projection is normalized. Native PostgreSQL/SQLite full-text
  indexes remain rebuildable derived state. PDF needs its own extraction/page
  contract and is explicitly deferred, along with OCR and compressed formats.
- Reserve immutable input in a short transaction, parse outside it, then publish
  the complete version/chunks/projection atomically. Thirty-second leases and three
  fenced attempts support explicit same-ID retry; no background worker or automatic
  write is introduced. Availability never makes a version known before publication.
- Preserve original claim-card arrays and add separate typed D document evidence,
  with honest imported/untrusted origin and no fabricated claim IDs. Memory is the
  master evidence switch; `use_documents` defaults false. v4 adds document context,
  while exact v3 prompts and claim retrieval remain supported. Explicit audited
  upgrades preserve old snapshots; default request fingerprints and completed
  replay remain unchanged.
- Keep the Android upload limit at 64 KiB, below the server's 256 KiB, so an exact
  upload and the existing chat/memory reservations fit a bounded encrypted v3
  record. Old v1/v2 records remain readable; identity verification precedes
  recovery, and restoration never automatically POSTs. No new dependency or device
  permission is required.
- Treat the separately requested login repair as explicit authorization for a
  verified backup, application migration 0004 and an exact existing-account grant.
  Keep Phase 08 migration 0005 as a separate unperformed installation step under
  the user's no-deployment instruction. The current source requires 0005.

See STATUS/WORKLOG for actual Windows/PostgreSQL/browser/emulator evidence and
remaining target checks. These decisions authorize no later phase or deployment.

## Phase 09: explicit scoped identity lineage

The selected identity milestone uses exact NFKC/case/whitespace aliases and
user-confirmed mappings. Canonical labels/types are knowledge annotations, never
accounts or role grants. Collisions remain valid across distinct entities; absent
explicit self binding, pronouns and `User` do not establish a canonical person.

Nullable claim references and append-only link/alias/merge intervals preserve raw
assertions and as-known-at interpretation. Backfill is intentionally null rather
than inferred. Corrections accept a new reference explicitly; omission retains
legacy fingerprints and leaves the replacement unlinked. Merge is a preview-bound
redirect with audit and undo, rather than a rewrite of old claims or traces.

Scope row locks make operation UUID replay and preview checking atomic on
PostgreSQL. Histories count against retained quotas. Alias matching expands
candidates inside the current budgets; ambiguity excludes linked assertions before
ranking. Truncated choices fail closed, and request-frozen alternatives remain
visible in Android retrieval details. Overlapping ambiguous names are treated
conservatively; explicit distinct aliases can clarify them. No new prompt version
or inference transaction is introduced.

The existing Android Memory entry hosts the editor instead of adding an unrelated
application. Exact entity operation recovery extends the same Keystore record to
v4; old chat/memory/document records remain readable. See
[identity policy](../docs/ENTITIES-AND-ALIASES.md) and [STATUS](STATUS.md).
