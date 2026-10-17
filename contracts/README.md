# Existing ADA HTTP contract

## Phase22 additive authentication

The exported contract adds `/v1/auth` login/refresh, browser cookie equivalents,
owned session metadata/revoke, logout current/all and password change. Existing
private request/response schemas, UUIDs, snapshots and replay remain compatible;
private OpenAPI security now offers HTTPBearer or APIKeyCookie. Middleware rejects
mixed credentials and enforces the exact HTTPS browser origin/CSRF policy. Browser
login/refresh return acknowledgements, never token JSON; access expiry is a
nonsecret response header. Native login returns opaque access/refresh credentials.
See [the lifecycle guide](../docs/PASSWORD-LOGIN-AND-SESSIONS.md).

`openapi.json` is exported from the implemented FastAPI routes. Phase 03 added
output schemas. Phase 05 adds explicitly granted, audited monitoring metadata
and introduced migration 0004; no admin prompt upgrade is needed. Phase 08 adds
document migration 0005, bounded text/Markdown uploads and separate imported document cards.
Phase 09 adds head 0006 and typed explicit entities/aliases, resolution, history,
previewed merge/undo and operation receipts. Optional canonical claim/card fields
and resolution plans preserve original subjects/evidence and legacy defaults.
See [ENTITIES-AND-ALIASES.md](../docs/ENTITIES-AND-ALIASES.md).
Phase 10 adds head **0007**, one owned derived-index rebuild endpoint and optional
semantic capability/trace/candidate diagnostics. All old routes, required fields,
request fingerprints and citation mappings are preserved. Semantic retrieval is
disabled by default; see
[EMBEDDINGS-AND-HYBRID-RETRIEVAL.md](../docs/EMBEDDINGS-AND-HYBRID-RETRIEVAL.md).
Existing CLI/user clients
use the same field names, statuses and retry fingerprints. Phase 16 adds optional
durable streaming/Stop without changing legacy request enums.
PDF/OCR, local language-model inference and enrollment remain absent. Phase 17
adds only explicit on-device speech input and optional offline TTS. The monitoring dashboard
is implemented in Phase 06.

All `/v1/` operations require a bearer credential. Ownership comes from the
authenticated user, never a supplied owner ID, profile name, source label or
personality. Private user resources owned by another account return the same sanitized 404
as an unavailable resource. The unauthenticated health routes disclose only
liveness/schema readiness.

Admin metadata routes are a separate explicit-grant boundary. Even granted admins
remain owners on the normal private routes. `admin_monitoring` is an additive
capability flag (older omitted values default false), not permission. All six
`/v1/admin/` outputs use closed allowlists and require current grants/audits;
see [ADMIN-MONITORING.md](../docs/ADMIN-MONITORING.md) for fields and limits.

| HTTP area | Exported outputs | Existing behavior |
|---|---|---|
| Account/capabilities | `UserOutput`, `CapabilitiesOutput` | `/v1/me` identifies the authenticated owner. Capabilities gate implemented features; a successful connection does not grant administration. |
| Profiles | `PersonalityOutput` | `/v1/personalities` creates/lists expression settings. Creation returns 201. |
| Conversations | `ConversationOutput`, `PromptUpgradeOutput` | Creation returns 201. List/detail preserve frozen personality, prompt version, scope and revision. Upgrade is explicit and audited. |
| Events | `EventOutput[]` | User/assistant evidence retains request IDs, request status, trust and source-version IDs. |
| Chat/status | `RequestOutput` | POST messages and GET request status share the durable running/completed/failed shape; nullable response/error/token counts remain explicit. |
| Retrieval | `RetrievalOutput`, `TraceOutput` | Direct retrieval and saved traces retain candidates, selected source snapshots, plan and budgets. |
| Scopes | `ScopeOutput` | Creation returns 201. Owned personal/project scopes only. |
| Sources | `SourceVersionOutput` | Explicit note creation returns 201, identical same-ID replay returns 200. Exact text/hash/trust are retained. |
| Documents | `DocumentUploadOutput`, `DocumentVersionOutput`, `DocumentChunkOutput` | Authenticated raw text/Markdown upload, receipt replay and owned version/excerpt/raw reads. Imported trust is separate from legacy source/claim schemas. |
| Claims/corrections | `ClaimOutput` | Explicit source-backed creation/correction returns 201, identical same-ID replay returns 200. Valid-time history remains available. |

