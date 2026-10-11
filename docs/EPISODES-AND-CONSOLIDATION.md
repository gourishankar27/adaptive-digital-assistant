# Episodes and consolidation — Phase 13

Migration **0010** adds four owner/scope-constrained tables: durable jobs, pinned
job sources, generated episodes and private episode navigation contexts. It adds
no columns to chat requests, events, claims or original sources. Earlier migration
files and saved v3/v4 prompts remain unchanged. Install head 0010 explicitly before
using this source; this implementation does not migrate the application database.

## Explicit jobs and publication

Authenticated owners POST `/v1/scopes/{scope_id}/consolidation-jobs` with a UUID
`job_id`, one of `episode`, `proposals`, `lexical_rebuild`, and exact source pins.
Pins contain version ID, version, full SHA-256 and half-open Unicode code-point
span. Summary/proposal jobs accept 1–4 distinct owned versions in the same scope,
up to 6,000 UTF-8 bytes of exact evidence. Sources from multiple conversations
must belong to that scope. Imported sources must already be published, ready and
available at reservation time. Source trust, event/conversation references and
availability are frozen; changes before publication produce a stale receipt.

Rebuild jobs accept no pins. The server freezes at most 500 current claim/document
projection inputs, validates original evidence and reviewed provenance, then
atomically replaces only that scope's lexical indexes. This job does not rebuild
embeddings, enable semantic retrieval, alter claims or rewrite valid-time history.

The exact owner/key/scope/body replays the original job, including terminal
receipts. A changed key payload or duplicate work snapshot conflicts. Work hashes
include source snapshots, kind, model and content/schema policy version. At most
100 retained jobs per scope are accepted; there is no automatic deletion. Lists
default to 25, allow 50, and cap offsets at 10,000.

Reservation, lease claim and fenced publication use separate short transactions.
Inference runs after claim commits, with no database connection on its thread.
The existing process shares one admission limit with chat and agents. Capacity
pressure leaves the job queued without consuming an attempt. One worker polls
once per second and executes at most one job at a time. It starts in the API
lifespan by default; `ADA_CONSOLIDATION_WORKER_ENABLED=false` pauses processing.
Use one Uvicorn worker until admission control is shared across processes.

A lease lasts 120 seconds, with at most three recorded attempts. Restart may
repeat read-only generation after an expired lease; every attempt is tracked.
An expired or replaced attempt cannot publish. Result, receipt and completed
checkpoint commit atomically. Failure retains prior episodes and original sources;
invalid output or a partially valid proposal batch publishes nothing. Shutdown
stops new claims and leaves unfinished work recoverable by its durable lease.

The native Ollama summarizer uses the configured model, strict structured JSON,
no thinking/tools, an 8,192-token context and 2,048-token output allowance. A
conservative UTF-8 bound includes the complete messages, schema, output reserve
and framing; otherwise accepted source pins can still exceed this whole-context
bound and fail honestly. Native inference is limited to 60 seconds, response
body to 64 KiB and generated JSON content to 16 KiB. There is no truncation or
fallback invented summary. Fake production providers advertise generation as
unavailable; deterministic summarizers exist only in explicit test fixtures.

`proposals` submits validated pending Phase 11 suggestions and an extraction
receipt. It never endorses a claim. Approval/edit/rejection still requires the
separate authenticated, exact Phase 11 review. Model confidence is not authority.
No job executes external commands, deletes evidence, schedules itself or resolves
contradictory statements as truth.

## Generated navigation and exact originals

Episode output records owner, scope, job, model, `episode-summary-v1`, time range
(end excluded), sections, compact tags and declared omissions. Every section has
exact support pins within the selected original map. The map retains original
hashes, spans, quotes, trust, source/version times and conversation/event references.
The episode itself always has `trust_class=model_generated`. Provenance does not
prove entailment or factual accuracy. Tags are navigation labels, not evidence.

Read `/v1/scopes/{scope_id}/episodes`, `/v1/episodes/{id}`, scope job lists and
`/v1/consolidation-jobs/{id}` as the authenticated owner. All private responses
are no-store. Old episodes remain inspectable even if a later source/policy
change prevents using them in a new context.

POST `/v1/scopes/{scope_id}/episode-contexts` with a request UUID and 1–3 episode
IDs freezes their authorized source maps as a `navigation_only` snapshot (24,000
UTF-8 bytes maximum; 100 contexts per scope). Same-key GET/replay preserves the
original snapshot; new contexts recheck current policy and original evidence.
Ordinary chat does not inject episodes or change its factual retrieval, prompt,
request input or completed replay. Episode navigation has a separate context
protocol so generated text cannot enter factual evidence candidates implicitly.

## Clients and monitoring

Android **0.13.0-episodes**, versionCode 8, exposes **History & episodes** from an
owned conversation when exact capabilities are advertised. It shows the first 50
completed events for explicit selection and pages episodes/jobs 25 at a time.
Review the complete original excerpts before queueing; no message is shortened.
Generation requires both generation and worker capabilities. Existing episodes
remain readable when generation is unavailable. Job state distinguishes queued,
running, completed, failed and stale; timestamps and final-attempt elapsed time
are measured, with absent values labeled honestly. Original version reads recheck
owner/scope, full hash, trust and code-point quote before display.

Keystore/AES-GCM journal v7 keeps one exact owner/server/scope/job/body reservation
before POST and reads v1–v6 records. Restore only GETs the original job. Timeout
means unconfirmed delivery: check, explicitly retry identical input, or explicitly
discard local recovery. Discard does not cancel/delete a server job. Session and
selection fencing prevents late private responses entering another account.
Oxford Blue remains the default; Dark Red and Olive Green are unchanged.

The read-only admin overview optionally adds closed state counts and the newest
25 metadata rows in its creation window. Rows contain owner/scope/job IDs, kind,
version, checkpoint, attempt and measured times only. No private inputs, quotes,
summaries, outputs, hashes or model reasoning enter this monitoring projection.
Current server grants and audited reads remain required; older servers are supported.

## Evaluation and target verification

`evaluations/episode-summary-v1.json` is a four-case public synthetic corpus:
tentative decisions, disagreement, untrusted imported instructions and generated
uncertainty with Unicode. `scripts/evaluate_episodes.py` executes actual migrated
HTTP jobs in disposable SQLite or the dedicated PostgreSQL test database, with a
fixture or native Ollama. It checks exact version/hash/code-point support, replay,
no endorsement, and model-thread connection isolation. Marker coverage measures
lexical omissions only; manually review attribution, uncertainty and unsupported
detail. It cannot establish broad summary quality, truth or entailment.

Run the task-owned emulator script `apps/android/scripts/verify-episode-emulator.ps1`
for actual HTTP UI, staged lost-response/force-stop recovery and strict cold launch.
It accepts only emulator serials, an ephemeral app-private credential and a
disposable fixture database. Actual checks, failures, skips and remaining Samsung
S24 FE/Android 16, HTTPS, TalkBack, production load and installation verification
are recorded in STATUS/WORKLOG. This phase does not deploy or implement later work.
