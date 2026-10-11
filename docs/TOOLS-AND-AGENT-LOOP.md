# Read-only tools and bounded agent runs

Phase 12 implements only `calculator`, `memory_lookup` and `source_lookup`.
Each native model request is a proposal requiring an authenticated owner's exact
approval. No shell, browser, file access, email, external write, schedule, memory
promotion or unlimited autonomous execution is included. Tool results and final
model answers are untrusted; receipt identity proves the recorded outcome, not
the truth of a sentence or permission for another action.

## Compatibility and installation

Migration **0009** adds owner/scope/conversation-constrained agent runs, steps,
approvals and receipts. Migrations 0001–0008 and populated historical chat,
prompts, citations, fingerprints and replay remain unchanged. Empty agent tables
can be downgraded; populated agent history refuses downgrade. A preflight also
preserves SQLite's empty agent schema when an attempted deeper downgrade would
hit the existing populated review-history guard. Agent downgrade needs an online
preflight; a destructive offline script is not generated.

Current source requires head 0009. Validate/backup and explicitly install through
the normal Alembic workflow for the intended database before operational use.
This implementation did not migrate the configured application (observed 0005),
change its grant, install on the phone or deploy. Disposable PostgreSQL/SQLite
migrations are verification evidence, not an application upgrade.

Normal chat is unchanged. Its required `tools: false` capability still describes
the plain-chat contract. The additive `agent_tools: approval_read_only_v1`,
`agent_protocol: ada-agent-v1` and exact `agent_registry` enable the separate client
flow only when a real agent adapter is configured. Production fake chat has no
agent fallback. `GET /v1/agent-protocols` advertises compatibility and bounds;
`GET /v1/tools` advertises immutable versions and typed schemas. Both authenticate.

New runs explicitly select `ada-agent-v1` and freeze their personality expression,
task, tools, owner, scope, time and context. They require an existing conversation
with saved `ada-baseline-v3` or `ada-baseline-v4`. Older conversations use the
existing explicit audited prompt upgrade first. There is no baseline-v5 change,
implicit upgrade or interpretation of plain-chat JSON as a tool command. Agent
history is separate and does not insert ordinary chat events or user claims.

