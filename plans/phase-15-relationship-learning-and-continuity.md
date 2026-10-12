# Phase 15 — opt-in interaction learning and continuity

Status: implemented; local checks and remaining targets recorded in STATUS/WORKLOG.
Prerequisites: Phases 11, 13 and 14 are present in source; intended installation
and physical-device/model quality gates remain separate.
Apply STANDARDS and CODEX-WORKFLOW. Relationship state is per-user interaction
preference history; it is not a substitute for knowledge scope or authorization.

## Goal

Improve continuity from evidence-backed episodes and repeated user preferences,
with consent, review and reset. A single exchange must not create a permanent
relationship rule, and generated recollection must never claim an unsupported
shared experience.

## Data and learning checkpoints

Record an InteractionObservation with owner, allowed context, source references,
time, confidence class, extraction/policy version and purpose. Distinguish explicit
statements, repeated observations and weak inference. Generated interpretations
remain proposals and retain their original source lineage.

Choose a documented configurable threshold for repeated observations from
independent interactions; validate it empirically rather than calling a numeric
threshold proof. Do not count retries, copied summaries or one event referenced
three times as independent evidence. User-explicit preferences override learned
ones. Weak inferences remain tentative/expiring and cannot create enduring rules.

Add opt-in enrollment, pause, view, approve/reject, edit and reset controls.
Learning can propose an interaction preference through the review mechanism;
only a validated user decision promotes it. Account-wide reuse must be a clear
choice and must not export project facts/private conversation content. Reset
removes learned state and suppresses reuse through derived indexes/caches according
to the implemented policy, while preserving only required minimal audit metadata.

## Continuity behavior

Use authorized source-linked episodes to recall relevant context with clear
uncertainty and citations where available. Keep generated summary and original
evidence distinct. Do not invent a shared history, present a guess as “I know
you,” or imply exclusive dependence. A warm response can acknowledge the user's
work without adding unsupported recollections or manipulative bond language.

Define deterministic precedence: explicit current instruction, explicit selected
preferences, reviewed learned preferences, defaults/session affect. None can
change factual conflict handling, memory authorization, tools or admin policy.
Freeze the selected version in a request snapshot and keep retry behavior stable.

## UI, verification and exit

Android settings explain what is learned, where it applies, evidence, uncertainty
and how to disable/reset it. Avoid numeric attachment/bond displays. Admin gets
aggregate operational counts only, no private relationship profile by default.

Test consent-off operation, opt-out/reset propagation, repeated-observation
deduplication, explicit override, stale proposals, cross-scope/private-history
leakage, false recollection, generated trust and completed replay. Run populated
migrations, PostgreSQL, prompt compatibility and real client review flows. Evaluate
continuity against source-linked cases with known omissions/conflicts.

Exit with user-controlled, inspectable learned preferences and evidence-backed
continuity. Record evaluation limits and unresolved retention requirements.
No automatic factual promotion, emotion diagnosis or unreviewed permanent rules.

## Implemented checkpoints and remaining targets

- [x] Owner/scope/source/time/version/purpose observations with original trust;
  selected completed user interactions only, no background classifier.
- [x] Configurable independent-interaction gate, retry/copy deduplication,
  tentative weak expiry and synthetic comparison of thresholds 3 and 4.
- [x] Opt-in/pause/view/approve/reject/edit/reset, explicit account reuse choice,
  reviewed source lineage and minimal durable same-key receipts.
- [x] Explicit instruction/settings precedence, bounded exact episode-source
  continuity, uncertainty/citations/omissions and frozen retries/replay.
- [x] Android Settings/recovery and private-input-free admin operation counts.
- [x] Populated migration/native constraints/concurrency, prompt/contract
  compatibility and real HTTP client review/restart flows (see actual run details).
- [ ] Intended backed-up application installation of 0012; physical Samsung S24 FE
  / Android 16, HTTPS/network transitions and manual TalkBack/accessibility.
- [ ] Representative consented preference accuracy/continuity quality, native-model
  wording/resources and final account/backup/historical-snapshot retention policy.

See [implemented policy](../docs/INTERACTION-LEARNING-AND-CONTINUITY.md). Reset
deletes live derived learning; historical chat/request snapshots remain for exact
replay and are explicitly disclosed. Later phase files remain planned.
