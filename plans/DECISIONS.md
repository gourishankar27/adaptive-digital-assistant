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

## Phase 10: exact scoped vectors, disabled activation

Use the existing pinned HTTP stack and local Ollama embedding endpoint rather
than adding a model runtime or vector extension. Bind the selected 300M model's
full manifest digest, dimension and text-prefix version to a namespace. Exact
bounded ranking on PostgreSQL/SQLite avoids an unproven scoped ANN pool. Rebuild
is an explicit owned API call under the same process admission as chat; it has no
background worker or independent GPU process.

Derived history indexes preserve original evidence. Publication rechecks the full
bounded corpus after inference, with atomic replacement and one namespace/scope.
Partial/stale/dimension drift fails the semantic channel as a whole to lexical.
Queries apply entity/time/availability gates before cosine scoring. Lexical-first
RRF60 preserves baseline reliability, whole conflict slots and prompt budgeting.
New trace metadata and channel results freeze at reservation; retries do not refresh.

Hand-built synthetic vectors improved fixture recall, but the selected model is
not installed and has no local resource/relevance measurement. Keep production
semantic activation disabled. This satisfies the selected phase's documented
disabled-exit alternative, with a reproducible real-provider evaluation command
for later target verification. No later phase or deployment is inferred.

## Phase 11: endorsement evidence and versioned reviewed origin

Keep existing v1 origin enums byte-compatible. Reviewed claims retain the legacy
user_asserted envelope because their mandatory evidence is a newly authored
explicit endorsement. Add an optional provenance object with version review-v1
and origin user_reviewed, advertised through memory_provenance capability. Updated
clients display User reviewed and original support trust separately. This avoids
breaking strict older decoders while preserving a distinct reviewed origin and
never relabeling model/imported text as user-authored. Existing claims and frozen
request citations retain their original shapes/provenance.

Use a separate proposal/extraction/review ledger with scope locks and exact
review hashes. Approval atomically creates immutable user evidence, claim,
original support links and receipt; specific corrections preserve other values.
Do not promote the original model/imported source itself. Fresh retrieval verifies
those mappings and support integrity. Downgrading populated review history is
refused. The Android record advances to v5 with old versions readable and exact
explicit recovery. No dependencies or prompt versions change. See
[the implemented policy](../docs/MEMORY-PROPOSALS-AND-REVIEW.md).

## Phase 12: separate protocol, all read-only proposals approved

Keep normal ChatInput, required tools:false, saved v3/v4 snapshots and completed
replay unchanged. Add an explicit ada-agent-v1 compatibility registry/run input
and additive agent capabilities rather than treating ordinary model JSON as a
command or silently upgrading old prompts. This preserves v3 claim retrieval and
uses the existing audited upgrade path for older conversations.

Select calculator and owned memory/source lookup only. Every selected tool,
including read-only calls, receives an exact version/argument/actor preview and
explicit approval. This exercises the permission/receipt checkpoint without
authorizing an unselected external integration. Unknown outcomes fence late workers
and never reexecute. Tool-origin evidence does not create user claims. SQLite's
nontransactional downgrade DDL requires a 0009 preflight before the existing 0008
review-history refusal; 0008 and older migrations are unchanged. The pinned Alembic
revision planner resolves both absolute and relative downgrade destinations.

The existing Android Keystore record becomes v6 without changing file/key/AAD or
dependency versions; all prior formats remain readable. Saved approval delivery
can reconcile by authenticated GET, with no automatic POST. Admin's optional
aggregate state counts carry no private arguments/results. See
[the implemented policy](../docs/TOOLS-AND-AGENT-LOOP.md).

## 2026-10-11 — Phase 13 continuity without factual promotion

Episode summaries have generated trust and exact original maps; they do not enter
claim/document candidates or alter ordinary chat/prompt inputs. The request-ID
navigation-context protocol freezes a selected bounded map separately, preserving
completed replay and saved v3/v4 snapshots. Android provides explicit navigation
and source inspection, not an implicit prompt upgrade. Tags are labels, not support.

