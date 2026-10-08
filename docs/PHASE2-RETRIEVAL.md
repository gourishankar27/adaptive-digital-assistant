# Phase 2 retrieval contract

Chat can read explicitly saved claims in its own authorized scope. It cannot
automatically extract claims, write memory, ingest documents or run tools.
Baseline v3 conversations enable retrieval; existing v1/v2 conversations need an
explicit `ada upgrade-prompt CONVERSATION_UUID` first. Migration never rewrites a
saved prompt or personality.

## Selection and time

Authentication supplies the owner. The conversation supplies the scope. Chat
cannot accept a replacement owner or scope from the caller or model. Other private
scopes, including the same user's other projects, do not enter its candidate lists.
To reuse memory across conversations, create them in the same owned scope.

The deterministic planner chooses a valid-time instant, query words, a small
versioned expansion dictionary and normalized subject phrases. It uses current
server time by default. `as_of` accepts an ISO 8601 timestamp with timezone and at
most millisecond precision. The phrase `as of YYYY-MM-DD` chooses UTC midnight.
Recognized ambiguous historical phrases, such as "last year", produce
`time_mode=needs_date` and no evidence; the prompt asks for a date. This is a limited
English heuristic, not a general natural-language date parser. An explicit `as_of`
takes priority. Use it for precise temporal questions.

Candidates satisfy both validity bounds: `valid_from <= as_of < valid_to`, with
a null end considered open. Status alone does not determine validity: a superseded
claim can still apply before a future correction. Historical queries use today's
stored valid-time intervals, not the state of knowledge at the historical date.

Migration 0003 builds a derived `claim_search` projection. PostgreSQL uses a GIN
full-text index with the `simple` configuration. SQLite tests use external-content
FTS5 and transactional insert/update/delete triggers. Search normalization splits
punctuation/underscores and maps C++/C# to search tokens; original evidence is exact.
Subject matching uses normalized phrases, with a self-pronoun hint for `user`.
It is not canonical entity resolution or semantic similarity.

Each channel returns at most 64 scope/time-filtered candidates. Per-document term
coverage reranks reciprocal-rank fusion of lexical and subject matches. There are
no global corpus statistics in the rank, so unrelated users' records do not alter
the result order. Stable claim IDs break ties. A memory overview is bounded too;
it is not an exhaustive inventory. Use `memory list --history` with pagination for
that purpose. Candidate truncation is visible in the trace.

Before selection, retrieval verifies the source's user trust label, recomputes its
SHA-256, checks the claim hash/span/exact quote, and checks projection consistency.
Invalid evidence is omitted. The derived index never authorizes a fact or source.
`ada rebuild-search` is a local administrator operation that rebuilds the projection
without changing claims. It holds the scope locks used by memory writers.

## Conflicting values and context

For each ranked subject/predicate slot, retrieval checks other valid claims in the
same slot. Identical values/kinds are deduplicated. Different values are marked as
potential conflicts and sent together; if the entire group cannot fit, it is
omitted. Oversized slots are omitted and flagged as truncated. This conservative
check does not decide truth, understand multivalued relationships or detect every
semantic contradiction. Correction chains retain Phase 1's explicit behavior.

The prompt builder first reserves the frozen system baseline, runtime time/memory
policy and current user input. It then reserves selected evidence up to
`ADA_MEMORY_BYTES` (default 2200) and `ADA_RETRIEVAL_LIMIT` (default 8). Complete
history pairs use the remaining whole-prompt `ADA_PROMPT_BYTES` budget (default
6000). Each message costs its UTF-8 bytes plus 64 bytes of framing allowance.
An oversized evidence group or history pair is skipped, allowing smaller entries
to fit. Quotes are never silently truncated. Current input that cannot fit returns
413 before reserving a request. This remains a conservative byte bound, not an
actual measurement with the model's tokenizer.

