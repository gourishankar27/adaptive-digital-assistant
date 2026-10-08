# Phase 15 — opt-in interaction learning and continuity

Status: planned. Prerequisites: Phases 11, 13 and 14.
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