Owned resource lists use `limit`/`offset` and return arrays, without a fabricated total or cursor.
Profile/conversation/scope lists default to 50, maximum 100. Event/source/claim
lists default to 100, maximum 200. Profiles, conversations, scopes and sources
order by creation timestamp then ID. Events order by request creation timestamp,
request ID, then user before assistant, including failed/running user events.
Claims order by valid-from timestamp, creation timestamp, then ID and apply the existing current,
historical and `history` filters.

All integer timestamps marked `int64` are UTC epoch milliseconds. Inputs such as
`as_of`, `valid_from` and `effective_at` are timezone-aware ISO 8601 timestamps
with at most millisecond precision; equivalent offsets identify the same instant.
Android uses `Long`. Web decoders validate integer precision before rendering
local time. `RequestOutput` has no generation timestamps or durations: clients
must not invent them from a request wait.

Evidence span offsets count Unicode code points and use the half-open interval
`[span_start, span_end)`. A supplementary character such as `🙂` counts as one
Python/code-point position and two Kotlin/JavaScript UTF-16 code units. Convert
UTF-16 selection boundaries before submitting explicit evidence; reject a
boundary inside a surrogate pair. Preserve exact whitespace and hash the full
source's UTF-8 bytes. Source text and model text remain untrusted display data;
provenance does not independently establish truth or entailment.

## Recovery and sanitized failures

A transport timeout, lost connection or canceled client wait means the outcome
is unknown. It does not mean the persisted request failed or the server stopped
generation. Verify the same server/account, then GET the same request UUID.
Running requests remain pending. Completed requests reconcile the saved answer
and source cards. Failed requests permit an explicit retry using the same UUID,
conversation, content, `as_of` and `use_memory`; reserved context remains frozen.
Document-aware requests also preserve `use_documents`; omission/false retains
legacy fingerprints, true uses a separate domain-bound option hash.
A missing request permits a consciously offered submission of the original
payload. Stop retries and clear private loaded state on 401.

Completed replay returns the original answer/citation mapping even after a memory
correction or prompt upgrade. Reusing a UUID with a different conversation,
content or options returns 409. A failed retry after the conversation revision
changes also returns 409. Profile, scope and conversation creation have no
idempotency key: reconcile a creation timeout by refreshing the owned list instead
of blindly creating a second resource.

`ErrorOutput` is `{ "detail": "sanitized_code" }`. A 422
`ValidationErrorOutput` may contain the same string code or a list of issues with
only `type`, `loc` (string/integer path segments) and `msg`. Validator input bodies
and exception context are omitted. Credentials and private request text must not
be displayed/logged as an error fallback. HTTP responses remain authoritative;
unknown/malformed errors receive generic client wording and never fixture data.

| Observed status | Client state |
|---|---|
| 401 | Authentication required/invalid/revoked; stop automatic retries. |
| 404 | Resource unavailable to this identity; clear its private display. |
| 409 | Conflicting ID/payload, active conversation/request, changed history or unsupported upgrade; reconcile before retry. |
| 408 | Document receive timed out/interrupted; retain the exact reservation and check its original upload ID. |
| 413 | Message exceeds the prompt budget, or a document size/retained-data quota is reached; preserve input and inspect the safe reason. |
| 415 | Unsupported document media type/format; review the exact saved input. |
| 422 | Input/query validation; show sanitized field issues or code. |
| 502 | Provider failure; inspect persisted failed request before offering exact retry. |
| 503 | Admission busy (`Retry-After: 3`) or schema/monitoring unavailable; bounded backoff and safe operator guidance. |

Admin routes return 403 for known accounts without a current grant and 429 for
bounded polling, with `Retry-After: 60`. DB/audit failures return sanitized 503.
Admin lists use bounded envelopes rather than changing existing user list arrays.

## Prompt and citation compatibility

| Frozen conversation version | Existing behavior |
|---|---|
| `ada-baseline-v1` / `ada-baseline-v2` | Original prompt/personality retained; fresh retrieval disabled with `prompt_upgrade_required` until explicit upgrade. |
| `ada-baseline-v3` | Scoped retrieval enabled when `use_memory` and time policy permit it. |
| `ada-baseline-v4` | Same claim retrieval, plus imported document excerpts only with `use_documents=true` and memory/time policy enabled. |
| Other versions | No inferred compatibility or automatic rewrite; the current upgrade operation rejects unsupported versions. |