The adapter receives system policy, retained complete history, an optional
user-role JSON block of type `ada_memory_evidence`, and the current question.
The system describes the block as untrusted evidence data. Source instructions
cannot grant permissions, write memory or enable tools. Prompts alone cannot
guarantee that a model will resist misleading content or interpret evidence well.

## Citations and immutable traces

The model is instructed to cite selected evidence as `[M1]`, `[M2]`, etc. The
request response includes `citations` only for known labels actually present in
the answer. Each card contains the claim, validity interval, scope, source/version,
exact quote/span and content hash. Unknown labels have no source card and appear
in `citation_warnings`. Labels are local to a request; old `[M1]` labels in history
are not evidence for a new answer. Uncited selected evidence remains visible in
the trace. Source cards verify source mapping, not that the generated sentence
follows from the source or is objectively true.

The reservation transaction locks the conversation, then takes a PostgreSQL shared
lock on its owned scope. Memory writes take an exclusive scope lock. This keeps
candidate ranking, conflict checks and evidence selection consistent with each
other. The request, messages, user event and retrieval trace commit together.
Inference runs outside the transaction. The trace contains the frozen prompt
version, planner output, authorized candidate IDs, scores/decisions, full selected
citations, context accounting, retrieval duration and creation time.

Failed retries reuse both the original messages and trace, even if memories have
since changed. Completed retries return the original reply/citations. New requests
observe corrections. The request fingerprint binds content, `as_of` and
`use_memory`. Equivalent timezone representations of the same instant match.
Default-option fingerprints retain compatibility with Phase 0/1 request IDs.
Prompt upgrades increment the revision and fence old failed retries. Legacy
requests have no reconstructed trace; their trace route returns 404.

## API and CLI

All routes below require bearer authentication and enforce ownership. Times in
responses use epoch milliseconds with OpenAPI int64 fields.

| Operation | Contract |
|---|---|
| Chat | `POST /v1/conversations/{id}/messages`: request_id, content, optional as_of and use_memory |
| Search without inference | `POST /v1/scopes/{id}/retrieve`: query, optional as_of, limit 1–16, budget_bytes 0–12000 |
| Inspect reserved evidence | `GET /v1/requests/{id}/retrieval` |
| Inspect answer/source cards | `GET /v1/requests/{id}` |
| Search CLI | `ada memory search 'query' --scope UUID [--at ISO_TIME]` |
| Trace CLI | `ada memory trace REQUEST_UUID` or `/trace` in chat |
| Cited evidence CLI | `/sources` in chat |
| Fixed time / bypass retrieval | `ada chat --at ISO_TIME` / `ada chat --no-memory` |

`use_memory=false` disables fresh retrieval; the conversation's existing selected
history remains available. A retrieval diagnostic does not call a model or reserve
a chat request. Chat trace rows and answer cards contain private data and need
the same backup/retention protections as the conversation itself.

## Evaluation

`scripts/evaluate_retrieval.py` creates a disposable SQLite database, migrates it,
seeds the synthetic fixtures and reports Recall@5, MRR@5, exact evidence coverage,
scope violations, negative-query failures and latency. `--postgres` uses isolated
schemas in the explicitly configured `ADA_TEST_DATABASE_URL`. It restores the
original environment and drops the temporary database/schema after completion.

The included SQLite baseline covers 11 claims and 20 queries: 15 positive and 5
negative. Recall@5 is 0.8667; MRR@5 is 0.8333. Exact evidence coverage is 1.0 with
zero scope violations or negative-query failures. Two paraphrases with no lexical
overlap are intentionally missed. The diagnostic uses a 6000-byte memory budget;
default chat uses 2200 bytes and may select fewer claims. This small fixture set
does not establish production latency, broad semantic recall or answer quality.
No real LLM was run. See `evaluations/sqlite-baseline.json` for individual cases.

Embeddings, canonical entities/aliases, document chunking, automatic extraction,
consolidation, general contradiction resolution, tools and mobile inference remain
future milestones. Personality continues to control expression only.
