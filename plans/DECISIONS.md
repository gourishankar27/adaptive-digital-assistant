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

### 2026-10-17 — Phase24 approved isolated public research

Keep research separate from chat/legacy tool execution as `ada-web-research-v1`,
using existing owned AgentRun/Step/Approval/Receipt rows. This preserves0016 and
the released recovery/erasure graph while retaining exact previews, immutable
source receipts and completed replay. Old protocol endpoints cannot execute new
research. New W citations avoid changing released origin/trust and M/D/C schemas.

Use a tiny, immutable Linux Docker broker with demonstrated OS/firewall isolation,
not a prompt filter or unrestricted in-process HTTP client. It receives only one
approved public request, narrow policy/budgets/expiry and opaque receipt metadata.
It receives no application secrets, history, memory, private DB/model access,
host mounts or Docker socket. Startup proof and exact source/image binding are
required; unavailable proof means disabled. Keep network admission separate from
shared local-model capacity and retain one server worker.

Choose a no-key English Wikipedia REST search after current primary-policy
review, plus a closed Python documentation URL pilot. Only Wikipedia receives
the operator-authorized public contact; show exact headers before approval and
enforce the recipient guard independently inside the worker. The first public
pilot mistakenly disclosed that header to Python too; this was reported, fixed
and regression checked, including corrected actual public requests. Do not store
the contact itself in versioned plans, logs or examples.

Prefer three total calls and zero automatic redirects to broad page/redirect
permission. Every follow-up needs matching new approval. Reject compressed bodies
rather than expanding the pilot's decoder attack surface. Validate every A/AAAA
answer, pin a public IPv4 socket and verify peer/TLS; IPv6 transport stays blocked.
Save bounded normalized extraction with explicit truncation, exact Unicode spans,
hashes/freshness/terms and untrusted provenance. Search snippets are not read pages.
Generate locally from saved public evidence, never use model output as authority,
and save only an explicitly requested imported-untrusted note. No automatic
personal fact, private-context export, scheduling, curiosity or later-phase work.

Reuse encrypted Android journal recovery, incrementing to v13 while preserving
old reads. Reserve exact UUID/payload before POST; GET-only restore and sticky
cancel prevent duplicate network effects or late UI restoration. Source hash/span
verification is independent on the client. Local isolation/public/native and
emulator results do not replace physical device, larger quality or operational
installation-host gates. Feature stays default-off; no deployment was authorized.


### 2026-10-17 — Phase25 owner-controlled curiosity

Keep curiosity opt-in and separate from factual memory and old chat contracts.
Use a bounded inspectable catalogue (30generic templates/five original-source
variants), broad task topic or explicit owner choice, and exact source-linked
uncertain follow-up. Do not claim model-generated personal insight. This avoids
hidden profiling/inference and permits concrete topic, repetition and premise
checks; wider naturalness/helpfulness still requires owner review.

Add owner-global policy, scoped question snapshots and minimal exact receipts via
0017, not overloaded expression/agent records. Serialize quotas/dedup under the
authenticated owner lock so scopes cannot multiply two normal inbox drafts/day.
Explicit per-question interview intent may bypass cadence within ten/day. Keep
old request fingerprints/prompts/source enums untouched; use versioned optional
navigation context and a new companion API after the actual answer. Opening an
inbox draft creates a conversation but no fabricated user event/request. Only
explicit typed answers use ordinary chat, outside the intent transaction.

New tables enter48-table erasure/60-table recovery. Version backup-v3 explicitly;
retain v1/0015 andv2/0016 artifacts. Verify original rows before disabling restored
curiosity/incrementing policy revision and quarantining all credentials. Copy
released lower downgrade preflight into0017 before SQLite DDL when crossing0016;
released migration files remain byte-identical. No live migration/restore run.

Off/pause, expiry and dismissal prevent stale premise delivery. Scrub dismissed
payloads; retain minimal dedup metadata30days and explicit suppression/receipts
until owner erasure. No inferred emotional, intimate, diagnostic or relationship
profile. Android v14 reads old journals and persists a bounded exact-operation
queue with a reserved off slot. The server receipt bound also reserves an off
slot; a full normal quota cannot force curiosity to remain enabled. Unknown
outcomes retain original keys, GET-only reopen and explicit retries. Late
identity/epoch/scope callbacks cannot restore private state.

