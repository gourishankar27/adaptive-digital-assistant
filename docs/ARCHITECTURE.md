# ADA architecture decisions

Status: persistent chat, explicit memory, claim/document retrieval and explicit admin monitoring.

## Deployment

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

Alembic migrations 0001–0004 are immutable snapshots. Add new migrations; never
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

One source version per claim is supported in this milestone. Canonical entities,
multiple evidence links, sharing, semantic validation and general contradiction
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
an exactly-once external side-effect mechanism. Tool executions will need their own
intent/authorization/receipt protocol before tools are enabled.

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
is not a security boundary. External tools are absent. Permanent claims are written
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
are revocable by rotation; no passwords, public signup, OIDC, or device enrollment
are implemented. Use HTTPS/encrypted transport for remote clients. Keep Ollama and
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
they never generate. Current readiness validates supported head 0014. Admission shows the
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