One bounded lifespan worker shares process admission and leases read-only
generation for at most three tracked attempts. Reserve/claim/publication are short
transactions; a fenced result and receipt commit atomically. Proposal publication
validates the complete batch before writes and submits only pending Phase 11
suggestions. Lexical rebuild changes derived projections only. Policy/schema/model
and source snapshots participate in dedup/stale checks. History is retained.

Static migration 0010 preflights populated lower-history downgrade guards before
any SQLite DDL. Android journal v7 retains old formats/keys; GET-only restoration
does not resubmit unknown delivery. Admin's newest-25 projection contains IDs,
states and measured times, with no private source/output text. See
[the implemented policy](../docs/EPISODES-AND-CONSOLIDATION.md).


## Phase 14 — explicit expression overlay, frozen defaults and reviewed signals

Baseline v4 stays current and v3 retrieval remains supported. A separately
versioned ada-expression-v1 overlay is applied only to explicitly activated or
newly inherited conversation bindings. This preserves saved personality/system
prompts and old request fingerprints while permitting an audited future-reply
update that conflicts with in-flight chat. Defaults never propagate behind
history. Failed/completed retries retain the original nullable expression snapshot
and exact messages. The policy reserves exactly 800 bytes within the current
whole-prompt limit, so different style values cannot alter evidence allocation
through their length; activation adds this documented fixed overhead.

Explicit preference precedence is personality, account, scope, profile, then
conversation. Exact source settings receipts are frozen per field. Dynamic tone
is separately opt-in and is not a feeling, diagnosis, evidence confidence or
permission. One native-bounded current session per owner/profile/conversation has
limited reviewed changes, deterministic decay, 30-minute idle/two-hour total
expiry and explicit disable/reset. Model text is never parsed automatically into
state. Reviewed model vectors use a strict authenticated review contract; Android
exposes explicit user-selected next-turn controls. No mood classifier or Phase 15
learning pipeline is added. Receipts retain fixed reasons/request IDs, not raw
psychological explanations. Android encrypted v8 retains v1–v7 and restores by
GET only. See [the policy](../docs/INTERACTION-PREFERENCES-AND-AFFECT.md).

## Phase 15 — selected evidence, reviewed defaults and exact-source continuity

Use a separate learning-v1 policy over unchanged v3/v4 baselines. Opt-in scoped
selected-source annotations, independent-interaction deduplication and explicit
review create wording defaults only. The configurable three-interaction gate is
conservative and evaluated on public synthetic HTTP cases; it is not proof or a
claim of optimal real-world preference accuracy. No automatic classifier/provider
pipeline is introduced. Explicit settings win; account reuse carries only enums
and needs both scopes' consent. Source-linked continuity selects original excerpts
through validated episodes, excluding generated summaries from ordinary chat.

Reset deletes live observations/proposals/defaults and suppresses every derived
reuse path; no learning index/cache exists. Minimal receipts keep keys, revision,
decision and original contributing observation identifiers for audit, without
quotes/values. Historical request snapshots remain immutable for existing retry/
replay contracts. The UI discloses this distinction; account-wide erasure/backups
and snapshot retention still require a selected policy. Android v9 encrypted
recovery preserves v1–v8 and restores by GET. Admin exposes aggregates only. See
[the implemented policy](../docs/INTERACTION-LEARNING-AND-CONTINUITY.md).

## Phase 16 — durable checkpoint plus bounded bearer SSE

Use additive 0013 attempt/event tables and reuse ChatService reservation rather
than change old Request enums, fingerprints or snapshots. Ordinary chat is a
separate streamable operation; old CLI/API and Phase 12 tool runs keep their
contracts. Terminal publication and owned Stop share row-lock order. Intent first
wins; delayed shutdown retains process admission. Instance/attempt fences and
startup/status/operator reconciliation prevent abandoned or late publication.

Observers are independent bearer-authenticated GETs with bounded replay and fresh
principal checks. Android uses a real OkHttp callback/flow transport with one-frame
buffer; leaving/backgrounding detaches only. Existing encrypted exact journal v9
suffices for GET-only recovery, avoiding a storage-format upgrade. Only canonical
terminal replies establish citations. Admin projects five metadata fields only.

