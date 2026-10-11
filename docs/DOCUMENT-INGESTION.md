# Text and Markdown documents — Phase 08

ADA imports bounded UTF-8 `.txt`, `.md` and `.markdown` files into an authenticated
owner's existing scope. Imported text is `imported_document` /
`imported_untrusted`, never an explicit user assertion. It cannot support the
existing claim/correction writer. Chat performs no extraction or promotion.
PDF, OCR, archives, crawling and remote fetch are deferred. Phase 10 implements
optional exact embeddings, disabled by default; this document records Phase 08.

## Upload and reads

All routes require the existing bearer credential. Other owners receive the same
404 as a missing resource; an admin monitoring grant grants no document access.
Private responses use `Cache-Control: no-store`.

| Route | Implemented behavior |
| --- | --- |
| `POST /v1/scopes/{scope_id}/documents/uploads/{upload_id}` | Raw UTF-8 bytes; query `source_id`, `filename`, optional timezone-aware `available_from` / `available_to`; Content-Type `text/plain` or `text/markdown`, optionally UTF-8 charset. New receipt 201, same-ID replay 200. |
| `GET /v1/scopes/{scope_id}/document-uploads` | Paged processing/ready/failed receipts in creation-descending order. |
| `GET /v1/document-uploads/{upload_id}` | Owned immutable-input receipt and current ingestion state. |
| `GET /v1/documents/{source_id}/versions` | Ready versions in version-descending order. |
| `GET /v1/document-versions/{source_version_id}` | Exact parsed text, source hash and upload metadata. |
| `GET /v1/document-versions/{source_version_id}/chunks` | Exact excerpts, code-point spans, hashes and line locations in ordinal order. |
| `GET /v1/document-versions/{source_version_id}/raw` | Original bytes as an attachment with a fixed safe filename and `nosniff`. |

The exported [OpenAPI](../contracts/openapi.json) defines exact DTOs and failures.
Lists return arrays, with limit 50/default, maximum 100 and offset at most 10,000.
The upload UUID belongs to its owner. Its fingerprint binds scope, stable source
UUID, filename, media type, raw content hash, requested availability and parser /
chunker versions. Retry the identical bytes and metadata; changed input is 409.
Use a new upload UUID with the same source UUID to reserve a new immutable version.
Version numbers include failed reservations, so gaps are valid.

Ownership is checked before buffering upload input. The server counts actual
streamed bytes and bounds receiving time to 15 seconds. It validates names as
metadata, never uses them as paths, accepts only the stated text media types and
extensions, checks strict UTF-8, rejects NUL/disallowed controls and known binary /
archive / PDF signatures. A filename or MIME declaration alone does not establish
accepted content. There is no multipart or compressed parser.

## Storage, publication and limits

Migration **0005** follows unchanged 0001–0004. It extends source origin/trust
constraints, adds uploads/chunks/search projection and adds default-empty document
snapshot arrays to retrieval traces. It preserves old prompts, hashes, evidence
and saved claim-card arrays. A downgrade refuses before deleting imported data.

Raw bytes live in private PostgreSQL BYTEA / SQLite BLOB storage, referenced by
the owner-bound upload UUID. There is no public web-root blob or filename-derived
path. Identical content across accounts has independent receipts and authorization;
hashes never grant access or cause cross-owner deduplication. Database/backups
remain private and the local database operator remains trusted.

Reservation commits in a short transaction. UTF-8 identity parsing, deterministic
chunking and initial validation run outside transactions. Publication revalidates
the reserved bytes/spans, then atomically inserts
the full source version, every chunk and lexical projection, then marks ready.
A failure retains a sanitized failed receipt and no searchable partial version.
A processing receipt can be explicitly replayed after its 30-second lease; attempts
are fenced and bounded at three. There is no background worker or automatic retry.

| Bound | Server |
| --- | --- |
| Raw file | 256 KiB |
| Reserved uploads per owner, including failed versions | 100 |
| Reserved versions per stable source | 20 |
| Total retained raw bytes per owner | 10 MiB |
| Chunk | At most 1,024 Unicode code points |
| Chunks per upload | 512 |
| Bounded parser elapsed time | 2 seconds |

