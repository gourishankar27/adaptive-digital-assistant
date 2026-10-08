# Android / iOS boundary

The generated `contracts/openapi.json` is the implemented Phase 1 contract.
Native clients send `Authorization: Bearer <token>` and JSON over HTTPS. Use UUIDs
for request IDs; preserve the ID/content until the request outcome is known. On
503, wait using Retry-After and randomized backoff. On network timeout, query
`GET /v1/requests/{id}` before assuming failure. A 404 means the server has no
request with that ID for the current account. A running response means wait.

Implemented flow:
1. GET /v1/me and /v1/capabilities.
2. POST /v1/personalities or select an existing private profile.
3. POST /v1/conversations with personality_id and an optional owned scope_id.
4. POST /v1/conversations/{id}/messages with request_id and content.
5. GET conversation events to inspect persisted evidence or resume the UI.

The chat endpoint accepts user text. It rejects unknown fields such as
owner_id, role, system_prompt, or claims. `edge_inference` is explicitly false.
Do not submit an on-device model's output to the user-message endpoint as though
the user wrote it. Show offline generated replies as local drafts and await a
future provenance-aware synchronization endpoint.

Phase 1 adds private project scopes, exact evidence versions and explicit memory
endpoints. Structured writes are user assertions, not a way to silently promote
device-model output to user evidence. `structured_memory=true`, `memory_in_chat=false`
and `automatic_memory_extraction=false` distinguish the implemented boundaries.
Refer to PHASE1-MEMORY.md for the source/claim APIs and temporal corrections.

All new memory timestamps are UTC epoch milliseconds with OpenAPI `int64` fields;
use 64-bit integers. Evidence offsets count Unicode code points, not UTF-16 units.
For supplementary characters, Kotlin/Swift string indices must be converted before
submitting spans. A claim's returned exact quote can be displayed directly.

## Future edge proposal (design only; no endpoint yet)

An eventual authenticated device may propose a result containing:

```json
{
  "proposal_id": "uuid",
  "conversation_id": "uuid",
  "source_event_ids": ["uuid"],
  "task": "draft_summary",
  "model": "configured-on-device-model",
  "model_version": "digest",
  "input_hash": "sha256",
  "output": "untrusted generated text"
}
```

The backend must resolve ownership, verify source IDs and input hashes, apply
size limits, record model-generated trust, and validate any proposed knowledge
separately. Source references cannot cross users or unauthorized scopes. Device
enrollment, offline sequence reconciliation, deletion propagation and credential
revocation must be implemented before enabling this endpoint. A local model can
help with UI intent classification or draft summarization; it cannot grant tools
permissions or become an authoritative memory database.

Kotlin and Swift implementations are not included in Phase 1. This keeps the
server contract testable before committing to an Android inference runtime.
