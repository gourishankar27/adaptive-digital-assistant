# ADA implementation plans

2026-10-24 Phase32 source/checkpoints: [Phase32 — private voice conversations](phase-32-private-voice-conversations.md)
records warm/calm feminine local speech, capture that continues across pauses,
and explicitly armed background/locked **Hello Ada** with shared session renewal.
Source is implemented for private evaluation; human wake trials missed and phase
exit/device/resource/license gates remain open. Current0022/77 tables/64 owner-content,
backup-v8, Android27/journal19 and additive OpenAPI166/220. Ordinary builds retain
platform speech. See STATUS/WORKLOG and the [guide](../docs/PRIVATE-VOICE-CONVERSATIONS.md).
No installed database/normal-phone upgrade or deployment.

Selected19A/31 source now adds a measured on-device draft study/signed receipt
protocol and bounded text-PDF ingestion. Both mobile candidates failed quality;
19A activation/exit remains open, local generation disabled. Phase31 OCR is disabled.
Current head0021/76 tables/63 owner-content/backup-v7, Android25/journal18.
Phase31's bounded text-PDF implementation/automated exit is verified, including
the S24 FE real HTTP/Keystore/restart flow and confirmed public-sample readability.
TalkBack/personal-file acceptance remains pending. The conditional OCR checkpoint
is closed with OCR off.
See [PDF](../docs/PDF-INGESTION.md), [study](../docs/ON-DEVICE-DRAFTS.md) and dated
STATUS/WORKLOG. Earlier phase rows retain their planning/history context; no19B,
later milestone or deployment was implemented.

Current source includes Phase28 bounded idle reports and catalogue question drafts
with exact owner review, encrypted Android recovery and aggregate admin monitoring.
Head0019 adds five tables; global reflection and separate owner consent default
off. Model summaries stay disabled. Actual checks and target limits are in STATUS
and [the guide](../docs/IDLE-REFLECTION-AND-DREAM-REVIEW.md). Phase29 now adds the
speech study/interface contract and platform preview; new adapters await physical,
license and compatibility gates. Phase30 now implements explicit scoped work, reviewed Save, balanced briefs and
GET-only recovery with separately consented questions/reminders; head0020, Android24.
See [the guide](../docs/PROJECTS-AND-FOLLOW-THROUGH.md). Phase31 remains
planned; no deployment is included. Earlier summaries retain milestone boundaries.

These plans continue the implemented Phase 0–2 server. Phase numbers in the earlier
architecture prompt were suggestions; this directory uses the actual release
history and puts usable interfaces before larger backend additions.