Parser version is `utf8-identity-v1`; chunker version is
`exact-codepoints-lines-v1`. Both participate in the upload fingerprint. They use
Python 3.12's strict UTF-8 decoder and code-point strings, without an external
document parser. Identity parsing preserves BOM, CRLF, combining characters and all accepted
whitespace. Parsed UTF-8 SHA-256 equals raw SHA-256. Chunks cover the exact text
without normalization, prefer LF boundaries and record code-point offsets.
Line ranges identify the first and last character's line inclusively. The parse
time limit is an elapsed check on this bounded pure parser, not a process kill.
Only a separate rebuildable search projection is normalized. Retrieval rechecks
the full version/raw hash, exact span, quote hash, projection and line location.
Run `ada rebuild-document-search` locally to rebuild it; `rebuild-search` retains
its existing claim-only behavior. Raw blobs, failed receipts, versions and snapshots
are retained; no deletion/automated cleanup endpoint is implemented. Quotas include
retained failures. Future retention work is not part of Phase 08.

## Retrieval and compatibility

Capabilities advertise `document_ingestion=text_markdown_v1`, `document_uploads`,
`document_retrieval`, `document_citations` and `document_max_bytes`. Chat and direct
retrieval accept strict boolean `use_documents`, default **false**. Older clients
continue to use the original claim contract and request fingerprints.

| Frozen prompt | New-request retrieval |
| --- | --- |
| v1/v2 | Original prompt; no fresh evidence until an explicit upgrade. |
| v3 | Existing claim retrieval remains supported. Document requests require an explicit upgrade. |
| v4 | Claims and documents require `use_memory=true`; documents additionally require `use_documents=true`. |

New conversations freeze `ada-baseline-v4`. The existing audited prompt-upgrade
operation supports v1/v2/v3 to v4, preserving old/new prompts and personality and
incrementing revision. No migration silently upgrades a conversation. Completed
replay and failed-attempt evidence remain frozen. With `use_documents=false`,
the original default/options fingerprints remain unchanged; true uses a separate
domain-bound option hash.

Original `[M1]` claim cards remain in `citations` / `selected` / `candidates`.
Typed `[D1]` imported excerpt cards use separate `document_citations` /
`document_selected` / `document_candidates`; they contain source/version/chunk
identity, location, availability, trust and exact evidence, with no fake claim ID.
Unknown document labels are warnings for document-enabled requests. Older saved
answers are not reinterpreted as document citations. Resolve cards only from the
matching request snapshot, never today's latest document version.

Owner/scope, ready state and publication/availability checks precede lexical
candidates, ranking and context. For each stable source, choose its highest ready
version already published and available at the query instant. If that replacement
has expired, do not reveal an older version again. Backdated availability cannot
make a version known before publication. Availability describes whether a version
was accessible, not whether its contents were objectively true at that time.
Historical ambiguity still requires a date.

Claims retain conflict groups; complete document excerpts fill remaining shared
evidence/selected-item and whole-prompt budgets. Oversized excerpts are omitted
with recorded decisions. Untrusted evidence enters a user-role data block; embedded
instructions cannot grant tools, change identity or authorize writes. Model calls
still occur outside database transactions. Lexical ranking establishes relevance,
not truth, answer entailment or semantic-search quality.

## Client and installation boundary

Android exposes Documents only when the real capabilities are available. It uses
owned scopes, bounded file selection or exact pasted text, preview and explicit
Upload, status/version/excerpt reads and imported source cards. Its 64 KiB mobile
limit is stricter than the server limit. Upload recovery preserves exact bytes,
UUIDs and metadata in the encrypted account/server-bound journal, with explicit
check/resume/discard; restoration never automatically POSTs. Existing chat/memory
recovery and old encrypted records remain supported. Admin web remains a metadata
monitor and exposes no private-document upload or read control.

Before running the Phase 08 source, back up the intended application database,
apply `python -m alembic upgrade head` to install 0005, and restart the one-worker
backend. Validate migrations on a disposable database first. This implementation
task does not deploy Phase 08 or apply 0005 to the application database. The
separately requested admin login repair installs 0004 and an explicit account grant;
using this new source afterward also requires 0005. See [STATUS](../plans/STATUS.md)
and [WORKLOG](../plans/WORKLOG.md) for actual evidence and remaining target checks.

Those installation statements describe the Phase 08 boundary. Current Phase 09
source requires head **0006**; `upgrade head` now includes the identity migration.
The final read-only Phase 09 application check observed 0005, with 0006 installation
still pending. See [ENTITIES-AND-ALIASES.md](ENTITIES-AND-ALIASES.md).
Those observations remain historical. Current Phase 10 source requires **0007**
and adds optional exact hybrid retrieval, kept disabled by default. See
[EMBEDDINGS-AND-HYBRID-RETRIEVAL.md](EMBEDDINGS-AND-HYBRID-RETRIEVAL.md) for its
installation/evaluation boundary; document trust, versions and frozen D cards are
preserved.