The separate native Ollama adapter follows the
[tool-call protocol](https://docs.ollama.com/capabilities/tool-calling) and
[chat endpoint](https://docs.ollama.com/api/chat). It accepts one native assistant
tool call with object arguments and no accompanying explanation, or a final
answer. Hidden reasoning, incomplete/wrong-model replies, duplicate JSON keys,
non-finite data, multiple simultaneous calls and oversized responses fail closed.
Provider URLs/credentials/body text are suppressed from HTTP debug logs for the
agent call, and only fixed error codes are exposed. No new SDK/dependency is used.

## Selected registry and limits

| Tool/version | Allowed target and data | Bound |
|---|---|---|
| calculator / calculator-v1 | Constrained exact rational arithmetic; no interpreter or arbitrary code | 256-character expression, 64 tokens, depth 8, bounded literals/intermediates |
| memory_lookup / memory-lookup-v1 | Owned run scope and frozen as-of; lexical retrieval of explicit/reviewed claims with original exact evidence | Query 400 characters; 1–5 items; 2,000-byte retrieval budget |
| source_lookup / source-lookup-v1 | Owned run scope/time and exact immutable source/version/hash/code-point span; published ready imports within the half-open availability interval retain original trust | 256 code points and 1,000 UTF-8 bytes per exact excerpt |

All specs are read-only, require `authenticated_owner_scope`, target only
`run_scope`, allow **two calls per tool**, require human approval, and bound
result JSON to **4 KiB** with a **five-second** execution limit. The arithmetic
parser uses fractions and a fixed grammar; it never uses `eval`, an executable
AST, a subprocess or filesystem/network access. Lookup opens its own short
read transaction; PostgreSQL adds a three-second statement and one-second lock
timeout. The elapsed guard checks returned results; SQLite has no forced thread
termination claim. Registry drift invalidates an old pending run.

Memory lookup preserves whole evidence/conflict groups rather than truncating
quotes. Its result distinguishes omitted candidates, candidate-pool truncation,
ambiguous identity and a required date. Empty/bounded lookup is not proof that
no fact exists. Imported/model text remains untrusted, including instructions
inside evidence. Every further requested tool again requires human approval.

Runs allow **five model steps**, **300 seconds** total (including review wait),
**120 seconds** per approval preview, **90 seconds** per generation/execution
lease, and **100 retained runs per owner/scope**. Whole frozen messages, advertised
schemas, 512 bytes of framing and 1,024 bytes of output reserve share **8,192 UTF-8
bytes**. Native inference is non-streaming, without thinking, temperature zero,
with num_ctx 8192, num_predict 1024, maximum 60-second configured timeout and
64 KiB HTTP reply bound. Context/step/call/time/output limits terminate visibly
without inventing a successful answer.

## Owned HTTP workflow and receipts

| Method/path | Meaning |
|---|---|
| POST /v1/conversations/{conversation_id}/agent-runs | Exact `run_id`, task, protocol, allowed tools and optional aware as-of |
| GET /v1/conversations/{conversation_id}/agent-runs | Bounded owned history |
| GET /v1/agent-runs/{run_id} | Owned current state and recorded steps/receipts; never advances execution |
| POST /v1/agent-runs/{run_id}/steps/{step_id}/approve | Exact `approval_id`, preview hash, argument hash and tool version |
| POST /v1/agent-runs/{run_id}/steps/{step_id}/revoke | Exact bound denial; cannot cancel an executing/completed effect |
| POST /v1/agent-runs/{run_id}/recover | Explicit operation nonce and generation after lease expiry; never reexecutes |
| GET /v1/tool-receipts/{receipt_id} | Original owned durable outcome |

Unknown tools, extra/malformed arguments, owner/foreign-scope guesses, stale
sources, changed/expired previews and reused UUIDs with changed input are rejected.
Personality, names, retrieved instructions and model confidence grant no authority.
Approvals bind actor, owner/scope/run/step, frozen time/protocol, version and both
hashes. Source pins are revalidated before preview and again before approval.
Exact nonce replay returns the original receipt, even after later run changes.
Identical creation replay observes the run and never repeats inference.

Short scope/row-locked transactions reserve and commit with generation fencing.
Model inference shares the process admission semaphore with chat and runs with
no database transaction open. Denial and receipt reads need no inference slot.
Tool dispatch occurs after approval commit; result/receipt/step/context publish
atomically. A failed receipt transaction cannot claim success. Lease expiry or
explicit recovery records `unknown`, fences late results and never repeats an
ambiguous execution. Completed receipts are immutable; cancellation cannot undo
a completed effect. The selected tools have no external effects to reconcile.

Receipts carry owner, scope, run, step, approval, tool version/hashes, sanitized
outcome/error, result and UTC-millisecond identity. Their fixed origin is
`tool_result`, trust `untrusted_tool_output`. Source results preserve original
origin/trust inside the envelope. They are not source versions, claims, embeddings
or review endorsements. GET responses are authenticated and no-store; admin
grants cannot approve another owner's run or read its private receipt.

## Clients and verification

Android offers **Read-only tools** from an open conversation only when the exact
capability/registry is supported. The preview shows account/server, fixed scope,
tool/version, exact arguments, expiry and read/calculation effect. Approval is an
explicit second action; denial produces a revocation receipt. Running, pending,
completed, failed, unknown, result trust and actual receipt are visible without
hidden reasoning. Unknown future states never imply completion.

Keystore/AES-GCM journal v6 preserves v1–v5 records in the existing 256 KiB
no-backup atomic file. Exact creation and decision/recovery keys are saved before
POST and bound to verified server/owner/scope/conversation/run. Restore performs
GET only; lost approval delivery can reconcile the original receipt by GET.
Otherwise check/retry/recover is explicit, preserving identical input. Identity
switch/logout/key loss clears private state; generation fences late replies/401s.
A terminal expired/rejected preview can close without inventing a tool receipt.

Admin overview's optional closed `agent_run_counts` reports current states for
runs created in the selected window: running, pending_approval, completed, failed
and unknown. Older schemas/servers report unavailable. No private tasks, arguments,
results, source excerpts, approval control or executable dashboard action is exposed.

Tests cover owned HTTP, schema/permission rejection, instruction injection,
capacity, context/step/call/time/output limits, denial/expiry, changed previews,
provider crash/timeout, transaction rollback, concurrent PostgreSQL reservations,
stable receipts, lease recovery/fencing, historical migration/replay, client
journaling/reconnect and actual force-stop. Real-model probes use only disposable
synthetic PostgreSQL evidence and explicit test approvals:

```powershell
$env:ADA_AGENT_OLLAMA_PROBE = '1'
# Set ADA_TEST_DATABASE_URL to the dedicated ada_phase2_test database securely.
.\.venv\Scripts\python.exe -m pytest tests/test_agent_ollama_probe.py -q -s
Remove-Item Env:ADA_AGENT_OLLAMA_PROBE
```

Use [verify-agent-emulator.ps1](../apps/android/scripts/verify-agent-emulator.ps1)
with a task-owned emulator serial for actual HTTP and staged recovery. This script
rejects physical-device serials. See [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md) for checks actually run, failures, skips, measured
real-model timings and remaining S24 FE/Android 16, HTTPS/accessibility/resource
verification. No external integration or later phase is an exit requirement.
