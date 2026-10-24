# ADA architecture decisions

## Phase32 long reviewed voice and persistent local wake

Migration0022 adds `long_voice_inputs`, bringing the inventory to77 tables and64
owner-content tables. Backup-v8 adds its full narrative/lineage; v1–v7 readers and
released migration history remain. New capability `ada-long-reviewed-voice-v1`
gates additive POST long-voice-requests/GET long-voice-input. Existing paths and
DTO schemas are unchanged except the additive capability field. Actual duration,
ordered immutable generated segment IDs/hashes/model metadata, separately reviewed
words, exact Unicode context span, style and epoch bind the atomic request.
Only the chosen <=4,000-character excerpt enters model context and ordinary event
evidence; the retained <=32,768-character story is not auto-indexed as fact.
Fixed conversation style is budgeted before model inference outside transactions.
Original prompts, source trust and completed replay remain frozen.

Android27/journal19 retains v1–v18 readers. App-owned AudioRecord feeds a bounded
2s queue and pinned streaming native decoder; endpoints commit internal text,
never finish capture. Checkpoints are Keystore-encrypted before acknowledgement.
Explicit release/Stop drains queued frames; explicit Send reserves exact approved
input before HTTP. Limits/failure are visible; no raw-audio file/upload/default
cloud processing. Optional asset-only installation verifies every pinned byte;
ordinary builds have no added native/model payload. Native release builds remain
blocked on redistribution/target acceptance. Neural playback uses bounded chunks,
explicit voice choice and the existing independent audio/generation Stop boundary.

An unexported microphone foreground service is armed only from a visible verified
conversation. A process-local grant carries no login secret. A shared coordinator
serializes UI/service renewal through atomic encrypted compare/replace, marks an
unknown outcome before HTTP, verifies owner/epoch and never replays a consumed
refresh. Access remains in memory; visible UI owns rotation and resume joins any
background rotation before restoring private views. Logout joins renewal before
revocation/cleanup. Every30s, the service verifies authentication and owned
conversation metadata; failure, expiry, logout, scope/epoch/family change and audio
loss stop/revoke listening. Wakes only cue/Open ADA; unlock/current auth precedes
private access. No boot restart, default-assistant role or private locked speech.
Native wake reliability remains under investigation, not an accepted capability.
See [usage and validation](PRIVATE-VOICE-CONVERSATIONS.md).


## Shared Android voice composer

Android app26/0.31.1 shares the message editor with reviewed voice drafts. Tap controls
and physical hold/release both retain the on-device ASR boundary. Provisional
partial text stays in memory and is never submitted. Final recognition retains
its original transcript ID/content, while typed-prefix and subsequent edits form
the reviewed wording. Explicit composer Send saves an approved encrypted draft,
then consumes it into the exact pending journal before HTTP on the existing
reviewed-voice route. It never falls back to a plain authored-text request.
Capture/release/edit/recovery do not approve or send. Gesture leases fence late
release/cancel, and existing identity/scope/lifecycle/storage fences remain.
Schema0021, OpenAPI and journal18 are unchanged.

## Phase31 PDF projection and selected19A drafts

Head0021 adds nullable extraction metadata and two owner-content device tables:
76 installed tables,63 owner-content, backup-v7. Old migrations and v1–v6 recovery
are retained. PDF original/extracted hashes, page/code-point maps and parser/image
identity are frozen at atomic publication. One secret-free, network-disabled,
resource-limited Docker worker parses outside transactions. Owner/principal is
rechecked before reservation/publication. Failed/processing text is not retrieved.
Old text/Markdown requests, prompt snapshots and completed replay are preserved.

The optional Android isolated UID receives only a model FD and explicit prompt.
Owner/device P-256 signatures bind exact scoped generated proposals, source pins
and monotonic sequence. Reads revalidate sources, privacy epoch and revocation.
Android journal18 encrypts before HTTP and restores with GET only. Restore retains
content and revokes device registrations. Drafts cannot create factual memory,
chat events, tool approvals or server replies. No private admin reader is added.
Both measured models failed quality: UI activation stays disabled, normal builds
omit JNI/weights and edge_inference=false. See [PDF](PDF-INGESTION.md),
[runtime limits](ON-DEVICE-DRAFTS.md) and dated STATUS/WORKLOG for actual checks.

## Phase30 explicit work and selected briefs

The current source adds four owner-content tables after0019: WorkItem,
WorkRevision, WorkReceipt and WorkBrief. Head0020 has74 tables,61 owner-content,
and backup-v6; released migrations and older backup formats are retained.
Owned scope/owner locks serialize revisions and operation receipts. Review hashes
bind owner, scope, epoch, item, expected revision, exact fields, source pins,
parent revision, resolved due instant and timezone rules. No model/network call
occurs in this path. All writes revalidate the current principal in transaction.

A requested chat draft pins its original completed reply, without promoting
model/imported text to fact or automatically adopting a commitment. Tasks never
enter the factual retrieval inventory. An owner-requested brief deterministically
projects selected task revisions and authorized original sources; T-labels are task
navigation. Cache keys include owner/scopes/epoch/revisions/calendar rules and
overdue state; immutable snapshots retain status and day flags, while source reads
are reauthorized. Completed chat replay is not rewritten.

Optional task questions use Phase25 consent/cadence; only Phase27 can schedule a
reviewed reminder. Task edits pause linked pending questions/reminders. Generic
schedule confirmation and reauthorization cannot bypass task revision/status
bindings. Restore quarantines automation and credentials, preserving work/history.
Android24/journal17 retains exact encrypted operations and checks GET on reconnect;
late owner/selection/lifecycle results are fenced. Admin gains no private reader.
The balanced personal/development focus and deterministic brief choice are detailed
in [the guide](PROJECTS-AND-FOLLOW-THROUGH.md) and plans/DECISIONS.md. Phase31 remains
planned; this source was not deployed.

## Phase29 local speech study boundary

