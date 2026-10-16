# Phase 20 — release readiness and a measurable baseline

Status: **Implemented; non-device baseline recorded on 2026-10-16.** Source,
recovery and evaluation checkpoints are implemented and locally checked. Emulator
intermittency, unavailable old-server checkout/model, manual assistive review and
live installation/HTTPS remain explicit limits, not completed target gates.
See [release readiness](../docs/RELEASE-READINESS.md), [STATUS](STATUS.md) and
[WORKLOG](WORKLOG.md) for actual evidence. Original inputs: source through Phase 18 at `fa2cbba`, actual
OpenAPI 96 paths/132 schemas, schema 0015, STATUS/WORKLOG, gap review G-01/G-03/G-04/
G-07–G-10/G-30/G-31/G-39/G-40. Read [FUTURE-ROADMAP](FUTURE-ROADMAP.md) and the shared
rules. Physical-Android and iOS checks are excluded and do not block this phase.

## Outcome and boundary

Establish a trustworthy server/web/emulator release baseline and safe upgrade
route before adding new behavior. Do not install into the live database, change
network exposure, delete private content or interpret historical 0005 as current
state. Live installation is a separately selected execution gate.

## Checkpoints

- **A — reconcile evidence.** Inspect source, migration history, generated
  contracts, capabilities and retained test reports. Audit protected migrations/
  prompts and fixture bytes/newlines. Reconcile stale current-status statements
  without erasing prior results. Re-exercise the cold-launch check on a suitable
  emulator; a new current-build pass does not retroactively pass an old run.
  Validate the existing private HTTPS proxy template on the laptop/test route.
- **B — legacy recovery prerequisite.** The 0015-only `operations.backup` cannot
  back up 0005. Design and test a narrowly versioned legacy encrypted export or
  independently verified encrypted PostgreSQL dump/restore procedure. Rehearse
  on populated disposable 0005, recover into a new isolated database with its
  matching old code/schema, then rehearse 0005→current-head upgrade, old replay,
  citations/hashes and rollback limits. Never upgrade merely to obtain a backup.
  Keep legacy artifacts explicitly separate from the 0015 backup format.
- **C — future recovery contract.** Define supported artifact/schema versions,
  authority quarantine and all-table/content inventory rules so future migrations
  cannot silently disable backup/erasure. Test fail-closed unknown tables and
  unsupported artifacts; specify forward upgrade versus unsupported downgrade.
  Do not broaden a backup manifest's accepted head without compatibility tests.
- **D — common evaluation baseline.** Reuse the five existing evaluation scripts
  for claims, documents, hybrid retrieval, extraction and episodes. Add a shared
  public/synthetic case manifest and cross-feature scorecard: useful answers,
  recall/MRR, evidence/entailment, uncertainty, corrections and latency/resources.
  Freeze a held-out set. Separate deterministic checks from local real-model
  probes and owner-consented private evaluation. No automatic model download.
- **E — closeout.** Run appropriate current server/PostgreSQL/web/emulator checks,
  keyboard/screen-reader web review where available, scoped dependency audits and
  documentation checks. Record exact skips and deferred physical gates. Prepare
  a concrete installation checklist with backup/restore evidence; do not execute
  it on a live installation within this phase by default.

## Data and interfaces

Prefer evaluation manifests/reports and versioned operator tooling. Any necessary
recovery-tool change preserves existing 0015 artifacts. No new runtime API or
prompt revision is required solely for this audit. Reports contain case IDs,
aggregate metrics/model digests and counts, never private text or credentials.
Migrations, if truly required, are additive after the actual head.

## Failure tests and verification

Test backup of an unsupported head, partial/tampered artifact, incorrect key,
wrong binary major, insufficient disk, existing restore target, interrupted
upgrade and recovery with old/deleted requests. Original database stays untouched.
Run populated PostgreSQL upgrades, Alembic drift checks and original replay.
Synthetic legacy fixtures must contain meaningful history, not empty schemas.
If a maintained old checkout cannot be recovered safely, document the missing
compatibility evidence rather than invent a successful legacy smoke test.

For source changes run pytest/Ruff and affected real PostgreSQL cases; for client
changes run their pinned checks. Documentation-only work uses link/UTF-8/scope
validation. Keep synthetic fixture cleanup restricted to checked task-owned paths.

## Exit

Every non-device gap has a result or explicit next owner/gate; legacy recovery
and upgrade have a reproducible disposable rehearsal; the baseline scorecard is
saved. Actual deployment/installation, representative live capacity and physical
validation remain visibly distinct. Stop at Phase 20. Phases 21–31 stay proposed.

## Recorded checkpoint results — 2026-10-16

- [x] A: source OpenAPI matches export (96 paths/132 schemas), protected-history
      audit, corrected current summaries, three strict current-build emulator cold
      launches and verified isolated TLS/proxy-template checks. Historical failures
      retained; manual screen-reader and actual private-network/system-trust gates
      remain open. `/admin` redirect failure was reproduced and fixed in the template.
- [x] B: separate encrypted0005 format/tool, populated19-table legacy restore,
      credential quarantine, transactional migration-failure rollback, successful
      forward upgrade/drift check and original cited reply/source-hash replay.
      Available Git history has0004 then0006 source heads, no maintained0005 server
      checkout: matching old-server HTTP is unverified, rather than fabricated.
- [x] C: explicit0005/0015 recovery inventory policy, unknown head/table/owner-model
      rejection, tool-major preflight and existing0015 artifact/erasure-ledger drill.
      Future migrations require an explicit compatibility/erasure/quarantine update.
- [x] D: five existing evaluation adapters reused, canonical-hash corpus manifest,
      eight heldout retrieval checks and saved aggregate scorecard. Fixture/span
      results remain separate from unassessed semantic usefulness/entailment.
      Real-model endpoint unavailable; no download or provider start attempted.
- [x] E: full PG18/SQLite760passed/24skipped; final affected23passed; Ruff160files;
      fresh Android224units plus lint/APKs; web56units/six PG Chromium; emulator
      HTTP/OS-dialog/force-stop/security results and failures separately recorded.
      Dependency audits, documentation checks and concrete installation checklist
      recorded in STATUS/WORKLOG. No live upgrade or later-phase implementation.

The new emulator HTTP suite passed on its instrumented retry after two missing-
request/provisional-text failures; an initial combined force-stop stage failed,
then its focused recovery run passed. No production Android fix is claimed from
these reruns. Keep this intermittency as a release-verification gate (G-41).
