# Phase 10: bounded exact semantic retrieval

The server implements an optional semantic channel beside the unchanged lexical,
subject and explicit-entity baseline. **It remains disabled by default.** The
available measurements use synthetic passages and explicit fixture vectors; they
do not establish production relevance or EmbeddingGemma quality. No application
database upgrade, model download or deployment was performed.

## Provider and index

The server-only `EmbeddingProvider` interface accepts at most eight texts per
batch. Its production adapter uses the existing locked httpx dependency and local
Ollama `/api/embed`. The selected specification is `embeddinggemma:300m`, default
768 dimensions, full manifest digest
`85462619ee721b466c5927d109d4cb765861907d5417b9109caebc4e614679f1`, verified
against the official registry on 2026-10-10. Official documentation describes
2,048-token input and a 768-dimensional output, with 512/256/128 options. The
adapter applies `task: search result | query: ` and `title: none | text: ` prefixes,
sets `truncate=false`, normalizes finite nonzero vectors, validates exact count,
dimension and returned model, and checks the installed tag's full digest before
and after each call. An oversize input fails instead of silently truncating.

Official references checked: [Ollama embed API](https://docs.ollama.com/api/embed),
[model listing API](https://docs.ollama.com/api/tags),
[selected Ollama model](https://ollama.com/library/embeddinggemma:300m), and
[Google's 300M model card](https://huggingface.co/google/embeddinggemma-300m).
The current Google inference guide redirects to EmbeddingGemma 2; the selected
300M specification comes from the specific model card above.

Migration **0007** adds only discardable `embedding_entries`. Owner/scope composite
references bind each claim or document chunk and its source version. Each entry
retains item/source IDs, exact source/text hashes, model/digest/dimensions,
namespace/index version, normalized vector and build time. Claim input is the
original subject, predicate, value and exact quote separated by newlines;
document input is its exact chunk quote. Canonical identity is resolved at query
time and never rewrites the embedded original annotation.

A namespace hashes model tag, full digest, dimension and preprocessing version
`embeddinggemma-search-v1`. Drift requires an explicit new namespace/rebuild;
incompatible vectors are never compared. A successful rebuild replaces the
scope's prior derived namespace, bounding retained vector storage. Source history,
claim write hashes, old prompts and request traces remain untouched. Downgrading
0007 discards vectors; it does not discard evidence or frozen semantic traces.

## Rebuild and authorization

`POST /v1/scopes/{scope_id}/semantic-index/rebuild` requires the authenticated
owner. No owner/model/vector fields are accepted from a client. The operation
reads and checks a bounded history snapshot, closes the session, embeds missing
or invalid entries in batches, then locks the owned scope and verifies the entire
snapshot again before atomic publication. Unchanged valid vectors are reused.
A failed batch, corrupt vector, changed corpus or failed publication leaves the
prior complete index intact. Newly added/corrected/uploaded evidence needs an
explicit rebuild; no automatic extraction or background job is implemented.

Rebuild includes authorized exact historical claims and ready imported document
versions so dated queries can select the proper version later. Invalid hashes,
spans, trust or lexical projections are excluded. Query-time claim validity and
document publication/availability/latest-version rules apply before ranking.
Ambiguous entity roots are excluded before the semantic channel, including
truncated ambiguity. An index cannot grant access or resolve identity ambiguity.

Bounds: 256 combined eligible items per scope, a conservative 1 MiB content-work
budget (four bytes per code point, counted per joined row), eight inputs/batch,
6,000 UTF-8 bytes/input including prefix, 512 KiB/provider response, 10-second
default per-call timeout and a 120-second rebuild deadline checked between
batches. A final in-progress bounded batch may finish after that deadline. At
most 257 metadata rows per category are read to reject overflow; full texts are
loaded only after that category's work gate. Combined validation materializes at
most two gated categories before its combined-byte check. Repeated large source
versions can exceed the conservative gate even with small chunks; lexical
retrieval stays available. There is no pgvector extension or ANN dependency.

The same process semaphore admits chat, embedding query and rebuild inference.
Chat holds its admission through query embedding and generation. Direct retrieval
acquires it only for query embedding; a busy semaphore produces lexical fallback.
No network embedding runs in a database transaction. Keep **one Uvicorn worker**;
other programs calling Ollama are outside this limiter.

Responses: 200 bounded counts/namespace/timing; 401 authentication; 404 unavailable
owned scope; 409 changed corpus; 503 disabled/busy/provider/bound failure with the
existing sanitized error/Retry-After policy. Identical rebuilds are safe derived
work; they do not create a second claim or document. The route is `no-store`.

## Deterministic ranking and replay

Exact cosine ranking examines only authorized, valid-time eligible rows in the
bounded scope, checks their full quotes/hashes/projections again and binds every
vector's metadata. Missing/stale/incompatible entries degrade the **whole semantic
channel** to the original baseline. No fabricated similarity appears on failure.
An empty eligible corpus needs no matching vector. Finite normalized vectors use
Python `math.fsum`; cosine ties resolve by item UUID. The configured minimum
similarity defaults to 0.7 and is recorded, not described as truth confidence.

`lexical-first-rrf60-v1` merges claim lexical/subject/entity/overview/semantic
channels by reciprocal rank `1/(60 + rank)`, with at most 64 hits/channel. Existing
lexical/subject/entity hits precede semantic-only hits; coverage, fused score and
UUID break ties. Documents similarly keep lexical hits before semantic-only hits.
Claims retain first use of the shared item/prompt budget, followed by documents.
Different values in one slot remain whole conflict groups. Exact quotes never
truncate, and the existing whole-prompt/history budget still applies.

Additive `plan.semantic` diagnostics freeze model/digest/namespace/index/ranking
version, threshold, eligible/indexed counts, build time, timing and fallback reason.
Candidate channel arrays and optional `semantic_similarity` freeze actual channel
results. The reserved request stores these with original messages/evidence.
Failed retry and completed replay never re-embed or search a newer index. Existing
request fingerprints, v3 claim prompts, v4 document opt-in, source labels and
completed response contracts are preserved. Legacy traces can omit semantic data.

Capabilities add `semantic_retrieval` (configured feature) and `semantic_state`
(`disabled`, `configured`, last `available` or `degraded`). The state is the last
process observation, not a per-scope freshness guarantee. Each owned trace gives
the actual fallback reason; lexical `memory_retrieval` stays advertised as before.
There is no new Android or admin control, and no mathematical truth badge.

## Installation and controlled evaluation

First validate migrations on a disposable database. Installing the source into
the intended application database requires `alembic upgrade head` to **0007**;
the configured application's final observed head is recorded in STATUS. Enabling
embeddings is separate from installing the schema. Existing clients remain usable
with embeddings disabled. No new Python, web or Android dependency is required.

For reproducible synthetic comparisons:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_hybrid.py --provider fixture
.\.venv\Scripts\python.exe scripts\evaluate_hybrid.py --provider disabled --output .pytest_cache\hybrid-disabled.json
# Dedicated ADA_TEST_DATABASE_URL only; never the application schema:
.\.venv\Scripts\python.exe scripts\evaluate_hybrid.py --provider fixture --postgres --output .pytest_cache\hybrid-postgres.json
.\.venv\Scripts\python.exe scripts\evaluate_retrieval.py
```

`--provider ollama` runs the same synthetic corpus through the production adapter
in a disposable database, requiring an already installed exact model/digest. It
does not download models or activate the application. The operator can separately
install the selected model, measure actual resource use and compare relevance on
representative authorized data before setting `ADA_EMBEDDING_ENABLED=true` and
restarting the single API process. `ADA_EMBEDDING_DIGEST` must be the full verified
installed digest; dimension changes require `ADA_EMBEDDING_DIMENSIONS` and rebuild.
Never activate solely because hand-built fixture vectors improve fixture recall.

The local runtime is Ollama 0.40.1 on an i9-14900HX, 31.62 GiB RAM and RTX 4090
Laptop GPU (16,376 MiB, 552 MiB used during inspection). The selected model was
absent. Registry layers total 621,875,501 bytes; that is download metadata, not
measured resident memory. A real bounded adapter probe returned sanitized
`embedding_model_changed` without inference. Model load/inference, GPU/CPU memory,
relevance/threshold calibration, sustained concurrency and real ADA citation
quality remain pending. STATUS/WORKLOG contain actual synthetic and capacity runs.