Count limits cap durable private partial data. The 24-hour cursor access window is
not deletion; checkpoints/terminal history remain retained, and no account/backups
erasure policy is implemented here. Local HTTP iterator shutdown is observable,
remote Ollama GPU-stop acknowledgement is not. See
[the policy](../docs/STREAMING-AND-CANCELLATION.md).


## Phase 17: on-device-only ASR and explicit reviewed endorsement

Choose Android SpeechRecognizer.createOnDeviceSpeechRecognizer on API31+, with
installed-language preflight on API33+, rather than adding server ASR or a generic
recognizer whose privacy behavior differs. Default to the user's selected en-US.
No model download/network fallback/audio upload is implicit. Text stays available
on older/unsupported devices. Offline availability is a platform capability, not
an accuracy/resource/battery guarantee; validate the S24 FE separately.

Preserve generated original text in immutable voice lineage. Require review and
approved wording before a normal user-explicit event is created. Bind original
metadata into a separate request-fingerprint domain without altering plain text
fingerprints, prompts, retrieval or completed replay. Android encrypted v10
atomically consumes approval into the exact pending request. Restoration reads
only; TTS plays completed safe text with independent stop/focus/route handling.
Metadata describes the client-reported platform, not an attested ASR binary or
recording; no server audio hash exists. Retention is private durable lineage,
bounded at1000 owner records, with no deletion/erasure claim. See
[the policy](../docs/VOICE-INTERFACE.md) and its primary Android references.

## Phase 20 onward planning choices — 2026-10-16 — proposed, not implemented

The owner selected the existing Windows laptop kept plugged in and awake as the
initial availability target, and wants all three curiosity channels: active chat,
a later inbox and occasional initiated conversations/notifications. Implement
chat/inbox before durable scheduled delivery; channel/topic/hours controls and
consent remain explicit. This is not permission to enable live automation.

Password login should remove manual bearer handling from ordinary Android/admin
sign-in while retaining internal revocable sessions and legacy compatibility.
Private HTTPS fronts a loopback API; neither LAN/Tailscale identity nor a username
confers an ADA admin grant. Keep the existing retain-until-owner-deletion policy.

The proposal separates evaluation/relevance, public research, curiosity, host
supervision, durable schedules and bounded idle artifacts. An optional text LLM
is not a substitute for ASR/TTS; exact speech runtime/model selection awaits
measurement. Original conditional Phase 19 is not renumbered or declared complete.
See [FUTURE-ROADMAP](FUTURE-ROADMAP.md) for the phase graph and unresolved choices.

## Phase 20 recovery and validation boundaries — 2026-10-16

Use a separate `ada-postgres-legacy-0005-v1` tool/artifact for pre-upgrade protection;
keep current `ada-postgres-backup-v1` semantics at0015. Do not widen accepted heads
without reviewed table inventory, populated migration, source/replay and authority
quarantine tests. Unknown actual tables/owner models fail closed. Matching PostgreSQL
major versions are the conservative rehearsed policy; it is narrower than all
upstream-supported combinations. No migration/API/prompt/dependency upgrade is needed.

The legacy copy always remains isolated with unusable restored tokens. Old snapshots
cannot bypass newer erasure: reconcile an authoritative current ledger through the
current-format restore flow before serving; missing history is a blocker. No live
migration, restore, backup or service start was performed. No standalone0005 source
checkout exists in available history, so schema/forward replay evidence is not
misrepresented as an old-server HTTP run.

The proxy lab uses a per-process trusted test CA and explicit loopback addresses.
It does not establish Android system trust or remote deployment. `/admin` redirects
to `/admin/`; other server contracts are unchanged. The quality baseline freezes
public corpus digests and reports unassessed semantic grades honestly; fixture
precision/markers cannot establish personal usefulness or citation entailment.

## Phase 21 connection boundaries — 2026-10-16