Android23/0.29.0-speech-study retains platform-only ASR and offline TTS. Versioned
local adapter/task/model-status metadata, public preview and a strict pinned
manifest/byte checker add no server capability, native dependency or installer.
Verification of a bundle cannot grant activation. A separately reviewed catalogue,
license/transitive inventory, compatible runtime and measured physical device gates
are prerequisites for any future adapter. No model is selected or redistributed.
Preview is authenticated-context/foreground/navigation fenced and uses the existing
audio focus path; it sends/saves nothing. Voice selection avoids an implicit
different-language fallback; playback rechecks system voice availability and fences
old utterance errors. Original ASR/review lineage, encrypted journal16, schema0019,
OpenAPI145paths/193schemas, prompts and completed replay remain unchanged. See
[the study, installation design and target protocol](NATURAL-LOCAL-SPEECH.md).


## Phase28 bounded idle review

Current source requires0019 /70 tables and exports145 paths /193 schemas.
Four owner-content tables hold reflection policy, exact receipts, leased runs and
typed artifacts; inventory57 joins explicit erasure and encrypted backup-v5.
A fifth table contains only a model fingerprint/safety suspension, preventing
owner erasure from clearing an ignored-cancellation ban. Restore verifies original
hashes first, then pauses grants/queues and invalidates model attestation.

The Phase27 dispatcher selects deterministic bounded source-set/policy/kind IDs;
the existing consolidation worker consumes idle units after explicit work. There
is no second scheduler or inference process. Fresh host-observer readings are
sampled outside owner transactions and the model slot. Unknown safety state skips
work. Global switches, origin/consent/data epoch, idle window and source metadata
are checked before private input and again before publication. Foreground activity
requests cooperative cancellation; the existing semaphore stays held until actual
provider return. Resource/deadline checks, finite attempts, quotas, source pins
and generation/lease fences reject late output.

The initial rule-only class reports owner-marked open items and possible differing
endorsed statements, and prepares Phase25 catalogue questions. Exact owner review
can keep a report, explicitly open a question, discard, or (when separately
validated) keep a generated summary through Phase13. No claim, preference, source
or external action is automatically changed. Summaries remain disabled after the
bounded native probe; client return timing is not proof of GPU cancellation or
usefulness. Old prompts/completed replay and existing API contracts stay intact.

Android22 uses encrypted journal16, v1–v15 reads and GET-only recovery of exact
operations. The read-only admin route uses the existing grant/audit boundary and
fixed counts/budgets only. See
[the detailed guide](IDLE-REFLECTION-AND-DREAM-REVIEW.md) and dated STATUS/WORKLOG
for actual evidence, skips and target limits. No installation/deployment occurred.


## Phase27 durable scheduling

The Phase27 milestone required0018 /65 tables, exports138 paths /181 schemas and adds
five private tables: scheduling consent, schedules, occurrences, inbox and exact
operation receipts. They join53-table owner-content erasure and recovery-v4;
released0001–0017 and v1/v2/v3 restore remain supported. Restore verifies original
archive hashes before disabling consent, quarantining schedules/credentials and
fencing pending leases. Old prompt snapshots and completed replay are unchanged.

One API-lifespan non-inference dispatcher claims bounded typed reminder or existing
catalogue-question jobs. There is no Phase28 handler, model/GPU process, external
message channel or parallel backup scheduler. Global enable and owner consent
default off. Explicit finite plans record pinned IANA rules, UTC occurrences,
fold/gap choices, quiet hours and expiry. Latest-only catch-up avoids backlog floods.
Owner locks, origin/epoch/source checks, generations, deterministic occurrence IDs,
leases and exact receipts fence concurrent/crashed/late workers. Background checks
validate metadata authority before loading private payloads and before publication;
no network inference runs inside a scheduling transaction.

Durable consent is independent of an ordinary expiring password-session family.
Origin-device revoke/rotate/expiry and legacy rotation pause corresponding grants;
password changes/all-session revocation pause automation and disable consent.
Owner off and explicit reauthorization remain separate. Source hashes/quotes and
scope are pinned at preview, confirmation and publication. Owner reads use MVCC
without unnecessary scope-write locks; paged history/client caches are bounded.

Inbox commits before client acknowledgement. Explicit open creates/resumes an
owned conversation and never fabricates a user turn. Android v15 journals reserve
exact writes before POST, retain v1–v14 compatibility, and recover with GET only.
Foreground polling is the sole enabled notice mechanism; background push and
lock-screen delivery are unavailable. Admin receives fixed aggregate counts and
loop/error metadata through a server-granted, audited read-only route. See
[the scheduling guide](DURABLE-SCHEDULING-AND-REMINDERS.md) and STATUS for actual
checks, remaining device/host gates and the no-deployment boundary.

Earlier sections describe their dated milestones, not the current schema total.

## Phase26 local Windows operations

The selected startup boundary is Task Scheduler2.0 under the current interactive
owner, LeastPrivilege, using the pinned Python environment. Plan mode emits XML;
installation is separate. A supervised API child owns both a kernel file lease
and a PostgreSQL session advisory lock, committed before inference. The supported
foreground script uses the same ownership gate. Recovery fences abandoned requests;
completed replay, stream instance fences and existing job leases remain unchanged.
Optional pinned Caddy is an owned loopback child; API shutdown drains first. A
Windows Job Object contains only assigned children on supervisor death. External
Ollama/DB/Docker/Serve processes remain outside that ownership.

Host observation separates process/HTTP liveness, DB/schema readiness, provider
installed/resident metadata and backup/ledger freshness. No health probe warms a
model. Supervised discretionary consolidation respects server-observed foreground
activity and AC/disk/RAM/thermal pressure; unknown sensors remain unknown. Empty
polls do not acquire inference admission. There is no new inference process,
notification scheduler, dreaming behavior or automatic factual-memory write.

No server table, HTTP route, capability or migration is added: schema0017/60tables,
OpenAPI126paths/168schemas and released recovery-v3/v2/v1 remain. New local files
are protected **operator/security metadata**, not ADA owner evidence: selected
Windows SID/profile/path configuration, fixed supervisor/backup receipts, task XML,
DPAPI key blob and encrypted latest erasure ledger. Existing database backups stay
outside source erasure under the disclosed operator policy. None of these files
contains plaintext credentials, private messages or source quotes; secrets/ledger
payloads are protected/encrypted. They grant no HTTP/admin permission.

