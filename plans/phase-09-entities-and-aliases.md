# Phase 09 — scoped entities and aliases

Status: planned. Prerequisites: Phase 03/current Phase 2.
Apply STANDARDS and CODEX-WORKFLOW. This is identity resolution for knowledge,
not user authentication or shared project membership.

## Goal

Represent the same person/project/object under explicit aliases without merging
unrelated names or crossing scopes. Preserve raw assertion wording and provenance.
The initial resolution policy is deterministic/user-confirmed; a model may suggest
candidates but cannot silently decide an ambiguous identity.

## Checkpoints and data

Add scoped Entity and Alias records with owner/scope composite constraints,
canonical label/type, normalized search key, raw display alias and origin/audit.
Choose uniqueness rules that permit genuine ambiguous aliases. Do not establish
a global name uniqueness constraint or link private aliases by global frequency.
Entity type labels do not confer permissions.

Add optional canonical entity references to claims while retaining their original
subject string, quote and valid interval. Backfill only unambiguous explicit
mapping or leave references null. A dedicated “self” link must be bound to the
authenticated owner/scope, never inferred from “User” or another person's name.

Implement owned create/list/detail/alias APIs, a resolution result with resolved,
ambiguous and absent states, and explicit user selection. Include name collisions,
case/Unicode normalization and historical rename handling. The server validates
every reference; client-supplied foreign IDs cannot bridge scopes.

Merging is a separate explicit action with preview, audit and reversible mapping
where possible. Limit it to the same owner/scope. Use redirects/identity lineage;
never rewrite original evidence or an old frozen trace to claim it had the new
canonical interpretation. Record retired aliases/merge decisions and prevent
redirect cycles. Cross-scope sharing is outside this phase.

## Retrieval and UI

Expand subject candidates using authorized explicit aliases before ranking.
Ambiguous matches stay separate; request clarification or show alternatives
rather than silently choosing one. Keep existing string-only subjects working.
Freeze entity/alias resolution used by a request and retain the exact original
evidence. Model access remains bounded to the same authorized scope/time.

Add a small entity picker/detail/editor to an existing client, with duplicate
warning and explicit alias/link/merge confirmation. If its client prerequisite
is absent, implement the tested API and document the UI as pending rather than
starting an unrelated application phase.

## Verification and exit

Test migrations with populated string claims, case/Unicode aliases, two people
sharing a name, same label in different scopes, self-identity forgery, foreign
entity IDs, merge/redirect cycles and correction/retry snapshots. PostgreSQL
constraints and API authorization both need execution evidence. Evaluate alias
retrieval against an explicit test corpus; do not label a fuzzy guess resolved.

Exit with auditable scoped links, ambiguity visible to the user, unchanged old
sources/replays and a documented resolution policy. Update OpenAPI/capabilities
and current client gates. No automatic extraction or cross-user entity graph.
