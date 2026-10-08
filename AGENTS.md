# ADA engineering rules

Read README.md, docs/ARCHITECTURE.md and the current migration/test state first.
Implement only the requested milestone. Do not claim planned mobile inference,
memory extraction, or tools are implemented.

- All private reads and writes require an authenticated owner.
- Personality changes expression, never ownership or permissions.
- Model output is not factual authority or authorization.
- Never connect native clients directly to Ollama or PostgreSQL.
- Preserve request IDs, snapshots, source trust and migration history.
- Never run network inference inside an open database transaction.
- Add invariants and failure tests before expanding write paths.
- Run pytest and ruff; run PostgreSQL fixtures for concurrency/schema changes.
- Use one Uvicorn worker until admission control is shared across processes.
- No deployment or external messages are authorized by this file.