The unattended secret-provider function uses current-user DPAPI. A separately
passphrase-encrypted portable capsule recovers its random key independently of
Windows. Backup success requires the consistent dump plus a sufficiently fresh,
consistent post-snapshot ledger and read-back/hash checks. Latest verified state
advances atomically; failures preserve older points and pruning remains off.
Protected-key restore targets only a new isolated database and retains credential/
curiosity quarantine. An uncertain or out-of-date erasure ledger cannot justify
re-enabling recovered access. Source retention remains explicit-owner deletion.
See [the operational guide](ALWAYS-ON-OPERATIONS.md) for bounded retries, crash-stop
reset, power opt-in, RPO/RTO selection and target gates. No live deployment occurred.

## Android Ambient Intelligence presentation

The 2026-10-18 redesign retains MainActivity, existing ChatDestination values,
ChatViewModel/controllers, HTTP adapters, capability gates and encrypted stores.
Theme/component layers own colors, scaled typography, bounded layouts, insets and
state-derived visuals; they own no private network/persistence/business actions.
Compact bottom navigation and expanded scrollable rail share the same four
destinations. AdaPresence uses existing recording/playback/request/tool state,
with explicit unconfirmed/offline/error semantics and no invented amplitude.
Motion is lifecycle/viewport/system-animation gated. Fresh-install appearance is
dark violet; earlier persisted palette and mode choices remain available unchanged.
No backend, schema, snapshot, request or journal contract changes. Test-host
captures contain synthetic data and do not disable production FLAG_SECURE. See
[the audit/guide](ANDROID-UI-REDESIGN.md) and dated validation evidence.

## Phase25 opt-in questions and private inbox

Migration0017 adds owner-global curiosity policy, owner/scope-bound question
snapshots and minimal exact-operation receipts. These are private content in the
48-table erasure/60-table recovery inventory. All prior migration bytes remain.
New backup-v3/0017 preserves original row hashes before credential/curiosity
quarantine;0015/v1 and0016/v2 recovery remain supported. Restored curiosity is off
until fresh owner consent. No live migration or deployment was performed.

Curiosity defaults off. Explicit controls cover five topics, personal depth,
cadence and chat/inbox channels. One catalogue companion is allowed per completed
reply; two normal inbox drafts/owner/UTCday across scopes, ten explicitly requested
interview questions/day, owner-wide dedup and permanent suppression. A bounded
inspectable catalogue avoids hidden inference/dossiers. Personalized follow-up
requires an exact accessible original pin; quotes remain untrusted and potentially
stale. No model text supplies permissions, topic consent or factual memory.

Companions use a separate versioned API after the actual answer. Drafts are not
assistant chat events. Explicit opening atomically creates a conversation without
inventing user text; answering records only the typed ordinary owner statement,
using existing request UUID/fingerprint/replay. No auto-claim or preference update.
Versioned optional navigation context is source/policy-bound and fits only within
the existing whole prompt budget. Old prompts, response contracts and request
messages remain exact. Network inference occurs after intent transactions commit.

Android journalv14 preserves v1–v13 reads and an encrypted bounded operation queue,
including a concurrent global-off intent. GET-only reopen, exact retries, receipt
binding and identity/epoch/scope fences prevent duplicate or late private display.
Receipt storage reserves a final slot for global off. Dismissed draft payloads are
scrubbed; minimal dedup metadata has a disclosed30day lifetime. No timer, push,
scheduler, private-profile extractor or new admin private view was added. See
[the guide](CONVERSATIONAL-CURIOSITY.md) and dated STATUS for actual local results,
refresh intermittency and remaining physical/quality/release gates.

## Phase23 bounded answer context and calendar windows

Schema remains0016. Existing v3/v4 prompts and API path contracts are preserved;
v4 stays the new-chat default. An explicit owner-authenticated, conversation-locked
quality upgrade audits v5 and increments revision using existing PromptChange.
Failed retries cannot cross that revision; completed replay retains original
messages/evidence. V5 ranks original user history and already-authorized original
continuity excerpts within existing byte/candidate bounds. Generated summaries
never become factual evidence. Selection/omission metadata is frozen in the
existing trace and exposed through a new owner-only diagnostic read.

Separate versioned calendar resolution/window APIs require timezone and reference,
use whole half-open valid-time overlap against current recorded state, and return
clarification for ambiguous/missing local boundaries. They never reinterpret old
point APIs or change chat input/recovery fingerprints. The claim-only window path
filters owner/scope/time before selection, revalidates exact support and returns
complete conflicting groups or omits the group. Android provides read-only bounds,
source/correction links and explicit v5 confirmation; loaded proposal grouping
does not approve, suppress or merge review operations.

Public native v4/v5 comparison found context benefit and date/brevity regressions.
V5 remains opt-in; absent supported embedding weights leave semantic disabled.
No migration, dependency, background worker or deployment was added. See
[the measured policy and interfaces](ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md).

## Phase22 password authority and transport

Schema0016 separates normalized login/password verifiers from owner display names
and legacy credentials. Password login creates revocable digest-only access and
rotating refresh families. Owner locks serialize reset/rotation/reuse; expensive
Argon2 work runs outside transactions under a two-slot bound. Exact pre-auth POST
routes have independent admission/body limits; every private route and outgoing
SSE batch retains fresh owner authentication. One worker remains required.

Android v12 journals store refresh material only in password mode, access in memory,
and preserve v1–v11 reads. HTTPS browser sessions use host-only Secure/HttpOnly/
SameSite=Strict cookies and exact-origin/custom-header CSRF; the advanced bearer
adapter remains separate. An authenticated owner header fences cross-tab cookie
account switches; cancelled auth cleanup stays inside the serialization boundary.
Monitoring permissions still come only from current
admin grants. Refresh/401/epoch/account changes clear private caches; private POSTs
are never automatically replayed. New encrypted backupv2 covers57tables;0015/v1
and separate0005 recovery remain supported. Restore disables recovered passwords
and sessions before explicit operator recovery. See
[PASSWORD-LOGIN-AND-SESSIONS](PASSWORD-LOGIN-AND-SESSIONS.md).

Current source: schema **0016**, with private chat/memory/documents, reviewed tools,
consolidation, preferences/continuity, streaming, Android voice and security/
operations. Phase 20 adds recovery/evaluation tooling and readiness evidence;
it does not install the application or implement later roadmap features. Dated
phase sections below retain their original validation and installation boundaries.