Prompt upgrade archives the old/new prompts and increments revision. It preserves
the personality snapshot and completed request replay. Output typing preserves
additive snapshot keys; clients safely tolerate unknown optional fields and enum
values. An unknown request state never means completed, and an unknown capability
never authorizes a write.

Labels such as `M1` belong to one request. Resolve them only from that request's
`citations`; `selected` trace entries can include uncited evidence. Unknown labels
produce `unknown_label:M99` warnings and no invented source card. Requests predating
retrieval traces retain their answer; GET retrieval returns 404
`retrieval_trace_unavailable`. The current status representation includes empty
citations and unknown-label warnings when no trace can resolve a label. Clients
may defensively accept older wire payloads without citation fields, but may not
reconstruct missing sources from the latest claims. Direct retrieval lacks chat
prompt/history budget keys; unranked slot siblings lack score/term-coverage keys.
Typing keeps these absences and any saved additive trace metadata.

Document cards use `D1` labels and separate `document_citations`,
`document_selected` and `document_candidates` arrays. Old claim schemas, M labels,
saved arrays and completed replay remain intact. New conversations freeze v4;
v1/v2/v3 upgrade explicitly with an audit through the existing operation. Legacy
source-version routes retain their two original trust classes; imported versions
are read through dedicated document routes. See
[DOCUMENT-INGESTION.md](../docs/DOCUMENT-INGESTION.md) for availability semantics,
storage/recovery quotas, raw-upload media types, snapshots and PDF deferral.

## Synthetic fixtures and verification

