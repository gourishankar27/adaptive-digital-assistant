# Phase 13 — episodic memory and durable consolidation

Status: planned. Prerequisites: Phases 08 and 11; Phase 10 is optional.
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