## Deployment

Phase21 adds no server route/schema/prompt change. Android stores up to12 named
HTTPS origins separately from encrypted private state; explicit selection clears
the previous login and never auto-connects. Reviewed version1 JSON imports carry
only a label/origin. The native me/recovery and web admin sign-in paths first use
the existing unauthenticated readiness endpoint, without sending a credential;
TLS/origin validation still applies to every subsequent request. Native TLS and
DNS errors are distinct; generic/browser errors do not prove a specific VPN cause.

Private route templates select Tailscale Serve → loopback Caddy18764 or directly
bound LAN Caddy HTTPS. API/PostgreSQL/Ollama stay private, admin uses same-origin
relative requests, and network headers confer no ADA authority. LAN Caddy defaults
to loopback until deliberately configured. Laboratory Caddy/ADA/SSE and emulator
negative-TLS checks do not enroll VPNs or establish release system trust/renewal.
See [PRIVATE-NETWORK-CONNECTIVITY](PRIVATE-NETWORK-CONNECTIVITY.md) for execution
steps and remaining target gates. No Phase21 deployment occurred.

Separately authorized local operation on 2026-10-16 freshly verified the configured
Docker PostgreSQL17.11 database at head0015 (54tables), with no pending migration.
The loopback API, Ollama and built admin preview were started and checked against
it; existing accounts/credentials/history were preserved. This is ordinary local
process hosting, without a Windows service, remote HTTPS or supervised restart.
See [Windows database administration](DATABASE-ADMINISTRATION-WINDOWS.md) and
[STATUS](../plans/STATUS.md) for commands, evidence and remaining release gates.

One Windows host runs the Python API, Ollama, and PostgreSQL. One Uvicorn worker
serves multiple users. The API limits in-flight inference with a process-local
semaphore. Excess requests get 503; clients retry with jitter and the same UUID.
This is bounded admission, not a durable job queue. Do not increase Uvicorn workers
until admission control is shared across processes. Other applications calling
Ollama are outside ADA's limiter. Model warming/partial CPU placement need local
measurement; no performance claim is made.

## Authority and personalities

The backend owns users, profiles, conversations, evidence, and request state.
One user can have multiple personality profiles. Profiles share model weights but
not message history. A conversation snapshots personality fields and the baseline
prompt version. Personality is expression configuration, never an authorization
principal. Owner IDs come from authentication, not input JSON.

Every conversation references an authorized personal/project scope. Migration 0002
creates scope records from the original conversation scope IDs. Multiple conversations
can use an owner's project scope while retaining separate histories and personalities.
Shared scopes and membership grants remain deferred. Client scope IDs
are checked against authenticated ownership before a conversation or memory write.

## Storage

PostgreSQL is authoritative. SQLAlchemy uses composite ownership foreign keys for
personality/conversation/request/event links. Application reads always include the
authenticated owner on private user routes. The explicitly granted admin metadata
routes select a separate fixed metadata allowlist across owners. This is application-enforced isolation with database integrity
constraints, not PostgreSQL row-level security. The database administrator and server
operator remain trusted. RLS is a future defense-in-depth decision before a less
trusted deployment.

Alembic migrations 0001–0015 are released snapshots. Add new migrations; never
replace them with `Base.metadata.create_all()` at server startup. Migrations are explicit.
Events and evidence versions are append-oriented through application code. This release does not install
database triggers preventing operator edits. Trust labels distinguish user words
from model output. Automatic claim extraction remains deferred.

## Explicit memory

Every chat event is recorded with a source/version in the same transaction. User
notes can also create evidence without inference. Migration 0002 backfills existing
events without changing their IDs or turning them into claims. Versions preserve
exact content, SHA-256 and the inherited user/model trust label.

Claim writes require one exact nonblank user span in the same owner/scope. The
server computes the quote/hash. Subject/predicate/value are an explicit user
annotation, not a model-verified fact. A mandatory composite source-version foreign
key ensures a stored claim has existing evidence. Temporal intervals, replacement
links and ownership also have database constraints. See PHASE1-MEMORY.md.

All memory writes lock the scope row on PostgreSQL. Idempotent replay uses the same
ID and canonical write hash. A different ID for an identical claim is a conflict.
Corrections insert the new claim and close/link the old one atomically. Current and
historical queries use both validity bounds, including future-dated replacements.
The explicit writer never calls a language model inside or outside its transaction.

One original user evidence version supports an explicit claim. Phase 09 adds scoped
canonical identities/links; Phase 11 adds reviewed endorsements with separate
original support. Sharing, general semantic validation and contradiction
resolution remain deferred. Retrieval conservatively groups different valid values
in the same normalized subject/predicate slot. The database/server operator is trusted; API immutability and
hash checks do not prevent an administrator changing the database.

## Request state machine

New -> running -> completed or failed. A failed request may become running with an
incremented attempt. A client UUID is unique within its owner. Reusing it with other
content, time/retrieval options or another conversation returns 409. Completed
retries return the saved response and citation cards. Provider failure is an explicit
502 with a sanitized code.

The reservation transaction locks the conversation and checks its active request.
A shared lock on the owned scope protects retrieval/conflict checks from concurrent
memory writes. Request, input messages, user event and retrieval trace commit together.
A partial unique index permits only one running request per conversation. Model
inference happens outside a database transaction. Completion locks conversation,
then request; validates the attempt; writes response, assistant event, and revision
atomically. Operator recovery updates old running requests to failed. A late attempt
cannot complete after that state change or after a retry changed the attempt.

Crash cases: before reservation -> no request; after reservation -> explicit
interrupted request for recovery; after completion before delivery -> the same ID
returns the stored answer. Model computation may repeat after a crash. This is not
an exactly-once external side-effect mechanism. Phase 12's separate read-only runs
have their own intent/approval/receipt protocol; general external writes remain absent.

## Context

System baseline + frozen personality + runtime memory/time policy + selected complete
user/assistant pairs + selected untrusted memory JSON + current input. Failed requests
remain inspectable evidence but do not become dangling model history. Evidence is
reserved within the whole UTF-8 byte budget before complete history pairs. Oversized
groups/pairs are skipped; smaller entries may fit. Exact quotes are never truncated.
This is a conservative bound, not provider-tokenizer precision or long-term memory.
The adapter sets an explicit Ollama context window/output limit. A real model test
must confirm token use and latency. No summary is silently substituted.

