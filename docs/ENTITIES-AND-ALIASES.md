# Scoped entities and aliases — Phase 09

Entities annotate knowledge in one authenticated owner's scope. They are not user
accounts, permissions or shared project membership. The server validates every
scope/entity/claim reference; even an admin cannot read another owner's identity
records through these routes. All names, aliases and decisions originate in
explicit authenticated user actions. No model extraction or fuzzy resolution runs.

## Schema and installation boundary

Migration **0006**, after document migration 0005, adds entities, alias history,
merge lineage, explicit self bindings, claim-link history and operation receipts.
Composite foreign keys bind each reference to its owner and scope. A nullable
`claims.subject_entity_id` leaves existing populated string claims unlinked.
Migration does not rewrite original subjects, source versions, quotes, validity,
write fingerprints, prompt snapshots, completed responses or retrieval traces.
Populated identity history blocks lossy downgrade. Empty 0006 can be reversed;
the preceding document migration still independently refuses document data loss.

Installation is a separate operator action. Back up the intended database, stop
ADA, then use the existing repository commands:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
```

The current source requires head 0006 for readiness. Phase 09 verification uses
disposable schemas and has not migrated the configured application database.
The final read-only check observed head 0005; installation of 0006 remains pending.
No new prompt version is needed: v4 remains current, v3 claim retrieval
remains supported, and old conversations retain their explicit upgrade policy.

## Resolution policy

`nfkc_casefold_whitespace_v1` uses Unicode NFKC, case folding and collapsed
whitespace. Raw labels remain exact. Accents and punctuation are preserved; visually
similar letters from different scripts and approximate spelling are not guessed.
Names are at most 160 Unicode code points, normalized keys at most 640.

Different entities may share a canonical name or alias. An entity has one current
canonical alias and no duplicate current normalized aliases of its own. Exact
resolution returns `absent`, `resolved` or `ambiguous`, with historical canonical
choices and contributing alias IDs. A `selected_id` must be one returned candidate;
selection affects that response, not future requests or authentication. Resolver
results contain at most 64 matching aliases. Additional matches set `truncated`
and remain ambiguous until explicit candidate selection.

Renaming retires the previous canonical alias rather than making the old name
permanent. It can be added again explicitly. Historical queries use the aliases,
links, self binding and redirects known at that instant, with half-open intervals.
The raw claim subject and its original evidence remain separate from this knowledge
time. Existing string-only retrieval retains its prior behavior.

Self is a dedicated explicit person binding per owner/scope. The string `User`, a
profile name or a pronoun creates no binding. Pronoun retrieval can use an existing
explicit binding; legacy raw-subject lookup still works independently.

## HTTP actions and recovery

Every route below requires the normal bearer owner. Foreign private references
return sanitized 404; forged owner/authority fields are rejected.

| Route | Action |
|---|---|
| `GET/POST /v1/scopes/{scope_id}/entities` | List/create owned entities |
| `GET /v1/entities/{entity_id}` | Current detail and redirect |
| `GET/POST /v1/entities/{entity_id}/aliases` | Retained alias history/add alias |
| `POST /v1/entity-aliases/{alias_id}/retire` | Retire an active noncanonical alias |
| `POST /v1/entities/{entity_id}/rename` | Rename with expected revision |
| `POST /v1/scopes/{scope_id}/entities/resolve` | Exact name or explicit self, optional selection/as-of |
| `POST /v1/scopes/{scope_id}/entities/self` | Explicit person binding |
| `POST /v1/claims/{claim_id}/entity` | Link/clear subject with expected current entity |
| `GET /v1/entities/{entity_id}/merge-preview?target_id=…` | Same-scope preview with counts and decision token |
| `POST /v1/entities/{entity_id}/merge` | Confirm unchanged preview |
| `POST /v1/entities/{entity_id}/undo-merge` | End current redirect, retain lineage |
| `GET /v1/entity-operations/{operation_id}` | Frozen receipt for exact recovery |
| `GET /v1/scopes/{scope_id}/entity-audit` | Paginated private decisions/receipts |

All writes reserve an owner-bound operation UUID. Identical action/path/scope/input
replay returns the original 200 receipt; a new commit returns 201 and reused IDs
with changed input return 409. Scope row locks serialize PostgreSQL writes. Failed
validation, quota or stale preview rolls back the decision and audit together.
Merge previews bind revisions, affected aliases/links and lineage. Merges require
distinct current roots of the same kind, with a maximum redirect depth of 16;
cycles and cross-scope references are rejected. Undo restores the mapping without
moving or rewriting original claims or evidence.

New claim/correction inputs optionally accept `subject_entity_id`. A supplied
reference is included in the write fingerprint and link history. Omitted/null
references preserve legacy fingerprints. A correction without an explicit new
reference remains unlinked; it does not silently inherit a later identity decision.

Retained limits per scope: 500 entities, 20 aliases per entity including retired
canonical names, 1,000 claim-link history entries and 10,000 operation receipts.
Quota exhaustion returns 413; histories are retained with no automatic deletion.

## Retrieval and Android

Exact alias expansion precedes ranking and shares existing item/evidence/prompt
budgets. Query lookup examines the first 64 whitespace tokens, phrases of up to
six tokens and at most 200 normalized keys. Up to 16 nonempty resolutions are
frozen in the plan, prioritizing ambiguity; truncation is explicit. Every ambiguous
root is excluded before candidate channels, including matches omitted from that
summary. A truncated alias result withholds all linked assertions because the
unlisted identities cannot be proven safe. Overlapping ambiguous names dominate
otherwise resolved matches conservatively; use a distinct explicit alias to clarify.

Linked conflicts group by historical root and predicate; string-only claims retain
their original subject grouping. Selected cards freeze the original entity ID,
historical canonical choice and exact evidence. Failed requests reuse their frozen
context; completed replay does not adopt renamed entities or newer links. A bounded
clarification with alternatives enters model context only when the evidence budget
can contain it. Recorded Android retrieval details also show the frozen alternatives.

Android exposes the editor from Memory only when `scoped_entities`, `entity_writes`
and `entity_resolution=explicit_aliases_v1` are supported. Scope selection, duplicate
warnings, exact resolution/selection, aliases, rename, explicit self, assertion
links, previewed merge and undo all call these APIs. Writes require a review dialog.
The existing Keystore file/key now uses additive record v4, preserving v1–v3 chat,
memory and document journals within the same 256 KiB bound. Exact operation/body
commits before POST. Restore never writes automatically; Check fetches the original
receipt and Resume sends identical input. Mismatched receipts and cleanup failures
retain the journal. Switching/logout/401 fence and clear private state.

The reproducible explicit corpus is `evaluations/entity-aliases-v1.json`; run
`pytest -q tests/test_entity_evaluation.py` on SQLite, or supply the dedicated
PostgreSQL test URL to execute both fixtures. Reports contain synthetic query/key
metrics under `.pytest_cache`, not private evidence. These are small deterministic
identity/isolation checks, not production relevance, factual truth or model quality.
