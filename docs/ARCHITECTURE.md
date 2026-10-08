# Phase 0 architecture decisions

Status: implemented foundation; later features are explicitly listed below.

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

Every conversation has an explicit personal scope ID; general projects, documents,
shared scopes and membership grants are deferred. No phase-0 resource is shared
between users. Later project scope IDs must reference authorized scope/membership
records rather than trusting arbitrary client identifiers.

## Storage

PostgreSQL is authoritative. SQLAlchemy uses composite ownership foreign keys for
personality/conversation/request/event links. Application reads always include the
authenticated owner. This is application-enforced isolation with database integrity
constraints, not PostgreSQL row-level security. The database administrator and server
operator remain trusted. RLS is a future defense-in-depth decision before a less
trusted deployment.

Alembic migration 0001 is an immutable snapshot. Add new migrations; never replace
it with `Base.metadata.create_all()` at server startup. Migrations are explicit.
Events are append-oriented through application code, but Phase 0 does not install
database triggers preventing operator edits. Trust labels distinguish user words
from model output. There is no claim extraction yet.

## Request state machine

New -> running -> completed or failed. A failed request may become running with an
incremented attempt. A client UUID is unique within its owner. Reusing it with other
content or another conversation returns 409. Completed retries return the saved
response. Provider failure is an explicit 502 with a sanitized code.

The reservation transaction locks the conversation and checks its active request.
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

System baseline + frozen personality + most recent complete user/assistant pairs +
current input. Failed requests remain inspectable evidence but do not become dangling
model history. Older pairs fall out when the conservative UTF-8 byte budget is full.
This is a conservative bound, not provider-tokenizer precision or long-term memory.
The adapter sets an explicit Ollama context window/output limit. A real model test
must confirm token use and latency. No summary is silently substituted.

The adapter receives only the selected conversation. Ollama has no ADA user state;
each call sends full selected messages. Clients never supply system roles. The model
is not a security boundary: actual tools and permanent claim writes are absent.

## Security and observability

Local administration issues 256-bit random bearer tokens and stores hashes. Tokens
are revocable by rotation; no passwords, public signup, OIDC, or device enrollment
are implemented. Use HTTPS/encrypted transport for remote clients. Keep Ollama and
the database inaccessible to clients. CORS is not enabled. No secrets or request
bodies are intentionally logged; start script disables HTTP access logs.

Durable traces include request ID, model/provider, input snapshot, prompt version
(on the conversation), attempts, start/finish times, error category, and token counts
when supplied. These contain private conversation data: protect database/backups.
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

Source/event and scope foundations precede claims. Add project scope membership,
explicit source versions, evidence spans, and claim operations with provenance
tests. Keep static personality. Defer vector search, tools, autonomous work, mood
simulation, relationship learning, and Android model execution until requested.
