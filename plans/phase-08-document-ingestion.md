# Phase 08 — immutable document versions and chunk retrieval

Status: planned. Prerequisites: Phase 03 and the existing Phase 2 server.
Apply STANDARDS and CODEX-WORKFLOW. Phase 07 is required only for its mobile
memory surfaces; backend ingestion can be implemented independently.

## Goal and checkpoints

1. Accept bounded text/Markdown uploads into an authenticated owned scope,
   preserving raw content and an immutable version/hash.
2. Produce deterministic exact-span chunks and a rebuilt lexical projection.
3. Retrieve/cite authorized document excerpts alongside existing claims.
4. Add upload/status/source UI only to a client whose prerequisite exists.

PDF is a separate checkpoint after the text path works. Defer OCR, archive
extraction, web crawling and arbitrary remote fetches. Record parser/tool versions
and format/size limits before adding another format.

## Data design

Extend source origin/trust constraints with a new migration; preserve chat-event
and user-note rules and hashes. A user-uploaded document is imported evidence,
not endorsement of every sentence. Give it a distinct origin/trust label and
keep the current explicit-claim endpoint's user-evidence rule intact. New raw
bytes and parsed text may need separate hashes; document the relationship.

Persist document/version metadata, owner/scope, bounded storage reference,
ingestion state/receipt and chunks pointing to exact version/code-point spans.
Display filename is metadata, never a filesystem path. Store blobs outside the
public web root with authorization on every read. Identical cross-user hashes
must not expose another user's upload or bypass ownership. Derived chunks/indexes
are rebuildable and never become new factual authority.

Define reupload semantics: stable source with a new immutable version, explicit
availability/effective dates and a default current-version rule. A request must
freeze the selected version; historical document queries cannot quietly pick the
latest bytes. Do not rewrite old request sources after reingestion. Separate
document version availability from the truth-validity interval of a claim.

## Proposed contract and ingestion flow

Design authenticated scoped upload, ingestion status and version/chunk reads.
Use an owner-bound upload ID and immutable input hash for replay. Reserve metadata
in a short transaction; parse/chunk outside it; publish an entire version/index
atomically after validating every span/hash. Expose processing/ready/failed states
and sanitized errors. Failed parsing must not publish partial searchable text.

Set quotas for bytes, files, parsing time, pages/chunks and output length. Reject
unsupported types and path traversal, hostile names, malformed encodings and
decompression bombs if compressed formats are later introduced. A filename/MIME
header alone does not validate a format. Preserve exact parsed source text;
normalization for search lives in a separate projection with mapping.

For PDFs, define page anchors and faithful extraction limits. A page number is a
locator, not a claim that OCR/reading order is correct. Failed or uncertain
extraction remains visibly incomplete and cannot yield fabricated citations.

## Retrieval/client changes

Add a typed document-evidence variant rather than inventing fake claim IDs for
chunks. Evolve cards compatibly or version the new variant with capability gating;
older clients still understand original claim cards. Apply owner/scope/version
availability before candidates, ranking and model context. Preserve budgets,
exact complete excerpt boundaries, conflicts among claims and immutable snapshots.

Document content is untrusted model input; embedded instructions cannot change
role, tools or permissions. Initial lexical retrieval must work without embeddings.
Android/web detail surfaces show imported origin, version and location; upload
controls remain disabled until the real backend capability exists.

## Verification and exit

Run populated migrations, PostgreSQL authorization/concurrency, upload replay,
size/path rejection, Unicode/hash/span round trips, parser failures and atomic
publish tests. Test two owners/scopes with identical content, historical versions,
old completed replay and prompt budget overflow. Evaluate a small documented
corpus with known exact excerpts; record real versus synthetic inputs.

The text path must upload, process, retrieve and cite through a real API/client
flow with no source-trust laundering. Record PDF inclusion or explicit deferral,
storage/cleanup limits, changed schemas/capabilities and target checks. Stop
before embeddings, extraction or automatic promotion of document statements.
