# Phase 13 — episodic memory and durable consolidation

Status: implemented; local exit gates passed; target verification remains.
Prerequisites: Phases 08 and 11 verified against source/contracts/tests;
Phase 10 is present but remains optional and disabled by default.
Apply STANDARDS and CODEX-WORKFLOW. Raw sources remain the provenance foundation.

## Goal

Create source-linked episodes/summaries and restartable maintenance jobs for
continuity without replacing explicit claims or rewriting chat history. A summary
is model-generated interpretation; it cannot silently become factual authority.

## Checkpoints and data

Define Episode with owner/scope, authorized conversation/event/version references,
time range, source hashes, summary version/model and provenance mapping. Store
generated summary as generated content. Keep compact structured tags separate
from exact supporting evidence. A summary of multiple conversations may use only
their same authorized scope; shared knowledge does not imply shared persona or
private conversation history.

Implement a durable job record with owner/scope, immutable input IDs/hashes,
kind/version, lease/attempt, checkpoint, status and result receipt. Reserve/claim
and commit in short transactions; extraction runs outside them. Restart uses
fencing and idempotent checkpoints, not a second untracked consolidation. Start
with a bounded worker in the existing process; a separate inference process
requires shared admission control before launch.

Jobs can generate episode summaries, rebuild derived indexes and submit memory
proposals to Phase 11. They do not approve proposals, erase evidence, resolve a
conflict as truth or alter valid-time history. Deduplicate proposed work and
record stale input when sources/policy have changed. Failed work leaves prior
published versions available and partial output unpublished.

## Retrieval and UI

Separate episodic continuity from claim/document factual retrieval. Use episodes
as bounded navigational/summary hints, with links to original sources and honest
generated labeling. A factual answer still requires original authorized evidence.
Freeze the selected episode/source mapping in request context; no generated
summary may smuggle another scope's history into a conversation.

Add an Android history/episode view where the client exists and an admin job
metadata view if Phase 06 exists. Show queued/running/completed/failed/stale
states and measured times. Do not label a queued summary “remembered truth” or
display raw private consolidation input in admin monitoring.

## Verification and exit

Test job crash before/after commit, lease expiry, duplicate job key, stale worker,
model failure, capacity admission, source-hash change, cross-scope input and
generated-summary citation mapping. Test that consolidation never creates an
endorsed claim without Phase 11 review. Use PostgreSQL for concurrency and
populated migrations, plus source/replay compatibility and real job lifecycle.

Evaluate summary faithfulness/omissions on a documented corpus with exact source
checks; do not substitute fluent wording for evidence. Exit with restartable
bounded jobs and inspectable source-linked episodes. Automatic cleanup/deletion
and unbounded background processing remain outside this phase.

## Checkpoint evidence — 2026-10-11

- [x] Owner/scope source-linked generated episodes, exact original hashes and
  code-point spans, conversation/event references, half-open time range and
  version/model/provenance map. Tags and omissions remain separate from support.
- [x] Migration 0010 adds literal owner/scope constraints without changing earlier
  migrations. Populated upgrade, native foreign keys, lower-history preflight,
  old chat replay and Alembic model/schema consistency run on PostgreSQL/SQLite.
- [x] Explicit durable jobs reserve, claim and atomically publish with 120-second
  leases, three tracked attempts, policy/source dedup and fencing. Model work
  runs outside database transactions and shares existing process admission.
  Crash before/after commit, shutdown, lease expiry, stale attempts, source/policy
  changes, capacity and partial-batch/model failures are covered.
- [x] Summary, pending Phase 11 proposal and scoped lexical projection rebuild
  flows work. Tests enforce no claim endorsement until separate explicit review;
  original evidence, prior episodes and valid-time history are retained.
- [x] Bounded navigation-context request snapshots freeze exact authorized maps.
  The explicit architecture decision keeps episodes separate from ordinary chat
  prompts and factual evidence candidates; no implicit prompt upgrade occurs.
- [x] Android history/episodes and encrypted v7 exact-key recovery (v1–v6 readable)
  use authenticated HTTP only. Admin's newest-25 metadata view has no private
  source/input/output text. Measured queued/running/completed/failed/stale states
  are distinct from missing/unconfirmed outcomes.
- [x] Four-case documented synthetic evaluation runs through actual durable jobs
  on migrated PostgreSQL, including native qwen3.8:27b. Exact original support,
  omissions/markers, attribution and uncertainty were checked independently;
  small-corpus success is not broad entailment/truth/quality evidence.
- [x] Full PostgreSQL/SQLite 516 passed/19 expected skips; Ruff 115 files clean;
  Android 164 units, lint/debug/test build and actual emulator HTTP/force-stop/
  cold launch; web clean install/contracts/typecheck/lint/54 units/build and six
  PostgreSQL Chromium cases. Detailed actual runs, corrected failures, skips
  and target limits remain in STATUS/WORKLOG.
- [ ] Explicit application head-0010 installation and representative operational
  checks; Samsung S24 FE/Android 16, minimum API 26, release HTTPS/short-idle
  behavior, TalkBack/manual accessibility and sustained worker resource/load
  verification. No physical phone was attached; release/distribution/deployment
  and later phases were not performed.

See [implemented policy](../docs/EPISODES-AND-CONSOLIDATION.md),
[status](STATUS.md) and [work log](WORKLOG.md).