Reuse the existing minimal unauthenticated readiness endpoint rather than add
discovery/private configuration. Check it without Authorization before native
credential establishment/recovery and browser admin sign-in; authenticate and
verify the owner/contract afterward. TLS/hostname validation remains per request.
Do not infer a unique VPN cause from generic network/browser errors.

Profiles are bounded local label/origin metadata, distinct from private encrypted
journals. Switching clears the old session; no credential is copied between
origins. Choose reviewed JSON metadata import for this phase; camera QR/deep links
are optional and add no needed capability to manual entry. Import cannot enroll,
authenticate, select silently or override trust. No schema/recovery format change.

Tailscale Serve terminates TLS before a loopback-only Caddy API/UI proxy accepting
the forwarded hostname. The alternative LAN TLS template has a safe loopback bind
default until a deliberate private address/firewall installation. Caddy admin API
stays off; controlled restart is required for selected file-based certificate
updates. No network membership/header grants ADA authority. Test-CA local edge
rehearsal is not proof of a real Serve daemon, ACLs or release Android system trust.

### 2026-10-16 — Phase22 password authority and session recovery

A distinct NFKC/casefold login maps to an unchanged owner UUID, assigned only by a
local hidden-prompt operator command. Argon2id uses pinned dependencies, a fixed
64MiB/3iteration/4lane profile and two concurrent hashes; generic failures use a
dummy verifier. Display names, old credentials and admin grants are independent.

Opaque digest-only access and rotating refresh families replace manual tokens in
normal client sign-in. Any consumed-refresh reuse revokes the whole family. Lost
responses/concurrent refreshes recover by explicit password sign-in, with no
plaintext escrow or replay grace.128families/4096rotations bound history, and
revoked history can be reclaimed at capacity so local reset remains usable.

Android v12 stores refresh material only in password mode and keeps access in
memory; released journals/advanced bearer mode remain compatible. Browser uses
exact-origin HTTPS host-only HttpOnly/Secure/Strict cookies with a custom CSRF
header. Auth operations are serialized (Web Locks across tabs where available).
Refresh clears private queries and revalidates roles; neither client auto-replays
private POSTs. Auth metadata/revocation remains available during content erasure.

The launcher ignores proxy headers entirely; behind a proxy, IP admission is
conservatively shared. Rate keys/counters are bounded process-local metadata; one
worker remains required. No forwarded identity, username or session grants admin.
Schema0016 backupv2 explicitly quarantines recovered password/session authority;
0015/v1 and separate0005 recovery remain supported. No live installation/enrollment.

Phase22 closeout refinement: authenticated X-ADA-Owner headers fence cross-tab
cookie account changes before response decoding/cache entry. Cancelled login
cleanup occurs inside the auth queue/Web Lock, before another login can replace
cookies, so a late cancellation cannot revoke the next account by mistake.


### 2026-10-16 — Phase23 explicit windows and optional context policy

Add separate versioned owner-only calendar-window reads rather than overloading
chat/point retrieval or silently treating a week as one instant. Version1 is
claim-only, valid-time overlap against current recorded corrections; document
availability and historical alias interpretation remain outside that version.
Require an explicit timezone/reference and clarify ambiguous local boundaries.
Return complete conflicting groups or omit the group, preserving exact support.

Retain v4 defaults and byte-identical old baseline text. V5 is an explicit audited
upgrade using the existing revision/retry fences and trace storage, not a schema
change. Rank original user/history and already-authorized original continuity
excerpts; generated summaries never become factual authority. Android links the
window lookup to existing reviewed corrections and annotates loaded proposal
repetitions without new automatic approval/write behavior.

A frozen public 8+8 comparison produced32native answers, exact evidence checks
and Codex qualitative review. Original-history gain is real within that case;
date-boundary/brevity regressions and overlapping small-sample intervals prohibit
a default-quality claim. Keep v5 opt-in. Matching supported embedding weights were
absent: fixture hybrid benefit does not justify native semantic activation.
No automatic downloads, private evaluation, later-phase work or deployment.
