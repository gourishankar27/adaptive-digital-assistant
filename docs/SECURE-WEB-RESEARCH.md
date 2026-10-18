# Secure public web research — Phase 24

Phase24 implements an opt-in public research workspace in Android and an
owner-authenticated HTTP protocol. It is disabled by default. This implementation
was checked locally on Windows/Docker Desktop; it has not been installed in the
running private service or on the S24FE. Schema head remains **0016/57 tables**.
Use [STATUS](../plans/STATUS.md) for dated results, failures and open gates.

## What the pilot supports

An owner enters a public question and either an allowlisted URL or a Wikipedia
search query. ADA reserves a run without fetching. The owner inspects and approves
the exact outgoing request. Retrieved pages become immutable, untrusted snapshots
with W citation cards. ADA can answer using these saved sources through the local
model. The owner can explicitly save that answer as an imported research note.

The URL pilot allows static Python documentation under `https://docs.python.org/3/`
and main-namespace English Wikipedia pages under `https://en.wikipedia.org/wiki/`.
The search pilot uses Wikimedia's public REST page-search endpoint, without an API
key or a purchased service. This is a closed pilot, not general internet browsing.
There are no authenticated sites, uploads, external writes, JavaScript,
subresources, crawling, automatic follow-up searches or automatic redirects.

Private conversations, history, memories, personality and files are not copied
into an outgoing request. The separately entered question stays on the ADA server
and local model. The approved URL/query and displayed request headers leave the
server; the recipient and network/DNS infrastructure also observe network metadata.
Text that you manually copy into a query will be disclosed exactly as approved.
There is no anonymization guarantee.

## Developer setup on Windows

Start with the existing [developer guide](HOW-TO-USE-ADA.md) and
[private HTTPS setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md). Keep PostgreSQL and Ollama
private, use one Uvicorn worker, and retain normal owner authentication. Android
talks only to ADA's API. This phase adds no migration or host Python dependency.

1. Open PowerShell in the repository root. Install the pinned project environment
   as described in the developer guide. Start Docker Desktop with its **Linux
   containers** engine and wait for `docker info` to succeed. The active Docker
   context must use a local named pipe or Unix socket; a remote daemon is rejected.
2. Build the isolated broker. The script copies only three allowlisted source
   files into a temporary build context; do not substitute the repository root as
   Docker's build context. The base image is digest-pinned and the package source
   is a dated Debian snapshot. Building downloads those public build dependencies.

   ```powershell
   ./.venv/Scripts/python.exe scripts/build_web_broker.py --output .pytest_cache/web-broker-image.json
   ```

3. Verify the actual container/network boundary. This starts disposable synthetic
   containers, demonstrates a reachable private service without the broker
   firewall, and verifies that the same service is blocked inside the broker.
   It does not call your application database, API or Ollama.

   ```powershell
   ./.venv/Scripts/python.exe scripts/verify_web_broker.py --manifest .pytest_cache/web-broker-image.json
   ```

   Require `isolation: passed`. A build alone is insufficient. Do not enable the
   feature after a failed check. Rebuild and repeat verification whenever the
   broker's source changes; the server rejects stale source/image manifests.
4. If you want Wikipedia search, choose a public project/contact identifier that
   may be disclosed in the request's User-Agent. Put it in your ignored `.env` as
   `ADA_WEB_OPERATOR_CONTACT=your-public-contact@example.org`. A valid HTTPS public
   contact URL also works. Leave the setting absent to disable search while
   retaining the Python documentation URL pilot. An empty or malformed setting
   is a configuration error. Never use a secret/API key in this field.
5. Optionally run the explicitly public pilot. This sends the fixed public Python
   ZoneInfo URL and the query `Jupiter`; the configured contact goes to Wikipedia
   only. It reports counts and states, not source quotes or header values.

   ```powershell
   ./.venv/Scripts/python.exe scripts/verify_web_broker.py --manifest .pytest_cache/web-broker-image.json --public-pilot
   ```

6. When you choose to install this source, add literal values to your ignored
   `.env`. Use your checkout's absolute manifest path, with forward slashes.
   These are future activation instructions; this implementation run did not
   enable or restart the private service.

   ```dotenv
   ADA_WEB_RESEARCH_ENABLED=true
   ADA_WEB_BROKER_MANIFEST=G:/your-checkout/.pytest_cache/web-broker-image.json
   ```

   Restart through your normal private-server procedure. At startup the server
   verifies the immutable image, current source hashes and container restrictions.
   If proof fails, authenticated capabilities report research unavailable; the
   server does not fall back to an unrestricted HTTP helper. `web_search` also
   requires the configured operator contact. Treat manifests/images as local
   build artifacts; do not copy an old proof to a different host and assume it
   validates that host.
