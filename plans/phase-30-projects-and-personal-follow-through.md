# Phase 30 — projects and personal follow-through

Status: **Optional proposal; planning only.** Inputs: 23 relevance, private scopes,
explicit owner review and Phase 18 erasure. Phase 27 is needed only for reminders; 28 optional.
Addresses useful daily outcomes behind G-23, not a required addition to every ADA
installation. Follow [shared rules](FUTURE-ROADMAP.md). Confirm task priorities
with the owner before selecting this phase.

## Outcome

ADA helps the owner resume a project, choose a next action and follow up on a
commitment. A useful brief can say what changed, what is open and what needs a
decision, with links back to actual owner material. It is not external task
execution or a claim that a suggestion is an agreed commitment.

## Checkpoints

- **A — explicit structured work.** Add owner/scoped goals, tasks, status and
  optional due date/timezone, each created or changed by explicit owner action.
  A model suggestion is a draft requiring confirmation. Distinguish planned,
  done, deferred and unknown; an elapsed date cannot silently mark a task done.
  Keep revision history and original source links without making tasks factual
  evidence merely because the model proposed them.
- **B — review from chat.** Offer an exact "Save next action" preview after a
  useful conversation when requested/enabled. Show scope, description, time and
  reminder choice before submission. Reserve IDs for duplicate/unknown-outcome
  recovery; reconnect performs GET, never a new task POST. No general tool can
  create a commitment from inferred intent or a retrieved document instruction.
- **C — brief and resume.** Generate an owner-requested project/day brief from
  selected authorized tasks and original source pins. Show overdue/open items,
  uncertainty and citations. Current task status and historical chat snapshots
  are different views; do not rewrite old completed answers. Cache by owner/scope/
  revision/epoch. The admin monitoring site never becomes a private task reader.
- **D — deliberate follow-up.**25 can ask about an unresolved task when permitted.
  Only27 creates a durable reminder; an LLM saying "I'll remind you" is not a
  scheduled event. Completion/dismissal pauses related question/reminder drafts.
  No email, calendar write or filesystem automation in this phase.

## Data/interfaces and failure tests

Proposed owner-bound task/goal/revision/receipt entities and typed create/update/
list/brief operations. Add after actual migration head and extend erasure/backup/
epoch inventories and scope locks. Preserve fact/source trust; model status is
not user completion. Test wrong owner/scope, concurrent edits, duplicate Save,
time ambiguity, source deletion, cancelled/late brief, revoked sessions and
restore of tasks with automation paused. Use PostgreSQL revision/idempotency
checks, actual API/client recovery and held-out scenario evaluation. Measure
completed useful workflows/owner acceptance, not tasks generated.

## Exit

The owner can create/revise/resume a real project and inspect exact origin/status,
with reliable offline/reconnect boundaries. Reminders are absent unless Phase 27 exists.
No external action, shared project access or automatic commitment is implied.