Phase 03 implements typed existing contracts and Android/web connection and UI
foundations. Phase 04 adds authenticated Android conversations, chat, encrypted
request recovery and original source cards. Physical-phone and release checks
remain distinct from local verification. Phase 05 implements explicit grants,
audited metadata APIs and bounded provider health. Phase 06 implements the read-only
admin dashboard with selectable palettes. Phase 07 adds explicit Android memory,
exact evidence/correction recovery and new static personality profiles. Phase 08
adds bounded text/Markdown upload/version/chunk retrieval and Android document UI.
Phase 09 adds explicit scoped identities, aliases, historical links, reversible
merge and Android review/recovery. Phase 10 adds bounded exact hybrid retrieval,
kept disabled by default until real-model evaluation supports activation. Phase 11 adds explicit selected-source suggestions/review; Phase 12 adds selected
read-only tools, bounded separate agent runs and explicit approval/receipt recovery.
Phase 13 adds source-linked generated episodes and bounded durable consolidation
jobs, explicit Android history/recovery and read-only admin job metadata. Later
backend features remain planned.
Phase 14 adds explicit scoped preferences and opt-in bounded session tone,
request-frozen expression snapshots and Android Settings/receipt recovery.
Phase 15 adds opt-in selected-source interaction observations, explicit reviewed
learned defaults, source-linked continuity and Android consent/review/reset.
Phase 16 adds durable incremental replies, checkpoint/reconnect recovery, explicit
Stop and admin stream metadata. Automatic affect inference remains deferred.
The Windows/PostgreSQL rerun closes the 02A fixture gate;
see STATUS/WORKLOG for preserved historical and current evidence.

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
| 17-A | [phase-17-a-s24-fe-validation-and-hardening.md](phase-17-a-s24-fe-validation-and-hardening.md) | Implemented hardening/portable runner; physical voice gates remain open | 17 |
| 18 | [phase-18-security-and-operations.md](phase-18-security-and-operations.md) | Device credentials, deletion/retention, recovery and shared capacity | 05, 06; whichever feature phases exist |
| 19 | [phase-19-edge-and-external-integrations.md](phase-19-edge-and-external-integrations.md) | Optional local mobile models and selected integrations | 12, 18; measured device requirements |
| 20 | [phase-20-release-readiness-and-quality-baseline.md](phase-20-release-readiness-and-quality-baseline.md) | Implemented: separate legacy recovery, frozen scorecard and local readiness baseline; limits in STATUS | Source through 18 |
| 21 | [phase-21-private-network-connectivity.md](phase-21-private-network-connectivity.md) | Implemented: named Android origins/import/preflight, diagnostics and private-route rehearsals; actual deployment/target gates remain | 20 transport audit; 18 |
| 22 | [phase-22-password-login-and-sessions.md](phase-22-password-login-and-sessions.md) | Implemented password/session source; live enrollment/target checks pending | 20; 21 before remote use |
| 23 | [phase-23-answer-quality-and-memory-relevance.md](phase-23-answer-quality-and-memory-relevance.md) | Implemented/local checks: explicit intervals, review cues, measured opt-in v5; v4 default/semantic disabled; remaining limits in STATUS | 20; existing memory features |
| 24 | [phase-24-secure-web-research.md](phase-24-secure-web-research.md) | Proposed: approved public research, isolated egress and saved web citations | 20, 12, 18 |
| 25 | [phase-25-conversational-curiosity.md](phase-25-conversational-curiosity.md) | Proposed: personal follow-up questions, topic controls and later inbox | 20, 14/15; 23 preferred |
| 26 | [phase-26-always-on-operations-and-recovery.md](phase-26-always-on-operations-and-recovery.md) | Source and four-hour development soak passed; installed-host gates remain in STATUS | 20, 18; 21 for remote reachability |
| 27 | [phase-27-durable-scheduling-and-reminders.md](phase-27-durable-scheduling-and-reminders.md) | Implemented source: reviewed timezone schedules, durable inbox/receipts and foreground polling; default off/no push | 26 development gate passed; 13/18/22 source present |
| 28 | [phase-28-idle-reflection-and-dream-review.md](phase-28-idle-reflection-and-dream-review.md) | Implemented initial reports/questions and review; model summaries disabled, target limits in STATUS | 23, 25, 26, 27 |
| 29 | [phase-29-natural-local-speech.md](phase-29-natural-local-speech.md) | Study/interface and platform preview implemented; no new runtime/model; physical activation pending | 17/17-A source; later device/license evidence |
| 30 | [phase-30-projects-and-personal-follow-through.md](phase-30-projects-and-personal-follow-through.md) | Optional proposal: reviewed goals, next actions and useful briefs | 23; 27 only for reminders |
| 31 | [phase-31-pdf-ingestion-and-document-expansion.md](phase-31-pdf-ingestion-and-document-expansion.md) | Optional proposal: bounded text-PDF extraction; OCR separately gated | 08, 20; 23 evaluation |
| 32 | [phase-32-private-voice-conversations.md](phase-32-private-voice-conversations.md) | Proposed: owner-controlled long-form capture, natural feminine local voice and background/locked Hello Ada | 17/17-A, 22, 29; measured native activation |

For the 2026-10-16 planning proposal, start with
[FUTURE-ROADMAP](FUTURE-ROADMAP.md). It reviews the original
[gap list](GAPS-AND-FUTURE-PLANS.md), records corrections/additional prerequisites
and maps all original gaps. Physical-Android validation and iOS are excluded
from this review. Phase 19 remains conditional; new work starts at 20 without
renumbering or implementing prior optional milestones. These rows are plans,
not implementation authorization or claims of new capabilities.

Phase 04 stops at chat and source inspection. A separately selected Phase 07 can
add user memory management; Phase 05 supplies authorization/metadata and a separately
selected Phase 06 now provides the read-only monitoring dashboard.
Later backend phases can be chosen independently according to their prerequisites.
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

Phase24 now implements default-off approved public research with a demonstrably
isolated Docker broker, closed Python documentation/Wikipedia pilot, immutable
untrusted W citations, explicit imported notes and Android encrypted recovery.
Schema0016 is unchanged. Local results and remaining host/physical/native-quality
gates are in STATUS/WORKLOG and [the guide](../docs/SECURE-WEB-RESEARCH.md).
Phases25–31 remain planned; this source was not deployed.

Phase 11 now implements selected-source proposals with explicit Android review,
new endorsement evidence and reliable scoped review receipts. Automatic extraction
and approval remain disabled. Application migration 0008 and remaining target
checks are separate from implementation; see STATUS. Later phases remain planned.