The adapter receives only the selected conversation and its authorized scoped evidence.
Ollama has no ADA user state;
each call sends full selected messages. Clients never supply system roles. The model
is not a security boundary. General external/network tools are absent; the separate
Phase 12 registry supports calculator and owned memory/source reads. Permanent claims are written
only through authenticated, explicit memory operations; chat has no memory tool.

Migration 0003 backfills the rebuildable search projection and adds PostgreSQL GIN /
SQLite FTS5 indexes. Lexical and normalized subject channels apply owner/scope/time
filters before returning candidates. Source hashes, trust and spans are checked
again before context selection. Current and historical retrieval share Phase 1's
valid-time semantics. See PHASE2-RETRIEVAL.md for ranking, caps and conflict rules.

New conversations freeze baseline v4. An explicit v1/v2/v3 prompt upgrade archives the old
and new prompts, preserves the personality snapshot, locks the conversation and
rejects in-flight changes. It increments the conversation revision so failed requests
with old context cannot be resumed. Completed retries retain their original answer.
Unupgraded v1/v2 conversations continue with their original prompt and no retrieval;
v3 continues claim retrieval. Document retrieval requires v4 and explicit opt-in.
Failed retries retain the original messages and selected evidence, even after a
memory correction. New requests retrieve again. Response labels map only to the
current request's selected source snapshots. Labels cannot authorize a source, and
source mapping does not verify the model's generated claim.

## Security and observability

Local administration issues 256-bit random bearer tokens and stores hashes. Tokens
are revocable by rotation. Phase 18 adds digest-only owner device enrollment,
rotation/expiry/revocation with enrollment disabled by default. Passwords, public
signup and OIDC are not implemented. Use HTTPS/encrypted transport for remote clients. Keep Ollama and
the database inaccessible to clients. CORS is not enabled. No secrets or request
bodies are intentionally logged; start script disables HTTP access logs.

Durable request state includes model/provider, input messages, attempts, timestamps,
error category and token counts. Retrieval traces snapshot the planner, prompt version,
authorized candidates, selected claim/source/span/hash/quotes, budget and duration.
The authenticated request/trace routes expose only their owner's records. Legacy
requests have no reconstructed retrieval trace. These contain private conversation
data: protect database/backups.
Snapshots and rejected/failed requests currently have no automated retention policy.
There is no public deployment, security certification, or high-availability claim.

Phase 05 migration 0004 adds grants defaulting absent, a fixed-field rolling audit
and indexed monitoring filters. Local UUID-based grant/revoke commands atomically
audit changes under a singleton audit-state lock. Admin reads use existing bearer
authentication, fresh grants and a pre-response audit/recheck, including in-flight
revocation. Normal private routes never bypass owner checks. The trusted local
operator has a reserved audit actor ID; HTTP audit actors are authenticated user IDs.

Monitoring selects columns/JSON scalar counts rather than private ORM snapshots.
It preserves composite owner/request identity and unrecorded metrics as null.
Polling, query windows, pagination and audit rows/age are bounded. Provider model-list
probes are serialized/cached, response/time bounded and run outside DB transactions;
they never generate. Current readiness validates supported head 0016. Admission shows the
actual process semaphore, with one worker; GPU/throughput remain unknown. See
[ADMIN-MONITORING.md](ADMIN-MONITORING.md) for allowlists, failure/audit semantics,
retention and installation. Phase 05 introduces no account impersonation.

## Admin web monitoring (Phase 06)

The React SPA in `apps/admin-web` serves under `/admin` and reads the six existing
same-origin `/v1/admin` endpoints. AdminSession verifies admin-me before enabling
queries. The live HTTP adapter holds the bearer token; submission clears the entry
field. No credentials or query results are persisted. Only enum-valued appearance
preferences (Oxford Blue/default, Dark Red, Olive Green; brightness/text size) use
localStorage. Reload requires operator sign-in again.

Query identity includes server, verified principal, session epoch, filters and
both request owner/request UUIDs. Logout, identity change and 401/403 abort pending
reads, clear metadata and fence late results. The server remains the permission
authority on every read. Ordinary private APIs are unchanged. Runtime projection
accepts only metadata fields and decodes int64 times as bigint, even when a future
response adds private fields. Request/detail/audit text is rendered literally.

Overview shows server counts and token coverage; Providers shows reported limits
and generation-free health; Requests uses server pagination/filters; Detail shows
recorded timeline/retrieval budgets with explicit missing legacy values; Audit
shows fixed-field role/read events. No chart is synthesized from counts. Metrics
have units and observation/last-success times. Unknown, zero, unavailable and
degraded states stay distinct. Transient errors mark retained values stale;
authentication loss removes them. Views poll at 30 seconds only when visible,
with no automatic retry or background refresh. Retry-After establishes a session
cooldown across view changes and manual refresh. Cache entries expire on unmount.

Native controls, labelled horizontal table regions, stable refresh focus, palettes
with light/dark/system modes and text sizing support keyboard/narrow/zoom layouts.
The same-origin local build smoke uses Vite preview with a fixed `/v1` proxy.
HTTPS static hosting with `/admin` fallback requires a separately selected setup;
no deployment or operational write control is part of Phase 06. Server OpenAPI,
schema, admission, snapshots and provider behavior remain unchanged.

## Mobile compute split (future)

Phase 03 adds typed OpenAPI output/error contracts and independent Android/web
connection foundations in `apps/`. Their injected transports call authenticated
ADA HTTP endpoints. No admin authorization, mobile chat, enrollment service,
streaming, cancellation or persistent client token storage is added in this phase.
The Android secure-storage interface is a boundary for Phase 04; the web bearer
credential remains in memory. See `contracts/README.md` and each app's README for
transport/state limits and reproducible local checks. Existing service transactions,
request fingerprints, prompt snapshots and migrations remain unchanged.

