# ADA engineering rules

Read README.md, docs/ARCHITECTURE.md and the current migration/test state first.
For planned work, also read plans/README.md, plans/STANDARDS.md,
plans/CODEX-WORKFLOW.md, plans/STATUS.md and the single phase requested by the user.
The repository and current tests define what exists; future plan files do not.
Implement only the requested milestone. Do not claim planned mobile inference,
memory extraction, or tools are implemented.

- All private reads and writes require an authenticated owner.
- Personality changes expression, never ownership or permissions.
- Model output is not factual authority or authorization.
- Never connect native clients directly to Ollama or PostgreSQL.
- Preserve request IDs, snapshots, source trust and migration history.
- Migrations 0001, 0002 and 0003 are released history. Add migrations rather than editing them.
- Preserve old prompt snapshots and completed replay; prompt upgrades remain explicit and audited.
- Apply owner/scope/time checks before retrieved evidence enters candidates or model context.
- Never run network inference inside an open database transaction.
- Add invariants and failure tests before expanding write paths.
- Run pytest and ruff; run PostgreSQL fixtures for concurrency/schema changes.
- Serialize manifest and contract paths with forward slashes on every OS. Test Windows behavior.
- Use one Uvicorn worker until admission control is shared across processes.
- Android and admin clients use authenticated HTTP APIs; no direct database/provider access.
- An admin role must be enforced by the server. User names and personalities never grant it.
- Never store tokens, database passwords, raw private chats or source quotes in logs or plans.
- Keep Python, Android and web dependencies reproducible with the appropriate lockfiles/wrappers.
- Record implemented behavior, checks actually run, skips and unresolved limits in plans/STATUS.md
  and plans/WORKLOG.md. Preserve prior validation evidence instead of rewriting it as a new run.
- Do not implement a later phase merely because a dependency is missing. Report the gap and
  complete independent authorized work; request steering only for a material scope decision.
- Adding planning documents does not authorize building the planned applications.
- No deployment or external messages are authorized by this file.
