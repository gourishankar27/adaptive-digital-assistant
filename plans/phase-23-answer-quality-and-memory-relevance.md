# Phase 23 — answer quality and memory relevance

Status: **A–E implemented with a measured opt-in/disabled decision; local verification
recorded in STATUS/WORKLOG.** V4 remains default, v5 requires explicit upgrade,
semantic remains disabled, and native embedding/independent review/physical checks
remain open. No deployment. Inputs: Phase 20's held-out scorecard and existing
claim/document/entity/proposal/episode/expression/continuity paths. G-12/G-13/
G-18/G-23/G-36. Follow [shared rules](FUTURE-ROADMAP.md). No live install or
physical phone is needed to evaluate disposable current-head fixtures.

## Outcome

ADA recalls relevant authorized information, asks when something is ambiguous,
handles dates explicitly, acknowledges uncertainty and improves after correction.
Prioritize useful answers over storing more text or merely changing the model.

## Checkpoints

- **A — measure the failures.** Extend existing evaluation cases with cross-chat
  continuity within an authorized scope, multiple projects, contradictory/dated
  claims, corrections, missing evidence, imported instructions and deleted sources.
  Record answer usefulness/citation entailment as well as recall/MRR and latency.
  Distinguish insufficient context, bad ranking and bad generation; keep a held-out
  set. Start with public/synthetic data; private evaluation is separately opt-in.
- **B — retrieval comparison.** Compare current lexical, subject/entity channels
  and existing exact hybrid ranking using an explicitly chosen installed embedding
  model/digest. Measure memory, index cost, prompt budget and fallback. Enable
  semantic retrieval only when held-out benefit justifies cost; a documented
  disabled decision is a valid exit. No automatic model download or new vector
  database is required. Test long histories and bounded candidate truncation.
- **C — time and clarification.** Add explicit timezone/reference-date handling
  for selected relative phrases such as yesterday/last week. Show resolved interval
  and ask for clarification on ambiguity. Do not silently map an interval to one
  existing point-in-time query. Version any interval API, define valid-time versus
  recorded-time semantics and preserve old `as of YYYY-MM-DD`/`--at` behavior.
  Contradictions remain visible; model preference cannot silently settle truth.
- **D — context and correction.** Select relevant original source excerpts through
  authorized continuity rather than adding generated summaries as facts. Improve
  omission/uncertainty explanations and correction affordances. A user correction
  creates a reviewed source/claim update; old prompt/evidence snapshots remain.
  Separate volatile conversational context from durable personal memory. Prompt
  improvements need a version, held-out comparison and explicit existing-chat
  upgrade; failed/completed retries do not silently use the new context policy.
- **E — review efficiency.** Make existing selected-source proposal review easier
  (duplicates, exact support, accept/edit/reject), without auto-approving. Automatic
  completed-turn selection belongs to Phase 28's opt-in draft jobs, not this checkpoint.
  A model comparison may inform selection; routing to additional providers or
  fine-tuning is not needed for this phase.

## Data and interfaces

Prefer versioned evaluation manifests, retrieval diagnostics and explicit temporal
options over new learned identity profiles. Any new stored interpretation/version
is owner/scope-bound and frozen into future request snapshots. Existing API defaults,
prompt versions, evidence origins and citation labels remain supported. Use22
sessions only as an adapter if already implemented, not a new auth prerequisite.

## Verification and exit

Require zero known ownership/permission/deleted-source leaks and exact source spans
in the held-out corpus. Report metric deltas and uncertainty/sample sizes, not one
aggregate intelligence score. A proposed relevance improvement needs no regression
in exact evidence, acceptable measured latency and visible ambiguity handling.
Evaluate timezone/DST/boundary dates, Unicode offsets, future corrections, malicious
source text, unsupported prompt versions and deterministic same-request replay.
Run affected PostgreSQL/API/client checks. Record local-model versus fixture evidence.
Exit with a measured configuration/version decision and actionable remaining cases;
do not claim general factual accuracy or silently enable automatic extraction.

## Implementation record — 2026-10-16 America/Phoenix

Prerequisites were verified against current source, head0016, exported OpenAPI
and existing retrieval/learning/proposal/evaluation tests. No prerequisite phase
or physical device was required. Source base is `fed5d4b` plus the pre-existing
Phase21/22/setup working tree; this phase preserves that work.

- **A complete:** frozen16case public corpus (8development/8regression holdout),
  fixture and32native qwen answers, exact evidence/isolation checks and explicit
  Codex qualitative review of usefulness/entailment/uncertainty. No independent
  human review or general factual accuracy claim. Failures are retained by type.
- **B complete with disabled exit:** reran lexical/subject/entity/exact-hybrid
  fixture comparison, budgets/truncation/fallback tests and recorded resource
  limits. Matching supported embedding weights were absent; native embedding
  comparison/index/GPU cost is skipped, no download/semantic activation.
- **C complete:** explicit IANA timezone/reference, yesterday/prior Monday-week,
  displayed real interval, ambiguity clarification, half-open valid-time overlap
  against current recorded state. Claim-only version; old point APIs unchanged.
- **D complete with opt-in decision:** v5 ranked original history/authorized
  continuity, frozen omissions, explicit audited upgrade, source/correction links,
  no automatic save. Long-history context improved; native date/brevity regressions
  mean v4 remains default. Failed/completed replay/version fences tested.
- **E complete:** exact loaded suggestion grouping/conflict cues, retained support
  and separate accept/edit/reject; no automatic selection or approval.

See [the quality guide](../docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md),
[manifest](../evaluations/answer-quality-manifest-v1.json) and
[reviewed results](../evaluations/answer-quality-results-v1.json) for interfaces,
commands, denominators and actionable remaining cases. No later phase implemented.
