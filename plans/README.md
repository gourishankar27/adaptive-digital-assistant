# ADA implementation plans

These plans continue the implemented Phase 0–2 server. Phase numbers in the earlier
architecture prompt were suggestions; this directory uses the actual release
history and puts usable interfaces before larger backend additions.

This update writes plans and fixes a Windows test fixture. It does not implement
an Android app, admin API, admin website or any later backend phase.

## Start here

Read [CURRENT-STATE.md](CURRENT-STATE.md), [STANDARDS.md](STANDARDS.md),
[CODEX-WORKFLOW.md](CODEX-WORKFLOW.md), [STATUS.md](STATUS.md), then one phase file.
Root `AGENTS.md` carries these rules into Codex sessions. Nested
[AGENTS.md](AGENTS.md) applies while editing this directory.

Every phase specifies a goal, prerequisites, bounded checkpoints, data changes,
interfaces, failures, verification and exit criteria. Proposed names and routes
are designs until implemented and exported in OpenAPI. The existing
`/v1/capabilities` must continue to report working features accurately.

## Phase order

| Phase | File | Result | Prerequisites |
|---|---|---|---|
| 02A | [phase-02a-windows-test-fix.md](phase-02a-windows-test-fix.md) | Portable installer test fixtures; close the reported failures | Existing Phase 2 |
| 03 | [phase-03-ui-foundations.md](phase-03-ui-foundations.md) | Typed client contracts, shared UI decisions and reproducible app scaffolds | 02A |
| 04 | [phase-04-android-chat-mvp.md](phase-04-android-chat-mvp.md) | Android connection, authenticated chat, history, retries and citations | 03 |
| 05 | [phase-05-admin-monitoring-api.md](phase-05-admin-monitoring-api.md) | Explicit admin authorization and private monitoring metadata | 03 |
| 06 | [phase-06-admin-web-ui.md](phase-06-admin-web-ui.md) | Browser dashboard for backend health and request inspection | 05 |
| 07 | [phase-07-android-memory-and-personality.md](phase-07-android-memory-and-personality.md) | User memory/evidence screens and current static personality controls | 04 |
| 08 | [phase-08-document-ingestion.md](phase-08-document-ingestion.md) | Versioned document uploads, chunks and cited document retrieval | 03, existing Phase 2 |
| 09 | [phase-09-entities-and-aliases.md](phase-09-entities-and-aliases.md) | Scoped canonical entities with explicit ambiguity handling | 03, existing Phase 2 |
| 10 | [phase-10-embeddings-and-hybrid-retrieval.md](phase-10-embeddings-and-hybrid-retrieval.md) | Measured semantic retrieval alongside the lexical baseline | 08; 09 for entity-aware features |
| 11 | [phase-11-memory-proposals-and-review.md](phase-11-memory-proposals-and-review.md) | Model suggestions reviewed before durable memory writes | 07, 08; 09 for canonical links |
| 12 | [phase-12-tools-and-agent-loop.md](phase-12-tools-and-agent-loop.md) | Bounded agent execution with server permissions and receipts | 03; 04/06 for client controls |
| 13 | [phase-13-episodes-and-consolidation.md](phase-13-episodes-and-consolidation.md) | Provenance-linked episodes and restartable consolidation jobs | 08, 11; 10 optional |
| 14 | [phase-14-interaction-preferences-and-affect.md](phase-14-interaction-preferences-and-affect.md) | Explicit interaction preferences and bounded session tone state | 07 |
| 15 | [phase-15-relationship-learning-and-continuity.md](phase-15-relationship-learning-and-continuity.md) | Opt-in preference learning and evidence-based continuity | 11, 13, 14 |
| 16 | [phase-16-streaming-and-cancellation.md](phase-16-streaming-and-cancellation.md) | Durable incremental replies and explicit generation cancellation | 04; 06 for monitoring |
| 17 | [phase-17-voice-interface.md](phase-17-voice-interface.md) | User-controlled voice input/output on Android | 04, 16 |
| 18 | [phase-18-security-and-operations.md](phase-18-security-and-operations.md) | Device credentials, deletion/retention, recovery and shared capacity | 05, 06; whichever feature phases exist |
| 19 | [phase-19-edge-and-external-integrations.md](phase-19-edge-and-external-integrations.md) | Optional local mobile models and selected integrations | 12, 18; measured device requirements |

Recommended next work: close 02A on Windows, implement 03, then 04. Implement
05–06 for admin monitoring and 07 for user memory management. Later backend
phases can then be chosen independently according to their prerequisites.
Streaming can be brought forward after 04; voice can follow streaming without
waiting for all memory phases. Phase numbers identify documents, not a requirement
to build every earlier numbered feature. Dependencies are the actual gates.

There is no calendar estimate here: app tooling, phone hardware and real-model
performance are not yet measured. Complete one checkpoint and keep ADA runnable
before starting another.

## Two UI products

`apps/android/` is the user's Kotlin/Compose application. It presents chat, source
cards, owned scopes, memory forms and expression settings. Its primary screens
use ordinary product language. Debug traces are an optional detail view.

`apps/admin-web/` is a React/TypeScript application for an authorized operator.
Its first release is read-only monitoring: health, capacity, request states,
timings, errors and retrieval budget summaries. It does not grant unrestricted
access to users' private text, run shell commands or rotate credentials.

Both clients call the ADA API. PostgreSQL remains authoritative. Neither client
contacts Ollama, a database port, or a model provider directly.

See [UI-SPEC.md](UI-SPEC.md) for screen states, accessibility, authentication,
request recovery and consistent presentation.

## Give one phase to Codex

From the repository root, use a prompt like this, changing the phase path:

```text
Read AGENTS.md, README.md, docs/ARCHITECTURE.md, plans/CURRENT-STATE.md,
plans/STANDARDS.md, plans/CODEX-WORKFLOW.md and plans/STATUS.md.
Implement only plans/phase-04-android-chat-mvp.md.
Inspect the current code, OpenAPI contract and test baseline first. Verify the
phase's prerequisites. Complete its checkpoints with working code, appropriate
failure tests and documentation. Preserve ownership, evidence, temporal queries,
request IDs, prompt snapshots and existing CLI behavior. Use real API adapters;
keep test fixtures out of production paths. Record checks actually run, skipped
checks and remaining device/model verification. Update the status/work log and
stop at this phase. Do not implement later phases or deploy anything.
```

For Phase 03, select that file first. A prompt is a scope instruction, not a
substitute for the repository's current state or server-side authorization.

## Planning records

- [STATUS.md](STATUS.md): phase/checkpoint progress and verification evidence.
- [WORKLOG.md](WORKLOG.md): append-only summaries of each implementation session.
- [DECISIONS.md](DECISIONS.md): architecture choices and unresolved inputs.
- [SOURCES.md](SOURCES.md): official references checked for planning, with a date.

Keep secrets, private message text and real source quotes out of these records.
