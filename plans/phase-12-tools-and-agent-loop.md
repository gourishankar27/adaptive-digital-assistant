# Phase 12 — bounded tools and agent execution

Status: implemented; local checks passed; target verification remains. Prerequisite: Phase 03; Phase 04/06 for relevant client controls.
Apply STANDARDS and CODEX-WORKFLOW. Implement selected tools only, not a universal
shell/browser/email agent.

## Goal and first scope

Allow ADA to request typed tools through a bounded orchestrator whose server
policy checks authority and records outcomes. Begin with read-only tools such
as a bounded calculator and authorized memory/source lookup. The calculator
uses a constrained parser, never `eval` or arbitrary code. External writes are
an additional checkpoint requiring a specifically selected integration.

## Registry and execution data

Define ToolSpec with version, argument/result schemas, permission policy,
read/write classification, time/size limits and allowed targets. Separate model
proposals from validated execution commands. Tool requests and results carry
owner/scope/request/step identity and a durable receipt. Reject unknown tools,
malformed/extra arguments, forbidden paths, resource guesses and private objects
from another scope. Credentials stay in a server-side provider, never model text.

Add agent-run/step/approval/receipt records with lease/attempt fencing and stable
idempotency keys. Record sanitized error/outcome, not secret arguments. Tool
outputs get their own trust/origin and are evidence, not automatic user claims.
Current claim promotion still uses explicit assertion/review policies.

## Bounded loop and compatibility

Use deterministic maximum steps, elapsed time, calls per tool, output size and
whole-context budget. Model/tool calls happen outside open transactions. Reserve
steps and commit outcomes in short transactions with fencing. Iteration limits,
invalid commands, capacity rejection and provider failure produce explicit
terminal states; do not manufacture an answer claiming a tool succeeded.

Today's Ollama adapter rejects unsupported tool-only replies. Add a separately
tested tool protocol/agent mode with capability gating, rather than interpreting
arbitrary JSON in normal chat as a command. Preserve plain-chat behavior, old
prompt snapshots, request fingerprint domain separation and completed replay.
New agent-aware prompts use an explicit compatibility registry/upgrade path so
v3 memory retrieval remains supported.

## External action checkpoint

For a selected write tool, show the exact target/account/arguments/effect in a
reviewable preview. Approval binds actor, request, tool version and argument hash;
any change invalidates it. Current user intent and server policy remain required.
Retrieved instructions, affect and personality do not grant permission.

Use provider-supported idempotency where possible and store a receipt before
declaring success. An external timeout may leave outcome unknown: reconcile via
the provider's receipt/status mechanism. Never automatically repeat an irreversible
write whose outcome cannot be determined. Cancellation cannot undo a completed
external effect. No real external messages are sent while implementing plans or
running ordinary tests; use explicit test transports/authorized test accounts.

## Client and monitoring

Android shows tool intent, pending approval, running, completed/failed/unknown
outcome and receipt. Admin shows operational metadata within its permission.
Do not reveal hidden model reasoning or add a shell action to the dashboard.
Approval controls require the exact implemented server route; fixture controls
cannot appear in production.

## Verification and exit

Test schema/permission rejection, prompt injection, budget exhaustion, duplicate
step replay, expired/revoked approval, changed args, provider crash/timeout,
lease fencing and capacity release. PostgreSQL tests cover concurrent reservations
and receipts. Test client reconnect around approval/execution and old chat/CLI
compatibility. Real read-only tool flow must have a trustworthy receipt; external
effects require separate explicit authorization and are not a default exit gate.

Exit with the documented selected registry, bounded loop, accurate capability,
reliable failure states and no implicit privilege from model output. Stop before
adding unselected integrations, schedules or unlimited autonomous execution.

## Implemented checkpoint mapping

- Registry/data: selected versioned read-only specs, strict typed arguments/results,
  scoped migration 0009 and immutable exact approval/receipt identity.
- Loop/compatibility: separate native ada-agent-v1 mode, explicit prompt compatibility,
  frozen bounded context, shared admission, short reservations and generation fencing.
- Action checkpoint: every selected read-only request gets exact human approval;
  no external write integration selected or authorized. Revocation and unknown
  recovery never claim cancellation or repeat an ambiguous execution.
- Clients/monitoring: Android exact preview/receipts and encrypted v6 GET-only
  restoration; admin closed aggregate counts with no private execution control.
- Verification: owned HTTP/schema/failure/PG concurrency and populated replay tests,
  actual client adapters, real local native tool receipts, staged emulator recovery.
  Consult [STATUS](STATUS.md) and [WORKLOG](WORKLOG.md) for actual results/skips,
  remaining target verification and migration installation boundary. Tests use
  synthetic disposable data; no external message or deployment is included.

Policy and exact bounds: [TOOLS-AND-AGENT-LOOP.md](../docs/TOOLS-AND-AGENT-LOOP.md).
Stop here; no unselected integrations or later phase is implemented.

Final local gate (2026-10-11 UTC): PostgreSQL/SQLite **440 passed/18 documented
skips**, Ruff/compileall; Android **155 units**, lint/debug/test APK, actual focused
HTTP approval/denial and two force-stop stages with strict cold launch, including
compact landscape/1.5× text; web **53 units/six PostgreSQL Chromium scenarios**;
real local qwen3.8:27b **three read-only native flows** with owned durable receipts.
Original 55 paths/76 schemas, released migrations and later phase files survive.
Head 0009 is not installed in the application; S24 FE/Android 16, release HTTPS,
manual accessibility and sustained target resource/model checks remain explicit
in STATUS/WORKLOG. No external write, later phase or deployment occurred.
