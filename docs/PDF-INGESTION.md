# Selected text PDFs

Phase31 implements bounded text-PDF ingestion. OCR, scanned documents, Office
files, archives, URL imports and directory crawling remain unsupported. Old
text/Markdown uploads and request snapshots retain their behavior.

## What is stored

Each upload retains immutable original bytes and SHA-256 separately from the
normalized extracted text and its SHA-256. Parser `pypdf-6.21.2-text-v1`, image ID,
normalization `lf-page-newline-v1`, warnings and contiguous page spans are stored
on that upload. Spans count Unicode code points in extracted text, never PDF bytes.
Page maps identify the whole extracted page; bounding boxes/visual regions are
not implemented. Chunk quotes cannot cross a page boundary. D source cards show
the original request's page, exact excerpt, imported/untrusted provenance and hashes.

Extraction order can differ from visible reading order. Repeated headers remain
text; columns and tables are not reconstructed as reliable semantic structures.
Hidden text can be extracted. Compare important excerpts against the original
PDF visually. A valid hash establishes lineage, not truth or visual equivalence.

The worker reserves an upload before parsing outside database transactions and
publishes the complete source/chunks/search index atomically. Failed/processing
versions never enter retrieval. Unsupported files retain a visible failure and
their original bytes. An explicit new upload/version reprocesses selected bytes;
it never replaces an old extraction or completed answer snapshot.

## Limits and isolation

Server input remains 256 KiB per upload; Android keeps its existing 64 KiB limit.
The existing retained file/version/original-byte quotas remain in force. Separate
derived bounds are 16 pages, 256 KiB UTF-8 extracted text, 512 chunks, 50,000 visited
PDF objects, 2 MiB protocol output and one parser per API process. These deliberately
support small selected text PDFs, not general books or image-heavy reports. Resource
tests include a highly compressed 2 MB text stream; representative personal-document
acceptance is still required before proposing larger quotas.

The [2026-10-22 public fixture profile](../evaluations/text-pdf-profile-2026-10-22.json)
measures six generated layout families with the actual verified parser. These
are developer fixtures, not personal documents or human reading-order ratings:

| Layout | Original bytes | Extracted UTF-8 bytes | Pages / chunks | Fits Android quota |
|---|---:|---:|---|---|
| Simple text |607|31|1 /1|Yes|
| Two columns |803|59|1 /1|Yes|
| Table with repeated header |1,237|71|2 /2|Yes|
| Unicode mapping |1,026|16|1 /1|Yes|
| Dense text |86,572|50,768|16 /64|No; select a smaller section|
| Same dense text, compressed |10,796|50,768|16 /64|Yes|

Local parse/validation/chunk times were437–531ms after initial isolation
verification, including each Docker call and cleanup. They exclude upload/model
latency and cold image download. Compressed and plain originals had distinct
raw hashes and identical extracted hashes. This demonstrates why page count
alone cannot predict file size. The existing byte quotas remain unchanged;
larger or personally representative files still need acceptance measurements.

