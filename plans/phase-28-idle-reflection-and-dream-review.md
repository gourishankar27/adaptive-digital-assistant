# Phase 28 — idle reflection and dream review

Status: **Initial reports/questions job set implemented and locally verified; native summaries disabled.** Inputs: 23 evaluation, 25 question drafts,
26 availability/resource budgets, 27 durable consent/scheduling, 13 consolidation,
11 review and Phase 18 erasure. G-25/G-35/G-36/G-38. Follow
[shared rules](FUTURE-ROADMAP.md). Existing explicit background jobs are reused.

## Outcome

When the owner is not actively using ADA, bounded local jobs organize selected
material and prepare useful drafts. The owner can later inspect what was produced,
its sources and omissions. "Dreaming" is a user-facing name for these jobs, not
consciousness, unrestricted thought, model training or an archive of hidden reasoning.

## Checkpoints

- **A — consent and input policy.** Owner chooses scopes, included source types,
  lookback window, allowed hours, job kinds, resource budget and whether an empty
  queue may do nothing. Automatic selection from completed turns is a new opt-in
  capability, separate from existing selected-source extraction. Unreviewed model
  material cannot become support for an endorsed personal fact. Sources are pinned
  by owner/scope/version/hash and revalidated after selection and before publication.
- **B — idle and foreground priority.** Proposed initial eligibility: 15 min without
  authenticated foreground activity, no admitted foreground inference, AC power,
  sufficient disk and acceptable measured thermal/memory budget. Idle refers to
  ADA activity, not a screen/keyboard surveillance feature. Unknown safety state
  skips discretionary work. Begin with a maximum 10 min nightly run and three jobs;
  tune only with measurements and explicit settings. One shared inference slot;
  foreground arrival stops new dispatch and requests cooperative cancellation of
  the current background unit. Bound units/deadlines and measure cancellation;
  if provider work does not stop promptly, disable that background job class.
- **C — small useful v1.** Reuse13 for generated episode-summary drafts; create
  report-only unresolved-thread/possible-contradiction items; reuse Phase 25 for suggested
  questions. Represent conflicting sources and uncertainty, not a hidden chosen
  truth. These artifacts stay in an owner review area. Later opt-in memory proposal
  drafts can reuse Phase 11 with an independent evaluation checkpoint and explicit review.
  No automatic claim acceptance, preference mutation, source correction/deletion,
  web research or external action. Full index rebuilds remain separate bounded
  maintenance jobs, not compulsory nightly work.
- **D — deduplication and recovery.** Deterministic source-set/policy/job keys,
  leased occurrences, bounded retries, stale-source rejection and publication
  fences reuse Phase 27/13 patterns. Owner stop, consent/device revocation and data epoch
  changes suppress current and queued work. A restored queue is paused. Never
  requeue an unknown output under a fresh ID to appear successful.
  Respect retained job/proposal quotas; dedup and suspend visibly at capacity
  instead of looping, silently dropping receipts or inventing an age-deletion
  policy. Any future archive/compaction must preserve reviewed content and replay.
- **E — review product.** "While you were away" lists artifacts, source links,
  completion time, measured duration and fixed rationale category. Explain skipped/
  cancelled jobs and zero useful findings honestly. Owner may keep a generated
  summary, answer a question, review a separate memory proposal or discard. No raw
  hidden reasoning or imagined reflections. Dismissal does not erase original
  evidence; Phase 18's explicit content deletion remains the erasure mechanism.

## Proposed data/interfaces

Reflection policy/consent, pinned source selection, job/occurrence receipt and
typed summary/report/question artifact. Extend existing leased jobs only after
checking state-machine compatibility; avoid a second scheduler. Encrypted owner
storage, backup/erasure/epoch inventory and exact source authorization apply to
every artifact. Admin sees budgets/counts/states, not the private review text.
No capability flips until the respective auto-selection/draft flow is tested.

## Failure tests, evaluation and exit

Test foreground arrival mid-generation, ignored provider cancellation, deadline/
resource pressure, offline model, revoked consent/device, source correction or
deletion during a lease, duplicate run, wrong-owner source and crash-before-publish.
Assert no factual claim is created and no network egress occurs. Use real
PostgreSQL fencing and a constrained local model probe, plus a host soak with
foreground chat/backup interference. Measure useful accepted artifacts, false
contradiction rate, duplicate questions, GPU time and foreground latency delta.

Exit only if artifacts are useful and background interference meets the measured
budget. A valid outcome is a smaller enabled job set or disabled reflection when
capacity is inadequate. Do not promise that unattended generation continually
improves model weights or that fluent summaries prove accurate memory.


## Implementation record — 2026-10-21

The selected initial job set is rule-only reports and Phase25 catalogue drafts.
Generated-summary schema/adapter/Phase13 Keep are implemented and exercised with
explicit synthetic providers, but production summary generation stays disabled.
The constrained public native probe measured client cancellation return, not
server GPU cancellation, useful output or foreground native-inference interference.
This uses the exit provision allowing a smaller enabled job set. No automatic
memory-proposal generation, later phase or deployment is included.

| Checkpoint | Implemented boundary | Evidence location |
|---|---|---|
| A | Separate owner automation/reflection/completed-turn consent; owned scopes, source types/lookback, time/job/resource budgets, version/hash/current availability pins | `test_reflection_policy.py`, `test_reflection.py`, source/read-barrier failures |
| B | Existing observer/dispatcher/worker;15-minute ADA activity threshold, unknown-safe skip, shared slot/cooperative stop, ignored-cancellation suspension | failure/provider tests, public native probe and bounded host exercise in STATUS |
| C | Owner-marker/possible-change reports, catalogue drafts, optional generated episodes; no factual/preference/source/external writes | evaluation and review tests; model summaries remain disabled |
| D | Stable canonical source-set keys, native leases/attempt fences, bounded retry/capacity, origin/consent/epoch/off suppression, restore quarantine | failure/storage/recovery tests, released-v4 compatibility, exact Android receipt recovery |
| E | Android While you were away: choices, provenance, source inspection, omissions/duration/empty outcomes, Keep/Discard/explicit question opening; admin fixed aggregates only | controller/Keystore tests, separate-emulator real HTTP force-stop stages and real Chromium monitoring |

Actual dated results, failures/corrections, skips and final target gates are in
[STATUS](STATUS.md), [WORKLOG](WORKLOG.md) and
[the operational guide](../docs/IDLE-REFLECTION-AND-DREAM-REVIEW.md). Do not interpret
an implemented checkpoint as installed-host, physical-device, representative
private-data or native-summary activation verification.
