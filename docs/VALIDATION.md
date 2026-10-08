# Phase 2 validation — 2026-10-08

Environment: Linux, Python 3.12.14, the included pinned dependencies. This is not
the target Windows/GPU machine. Source version 0.2.0; schema 0003.

## Completed

- `pytest -q`: **60 passed, 50 skipped**, one dependency deprecation warning.
  Skips: 48 PostgreSQL fixture variants because no test server is available,
  plus two SQLite copies of PostgreSQL row-lock tests.
- Ruff lint and formatting passed for `src`, `tests`, `migrations` and `scripts`.
- Package 0.2.0 installs without new dependencies. The CLI exposes scoped search,
  request traces, fixed-time chat, retrieval bypass, source cards and index rebuild.
- Fresh SQLite migrations to 0003 and `alembic check` pass. Populated Phase 0/1
  upgrades preserve history, scope/source/claim IDs, prompt/style snapshots and
  completed request replay. Both original migration files are byte-identical.
- Migration 0003 backfills existing claims into the native search projection.
  SQLite FTS5 indexing, atomic claim/index writes, rebuild and rollback checks pass.
- Retrieval checks owner/scope, both valid-time bounds, user evidence trust,
  recomputed source hash, exact span/quote and derived projection consistency.
  Missing/changed evidence and future/out-of-scope records never enter context.
- Current/historical lookups, exact correction boundaries, future replacements,
  limited natural-date parsing and ambiguous-date behavior pass. Explicit memory
  times with equivalent timezone representations replay identically.
- Potential conflicting slot values are kept together or omitted. Oversized
  evidence is skipped without truncating quotes; smaller entries can fit. Whole
  prompt accounting includes baseline, runtime policy, complete history, evidence
  framing and the current input. Existing context-budget checks still pass.
- Requests bind content/time/retrieval options with domain-separated hashes while
  preserving default-option Phase 0/1 fingerprints. Changed options return 409.
- Failed retries preserve original messages/traces after correction. Completed
  retries preserve original responses/citations. Unknown labels receive warnings
  and no card. Authenticated request/trace reads enforce owner isolation.
- v1/v2 prompts retain their original context with retrieval disabled until an
  explicit, audited v3 upgrade. Style/history remain frozen; old failed retries
  are fenced by the revision change. In-flight prompt upgrades are rejected.
- Untrusted source content is passed as evidence data. Chat has no memory write
  tool; sources and model output cannot grant application permissions. These
  checks do not establish a real model's resistance to misleading source text.
- The installer validates both original migrations and all update destinations,
  accepts CRLF, backs up originals, preserves local configuration, rejects local
  edits/corrupt files, and replays safely. The complete generated manifest is
  checked against the original Phase 1 source bundle before packaging.
- OpenAPI is generated from actual routes, including citations, request/trace UUIDs
  and epoch-millisecond int64 fields. PostgreSQL migration and retrieval SQL
  compile, including GIN full-text search and composite foreign keys. Compilation
  is not a PostgreSQL runtime check.
- Real Uvicorn/HTTP process smoke passed with disposable SQLite and the fake
  provider: create Phase 1 history/memory, stop, migrate, replay old requests,
  explicitly upgrade v2 to v3, retrieve/cite evidence, correct a memory, restart,
  replay the frozen old citation snapshot, query current/historical values and
  reject another user's trace reads. `evaluations/http-upgrade-smoke.json` records
  the checks. The fake model echoes a test label; this verifies source mapping,
  not generated answer correctness.
- Original authentication, inference failure, admission control, source trust,
  temporal corrections and interrupted-request recovery checks still pass.

## Retrieval baseline

The included synthetic evaluation contains 11 claims and 20 queries, with
15 positive and 5 negative cases. At K=5 and a 6000-byte diagnostic memory budget:

| Metric | Result |
|---|---:|
| Recall@5 | 0.8667 |
| MRR@5 | 0.8333 |
| Exact evidence coverage | 1.0000 |
| Scope violations | 0 |
| Negative-query failures | 0 |

Two positive paraphrases have no lexical overlap and are missed. Latencies and
individual cases are in `evaluations/sqlite-baseline.json`. This small dataset
measures retrieval behavior, not production performance or answer quality. It
uses a larger diagnostic memory budget than default chat's 2200 bytes. No real
LLM was run, so citation entailment and model adherence remain unmeasured.

Reproduce with `python scripts/evaluate_retrieval.py`. `--postgres` uses temporary
schemas in an explicitly configured dedicated `ADA_TEST_DATABASE_URL`.
The HTTP smoke can be repeated with `python scripts/smoke_upgrade.py --phase1-root
PATH_TO_ORIGINAL_PHASE1_BUNDLE`.

## Remaining target-environment checks

- PostgreSQL runtime, native full-text ranking consistency and row-lock races.
  The host environment prevents switching to the database's required OS user,
  so a local PostgreSQL server could not be prepared. Run
  `scripts/test-postgres.ps1` on your laptop. It creates/reuses the separate
  `ada_phase2_test` database and uses disposable schemas.
- Native Windows PowerShell execution and Docker port handling.
- Real Ollama inference, model citation use/interpretation, identity prompt
  adherence, context/token use, GPU/CPU placement and latency on your hardware.

The existing Starlette/httpx test-client deprecation warning does not fail the
suite. Dependencies remain pinned to the prior bundle versions. Phase 2 does not
implement automatic extraction, embeddings, shared scopes, tools, document
ingestion, consolidation, affect learning or mobile/edge inference.
