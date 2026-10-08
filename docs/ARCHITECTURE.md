# Phase 2 architecture decisions

Status: persistent chat, explicit source-backed memory, scoped retrieval and citation traces.

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
Shared scopes, membership grants and documents remain deferred. Client scope IDs
are checked against authenticated ownership before a conversation or memory write.

## Storage

PostgreSQL is authoritative. SQLAlchemy uses composite ownership foreign keys for
personality/conversation/request/event links. Application reads always include the
authenticated owner. This is application-enforced isolation with database integrity
constraints, not PostgreSQL row-level security. The database administrator and server
operator remain trusted. RLS is a future defense-in-depth decision before a less
trusted deployment.

Alembic migrations 0001/0002/0003 are immutable snapshots. Add new migrations; never
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

New conversations freeze baseline v3. An explicit v1/v2 prompt upgrade archives the old
and new prompts, preserves the personality snapshot, locks the conversation and
rejects in-flight changes. It increments the conversation revision so failed requests
with old context cannot be resumed. Completed retries retain their original answer.
Unupgraded v1/v2 conversations continue with their original prompt and no retrieval.
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

## Mobile compute split (future)

Android Kotlin: UI, secure token storage, microphone, optional local model, local
intent suggestions, draft summaries and offline drafts. iOS Swift later uses the
same HTTP contract. Server: authoritative memory, heavy model calls, retrieval,
authorization, synchronization, and tool effects. Local models submit proposals,
not trusted claims or actions. See MOBILE-CONTRACT.md. Hardware-dependent Android
model/runtime selection awaits the phone's RAM, SoC, Android version, and goals.

## Next milestone

Phase 2 establishes a measured lexical/subject baseline. Subsequent milestones can
evaluate canonical entities, embeddings, document ingestion and consolidation
against it while preserving the scope/time boundary and exact evidence provenance.
Tools need explicit intent/authorization/receipt contracts before execution. Automatic
extraction, autonomous work, affect learning and device inference remain deferred.
