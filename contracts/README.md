# Existing ADA HTTP contract

`openapi.json` is exported from the implemented FastAPI routes. Phase 03 adds
output schemas; it does not add an admin role, sign-in, streaming, cancellation,
upload, device inference or monitoring endpoint. No database migration or prompt
upgrade is required to use these schemas. Existing CLI clients use the same
field names, statuses and retry fingerprints.

All `/v1/` operations require a bearer credential. Ownership comes from the
authenticated user, never a supplied owner ID, profile name, source label or
personality. A resource owned by another account returns the same sanitized 404
as an unavailable resource. The unauthenticated health routes disclose only
liveness/schema readiness.

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
| Claims/corrections | `ClaimOutput` | Explicit source-backed creation/correction returns 201, identical same-ID replay returns 200. Valid-time history remains available. |

Lists use `limit`/`offset` and return arrays, without a fabricated total or cursor.
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
| 413 | Message exceeds the whole prompt budget; preserve an editable draft. |
| 422 | Input/query validation; show sanitized field issues or code. |
| 502 | Provider failure; inspect persisted failed request before offering exact retry. |
| 503 | Admission busy (`Retry-After: 3`) or database not ready on health readiness; bounded backoff. |

Clients also have safe mappings for 403/429 and future error statuses, but no
current route is advertised as emitting these or as providing an admin API.

## Prompt and citation compatibility

| Frozen conversation version | Existing behavior |
|---|---|
| `ada-baseline-v1` / `ada-baseline-v2` | Original prompt/personality retained; fresh retrieval disabled with `prompt_upgrade_required` until explicit upgrade. |
| `ada-baseline-v3` | Scoped retrieval enabled when `use_memory` and time policy permit it. |
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