Reproduce the metadata-only profile from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_text_pdfs.py --manifest .pytest_cache/pdf-parser-image.json --output .pytest_cache/text-pdf-profile.json
```

The profile uses only fixed public synthetic files, no database or model. The
corresponding `tests/test_pdf_profiles.py` checks exact page spans, Unicode,
repeated headers, all expected column/table fragments and reading-order warnings.

The parser runs only in a verified local Docker Linux container: no network,
read-only root, no mounts/application environment, UID65534, no capabilities,
no-new-privileges, 256 MiB memory/swap cap, one CPU, 16 processes, 32 file descriptors,
256 MiB address-space limit and six CPU seconds. The host deadline is ten seconds
plus bounded cleanup. Stderr and container logs are disabled. Parser, image hash,
source labels and a real resource/egress probe must verify before the capability
is advertised. A remote Docker context is rejected. This trusts the local Docker
daemon/operator as part of the host boundary, not as a hostile administrator.
If a failed worker cannot be confirmed stopped, this parser adapter disables
itself before releasing host capacity. Later uploads return503 rather than
starting work alongside an unknown container. Resolve the Docker problem and
inspect/remove only its owned parser container before restarting the API; startup
must pass the isolation probe again. An API restart alone is not proof that an
old container was removed.

Encrypted, malformed, active-action/script, attachment, form and remote-link PDFs
are rejected. Image-only/blank pages fail the whole version with `pdf_ocr_required`;
there is no external OCR or partially searchable result. Parser failure is a fixed
code, not raw exception text. Saturation returns 429; missing isolation returns503.
If capacity is lost after reservation, check its retained failed receipt before a
consciously new upload; repeating a failed immutable upload does not reprocess it.

## Developer setup on Windows

These are installation instructions for a later authorized setup. This change did
not migrate or reconfigure the installed ADA server.

1. Use the root README's locked Python environment and start Docker Desktop with
   Linux containers. Confirm `docker info` succeeds and the Docker context is local.
2. Back up the intended database using the existing protected runbook. Stop ADA
   before a separately authorized upgrade. Source now requires migration0021:

   ```powershell
   .\.venv\Scripts\python.exe -m alembic upgrade head
   .\.venv\Scripts\python.exe -m alembic check
   ```

3. Build the secret-free allowlisted parser context:

   ```powershell
   .\.venv\Scripts\python.exe scripts/build_pdf_parser.py
   ```

4. If enabling PDF uploads on that host, set literal `.env` values, using the
   absolute forward-slash path to the generated manifest:

   ```dotenv
   ADA_PDF_INGESTION_ENABLED=true
   ADA_PDF_PARSER_MANIFEST=G:/your-checkout/.pytest_cache/pdf-parser-image.json
   ```

5. Restart one Uvicorn worker through the existing private startup procedure.
   Authenticate and check `/v1/capabilities`: `pdf_ingestion=ada-text-pdf-v1` means
   the actual isolation probe passed. The old `document_ingestion=text_markdown_v1`
   remains unchanged. Docker unavailable, an edited worker/manifest or missing
   cgroup restrictions keeps PDF capability off. Rebuild after parser/source changes.
6. Build/run the updated Android client. Open Documents, choose an owned scope,
   New upload, then choose a small PDF with selectable text. Review filename,
   exact binary type/size, scope and availability; tap Upload reviewed document.
   Wait for Ready before enabling document use in chat. Open its extracted text,
   page chunks and D source cards. The Android preview describes exact selected
   bytes; it is not a PDF visual renderer.
7. After a lost response, check the original upload ID. Explicit Resume uses the
   identical encrypted reservation. Discard removes local recovery only. Failed
   files need a consciously new upload after correction; there is no automatic retry.

## HTTP and recovery

The separate authenticated binary route is
`POST /v1/scopes/{scope_id}/documents/pdf-uploads/{upload_id}` with
`Content-Type: application/pdf` and existing source/filename/availability query
fields. The old text route still rejects PDFs. Existing upload/version/chunk reads
gain optional extraction/page metadata. Original bytes are available as safe
attachments through the existing version raw route when ready and the new
`GET /v1/document-uploads/{upload_id}/raw` for retained failed/processing versions.
No raw original is executed or rendered as browser HTML.

0021 adds nullable extraction metadata and the separately selected19A device tables:
76 installed tables, 63 owner-content tables. Backup-v7 includes originals,
derived text/maps, chunks and device drafts. Older v1–v6 artifacts remain readable.
Restore quarantines credentials/automation and device signing registrations;
saved content remains untrusted. Owner deletion covers these tables and projections;
offline copies and existing encrypted backups require their existing separate policy.
Populated PDF/device history blocks destructive downgrade before DDL.

## Dependency review and verification

[pypdf6.21.2 on PyPI](https://pypi.org/project/pypdf/6.21.2/) supplies the pinned,
hash-locked wheel in `ops/pdf-parser/requirements.txt`. Its BSD-3-Clause license
and notices stay in the installed wheel/container. Review the
[upstream security advisories](https://github.com/py-pdf/pypdf/security/advisories)
before future upgrades; a pin and sandbox do not establish absence of vulnerabilities.
The [6.21.2 release](https://github.com/py-pdf/pypdf/releases/tag/6.21.2) includes
cross-reference size/repeated-load security fixes. Review included the
[xref advisory](https://github.com/py-pdf/pypdf/security/advisories/GHSA-gmh7-3g9r-mjh5)
patched in6.21.2 and
[image-loading advisory](https://github.com/py-pdf/pypdf/security/advisories/GHSA-5hx5-vpf9-5wcv)
patched in6.21.1. Pillow and image extraction are absent from this text-only worker.
The API process does not import pypdf or install crypto/OCR extras.

Use a dedicated `ada_phase2_test` database and explicit
`ADA_TEST_PDF_MANIFEST` for `tests/test_pdf_flow.py`, `test_pdf_limits.py` and
`test_pdf_edge_recovery.py`. Native PostgreSQL covers populated upgrade, schema
drift, exact replay and encrypted restore. `scripts/verify_pdf_edge_android.py`
uses a separate validation APK, synthetic public files, real HTTP/Keystore and
actual process stop. Actual results, failures and unrun target checks are in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md).

## Phase31 verification and acceptance boundary

The bounded text-PDF implementation covers all four checkpoints. OCR is an
explicit deferred decision, not an enabled fallback.

| Checkpoint | Verification |
|---|---|
| A: isolated parsing | Actual local Docker UID/cgroup/no-egress/no-ADA-environment probe; malformed/encrypted/active input, compressed expansion, huge xref, hang, crash and output-flood tests. Cleanup faults cannot leak parser capacity. |
| B: immutable extraction | SQLite and native PostgreSQL publication, Unicode/code-point mapping, original and text hash checks, duplicate/conflicting uploads, new versions, owner/epoch/deletion fences, populated upgrade and encrypted restore. A PDF-specific completed-answer replay test retains its original page citation after a new extraction. |
| C: conditional OCR | OCR remains disabled. Blank/scanned pages fail the complete version visibly; the API and S24 FE tests verify that failure and retain no searchable partial text. No OCR model was evaluated or approved. |
| D: Android flow | Separate validation app on S24 FE Android16/API36, actual HTTP, Keystore and force-stop: exact binary review, two-page extraction, D-page source display, visible scan failure, GET-only restore and one explicit original upload. |

The physical automated stages passed on 2026-10-22. The user confirmed the public
sample's page/source readability without overlap or clipping, then completed the
reopened review with Finish review. Detailed runs and retained failures/corrections
are recorded in STATUS/WORKLOG.
These tests use small public synthetic documents and an explicit fake answer
provider. They establish ingestion, lineage and recovery correctness, not real
model answer quality or acceptance of every personal PDF. Representative files,
column/table semantic comparison, TalkBack announcements and older Android devices
remain further acceptance work. Page mapping does not provide PDF rendering,
highlighted bounding boxes or reliable table reconstruction.

To reproduce only the PDF phone checks, first configure a dedicated test database
and the verified parser manifest as above. Build the separate validation APK:

```powershell
Push-Location apps/android
.\gradlew.bat '-PadaValidationApplicationId=dev.ada.validation.phase19' assembleDebug assembleDebugAndroidTest
Pop-Location
$env:ADA_TEST_DATABASE_URL = 'postgresql+psycopg://test-role@127.0.0.1:55421/ada_phase2_test'
$env:ADA_TEST_PDF_MANIFEST = (Resolve-Path .pytest_cache/pdf-parser-image.json).Path
.\.venv\Scripts\python.exe scripts/verify_pdf_edge_android.py --device '<adb-device-id>' --pdf-only
```

The example database must already be an isolated test instance; substitute its
actual test role/port. The runner requires the expected S24 FE model before any
physical installation, creates a disposable schema and removes its validation
packages/reverse mapping afterward. It never installs over the normal ADA app.
`--manual-review` adds an optional public-data screen using the actual document
and source components. Inspect both tabs and tap **Finish review** within nine
minutes; elapsed time is never recorded as human acceptance. No native library
or model is required. Rebuild without the validation property afterward to
restore ordinary APK outputs; that build does not install or deploy anything.