`fixtures/manifest.json` records each file's actual route, method, HTTP status and
capture provenance. The fixtures come from a migrated disposable SQLite database,
synthetic accounts and a deterministic test completion through FastAPI TestClient.
They contain invented examples, consistently replaced UUIDs, normalized current
timestamps and zero elapsed retrieval time. The legacy cases deliberately freeze
baseline v2 and remove a synthetic completed request's trace. They are test data,
never a production adapter fallback or evidence of a real-model/device run.
Manifest/contract paths use forward slashes, including on Windows.

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe scripts\export_openapi.py
.\.venv\Scripts\python.exe -m pytest -q tests\test_client_contract.py tests\test_schema_contract.py
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
```

For deliberate fixture regeneration from the synthetic flow only:

```powershell
$env:ADA_UPDATE_CONTRACT_FIXTURES = '1'
try {
    .\.venv\Scripts\python.exe -m pytest -q 'tests/test_client_contract.py::test_actual_responses_match_export[sqlite]'
} finally {
    Remove-Item Env:\ADA_UPDATE_CONTRACT_FIXTURES
}
```

The tests compare live HTTP responses and committed fixtures with the exported
schemas, reject a stale export, exercise owner boundaries and cover replay,
correction, prompt compatibility, unknown labels, missing traces, pagination,
Unicode spans and sanitized failures. PostgreSQL harness cases require the
dedicated `ADA_TEST_DATABASE_URL`; a skipped case is not PostgreSQL execution.
Output configuration follows the existing pinned Pydantic release's
[documented TypedDict configuration](https://docs.pydantic.dev/latest/api/config/#pydantic.config.with_config),
checked 2026-10-08; no Python dependency was added or upgraded.

## Phase 11 additions

Head 0008 adds seven authenticated selected-source extraction/proposal/edit/review
and receipt paths. Existing operations, required fields and old property shapes
remain unchanged. Optional proposal/review/provenance capabilities, reviewed
claim/card provenance and admin state counts are additive. Legacy origin enums
remain intact; review-v1 provenance.origin=user_reviewed identifies new explicit
endorsements and preserves original supporting trust. Automatic extraction stays
false and old frozen cards remain unchanged. See
[MEMORY-PROPOSALS-AND-REVIEW.md](../docs/MEMORY-PROPOSALS-AND-REVIEW.md).

## Phase 13 additions

Head 0010 adds authenticated job, episode and navigation-context paths. Job and
context POSTs document 201 creation and 200 exact replay. New capabilities and
admin metadata fields are optional; existing path operations, required fields,
property shapes, origin enums, chat inputs and prompt snapshots remain unchanged.
Private navigation contexts never become factual chat evidence. See
[EPISODES-AND-CONSOLIDATION.md](../docs/EPISODES-AND-CONSOLIDATION.md).

## Phase 14 additions

Head 0011 adds six owner-only preference, expression, signal/reset, request-state
and exact receipt paths. POSTs document 201 creation and 200 identical replay.
Three optional capabilities advertise explicit settings and expression-v1 while
automatic affect inference stays false. Existing 69 paths/94 schemas preserve
their required fields/property types; only optional capability fields are added.
The expression policy is independent of saved v3/v4 baselines. Nine new expression
fixtures are generated from actual synthetic HTTP, including legacy-null request
state, reviewed-model vector clamps and reset receipts. Earlier legacy fixtures
are retained; current capabilities/readiness and manifest are refreshed. See
[policy](../docs/INTERACTION-PREFERENCES-AND-AFFECT.md).

## Phase 15 additions

Head 0012 adds seven owner-only learning state/config/observation/review/reset,
receipt and request-snapshot paths. Creation is 201, exact replay 200. One optional
capability advertises `ada-learning-v1`; RequestOutput optionally includes original
C source cards and admin overview optionally includes closed operation counts.
All 75 earlier path operations and 105 schema shapes/required fields are preserved.
Chat inputs, fingerprints, old source enums and saved prompts remain unchanged.

Twelve new synthetic HTTP fixtures cover enrollment, three selected observations,
pending/approved/reset state, exact reviews/receipts and legacy/frozen snapshots.
The 53 previous non-capability/readiness/manifest payloads retain their bytes.
Expires-at fixture normalization preserves the original duration relative to
created-at. Nullable legacy learning and absent optional C cards stay supported.
See [policy](../docs/INTERACTION-LEARNING-AND-CONTINUITY.md) for provenance, bounds,
consent, source authorization and the historical replay/reset retention exception.

## Phase 16 additive streaming contract

Head 0013 adds stream submit, status/checkpoint, bearer-authenticated SSE and
strict same-attempt cancel. `RequestOutput`, ChatInput/options/fingerprints and
legacy enums stay unchanged. Cancellation maps to failed/request_cancelled;
StreamStatus carries richer state separately. Capability fields `stream_protocol`
and `generation_cancellation` default to unsupported/false when omitted. Android
requires those fields plus streaming before enabling incremental replies/Stop.

SSE IDs are attempt:sequence. The OpenAPI stream operation exports the typed event
under `x-ada-event-schema`; safe transport control frames are separate. GET
checkpoint replacement handles gaps/expired cursors; terminal frames never
manufacture final source cards. Admin detail's optional stream object has only
state, sequence, replay_after, created_at and finished_at.

Eight additional synthetic HTTP fixtures cover supported capabilities, started/
running/cancel receipt/cancelled/completed checkpoints, legacy unavailability and
legacy failed cancellation. Existing fixture payloads remain byte-identical except
current capabilities/readiness and the expanded manifest. Paths serialize with
forward slashes on Windows. See
[the policy](../docs/STREAMING-AND-CANCELLATION.md) for bounds and retry/race rules.


Phase17 adds head0014 and three owner-authenticated reviewed-voice routes, typed
original/generated and reviewed/endorsed lineage, plus optional voice_input and
voice_audio_uploads capabilities. All old paths/schemas retain their contracts;
only capability fields are additive. Existing synthetic fixture payloads are
preserved except capabilities/readiness. Three new HTTP-captured voice fixtures
show a typed submission and truthful provenance; server audio/hash are absent.
See [the voice policy](../docs/VOICE-INTERFACE.md).


Phase18 adds head0015 and seven security path templates for owner status,
credential list/enroll/rotate/revoke and saved-content preview/job list/confirm/status.
Original89 paths and125 schemas remain; only UserOutput.data_epoch and two capability
properties are additive with defaults. Private routes document bounded middleware
errors without changing existing request shapes, origin/trust enums or snapshots.
Explicit owner-confirmed erasure returns410 for old requests, a documented exception
to normal completed replay. Security receipts contain counts/UUID metadata, never
private evidence text or stored plaintext tokens. Issuance returns its secret once;
exact replay returns token:null. See [security and operations](../docs/SECURITY-AND-OPERATIONS.md).


Phase23 preserves all105existing Phase22 path definitions and137old non-capability
schemas. It adds109total paths/143schemas: explicit authenticated time resolution,
claim-window retrieval, audited v5 upgrade and frozen request-quality diagnostics.
Only CapabilitiesOutput gains three optional fields with defaults. Chat request,
point-in-time retrieval, citation shapes and old trace schemas are unchanged.
V4 stays default; v5 is explicit. Calendar resolution is `ada-time-window-v1` and
retrieval is `ada-window-retrieval-v1`, with valid-time-overlap/current-recorded
semantics. See [the quality policy](../docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md).