Keep scheduler/push/lockscreen delivery unimplemented, notifications false, no
new GPU worker/budget, and one Uvicorn worker. Planning all channels is not live
notification consent. Existing admin views remain unchanged; only owners see
question/feedback metrics. Small public/native/emulator evidence is not real
owner-rated usefulness or release reliability. Stop at Phase25; no deployment.

## 2026-10-19 — Phase 26: owner-logon supervision and independent key recovery

Use native Windows Task Scheduler with InteractiveToken/LeastPrivilege for the
selected plugged-in laptop. A boot trigger cannot start login-dependent Docker
Desktop or prove provider GPU access. Keep pre-logon service setup as a separate
measured target. The supervisor owns only its API and optional pinned loopback
proxy; external Ollama/PostgreSQL remain operator-managed dependencies. Supported
foreground and supervised API entries share kernel/database admission ownership.
The advisory lock is session-scoped and committed before inference.

Keep local configuration, fixed receipts and DPAPI blobs in an owner/SYSTEM-only
installation directory, outside the private database recovery inventory. No new
durable operation table, migration, API or archive version is needed. Current-user
DPAPI supplies unattended access without a plaintext scheduler/env secret. A
separately passphrase-encrypted portable key capsule provides independent recovery
after losing that Windows profile; a copied DPAPI blob alone cannot do so.

Reuse the existing consistent encrypted snapshot, independent erasure ledger and
credential quarantine. Verify before advancing recovery receipts; no pruning or
retention change. Refresh the encrypted erasure ledger independently of model
work. Daily backup/26-hour alert are initial proposals pending representative
RPO/RTO measurements. One narrow OS backup trigger can later be reused/replaced
by Phase27; this phase adds neither that general scheduler nor dreaming.

Native isolated rehearsals and the authorized four-hour development soak are
distinct from installation, reboot/sleep, off-device recovery and a24-hour trial.
No production tasks or host policy were applied by this implementation.

The first long development attempt failed early. Native failure injection then
confirmed that an ordinary Windows metadata reader can deny atomic replacement.
Use unique receipt temporary files and a bounded3-second sharing retry, preserving
the previous complete receipt on persistent failure. Keep safe stage/counter/error
type diagnostics in the rehearsal so a later failure does not erase its evidence.
A short corrected fault test does not substitute for the still-open four-hour gate.

## 2026-10-19 — Phase27: reviewed schedules and foreground inbox delivery

Phase26's separately authorized continuous rerun subsequently passed its four-hour
development gate; installed-host and sustained native-inference gates stay separate.
Use that source prerequisite without installing a task or changing the live service.
One lightweight API-owned dispatcher handles only typed reminders and existing
catalogue questions; retain the OS backup trigger as its sole backup owner. No
reflection handler, external-person message or model/GPU daemon is introduced.

Choose authenticated foreground in-app polling for this phase. No cloud wake-up
provider, device registration, notification permission or lock-screen text is
enabled. Durable inbox acknowledgement is at-least-once transport recovery, never
proof of delivery/read or exactly-once push. Opening explicitly creates/resumes an
owned conversation with no user message or automatic inference.

Pin tzdata2026.5 across operating systems and save finite reviewed UTC plans.
Require explicit fold/gap decisions, same-day allowed hours, expiry and latest-only
catch-up. Keep reviewed-plan generations distinct from execution generations so
edit/snooze after a backward clock step cannot skip a new plan. Enforce independent
durable owner grants and current metadata authority before private background reads,
then recheck before publication. Session logout/refresh differs intentionally from
device revocation/password reset/all-session stop. Owner consent/global dispatch
default off; turning consent on alone does not reactivate paused schedules.

