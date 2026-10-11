# Android / iOS boundary

The generated `contracts/openapi.json` is the implemented Phase 2 contract.
It also includes implemented Phase 08/09 additions and Phase 10's optional
semantic diagnostics. Clients may ignore absent/additive `plan.semantic` and
`semantic_similarity`; original request source cards remain authoritative for
display. Semantic retrieval stays disabled by default. Clients never generate
embeddings or contact the provider/database. Mathematical scores are optional
diagnostics, not truth confidence. See
[Phase 10 policy](EMBEDDINGS-AND-HYBRID-RETRIEVAL.md).
Native clients send `Authorization: Bearer <token>` and JSON over HTTPS. Use UUIDs
for request IDs; preserve the ID/content/time/retrieval options until the request outcome is known. On
503, wait using Retry-After and randomized backoff. On network timeout, query
`GET /v1/requests/{id}` before assuming failure. A 404 means the server has no
request with that ID for the current account. A running response means wait.

Implemented flow:
1. GET /v1/me and /v1/capabilities.
2. POST /v1/personalities or select an existing private profile.
3. POST /v1/conversations with personality_id and an optional owned scope_id.
4. POST /v1/conversations/{id}/messages with request_id and content; optional as_of, use_memory and use_documents.
5. GET conversation events to inspect persisted evidence or resume the UI.

The chat endpoint accepts user text. It rejects unknown fields such as
owner_id, role, system_prompt, or claims. `edge_inference` is explicitly false.
Do not submit an on-device model's output to the user-message endpoint as though
the user wrote it. Show offline generated replies as local drafts and await a
future provenance-aware synchronization endpoint.

Phase 1 adds private project scopes, exact evidence versions and explicit memory
endpoints. Structured writes are user assertions, not a way to silently promote
device-model output to user evidence. `structured_memory=true`, `memory_in_chat=true`
and `automatic_memory_extraction=false` distinguish the implemented boundaries.
Refer to PHASE1-MEMORY.md for the source/claim APIs and temporal corrections.

Phase 2 adds scope-bound retrieval and snapshot citation cards. Show `[M1]` labels
alongside the corresponding `citations` cards from the same request response; do
not resolve labels against the latest scope contents or a different request.
`GET /v1/requests/{id}/retrieval` provides the reserved evidence, budget and planner
state, including for failed attempts. A missing legacy trace returns 404.
Unknown answer labels appear in `citation_warnings` and have no card. Selected
but uncited evidence is available in the trace. Cards establish provenance, not
semantic correctness. See PHASE2-RETRIEVAL.md for the complete retrieval contract.

Existing v1/v2 conversations need an explicit prompt upgrade for retrieval. New
conversations use v4. v3 continues claim retrieval; document retrieval requires
an explicit v4 upgrade. `use_memory=false` disables fresh retrieval while retaining
eligible conversation history. An explicit as_of instant uses the same valid-time
semantics as memory queries. It is part of the idempotent request input.
`use_documents` defaults false and is bound to the request when true. Imported
document cards use separate D labels and `document_citations` / trace document
arrays; they have imported origin/trust, exact versions, spans and locations.
Keep original claim M cards and legacy encrypted journals intact. Source-version
routes keep their original user/model trust contract; use document-version routes
for imported text. Upload recovery commits exact bounded bytes/UUIDs/metadata to
the encrypted verified-owner/server journal before POST and never automatically
replays on restore. See [DOCUMENT-INGESTION.md](DOCUMENT-INGESTION.md).

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

Phase 03 includes a Kotlin/Compose foundation and typed transport in
`apps/android/`. Phase 04 adds authenticated conversation/history/chat/source UI
and Keystore-encrypted credential/journal recovery for manually issued tokens.
It introduces no server enrollment route or changed chat contract. Creation POSTs
without idempotency keys are reconciled through list refresh after ambiguous loss,
and retries retain the original message UUID and options. There is no Swift client
or Android inference runtime.
The web foundation in `apps/admin-web/` also uses this HTTP contract and cannot
grant admin access. See `contracts/README.md` for response/error schemas and the
apps' READMEs for local development connections.

## Phase 09 identity extension

The implemented scoped identity routes are documented in
[ENTITIES-AND-ALIASES.md](ENTITIES-AND-ALIASES.md). Capabilities add
`scoped_entities`, `entity_writes` and `entity_resolution=explicit_aliases_v1`, with
false/unsupported defaults for legacy servers. Claims/cards optionally carry an
original `subject_entity_id`; selected cards freeze a historical canonical choice.
Recorded retrieval plans retain ambiguous alternatives. Existing subjects, exact
quotes, request IDs and prompt upgrade rules remain unchanged.

Android's reviewed entity writes reserve an exact owner/server/scope/operation/body
in Keystore record v4/256 KiB alongside chat, memory and document recovery.
v1–v3 records survive upgrade. Restore never POSTs; receipt check or identical retry
is explicit. A local discard changes no server identity history. Foreign references,
changed previews and permission fields are enforced by the server. No direct
provider/database client or account inference is introduced.

## Phase 13 episode navigation

Capabilities add optional `episodes=source_linked_v1`,
`consolidation_jobs=bounded_jobs_v1`, `consolidation_generation` and
`consolidation_worker`. Legacy clients/servers retain unsupported defaults.
Android consumes only authenticated HTTP jobs/episodes/original-source routes.
Encrypted journal v7 retains earlier records and reserves one exact owned job
body before submission; restore never POSTs. Navigation contexts are separate
from ordinary chat input and factual retrieval. See
[EPISODES-AND-CONSOLIDATION.md](EPISODES-AND-CONSOLIDATION.md).