7. Build the normal Android app using its pinned wrapper. Source version is
   **17 / 0.24.0-research**. Sign into your usual private HTTPS ADA origin. No
   database, Ollama or third-party credentials belong in the Android app.

For disabling, set `ADA_WEB_RESEARCH_ENABLED=false` and restart through the normal
procedure. Saved runs remain owner-readable; creating/approving new calls is
disabled. A Docker failure during a request never triggers unrestricted fallback.

## Use it in Android

1. Open an owned conversation and choose **Public research**. If unavailable,
   check authenticated server capabilities and broker configuration.
2. Enter a public question. Select URL fetch or, when enabled, Wikipedia search.
   Enter the public URL/query yourself. Creating the preview performs no fetch.
3. Read the canonical URL, recipient, exact headers, disclosure, expiry and
   budgets. Wikipedia previews include the public operator contact. Python
   previews omit it. Confirm the approval dialog only if the entire disclosure
   is acceptable. Editing or following another URL requires a new preview and
   approval; an earlier approval never covers a different request.
4. Inspect the receipt. Search snippets are explicitly snippets, not W page
   evidence. Select a result only through another preview/approval. Redirects
   stop and offer a separately approved next request.
5. Inspect saved source text and its citation. Ask for an answer from saved W
   sources. Source text remains untrusted: a quotation is not proof of truth or
   of the model's interpretation. No model output can approve another call.
6. If useful, explicitly save a research note. This creates an imported untrusted
   document through existing document APIs; it does not create a personal claim
   or silently endorse the page. Later chat retrieval still requires the
   conversation's existing document/memory controls.
7. Cancel when finished with an unfinished run. Reopening verifies the same
   server/account/scope and performs GET-only recovery. A lost response is not
   proof of failure. Check the original run before an explicit exact retry.

Android encrypts the operation UUID and exact payload before POST, using journal
v13. Old v1–v12 journals remain readable. Identity/server/scope/epoch changes fence
private state. An in-flight cancel remains journaled until acknowledged; a late
fetch or model result cannot restore the cancelled client/run state.

## Limits and failure handling

| Boundary | Implemented pilot limit |
|---|---|
| Calls | Three total outbound calls per run, including search and redirect follow-ups |
| Redirects | Zero automatic redirects; each follow-up consumes a newly approved call |
| Network | Two concurrent broker operations and ten starts/minute per server process |
| Response | 1 MiB bytes; identity encoding only, compressed responses rejected before reading |
| Extracted text | At most 32,768 Unicode codepoints; truncation is recorded on the snapshot/card |
| Time | 15 s network I/O, separate 3 s bounded DNS wait and bounded container setup allowance |
| Transport | All A/AAAA answers must be public; this pilot connects only to a pinned public IPv4 address |
| Source freshness | 24 h for new answer generation; completed answer replay remains the original saved result |
| Model | Existing whole prompt-byte budget and shared inference admission; no extra model capacity |
| Retention | At most 100 retained agent/research runs per scope; existing document quotas apply to notes |

The Docker CLI wait has a 23 s deadline including setup, followed by bounded
best-effort container removal (10 s) and CLI termination/reaping (5 s). A stalled
output pipe or failed removal yields an unknown outcome, not a second request.
OS resolver
calls that outlive the 3 s wait can occupy at most two bounded resolver slots;
their late results cannot initiate a fetch. A stalled Docker daemon or OS is an
operational fault, not a hard real-time availability guarantee. After daemon
recovery, inspect/remove only abandoned `ada-web-` containers from this service;
do not broadly prune unrelated workloads. The worker itself retains its firewall
and15s network deadline if daemon cleanup fails.

`blocked`, `inaccessible`, `rate_limited`, `expired`, `partial` and `unknown` have
different meanings. Inspect fixed receipt codes. A redirect/private DNS answer,
unsupported MIME/encoding or invalid TLS identity stops before accepting evidence.
No available IPv4 address also stops the pilot. On rate limits, wait rather than
looping. Cancel an expired preview and create a fresh run; an unknown execution never
automatically refetches. Source expiry prevents a new answer, not historical
replay. Revocation/deletion fences stop late publication.

If `research_provider_changed` appears, the configured local provider/model no
longer matches the unfinished run's saved provenance. Restore that configuration
or cancel and create a fresh run. Completed answers still replay unchanged after
a configuration change; ADA does not regenerate them with the replacement model.

If startup capabilities remain false, check Docker is running, local context,
manifest absolute path, source-hash freshness and the verification script. Do not
weaken TLS, firewall rules, IP checks or container privileges to make a fetch pass.
Do not print request bodies, private URLs, credentials or contact headers into
operational logs while troubleshooting.

## API and saved evidence

All routes require a current authenticated owner. Added path templates:

