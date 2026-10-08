# Validation record — 2026-10-08

Environment: Linux, Python 3.12.14. This is not the target Windows/GPU machine.

## Completed

- `pytest -q`: 23 passed, 14 skipped. The skipped cases are PostgreSQL versions
  of the database tests; no ADA_TEST_DATABASE_URL was available.
- Ruff lint and formatting checks passed.
- Migration 0001 applies to fresh SQLite databases, is repeatable at head, and
  matches ORM metadata through `alembic check`.
- PostgreSQL migration SQL compiles, including the partial unique index and
  composite ownership/request foreign keys. This is not a PostgreSQL execution test.
- Ollama HTTP adapter tested with simulated responses: request format, usage,
  unavailable/missing model, timeout, malformed/incomplete answers, and unexpected
  tool calls. No actual model weights or GPU inference ran.
- Cross-user reads/writes fail; another user's personality cannot be selected.
- Database constraints reject cross-user personality links.
- Concurrent turns on a conversation are rejected; full model capacity returns 503.
- Completed retries do not regenerate; failed retries do not duplicate user events.
- Interrupted-request recovery rejects an old attempt's late response.
- Context remains bounded and contains complete pairs from only its conversation.
- Profile snapshots survive later profile record changes.
- Real Uvicorn HTTP process restart smoke check passed with the fake provider and
  SQLite: authentication, conversation, stored reply, and duplicate-request replay
  survived process termination and restart.

## Not verified here

- PostgreSQL runtime/locking behavior: attempted local startup was blocked because
  the environment cannot create/switch to an unprivileged database OS user. The
  PostgreSQL test fixtures are included for the target environment.
- Native Windows PowerShell execution and Docker Desktop startup.
- Qwen model availability in the user's installed Ollama, actual memory placement,
  throughput, model quality, and concurrent-user latency on the laptop.
- Android/iOS clients and local models, which are not implemented in this milestone.

The test client emits a dependency deprecation warning about its HTTP transport;
tests pass. The pinned dependency file records the versions used by this release.
Run the PostgreSQL tests and a real-model smoke conversation on Windows before
considering the deployment exit criteria complete.
