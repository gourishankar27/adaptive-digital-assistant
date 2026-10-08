# Phase 10 — embeddings and measured hybrid retrieval

Status: planned. Prerequisite: Phase 08; Phase 09 for entity-aware behavior.
Apply STANDARDS and CODEX-WORKFLOW. Keep the Phase 2 lexical baseline available.

## Goal

Improve paraphrase retrieval with a versioned semantic index without reducing
ownership, temporal correctness, citation integrity or lexical reliability.
Embedding similarity ranks authorized evidence; it does not verify a claim or
grant permission to read another scope.

## Checkpoints

1. Define an embedding provider interface, exact model/dimension/version and
   bounded batching. Verify the selected official model/runtime documentation
   and local resource use before pinning a dependency.
2. Build an owner/scope-bound derived index of eligible claim text and document
   chunks with source/claim IDs, source hash, embedding model digest and index
   version. Rebuild invalidated entries; never mutate source history.
3. Implement exact semantic ranking over an authorized bounded scope first,
   then merge lexical/subject/semantic channels using a documented deterministic
   policy. Approximate search is a later checkpoint within this phase only if
   corpus measurements justify it.
4. Run quality, failure and capacity evaluation against the unchanged baseline;
   enable the capability only when evidence supports it.

## Data and authorization

Add migrations for derived-index metadata as needed. Model/dimension drift
requires a new index namespace and rebuild; never compare incompatible vectors.
All references use owner/scope composite constraints and exact source hashes.
Filter authority, valid time and source availability before semantic candidates
can enter ranking/model context. No global nearest-neighbor pool followed by
client filtering. If ANN is selected, prove scoped partitions/query semantics
and recall under filters; otherwise keep the simpler exact scoped approach.

pgvector is an option, not an assumed installed extension. Validate installation
and migrations on the user's PostgreSQL environment before depending on it;
document SQLite test coverage limits. Exact search must have explicit corpus/work
bounds rather than downloading an unbounded private database into memory.

Embedding calls run outside transactions and respect shared generation/GPU
capacity. Keep one process until admission is genuinely shared. CPU-only or
provider-disabled operation still has lexical retrieval; record the fallback in
the trace. Do not return made-up semantic scores when embeddings fail.

## Retrieval and contract

Preserve conflict handling, half-open intervals, full quote/hash verification,
whole-prompt budgets and frozen request evidence. Store index/model/ranking
version and channel results with the reserved trace. A failed retry cannot rerun
search against a newer index and silently change its original context.

Capabilities distinguish available semantic retrieval from temporarily degraded
lexical fallback. Extend diagnostic output compatibly. Clients may show a simple
source explanation; mathematical scores belong in optional diagnostic details,
not a “truth confidence” badge.

## Verification and exit

Create a reproducible evaluation corpus with paraphrases, lexical matches,
historical changes, ambiguous entities, conflicting claims, imported documents
and cross-owner/scope decoys. Report recall@k, source selection/citation integrity,
bounded latency/resource measurements and fallback rate with dataset provenance.
Keep synthetic tests distinct from real ADA content/model measurements.

Test provider timeout, dimension/model change, stale hash, partial rebuild,
concurrent correction, scoped ANN recall if used, disabled embeddings and old
completed/failed replay. Run migrations/PostgreSQL/Ruff/backend and evaluation
checks. Exit with measured benefit or a documented decision to leave semantic
retrieval disabled; never assert quality improvement without comparative data.