Phase 04 implements Android chat over those existing routes. A Keystore AES-GCM
key encrypts a bounded atomic record under noBackupFilesDir containing the verified
normalized server/owner credential and at most one exact pending request. The
client commits this reservation before POST and never automatically repeats a
creation POST or changes a retry's UUID/content/options. Restart re-authenticates
the saved identity and queries the original request ID. Key loss/corruption
requires reconnect; logout/account switching clears private recovery and caches.
Drafts and loaded history/source cards otherwise stay in ViewModel memory.
Source cards and retrieval details come from the same owned request snapshot;
they are not reconstructed from current claims. Polling is bounded, 401 stops
recovery. Phase 04 itself did not add cancellation, streaming or
device inference; Phase 16 adds the stream/Stop flow below. Existing server authority and released schema remain intact.

Phase 07 adds a MemoryController owned by the authenticated chat ViewModel. Its
scope/mode/date/page and source-detail state is fenced by verified server/owner
and selection epochs; it never changes saved request citation maps. Lists use
server interval filtering, including superseded rows valid before a future
correction. Competing loaded assertions are warnings, not truth rankings.

The additive encrypted session format v2 retains the v1 credential/chat journal
and adds one immutable memory reservation. Source/claim IDs, note or exact
user-evidence selection, annotation, interval and correction target commit before
POST. A returned note version is a second durable stage before claim submission.
Both journals share the existing Keystore key/file and a bounded 128 KiB record;
token rotation preserves them only after server/owner verification. Switching,
logout and 401 clear both. No memory POST runs automatically during restore.
Identical replay uses existing server write fingerprints; conflicts retain input
for review. Explicit local recovery discard never deletes server evidence.

Exact evidence uses UTF-8 SHA-256 and Unicode code-point spans converted from
UTF-16 selections. Existing model sources remain read-only and cannot support a
user write. Settings creates profiles using the current style/warmth/detail enums;
selection applies to new conversations. Frozen personality/prompt snapshots and
the explicit supported prompt-upgrade flow remain unchanged. No server contract,
migration, inference or dependency change is required by this client phase.

Future client work may add Android microphone input, an optional local model,
intent suggestions, draft summaries and offline drafts. These are not implemented
by Phase 04. An iOS Swift client could later use the same HTTP contract.
Server: authoritative memory, heavy model calls, retrieval,
authorization, synchronization, and tool effects. Local models submit proposals,
not trusted claims or actions. See MOBILE-CONTRACT.md. Hardware-dependent Android
model/runtime selection awaits the phone's RAM, SoC, Android version, and goals.

## Phase 08 document ingestion

Migration 0005 extends source origin/trust without changing released migrations
or old prompt/retrieval snapshots. Owner-bound upload receipts retain raw database
blobs and immutable input fingerprints. Reservation and publication are short
transactions; identity parsing/chunking runs between them. Publication validates
exact hashes/spans and commits the full version, chunks, lexical projection and
ready receipt atomically. A bounded lease and attempt fence support explicit
same-ID replay without a background worker. Failed receipts remain private and
count against quotas. Names are display metadata, never filesystem paths.

Document chunks are imported/untrusted evidence, not claims. Retrieval filters
owner, scope, publication and version availability before candidates/context,
then places complete excerpts in remaining shared budgets. D cards and document
trace arrays are separate from existing M claim cards. Requests freeze selected
versions and exact evidence across failure retries and completed replay. New
conversations freeze v4; v3 claim retrieval survives and explicit audited upgrades
retain old prompts. `use_documents` defaults false and requires memory enabled.

Android capability gates its document UI. The bounded encrypted session record
is now v3/256 KiB with one chat, one memory and one document journal; v1/v2 records
remain readable. Raw upload bytes/IDs/options commit before POST, restoration
checks identity and never automatically writes. Original D cards come from the
saved request, not current version lists. No provider/database client is added.
See DOCUMENT-INGESTION.md for exact contracts, limits and the separate 0005
installation boundary. PDF, OCR, embeddings and automatic promotion are deferred.

## Phase 09 scoped identity

Migration 0006 adds explicit scoped entities, alias/rename history, self bindings,
claim annotations, reversible merge lineage and exact operation receipts. Every
reference uses owner/scope constraints. Existing claims remain nullable/unlinked;
raw subjects, evidence and old write hashes are retained. Scope row locks serialize
decisions and audit atomically. Names and entity kinds confer no authority.

NFKC/case/whitespace exact aliases expand candidates before ranking. Ambiguous
roots remain separate and are withheld before context; bounded alternatives and
historical interpretations freeze in the request trace. Linked conflicts use the
historical canonical root, and old string-only subjects remain supported. No new
prompt version, extraction or shared identity graph is introduced.

Android's Memory entry opens the capability-gated entity picker/editor. Reviewed
alias/link/self/rename/merge/undo changes reserve exact operations in the existing
Keystore record v4/256 KiB; v1–v3 journals remain readable. Restore is read-only
until explicit receipt check or identical retry. Current identity decisions never
replace saved source cards. See ENTITIES-AND-ALIASES.md for policy and installation.

## Phase 10 exact hybrid retrieval

Migration 0007 adds discardable owner/scope-constrained embedding entries, binding
claim/chunk/source IDs and exact hashes to a full model digest/dimension/index
namespace. Explicit bounded rebuild snapshots immutable history, embeds outside
transactions under the same generation semaphore, then rechecks under a scope
lock before atomic publication. Failed or raced rebuilds retain the prior index.

Query embedding occurs before reservation, after ownership checks, outside any
database transaction. Exact cosine ranking filters current/historical authority
and entity ambiguity before scoring, with 256-item/content-work bounds. Missing,
invalid or incompatible entries degrade to the original lexical baseline. Whole
conflict groups, prompt budgets and imported trust survive. New traces freeze
semantic/channel metadata; failed/completed replay never searches a newer index.
There is no ANN, pgvector dependency, new prompt or automatic indexing job.

Semantic retrieval remains disabled by default pending real-model quality/resource
evidence. Capabilities distinguish configuration and last observed degradation;
per-request diagnostics record the actual reason. Clients still use owned ADA
HTTP APIs. See [the Phase 10 policy](EMBEDDINGS-AND-HYBRID-RETRIEVAL.md).

## Next milestone

Phase 2 establishes a measured lexical/subject baseline. Subsequent milestones can
evaluate optional retrieval improvements and episode quality
against it while preserving the scope/time boundary and exact evidence provenance.
External writes need a separately selected integration and explicit intent/authorization/receipt contracts. Automatic
extraction, autonomous work, affect learning and device inference remain deferred.

