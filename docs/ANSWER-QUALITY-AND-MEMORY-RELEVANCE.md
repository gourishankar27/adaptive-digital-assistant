# Answer quality and memory relevance — Phase 23

Phase23 adds an optional context policy, an explicit calendar-window memory
lookup, clearer selected-source review and a reproducible public evaluation.
Schema head remains **0016**; there is no migration or new dependency. New chats
still use **ada-baseline-v4**. Semantic retrieval remains **disabled**. This work
was checked against disposable databases and an emulator; it was not deployed
to the existing Windows/Tailscale service or installed on the S24 FE.

## Use the Android controls

After a future deliberate installation of compatible server/client builds:

1. Sign in normally and open **Memory**. Select the intended private scope.
2. Expand **Explore a calendar interval**. Enter a memory question, choose
   **yesterday** or **last week**, and review the timezone and reference date/time.
   The initial values come from the device; both are editable and sent explicitly.
3. Select **Resolve and find assertions**. Review the displayed start and end;
   the end is excluded. Last week means the previous Monday-to-Monday calendar
   week, not a rolling seven days.
4. Compare every exact assertion/source card. Different values may represent a
   change within the interval or conflicting assertions. ADA does not silently
   pick one. If a group cannot fit, the whole group is omitted with a notice.
5. Select **Review source or correct explicitly** to open the existing exact
   source/claim review and dated correction flow. A correction requires review
   and creates the existing versioned claim update; searching does not save it.

The lookup is read-only and claim-only. It does not submit the interval to chat,
interpret document availability or resolve historical aliases. Existing dated
point lookups remain available. A missing result means no exact evidence was
supplied by this bounded search, not that the owner never recorded something.

For the optional chat policy, open a conversation and select **Review context
upgrade**, then read the confirmation and select **Enable for future replies**.
The server must advertise `quality_prompt_version=ada-baseline-v5`. The action is
owner-authenticated, explicit and audited. It changes future context selection;
it does not rewrite old responses or save conversational details as memory.
Document opt-in remains available under v5. Continuity still requires its existing
scope enrollment/consent; upgrading a prompt does not enable learning.

The existing upgrade action still targets v4. It cannot downgrade a v5
conversation. To compare the default again, create a separate v4 conversation;
do not edit saved prompts or request rows in SQL. An active attempt rejects an
upgrade with409. Repeating the same completed upgrade is idempotent. Completed
request replay remains exact; failed retries crossing a prompt revision are
rejected rather than silently acquiring the new prompt/context.

Proposal review now annotates identical loaded pending suggestions and different
values for the same scoped subject/predicate. All individual suggestions, exact
support, trust labels and accept/edit/reject controls remain visible. Grouping is
limited to loaded items and is a navigation aid, not proof that values are true
or that a duplicate has already been approved. Editing still needs a fresh
revision preview and acceptance still creates a separate endorsement.

## New HTTP interfaces

All four routes require the authenticated owner. Existing path contracts and
request models are preserved. OpenAPI adds four paths/five schemas and three
optional capability fields: `answer_quality`, `calendar_windows`,
`quality_prompt_version`. Older clients can ignore them; older servers leave the
new Android controls unavailable.

| Route | Behavior |
|---|---|
| `POST /v1/temporal/resolve` | Resolve an explicit calendar phrase without reading private evidence |
| `POST /v1/scopes/{scope_id}/retrieve-window` | Search owned claims overlapping the whole resolved interval |
| `POST /v1/conversations/{conversation_id}/quality-upgrade` | Explicit audited upgrade to v5 for future turns |
| `GET /v1/requests/{request_id}/quality-context` | Read frozen v5 selection/omission diagnostics; older requests return null policy |

Example resolver body (synthetic dates):

```json
{
  "version": "ada-time-window-v1",
  "expression": "yesterday",
  "timezone": "America/Phoenix",
  "reference": "2025-06-02T12:00:00-07:00"
}
```

For the window route, wrap that body in `selection` and add `query`, optional
`limit` (1–16, default8) and `budget_bytes` (0–12000, default2200). The response is
`ada-window-retrieval-v1`, with `resolution`, exact `selected` M cards, bounded
candidate/omission/invalid-group counts and explanatory guidance. Timestamps use
UTC epoch milliseconds; the response also supplies local boundaries with offsets.

Missing timezone/reference, an unknown zone, an unsupported phrase, or a missing
or repeated local midnight returns `state=needs_clarification` and no evidence.
Malformed/naive reference timestamps or unsupported versions return422. DST days
may span23 or25hours. Leap days, year boundaries and prior-calendar-week boundaries
are resolved as calendar dates, never assumed to be fixed24hour periods.

The exact semantics are **valid_time_overlap_current_recorded_state**:
`valid_from < end` and `(valid_to is null or valid_to > start)`. Current recorded
correction history is consulted; this is not a reconstruction of what ADA knew
at an earlier recording time. No historical availability/document/alias claim is
implied. Owner, scope, active/trust and both interval bounds constrain candidates
before selection. Exact source/review integrity is checked before returning cards.
Every overlapping value in a matched normalized subject/predicate slot must fit
and validate, or the whole slot is omitted. Candidate lookahead is65 for a64item
bound. Existing `as of YYYY-MM-DD` and CLI `--at` keep their UTC point semantics.

## What v5 changes

The saved baseline adds `ada-quality-context-v1`: volatile history is distinct
from durable memory, corrections require explicit review, bounded misses need
uncertainty, and intervals/validity/recording must be distinguished.

