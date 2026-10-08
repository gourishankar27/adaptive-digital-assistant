# Phase 14 — explicit preferences and bounded session affect

Status: planned. Prerequisite: Phase 07. Apply STANDARDS and CODEX-WORKFLOW.
Static warm/caring personality is already available and does not wait for this
phase. Here “affect” means computational expression state, not biological feeling.

## Goal

Give the user explicit control over interaction preferences and let validated,
short-lived session signals modestly adjust expression. Truth, authorization,
evidence confidence, memory selection and tool policy must remain independent.

## Checkpoint A — preference controls

Define explicit preferences for verbosity, initiative, formality, humor and
interaction cadence, using a small allowlisted schema and documented precedence
over learned suggestions. Keep source/review receipt and user reset/edit controls.
Distinguish settings for one conversation/profile/scope from deliberately
account-wide preferences. Project/private facts never become global preferences
implicitly. Do not reuse personality ID as a permissions principal.

Preserve existing conversation snapshots. If changing expression for an active
conversation is supported, create an explicit versioned/audited update contract
that respects in-flight requests; do not mutate saved profiles behind history.
Android settings show clear scope and “applies to future replies” behavior.

## Checkpoint B — bounded session state

Choose a small expression vector such as warmth, focus, energy, playfulness and
concern with fixed ranges. Define deterministic validation, maximum change per
turn, decay/defaults and session expiry. Model-emitted signals are proposals;
reject malformed/unknown values and clamp accepted updates. The model never
writes arbitrary affect columns or changes permission/trust fields.

Partition state by owner/profile/conversation/session. Snapshot the expression
state used by a request so failed/completed retries preserve it. Keep minimal
provenance/reason codes without unnecessary sensitive psychological profiles.
An inferred mood is not a diagnosis or a durable fact about the user. Do not
display an invented happiness/bond score or claim ADA has literal feelings.

## Prompt and data compatibility

Add migrations/config as required and an explicit prompt policy version. Maintain
supported v3 retrieval and older saved prompts via a tested compatibility matrix;
do not let a new current-version constant disable old retrieval accidentally.
Keep model/context budget, exact evidence and request fingerprints intact.
State may influence wording, never whether a source is true, who owns it or which
tool/action is allowed. The user can disable dynamic state and reset it.

## Verification and exit

Test ranges, malformed signals, transition bounds, decay, expiry, reset, explicit
preference precedence, cross-user/session isolation, in-flight update conflict
and identical retry expression. Inject signals that ask for admin access, truth
overrides or tool execution and confirm they are rejected. Test prompt upgrades,
old v3 retrieval and client accessible controls with real API checks.

Exit with inspectable bounded state and user-selected preferences, accurate
capabilities and no unsupported psychological claims. Learned relationship
preferences and automatic long-term inference remain Phase 15.
