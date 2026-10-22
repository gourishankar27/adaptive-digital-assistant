# Phase 31 — PDF ingestion and document expansion

Status: **Selected; implemented source, actual checks/remaining gates in
STATUS/WORKLOG.** Text-PDF isolation, immutable original/extracted page mapping,
atomic publication and Android review/source display. OCR remains disabled: scans
are visible failures and no OCR need/quality evidence was measured. Archives,
Office, URL/directory ingestion stay outside scope. See
[setup and limits](../docs/PDF-INGESTION.md). No deployment.

Inputs: 08 text/Markdown ingestion,
20 recovery/inventory rules, 23 quality scorecard, G-14. Follow
[shared rules](FUTURE-ROADMAP.md). Start with one needed format, not every file type.

## Outcome

Ask ADA about selected local PDF material and inspect exactly which extracted
page/span supports an answer. Preserve original bytes/version and distinguish
extracted/OCR text from the original, including uncertainty and omissions.

## Checkpoints

- **A — text PDFs first.** Choose a maintained pinned parser after license/security
  review; isolate it with hard byte/page/time/memory bounds and no network or
  application secrets. Reject encrypted/unsupported/malformed PDFs safely. No
  embedded scripts, attachments, remote links, archive recursion or external OCR
  service. MIME and extension are not enough; validate actual content.
- **B — versioned extraction.** Retain immutable original hash/bytes, parser
  version, page/region mapping and normalized extracted-text hash. Citation spans
  count code points in exact extracted text, not pretend offsets into PDF bytes.
  Atomically publish complete searchable extraction or visible failed state.
  New extraction versions do not change old request evidence/replay.
- **C — OCR only after need is measured.** Treat scans as a separate opt-in local
  OCR job with model/language/license metadata, confidence/quality limits and page
  evidence. Evaluate en-US text/layout/table errors on agreed fixtures. Human
  correction creates a new derived version; OCR is generated imported text and
  never silently turns into an owner statement. Keep unsupported files visible.
- **D — useful document flow.** Preview exact upload/type/size/scope and progress,
  inspect page-linked quotes, reprocess explicitly and query only when ready.
  Preserve Phase 08 bounded text/Markdown behavior, D-source trust and opt-in
  retrieval. Reuse this source version mapping in Phase 23 evaluations and research only
  through explicit selected files, never filesystem crawling.

## Data/interfaces, failures and exit

Add a versioned extraction artifact/page map and processing receipt if needed;
update original-byte, derived-text, parser-cache and job-payload erasure/backup/
epoch inventory. Worker shares bounded capacity and cannot perform network inference
inside transactions. Propose limits only after representative file measurements;
do not weaken existing upload/body quotas silently. Test malicious/oversized/
compressed PDFs, parser hang/crash, timeout, Unicode reading order, repeated headers,
tables, partial publish, duplicate upload, wrong owner, deletion mid-extraction,
restore/replay and source hash mismatch. Use actual API/PG/source-card integration.

Exit with a demonstrably useful bounded text-PDF flow and honest extraction/source
mapping. OCR may remain disabled with a documented decision. Archives, Office files,
remote URL import and unrestricted directory access stay outside this phase.