## Phase 11 proposals and review

A user selects owned immutable excerpts for bounded structured extraction. The
server validates source/version/hash/span before and after inference; extraction
shares process admission with chat and runs outside transactions. Pending
proposals are separate from claims, lexical search and semantic indexes. A scoped
lock binds candidate revision, exact evidence, conflicts and canonical mapping to
a review hash. Confidence never grants factual authority or authorization.

An explicit principal-bound review creates a new user endorsement source and a
claim with that mandatory exact span, plus original supporting source links.
Receipt, claim, mapping and optional specific valid-time correction commit
atomically; same-key replay returns the original receipt. The original imported or
model trust is preserved. Fresh retrieval validates this mapping before context.
Request-frozen historical cards remain unchanged.

Migration 0008 adds four scoped tables and nullable claim provenance without
changing released history or original evidence requirements. Old origin enums
remain intact; optional `review-v1` provenance exposes `user_reviewed` to capable
clients. Android extends encrypted persistence to v5 for one draft and exact
pending operation; restore never writes. Admin receives windowed state counts
only. See [the policy](MEMORY-PROPOSALS-AND-REVIEW.md) and
[compatibility decision](../plans/DECISIONS.md). No automatic extraction, approval,
agent loop or new chat prompt is added by Phase 11.

## Phase 12 separate bounded agent protocol

Migration 0009 adds four owner/scope-constrained run/step/approval/receipt tables
without modifying released migrations, chat requests/events or saved prompt context.
The server registry selects read-only calculator and owned memory/source lookup.
Native ada-agent-v1 commands are separate from ordinary chat and require exact
human preview approval. Maximum steps, time, calls, outputs and full context are
deterministic. Short locks reserve and atomically publish receipts with generation
fencing; inference uses shared process admission outside any transaction.

Expired leases/receipt failures cannot imply success or trigger repeated execution.
Tool receipts retain tool_result/untrusted_tool_output provenance; they never promote
claims or original imported/model trust. Android journal v6 binds exact keys to the
verified owner/scope; restoration only reads. Admin exposes aggregate run states.
See [TOOLS-AND-AGENT-LOOP.md](TOOLS-AND-AGENT-LOOP.md) for native protocol, bounds,
installation and checks. No external write integration or autonomous schedule exists.

## Phase 13 generated episodes and durable consolidation

Migration 0010 adds owner/scope-constrained job, source-pin, episode and navigation
context tables. Exact immutable source IDs, hashes, trust and availability are
checked before reservation, generation and fenced publication. One bounded
in-process worker uses shared admission, short transactions, 120-second leases
and three recorded attempts. Atomic receipts make restart and completed replay
idempotent; only expired read-only generation may be repeated as a tracked attempt.

Episodes remain generated navigation with original evidence links. They are not
claim/document factual candidates or automatic chat context. A separate request-ID
navigation snapshot freezes up to three authorized episode maps without changing
old prompts or chat input. Proposal jobs submit only pending Phase 11 suggestions;
rebuild jobs replace only scoped lexical projections. No approval, deletion or
valid-time rewrite is permitted. Android v7 journals restore by GET; admin exposes
only bounded job metadata. See [the policy](EPISODES-AND-CONSOLIDATION.md).

## Phase 14 explicit expression policy

Migration 0011 adds owner-target preferences and immutable settings receipts,
frozen conversation bindings, one bounded current session per conversation and
nullable request expression snapshots. Explicit precedence is saved personality,
account, scope, profile, then conversation. Changes to defaults apply only to new
conversations; an explicit conversation update adopts reviewed settings for future
replies and conflicts with in-flight chat. Original personality/system prompts,
request fingerprints and failed/completed replay remain intact.

The separate ada-expression-v1 overlay retains baseline v4/current and v3 claim
retrieval. Its fixed 800-byte budget keeps style choices independent of evidence
allocation. Opt-in session vectors have native integer ranges, bounded reviewed
changes, deterministic decay, expiry and explicit disable/reset. Normal model
output never writes state. Model vectors remain untrusted proposals until an
authenticated explicit review; there is no mood classifier or learned relationship
profile. Minimal receipts retain reason codes/source request IDs, not psychological
explanations. Expression never changes ownership, trust, ranking or tool policy.
Android Settings uses encrypted v8 exact-key recovery; restore only reads. See
[policy](INTERACTION-PREFERENCES-AND-AFFECT.md) for limits and compatibility.

## Phase 15 interaction learning and continuity

Migration 0012 adds owner/scope-constrained consent, immutable selected-source
observations, tentative enum-based suggestions, reviewed learned defaults and
minimal exact-key receipts. Owner row locks serialize consent/reset, review and
fresh request selection. No new provider call, index, cache or worker is created.
Observations retain source trust and policy lineage; deduplicated independent
completed user interactions reach a configurable review gate, never automatic
promotion. Weak guesses expire and cannot create rules. Explicit settings override
learned defaults. Optional account reuse contains no project/history text and
requires both originating and destination scope consent.

Opt-in continuity revalidates scoped/time-authorized episode source lineage and
selects exact original excerpts; generated summaries do not enter ordinary chat.
Factual retrieval keeps its conflict/ranking rules and first access to the evidence
budget. C source cards, uncertainty/omissions and learned policy/receipts freeze in
nullable request snapshots. v3/v4 baselines, personality snapshots, fingerprints
and failed/completed replay are preserved. Reset erases live learned state and
suppresses future reuse; minimal audit and immutable historical requests remain.
Android journal v9 preserves v1–v8 and restores by GET only. Admin exposes aggregate
operation counts, never private relationship profiles. See
[the Phase 15 policy](INTERACTION-LEARNING-AND-CONTINUITY.md).

## Phase 16 durable streaming and cancellation

Migration 0013 adds composite owner/request/attempt checkpoints and sequenced
owned events without altering Request status or payload fingerprints. ChatService
shares its exact reservation/context builder across legacy and streaming paths.
The native adapter yields bounded NDJSON outside transactions; short delta writes
and HTTP sends provide backpressure. A shared process semaphore covers the entire
provider iterator lifetime, including shutdown. One Uvicorn worker is required.