Within the existing whole-prompt byte budget, v5 considers at most50 completed
same-conversation pairs, keeping the newest pair first and ranking the remainder
by overlap with original user wording. Assistant inventions do not supply ranking
terms. Selected complete pairs are then emitted in chronological order. No history
from another conversation is pulled in by this history policy.

Separately opted-in continuity considers at most20 authorized, fresh episodes.
It ranks exact original source excerpts, with at least two matching query terms,
deduplicates source-version/spans and supplies at most two600byte excerpts.
Generated summaries remain navigation, never factual evidence. Existing
owner/scope/time/consent/freshness checks run before ranking; source trust and
request-frozen C mappings remain intact. Pausing/resetting affects future
selection, not a completed request's original snapshot.

The new request diagnostic reports considered/selected history, truncated search,
selected evidence, continuity reason and omission reason codes. It reads the
stored trace, not today's memory. It does not expose hidden model reasoning or
retroactively reconstruct an old request. V3/v4 policies and prompt bytes remain
unchanged; v4 is still the default because this comparison found regressions.

## Reproduce the public evaluation

Use the pinned Python environment and existing native Ollama. No command here
downloads a model, accesses private ADA content, changes the application database
or starts a deployment. The default SQLite run uses a temporary migrated database.

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/evaluate_answer_quality.py --provider fixture --output .pytest_cache/quality-fixture.json
```

For PostgreSQL, provision the dedicated disposable `ada_phase2_test` database as
described in [the test guide](../README.md). Set `ADA_TEST_DATABASE_URL` only to
that test database, using your local test role/port. Do not copy the application's
database URL. The runner checks the database name and uses a new schema which it
drops in `finally`.

```powershell
./.venv/Scripts/python.exe -X utf8 scripts/evaluate_answer_quality.py --provider fixture --postgres --output .pytest_cache/quality-fixture-pg.json
./.venv/Scripts/python.exe -X utf8 scripts/evaluate_answer_quality.py --provider ollama --postgres --output .pytest_cache/quality-native.json
```

The native command uses the already configured installed model and records its
digest. It creates32 answers:16 synthetic cases for each of v4/v5. Fixture mode
checks routing/context/integrity, not usefulness or entailment. Reports initially
leave semantic grades null. Explicit qualitative review must compare the actual
answer with supplied exact source mappings; a marker match is not entailment.
The original Phase20 corpus/results remain unchanged.

The frozen [manifest](../evaluations/answer-quality-manifest-v1.json) identifies
eight development and eight regression-holdout cases. Its canonical JSON hash is
independent of Windows CRLF. Holdout means separated for regression comparison,
not unseen training data. [Reviewed results](../evaluations/answer-quality-results-v1.json)
retain metric denominators, per-case ordinal findings, model/prompt digests,
configuration decision and limitations. Raw outputs in the local ignored report
are synthetic; private evaluation requires separate opt-in and data handling.

## Measured decision and remaining cases

On disposable PostgreSQL18.6, installed `qwen3.8:27b` digest
`aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813`
was checked before and after the native run. Both policies had recall1.0 over the
five positive development/four positive holdout queries; MRR was0.9/1.0.
No ownership/project/deleted-source leaks or exact-span failures were detected.

| Native comparison | v4 | v5 |
|---|---:|---:|
| Development fully useful answers, Codex review | 8/8 | 6/8 |
| Holdout fully useful answers, Codex review | 5/8 | 8/8 |
| Development median end-to-end latency | 4.272s | 4.716s |
| Holdout median end-to-end latency | 3.482s | 3.922s |
| Long-history original turn supplied | No | Yes |
| Long-history prompt bytes, under6000byte budget | 5850 | 5542 |

Codex reviewed the actual32 answers; this is **not independent human review**.
The rubric separately records usefulness, uncertainty and entailment of citations
actually used, not merely available cards. Small illustrative95% Wilson intervals
overlap; this is one output per case/version with a192token output cap. Host load
was not controlled, including other validation. The first v4 generation took55.55s
with cold model startup; latency is not an SLA or a repeated resource benchmark.
Native Python allocation peak was21,016,581bytes; it excludes GPU/database/native
process allocations.

The existing13question exact-hybrid **fixture** comparison also ran: lexical
recall/MRR0.4286/0.4286, hybrid1.0/0.7857, with zero detected isolation/integrity
violations. Its eight5dimension fixture vectors used448JSONbytes, not a real
model index estimate. Python peak/latency measurements include warmup effects and
exclude database/GPU memory. This validates mechanics, not real embedding quality.
The supported `embeddinggemma:300m` digest
`85462619ee721b466c5927d109d4cb765861907d5417b9109caebc4e614679f1`
was absent. No model was downloaded; native embedding benefit, index build cost
and GPU/working-set cost remain unmeasured. Existing fallback tests still apply.

Keep v4 default and v5 explicitly opt-in. Before considering default activation,
resolve the v5 inclusive wording for an exclusive validity boundary and its
brevity-instruction regression; improve unrelated lexical hits without hiding
conflicts; then compare a newly versioned larger corpus with independent review
and repeated warmed latency/resource runs. Do not tune and rescore this holdout
as if it remained untouched. Android physical/TalkBack/large-font/release HTTPS
checks, private evaluations and native embedding comparison remain open. Existing
voice and G-41 device gates are unaffected. See [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md) for actual commands, skips and corrected failures.

Public web access, automatic completed-turn selection, background reflection,
new speech models and provider routing remain later phases. No service, database
or device deployment was performed for Phase23.