Add unreleased0018 and five private tables to full owner-content erasure and
versioned backup-v4. Verify original backup hashes before restore quarantine;
preserve old formats and released migrations. Bound retained schedules/occurrences/
inbox/receipts and exact encrypted client operations; reserve an off slot and fail
closed at capacity. No implicit pruning or factual-memory extraction is added.
Admin sees only fixed aggregate state/error metadata through the existing grant/
audit boundary. Actual local checks and remaining device/host limits are in STATUS.

Final review reproduced representable-date overflow through both database/API
fixtures. Normalize calendar arithmetic/offset overflow to the existing422
calendar-validation result without reserving an operation. A supervised wiring
test also exposed an unnecessary provider/quiet-period dependency inherited from
the consolidation gate. Inbox/catalogue publication now has its own fresh-DB/
resource gate; existing inference/consolidation health and quiet gates remain.
These bounded corrections follow the frozen full run and have a separate final
scheduling/host regression record rather than being attributed to that earlier run.


## 2026-10-21 — Phase28: bounded review jobs and a smaller initial job set

Reuse the Phase27 dispatcher and Phase13 worker/admission slot. Idle means
absence of authenticated ADA foreground activity, not screen/keyboard monitoring.
Use the existing host observer's fresh measurements; never run a potentially slow
sensor subprocess inside an owner transaction or while reserving inference.
Unknown safety skips work. Recheck durable origin consent, epoch, policy and
source metadata before private payload and before publication. Charge reserved
unit time conservatively; hard UTC-day caps survive timezone changes/restart.

Initial enabled classes are rule-based reports and existing catalogue question
drafts. They create no factual claim, preference, source correction, automatic
proposal or external action. Generated episode support reuses Phase13 schema and
Keep, but model summaries stay separately disabled: a public native adapter
cancellation return is not proof of server GPU cancellation, useful summaries or
acceptable foreground inference interference. The plan explicitly permits a
smaller job set when capacity evidence is inadequate. Do not bypass safety rows.

Deterministic source-set/policy/kind IDs exclude transient day/revision values;
unordered policy choices are canonicalized. Old attempt/lease outputs are fenced,
finite retry preserves IDs, and capacity suspends visibly rather than pruning
retained history. New private tables join explicit erasure/backup-v5; restore
pauses grants/queues and invalidates model attestation. Non-content provider
suspension survives owner erasure. Admin receives fixed aggregate metadata only.
Android journals exact operations before HTTP, retains old formats, and restores
with GET receipts only. Earlier prompts/replays/migrations remain unchanged.


Final review keeps owner-wide question-template metadata in the private artifact
row even when its text is discarded, with a native uniqueness backstop. It joins
owner erasure/backup and exposes no new admin/private text. Opening compares the
created catalogue question to the reviewed draft and rolls back on change.
A post-selection foreground check stops dispatch, running reflection joins the
existing deletion quiescence guard, and provider metadata streaming obeys the
same cancellation/deadline budget. These late corrections have a separate
post-broad-run validation record; the full-suite result is not relabeled.


## 2026-10-22 — Phase30 explicit work and deterministic briefs

The owner selected balanced personal commitments and development projects.
Explicit structured goals/tasks are owner commitments with immutable revisions,
not claims or retrieval evidence. Requested chat Save starts a blank editor and
pins the original generated reply; review does not change its trust. Due dates
are calendar metadata and never imply completion or a scheduled event.

The first project/day brief deterministically projects selected task revisions,
changed field names, due grouping, overdue/unknown state and reauthorized original
pins. This satisfies the selected-work outcome without a new synthesis authority,
provider call or background process. T-labels navigate work; immutable chat replay
and factual citations stay separate. Calendar rule versions and resolved instants
bind preview/cache, and snapshot flags retain their original calendar interpretation.

All work writes are exact owner-reviewed operations with encrypted client recovery.
Existing owner/scope locks fence revisions; restore includes the new inventory and
quarantines automation. Optional25 question drafts and27 reminder confirmation use
existing consent, never a tool inference. Editing work pauses its linked question
and reminder; generic schedule reauthorization cannot revive completed work.
Admin remains monitoring only. New head0020 and backup-v6 preserve earlier released
migrations/formats. Human usefulness/physical accessibility remain verification
items, not fabricated acceptance results. Phase31 is outside this implementation.