Publication and Stop serialize on conversation/request/attempt locks. Durable
intent wins if it commits first; completed publication otherwise wins. Instance,
attempt and request fences reject late chunks. Final response/source event,
revision and terminal event commit once. Restart and failed publication become
interrupted; operator recovery reconciles rich stream state while a live provider
keeps admission. Disconnect is observation loss, not generation cancellation.

Android uses bearer-authenticated OkHttp SSE and GET checkpoint replacement under
verified identity/generation guards. Its v9 encrypted pending payload stays intact;
no automatic POST or Stop on restoration. Only canonical final RequestOutput
constructs source cards. Admin queries five state/time/sequence fields, with no
private deltas or cancellation control. Event retention is count-bounded; 24-hour
cursor expiry is not physical erasure. See [the policy](STREAMING-AND-CANCELLATION.md).


## Phase 17 reviewed voice and independent playback

Migration 0014 adds immutable voice_inputs with composite owner/request/
conversation/scope constraints and an exact endorsed event/source-version link.
POST voice-requests requires explicit approval, original generated transcript,
client-reported on-device engine/platform/language/duration metadata and the old
chat options. Its fingerprint extends the old fingerprint in a separate domain;
ordinary text fingerprints and completed replay remain identical. Original ASR
text has generated-interpretation provenance and enters neither retrieved
candidates nor model context. Only approved wording creates user-explicit
conversational evidence. No audio/provider call runs in the registration
transaction; there is no server audio storage or ASR in this phase.

The native controller uses an API31+ on-device-only factory, API33+ installed
language preflight, runtime microphone permission, bounded recording and fenced
callbacks. Keystore journal v10 keeps review separate, then atomically consumes
an approved draft into the exact pending request before POST. Restores read only;
old journal versions remain supported. Local installed offline TTS reads owned
completed reply text and owns separate focus/route/lifecycle/stop controls. It
never stops server generation. See [VOICE-INTERFACE.md](VOICE-INTERFACE.md) for
limits, absent audio hashes, retention and remaining physical-device gates.


## Phase18 security and recovery

Migration0015 adds digest-only owner device credentials, explicit erasure preview/job
metadata, UUID request tombstones and account content revision/epoch fields. Legacy
CLI tokens remain compatible; owner-authenticated enrollment is configured off by
default. Rotation/revocation never grants an admin role. Fresh authorization fences
response delivery and every SSE batch; admitted generation may finish durably.

A single-process middleware bounds owner rates, HTTP admission, actual body bytes,
delivery time and JSON depth. It reserves a content revision before each ordinary
private POST and keeps one worker. Security metadata reads are explicitly allowlisted;
completion receipts remain readable across content-epoch changes while bearer
revocation still denies them. Admin routes retain metadata-only SQL projection and
receive a privacy epoch to invalidate monitoring caches after erasure.

The chosen retention policy is explicit owner deletion. Preview inventories all45
installed owner-content tables and rejects active private publishers. Confirmation
binds a fresh preview to a durable job UUID. A leased worker deletes the dependency
graph, creates UUID-only tombstones and advances the account epoch in one transaction.
Native SQLite FTS/PostgreSQL projections are included. Account/credential/grant/minimal
operation metadata remains; backups/offline copies are disclosed. Explicit erasure
is the sole new exception to saved completed replay, which then returns410.

Android v11 Keystore journals retain v1–v10 reads, reserve security UUIDs before POST
and discard private journals when the verified epoch changes. Reopening performs
GET-only reconciliation; a one-time issue secret cannot be recovered from its digest.
Android settings offer enrollment/rotation/revoke and preview/confirmed erasure.
The read-only web dashboard accepts these bearer tokens and clears on revocation or
privacy-epoch changes without persisting authentication/private query data.

Portable encrypted PostgreSQL recovery uses an exported snapshot, custom dump,
row-count/hash manifest and current separately encrypted deletion ledger. Restore
accepts only a nonexistent isolated ada_restore_* database, verifies original rows,
quarantines all restored credentials and reapplies later erasure/tombstones. Immutable
source/snapshot/receipt history survives unless explicitly deleted. Configuration
allowlist is separate from credentials/private keys. The selected destination is
%LOCALAPPDATA%/ADA/backups. See [the operational runbook](SECURITY-AND-OPERATIONS.md).
No live backup, application migration, erasure, service publication or Phase19 work
is implied by these source changes.

## Phase24 isolated public research

The `ada-web-research-v1` protocol adds an owner-controlled research workspace,
separate from legacy tools/chat. It reuses existing AgentRun/Step/Approval/Receipt
rows in the installed erasure/backup inventory; head0016 and all57tables remain.
Legacy tool routes explicitly reject this protocol. Exact preview hashes bind
canonical public targets, headers, expiry and budgets. An approval is a single
call, never session-wide permission. Durable reservation precedes network I/O;
fresh credential/epoch, lease and generation fences reject late publication.

A default-off Docker adapter admits only a locally verified immutable image.
Its tiny secret-free build context, default-drop IPv4/IPv6 firewall, pinned public
IPv4 peer/TLS hostname, bounded parser and post-setup privilege drop are the
egress boundary. There is no host mount, DB handle, inherited secret/proxy,
private model context, cookie, JS or fallback HTTP client. All DNS A/AAAA answers
must pass; redirects require another owner preview. Python documentation and
English Wikipedia are the closed pilot; the Wikipedia-only public contact is
visible in the exact headers. Network admission is separate from the existing
shared model capacity. One worker remains required.

Immutable untrusted W snapshots bind exact UTF-8 hashes and Unicode spans,
retrieval/freshness, URLs, parser and terms. Search snippets are not W evidence.
Answers use only the public question and saved web excerpts through the local
provider; generated text cannot authorize another call. Explicit save creates
an imported-untrusted research document, never an endorsed personal fact.
Completed replay does not refetch. Android encrypted journalv13 preserves exact
operations and GET-only recovery while retaining v1–v12 compatibility. Admin
projects existing aggregate states/counts only. OpenAPI117paths/156schemas is
additive; old prompts, citation contracts and chat fingerprints are unchanged.
See [the security/usage runbook](SECURE-WEB-RESEARCH.md) for measured proof,
limits, corrected disclosure error and remaining target/host/native-quality gates.