| Method | Path | Purpose |
|---|---|---|
| POST / GET | `/v1/conversations/{id}/research-runs` | Reserve a preview / list owned runs |
| GET | `/v1/research-runs/{id}` | Reconcile original saved state |
| POST | `/v1/research-runs/{id}/calls` | Reserve the next exact outgoing request |
| POST | `/v1/research-runs/{id}/approve` | Approve the call UUID and matching preview hash |
| POST | `/v1/research-runs/{id}/cancel` | Fence late execution/publication |
| POST | `/v1/research-runs/{id}/answer` | Generate locally from saved, fresh W sources |
| GET | `/v1/research-runs/{id}/sources/{receipt_id}` | Read the exact saved text and card |
| POST | `/v1/research-runs/{id}/save-note` | Explicit idempotent imported note |

The `ada-web-research-v1` protocol reuses existing owner-scoped AgentRun, Step,
Approval and Receipt storage with a separate protocol guard. Old agent routes
cannot drive research runs. Each approval binds the exact canonical target,
headers, expiry and budgets. Same-ID changed payloads conflict; same approved
operation replays its receipt without refetching. Network/model calls happen
after reservation transactions commit. Fresh credential/epoch and cancellation
checks fence publication.

`ada-web-citation-v1` W1–W3 cards preserve fetched/final URL, retrieval/freshness
times, parser version, public-web origin, untrusted-web class, terms metadata,
SHA256 of saved UTF-8 text and exact Unicode codepoint spans. Android independently
verifies hash and quote before displaying original evidence. Search snippets do
not receive W labels. The full normalized extraction is retained subject to the
recorded limit, not a claim to have saved every rendered page element.

Snapshots/receipts are inside the existing 45-table owner-content erasure and
57-table encrypted recovery inventory. Private URL/query audit is available only
to the owner. Existing admin views receive aggregate run states/counts, not
queries, headers, source text or private research questions.

OpenAPI adds eight path templates/nine methods and thirteen schemas:
**117 paths / 156 schemas**. All 109 old paths and 142 non-capability schema
definitions remain unchanged. The two optional capability defaults are additive.
Old prompts, chat fingerprints, M/D/C citations, completed replay, dependency
locks and migration history are preserved. See [contracts](../contracts/README.md).

## Security evidence and remaining verification

The actual Linux broker installs default-drop IPv4/IPv6 OUTPUT rules before
dropping privileges. It permits only the chosen public IPv4 TCP/443 peer, checks
the actual socket peer and TLS hostname, drops all capabilities and runs UID65534
under read-only storage, seccomp and no-new-privileges.
The read-only startup probe requires EROFS in world-writable `/tmp`; a mere
permission-denied error does not satisfy it. It receives no private
database handle, model context, application environment, host mount or Docker
socket. Upper/lowercase proxy variables are explicitly cleared. Container logs
are disabled. Trusted setup/host/Docker compromise remains outside this boundary.

Local evidence includes a reachable-private-service positive control followed by
blocked access inside the broker, public Python fetch/Wikipedia search, exact W
hash/span tests, concurrent approval and revoke/cancel/crash tests, encrypted
PostgreSQL restore/erasure, Android real HTTP approval and force-stop recovery,
and one native qwen3.8:27b public answer/replay. Full-suite counts and earlier
corrected failures are recorded in STATUS/WORKLOG. A single native answer and
marker checks do not establish general factual accuracy, entailment or immunity
to prompt injection. Evidence is data, never tool authority.

The first public pilot incorrectly sent the configured operator contact to Python
documentation as well as Wikipedia. Recipient-specific headers and an independent
worker rejection now prevent that disclosure; regression tests and corrected
public requests passed. No contact value is recorded in repository documentation.

Still required before target release: installation-host isolation recheck, physical
S24FE/Android16 approval/recovery/TalkBack/large-font and signed HTTPS tests,
broader native answer and hostile-source quality review, sustained resource/soak
and daemon-failure checks, and explicit operator installation/activation. Earlier
voice/G-41 gates remain open. No Phase25 curiosity, scheduling, background dreaming
or deployment was implemented.

Provider policies checked 2026-10-17: Wikimedia's
[REST API](https://www.mediawiki.org/wiki/API:REST_API/Reference),
[User-Agent policy](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy),
[rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits),
[terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use) and
[privacy policy](https://foundation.wikimedia.org/wiki/Policy:Privacy_policy).
This pilot uses public unauthenticated requests, no dedicated key or purchase;
those policies are not a zero-retention promise or service SLA. Site-wide license
metadata does not replace per-material attribution/license review. Python's
[license](https://docs.python.org/3/license.html) and
[privacy notice](https://policies.python.org/python.org/Privacy-Notice/) apply to
its documentation pilot.
