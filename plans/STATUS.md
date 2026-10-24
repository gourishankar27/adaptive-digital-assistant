# Phase status

Current overview updated 2026-10-22 America/Phoenix; historical entries retain their
own dates and verification provenance. Update after implementation and verification.
“Planned” means a specification exists, not that code or a working UI exists.

**Android shared voice composer (2026-10-22):** app26/0.31.1-voice-composer adds
tap controls and hold/release on the same microphone. Available partial ASR appears
in the editor; final recognition becomes an editable encrypted draft. Ordinary
Send explicitly approves exactly that wording through the existing reviewed-voice
route, preserving the original generated transcript, typed prefix and exact
journal-before-HTTP order. Release/edit/recovery never submits. Cancellation,
permission/setup release, stale callbacks, storage failures and duplicate Send
remain fenced. Keyboard/accessibility have the tap/Record route.
Schema0021, OpenAPI164/216, journal18 and dependency locks remain unchanged.
Final normal debug/test APK builds, Android313 unit checks, lint0 errors/24 warnings,
Ruff and SQLite/PostgreSQL voice56 checks passed. The separate
API37 emulator passed actual touch/Compose/HTTP/Keystore flows: five stages, then
affected multiline-IME/cancellation reruns and physical-tap/semantic-long-click
verification. Earlier cancellation and setup-timing failures and their fixes are
retained in WORKLOG. No normal phone app installation or native S24 FE speech/
partial-result/TalkBack acceptance is claimed; these remain target verification.
See [usage](../docs/VOICE-INTERFACE.md) and dated WORKLOG for commands/results.

**Manual startup clarity (2026-10-22):** `start.ps1` now prints immediate progress;
the foreground runtime prints its actual listening address, readiness/explorer
URLs, conditional configured HTTPS admin/Android addresses and a shutdown notice.
Success is announced only after Uvicorn binds. One worker, ownership/recovery
gates, disabled access logs/proxy-header trust and quiet Ctrl+C remain intact.
The usage guide now leads with password/Tailscale setup and the three-window
daily sequence, current head0021 and layered502 troubleshooting.
Focused final checks: **15 passed / 0 skipped**, Ruff lint/format283 files,
unchanged OpenAPI164 paths/216 schemas,63 guide links/anchors and balanced fences.
Read-only live checks found API8000 → Caddy18764 → tailnet HTTPS ready/0021,
admin HTML200, healthy PostgreSQL5433 and the configured Ollama tag installed.
An earlier API interruption/502 was observed; its cause remains unconfirmed.
No live API/proxy restart, migration, password/configuration change or deployment
was performed. The banner appears on the next manual start. Full regression,
PostgreSQL fixture matrix, client/device and inference checks were not rerun for
this console/documentation change. Details and prior evidence remain below/in WORKLOG.

**Phase31 bounded text-PDF exit verified (2026-10-22):** isolated selected uploads,
immutable original/extracted hashes and page/code-point maps, atomic publication,
exact Android review/source cards and restart recovery are implemented. Final
PDF checks47passed/no skips on SQLite/native PostgreSQL/actual Docker, plus six
public layout/profile checks; separate
S24 FE/API36 HTTP/Keystore/force-stop stages passed. Android306units, no lint
errors, debug/unsigned-release/test APK builds and Ruff passed. The user confirmed
public-sample readability/no overlap or clipping; the final review stage completed
through Finish review. TalkBack and representative personal-file acceptance remain
pending. OCR is disabled by the phase's conditional decision.
Current source **0021 /76 tables /63 owner-content /backup-v7**, OpenAPI164paths/
216schemas, Android25/journal18. PDF defaults off; installation requires a later
authorized migration/verified parser setup.19A activation/exit remains open after
both quality failures. No normal app upgrade, live migration, later-phase work or
deployment. Dated records below preserve broad-regression provenance and failures.
[PDF guide and reproduction](../docs/PDF-INGESTION.md).

**Phase30 source/local verification (2026-10-22):** explicit scoped projects,
goals/tasks, requested exact Save review, immutable revisions/source resume,
balanced personal/development selected-work briefs and encrypted GET-only recovery
are implemented. Optional questions use25 consent/cadence; only27 schedules a
separately reviewed reminder. Task edits pause linked automation; no inferred
commitment, external execution or private admin reader. Current source:
**0020 /74 tables /61 owner-content /backup-v6**, OpenAPI157paths/206schemas,
Android24 /0.30.0-work and journal17 (v1–v16 readable).
Full1206 passed/33 skipped preceded final guards; post-guard affected221/5,
final Phase30 selection49/1 and linked-automation native restore1 passed.
Android300 units/no lint errors/debug+unsigned-release and web72 units/8Chromium
cases passed. Real HTTP/emulator force-stop recovery and final closeout provenance
are in the dated record below and WORKLOG. Human usefulness and physical
accessibility remain open. No installed DB/app/service upgrade or deployment;
Phase31 remains planned. [Guide](../docs/PROJECTS-AND-FOLLOW-THROUGH.md).

**Phase29 study/interface locally checked (2026-10-21):** Android23 adds explicit
public voice preview, engine/model status, strict local manifest/byte validation
and playback guards. The candidate/license study and opt-in installation/removal
design are documented; no new runtime/model/installer/activation is enabled.
Existing platform ASR/offline TTS, schema0019, OpenAPI145paths/193schemas and
journal16 are preserved. Target device/quality/resource/focus/permission gates
remain pending under the phase's permitted study-only exit. See the dated record
below and [NATURAL-LOCAL-SPEECH](../docs/NATURAL-LOCAL-SPEECH.md). No deployment.

**Phase28 initial job set implemented and locally verified (2026-10-21):**
opt-in source-pinned idle reports and catalogue question drafts, typed Android
review/GET-only recovery, aggregate admin monitoring, source/foreground/consent/
lease/erasure fences and restore quarantine. Model summaries remain disabled;
the public cancellation probe does not establish GPU stop or useful native output.
Current source requires0019/70 tables, owner-content57 and backup-v5; OpenAPI145
paths/193 schemas. Android22/0.28.0-reflection uses encrypted journal16 (v1–v15 read).
Global reflection/owner consent default off. Full1161 passed/32 skips preceded
final guards; final affected282 passed/4 skips, plus4 completed-turn checks passed.
Android283 units/no lint errors/two final real HTTP force-stop stages; web72 units/
8 Chromium cases passed. See the detailed dated record below and
[the guide](../docs/IDLE-REFLECTION-AND-DREAM-REVIEW.md). No live migration, normal
app installation, later phase or deployment. Physical/installed-host/native-summary
quality and GPU gates remain explicit.

**Phase27 source/local verification:** reviewed timezone reminders/catalogue
questions, durable origin-bound consent, fenced dispatch, private inbox/receipts,
Android21/journal15 and read-only admin counts are implemented. Source requires
0018/65 tables; recovery-v4 includes53 owner-content tables and restore quarantine.
Global dispatch/owner consent default off; foreground in-app polling only, no push.
The preceding run passed1042 tests/30 skips, then107 affected tests/3 skips after
two final calendar/host-gate corrections. Android275 units/two real emulator HTTP
stages and web71 units/seven Chromium cases passed. The 2026-10-21 reconciliation
below records the original 2026-10-19 evidence, rather than claiming a new run.
No live migration, normal app installation or deployment. See
[the guide](../docs/DURABLE-SCHEDULING-AND-REMINDERS.md) for controls and target gates.

**Phase 26 source and isolated validation:** owner-logon supervision, single API
ownership, bounded recovery, fixed health/resource metadata, reversible AC tools
and protected unattended backup/restore are implemented. No API/schema/prompt
change. Native Windows/PostgreSQL, same-identity Task Scheduler key access,
owned-proxy/crash/replay and configured-model short rehearsals passed. The first
four-hour disposable soak failed after approximately 3h15; its evidence remains
below. Windows receipt-sharing and foreground port guards were corrected, and
the final full suite passed 975 tests with 27 skips. The separately authorized
continuous rerun passed 14,400.39 seconds: 14,278 health checks, zero unavailable
samples, 1,428 public replies, encrypted backup, protected-key isolated restore,
graceful stop and verified cleanup. This closes the four-hour development gate
using an explicit fake provider; it does not establish sustained native inference
or installed-host uptime.
Installation, reboot/logon, sleep/resume, representative RPO/RTO, off-device
recovery and a separately authorized 24-hour trial remain target gates. See the
[operations guide](../docs/ALWAYS-ON-OPERATIONS.md). No production tasks, power
changes, live database migration or deployment.

**Android design hardening:** app20/0.25.2-ui fixes verified presentation,
feedback, selection, confirmation, short-window, appearance and reading-position
gaps. S24FE/API36 automated checks use a separate synthetic validation app;
manual TalkBack/audio remain pending. See the dated entry below and
[verified gap matrix](../docs/ANDROID-DESIGN-GAPS.md#8-verified-follow-up-2026-10-18).
Server contracts/private state remain unchanged; no normal app update/deployment.

**Phase25 source/local verification:** opt-in topic/depth/cadence controls,
bounded chat/inbox questions, original-source pins and explicit conversation/
ordinary-answer recovery are implemented. Current source needs0017/60tables;
OpenAPI126paths/168schemas preserves117earlier paths/155non-capability schemas.
Curiosity is off by default; no notifications/scheduler or auto-memory. Actual
checks, corrected failures, emulator intermittency and remaining target gates are
recorded below and in [the guide](../docs/CONVERSATIONAL-CURIOSITY.md). Phase24's
existing uncommitted work was preserved. No live migration, phone install or deployment.

**Phase24 source/local verification:** default-off owner-approved public research
now has an actual isolated Docker egress boundary, exact request previews, saved
untrusted W evidence, local answer/replay and Android approval/recovery. Schema
stays0016/57tables; OpenAPI117paths/156schemas preserves released contracts. See
the dated record/closeout below and [runbook](../docs/SECURE-WEB-RESEARCH.md) for
actual checks, corrected disclosure error and remaining physical/host/quality
gates. The running private service and normal phone app were not updated.

**Phase23 source/local verification:** calendar-window lookup, explicit v5 context
upgrade and review cues are implemented. New chats retain v4, semantic stays off,
and schema stays0016. See the dated Phase23 record below for actual checks,
native-model findings and remaining gates. This work has not been deployed to
the separately installed Phase22 private service or physical S24FE.

**Subsequent authorized private installation:** see the 2026-10-16 Windows/Tailscale
setup follow-up at the end of this file and the
[step-by-step guide](../docs/PRIVATE-SETUP-WINDOWS-TAILSCALE.md). Live0016 and the
private HTTPS route are now observed/running; owner password enrollment and actual
laptop admin/S24FE sign-ins are confirmed. Earlier implementation-only
no-deployment statements retain their original evidence boundary.

**Phase22 source update:** current source requires0016/57tables and exports
105paths/138schemas. That implementation run left live enrollment/installation
pending and used only isolated validation services/databases. The authorized setup
above records subsequent live results; earlier observations retain their own dates.
See the Phase22 entry for actual checks, skips and remaining target gates.

**Historical authorized local-operation update, 2026-10-16:** the configured Docker
PostgreSQL17.11 database was freshly verified at0015/54tables. No-op upgrade and
schema-drift checks passed. Current loopback API8000, built admin preview5173 and
Ollama11434 were started; synthetic owner/admin/real-model/replay checks passed.
Existing accounts, credentials, grants and saved records were preserved; no reset
was needed. This supersedes historical installation-pending statements below
for the local schema/current-server only. Remote HTTPS, physical-phone and G-41
release-reliability gates remain separate. See the follow-up entry at the end and
[Windows database administration](../docs/DATABASE-ADMINISTRATION-WINDOWS.md).

| Phase | Status | Evidence / next gate |
|---|---|---|
| 00–02 | Implemented baseline | Packaged Linux run: 60 passed/50 skipped. User's Windows PostgreSQL run: 105 passed/3 fixture failures/2 skipped. Real chat reported by user. |
| 02A | Target gate verified | Prior Linux: 61 passed/50 skipped, four installer tests, Ruff passed. This Windows baseline: 61 passed/50 skipped; dedicated PostgreSQL 109 passed/2 expected SQLite lock skips. |
| 03 | Checkpoints A–C implemented; local verification passed | Typed/exported API and 47 synthetic fixtures; Android/web HTTP, connection/state/design foundations. Windows/PostgreSQL 114 passed/2 expected skips; final affected contract rerun 5 passed. Ruff passed. Android 15 unit + 3 emulator tests, lint/debug/unsigned release builds; web 28 unit + 3 Chromium browser tests, clean install/typecheck/lint/build. Physical phone and manual accessibility/HTTPS checks remain. |
| 04 | Checkpoints A–D implemented; local verification passed | Keystore credential/exact journal, owned conversations/history/chat, identity-verified recovery, explicit retries and original sources. Android 57 unit tests, lint/debug/unsigned release builds, 11 emulator tests + 2 actual force-stop stages passed in small landscape at 1.5× text. PostgreSQL/SQLite 116 passed/2 expected skips; Ruff passed. Physical phone/HTTPS/manual accessibility/real-model verification remains pending. |
| 05 | Checkpoints A–C implemented; Windows/PostgreSQL checks passed | Migration 0004, explicit UUID grants, bounded audit, six typed metadata routes and cached non-generating health. Dedicated suite 147 passed/2 expected SQLite skips; final provider refinement 4 passed; Ruff passed. Intended application DB installation, HTTPS and operational performance verification remain pending. |
| 06 | Checkpoints 0/A–D implemented; local Windows/PostgreSQL/Chromium checks passed | Read-only admin dashboard, three Settings palettes, memory-only sign-in/current-role cleanup, metadata views and bounded polling. Web 45 unit tests and five production-build Chromium tests; PostgreSQL suite 152 passed/4 documented skips. HTTPS/manual accessibility/other-browser/load checks remain. |
| 07 | Checkpoints A–D implemented; local Android/PostgreSQL/emulator checks passed | Owned memory/evidence, reviewed writes and encrypted same-ID recovery, valid-time corrections and new static profiles. Android 98 unit + 21 emulator tests + 4 actual force-stop stages passed. Physical S24 FE/Android 16, HTTPS/TalkBack/real-model checks remain. |
| 08 | Text/Markdown checkpoints 1–4 implemented; local verification passed | Migration 0005, atomic versioned uploads, exact chunks/lexical projection, typed imported evidence and Android upload/recovery/source UI. Backend 244 passed/7 expected skips; web 51 unit/6 Chromium. Android evidence below. PDF deferred; application 0005 installation and target checks remain. |
| 09 | All selected checkpoints implemented; local verification passed | Additive 0006, owned explicit aliases/self/claim links, previewed reversible merge, historical frozen retrieval and Android reviewed recovery. Full backend 271 passed/8 skips; final affected PostgreSQL/SQLite 35 passed/1 skip. Android 134 unit/25 emulator tests + 8 actual force-stop stages; web 51 unit/6 Chromium. Application 0006 and physical-phone/HTTPS/real-model checks remain. |
| 10 | Checkpoints 1–4 implemented; disabled exit locally verified | Additive 0007, digest-bound bounded embeddings/index rebuild, exact scoped ranking, lexical fallback and frozen diagnostics. Full backend 307 passed/8 skips; final affected 37 passed. Synthetic comparison/capacity, Ruff and web checks passed. Real-model quality/resources and application 0007 installation remain pending; semantic is disabled by default. |
| 11 | Implemented; cold-launch and target verification remain | Additive 0008, bounded selected-source suggestions, exact reviewed revisions, immutable endorsements/support, same-key receipts and encrypted Android inbox. Backend/Ruff/web/evaluation checks, 145 Android unit tests, 26 emulator tests and ten force-stop stages passed. The strict cold-launch gate failed. Application 0008/physical-phone/HTTPS/representative quality remain. |
| 12 | Checkpoints implemented; local verification passed | Read-only calculator/memory/source registry, separate bounded native protocol, exact approvals/fenced durable receipts, Android encrypted v6 recovery and admin state counts only. Final PostgreSQL/SQLite 440 passed/18 documented skips; Android 155 units, focused emulator HTTP/force-stop/cold launch; web 53 units/six PG Chromium tests; three real qwen3.8:27b tool flows. Application 0009 installation, S24 FE/Android 16, HTTPS/manual accessibility/resource checks remain. No later phase or deployment. |
| 13 | Implemented; local gates passed; target verification pending | Head 0010, exact source-linked generated episodes, bounded leased/fenced summary/pending-proposal/lexical jobs, private navigation snapshots, Android v7 history/recovery and admin metadata. PostgreSQL/SQLite 516 passed/19 expected skips; 164 Android units and emulator HTTP/restart/cold launch; 54 web units/six PostgreSQL Chromium checks; four real native summary cases. Application installation, physical S24 FE/Android 16, HTTPS/accessibility/load and broader summary quality remain. Stop at Phase 13; no deployment. |
| 14 | Implemented; local exit gates passed; target verification pending | Head 0011, explicit account/scope/profile/conversation preferences, immutable exact receipts, opt-in bounded session tone and frozen request expression. Full PostgreSQL 18/SQLite 562 passed/21 skips; final affected 74 passed/3 skips; Android 174 units and emulator HTTP/force-stop/cold launch; web 54 units/six PostgreSQL Chromium cases. Intended installation, S24 FE/Android 16, HTTPS/accessibility and native-model wording/performance remain. No Phase 15 or deployment. |
| 15 | Implemented; local verification passed; target verification pending | Head 0012, opt-in selected-interaction observations, independent evidence/review, scoped learned defaults and bounded source-linked continuity. Full PostgreSQL/SQLite 587 passed/22 skips; final affected 172 passed/6 skips; Android 186 units and real HTTP review/recovery/source-card flows; web 54 units/six PostgreSQL Chromium cases. Intended installation, physical S24 FE/Android 16, HTTPS/accessibility, representative preference accuracy, native-model wording and retention policy remain. No later phase or deployment. |
| 16 | Implemented; local verification passed; target installation/device checks remain | Head 0013, durable owned stream/checkpoint/SSE, exact-attempt Stop and fenced terminal publication; Android 0.16.0-streaming and admin metadata. Full PostgreSQL/SQLite 631 passed/23 skips, final affected 92 passed/2 skips plus two real TCP slow-observer checks; Android 194 units, portrait/compact HTTP UI and force-stop/cold launch; web 55 units/six PG Chromium cases; real Ollama completion/Stop/legacy follow-up. Application 0005 installation to 0013, S24 FE/Android16, HTTPS/manual accessibility/load and retention policy remain. No later phase or deployment. |
| 17 | Implemented; partial S24 FE verification; permission/focus issues require 17-A | Head 0014, owner-bound original ASR/reviewed endorsement lineage, exact voice fingerprints; Android 0.17.0-voice on-device-only input, en-US default, encrypted v10 review/recovery and independent offline TTS. Final PostgreSQL/SQLite 695 passed/23 expected skips; Ruff/format144 files. Android 211 units, seven normal/two compact emulator checks, four force-stop stages and cold launch; web 55 units/six PG Chromium cases. Historical local results above are preserved; current S24 FE quiet/offline audio, speaker/lifecycle, recovery and font checks are recorded in the audit below. Permission/focus hardening, portable physical tests, intended installation, service resources/battery, accessories/calls, older APIs and HTTPS/manual accessibility/retention remain. No later phase or deployment. |
| 17-A | Hardening implemented; testing paused by user | Permission lifecycle fencing, per-request audio focus leases and isolated physical runner implemented. New API36 phone OS-dialog/HTTP/Keystore/force-stop checks passed; native full-focus loss/interruption callback observed, but audible stopping remains unconfirmed. Resume the separate native focus trials and remaining target matrix; see checkpoint below. |
| 18 | A–D implemented in source; validation paused by user | Head0015, digest-only device lifecycle, owner rate/body/admission bounds, encrypted PostgreSQL recovery drill, confirmed all-content erasure, Android v11 journals/settings and admin privacy cache fencing. Full backend747passed/23skipped, affected62passed/1skip, Android224units, six Chromium cases and API36/37 isolated checks recorded below. Final audit/remaining target gates are open; no deployment or live migration/erasure. |
| 19 | Conditional plan | Phases 12/18 plus measured device or selected integration requirements. |
| 20 | Implemented; local non-device baseline recorded, release limits remain | Separate encrypted0005 recovery/current policy, populated restore/upgrade/replay, saved five-component plus holdout scorecard and Caddy lab validation. Full PG18/SQLite760passed/24skipped; final affected23passed; fresh Android224units, web56units/six Chromium, emulator cold/HTTP/dialog/recovery/security evidence below. Preserve intermittency and unavailable model/old-server/manual/live gates. No installation or deployment. |
| 21 | Implemented; local connectivity verified, target/recovery gates remain | Named Android HTTPS addresses/import, public login preflight, TLS/DNS diagnostics, fixed same-origin health proxy and private Caddy routes. Actual ADA/TLS/SSE host rehearsals, Android metadata UI/negative TLS and web/backend checks below. G-41 intermittency remains; no real VPN/firewall/certificate deployment. |
| 22 | Password/session checkpoints A–E implemented; source and isolated verification, live/target gates separate | Explicit hidden-prompt enrollment, pinned Argon2id, digest-only rotating families, bounded pre-auth, Android refresh-only Keystore and HTTPS HttpOnly admin cookies. Dated checks/skips below; no live password, migration or deployment. |
| 23 | A–E implemented; measured opt-in/disabled decision, local verification | Explicit claim intervals/time clarification, original-source/history ranking under optional audited v5, request diagnostics and Android review cues. V4 remains default; semantic disabled because supported weights absent. Public fixture/native comparison and remaining cases in dated entry; no migration/deployment. |
| 24 | A–E implemented; default-off, local verification and target limits recorded | Verified isolated approved Python/Wikipedia pilot, immutable W sources, explicit imported notes and Android v13 exact recovery. Actual Docker/public/native/PG/emulator checks and corrected failures below. No migration, activation or deployment. |
| 25 | A–E implemented; opt-in local chat/inbox verification, target/quality limits remain | Migration0017, owner-wide controls/quotas, inspectable catalogue/original pins, atomic opening/ordinary answer and Android v14 queued recovery. Dated full/affected/PG/native/emulator evidence and skips below. No scheduler, auto-memory or deployment. |
| 26 | Source and four-hour development soak passed; target gates remain | Final full 975 passed/27 skipped. Corrected continuous explicit-fake rerun passed 14,400.39 s, 14,278 healthy samples, backup/restore and cleanup. Prior failed attempt preserved; installation/reboot/sleep/large-data/off-device/24-hour verification remains. |
| 27 | A–F implemented for foreground-inbox selection; local checks passed | 0018/65 tables, recovery-v4, default-off consent/dispatcher; backend1042/30 then final affected107/3, Android275 units/two HTTP force-stop stages, web71/seven Chromium. Physical/installed-host gates remain; no push/deployment. |
| 28 | Initial reports/question drafts implemented; local verification, summaries disabled | Detailed Phase28 record below preserves the full/affected/native/emulator evidence and open target gates. |
| 29 | Study/interface/platform preview locally checked; physical activation pending | License-qualified shortlist, pinned byte contract, unchanged server/journal; no new runtime/model/installer. Dated checks and skips below. |
| 30–31 | Proposed roadmap; no implementation | See [FUTURE-ROADMAP](FUTURE-ROADMAP.md). Each requires explicit selection. |

Phase 02A's Windows fixture gate is closed. Phase 03's foundation builds and
local HTTP/browser/emulator gates passed. Phase 04 now implements the Android
chat MVP; target-phone/release verification remains distinct from local checks.
Phase 05 now supplies server admin authorization and monitoring metadata.
Phase 06 now supplies the read-only web dashboard. Phase 07 now supplies Android
explicit memory and new static personality profiles. Phase 08 now supplies bounded
text/Markdown ingestion and imported document retrieval. Phase 16 adds durable
streaming and explicit Stop; Phase 17 adds reviewed Android voice and separate
playback. Phase18 is implemented in source with verification still open; Phase19 remains planned. The separately requested admin repair installed 0004 and an exact
account grant. At the Phase 08 boundary, application migration 0005 was pending.
The final Phase 09 read-only check observed application head 0005 and one active
grant for the selected account; Phase 09 has not migrated it. Current source needs
0016 before operational use. Phase 09 supplies explicit scoped identities and
the Android review/editor. Phase 10 supplies optional exact hybrid retrieval,
deliberately disabled pending real-model measurements. Phase 11 adds explicit
selected-source proposals/review, while automatic extraction remains off. No deployment was performed.
If work is incomplete, record the checkpoint and exact blocking condition; keep
the usable earlier feature active. Missing device/database checks stay visible.

## Phase 08 verification details — 2026-10-10 UTC

Code: base `1ca228a` plus this working tree. Required/root/scoped instructions,
current source, OpenAPI, migration state and test baselines were inspected first.
Existing Phase 2 retrieval and Phase 03/04/07 Android flows met the prerequisites.
Android version is `0.8.0-documents`, versionCode 4. No dependency, lockfile,
wrapper or version-catalog change was needed. Machine evidence uses UTC; the
host's displayed local date was 2026-10-09, America/Phoenix.

| Checkpoint | Implemented behavior | Local evidence |
| --- | --- | --- |
| 1 | Owner/scope-bound raw UTF-8 text/Markdown upload, immutable receipt/fingerprint, processing/ready/failed state, quotas and exact version/raw reads | Actual authenticated API upload/replay; hostile Windows names/types/encodings; independent owners/scopes and quotas; PostgreSQL reservation, lease fencing and atomic failure cases |
| 2 | Identity parsing outside transactions; exact code-point/hash/line chunks; atomic full publication and rebuildable native lexical projection | Unicode/BOM/CRLF/combining/astral round trips; no partial searchable failure; rebuild checks; populated 0001/0003/0004 upgrades, Alembic schema/offline checks and preserved history |
| 3 | Separate typed D cards and trace arrays with imported/untrusted origin; owner/scope/time filters, shared complete-excerpt budgets and frozen replay | v3 claims/v4 explicit document upgrade; legacy hashes/prompts; failed retry and completed old-version replay; actual HTTP upload→cited response→new version→old replay; SQLite/PostgreSQL corpus evaluation |
| 4 | Capability-gated Android Documents, exact file/paste preview, explicit upload, status/version/excerpt inspection and encrypted same-ID recovery | Unit/HTTP/Compose/emulator and actual process-stop evidence below; no private-document control added to admin metadata dashboard |

Server bounds: 256 KiB/file, 100 retained receipts/owner, 20 reserved versions/source,
10 MiB retained raw bytes/owner, 1,024 code points/chunk and 512 chunks/upload.
Receive timeout is 15 seconds; bounded pure-parser elapsed check is 2 seconds,
not a hard process kill. Lease is 30 seconds with three fenced attempts. Raw blobs,
failed receipts, source versions and request snapshots remain private and retained;
quotas include failures. No deletion, background retry or automatic cleanup API.
PDF is explicitly deferred, as are OCR, archives, remote fetch, embeddings,
extraction, promotion and later phases. See [document contract](../docs/DOCUMENT-INGESTION.md).

Checks actually run:

- Initial ordinary pytest: 87 passed/69 skipped; initial dedicated PostgreSQL:
  152 passed/4 skipped. Initial Ruff passed across 48 files. Existing
  Starlette/httpx warning remains documented, not suppressed.
- Final ordinary pytest: **137 passed/114 skipped**, 33.96 seconds. PostgreSQL was
  absent from that command; its parameterizations were skipped, not counted as
  executed. Final `scripts/test-postgres.ps1`: **244 passed/7 skipped**, 69.46
  seconds. Seven skips are five SQLite row/shared-lock variants and two opt-in
  live-provider checks; corresponding PostgreSQL locking cases ran. Final Ruff
  lint/format passed across **58 files**.
- After full validation, stronger independent OpenAPI checks and real HTTP
  cited-document/version-replay assertions were added. Affected document API tests
  reran on SQLite and dedicated PostgreSQL: **6 passed**, 3.73 seconds. Runtime
  code was unchanged after the full backend run.
- Document corpus: nine versions, five positive and six negative queries; one
  public repository README excerpt at `1ca228a`, duplicated across two synthetic
  owners, plus seven synthetic documents. SQLite and PostgreSQL recall@5, MRR@5
  and exact evidence were **1.0**, with zero known-excerpt, isolation or negative
  query failures. These are small lexical fixtures, not answer-entailment or
  production latency measurements. Existing claim corpus PostgreSQL recall/MRR
  remained 0.8667, exact evidence 1.0, with zero isolation/negative failures.
- Web clean install: 270 packages, audit zero vulnerabilities; contract generation/
  freshness, typecheck, lint, **51 unit tests** and production build passed.
  Production-build Chromium: **6 passed**, 18.2 seconds, recorded 04:01:58 UTC.
  Known database-not-ready JSON gives fixed safe guidance, clears credentials and
  respects cooldown; the test then performs real PostgreSQL-backed sign-in.
  Unknown/private/malformed responses remain generic. No credentialed recording.
- Android baseline: pinned JDK 21/Gradle 8.13/SDK 36, **98 unit tests**, lint/debug
  build passed; lint zero errors/14 existing dependency availability notices.
  Final unit/lint/debug/unsigned release/test-APK build passed: **120 unit tests**,
  zero failures/skips, same lint notices. Final emulator evidence is appended below.

Failures were retained and corrected: document API/storage/retrieval collection
and invariant tests were red before implementation; seven Windows-name cases and
inclusive line-end semantics failed before fixes. Two synthetic retrieval fixtures
had invalid chunk size/date assumptions and were corrected. An old admin test
hardcoded head 0004; it now checks the supported head. Web readiness tests were
red before safe guidance. Android journal and receipt/content-integrity regressions
were red before fixes. No failing assertion or required case was disabled.

Final read-only compatibility audit against `1ca228a`: all 27 original OpenAPI
paths/31 operations and 43 schemas remain; old parameters, required fields,
security, response references and enums are unchanged. Optional document fields
are additive in seven schemas, with seven new paths. Released 0001–0004 are
unchanged. v3 prompt string is byte-identical to the previous baseline; four
legacy/default/time/memory option hashes match, including explicit false document
use. Authorization, historical version exclusion and frozen replay were reviewed.

Admin login repair: the configured database was at 0003; actual application
readiness returned sanitized 503 while liveness returned 200. A verified private
69,300-byte backup archive preceded upgrading that database to **0004** and the
user-authorized explicit grant for the exact existing `gourishankar` account.
Existing table row counts were preserved. No token rotation or model call. No
live listeners at 8000/5173 were available for the user's browser-session check.
**Application migration 0005 is uninstalled. The current Phase 08 source requires
0005 before restarting; applying it is a separate installation step, not a claim
that the updated browser can already sign in.**

Remaining target verification: physical Samsung S24 FE/Android 16 app installation,
real-server upload/citation/version review, actual network interruption, token
rotation/logout, trusted release HTTPS, TalkBack/hardware keyboard and manual
visual/IME/file-picker review, API 26 behavior and a real Ollama known-source
conversation. A phone briefly appeared attached, then disconnected before the
allowed read-only identity check; no phone installation or app interaction was
performed. Emulator/fixture checks are not physical-phone or real-model evidence.
Web trusted HTTPS, other-browser/manual accessibility and operational load checks
remain. Opt-in provider health checks were not enabled. No later phase or Phase 08
deployment is implemented.

Next eligible implementation is Phase 09 only if separately selected. This task
stops at Phase 08; installation and target verification limits remain visible.

## Phase 07 verification details — 2026-10-09 UTC

Code: base `b828192` plus preserved Phase 05/06 working-tree changes and this
Phase 07 Android change; app version `0.7.0-memory`, versionCode 3. Required/scoped
instructions, current source/OpenAPI and tests were inspected before implementation.
Phase 04 and existing Phase 1/2 memory/personality APIs met the prerequisites.

- A: Memory navigation, owned scope pagination and server-paged current/as-of/history
  claims. Query/identity epochs fence late success; any current-session 401 clears
  private state even after changing views. Exact source/hash/quote detail and
  replacement links preserve IDs. Overlapping different assertions are advisory;
  superseded status never substitutes for interval filtering. Valid time is
  explicitly distinct from what ADA knew/stored on the selected date.
- B: user note or read-only exact owned user-source selection, annotation/kind/time
  form, preview and explicit Save. UTF-16 selections convert to code points without
  normalizing evidence. Model/unknown source trust cannot support user writes.
  Immutable source/claim IDs and input are encrypted before POST; the returned
  note version commits before the claim step. Failed/uncertain outcomes and 409/422
  retain input for original-ID checking or identical replay. Local recovery discard
  is explicit and never deletes remote evidence; failed cleanup blocks a new write.
- C: correction previews old/new value, effective time and new evidence, validates
  boundaries and calls the existing atomic supersede API. Current/history/detail
  refresh without changing original chat citation snapshots. Explicit identical
  replay also handles a committed claim subsequently corrected by another client.
  Source edits/deletion and optional retrieval search were not added.
- D: Settings exposes name plus all existing style/warmth/detail enums; creates
  a new owned profile for new conversations. Verified selected profiles survive
  first-page refresh without altering server page order. Profile drafts survive
  rotation in ViewModel memory; ambiguous unkeyed creation requires review. Existing
  conversation personality/prompt snapshots and supported explicit upgrade remain
  intact. Active saved style/detail and scope are visible in chat; appearance stays local.

Data/contracts: additive encrypted local record v2 reads v1 chat recovery with the
same file/key/AAD; maximum plaintext is 128 KiB for bounded concurrent chat/memory
journals. Verified token rotation retains both; logout/server/account/401 clears
both. No automatic memory POST on restore. No migration/API/OpenAPI/server/prompt
or dependency change: **31/31** captured source/migration/contract/lock/catalog files
remain byte-identical to the Phase 07 starting tree.

Checks actually run:

- Baseline ordinary pytest: **87 passed/69 skipped**, existing Starlette/httpx warning.
  Android unit/lint/debug tasks succeeded, with cached tasks explicitly up-to-date.
  Ruff lint/format passed for **48 files** at baseline and final review.
- Test-first gates: fixed memory error recognition **1 expected failure**; encrypted
  journal invariants **9 expected failures** before expansion. Focused contract/HTTP
  **26 passed**; focused storage **22 passed**. Later regression checks failed first
  for corrected-after-commit replay, late same-session 401 and off-page profile
  selection, then were fixed. Existing conversation-creation fixture now supplies
  an owned selectable profile to exercise the stricter selection invariant.
- Final `testDebugUnitTest lintDebug assembleDebug assembleRelease
  assembleDebugAndroidTest`: **98 unit tests, 0 failures/skips**, lint **0 errors/14
  existing dependency availability warnings**, debug, unsigned release and test
  APK builds passed. Repeated after the emulator-found selection fix. A transient
  Windows `R.jar` lock was resolved by stopping Gradle/rebuilding; no check was suppressed.
- Dedicated `scripts/test-postgres.ps1`: **152 passed/4 skipped**, 41.08 seconds;
  two expected SQLite row-lock skips and two opt-in live-provider health skips.
  Existing Starlette/httpx deprecation is unchanged. Disposable migrated schemas;
  no application database migration or actual account grant.
- APK inspection: versionCode 3/name 0.7.0-memory, target SDK 36, backup/cleartext
  disabled in release, no release HTTP domain exceptions; debug permits only the
  three documented loopback/emulator hosts. PowerShell emulator script parses.
- Initial emulator suite: **19 passed/2 failed**, zero skips. It exposed focus-loss
  collapsing the selected quote before preview and an IME/navigation test race.
  Preview now captures the reservation before clearing focus; the test explicitly
  checks the selected span. The profile test waits for keyboard/nav restoration.
  Final `scripts/verify-emulator.ps1`: **21/21 passed, 0 skips**, followed by **2
  existing chat + 2 new memory force-stop stages passed**. Memory stages commit a
  real note, explicitly simulate failure before claim POST, force-stop the process,
  restore through production MainActivity/Keystore and explicitly resume the same
  source/claim IDs and exact payload. One note/claim remains; no automatic restore
  POST, duplicate or rewritten citation. Long Unicode evidence and correction
  validation focus were exercised through the restored real-HTTP UI. Debug cold
  launch succeeded. Emulator reports **Android 17/API 37**, WHPX, **480×320 dp
  landscape** (640×960 override, density 320, rotation 1), system font **1.5×**.
  Four new Compose tests use explicit synthetic API/storage fixtures; four new
  memory integration tests use real authenticated ADA HTTP and migrated SQLite.
  Real HTTP checks include same-ID replay/mismatch/duplicate, denied source/claim
  guesses, exact Unicode, model-source rejection, future history, boundary-at-end
  correction, frozen personality and original fake-chat citations.
- Markdown/link review at this checkpoint: **43 files/55 local links**, all resolve.

Final machine evidence recorded **2026-10-09 22:30:46 UTC**: temporary app-private
test credential absent, disposable HTTP listener stopped; display/font settings
reset and the task-started emulator shut down. Release APK is unsigned and local.
Final documentation/encoding review: **43 Markdown files/59 local links** resolve;
**79 combined Phase 05/06/07 changed/new text files** decode as UTF-8 without NUL.
Repository-configured `git diff --check` passed; later phase files are unchanged.

Remaining target verification: Samsung S24 FE/Android 16 is not attached; physical
installation, TalkBack/hardware keyboard/display settings, release trusted HTTPS,
API 26 runtime behavior, actual ADA/Ollama generation/source quality and real
network loss remain pending.
Emulator HTTP uses a migrated disposable SQLite database and explicit FakeProvider;
synthetic Compose/storage fixtures are separate from real HTTP. No claim of target
phone, real-model, release distribution or production deployment verification.
Web tests were not rerun because this phase changes no admin web behavior. No later
phase, upload, extraction, affect/relationship learning, tool or deployment was implemented.

## Phase 06 verification details — 2026-10-09 UTC

Code: base `b828192` plus the preserved Phase 05/user-edited Phase 06 working tree
and this Phase 06 change. Current source, exported OpenAPI, head 0004, scoped
instructions and existing tests met the Phase 03/05 prerequisites. The added theme
checkpoint was implemented alongside A–D. Earlier evidence below is historical.

- 0: Oxford Blue #002147 is default; Dark Red #350616 and Olive Green #3c4c24 are
  selectable in Settings. Each supports light/dark/system and larger text. Only
  enum appearance preferences persist; storage-disabled users can still change
  appearance in the current tab. The Android app was unchanged.
- A: admin-me verifies operator UUID/current monitoring permission. Bearer input
  clears on submission; token stays solely in the live adapter. `/admin` routing
  includes direct owner/request detail. Server/principal/epoch/filter/composite
  identity keys, aborts/cache clear and late-result fences cover logout/switch and
  401/403. A denied detail is removed, and normal private APIs remain owner-only.
- B: overview/providers display actual creation-window counts, token coverage,
  database/schema/admission and measured health with units/last-success times.
  Zero/unknown/unavailable/degraded are distinct. Transient failures retain stale
  values. Mounted views poll every 30 seconds while visible, pause hidden polling
  and refresh, and honor Retry-After across navigation/sign-in/manual reads.
  No synthetic time series, GPU percentage, throughput or generation health poll.
- C: requests use server pagination/filter/sort with bounded UTC windows, reset
  and safe detail/back state. Details show recorded attempt/timeline/tokens/fixed
  error/retrieval counts and byte budgets; missing legacy values are Not recorded.
  Selected memories are labelled separately from unavailable citation counts.
  Runtime projection excludes additive private fields before caching; int64 times
  remain bigint. No private retrieval endpoint, chat/prompt/quote UI or fallback.
- D: safe provider/limit configuration and fixed-field audit are read-only.
  Native labels, table captions/headers and keyboard-scroll regions, skip link,
  stable refresh focus and responsive layouts support keyboard/zoom. No shell,
  retry/cancel/purge/token rotation/prompt editing or later operational control.

Checks actually run:

- Baseline: ordinary pytest **80 passed/69 skipped**, Ruff lint/format passed
  (46 files). Web exported DTO check/typecheck/lint/build passed; **28 unit** and
  **3 Chromium** foundation tests passed. These precede the implementation.
- Clean `npm ci`: **270 locked packages**, audit **0 vulnerabilities**; unchanged
  package lock/pins. `contracts:check`, typecheck/lint, **43 interim unit tests** and
  production build passed. Final review then added two regression checks for exact
  millisecond filter reapplication and read-only error wording; both failed before
  correction. Final typecheck/lint, **45 unit tests** and build passed. Unit tests
  cover projection/int64/composite identity,
  fresh/late revoked authorization, account/server cleanup, filters/back state,
  legacy traces, unknown/zero/escaped data, appearance and polling/Retry-After.
- Development-browser interim: **4/4 Chromium tests passed**, real one-worker ADA
  HTTP/migrated disposable PostgreSQL schema. Final production-build smoke via
  `ADA_WEB_BUILD_SMOKE=1 npm run test:e2e`: **5/5 passed**, 14.2 seconds initially,
  then **5/5**, 14.3 seconds after the final field/error/health-type refinements. Preview
  served built `/admin` assets/route fallback plus a fixed same-origin `/v1` proxy.
  Actual grants/ordinary rejection/local revocation, two owners sharing UUID,
  pagination, known/legacy details, failed request, audit and session refresh ran
  through real HTTP/DB. Successful seed chats used FakeProvider. Failed request
  and health used actual local TCP refusal to a non-listening bound socket.
  Intercepted 401/429/503 and unknown/degraded model tags are explicit UI fixtures;
  they do not establish real provider success or authorization.
- Browser keyboard skip link/form feedback/main focus/table traversal passed.
  390px and 200% CSS-zoom layout checks passed; polling/refresh focus stays stable.
  All three palettes × light/dark semantic text/muted/button pairs met 4.5:1 and
  boundary/focus pairs met 3:1. System media and appearance reload passed. Three
  signed-out appearance captures were visually inspected (wide blue/light and
  red/dark, narrow olive/light). No credentialed screenshots/traces/video were
  captured. Automated semantics/contrast/zoom are not manual screen-reader review.
- Final ordinary pytest: **87 passed/69 skipped**, 20.15 seconds. Seven new fixture
  guards verify dedicated DB/schema/search-path safety; their targeted run was
  **7 passed**. Dedicated `scripts/test-postgres.ps1`: **152 passed/4 skipped**,
  44.21 seconds; two expected SQLite lock exclusions and two opt-in live Ollama
  health cases. Separate opt-in non-generating local Ollama checks then passed
  **2 tests/27 deselected**, on SQLite/PostgreSQL. No live model generation ran.
  The full dedicated suite includes actual HTTP/CLI grant/revoke, schema/upgrade,
  replay/ownership and monitoring concurrency/failure/metadata tests.
- Ruff lint/format passed for **48 files**. Existing Starlette/httpx deprecation,
  npm whatwg-encoding notice and Playwright NO_COLOR notices remain separate from
  failures. No dependency was upgraded to suppress them.
- Corrected interim failures: test mock literal types and an ambiguous unknown
  label; the helper initially resolved .env from the web directory and failed DB
  authentication (fixed root resolution with sanitized failures); a browser audit
  assertion selected a hidden filter option (scoped to table cell); production
  contrast parsing omitted minified 3-digit hex (fixed); a development escaping
  assertion matched Vite's own script (scoped to rendered main). Date filters now
  preserve milliseconds and monitoring errors describe reads; a malformed health
  state cannot pass runtime decoding as a string. All final checks above
  passed; no assertion or required check was suppressed.

Final review/cleanup at **2026-10-09 20:13:52 UTC**: the exact-millisecond
reapplication check passed in both final development (**5/5**, 15.4 s) and built
preview (**5/5**, 14.6 s) browser runs. A subsequent measured Oxford Blue input
border adjustment raised background contrast from **2.9601:1 to 3.1998:1**.
Final typecheck/lint/build and **5/5 production-build tests** passed (**14.5 s**),
including input-background boundary checks for all six palette/mode combinations.
SHA-256 matched all **10** captured server/OpenAPI/migration/Python-lock baseline
files; the web lock was unchanged. UTF-8/NUL/relative-link/whitespace checks passed
across the combined preserved Phase 05 + Phase 06 working tree: **53 files**,
**53 links in 14 documents**. All task HTTP/preview listeners stopped and no
disposable browser/suite schemas remained in the dedicated test DB.

Skipped/remaining target verification: manual screen-reader and full keyboard/
assistive review, Firefox/Edge/other browsers, real HTTPS hosting, sustained
polling/audit load, production-sized metadata and offline target-network recovery.
The intended application DB still needs the separately requested Phase 05 install/
real UUID grant. No such migration/grant or deployment ran. Android/device checks
were skipped because Android was unchanged; prior S24 FE/Android 16/HTTPS limits
remain historical. Fixtures are synthetic, not real-model latency/GPU evidence.
The local build preview is not a deployed release. Stop at Phase 06; later phases
and operational write controls remain separately selected work.

## Phase 05 verification details — 2026-10-09 UTC

Code: clean base `b828192` plus the Phase 05 working tree. Phase 03 prerequisites
were present. No later phase, dashboard workflow, production migration or real
account grant was performed. Earlier validation evidence below remains historical.

- A: migration 0004 follows unchanged released 0001–0003. Existing/new accounts
  have no implicit grant. Local UUID CLI grant/revoke and fixed-field audits commit
  atomically. Every monitoring read checks current grants; successful reads recheck
  and audit before delivery. Revocation during a probe blocks its result. Normal
  private user endpoints remain owner-only. Local operator actor IDs/limits are
  documented in [ADMIN-MONITORING.md](../docs/ADMIN-MONITORING.md).
- B: all six typed admin GET routes are exported. Filters, windows, pagination,
  audit retention and polling are bounded. Responses preserve composite identity,
  UTC/int64 timestamps/durations, null versus zero metrics and unavailable legacy
  summaries. SQL selects metadata and JSON scalar lengths/budget keys; no private
  message, answer, prompt, evidence, username, digest or configuration secret is
  selected into monitoring DTOs. Representative bodies/SQL/logs were checked.
- C: supported-head readiness is 0004 and tested against Alembic. Provider probes
  use cached/bounded model-list metadata outside transactions, with no generation.
  Bare model tags correctly normalize to latest. Process admission reads the real
  semaphore; GPU/throughput stay unknown. Admin responses prohibit HTTP caching.
  Existing 21 paths and 31 schemas were compared to the baseline: only the additive
  `admin_monitoring` property changes an existing schema. Prompt/input/replay behavior
  and released migration SHA-256 values are unchanged. No dependency pin changed;
  FastAPI's minimum is 0.121 for pre-response dependency scope (locked 0.142.4).

Checks actually run:

- Baseline `pytest -q`: 65 passed/53 skipped; dedicated PostgreSQL/SQLite baseline:
  116 passed/2 expected SQLite lock skips. Ruff lint/format were clean for 39 files.
- Final ordinary `pytest -q`: 80 passed/69 skipped. Skips are unavailable PostgreSQL
  copies, SQLite-only lock exclusions and the opt-in real-health case. Dedicated
  `.\scripts\test-postgres.ps1` with process-local `ADA_TEST_OLLAMA_HEALTH=1`:
  **147 passed/2 expected SQLite lock skips**, 38.06 seconds. This executed populated
  0001/0003-to-head upgrade and Alembic drift checks, ownership/replay/prompt cases,
  grants/revokes, concurrent grant serialization, actual indexed PostgreSQL queries,
  aggregation, retention, rate limits, missing metrics/traces and failure tests.
  After the last bare-model-tag refinement, the affected cached/failure and real
  Ollama probe cases were rerun on both databases: **4 passed/25 deselected**.
- Actual socket/CLI tests on SQLite and PostgreSQL started/stopped one-worker
  loopback Uvicorn with the fake model, used actual CLI subprocess grants/revokes,
  read cross-owner metadata and verified normal private 404s/immediate revocation.
  Operational output was scanned for synthetic body, token and digest leakage.
  Real local Ollama GET-only metadata health also passed on both databases; ADA
  request counts stayed unchanged. No real generation or GPU/throughput test ran.
- Final Ruff lint and format: passed, **46 files**. OpenAPI export, compatibility
  comparison and unchanged released migration hashes passed. `git diff --check`
  passed. Final UTF-8/NUL checks covered 29 changed/new files; local links passed
  for 13 Markdown documents. Cleanup was rechecked at 2026-10-09 10:01:10 UTC.
  Dedicated database is PostgreSQL **17.11** on this Windows host; temporary
  test/evaluation schemas were confirmed cleaned up. Default test warning remains
  the existing Starlette/httpx deprecation; no packages were upgraded to hide it.
- Retrieval evaluations ran against disposable SQLite and PostgreSQL: recall@5
  0.8667 on both, MRR@5 0.8667/0.8333, exact evidence coverage 1.0, zero scope
  violations/negative-query failures. Reports are ignored local `.pytest_cache`
  artifacts; synthetic timings are not production/model performance evidence.
- Web generated DTOs were synchronized. `npm ci` (270 locked packages, audit zero
  vulnerabilities), contracts generation/check, typecheck, lint, 28 unit tests,
  build and 3 Chromium tests passed. The actual HTTP foundation used migrated
  disposable SQLite/FakeProvider; the browser dashboard remains unimplemented.
  Final DTO regeneration/typecheck/lint passed after the int64 elapsed-field
  refinement. Existing encoding/color notices remain non-failing.

Skips/remaining target verification: application database backup/install/migration
0004 and deliberate real-account grant are installation steps, not performed in
this no-deployment task. Private remote HTTPS, sustained polling/audit contention,
real inference/citation/GPU/latency and operational backup/retention measurements
remain unperformed. Standalone legacy `smoke_upgrade.py` was not run (requires an
old Phase 1 checkout); populated upgrade/replay tests and new actual HTTP/CLI
tests ran instead. Android/device checks were skipped because no Android source
changed; prior S24 FE/Android 16 and release/accessibility gates remain historical.
The first standalone PostgreSQL retrieval evaluation lacked its test URL; it was
rerun successfully with the dedicated test database supplied only inside Python.

Phase 05 stops here. A separately requested Phase 06 may implement the dashboard.

## Phase 03 verification details — 2026-10-08

Code: base `6a6a278` plus the Phase 03 working tree. No schema migration, prompt
upgrade, authentication change, request-fingerprint change or Python dependency
update is required. Released migrations 0001–0003 and server bind/worker settings
are unchanged. Earlier validation evidence above and in WORKLOG remains historical.

- Server: Python 3.12.10; full dedicated Windows PostgreSQL/SQLite pytest suite
  114 passed, 2 expected SQLite-only row-lock skips, 1 existing Starlette/httpx
  deprecation warning. After the final additive-trace preservation refinement,
  the affected contract suite passed all 5 SQLite/PostgreSQL cases. Ruff lint and
  format passed for 38 files; scoped final contract Ruff also passed. Actual HTTP
  responses match exported OpenAPI; schema/migration, replay, owner isolation,
  Unicode, snapshot, source/correction and failure checks are included.
- Android: JDK 21.0.12.1+1, Gradle 8.13, AGP 8.11.1, Kotlin 2.2.21, Compose BOM
  2025.10.00, compile/target SDK 36/minimum 26. Fifteen unit tests passed; lint
  had 0 errors/14 dependency availability notices; debug and unsigned release
  builds passed. Three instrumented tests passed with no failures/skips on the
  installed Android 17/API 37 emulator, including real authenticated HTTP,
  rejected credentials and connection/theme controls; debug cold launch passed.
  The final helper run also passed in landscape with 1.5× system font scaling;
  device settings and caller environment variables were restored afterward.
  Release resources were inspected to confirm no debug cleartext exceptions.
  A final unit/lint/debug/release command passed without rewriting dependency
  locks; the test helper and session-created headless emulator were stopped.
- Web: Node 24.12.0/npm 11.6.2; clean install (270 locked packages, audit 0
  vulnerabilities), generated-contract check, typecheck, lint, 28 unit tests,
  production build and 3 Chromium tests passed. Playwright 1.64.0 used Chromium
  156.0.8078.4. Browser checks cover keyboard focus, narrow/dark/large text,
  escaped fixture text, sanitized failure and actual HTTP authentication. The
  credential-free desktop and narrow design screenshots were visually reviewed.
  Existing transitive encoding deprecation and terminal color notices did not
  fail checks. Test/browser servers were stopped.

Both client HTTP integration flows used the actual ADA application with migrated
disposable SQLite, an ephemeral synthetic account and FakeProvider; they did not
exercise the user's production data or request a real Ollama generation. The
server suite separately executed real PostgreSQL fixtures. See app READMEs for
exact Windows commands, primary compatibility references and initial failures
corrected during scaffolding.

Remaining target verification: Samsung S24 FE/Android 16 physical-phone install
and actual-server/USB or chosen private remote connection; verified release HTTPS;
TalkBack/manual screen-reader, keyboard, display/zoom and long-content checks on
target devices/browsers. Android encrypted storage/enrollment/journaling and chat
belong to Phase 04; admin authorization/monitoring belong to Phases 05/06. Real
Ollama citation quality, GPU placement and latency retain their earlier limits.

## Android appearance follow-up — 2026-10-08

User-selected scope: Android themes only, on base `6a6a278` plus the Phase 03
working tree. Settings → Appearance now offers Oxford Blue (`#002147`, default),
Dark Red (`#350616`) and Olive Green (`#3C4C24`), each with light/dark semantic
colors. Changes apply immediately; only the palette key and dark-mode boolean
are saved as device-local appearance preferences. Unknown palette keys fall back
to Oxford Blue. Credentials remain memory-only; server contracts, migrations,
prompt history, dependency locks and later-phase behavior are unchanged by this follow-up.

- Baseline Python: `pytest -q` passed 64 tests, skipped 52 database-dependent/
  SQLite-lock cases, with 1 existing Starlette/httpx warning. Ruff lint and format
  checks passed for 38 files. This is separate from the prior PostgreSQL evidence.
- Android baseline passed. Final `testDebugUnitTest lintDebug assembleDebug
  assembleRelease --console=plain` passed: 15 unit tests, 0 failures/skips,
  lint 0 errors/14 existing dependency notices, debug and unsigned release builds.
- Android 17/API 37 emulator: complete helper run passed 3 instrumented tests,
  0 failures/skips, plus debug cold launch. The final appearance-only smoke passed
  at 23:59:20 UTC in landscape with 1.5× system text, exercising all six
  palette/mode combinations and preference reload after activity recreation.
  Device font/rotation settings were restored. Text/outline contrast calculations
  passed 4.5:1/3:1 thresholds for the checked semantic pairs; see Android README.

Skipped for this appearance-only change: dedicated PostgreSQL fixtures and web
checks (no server/schema/concurrency or web changes), physical S24 FE/Android 16,
manual TalkBack/keyboard/visual/IME review, release HTTPS and real-model checks.
Target-phone appearance/accessibility verification remains pending. The disposable
HTTP helper and session-created emulator were stopped. No later phase or deployment
was performed; earlier validation evidence remains historical.

## Phase 04 verification details — 2026-10-09 UTC

Code: base `6a6a278` plus the preserved Phase 03/theme working tree and Phase 04
changes. Current source/OpenAPI, migrations and tests met the prerequisites;
all required HTTP routes already existed. No server API, capabilities, provider,
request fingerprint, prompt snapshot or schema change was needed. SHA-256 checks
of eight server/OpenAPI/released-migration files matched the Phase 04 baseline.
Dependencies and wrappers remain pinned; no lock refresh or deployment occurred.

| Checkpoint | Implemented behavior | Local evidence |
| --- | --- | --- |
| A | Normalized authenticated Connect; `/me`/capabilities; encrypted token and exact journal; key-loss reconnect; logout/switch cleanup; explicit same-account token replacement; debug-only local HTTP | Transport/identity/storage unit invariants; 4 actual Keystore/AtomicFile emulator tests; authenticated and rejected HTTP; packaged backup/cleartext policy |
| B | Owned paginated profiles/scopes/conversations/events; create/resume; automatic personal-scope label; ambiguous creation review; server order/event deduplication; explicit prompt update | Ordered-page/creation/conflict invariants; explicit upgrade/no duplicate/immutable prior cards/style/history and rejected-upgrade feedback tests; real HTTP owned/personal creation, resume and event/source flow |
| C | UUID/options journal before POST; separate drafts/status/history; 4,000 code points; bounded GET recovery; explicit exact retries; no silent POST replay; memory/historical controls | 28 ViewModel invariants and 12 transport tests; response-delivery loss after actual commit; double Send/navigation/recreation; two instrumentation stages separated by adb force-stop |
| D | Selectable literal text/code; explicit safe HTTP(S) links; matching original request cards; exact quotes/provenance/validity/Details; unavailable labels/legacy trace; separate retrieval details | Contract/legacy/source invariants; real HTTP original Unicode source quote, historical reload and unknown-label UI; unsafe markup/link instrumentation |

- Baseline in this phase: Android 15 unit tests/lint/debug build passed; Python
  `pytest -q` 64 passed/52 skipped, one existing Starlette/httpx warning; Ruff lint
  and format passed for 38 files. The skips reflected unprovisioned PostgreSQL
  and SQLite-only lock variants at that baseline, not the final database run.
- Server after the explicit disposable Android fixture helper/test: full
  `scripts/test-postgres.ps1` passed 116 tests, skipped only the two expected
  SQLite row-lock variants, with the existing warning. Ruff lint and format
  passed for 39 files. No production database or model was exercised.
- Android final `testDebugUnitTest lintDebug assembleDebug assembleRelease
  --console=plain` passed 57 unit tests, no failures/skips; lint 0 errors and
  14 existing dependency availability notices. Debug and unsigned release
  `0.4.0-chat-mvp` APKs built. Release resource inspection confirmed HTTPS-only
  cleartext policy, disabled backup and complete transfer/backup exclusions;
  debug retained only its three local HTTP hosts.
- Android 17/API 37 emulator: the complete helper passed 11 ordinary tests and
  two separate committed-reply recovery stages with an actual adb force-stop,
  then cold launch. The final small landscape run used density 540 on the
  1080×2400 emulator (smallest width 320dp), rotation 1 and font scale 1.5;
  all 11 + 2 passed without skips. Font/density/rotation were restored.
  The final restored normal-layout run at 2026-10-09 09:04:54 UTC passed all
  11 ordinary tests plus both force-stop stages and cold launch without skips.
  HTTP used the real migrated ADA application with an ephemeral synthetic owner,
  explicit known evidence and a deterministic FakeProvider. Response-delivery
  loss was simulated after a real server commit; process death was real.
- Corrected failures remain part of this phase's evidence: unavailable public
  directory-open constant; one invalid test import; initial 8/10 passing UI run
  with two layout/assertion failures; a 6/11 smaller-layout run exposed keyboard
  viewport and lazy-scroll gaps, followed by 9/11 and 10/11 runs while correcting
  IME/composition assertions. The final 11/11 + 2 stages passed. The OkHttp
  immediate-503 POST replay regression failed before the one-shot-body fix and
  passed afterward. A normal-layout rerun initially passed 10/11 because navigation
  raced IME dismissal; an explicit dismissal/wait corrected that test. Two
  prompt-update notice regressions failed before preserving feedback after refresh
  and passed in the final 57-test suite. No assertion, lint failure or required
  test was suppressed.

Remaining target verification: no physical device was attached. The user's
Samsung S24 FE/Android 16 still needs install/connect/list/create/resume/send,
actual network interruption/recovery, token rotation/logout and source inspection
through the real server. Verified release HTTPS, a manual real-Ollama conversation
with known memory, TalkBack, hardware-keyboard traversal, visual/IME/selection
review and API 26 behavior remain pending. Automated labels/focus/large-text and
scrolling are not a manual accessibility review. Web checks were skipped because
the web app and default helper behavior were unchanged. This is an implemented,
locally checked chat MVP, not a target-verified or distributed release.

Stop at Phase 04. Memory editing, streaming, cancellation, voice, tools, admin
authorization/monitoring and device inference remain later selected work.
Final cleanup verified that the temporary credential and synthetic encrypted
session/journal were removed, the disposable HTTP listener stopped, emulator
font/density/rotation restored and the session-created emulator shut down.
## Phase 08 carryover verification, checked during Phase 09

The preceding 120-unit build evidence remains historical. Before Phase 09 edits,
the final late Phase 08 artifact contained 121 passing unit cases; the fresh
baseline build used that cached unit task. Earlier Phase 08 emulator evidence was
24 ordinary passes, four chat/memory force-stop stages and document preparation;
document resume failed on an off-screen control. The late SAF identity/draft fence
and detail-toggle refinements had compiled but had no final emulator rerun.

Phase 09's final regression run executes those existing production flows on app
code 5: 25 ordinary tests, followed by two chat, two memory, two document and two
entity force-stop stages, all passing. It closes the outstanding automated
document/source recovery check on the current tree. The original failures and
120-unit evidence are retained rather than relabeled as a previous successful run.
Physical-phone/manual/HTTPS/model limits below still apply.

## Phase 09 verification details — 2026-10-10 UTC

Code: `1ca228a` plus the preserved uncommitted Phase 08 tree and this phase's
changes. Root/scoped instructions, requested documents, actual source/OpenAPI,
schema/test state and Phase 03/current Phase 2 prerequisites were inspected first.
The requested Android editor already had its client prerequisite. No later phase,
dependency upgrade, automatic extraction or deployment was implemented.

Checkpoint results:

- Data/API: migration 0006 and owner/scope composite references, nullable explicit
  claim mapping, retained alias/self/link/merge history, exact operation receipts
  and private audit. Name collisions remain allowed. Explicit self never comes
  from names, kinds, personalities or model output. Quotas and failed/stale writes
  are atomic; PostgreSQL opposite merges serialize without a redirect cycle.
- Resolution/retrieval: exact NFKC/case/whitespace with preserved raw labels,
  absent/resolved/ambiguous states and validated explicit candidate selection.
  Alias candidates precede ranking, all ambiguous linked roots are excluded before
  context and truncated matches fail closed. Historical mapping/rename/merge/undo,
  failed retry and completed replay preserve exact old evidence and interpretations.
  Old string-only claims and omitted-reference write hashes survive populated upgrade.
- Android: Memory opens a capability-gated picker/editor with duplicate warning
  and reviewed alias/rename/self/link/merge/undo. Exact encrypted journal v4 retains
  v1–v3 recovery within 256 KiB. Saved-operation check, identical resume, storage and
  receipt failure, duplicate taps, cooldown and late owner/scope/401 fences passed.
  Source cards and ambiguous alternatives use request-frozen metadata. App is
  `0.9.0-entities`, code 5, minimum API 26/target 36; no provider/database bypass.
- Contracts/docs: exported OpenAPI/generated web types and current capability
  gates, identity policy, architecture/current state and decisions updated.
  Prompts remain v4/current and v3/claims; no new prompt or automatic upgrade.

Checks actually run:

- Fresh ordinary backend baseline: **137 passed/114 skipped**, 121.99 s. Initial
  PostgreSQL command could not connect; no tests ran. Starting the existing local
  Docker database allowed the baseline **244 passed/7 skipped**, 198.07 s.
  Baseline Ruff lint/format passed (58 files). Android baseline build/lint passed,
  with the 121-unit task cached; it is not a new 121-case execution.
- Full changed ordinary `pytest -q`: **150 passed/129 skipped**, 185.74 s. Full
  `scripts/test-postgres.ps1`: **271 passed/8 skipped**, 304.92 s. Two subsequent
  history/truncation tests were then executed in the final affected suite with
  entity/storage/history/corpus/document-upgrade cases: **35 passed/1 skipped**,
  47.21 s on SQLite and dedicated PostgreSQL. The single skip needs PostgreSQL
  scope locks; it passed on PostgreSQL. The eight full-suite skips are six SQLite
  lock/concurrency exclusions and two opt-in provider-health cases. The existing
  Starlette/httpx deprecation warning remains; no required assertion was disabled.
- Ruff lint and `format --check`: **112 files passed**. Populated 0005→0006 upgrade,
  native foreign-key rejection, lossy downgrade refusal, restored head/check and
  old hashes/replay passed. Offline PostgreSQL 0005→0006 SQL compiled successfully.
- Explicit alias corpus: **11/11 cases passed on each database**, zero false
  resolutions, isolation violations or exact-evidence failures. Synthetic explicit
  aliases include case/compatibility/combining forms, same-name people, foreign
  scopes/owners, explicit self, accents/scripts and approximate-spelling negatives.
  This measures deterministic identity behavior, not factual/model/production quality.
- Android final `testDebugUnitTest lintDebug assembleDebug assembleRelease
  assembleDebugAndroidTest`: **134 unit cases passed, zero skips**, lint zero errors/
  14 existing dependency notices; debug, unsigned release and test APKs built.
  Release APK metadata confirms code 5, version name, minimum 26 and target 36.
  `verify-emulator.ps1` final: **25 ordinary passes/zero skips**, then **8 actual
  force-stop stages passed** and a successful cold launch. Android 17/API 37/WHPX,
  small 480×320 dp landscape, 1.5× text; explicit FakeProvider/disposable SQLite
  HTTP exercises actual owner validation and production Compose/Keystore flows.
- Web contract generation/freshness, typecheck, lint, **51 unit cases**, production
  build and **6 production-build Chromium cases** passed (25.4 s browser run),
  including real disposable PostgreSQL auth/grants and safe readiness guidance.
  The generated types are the only Phase 09 web runtime-source change; earlier
  Phase 08 sign-in fixes were preserved. Clean pinned installation is recorded
  with the final checks below; no web deployment or credentialed recording.
- Read-only Phase 09 compatibility comparison preserved **34 old paths, all old
  operations and 48 schemas**: parameters, security, request/response references,
  required fields and existing property shapes are unchanged. Additions are
  optional in six schemas, with 13 new paths. **76 protected file hashes** matched
  the phase starting tree, including migrations 0001–0005, old fixtures, prompts,
  dependency locks/wrappers and later phase files. `git diff --check` passed;
  repository autocrlf notices are retained as platform notices.

Failures and corrections: API invariants initially failed on missing routes;
optional-reference code caught and fixed a missing DB argument. Alias candidates
were red before expansion. An old document downgrade assertion needed to restore
an already reversed empty 0006 before checking the independently protected 0005.
Android test-interface/syntax/constructor compile errors were fixed, then unit and
build checks passed. Initial emulator run was 23 passed/2 failed on a lazy-row
scroll and a partial-text assertion. The full rerun passed 25; document recovery
later reached an off-screen D quote and failed. Explicit list scrolling was fixed,
and the final full run passed all ordinary and recovery checks. Synthetic history
tests corrected an admin route and required the test provider to emit a citation.
Read-only operator check quoting/schema-name/case assumptions were corrected; they
performed no database mutation. These intermediate failures are not counted as passes.

Remaining target verification: application **0006 installation**; physical Samsung
S24 FE/Android 16 install/connect/edit/canonical-source/ambiguity/recovery/logout/
token checks, trusted release HTTPS, API 26, TalkBack, hardware keyboard and manual
visual/IME accessibility. Real Ollama with known explicit aliases/evidence and
actual-server network loss remains unverified. Browser HTTPS/manual accessibility/
other browsers, production load and operational backup/restore remain pending.
No physical phone was installed, launched or changed. Final read-only application
state was head **0005** and one active grant for the selected account; no Phase 09
application migration or role change was made. Disposable schemas were removed;
test-helper and emulator cleanup is recorded below. Histories have retained quotas
and no automatic cleanup/delete service. Stop at Phase 09; later phases remain planned.

Final refinement/cleanup — **2026-10-10 10:08:59 UTC**: encrypted entity input
validation additionally rejects null characters before reservation. The final
134-unit/lint/debug/unsigned-release/test-APK build passed, followed by focused
real-HTTP entity UI **1 passed** and **all eight force-stop stages passed again**.
The full 25-case emulator pass above remains separate evidence. Pinned clean web
install added 270 packages with zero audit vulnerabilities; post-install contract,
typecheck, lint and production build passed. Final expanded compatibility checks
matched **85 protected hashes**, including prior Phase 08 document implementation,
and checked **57 changed UTF-8/NUL/Markdown-link files** successfully. An extra
autocrlf-disabled diff invocation misclassified CRLF as whitespace; the repository-
configured whitespace check passed without rewriting files.

Read-only cleanup verification: application head 0005, selected account grant
active, zero disposable PostgreSQL schemas, temporary test credential and encrypted
journals absent, fixture listeners stopped. Emulator font/display reset and the
task-launched emulator stopped. The local compose DB was restored to its initially
stopped state, retaining application/test data and grants. No application upgrade,
physical-phone action, external message, later phase or deployment occurred.

## Phase 10 verification details — 2026-10-10 UTC

Code: clean base **13a0cb3** plus this Phase 10 working tree. Required/root/plan
instructions, current source/OpenAPI/migration history and tests were inspected
first. Phase 08 documents and Phase 09 identities were present; the initial source
head was 0006. Existing server/client contracts, released history and previous
validation evidence were preserved. No later phase or deployment was implemented.

Checkpoint results:

- Provider: interface and server-only bounded HTTP adapter over the existing
  locked httpx/Ollama runtime. Selected `embeddinggemma:300m`, 768 dimensions by
  default, verified full official manifest digest and search-prefix/index version.
  Exact count/model/dimension/digest, finite nonzero vectors, no input truncation,
  input/batch/response/time bounds and shared generation admission are enforced.
  No new dependency, lockfile or wrapper. The selected model is absent locally.
- Index: migration **0007** adds only discardable composite owner/scope/item/source
  references, exact hashes and digest/dimension namespace metadata. Explicit owned
  rebuild reuses valid entries, embeds outside transactions and rechecks the full
  bounded history snapshot under a scope lock before atomic publication. Partial
  failure/correction races preserve the prior index and all original history.
- Retrieval: exact authorized cosine ranking with 256-item/conservative-content
  bounds; time, document availability, source integrity and entity ambiguity gates
  precede scoring. Lexical-first RRF60 merges channels while preserving conflict
  groups and whole-prompt budgets. Missing/stale/drifting/provider/busy/bound cases
  fall back to the original baseline without fabricated scores. New semantic and
  channel metadata freezes with request context; failed/completed replay does not
  re-embed or search a newer index. v3/v4 prompts and fingerprints are unchanged.
- Evaluation/exit: 13 synthetic mixed questions and explicit fixture vectors,
  plus 256-item/768-dimension capacity/failure checks on both databases. No ANN or
  pgvector was selected. **Semantic retrieval remains disabled by default.**
  Fixture benefit does not establish real-model relevance/resource quality; the
  selected phase explicitly allows a documented disabled exit. See
  [the policy and installation route](../docs/EMBEDDINGS-AND-HYBRID-RETRIEVAL.md).

Checks actually run:

- Ordinary unchanged baseline `pytest -q`: **152 passed/131 skipped**, 215.88 s.
  Existing compose PostgreSQL was initially stopped; it was started for dedicated
  fixtures. Unchanged PostgreSQL/SQLite baseline: **275 passed/8 skipped**,
  333.52 s, excluding the two newly written Phase 10 test modules. Baseline Ruff
  lint/format passed for **67 files**. No production schema was used by fixtures.
- New provider invariants were red before implementation (missing module).
  Intermediate focused runs: 21 passed/4 failed, then 23 passed/2 failed; bounds
  and evaluation-fixture issues were corrected. An affected suite then passed
  **32 tests**, 64.22 s. Full changed ordinary run: **171 passed/143 skipped/1
  failed**, 258.16 s. The failure assumed a rejected older downgrade retained head;
  0007 can discard derived vectors before 0006 refuses to destroy identity history.
  Restoring head before Alembic check corrected that test without suppressing it.
- Full `.\scripts\test-postgres.ps1`: **307 passed/8 skipped**, 411.31 s.
  Subsequent refinements added strict zero-checked-out-connection embedding
  assertions, evaluation DB guard/stable tie ordering and original semantic M/D
  citation replay across document replacement. Final affected provider/retrieval/
  storage/evaluation/old-upgrade suite: **37 passed, zero skips**, 71.85 s on
  SQLite and dedicated PostgreSQL. Backend runtime was unchanged after the full
  run; these final changes are evaluation/tests. Full-suite skips are six SQLite
  lock/concurrency exclusions and two opt-in live-provider health cases.
- Populated upgrade/downgrade/re-upgrade, Alembic check, native scoped FK rejection,
  prior write/source hashes and frozen requests passed. Offline 0006→0007
  PostgreSQL SQL compiled with a fake connection URL; this is distinct from the
  migration execution above. Final Ruff lint/format: **76 files passed**.
  Compileall and repository-configured `git diff --check` passed.
- Final synthetic comparison on each database: lexical recall@5/MRR@5 **0.4286/
  0.4286**; explicit fixture hybrid **1.0/0.7857**, with **18/18 exact evidence
  checks**, zero isolation/integrity/negative failures and normal-run degraded
  fallback rate **0**. Dataset is entirely synthetic and vectors are five hand-built
  concept components; no real-model quality claim. Final hybrid median/max HTTP
  latency was SQLite **132.229/286.993 ms**, PostgreSQL **159.884/290.051 ms**,
  under Python allocation tracing. Synthetic timings are not production estimates.
  The standalone fixture/disabled CLI modes ran; disabled mode retained recall/MRR
  0.4286 and the same baseline selections. The unchanged original claim benchmark
  CLI retained recall/MRR **0.8667**, exact evidence **1.0**, zero isolation/negative
  failures. Its generated report was moved to ignored task artifacts.
- Final capacity: **256 items × 768 dimensions**, **32 batches of eight**; SQLite
  build/query **2374.736/2493.530 ms**, Python peak **10,096,858 bytes**; PostgreSQL
  **2498.062/2366.315 ms**, **9,206,837 bytes**. Item 257 caused lexical fallback and
  rejected rebuild. Provider vectors were explicit synthetic constants; tracing
  excludes database/GPU allocations and does not measure real embedding inference.
- Web `npm ci`: **270 packages**, audit **0 vulnerabilities**. Generated contracts/
  freshness, typecheck/lint, **51 unit tests**, production build and **6 actual
  PostgreSQL-backed Chromium cases** passed (21.9 s). Final timestamp metadata
  regeneration/freshness/typecheck passed. Only generated web DTOs changed.
- Compatibility: **47 old paths and 63 old schemas** preserve existing operations,
  parameters/security/responses, required fields and old property shapes. New
  fields are optional in four schemas, with one new owned path. **276 protected
  hashes** matched, including migrations 0001–0006, prompts, fixtures, locks,
  wrappers, Android source and later phase files. UTF-8/NUL/link review passed;
  final record/cleanup checks below include the completed status/work log.
- Local inspection: Ollama **0.40.1**, i9-14900HX, **31.62 GiB RAM**, RTX 4090 Laptop
  GPU **16,376 MiB**, observed **552 MiB** used. Official registry layers total
  **621,875,501 bytes**, not measured resident model memory. The selected model
  was absent; a real bounded adapter probe returned sanitized
  `embedding_model_changed` before inference. No model was downloaded/generated.

Failures/skips/target verification: initial tests and fixture/schema assumptions
above were corrected, not counted as passes. One read-only inline probe command
had shell quoting failure; the saved helper ran successfully. A formatting check
caught the benchmark refinement and passed after formatting. Patch context
mismatches performed no writes and were corrected. The existing Starlette/httpx,
npm encoding and Playwright color notices remain. Standalone legacy smoke upgrade,
ANN/pgvector, Android build/emulator/phone and real-model inference were not run:
legacy replay is covered by migrated fixtures, exact search needs no extension,
Android is byte-identical, and the embedding model is absent. No new mobile control.

Remaining targets: application **0007 installation** (final observed head **0005**,
selected grant active and unchanged); actual selected-model load/CPU/GPU memory,
latency/threshold calibration and comparative relevance on representative authorized
ADA evidence before activation; sustained load and operational install/backup
checks. Earlier physical S24 FE/Android 16/HTTPS/manual accessibility limits remain
historical. No application migration, role/token change, physical-phone action,
later phase, external message or deployment occurred. Stop at Phase 10.

Final record/cleanup — **2026-10-10 18:59:16 UTC**: all **276 protected hashes**
still match; **35 changed/new UTF-8/NUL files**, **14 Markdown documents/68 local
links**, Ruff lint/format (76 files) and normal whitespace checks passed. Read-only
application check confirmed head 0005 and the selected grant unchanged; **zero
disposable schemas** and no fixture/API/preview listener remained at the inspected
task ports. The compose database was restored to its initially stopped state,
preserving volumes/data/grants. No application install, embedding activation,
model download, phone change, later phase or deployment occurred.

## Phase 11 verification details — 2026-10-10 UTC

Code: **13a0cb3** plus the preserved uncommitted Phase 10 baseline and this Phase
11 working tree. Required root/plan/scoped instructions, actual source, OpenAPI,
migration/test state and prerequisites were inspected before implementation.
Phases 07/08/09 are present; source initially required 0007, configured application
was observed at 0005. No application upgrade, grant/token change or deployment.

Checkpoint implementation:

- Strict owned selected-source extraction is bounded and shares chat admission;
  inference has no checked-out DB connection. Exact source/version/hash/spans are
  checked before inference and before atomic batch publication. Unknown fields,
  fabricated/foreign evidence, duplicate keys, nonfinite values and model-selected
  canonical links fail safely. Pending proposals never enter factual retrieval.
- Migration **0008** adds extraction/proposal/review/support ledgers and nullable
  provenance; migrations 0001–0007, original evidence and prompts are preserved.
  Edits retain the original model candidate, revision history and exact support.
  Review hash binds candidate, conflicts and canonical mapping under a scope lock.
- Explicit acceptance creates separate immutable user endorsement evidence and
  original support mappings. Principal/review key/revision/hash are bound to the
  receipt. Specific half-open correction and all mappings commit atomically;
  repeated identical review returns the original receipt. Reject creates no claim.
  Optional review-v1/user_reviewed provenance preserves old origin enums, old
  clients and frozen historical cards. Fresh retrieval verifies support integrity.
- Android implements owned inbox/detail/exact excerpts, edits/new preview,
  annotation and explicit accept/reject confirmation. Existing Keystore no-backup
  persistence advances to v5 with one unsent draft and one exact operation, old
  versions readable, verified identity and no automatic submission on restore.
  Admin overview exposes only windowed state counts through a closed decoder.
  No dependency, wrapper, lockfile, chat prompt or automatic extraction change.

Checks actually run so far:

- Unchanged ordinary baseline `pytest -q`: **174 passed/144 skipped**, 268.39 s.
  PostgreSQL was initially stopped and absent from that command's fixture env.
  Unchanged dedicated PostgreSQL/SQLite baseline: **310 passed/8 skipped**,
  432.35 s. Ruff lint/format passed for **76 files**. Android baseline unit/lint/
  debug build succeeded with cached tasks; this is not a fresh 134-test execution.
- New approval test failed before service wiring (missing state.proposals).
  Android journal compilation failed before the required storage methods existed.
  First affected backend run: 8 passed/2 failed/12 skipped; UTC Z versus +00:00
  canonicalization was fixed. Subsequent affected checks: **21 passed/1 skip**,
  24.41 s; **29 passed/1 skip**, 39.43 s; **59 passed/1 skip**, 72.21 s.
- Full changed `scripts/test-postgres.ps1`: **349 passed/9 skipped**, 559.23 s.
  Final added admin privacy, all-or-nothing publication, publication-time source
  tamper and scoped FK invariants are covered by the subsequent affected run:
  **45 passed/1 skip**, 57.96 s. These late tests were added after full collection;
  do not infer a later full-suite count. Full skips are seven SQLite lock/race
  exclusions and two opt-in live-provider health checks. Real PostgreSQL fixtures
  exercised concurrent review, native scoped foreign keys, rollback, populated
  0007→0008 upgrade, empty downgrade/re-upgrade, Alembic check and refusal to
  downgrade populated review history. Original completed replay/hashes passed.
- Offline PostgreSQL **0007→0008 SQL** compiled with a fake URL separately from
  real fixture migration execution. Compileall and Ruff lint/format passed for
  **87 files**; normal repository whitespace check passed. Existing Windows CRLF
  notices and Starlette/httpx deprecation are recorded separately from failures.
- Web `npm ci`: **270 packages**, audit zero vulnerabilities. Contract generation/
  freshness, typecheck, lint, **52 unit tests**, production build and **six actual
  migrated PostgreSQL/HTTP production-build Chromium cases passed**, 23.7 s.
  Counts privacy/legacy decoder behavior is tested without a private review UI.
- Initial changed Android build found a job-completion type mismatch, fixed.
  The next unit run had 136 tests/two old storage-version expectation failures;
  v5 and real v3 test conversion were corrected. The subsequent build passed
  **143 unit cases**, lint zero errors/14 warnings, debug and test APK assembly
  (2 m 3 s). Timestamp/partial-draft refinements have two further tests awaiting
  the final unit gate. An intermediate command attempted compilation before its
  new timestamp helper was defined; the helper was immediately added.
- First full emulator run: **20 passed/6 failed**, 26 ordinary tests, 5 m 16 s.
  Five older chat/document/entity cases failed and the new proposal test asserted
  text on its container rather than its text child. The assertion was corrected.
  Second full run: **20 passed/6 failed**, 5 m 8 s; the proposal case now reaches
  the empty-claims HTTP check but fails along with the older flows. Focused
  diagnostics and final recovery verification are still in progress. These runs
  are failures, not device passes; staged recovery did not run after suite failure.

Extraction evaluation:

The committed eight-case corpus is entirely synthetic, with five positive cases
across explicit/imported/generated sources, Unicode and decisions, and three
instruction/question/ambiguous-identity negatives. Gold fixture execution on
SQLite and dedicated PostgreSQL produced **5 proposals/5 exact evidence matches/
5 explicit endorsements**, precision/recall 1 (tautological fixture result).
First two-case real Ollama probe produced two exact-supported proposals with
strict-string precision/recall zero and no endorsements (before the independent
review edit was added). The full real **qwen3.8:27b** eight-case run produced
**4 proposals, 4 exact support matches, 0 extraction failures, 4 explicit review
edits and 4 endorsements**. It abstained on the tentative generated case and all
three negatives. Strict subject/predicate/value/kind gold-string precision and
recall were both **0** because the returned annotations used different field wording. Reports
remain ignored; no private ADA evidence or source quotes appear in these records.
Exact evidence is not entailment, truth or representative model quality. A
simulated reviewer independently supplies the corpus's final annotation; the
model cannot approve itself. Independent manual/representative quality remains.

Verification still pending: final Android unit/lint/build/emulator/recovery,
complete compatibility/record/cleanup audit; application **0008 installation**
(observed head 0005), physical **Samsung S24 FE/Android 16**, release HTTPS/manual
TalkBack/keyboard accessibility and representative real-model quality/load. No
standalone old-checkout smoke, release signing/installation, ANN extension or
semantic activation was run; populated migrated fixtures cover old replay,
release deployment is unauthorized and exact/disabled Phase 10 is preserved.
No later phase, external message, private-phone action or deployment. Stop at 11.

Phase 11 final refinements/checks (verification continues): strict boolean
confidence/numeric-date coercion tests were red (**2 failed**) before validation
was tightened. A subsequent affected run passed **55/1 skip**, 74.32 s. The new
PostgreSQL concurrent edit-versus-review case passed (**1/1 SQLite skip**, 0.87 s),
with only the winning revision/decision persisted. Cross-owner nonce reuse was
red (**1 failed/1 PostgreSQL-not-configured skip**): derived endorsement/claim IDs
collided. Namespace derivation now includes the authenticated owner for proposal,
endorsement, claim and identity-history IDs. Final affected proposals/extraction/
corpus/schema/client-contract run: **58 passed/2 expected SQLite race skips**,
74.35 s on SQLite and actual PostgreSQL. These are later checks than the full
349-test run; no larger full count is inferred. Lint/format remains 87 files.

Emulator investigation: a focused proposal case failed with a transport
Unreachable result (1 failed, 1 m 12 s); loopback checked the same synthetic empty
claims response as HTTP 200/zero rows in 15 ms. Extending the disposable helper's
five-second idle connection lifetime to **90 seconds** allowed the explicit
real-HTTP edit/accept/reject flow to pass (**1 ordinary test**, 4 m 17 s), followed
by **all ten force-stop recovery stages** without skips. Production adapter
redirect/POST-retry behavior is unchanged. Temporary diagnostics printed only
safe failure classes, were removed, and the three older diagnostic test files
were restored byte-for-byte. Short-idle/HTTPS behavior on the actual phone/server
remains a target check. The separate launch command reported **Status timeout**
despite exit zero; it is not a launch pass. The script now force-stops for cold
launch and requires **Status ok**, not just an exit code.

Final Android unit/lint/debug/test-APK gate passed: **145 unit tests, zero
failures/skips**, lint **0 errors/14 existing warnings**, build **1 m 29 s**.
Includes v4→v5 encrypted partial draft recovery preserving entity state, malformed
Unicode rejection, exact UTC edit reconciliation and safe unknown provenance
labels. The full 26-case ordinary emulator suite and strict launch/recovery gate
are running against the finished source. Read-only app check still showed 0005/
active selected grant unchanged; zero disposable PostgreSQL schemas. Complete
compatibility audit: **48 original paths/65 schemas** preserve prior operations,
security, required fields and property definitions; **271 other baseline hashes**
match, including all old migrations/prompts/locks/wrappers/fixtures/later phases.
**62 changed/new UTF-8/NUL files, 13 Markdown documents/78 local links** passed.
Final record/cleanup follows; no later phase or deployment.

Final publication quota invariant: two concurrent extractions can reserve below
400 before either finishes. The PostgreSQL regression was red (1 failed/1 SQLite
skip, 1.02 s). Publication now rechecks the exact staged batch plus retained rows
under the scope lock, failing the losing batch with zero partial proposals and a
replayable failure receipt. Final affected proposal/extraction/corpus/schema/client
suite: **59 passed/3 expected SQLite concurrency skips**, 78.86 s. The real
PostgreSQL race retained exactly 400 proposals and zero unreviewed claims. This
supersedes 58/2 for the final backend runtime; the earlier full 349/9 run remains
historical evidence. The already-running emulator helper loaded before this last
quota-only guard; its ordinary single-extraction scopes do not hit that guard.
The guard itself ran against actual PostgreSQL. No server contract changed.

Final ordinary Android emulator suite against the finished client source:
**26 passed, zero failures/skips**, build/test command completed in **21 m 46 s**.
This includes the real-HTTP proposal edit/accept/reject flow and existing chat,
memory, document and entity regressions. The ten separate force-stop stages and
strict cold launch continue after this ordinary-suite pass; their final outcome
is recorded below when available. This is the Android 17 emulator, not the
physical Samsung S24 FE/Android 16. The helper uses synthetic extraction and
90-second idle keep-alive; no real-model or release-HTTPS device pass is inferred.

Phase 11 close-out before the separately requested Phase 12: **all ten actual
force-stop stages passed**, including exact review-key/original receipt recovery
with one endorsement/claim. The subsequent strict cold-launch check **failed**;
the complete emulator script exited **1**, so this is not an all-gates pass. On
follow-up the task emulator was no longer available; no successful retry is
claimed. Physical S24 FE/Android 16, cold launch, short-idle/HTTPS/manual
accessibility and independent representative quality remain target checks.
Final lint/format (87 files), compileall, whitespace, old 48 paths/65 schemas,
271 protected baseline hashes and 62 UTF-8 files/78 local links passed. The last
read-only application check remained 0005 with the selected grant unchanged and
zero disposable PostgreSQL schemas. Migration 0008 was not installed. Phase 11
code stopped here; Phase 12 is a new explicit scope, not inferred authorization.

Resource close-out observation: no task emulator or disposable HTTP helper port
was present on follow-up. A physical device was detected and was not operated.
PostgreSQL had been restarted externally and remains running; no shutdown or
application migration was performed. Automatic approval review rejected removal
of the five task-created synthetic helper directories as blocked by policy;
they remain in Windows Temp. No cleanup success is claimed for those directories
or for the unavailable emulator's display settings.

## Phase 12 baseline and first checkpoint — 2026-10-11 UTC

Scope: only the separately selected read-only tools and bounded agent loop.
Required/root/plan/client instructions, actual source and prerequisite Phase
03/04/06 APIs/clients were inspected first. The preserved working tree contains
Phase 10/11 work on HEAD 13a0cb3. All **333 baseline files** were hashed; actual
source/exported OpenAPI matched (**55 paths/76 schemas**). Application remains
observed 0005 with unchanged selected grant and zero disposable schemas.

Unchanged dedicated PostgreSQL/SQLite baseline: **361 passed/11 skips**, 179.90 s;
skips cover SQLite concurrency variants and opt-in provider probes. Ruff
lint/format passed across **87 files**. Android baseline unit/lint/debug build:
**18 s**, 53 tasks/9 executed/44 up-to-date; unit and lint tasks were cached,
so this is not a new 145-test execution. Web baseline contract freshness,
typecheck and **52 unit tests** passed, 7.56 s. No dependency upgrade.

Test-first checks were red: missing calculator module (**1 failed**, 0.13 s),
missing agent service (**1 failed**, 0.52 s). Separate calculator/native adapter
checks subsequently passed **2 tests**, 0.04 s. First owned HTTP
proposal→approval→tool receipt→answer/replay passed on SQLite (**3 passed/1
unconfigured PostgreSQL skip**, 0.56 s including calculator/provider cases).
Lease-expiry regression was red (**1 failed**, 0.65 s): late model output became
a pending proposal after its lease expired. Publication now fences expired leases
and records unknown/interrupted rather than accepting late output. The affected
agent/calculator/native protocol/schema suite subsequently passed on SQLite and
real PostgreSQL: **17 passed**, 5.57 s. Broader phase verification remains.

Selected registry is calculator, memory_lookup and source_lookup only. Every tool
proposal requires exact actor/version/argument/preview approval. Agent mode has
its own explicit ada-agent-v1 protocol and frozen context; normal chat/v3/v4
prompts, fingerprints, snapshots and completed replay remain separate. Migration
0009 is additive and not installed in the application. No external write,
unselected integration, later phase or deployment is included. Machine evidence
uses UTC (local user date is 2026-10-10, America/Phoenix).


## Phase 12 expanded verification — 2026-10-11 UTC

After the baseline/first checkpoint above, actual PostgreSQL and SQLite server
checks expanded through **27 passed/1 expected SQLite concurrency skip**, 11.23 s;
owned memory/source/injection/budget subset **12 passed**, 5.72 s; provider privacy
and strict native protocol **8 passed**, 0.03 s; failure/monitoring subset **17
passed**, 7.61 s; current affected suite **71 passed/7 skips**, 35.21 s. Its skips
are one SQLite copy of the PostgreSQL-only concurrent reservation test and six
opt-in real-model cases. Real probes were run separately, not counted as fake
provider evidence. An earlier subset had two fixture-unpack failures (46 passed)
and one new failure-test import/collection error; both fixtures were corrected.

The first full regression was **423 passed/12 skips/1 failure**, 328.00 s: a
SQLite downgrade crossed empty agent tables before the existing 0008 review
guard refused. A new red preflight case reproduced it (**1 failed/1 unconfigured
PostgreSQL skip**, 0.77 s). Migration 0009 now checks the deeper guard before DDL;
0008 remains unchanged. Populated upgrade/downgrade/preflight rerun **6 passed**,
5.49 s. The next full dedicated suite passed **430 tests/18 skips**, 267.11 s;
subsequent new HTTP/OpenAPI checks passed **2 tests**, 1.03 s.

Native installed **qwen3.8:27b**, synthetic disposable PostgreSQL and explicit
test approvals: **3 passed/3 deliberate SQLite skips**, 148.37 s. Calculator,
owned memory and exact source each recorded an owned durable completed receipt
and completed final answer; elapsed **38.91/53.28/53.17 s**, respectively. Updated
memory omission metadata rerun: **1 passed/1 SQLite skip/4 deselected**, 56.14 s,
memory flow **54.95 s**. No source quotes/private transcripts/credentials are
recorded here. This small local functional probe is not sustained throughput,
GPU-placement or comprehensive adversarial quality evidence. No model download
or semantic activation occurred.

Android new main sources compiled; initial journal-version assumptions caused
two unit failures out of 145. The tests now validate v6 and unknown-version
destruction. Unit/lint/debug/test-APK gate passed **23 s**, then **35 s** after
the terminal-preview recovery refinement. Actual tool UI over disposable HTTP
passed on **Medium_Phone_API_37.0 / Android 17**, followed by **two real force-stop
stages** restoring the original approval receipt by GET, and strict cold launch
`Status: ok`. The same focused UI/stages/launch passed at **900×500 pixels,
240 dpi, 1.5× text**. The first two staging-script attempts failed because Gradle
uninstalled the APKs; the script now explicitly reinstalls both and reprovisions
the app-private ephemeral fixture credential. Those attempts are not recovery
passes. The attached physical Samsung was not operated; Android 16 remains a
separate target. Prior Phase 11 cold-launch failure remains historical evidence;
the current Phase 12 app's new launch passed.

Web clean **npm ci** (270 packages, zero reported vulnerabilities), fresh contract
generation/check, typecheck, lint, **53 unit tests** and production build passed.
Actual migrated PostgreSQL/Chromium integration: **6 passed**, 22.8 s, including
keyboard, palettes, narrow/zoom and authorization/revocation/reconnect checks.
Known whatwg-encoding, Node color and Starlette/httpx warnings remain separate
from failures; pinned dependencies/wrappers/lockfiles are unchanged.

Final review found imported exact lookup needed the existing half-open document
availability interval, in addition to publication time. Its red tests were
**2 failures/1 pass/3 unconfigured PostgreSQL skips**, 1.60 s; the actual
PostgreSQL/SQLite source suite then passed **18 tests**, 9.66 s. A separate red
tampered-source approval case (**1 failure/1 unconfigured PostgreSQL skip**,
0.62 s) led to terminal rejection without execution/receipt. The final full
regression is running against these last source guards; results follow below.

Fresh exported contract: **63 paths/85 schemas**. Original **55 paths/76 schemas**
retain exact routes, required fields and prior property definitions. All **333
baseline files** remain; changed files are confined to the phase. Core plain
chat/prompt/provider/model code, released migrations, later plans and pinned
dependencies are unchanged. Ruff lint/format across **103 files**, compileall
and source/export comparison passed. No configured application migration or
deployment was performed. Remaining close-out: final regression, documentation
links/whitespace, resource checks and explicitly pending physical/HTTPS/manual
accessibility/resource verification.

## Phase 12 final close-out — 2026-10-11 03:10 UTC

Code: **13a0cb3 + this preserved working tree**, Android versionCode **7** /
**0.12.0-tools**. Only Phase 12 implemented; prerequisite 03/04/06 behavior was
inspected, existing Phase 10/11 changes retained, later plan files unchanged.

Final full `scripts/test-postgres.ps1`: **440 passed/18 skips**, **223.69 s**.
SQLite and actual PostgreSQL 17 both ran; concurrency/schema cases used real
PostgreSQL. Skips remain SQLite-only concurrency variants and opt-in real-provider
probes; real read-only agent probes ran separately as recorded above. Historical
chat/CLI, populated migrations, snapshots/replay, permission/time/source trust,
native protocol, limits, provider/capacity failure, receipt rollback and lease
fencing are covered. No successful result was fabricated for a rejected,
expired/revoked, failed or unknown operation. Imported availability and changed
pin guards are included in this final run. Exact schema/native receipt/owner
HTTP cases are included as well.

Final Android `testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest`
passed **47 s**, 80 tasks/16 executed/64 up-to-date. JUnit XML confirms **155
passed/zero failures/errors/skips**, 20 suites; lint **zero errors/fatal, 14 existing
warnings**. After displaying the exact frozen time in the approval preview,
focused `connectedDebugAndroidTest` passed again on the task-owned Android 17
emulator in compact landscape/1.5× text (**23 s** Gradle gate), plus both separate
actual force-stop recovery stages and strict cold launch `Status: ok`.
The earlier normal-portrait and compact-layout successes remain separate evidence.
This is the focused Phase 12 flow, not a fresh run of all earlier instrumented
scenarios. No physical phone or release installation was performed.

Final Ruff lint/format: **103 Python files** clean; compileall clean. Actual source
and exported OpenAPI match (**63 paths/85 schemas**); all **55 original paths/76
original schemas** retain routes, required fields and prior properties. The
**333-file** baseline/scope audit preserves core chat/prompt/provider/model code,
all released migrations, dependencies/wrappers and all later phase files.
Markdown UTF-8/local-link review: **12 changed/new files, 81 links** valid;
`git diff --check` clean. Clean web installation, 53 units/type/lint/build and six
real PostgreSQL Chromium tests remain the final web evidence; no web code changed
after those runs. Real qwen3.8:27b evidence remains the separate measured probe
above, not inferred from fixtures.

Selected external-write checkpoint: **not applicable**—only the explicitly
documented read-only registry was selected. There is no shell/browser/email,
external effect, implicit model approval, scheduled worker, new normal-chat
prompt or later-phase implementation. Production controls call actual owned
routes; fixture agent behavior exists only in the disposable test helper.

Read-only resource close-out confirmed application **0005**, unchanged active
selected grant, **zero disposable PostgreSQL schemas**, and **zero disposable
HTTP listeners**. Emulator size/density/font/rotation were reset and the owned
emulator-5556 was stopped; the physical device was not operated. Externally running
PostgreSQL remains running. The five earlier Windows Temp helper directories
remain after automatic approval review rejected removal as **blocked by policy**.
Five additional stopped Phase 12 disposable-helper directories remain in Temp;
removal was not retried or claimed. They contain synthetic test databases, not
application data. This is a documented cleanup skip, not a functional gate pass.

Remaining target verification: explicitly back up/upgrade the intended application
from observed 0005 to head **0009**; test the user's **Samsung S24 FE / Android 16**,
release HTTPS/network transitions, manual TalkBack/screen reader/keyboard review,
release build/signing and sustained model latency/resource/concurrent load and
broader tool/prompt-injection quality. Prior Phase 10 real embedding activation
remains disabled/pending. No deployment or application migration is claimed.
Source checkpoint exits here; a later phase requires a new user selection.


## Phase 13 baseline and implementation boundary — 2026-10-11 08:35 UTC

Code: **13a0cb3 + preserved working tree**, local date 2026-10-11 America/Phoenix.
Required/root/plan/client guidance, current source/OpenAPI and actual prerequisite
08/11 behavior were inspected first. The Phase 12 tree has **359 captured files**
and **63 paths/85 schemas**. Prior validation evidence remains historical.

Unchanged dedicated PostgreSQL/SQLite baseline: **440 passed/18 skipped**,
**219.11 s**, existing Starlette/httpx warning. Baseline Ruff lint/format:
**103 files** clean. Android baseline unit/lint/debug gate: **11 s**, 53 tasks,
1 executed/52 up-to-date; units/lint were cached, not freshly rerun. Web baseline
typecheck and **53 unit tests** passed (**7.37 s**). No dependency upgrades.

Selected scope: exact source-linked generated episodes; explicit durable episode,
proposal and lexical rebuild jobs; one bounded in-process worker using existing
admission; fenced short publication transactions; private navigation snapshots;
Android history/job recovery and admin metadata only. Ordinary chat and old prompts,
claim retrieval, valid-time history and completed replay remain independent.
New migration **0010** is only validated on disposable databases, not installed
in the configured application. No later phase or deployment is authorized.

Initial invariants were red before implementation: missing consolidation service
(**1 failure**, 0.65 s), Android encrypted journal methods/types missing
(`compileDebugUnitTestKotlin` failed). A JSON-null/SQL-null receipt constraint
caused **2 failures/1 skip**, then fixed. Initial SQLite flow: **6 passed/6
PostgreSQL-not-configured skips**, 3.04 s. Expanded PostgreSQL subset:
**45 passed/3 SQLite concurrency skips/2 failures**, 26.70 s; deeper downgrade
preflight wording was aligned with preserved review-history checks. Later expanded
subset: **54 passed/1 SQLite concurrency skip/2 failures**, 28.93 s; its synthetic
future-document fixture attempted the ordinary user/model source route, which
correctly hides imported versions. The fixture now reads the exact test DB version
for that negative authorization/time case. Final verification is in progress.

Remaining gates: expanded crash/concurrency/publication checks, full regression,
summary faithfulness/omission corpus and real job lifecycle, client HTTP/emulator/
Chromium flows, compatibility/docs/resource audits. Physical S24 FE/Android 16,
release HTTPS/accessibility/load and application installation remain target checks.

## Phase 13 completed implementation and local verification — 2026-10-11 UTC

Code: base `13a0cb3c63b09571d2fcdcf43084b80d4b1e34fb` plus the preserved working
tree. This phase's 359-file baseline distinguishes earlier uncommitted Phases
10–12 work from new changes. Phases 08/11 prerequisites were verified against
actual source, OpenAPI and fresh existing tests. Phase 10 remains optional/off.

Implemented: static migration **0010** adds four owner/scope-constrained tables;
exact generated episodes and source/event/version maps; explicit summary,
pending-proposal and scoped lexical-rebuild jobs; lease/checkpoint/attempt/fenced
atomic receipts and a bounded lifespan worker sharing existing admission. Model
inference runs outside transactions. Policy/source changes become stale; invalid
or partially valid batches remain unpublished. Pending proposals require separate
Phase 11 review. No deletion, automatic approval, valid-time rewrite or external
effect exists. Private bounded navigation snapshots preserve original mappings;
episodes never enter normal chat or factual retrieval. Android **0.13.0-episodes**,
versionCode **8**, adds explicit history/source previews, measured job states and
Keystore journal **v7** (v1–v6 readable), with GET-only restore/exact retry. Admin
shows counts/newest-25 IDs, checkpoints and measured times only. Oxford Blue,
Dark Red and Olive Green remain unchanged. See the Phase 13 policy and DECISIONS.

Actual final checks:

- `scripts/test-postgres.ps1`: **516 passed/19 skipped**, **291.26 s**, actual
  dedicated PostgreSQL 17 and migrated SQLite. Covers concurrency/native scoped
  foreign keys, populated 0009→0010 upgrade/Alembic check, old chat replay,
  duplicate keys, capacity, lease expiry/stale fencing, crash before/after commit,
  shutdown during generation, lower-history downgrade preflight, source/policy/
  time changes, full prompt/source bounds, generated maps and no endorsement
  without explicit review. Skips: **11 SQLite row-lock variants** whose PostgreSQL
  counterparts run; **6 opt-in prior Phase 12 native-tool probes** and **2 opt-in
  generation-free Ollama-health variants** not requested for this phase. Existing
  Starlette/httpx deprecation warning persists; no package upgrade was made.
- Ruff lint/format clean across **115 Python files**. `compileall` passed.
  OpenAPI export/generation succeeded: **69 paths/94 schemas**. A comparison to
  the saved Phase 13 baseline preserves all **63 old paths**, **85 old schema
  required/property shapes and metadata**. Earlier migration files 0001–0009,
  dependency locks/wrappers, normal chat/provider/prompt/retrieval/source code and
  earlier/later phase files remain byte-identical to that baseline. `git diff
  --check` passed (Windows CRLF notices only).
- Android `testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest`:
  final build **13 s**, 80 tasks (19 executed/61 up-to-date); XML confirms
  **164 tests, 0 failures, 0 skips**. Lint **0 errors/14 existing dependency-version
  advisories**. Unit checks include durable-before-POST, duplicate tap, exact
  Unicode code points, lost delivery, session fencing, encrypted v7 restart,
  genuine v6 upgrade, startup navigation during journal restoration and local
  discard without a server write. No lock, wrapper, SDK or dependency upgrade.
- Task-owned **emulator-5556 / API 37 / Android 17**: actual loopback HTTP summary
  preview/submission, generated labeling/exact original version, no endorsed
  claims and prior tool approval/denial regression. Staged lost queue response,
  actual `am force-stop`, restart GET of the original job with one episode/attempt,
  and strict `am start -S -W` **Status ok** passed. Current compact configuration
  **900×500 px / 240 dpi / font scale 1.5** passed two HTTP UI tests plus two recovery
  stages; standard portrait evidence is recorded below. This is explicit fixture
  inference in disposable migrated SQLite, not a phone/native-model UI claim.
- Web `npm ci --ignore-scripts` (270 packages, 0 reported vulnerabilities),
  contracts generation/check, typecheck, lint, **54 unit tests** (**27.56 s**) and
  production build passed. Production-preview Chromium against migrated dedicated
  PostgreSQL: **six cases passed**, first **20.3 s**, final expanded run **20.1 s**.
  Metadata states/missing times, five accessible columns, keyboard table focus,
  390-pixel layout/200% zoom, old metadata, grant revocation and privacy were
  verified. Credentials stayed ephemeral; traces/screenshots/videos remained off.
- Synthetic corpus `episode-summary-v1`: actual bounded-worker fixture run on
  SQLite/PostgreSQL plus native **qwen3.8:27b / Ollama** on disposable PostgreSQL.
  All **four native cases completed at attempt 1** (33,159 / 38,368 / 37,403 /
  35,617 ms); **five exact version/hash/code-point support checks**, **13/13 lexical
  markers**, **zero endorsed claims**. Manual review preserved tentative status,
  both disagreement attributions, untrusted imported instructions and generated
  uncertainty; no unsupported resolution or user-preference promotion observed.
  Declared omissions were inspectable. Marker coverage and this small public
  synthetic corpus do not prove truth, entailment or representative quality.

Corrected intermediate evidence (retained rather than relabeled as passes):
**88 passed/4 skipped/3 failed**, 50.70 s exposed a missing synthetic-fixture import
and an old test's hardcoded head 0009; the head check now uses SCHEMA_HEAD and
preserves stricter downgrade preflight. **161 passed/7 SQLite concurrency skips**,
80.31 s followed. An inferred-interval partial-batch invariant was red (1 failed,
22 deselected, 0.67 s), then fixed before staging any proposal. Corpus/provider
run **13 passed/1 failed**, 15.59 s used an invalid global pool observer while
HTTP polling used another thread; the observer now measures the model's thread.
Surrogate-tag validation was red (1 failed, 24 deselected, 0.68 s), then Unicode
validation was added. The corrected corpus/provider/failure subset passed
**39 tests**, 22.45 s. The first real-evaluation helper start lacked the repository
import path; that helper was fixed before inference and the native run succeeded.

The initial full gate **506 passed/19 skipped/2 failed**, 310.63 s read a stale
OpenAPI export; export regenerated and both actual response/schema tests passed
(2 tests, 1.99 s), followed by the final full green run above. A newly added
lower-history SQLite downgrade case was red (1 failed, 0.71 s): imported sources
without upload receipts reached 0005's refusal after partial DDL. Only **0010**
was refined to preflight that existing guard. The next affected set was
**47 passed/1 skipped/4 failed**, 30.84 s: new size fixtures used a >4,000-character
note and expected an aggregate-byte error for a per-source failure. Fixtures now
use valid notes and aggregate Unicode bounds; their four cases passed (2.06 s)
and are included in the full final suite. New shutdown/preflight cases also pass.

Android intermediate build passed (69 s, then 22 s); an initial emulator case
expected a nonexistent trust label and failed, then passed with the actual trust.
Compact run first had **one UI failure/one passing prior tool regression** because
an offscreen LazyColumn node was not composed; the test now scrolls the container
to the node before interacting. Corrected compact UI/recovery/cold launch passed.
Startup-navigation journal restoration and post-discard selection each had a
focused red unit test, then were fixed. Intermediate full Android build passed
(16 s); the final 164-test build/current emulator evidence supersede these runs.

Skipped / remaining target verification: configured application installation of
head **0010** (read-only check still **0005**, selected admin grant active); physical
**Samsung S24 FE / Android 16** and minimum API 26 compatibility; release HTTPS,
short-idle reconnect and real-provider Android UI; manual TalkBack/screen-reader/
accessibility; sustained concurrent worker/model resource/lease/queue load and
broader representative summary quality. The entire old instrumented Android suite
was not freshly rerun: focused changed episode flows and tool-navigation regression
were selected. Release signing/distribution/deployment were not performed. Old
blocked Windows Temp cleanup evidence remains historical; it was not retried.
No application data migration, prompt upgrade, semantic activation, later phase
or external message was performed. Final task-owned resource audit follows below.

Final portrait/client/resource evidence — 2026-10-11 09:14 UTC (02:14 Phoenix):
current standard portrait passed **two HTTP UI tests plus two force-stop recovery
stages**, connected gate **20 s**, and strict cold launch **Status ok**. Current
compact gate was **21 s**, with the same four checks. Both runs include the
startup/discard fixes. Emulator settings were restored and the task-owned
emulator was stopped; test helper listeners on 18763/18764/5173 are absent.
Read-only application check: **head 0005**, selected admin grant **active**;
dedicated PostgreSQL disposable schemas **0**. The external PostgreSQL service
was left running. Final Ruff/compile/compatibility checks remain green.

Automatic approval review rejected recursive removal of **six new Phase 13
workspace fixture directories** under `.pytest_cache/client-fixtures` as **blocked
by policy**, despite absolute-path containment checks. They contain only disposable
synthetic fixture databases, remain in ignored workspace storage, and were not
removed or retried. Prior blocked Windows Temp resources were not touched.
No cleanup success is claimed for either set. Stop at Phase 13.

Final documentation audit — 2026-10-11 09:17 UTC: UTF-8/local links checked for
14 changed/new Markdown files, no issues. Repository-configured `git diff --check`
passed. An extra command disabling Git autocrlf interpreted existing Windows CRLF
as trailing whitespace and failed; no repository-wide newline rewrite was made.
The normal configured check remains green. Final web contract/type/lint checks
passed after the expanded browser assertions. Device inventory is empty after
stopping the owned emulator. Functional and compatibility gates above are final.


## Phase 14 — final implementation and local verification — 2026-10-11 20:38 UTC

Time displayed locally: 13:38 America/Phoenix. Base `4df9a72` with a clean initial
working tree; this working tree implements only Phase 14. Required/root/scoped
instructions, source, OpenAPI, migration history and test baseline were inspected
first. Phase 07 prerequisites are present; its target-phone checks remain distinct.

Implemented: migration **0011**, explicit owner-only account/scope/profile/
conversation preferences and precedence, immutable exact reviewed receipts,
frozen default inheritance/source receipt maps and an explicit future-reply
conversation update. Opt-in session tone has native integer ranges, one reviewed
signal per completed turn, +/-10 accepted changes, deterministic five-point decay,
30-minute idle/two-hour total expiry, clock-rollback guards and disable/reset.
Source request/binding/session checks reject stale/foreign signals; malformed
permission/truth/tool fields never write state. No normal model text is parsed into
state, automatic mood classifier or Phase 15 learning pipeline was added.

Expression-v1 uses a fixed 800-byte prompt allowance within existing budgets.
Saved v3/v4 system prompts, personality snapshots, factual filters/ranking, evidence,
tool policy and chat fingerprints remain unchanged. Failed/completed retries freeze
expression/messages/citations. Android 0.14.0-expression adds scoped Settings and
Keystore-encrypted exact journal v8 with v1–v7 compatibility and GET-only restore.
The admin app stays read-only/private-input-free. Architecture/policy/compatibility
and bounded storage decisions are documented; no new dependencies were added.

Checks actually run (earlier failures retained as history):

- Baseline: configured PostgreSQL helper failed because application port **5433**
  was unavailable. SQLite **290 passed/245 skipped**, **174.17 s**; Ruff lint/format
  clean, **115 files**. A task-owned PostgreSQL **18.6** instance on loopback port
  55414 and dedicated `ada_phase2_test` then ran the unmodified collected baseline
  (new invariant file explicitly excluded): **516 passed/19 skips**, **396.99 s**.
  New invariant first failed before API wiring: **1 failed/32 deselected**. Android
  baseline unit task was forced fresh; existing XML confirms 164 cases. Web baseline
  contract/type checks and **54 units** passed (**23.38 s**).
- First new backend gate **33 passed/1 SQLite concurrency skip**, **25.45 s**.
  Intermediate affected gate **84 passed/4 failed/3 skipped** (**75.36 s**): export
  needed regeneration, and a historical migration test queried the new nullable
  request column while deliberately downgraded. Replay is now checked after its
  populated upgrade. Expanded new tests initially **44 passed/2 failed/2 skips**
  (**33.77 s**) due to a missing test import, corrected. Initial Ruff one-line
  test/service style errors were formatted; no failing lint remains.
- Full changed PostgreSQL 18/SQLite suite: **562 passed/21 skipped**, **508.94 s**.
  Covers real populated migrations/Alembic check, native ownership/range constraints,
  CAS/in-flight concurrency, rollback, lease/review/proposal/tool history and old
  source/request/prompt replay. Skips: **13 SQLite locking variants** with executed
  PostgreSQL counterparts, **6 opt-in prior native-tool probes** and **2 opt-in
  Ollama health variants**. Existing Starlette/httpx deprecation remains.
- Subsequent final clock-rollback/provenance/actual HTTP-fixture refinements were
  checked with **74 passed/3 expected SQLite locking skips**, **76.71 s**. A prior
  final affected run was **72 passed/3 skips**, **72.51 s**, before the two clock
  cases. Do not infer a later full-suite count from these extra cases.
- Final Ruff lint/format **121 Python files** clean, compileall and normal Git
  whitespace check passed (ordinary Windows CRLF notices only). OpenAPI is
  **75 paths/105 schemas**; all **69 old path operations and 94 old schema required/
  property shapes** preserved, with three optional capabilities. Migration 0001–0010,
  locks/wrappers and saved personality prompt source hashes remain unchanged.
  **56 synthetic HTTP fixtures** include nine new expression cases. Current
  capabilities/readiness and manifest were refreshed; all 45 other earlier fixture
  bytes were restored, including their original Windows newlines. Fixture HTTP
  export was **1 passed/1 unavailable-PG skip**, not a PG fixture claim.
- Android first changed run: **164 cases/3 obsolete v7-expectation failures**.
  Next test compilation found a nonexistent fake base, corrected to the existing
  injected test-adapter pattern. Final XML: **174 tests/0 failures/0 skips**, lint
  **0 errors/14 existing dependency advisories**, debug/test APK builds passed;
  reviewed gate **19 s**, **80 tasks, 17 executed/63 up-to-date**. v7/v6 ciphertext,
  identity rotation/switch, save-before-POST, loss/restart GET-only receipt recovery,
  malformed fields, legacy capability/range decoding and late-result fencing pass.
- Actual emulator HTTP: **5 tests passed** (expression controls plus four existing
  Memory UI checks), **two force-stop stages** restored the original committed
  preference receipt, and strict cold launch **Status ok**. Initial portrait gate
  **51 s**, compact **900x500/240 dpi/1.5x text** gate **47 s**, final reviewed
  portrait gate **48 s**, all on Medium_Phone_API_37.0 / Android 17. Compact geometry
  was restored. The entire old instrumented suite was not freshly rerun.
- Web clean `npm ci` reported **0 vulnerabilities**; contract generation/freshness,
  typecheck, lint, **54 units** (**27.30 s**) and production build passed.
  Actual isolated PostgreSQL/HTTP production-build Chromium regression:
  **6 passed**, **22.8 s**. No private preference monitoring view was added.

Remaining targets/skips: explicitly backed-up intended application installation of
head **0011**. Its configured server remains unavailable (`OperationalError`);
**0005 is the earlier observation, not a fresh successful read in this phase**.
Existing PostgreSQL on port 5432 was untouched. Ollama metadata was unavailable
(`ConnectError`), so **no native inference/wording-quality run occurred**; fixture
checks establish protocol behavior, not model compliance or diagnosis accuracy.
Physical **Samsung S24 FE/Android 16**, minimum API 26, release HTTPS/short-idle/
network transitions, manual TalkBack/keyboard accessibility and representative
native-model wording/resource/load remain pending. Release build/signing/installation,
standalone old-checkout smoke and complete old instrumented-suite rerun were not
performed. Populated fixture replay supplies compatibility evidence.

No application migration, real account/role change, external message, classifier,
semantic activation, automatic approval/deletion, later phase or deployment.
Temporary data contain synthetic fixtures only; prior retained/blocked Phase 11–13
storage was not cleaned or retried. Final task-owned resource/link audit follows.


Final audit — 2026-10-11 20:43 UTC (13:43 Phoenix): 12 changed/new Markdown files
passed UTF-8/local-link checks; Ruff/format 121 files, normal whitespace, web
contract freshness/typecheck and protected history hashes passed. Restored legacy
fixture bytes were rechecked by the final Android unit/lint/debug gate (3 s;
53 tasks, 3 executed/50 up-to-date), XML still 174/0/0. Disposable schemas count
was zero. Task-owned PostgreSQL stopped successfully; emulator stopped and no
fixture HTTP/web/test-PostgreSQL listeners remained. The pre-existing PostgreSQL
service was untouched. New ignored synthetic validation artifacts remain retained;
no prior blocked cleanup was attempted. No local check failure remains. Stop at14.

## Phase 15 — implementation and local verification — 2026-10-11 21:56 UTC

Code: base `4df9a72` plus the existing uncommitted Phase 14 working tree and
Phase 15 additions. Required/root/scoped instructions, source, current OpenAPI,
migrations and tests were inspected first. Phases 11/13/14 exist in source;
their installation/physical-device gates were not treated as completed. The
pre-existing Phase 14 changes and validation evidence were preserved.

Implemented: additive **0012**, owner/scope/time/source/version/purpose-bound
InteractionObservations, confidence classes and configurable independent-evidence
threshold. Only explicitly selected completed user interactions are annotated;
there is no automatic extraction/classifier. Same-event retries, copied quotes,
notes/imports and generated summaries cannot manufacture independent observations.
Weak guesses expire and never count. Pending proposals never affect chat.

Opt-in/pause/view/approve/reject/edit/off/reset use native ownership constraints,
owner row locks, CAS revisions and durable same-key receipts. Approved lineage
freezes contributing observation IDs/revision and stays inspectable after expiry
or later evidence. Explicit account reuse carries wording enums/receipt IDs only;
both source/destination scopes must be enrolled. Reset removes live derived state,
stops new reuse and preserves minimal identifier audit. Immutable historical chat/
request snapshots and original sources remain for replay; reset is not complete
account erasure. No derived learning index/shared cache exists.

The independent 1,024-byte learning overlay preserves v3/v4 baselines, frozen
explicit expression settings and instruction precedence. Authorized episode
continuity selects bounded complete original excerpts, retains uncertainty,
omissions/original/generated trust and C citations, and never feeds generated
summary text as recollection. Factual retrieval receives its budget first.
Failed/completed retries retain selected policy/cards/messages after reset.
No automatic factual promotion, emotion diagnosis or exclusive-dependence rule.

Android **0.15.0-learning** adds capability-gated Settings consent, source/evidence,
review/edit/reject/account choice/pause/disable/reset and exact C source cards.
Keystore-encrypted **v9** journal preserves v1–v8 reads, saves exact mutations
before POST and restores receipts using GET only; identity/scope changes and 401
are fenced. Admin sees aggregate config/observe/review/reset counts only.

Checks actually run (earlier failures retained as history):

- Baseline Ruff lint/format **121 files**, Android **174 units** and web **54
  units** passed. PostgreSQL 18.6/SQLite baseline **563 passed/1 failed/21 skips**,
  **428.09 s**: the pre-existing hybrid evaluation fluctuated to recall 0.8571
  against 1.0 before Phase 15 wiring. Its unchanged focused rerun was **3 passed**,
  **4.23 s**; no benchmark fix or new Phase 15 failure is claimed.
- New consent invariant failed before wiring (**1 failed/1 unavailable-PG skip/
  6 deselected**). Initial learning gate **6 passed/2 failed** (nullable preference
  JSON expectations); first affected gate **75 passed/2 failed/3 skips** (old
  hardcoded schema head), corrected. Expanded learning **21 passed/1 SQLite
  locking skip**. First full changed run **578 passed/7 failed/22 skips**,
  **531.14 s** exposed a PostgreSQL JSON aggregate GROUP BY binding issue;
  grouping by the selected alias fixed it. Focused admin/agent gate **29 passed/
  2 skips**, **30.03 s**.
- Full changed PostgreSQL/SQLite regression: **587 passed/22 skipped**,
  **500.62 s**. Populated upgrades, guarded downgrade/upgrade/replay, Alembic
  schema/native constraints, locking/concurrency, authorization, source trust,
  prompt compatibility and prior feature regressions passed. Skips: **14 SQLite
  locking variants** with executed PostgreSQL counterparts, **6 prior opt-in
  native agent probes** and **2 opt-in Ollama-health variants**. Existing
  Starlette/httpx deprecation remains.
- Later reviewed-lineage, source-time, C mapping/omission and contract refinements
  passed final affected **172 passed/6 skips**, **164.77 s**, across learning,
  storage/evaluation, contracts, admin/agent monitoring, consolidation and
  expression. Its skips are **4 SQLite locking variants** with PostgreSQL
  counterparts and **2 Ollama-health opt-ins**. An earlier affected run was
  **101 passed/3 skips**, **89.21 s**. Do not infer a later full-suite count.
- Public synthetic evaluation **27 passed/1 SQLite locking skip**, **29.50 s**:
  five cases, two database backends and thresholds 3/4 give **20 measured
  eligibility decisions**, zero automatic promotions. Single explicit/copy/weak/
  three-independent/four-independent cases distinguish threshold behavior.
  This does not prove preference accuracy or an optimal real-world threshold.
- Final Ruff lint/format **180 files** clean, compileall and repository-configured
  Git whitespace check passed. Existing **75 path operations/105 schema shapes**
  preserved; current OpenAPI **82 paths/118 schemas** adds seven learning paths
  and optional capability/response/aggregate fields. **23 protected history,
  prompt, lock/wrapper and later-plan files** unchanged. All **53 other previous
  fixture payloads** preserved byte-for-byte. **68 synthetic fixtures** include
  12 new learning cases; current capabilities/readiness/manifest refreshed.
  Actual HTTP fixture export **1 passed/1 unavailable-PG skip**, **2.08 s**,
  is SQLite evidence, not a PostgreSQL export claim.
- Android final XML **186 tests/0 failures/0 skips**; lint **0 errors/14 existing
  dependency advisories**, debug/test APK builds passed. Reviewed unit/lint/debug
  gate **15 s**, **53 tasks (11 executed/42 up-to-date)**. Initial v8-tag/legacy
  version expectations and fixture names were corrected; no unit failure remains.
  Actual emulator HTTP portrait gate: **7 focused tests passed**, **53 s**, plus
  **two actual force-stop stages** restoring the original reviewed receipt and
  strict cold launch **Status ok**. The tests cover selected-source Settings
  review/edit/reject/pause/reset and exact saved C source display, plus expression
  and memory regressions. The full old instrumented suite was not freshly rerun.
  Compact enlarged-text rerun results are recorded in the final audit below.
- Web clean `npm ci` reported **0 vulnerabilities**; contract generation/freshness,
  typecheck, lint, **54 units** (**23.92 s**) and production build passed.
  Actual isolated PostgreSQL/HTTP production-build Chromium regression:
  **6 passed**, **22.2 s**. Final contracts/type/lint checks passed again after
  the final schema export. Admin gains no private profile/source-text access.

Remaining targets/skips: backed-up intended application installation of **0012**.
Fresh configured database inspection failed (`OperationalError`); **0005 remains
an earlier observation**, not a fresh read. Ollama metadata failed (`ConnectError`),
so no Phase 15 native inference/wording-quality run occurred. Representative
consented preference/continuity accuracy, native-model language/resource/load,
physical **Samsung S24 FE/Android 16**, minimum API 26, HTTPS/network transitions
and manual TalkBack/keyboard checks remain. Emulator is API 37 / Android 17;
test-only deterministic HTTP providers establish protocol/provenance behavior.
Release signing/distribution and standalone old-checkout smoke were not run.
Final account/backup/historical-snapshot retention policy remains unresolved and
is disclosed in Settings/policy. Historical replay is tested, not deletion.

No application migration, real account/role change, semantic activation, external
message, later phase or deployment. Task resources contain synthetic fixtures;
prior retained/blocked Phase 11–13 storage was not cleaned or retried.

Final Phase 15 audit — 2026-10-11 21:57 UTC (14:57 Phoenix): compact
**900x500/240 dpi/1.5x text** run passed **7 focused HTTP UI tests**, **51 s**,
**two force-stop recovery stages** and strict cold launch **Status ok**. Initial
offscreen assertion and subsequent child-scroll lookup failed; scrolling the
Sources LazyColumn to its uncomposed quote before the child assertion resolved
the test. Geometry/density/font were restored. **14 changed/new Markdown files**
passed UTF-8/local-link checks; final contract/history/53-fixture-byte audit and
normal Git whitespace check passed. Disposable PostgreSQL schemas count was zero;
task-owned PostgreSQL and emulator stopped. No fixture HTTP/web/test-PostgreSQL
listeners remained. The existing PostgreSQL service and prior retained/blocked
storage were untouched. No unresolved local failure; target gates above remain.
Stop at Phase 15.


## Phase 16 — implementation and local verification — 2026-10-12 04:17 UTC

Code: base `4df9a72` plus the preserved Phase 14/15 working tree and this Phase 16
implementation. Required/root/scoped instructions, README/architecture/current
state, OpenAPI/source/migrations and Python/Android/web baselines were inspected
before stream wiring. Phase 04 chat/recovery and Phase 06 server-granted monitoring
met the source prerequisites. Earlier installation/physical gates are retained;
this implementation does not claim those were completed. Displayed local date is
2026-10-11, America/Phoenix. Android **0.16.0-streaming**, versionCode **11**.

Implemented checkpoints:

- Additive **0013**, owned composite attempt/event foreign keys, monotonic durable
  sequences, bounded provisional/checkpoint replay and guarded populated downgrade.
  Migrations 0001–0012, personality prompts and dependency locks/wrappers unchanged.
- Reused exact ChatService reservation, request UUID/options/fingerprint, frozen
  prompt/retrieval/expression/learning/source mapping; legacy API/CLI unchanged.
  Final response, assistant event/source, revision and terminal event commit once.
- Bearer-header submit/status/SSE/cancel; idempotent exact-attempt cancellation
  intent/receipt, completion-vs-cancel locking, delayed shutdown admission and late
  worker fences. Cancelled maps to old **failed/request_cancelled**. Explicit retry
  retains its snapshot and existing revision checks. Observer loss never cancels.
- Bounded native Ollama NDJSON, UTF-8/frame checks, 64 KiB text, 256 retained events,
  16-event batches/16 observers and shared generation admission. Retained attempts
  are limited to 8/request and 1,000/owner. Quota rejection rolls back reservation.
  Instance restart, failed terminal write, operator recovery and expiry fence
  publication. No inference/observer connection spans an open DB transaction.
- Android real authenticated OkHttp SSE, duplicate/gap/checkpoint handling,
  provisional/incomplete display without early source cards, real Stop, bounded
  reconnect/Retry-After, conversation/navigation/background detach and GET-only
  same-request force-stop recovery. Existing encrypted journal stays **v9**.
- Admin exposes only stream state/sequence/replay floor/creation/finish metadata;
  no deltas, private text or cancellation control. Optional capabilities gate the
  new client path; older capability payloads retain ordinary chat/polling.

Actual checks and evidence:

| Check | Result / provenance |
| --- | --- |
| Backend baseline, migrated SQLite + native PostgreSQL 18.6 | **601 passed, 2 failed, 22 skipped**, 535.78 s. Pre-existing SQLite admin 503 and hybrid recall 0.8571 vs 1.0; the same focused tests then **5 passed**, 10.70 s (reservation refactor had just landed). No unrelated fix is claimed. |
| Baseline Ruff / Android / web | Ruff lint/format **129 files**; Android **186 units**, fresh 53 s run; web **54 units** and contract freshness passed. |
| New streaming invariants | Initial auth/cancel red **1 failure/1 unavailable-PG skip**; first gate **5 passed/1 failed** exposed a mixed SQLite checkpoint read, fixed with snapshot transaction. Then **6 passed**, expanded **21/1 skip**, TCP **23/1 skip**, metadata/failure **27/1 skip**. |
| Full changed backend | **631 passed, 23 skipped**, 539.09 s. This run precedes the final operator/quota/deadline defenses below. |
| Final review invariants | Operator recovery/state mismatch and quota configuration red **4 failures**; follow-up **30 passed/2 failed/1 skip** had only a test assertion using the wrong error envelope, corrected to existing detail. Final-only deadline publication red **2 failures/2 passed**; fixed the finish-time fence. |
| Final affected PostgreSQL/SQLite suite | **92 passed, 2 skipped**, 88.03 s: stream service/provider/TCP, contracts, foundation/legacy chat, admin and consolidation storage. Includes owner/request quota rollback, native cancel/completion race, delayed capacity, restart/stale publication and populated 0012 upgrade/check/replay/downgrade guards. |
| Final slow-observer/commit TCP addition | **2 passed**, 10.08 s after the affected run; an unread SSE body does not block the small synthetic generation, final commit survives detach, batch stays 16 and terminal replay stays exact. This is functional coverage, not a saturated-network/load benchmark. |
| Contract export / compatibility | Actual SQLite HTTP fixture export **1 passed/1 unavailable-PG skip**. OpenAPI **86 paths/122 schemas**; all 82 prior path operations and 118 prior schemas preserved except three optional additive fields. **Eight fixtures** added: 76 payloads plus manifest. **66** original JSON files unchanged; only capabilities/readiness/manifest updated. |
| Final backend/static audit | Ruff lint/format **138 files**, compileall and whitespace passed. **22** protected hashes match: migrations 0001–0012, personality, later phases and locks/wrappers. **16** changed/new Markdown files passed UTF-8/local-link checks. A first audit allowed-list used the wrong admin schema name; corrected to AdminRequestDetailOutput before the successful audit. |
| Android reviewed unit/lint/debug | **194 units, zero failures/errors/skips**, 19 s Gradle gate. Lint zero errors/14 existing advisories; debug/test APKs built. A new conversation-detach invariant failed before fixing observer transitions. |
| Android emulator: portrait + compact | Explicit synthetic HTTP provider on API37/Android17 emulator: **five focused UI cases**, **two actual force-stop stages**, strict cold launch **Status ok**. Portrait instrumentation gate 53 s; compact **900x500/240 dpi/1.5x text** 51 s. Compact first run failed one offscreen label assertion; scrolling the actual list/child passed, without product layout changes. Geometry/density/font restored. |
| Web frozen install / gates | Root npm ci encountered a Windows EPERM on a DLL held by the pre-existing user Vite process, after removing dependency files. Isolated same-lockfile npm ci **270 packages/zero vulnerabilities** succeeded. Missing workspace files restored; the matching locked DLL/existing files were not overwritten and user Vite stayed running. Isolated contracts/generation/type/lint/**55 units** (29.26 s)/production build passed; generated contract copied back and workspace freshness/type/lint passed. |
| Web actual HTTP browser | **Six production-build Chromium cases passed**, 21.3 s, using disposable PostgreSQL/HTTP and isolated UI port5174. User's existing port5173 process was retained. Credentials were memory-only; no credentialed traces/screenshots. |
| Native provider, separate from fixtures | Real **Ollama/qwen3.8:27b** against own migrated SQLite/ADA API: completed incremental reply, Stop -> cancelled/failed/request_cancelled, original cancel receipt replay, admission release and legacy non-streaming follow-up all passed. Final provider review run: completion first delta **17,281 ms**, total **18,703 ms**, 691 input/14 output tokens; Stop first delta **2,125 ms**, total **2,235 ms**, unknown token counts. Earlier native run: 16,547/18,485 ms (691/16 tokens) and Stop 2,172/2,265 ms. These are synthetic smoke timings, not quality/load or remote GPU-stop acknowledgement. |

Intermediate checks did not count as success: one affected command named absent
legacy test files and collected nothing; stale OpenAPI/fixture expectations caused
**69 passed/2 failures/2 skips** before regeneration; the interrupted root web
install left generation/type commands without their executables until repair.
The existing Starlette/httpx warning, npm whatwg-encoding deprecation and lint
advisories were recorded without upgrading pinned dependencies to suppress them.

Skips: full backend **15 SQLite row-lock variants** with executed PostgreSQL
counterparts, **six prior opt-in native agent probes**, **two opt-in Ollama-health
cases**. Final affected skips are the SQLite cancellation race and consolidation
locking copies; both PostgreSQL counterparts ran. Fixture export's PG copy had no
PG URL in that export command; final PG contract checks ran later. Real Phase 16
provider smoke is separate from the skipped older opt-in probes.

Remaining installation/target verification: a fresh read-only check observed
configured application head **0005**, while current source requires **0013**.
No application migration/deployment was performed. Backed-up intended installation,
physical Samsung S24 FE/Android16, minimum API26, HTTPS/mobile network interruption,
manual TalkBack/accessibility, signed release, full old instrumentation suite,
other browsers and representative concurrency/resource/slow-network measurements
remain. Native smoke predates the final finish-time defensive fence; the final
provider/legacy/lease tests cover that refinement. No native quality/remote GPU
stop acknowledgement is claimed.

Retention limit: 24-hour finished cursor access is **not timed deletion**. Private
provisional/checkpoint text and bounded retained events/attempts persist; incomplete
text stays outside completed assistant history/factual retrieval. Account/backups/
historical erasure requires a separately selected policy. No voice, autonomous
background tasks, real external tool effects or Phase17–19 implementation.
See [the policy](../docs/STREAMING-AND-CANCELLATION.md). Stop at Phase16.

Final Phase 16 audit — 2026-10-12 04:20 UTC (2026-10-11 21:20 Phoenix):
Ruff lint/format138files,16UTF-8/local-link Markdown checks and whitespace passed
after the final changes. OpenAPI/protected-history/fixture compatibility audit
passed. Disposable PG schemas count zero; only the task-owned PG55414/emulator5556
were stopped. No task fixture HTTP18763–18765 or isolated web5174 listeners remain.
The pre-existing user Vite5173/PID636 and PostgreSQL5432 were retained. Prior blocked
synthetic artifacts and new ignored validation evidence retained. No unresolved
local check failure; intended installation and target/retention gates remain.


## Phase 17 — explicit Android voice input and output

Recorded 2026-10-12 11:44 UTC (04:44 America/Phoenix). Scope only Phase 17;
Phases 04/16 prerequisites were present in current source, exported contracts and
passing baseline tests. Initial worktree was clean at 18690f0. No later phase,
application migration, server deployment or external message was performed.

Implemented all four code checkpoints: explicit record/stop/discard and runtime
permission/availability states; on-device-only ASR selection from primary Android
docs with en-US default/selectable installed language checks; separately encrypted
original/reviewed approval followed by typed owned submission and immutable
endorsement lineage; installed offline TTS with completed safe text, voice/speed
and independent focus/device/noisy-output/lifecycle/Stop playback handling.
Audio is not retained by the app or sent to ADA. Platform metadata/duration are
client reported; no server audio hash or attested recognizer binary is claimed.
Original ASR is generated interpretation and never enters model context/factual
memory. Approval creates only a normal user-explicit turn with user-reviewed
lineage. Text, frozen snapshots, plain fingerprints and existing source contracts
remain intact. See [VOICE-INTERFACE.md](../docs/VOICE-INTERFACE.md).

Migration 0014 adds composite owner/request/conversation/scope/endorsement foreign
keys, unique owner/capture IDs, bounded metadata and guarded downgrade. Voice
history is capped at 1, 000 per owner, with immutable retained original text and no
new deletion/erasure policy. Android v10 atomically consumes the approved draft
into the exact pending request before POST; v1–v9 remain readable. Recovery reads
only. Background saves are checked on resume; draft loading blocks new capture,
and another conversation's saved draft offers Open/discard. Rejected voice returns
to unapproved review, preserving an independent typed draft. Unsupported servers
cannot fall back to authored-text submission. Stop playback does not cancel a
request; Phase 16 Stop/retry/fencing/capacity rules are reused.

Checks actually run:

- Baseline: full SQLite + disposable PostgreSQL 18.6 **639 passed, 23 skipped**
  (579.88s), Ruff lint/format 138 files; fresh Android unit/lint/debug build and web
  contracts/55 units. Previous Phase 16 evidence remains unchanged.
- Initial boundary checks: backend reviewed route **2 failed** before implementation
  (missing route); encrypted journal **2 failed** before v10 storage. Subsequent
  voice/streaming checks **79 passed,1 expected SQLite lock skip** (67.26s).
- First full implementation suite: **694 passed, 23 skipped,1 failed** (683.92s).
  The existing PostgreSQL hybrid evaluation measured fallback 1/13 where its test
  expects zero; ownership/exact-evidence assertions passed. No retrieval code or
  evaluation assertion was changed. Focused hybrid+voice rerun **59 passed**
  (54.11s), then a second full run **695 passed, 23 skipped** (645.99s).
- The23 skips are15 SQLite-native-row-lock copies,6 pre-existing opt-in native
  agent probe copies and2 opt-in Ollama-health copies. All PostgreSQL native lock/
  schema copies ran. Existing Starlette/httpx deprecation warning remains.
- Final Ruff lint/format **144 files**, compileall and whitespace checks passed.
  Actual HTTP/schema fixture generation passed. All86 old OpenAPI paths and122
  existing schemas retain their contracts except two optional capability fields;
  three routes/three schemas added. All22 protected migration/prompt/lock/wrapper/
  Phase 18–19 hashes unchanged. 79 synthetic HTTP fixture payloads; only two old
  capabilities and readiness payloads changed, with old history payloads preserved.
- Android **211 unit tests, 0 failures/0 skips**; testDebugUnitTest, lintDebug,
  assembleDebug and assembleDebugAndroidTest passed. Lint0 errors/14 existing
  dependency-version warnings. Tests cover encrypted approval/commit failure,
  released v9 read, identity/scope changes, draft recovery/load races, permission
  states, language/hardware errors, duration/setup/final deadlines, edit approval,
  duplicate Send, old-server gating, safe completed playback and late callbacks.
- API 37/Android 17 disposable emulator: **7 normal HTTP/Compose/Keystore checks**
  (four existing memory checks, two voice checks and native availability),
  **2 voice checks at 900×500/240dpi/150% font**, and **4 successful actual force-stop
  stages** for saved review and exact submitted request. No skips/failures. Final
  voice checks include actual activity pause/resume. Synthetic capture/playback
  adapters are explicit; real HTTP/source lineage, Android permission plumbing,
  production controller and Keystore are exercised. A separate native factory
  availability probe reported Available; it did not record speech or prove en-US
  installation. Final cold launch Status:ok/COLD,2517 ms (emulator smoke only).
- Web: pinned npm ci in an isolated workspace (270 packages, 0 audit findings),
  generated DTO freshness, typecheck, lint, **55 units**, production build and
  pinned Chromium installation passed; **6 PostgreSQL-backed Chromium checks**
  passed against that build on private test port 5174 (27.4s). Root clean npm ci was
  not run because the existing user Vite installation was in use at baseline.
  Dependency locks unchanged; no web voice controls were added. Known dependency
  deprecation/NO_COLOR warnings remain.

Remaining verification and skips are deliberate: no real microphone/speaker/
headset or en-US speech samples, airplane-mode ASR/TTS, real permission dialog/
revocation matrix, hardware focus/call/Bluetooth/noisy-route behavior, CPU/RAM/
battery or transcription accuracy was measured. Check the intended S24 FE/Android 16
and older API 26/31/33 devices, TalkBack/keyboard, release HTTPS and retained private
transcript/backup policy before claiming target readiness. No server audio decode/
malformed-file/ASR-provider test applies: the server accepts no audio; forbidden
JSON audio fields and engine/size/duration/Unicode limits are tested. Inherited
model timeout/cancellation checks ran; native agent/health opt-ins were skipped
as noted. A fresh read found configured application revision 0005 and the configured
native model installed; no new real-model inference or application upgrade ran.
Install the supported chain through 0014 separately when authorized.

Cleanup: disposable PostgreSQL fixture schemas counted zero; task-owned PG 55417
and emulator 5556 were stopped. No task HTTP 18763/18765 or web 5174 listeners remain.
The pre-existing PostgreSQL 5432/PID 8868 was untouched. No stop was issued for the
user's Vite 5173; the final listener inventory found it absent. Prior validation
records/artifacts and new ignored synthetic evidence are retained. Stop at Phase 17.


Final Phase 17 audit — 2026-10-12 11:55 UTC (04:55 America/Phoenix):
The final UI audit made typed Send react to the observed voice phase; a nonempty
independent typed draft stays disabled during recording. Final 211-unit/lint/
debug/test-APK checks passed. Focused real-HTTP voice UI checks passed again:
two normal and two compact/font150% cases, including that reactive control and
actual activity pause. Final snapshot cold launch Status:ok/COLD, 2797 ms. Earlier
checks and timing records above remain evidence of their own runs. Eleven changed
Markdown files passed UTF-8/local-link checks; Ruff 144 files, protected 22 hashes,
old contracts/fixture compatibility and whitespace passed. The last task-owned
emulator was stopped again; PG 55417 remains stopped. No later phase/deployment.


## Phase 17-A — S24 FE physical audit — 2026-10-13 UTC

Scope: user-requested physical testing and a **planned** follow-up only, at source
`2c242d1`. Read root/client/plans rules, README, architecture, current state,
standards/workflow/status and Phase17; inspected implementation, migrations,
OpenAPI and existing test baseline. No production code, API, prompt, migration,
lockfile or dependency change; no intended database upgrade or deployment.
[Phase 17-A](phase-17-a-s24-fe-validation-and-hardening.md) is planned, not implemented.

Target: connected Samsung S24 FE/SM-S721U1, Android16/API36, primary user0,
1080×2340/450dpi. Installed user's `dev.ada.assistant.debug` v12/0.17.0-voice
was preserved, including RECORD_AUDIO=false. Separately installed validation
app/runner used identical production Kotlin, changed test package/label and
127.0.0.1 test origins over USB reverse. Only synthetic owned disposable SQLite
head0014/fake-model HTTP was used. No production account data, raw speech,
credential or private quote was included in diagnostics/plans. Secure Folder
user151 was not accessed; generic package inventory's permission error was handled
by explicitly scoping subsequent package operations to user0.

Actual checks:

- `pytest tests/test_voice.py tests/test_streaming.py -q`: **40 passed,42 skipped**,
  29.19s, existing Starlette/httpx warning.41 skips were unavailable PostgreSQL
  fixture copies;1 was a SQLite native-row-lock copy. Full PostgreSQL/web/native
  model suites were not rerun for this documentation-only audit. Prior Phase17
  695/23 and browser results above remain historical evidence.
- Isolated unchanged-code Android `testDebugUnitTest lintDebug assembleDebug
  assembleDebugAndroidTest`: **211 units,0 failures/0 skips**, build110s,
  lint0 errors/14 existing dependency-version warnings. First isolated build
  failed for missing SDK location; copied the ignored local SDK configuration,
  then passed. Additional diagnostic runner/focus-fixture builds passed offline.
- Native inventory **1 passed** (2.72s): microphone hardware, on-device factory,
  en-US installed,15 eligible offline TTS voices/10 en-US. Availability alone
  was not used as a quality pass.
- Actual microphone R1 produced review/no-send but user was not ready; exclude
  its mismatch from accuracy. R2 **1 passed** (19.498s): controlled quiet8-word
  sample,0 word errors,ready386ms/result7625ms/capture7238ms. R3 airplane mode,
  Wi-Fi/mobile data off **1 passed** (29.953s): same controlled sample,0 word
  errors,ready504ms/result5825ms/capture5276ms. User confirmed exact quiet samples.
  Both checked no event before approval, actual reviewed owned HTTP submission,
  original generated interpretation/edited endorsement, absent audio hash and
  one lineage record despite duplicate Send. No transcript text was emitted.
- Real installed offline TTS/rates/Stop/owned completed reply/activity pause:
  **1 passed** (25.586s). Public sentence durations0.75/1/1.25/1.5× were
  **5589/4664/3758/3157ms**. User confirmed clear audio, rates and stopping.
  Native Stop suppresses late completion; actual pause stops completed-reply
  playback and resume does not restart it. Same-UID focus probe in that passing
  run was explicitly inconclusive, not a focus pass.
- Native capture interruption/missing language and adapted streaming UI:
  **2 passed** (18.587s). Actual pause/resume/navigation discard with0 events and
  no recovered draft; missing installed language safe error. First temporary
  capture test failed because it did not re-expand controls after Settings;
  correcting that test setup passed on unchanged production code.
- Initial selected physical regression16 tests: **13 passed,1 skipped,2 failed**
  (61.476s). Foundation invalid-token check needed its explicit integration flag;
  one voice provisional wait timed out; streaming locator searched compact
  history instead of noncompact pending panel. Flag-enabled retry **4 passed,
  1 failed** (19.919s): voice2/foundation2 passed; streaming locator failed again.
  Layout-independent locators subsequently passed on unchanged app. Initial
  timeout remains recorded as a flaky run; no invented product cause or fix.
  Six actual Keystore tests, four memory UI tests and platform probe passed.
- Actual force-stop recovery **4 stages passed**: edited review draft prepare/
  resume1.156/2.120s, submitted exact request prepare/resume1.194/7.051s.
  Recovery reads the original state; it does not auto-send a new request.
- Font150% portrait **5 passed** (36.277s): voice2/streaming1/foundation2.
  Font150% landscape **2 voice checks passed** (8.442s). Palette selection/
  persistence included. These are synthetic-driver UI checks, not TalkBack QA.
- Actual first-grant/denial assertions failed: verified OS choices result in
  `Interrupted`, losing the pending permission action. Repeated verified Deny
  reproduced false permission/rationale=true/Interrupted. Some later repeated
  denial attempts had no verified Deny click and unexpected granted permission;
  permanent-denial matrix remains **inconclusive**, not passed. Earlier dialog
  synchronization/external UI dump/synthetic setup-timeout attempts remain
  harness evidence, not extra product defects.
- Two combined separate-UID native focus probes failed; initial same-UID probe
  also failed an inapplicable assumption. Final isolated probe **1 failed**
  (6.489s): competitor confirmed focus granted/windowFocus=true but no native
  playback interruption callback. Investigate engine/listener coordination and
  audible behavior; ordinary activity-background stopping passed separately.
- Cold debug launches Status:ok/COLD **575ms**, final **538ms**. One foreground
  post-launch app snapshot PSS120751KiB/RSS217965KiB/swap584KiB; app idle CPU
  **4 ticks/~2s**, tick frequency not measured. These exclude recognition/TTS
  service costs and do not establish peak audio resource use. USB charging=true;
  battery47% initially/64% at later reading, temperature36.2/39.7C. No battery
  drain or speech-attributable thermal claim is possible under charging.
- Fresh fixture `/openapi.json` exactly matched committed OpenAPI:89 paths,
  125 schemas,3 voice routes. Protected353 production/contract/lock files hash
  identical. Ruff lint/format for `src tests scripts migrations` **144 files**
  passed; broader `.` invocation also passed (198 files including local artifacts).

Required changes:17A-01 permission action/lifecycle fencing;17A-02 investigate
and resolve native focus interruption;17A-03 portable non-destructive physical
runner, verified dialog actions, layout-independent locators and resource protocol.
The plan also lists remaining noisy/representative speech, native duration/deadline,
revocation/permanent denial, headset/Bluetooth/noisy-route/call, service CPU/RAM,
unplugged battery, older API26/31/33, manual TalkBack/keyboard, release HTTPS,
intended head0014 installation and retained transcript/backup checks. No headset
was available; user selected the phone microphone. Server audio decode/malformed
file/provider-ASR tests remain inapplicable: no audio-upload route exists.
Historical configured DB0005 was not freshly queried or migrated here.

Cleanup: restored airplane0/Wi-Fi1/mobile-data1/font1.0/rotation0/auto-rotation0;
Bluetooth remained1. Only owned fixture18767 process and USB reverse18764/18765
were removed. Validation app, runner and separate focus fixture were uninstalled
for user0, removing their test credentials/local drafts. User ADA version and
microphone permission are unchanged. Ignored sanitized evidence is retained.
Phase17 is partially target-verified with unresolved failures;17-A is planned.


Audit closeout — 2026-10-13 07:44 UTC (00:44 America/Phoenix):
Seven changed/new Markdown files passed UTF-8 and53 local-link checks;
protected353 files remain byte-identical to the pre-audit baseline at2c242d1.
Git whitespace check passed. Fresh cleanup verification found no validation
packages, owned reverse18764/18765 mappings or fixture18767 listener; all modified
phone settings matched the recorded originals. Prior records remain preserved.
No production fix, intended database migration, later phase or deployment.


## Developer how-to guide — 2026-10-13 — documentation only

Added [HOW-TO-USE-ADA](../docs/HOW-TO-USE-ADA.md) with step-by-step Windows tool
setup/clone, fresh PostgreSQL/Ollama/API installation, existing-data backup/upgrade,
account/token/admin grants, USB/emulator Android build/login, same-origin admin
proxy/login, implemented feature workflows, CLI examples, daily startup/shutdown,
troubleshooting and developer verification. Linked it from the root and client
READMEs; corrected current admin setup requirements to head0014 while preserving
historical phase/repair evidence. Phone permission/focus workarounds and pending
17-A gates are explicit. No product behavior, contract, migration or dependency
change; prior uncommitted audit documents/evidence preserved.

Checks actually run at source2c242d1: focused `pytest tests/test_memory_cli.py
 tests/test_upgrade_installer.py tests/test_client_contract.py -q` **8passed,
3skipped**,3.26s; all3 skips are missing `ADA_TEST_DATABASE_URL` PostgreSQL copies.
Existing Starlette/httpx deprecation warning remains. Ruff lint/format **144files**
passed. Actual CLI help checked main/chat/grant-admin/scopes create/memory remember/
correct/list/search/upgrade-prompt/recover-stale/rotate-token. `alembic heads`
reported0014; compared the source readiness constant and exported `/v1/me` fields.
All **48PowerShell examples** passed native AST syntax parsing without execution;
14 contents anchors, UTF-8 and135 local links across12 changed/new Markdown files
(including prior audit edits) passed.415 protected implementation/test/contract/
wrapper/lock files byte-identical; git diff contains Markdown only, whitespace clean.

Official Git/Python/Docker/Ollama/Temurin/Node/Android install/device/CLI and Compose
copy references were browsed and linked near their instructions. Pins/defaults are
repository requirements, not claims of universal model availability/performance.
Initial local validators needed explicit UTF-8 on Windows and support for indented
Markdown fences; corrected validators passed with no guide syntax defect.

Skipped: full PostgreSQL/backend/client build/browser/device/native inference and
fresh-install walkthrough; documentation changes require no product rebuild or
real application mutation. Setup/dependency installs/model pulls, doctor/current
against the configured database, backup/migration/account/grant changes and service
startup were **documented, not performed**. Intended runtime/HTTPS installation and
17-A fixes remain pending. No deployment or later-phase implementation.


Documentation closeout — 2026-10-13 08:42 UTC (01:42 America/Phoenix):
Final UTF-8/local-link check passed12 Markdown files/136 local links (including
preserved prior audit edits);415 protected implementation/contract/test/wrapper/
lock hashes unchanged and whitespace check passed. Guide is linked from the main
and client READMEs. No runtime setup, application migration or deployment performed.

## Phase17-A + Phase18 checkpoint — 2026-10-14 UTC — testing paused by user

Source: working tree based on `2c242d1`; earlier uncommitted documentation/audit
work preserved. User authorized Phase17-A fixes followed by Phase18 only. The
user stopped testing to disconnect the S24 FE and intends to resume tomorrow.
This is a saved checkpoint, **not a claim that all exit gates are complete**.
Phase19 is unimplemented. No deployment, intended database migration, live backup,
private account erasure or normal Android app installation was performed.

Implemented checkpoint evidence:

- 17A-01: preserve a foreground, same-context recording intent across its own
  permission dialog; cancel on real background/context departure, denial or stale
  callbacks. Five new failure cases preceded the fix. Real first-grant and
  repeated/permanent-denial dialog checks passed on the isolated API36 phone and
  API37 emulator. Settings-return and active native microphone revocation remain
  target checks, distinct from these synthetic-capture permission tests.
- 17A-02: exact per-acquisition focus leases reject abandoned callbacks; native
  speech/media attributes and loss/duck handling stop playback without resuming.
  Debug-only validation probes use public synthetic speech and a separate UID.
  User confirmed clear speaker output and explicit Stop. Latest tightly staged
  full-focus trial recorded native start, fixture launch, focus-transient-loss
  and adapter interruption (about6.6s after start), plus a new granted full-focus
  result from the fixture. The user reported speech continuing in the fixture;
  whether it stopped after a delay was **not confirmed before testing stopped**.
  Do not call this a completed audible interruption pass. Earlier stale/no-overlap
  requests are inconclusive; historical failed probes remain recorded above.
- 17A-03: explicit selected-device/user0 runner, separate validation app IDs and
  label, injected USB-loopback HTTP origin, APK-ID guard before install, verified
  OS-dialog actions, layout-independent locators, explicit IME preconditions and
  owned cleanup. Normal ADA app/data/permissions were preserved.
- 18A: migration0015 adds digest-only owner credentials with labels, issue/expiry/
  last-use/revocation, configured enrollment, atomic rotation and exact operation
  replay. Legacy CLI tokens remain compatible. Fresh response/SSE authorization
  stops revoked delivery; admitted work may complete durably. Android Settings
  and encrypted v11 journals retain v1–v10 reads and GET-only recovery. Admin
  access remains server-granted; no device/name/personality can grant a role.
- 18B: one worker, bounded per-owner/global HTTP admission, read/write rates,
  actual body bytes/deadline/depth, sanitized fixed failures and bounded telemetry.
  Loopback start script and private VPN + supplied trusted HTTPS certificate
  Caddy example/runbook added. No extra inference/job process or shared multiworker
  admission claim. Only scoped cryptography dependency additions; locks preserved.
- 18C: AES256-GCM/scrypt encrypted backup to selected
  `%LOCALAPPDATA%/ADA/backups`, exported PostgreSQL snapshot, dump +54-table
  row/hash manifest, allowlisted config and separate current deletion ledger.
  Isolated new `ada_restore_*` targets only; restored credentials quarantined,
  later owner erasure/tombstones reconciled. Populated54-table drill checked
  source hashes, original replay/citations, jobs and revocation. Latest completed
  drill measured backup0.516s/restore1.25s on a small native PG18 fixture, not a
  production recovery objective. Data loss boundary is the exported committed
  snapshot plus the latest supplied deletion ledger; no live backup was taken.
- 18D: selected policy is retain until explicit owner deletion, no age expiry.
  Fresh preview/revision/count confirmation, durable UUID job, bounded leases/
  retries and atomic dependency erasure cover all45 installed private-content
  tables and search projections. UUID-only request tombstones return410; account,
  credentials/grants and minimal operation metadata remain. Android epoch changes
  clear private journals/controllers; admin privacy epoch clears caches. Backups
  and offline clients may retain copies; erasure cannot promise remote wiping.

Checks actually run (preserve failures and provenance):

- Initial SQLite baseline382passed/336skipped; dedicated PG18 voice/stream baseline
  81passed/1SQLite-lock skip. Baseline Android build was mostly cached, not a new
  full unit execution. First PG invocation named a nonexistent test and ran none.
- New permission regressions initially3failed, then13focused tests passed. Initial
  security invariants9failed/9skipped, then implemented paths passed and expanded
  PostgreSQL/graph/recovery suites passed. First full server run11failed/736passed/
  23skipped; fixed admin SQL overfetch, preflight downgrade guards and isolated
  recovery fixture assumptions. Subsequent complete PG18/SQLite suite **747passed,
  23skipped,1warning in978.20s**. This precedes final narrow refinements; affected
  security/recovery/contracts then **62passed,1skip,1warning in112.80s**. A further
  standalone recovery-import inventory regression check was added at closeout;
  its last affected run is recorded separately when completed, not assumed here.
- Full server skips remain the suite's deliberate SQLite locking/provider/optional
  fixture limits; they are not new passes. Existing Starlette/httpx deprecation
  warning remains. Native PG18 exercised real schema, populated migration,
  concurrency, deletion rollback/lease fencing and isolated restore.
- Ruff lint/format **154files passed** after final standalone-import test formatting.
- Latest Android normal-package unit/lint/debug/instrumentation/unsigned-release
  and separate fixture build **BUILD SUCCESSFUL38s**,161tasks27executed; prior
  full unit report **224passed,0failed,0skipped**. A late wording edit briefly
  failed compilation due to UUID-to-Text types; explicit string conversion fixed
  the rerun. Earlier fixture-version, MockWebServer host and Windows concurrent
  Gradle file-lock failures were corrected; no conflicting APK was installed.
- Isolated API37 emulator:8HTTP/Compose checks, two real OS-dialog cases, two actual
  force-stop prepare/resume pairs (four stages), and SecurityUI HTTP/Keystore flow
  passed. Phone API36 retry:8checks43.148s, first grant3.238s, repeated/permanent
  denial2.607s, same four force-stop stages and SecurityUI6.295s passed. Initial
  phone attempt failed window-focus preconditions before the user unlocked it.
  OS-dialog suites use synthetic capture; they are not native ASR quality tests.
- Web npm clean install/typecheck/lint/build and contract generation/check passed;
  **56unit tests passed**. Final full PG-backed Chromium rerun **6passed25.5s**.
  Earlier full run had one refresh-focus failure (5passed/1failed); focused retry
  passed before this clean full rerun. First E2E fixture timeout used the wrong
  database environment variable and was corrected.
- Python lock audit:0known vulnerabilities/41dependencies; npm audit:0findings/
  295dependencies. These are audit-time findings, not a security guarantee.
- Exported contract now96paths/132schemas (baseline89/125), with nine additional
  synthetic credential/deletion fixtures (88total). Existing request schemas and
  enums retained; UserOutput data_epoch defaults0 and capability additions default
  unsupported. One-time issue secrets are never captured in contract fixtures.
  Final protected-file/fixture-byte/newline and documentation audits remain open.

Cleanup before phone disconnect: temporary physical validation app/test and separate
focus fixture uninstalled for user0; owned USB reverse19820 and fixture listener
removed. Read-only check confirmed normal ADA debug versionCode12 unchanged.
Owned read-only emulator stopped. Phone settings/private profiles were not changed.
The disposable PG18 server remains only while the already-started affected suite
finishes; its cleanup/result is recorded below. No new testing is authorized by
this checkpoint until the user resumes.

Remaining verification: confirm audible full/transient/duck interruption with
fresh granted overlapping focus and timing (not merely callback); settings-return/
active native revoke, calls/headsets/noisy routes when available, representative
speech/native duration/deadlines, service resource/unplugged battery measurements,
older API26–33 and manual TalkBack/IME. Phase18 still needs final source/contract/
protected-history/doc audit and Caddy syntax/actual private HTTPS validation.
Intended installation, real data sizing/capacity and live operations remain separate
scope; none is implied by successful disposable fixtures. Retain historical device
and native-model evidence rather than presenting it as new Phase18 validation.
Resume from these open gates; do not implement Phase19 or deploy.

Pause closeout — 2026-10-14 10:36 UTC: the affected suite already running when
pause was requested completed **63passed,1skipped,1warning in130.00s**, including
standalone recovery inventory registration. No further suite was started. The
owned disposable PostgreSQL18 loopback55418 server was shut down with pg_ctl
using its checked task-owned data path/port; no configured application service
was stopped. Native audio overlap/audible-stop confirmation remains open.

## Gap audit and future planning — 2026-10-15 (documentation only)

A read-only gap audit of all plans/ phase files against source, tests, contracts,
migrations and clients was performed. Findings are recorded in
[GAPS-AND-FUTURE-PLANS.md](GAPS-AND-FUTURE-PLANS.md): 29 gaps (G-01…G-29) —
operational/installation, deferred-by-design and user-requested capabilities —
plus 13 future-plan proposals (F-0…F-12) with a recommended sequencing, and the
log-maintenance conventions. No code, migration, contract, product behavior or
phase-table change was made; the phase status table above is unchanged. No test
suite was rerun and no live database was queried. This document does not
authorize building anything. Next eligible work is F-0 (close known gaps,
including the authorized installation) or a user-selected F-xx, upon explicit
selection.

## Future roadmap review — 2026-10-16 America/Phoenix — documentation only

Reviewed requested repository instructions/current-state records, the original
GAPS-AND-FUTURE-PLANS audit, all phase status/exit/deferral sections and relevant
actual source, OpenAPI, migrations and tests at `fa2cbba`. Source head is 0015;
exported OpenAPI has 96 paths/132 schemas and 15 migration files. No live database
state was queried or inferred from the historical 0005 observation.

Added [FUTURE-ROADMAP](FUTURE-ROADMAP.md) and twelve proposed phase files, 20–31,
with inputs, bounded checkpoints, proposed data/interfaces, failure tests and
exit criteria. Reviewed all 29 original gap IDs, retained their dated evidence,
added corrections plus G-30–G-40 prerequisite/design risks, and mapped their
next phase or deliberate deferral. No gap is closed merely by this planning.
Main corrections: 0015-only recovery cannot back up an older database unchanged;
valid HTTPS origins are already supported by Android; explicit consolidation
workers and five evaluation programs already exist; password login still needs
sessions; generic questions need no prior evidence; source retention stays the
chosen policy. Every future schema must extend backup/erasure/authority quarantine.

Confirmed owner choices: existing laptop on AC/awake initially; all three curiosity
channels (active chat, later inbox, occasional initiated notices), implemented in
stages with topic/channel/hours controls. Everyday task priorities remain provisional.
Physical-Android validation and iOS excluded as requested; older target gates stay
open without blocking independent server/web/emulator planning. Local speech has
only a proposed architecture/license study until later hardware measurement.

No runtime feature, authentication scheme, migration, contract, test, dependency,
model, service or device was changed. No deployment, live migration/backup, account
mutation, network enrollment or external message. No application test suite rerun:
this review changes documentation only. Prior Phase 18 runs remain historical,
not new evidence. Documentation/protected-file checks are recorded at closeout.
Next suggested selection is Phase 20; selection/implementation is not implied here.

Planning closeout — 2026-10-16 America/Phoenix: UTF-8 and **122 local links across
20 changed/new documents** passed; all twelve proposed phase files have distinct
20–31 numbering, checkpoints, interfaces, failure coverage and exit criteria.
All 29 original gap IDs have an explicit disposition. **519 tracked files outside
the six intentionally edited tracked documents are byte-identical** to this review's
starting snapshot, including runtime source, tests, migrations, prompts, contracts
and lockfiles. New files are planning documents; unrelated preexisting files were
preserved. Git whitespace check passed; Git's LF→CRLF notices are informational.
First documentation validator required a clearer failure-test heading in optional
Phase 30; corrected and rerun successfully. No application tests were run or claimed.

## Phase 20 — release readiness and quality baseline — 2026-10-16

Source: `fa2cbba` plus this working tree. Prerequisites verified from source,
96-path/132-schema exported OpenAPI, immutable migrations0001–0015, existing
security/recovery/evaluation tests and retained evidence. Read required root,
planning and scoped client rules. Preserved earlier planning edits/unrelated
files. Physical-Android and iOS excluded. No live schema query or installation.

| Checkpoint | Implemented result / actual verification |
|---|---|
| A | Source OpenAPI equals the saved export; protected history/fixtures/locks audit; current architecture/navigation/17-A implementation checklists reconciled. Three strict API37 emulator cold launches Status:ok/COLD at3371/2683/2332ms. Actual Caddy2.11.7 template/loopback TLS/JSON/SPA/SSE checks, reproduced `/admin`404 fixed to308→`/admin/`. |
| B | Separate `ada.legacy_recovery` format `ada-postgres-legacy-0005-v1`, encrypted exclusive artifacts, new isolated target only, exact19-table row/hash verification, all restored tokens invalidated. Populated0005 restore→injected transactional upgrade failure/rollback→successful0015 upgrade/drift check→original cited completed replay/source hash preserved. Source remained0005 with original credential intact. |
| C | Explicit0005/0015 inventory policy; unsupported heads, unknown actual tables/owner models and mismatched PostgreSQL binary majors refused. Original0015 format remains compatible; populated54-table current restore/replay/revocation/latest erasure ledger drill passed. Future heads/session/schedule authority need explicit policy/quarantine/erasure changes. |
| D | Reused five evaluation adapters, canonical JSON digest manifest, development/heldout split, eight new heldout retrieval cases and saved aggregate `evaluations/quality-baseline-results-v1.json`. Exact provenance/isolation and fixture precision/markers remain separate from unassessed semantic usefulness/entailment. |
| E | Server/PostgreSQL, pinned Android/web, emulator, dependency/security and documentation checks below; concrete backup-first isolated rehearsal/intended-installation checklist in RELEASE-READINESS. All owned processes/packages/reverses stopped/removed. No live upgrade, new auth/features, deployment or later-phase implementation. |

Behavior/data contracts: head0015 unchanged; no migration, prompt, API schema,
capability, runtime Android feature or dependency/lock change. Only operator
recovery preflight/legacy format, evaluation tooling, example proxy redirect,
test diagnostics/focused runner and documentation changed. New tables/blobs were
not added. Username/password, LAN/Tailscale setup, public research, curiosity,
scheduling/dreaming and new speech remain future phases.

Checks actually run:

- Before implementation: focused `test_recovery/test_schema_contract/test_client_contract`
  **11passed,1warning33.17s** with isolated native PostgreSQL18; Ruff lint/format
 154files passed; source/export equality. Initial Android baseline passed13s but
  mostly cached; it is not counted as a fresh unit execution.
- Failure tests before features: recovery **3failed,2passed,1skipped** (missing
  legacy/policy/version features; native fixture URL not supplied to that initial
  invocation). Quality **3failed,1skipped** (missing scorecard adapter). Subsequent
  native recovery **9passed27.10s**. Expanded run briefly **1failed,21passed**
  because the seed fake reply cited nothing; changed the synthetic fixture to
  explicitly cite selected M1 evidence, then **22passed66.46s**. No product fix
  is attributed to that fixture mistake. An added test import/lint issue was
  corrected before final validation.
- Full PostgreSQL18.6/SQLite suite **760passed,24skipped,1warning1019.24s**.
  The full run preceded the final quality-test file/assertion strengthening;
  final affected recovery/policy/quality/schema/client-contract suite **23passed,
  1warning81.70s** covers the final additions. Twenty-four full skips: **16SQLite
  row/shared-lock/concurrency cases**, whose PG counterparts ran, and **8opt-in
  real-Ollama metadata/tool probes**. Existing Starlette/httpx deprecation remains.
  No skipped case is represented as passed. Native interrupted-migration injection,
  quarantine on inconsistent manifest, wrong passphrase/no target, unknown table,
  incompatible format/head, simulated full-disk failure and old cited replay ran.
- Latest small-fixture legacy drill: **19tables,1request; backup0.594s/restore0.859s**.
  Current populated drill: **54tables; backup0.765s/restore1.312s**. Legacy loss
  boundary is the exported committed snapshot; current recovery adds the latest
  supplied deletion ledger. Timings are small fixtures, not productionRTO/RPO.
- Quality pipeline actually ran all five existing families plus heldout, using
  PG where supported; extraction standalone remains SQLite. Claim recall/MRR@5
 0.8667; document recall/MRR1.0; heldout recall/MRR/exact coverage1.0, zero known
  owner/scope/future/negative failures. Fixture hybrid/extraction/episode outputs
  are explicitly synthetic. Python peaks/latencies were measured during concurrent
  validation, excluding DB/native/GPU costs. Semantic usefulness/entailment,
  uncertainty quality and future follow-up helpfulness are **unassessed**, not1.0.
- Fresh Android unit task with `--rerun-tasks`: **224passed/0failed/0skipped**,
 55s/24tasks executed. Final lint/debug/instrumentation/unsigned-release build
  **passed64s**,123tasks31executed. No normal phone package was installed/reset.
- Owned read-only API37 emulator cold launches passed as above. First two eight-
  check HTTP runs failed provisional text; safe diagnostics found `Missing/NotFound`.
  Instrumented retry: **8passed55.072s**, real OS grant **1passed6.955s**, repeated/
  permanent denial **1passed6.379s**. Combined run then failed a force-stop resume
  with no emitted stage output. New `-RecoveryOnly` and stage diagnostics: **four
  prepare/resume checks across two actual force-stops passed**, SecurityUI **1passed
 7.812s**. Passing reruns do not establish a production fix; G-41 stays Open.
  No physical/native recognition/audio quality or older-API evidence is claimed.
- Web clean `npm ci`, contract freshness/typecheck/lint/build: passed. **56unit
  tests**, six files6.91s; production-build PG-backed Chromium **6passed23.3s**,
  including keyboard/contrast/zoom and revocation/state cleanup. No credentialed
  screenshot/video/trace. Actual manual screen-reader testing not available/run.
- Python pinned audit **0known vulnerabilities/41deps**; npm **0findings/295deps**.
  Existing no-deps/hash-lock and deprecated whatwg-encoding notices recorded; no
  blanket update. Audit-time absence of findings is not a security guarantee.
- Caddy official Windows2.11.7 archive verified with published **SHA512** before
  execution (initial SHA256 assumption refused safely). Actual template validates;
  lab CA verified only per-process, untrusted root/wrong hostname rejected, API
  auth-header forwarding/JSON errors, root redirect/nested SPA and two SSE frames
  passed. Tightened negative TLS harness initially could not see wrapped SSL types;
  direct TLS sockets resolved the diagnostic issue. No trust bypass or system CA.
- Final Ruff **160files** lint/format passed. New CLI help checked. Documentation/
  protected-file/PowerShell syntax results recorded in closeout below.

Skipped/remaining verification: matching standalone0005 server source is absent
in available history (0004 then0006), so schema recovery and forward current-server
replay are not old-server HTTP proof. Local model metadata endpoint unavailable;
no inference service start/download or real-model quality run. Manual assistive
review, actual private-network/system-trusted HTTPS, intended installation,
representative data-size/load/resource targets and physical/iOS checks remain
separate. Emulator streaming/recovery intermittency G-41 needs controlled-load
submission-level diagnostics before operational release. No root cause or fix
is claimed from successful retries. Historical fixture evidence was retained;
no blanket Temp/cache purge. Every non-device gap has its disposition in GAPS.

Cleanup: own PG18 loopback55420/data path verified then stopped; Windows startup
controller held by descendant waiting was stopped separately. Own read-only
emulator5582 stopped. No validation packages/reverse19822/listeners18420/19420/
19822/55420 remained at cleanup. Fixture accounts/data stayed disposable; no real
account/token/admin grant, application DB, .env, firewall, VPN or system trust change.
Stop at20; next feature phases require separate selection.

Phase20 closeout — 2026-10-16 America/Phoenix: final UTF-8/local-link check passed
**27Markdown documents/205local links**; native PowerShell AST passed **66examples**
and the updated runner. Source OpenAPI still equals the96-path/132-schema export.
**509tracked files outside the16 intentionally edited tracked files are byte-
identical** to this phase's initial working-tree baseline; all released migrations,
contract/fixture bytes, prompt sources, lockfiles and production Android source
are preserved. **12later-phase documents (19 and21–31) are byte-identical**. Prior
uncommitted planning/unrelated files preserved. Git whitespace passed; LF→CRLF
notices are informational. Audit reports/fixture metrics/safe failure evidence
remain ignored under `.pytest_cache/phase20/`; public aggregate results are in
`evaluations/quality-baseline-results-v1.json`. No live operation or deployment.

### 2026-10-16 — authorized local database/service operation and Windows guide

User explicitly authorized database changes/reset and deployment after Phase20.
Code: `fa2cbba` plus the existing Phase20 working tree. This follow-up changes
documentation only; runtime contracts, released migrations and prompts remain
unchanged. Existing uncommitted work is preserved.

Fresh inspection of the intended `.env` target (without printing its URL/password)
found Docker PostgreSQL **17.11**, database `ada`, host **127.0.0.1:5433**, head
**0015**, all **54tables**. Thus no0005→0015 upgrade was necessary or performed.
`alembic current`, `upgrade head` and `check` passed; upgrade was a no-op. Existing
two accounts, three personalities, four conversations,14requests,27events and
27sources were retained. The exact stored account name `Gourishankar` has an
enabled admin grant; `developer` does not. No existing token rotation/grant change,
database reset, `.env` edit, new migration or model download was needed.

Started the current API (one worker, no access log) on127.0.0.1:8000 and native
Ollama on127.0.0.1:11434; built current admin assets and served the loopback preview
on127.0.0.1:5173/admin/. These are ordinary local processes, not supervised Windows
services or auto-start tasks. Existing Docker DB was already healthy and left
running. Unrelated native PostgreSQL5432 was left alone. Enrollment/deletion worker
and embeddings remain disabled; existing consolidation setting remains unchanged.

Checks actually run:

- Live Docker `pg_isready`, SQL database/role/server/head/table/account metadata,
  native CLI doctor and no-drift Alembic checks passed. `/health/live` and
  `/health/ready` returned200/ready0015; unauthenticated `/v1/me` returned401.
- Through the actual built admin preview's `/v1` proxy, an ephemeral synthetic
  owner passed me/capabilities, ordinary admin403, explicit local grant then
  admin-me/overview/providers/requests/audit200, personality/conversation201,
  real `qwen3.8:27b` completed chat200, identical request replay200 and two stored
  events. First generation18.359s; corrected full rerun2.297s. These two tiny
  synthetic timings are not capacity or answer-quality evidence. The first
  one-off harness misread the events response as an object; corrected it to the
  contracted list and reran successfully. No product/API fix was required.
- Both ephemeral accounts, their content and grants were removed by exact UUID/
  random-name checks in a transaction; ordinary minimal monitoring audit entries
  were retained. Before/after comparisons of original users/credentials/grants,
  personalities/conversations/requests/events/sources/versions were identical.
  No secret, private content or credential hash was printed or put in reports.
- Focused schema/client-contract/admin/admin-HTTP pytest on SQLite and disposable
  schemas in Docker PostgreSQL17 `ada_phase2_test`: **37passed,2skipped,1warning,
  46.31s**. Both skips were opt-in non-generating real-Ollama health probes;
  explicitly enabled follow-up ran **2passed,1warning,2.00s**. The existing
  Starlette/httpx deprecation warning remains. Tests did not target live `ada`.
- Ruff lint and format checks passed (**160files**). Admin contract freshness,
  typecheck and production build passed. A temporary-table transaction from the
  new guide executed against PostgreSQL17 and rolled back completely; head stayed
  0015. Final documentation/PowerShell syntax/link checks are recorded below.

Added one consolidated
[Windows database administration guide](../docs/DATABASE-ADMINISTRATION-WINDOWS.md):
actual ports/credentials, Docker/native psql and optional pgAdmin, safe metadata
queries, audited account commands, migration workflow, matching-major encrypted
recovery, transactional SQL practice, guarded optional named-database reset,
service startup/shutdown and troubleshooting. README/HOW-TO/architecture/current
state link the new live evidence; G-01 local installation is closed without
rewriting the original audit or Phase20's test-only history.

Skipped/remaining: no live backup/restore or destructive reset was run, because
the schema was already current and no real maintenance edit was needed. Windows
pg_dump/pg_restore18 are installed but the live server is17; obtain matching17
clients and select a private passphrase before using ADA's recovery CLI on this
installation. No backup/key is implied by the earlier disposable drills. GUI
pgAdmin steps are instructions, not a GUI test. Full server/client/emulator suites
were not repeated for this docs/operator-only follow-up; prior Phase20 evidence
is preserved. No physical phone/iOS, manual assistive review, trusted remote HTTPS,
supervision/autostart, sustained load or broad real-model evaluation. G-06/G-09/
G-41 remain open; local hosting does not close those release gates. No firewall,
VPN, system trust or later-phase feature changes. Services intentionally remain
running for the user's local access; no external messages or commit.

Follow-up closeout checks: **8UTF-8 documents/108local links** passed;
**24new-guide PowerShell examples** parsed without execution, including guarded
destructive examples. Windows psql18 successfully queried the live PG17 target
using protected connection environment (no password argument/output); this does
not relax recovery's matching-major policy. Final API live/ready200, admin HTML200,
proxy unauthenticated401, exact live OpenAPI/committed-contract equality and no
leftover synthetic owners passed. Live counts remain2users/3personalities/
4conversations/14requests/27events/27sources/27versions. Git whitespace check
passed; existing LF→CRLF notices are informational. No destructive guide command
was run. Local service processes are intentionally left available.

### 2026-10-16 — Phase21 private-network connectivity — fed5d4b working tree

Scope: only `phase-21-private-network-connectivity.md`; no later phase or
deployment. Inspected rules/roadmap/current source, schema history/OpenAPI,
client transports/recovery/tests and Phase20 evidence first. Source prerequisite
0015/96paths/132schemas is intact; existing HTTPS/private auth/readiness supports
this work without a new API endpoint, migration or prompt upgrade. Physical/iOS
and real VPN/certificate/firewall execution were not selected.

Implemented checkpoints:

- A: Tailscale Serve → loopback Caddy18764 API/built-UI template; direct LAN TLS
  template defaults to loopback unless `ADA_PRIVATE_BIND` is explicitly set.
  Windows runbook covers both routes, controlled DNS/certificate ownership,
  narrow firewall example, renewal, exact-origin client setup and withdrawal.
  Tailscale identity headers never substitute for ADA credentials or admin grants.
- B: Android up to12 named HTTPS label/origin profiles, explicit selection/removal/
  clear and existing private-session reset; bounded readiness without a bearer
  before native me/recovery/rotation and browser admin sign-in. Native TLS/DNS/
  timeout/generic errors are distinct; unknown503 does not assert a DB cause.
  Web errors explicitly acknowledge browser diagnostic limits. Vite proxies fixed
  same-origin `/health` as well as `/v1`. Authenticated owner/capability/role and
  generation fences remain authoritative. Android version14/0.21.0-connectivity.
- C: strict version1 JSON label/origin import, full preview and explicit selection,
  no credential/trust fields or automatic connection. Manual entry remains. No
  camera/QR/deep-link handler, silent discovery or cross-origin web sign-in added.
- D: real Caddy + migrated disposable ADA + built UI + authenticated SSE/cursor/
  completed replay through direct TLS and the two-proxy Serve-boundary laboratory;
  certificate negatives, stopped upstream and emulator metadata/platform checks.
  The lab's local edge is not an actual Tailscale daemon/ACL test.

Privacy/data contracts: profile metadata is separate from Keystore private
state; selection clears the prior token/private session and never copies a
credential between origins. No release network-security/trust exception,
cleartext LAN, CORS widening, provider/DB native access, live `.env`/account/grant
change or application database operation. Released migrations/prompts/contracts,
Python runtime source and dependency locks remain unchanged. New Python code is
test/operator rehearsal only, using isolated loopback processes/disposable data.

Checks actually run:

- Baseline before implementation: Android HTTP/connection/chat selection
  **52unit tests passed**, Gradle27s; web **56passed30.75s**; schema/client pytest
  **6passed,2skipped,1warning8.76s** (PG URL not supplied); Ruff passed. Snapshot
  of551tracked paths captured before edits. Initial new profile tests failed
  compilation as expected before types existed; new web invariant suite **4failed**
  before preflight/path checks were implemented.
- Configured PostgreSQL test target was unavailable. Initial PG fixture run was
  interrupted rather than reported complete; first browser server startup timed
  out. Started an owned PostgreSQL18.6 loopback55421 cluster in ignored phase21
  storage, database `ada_phase2_test`, with public synthetic data only. No Docker
  engine/application DB repair/start was attempted in this no-deployment scope.
- Final focused schema/client/streaming/admin-HTTP pytest: **35passed,1skipped,
  1warning70.28s**, SQLite and real PG18. Security/erasure/revocation follow-up:
  **55passed,1skipped,1warning78.01s**. Both skips are SQLite native-row-lock cases;
  their PG variants ran. Existing Starlette/httpx deprecation remains. These are
  targeted suites, not a new full760-case Phase20 run.
- Android full units **231passed/0failed/0skipped**; final validation lint/debug/
  instrumentation/unsigned-release build passed26s/128tasks24executed after the
  last metadata bounds/storage guard change. Earlier full builds also passed74s,
 32s and49s. Final normal-application artifact check is recorded in closeout.
- Owned read-only API37 emulator5584: profile save/select/clear/remove, Activity
  recreation persistence and import preview/explicit selection passed8.765s;
  final metadata/DNS pair passed **2tests12.654s**. Reserved `.invalid` lookup
  produced native DNS feedback. Actual Android platform rejected the laboratory
  CA/hostname without a trust bypass. No physical phone or system-CA install.
- Actual Caddy2.11.7 direct TLS and two-proxy boundary checks passed: readiness,
  unauth401, ordinary admin403, explicit admin200, ignored network identity as
  authority, real built SPA/API routing, six durable stream events, cursor and
  completed replay, other-owner404, untrusted root/wrong host/expired cert rejection
  and stopped-upstream unavailability. Standard Phase20 proxy regression passed
  too (two fixture SSE frames). TLS CA trust was per-process only; model was fake.
- Web **64unit tests/7files passed8.00s**; typecheck/lint/contracts/build passed;
  production-build PG18-backed Chromium **6passed24.0s** with auth, revoked role,
  account/server cleanup, keyboard/contrast/zoom and existing fixed-error states.
  Five browser checks initially failed after preflight because Vite lacked the
  `/health` proxy; added it, then the full six passed. Fresh `npm ci`/final repeat
  results are recorded in closeout. No credentialed browser recordings.
- Recovery-only emulator evidence is deliberately mixed: first two runs passed
  four actual-force-stop stages each but failed SecurityUI deletion waits. Its
  test now waits for confirmation acknowledgement before owned GET polling and
  an explicit client refresh, with fixed safe status diagnostics. One corrected
  full run passed four stages + SecurityUI8.767s. A later repeat timed out in the
  existing voice-draft resume wait (line39); **G-41 remains Open**, not fixed by
  retries or a claimed production change. Preserve all these individual outcomes.
- Intermediate implementation/harness mistakes were corrected: Compose context
  access inside remember; mock-server host outside the debug allowlist; the web
  subclass initially dropped the public-request flag; an admin test DTO used the
  wrong fields; PowerShell split an unquoted dotted Gradle property; a nested
  Compose synchronization call failed. Host checks found the tailnet template's
  original hostname matcher rejected Serve's Host; changed to any Host on an
  explicitly loopback-bound socket. TLS harness now accepts Caddy refusing wrong
  SNI before certificate presentation, and handles combined no-store headers.
  These failed runs are not represented as passing checks.

Remaining verification: no actual Tailscale enrollment/allowed-versus-revoked
policy, real LAN firewall/DNS changes, positive system-trusted Android release
HTTPS, renewal, physical Wi-Fi/VPN handover, manual assistive review or sustained
load. G-06/G-29 installation/target parts remain open, as does G-41 reliability.
No new real-model quality claim or always-on service/scheduler/password login.
The new [private-network guide](../docs/PRIVATE-NETWORK-CONNECTIVITY.md) distinguishes
tested laboratory commands from unexecuted installation examples. Stop at21.

Phase21 closeout: normal application-ID Android units/lint/debug/unsigned-release
artifacts passed **28s/101tasks44executed**, with **231units/0fail/0skip**. Nothing
was installed onto a normal/physical phone. Fresh web `npm ci` installed270packages,
audited271 with0findings (existing whatwg-encoding deprecation); contracts/types/
lint, **64units8.17s** and build passed afterward. No dependency/lock upgrade.
Final LAN emulator-assisted and tailnet-boundary host rehearsals both passed,
including stopped-upstream checks; Android platform rejected the lab TLS endpoint.

Final checks: **17UTF-8 Markdown files/224local links** passed; **13new-guide
PowerShell examples** parsed without execution. **199protected tracked paths**
(server Python, released migrations/contracts/prompts/locks and phase19/20/22–31
plans) unchanged; **524of551 baseline tracked files** unchanged outside27intended
edits. Source OpenAPI equals the committed96path/132schema contract as parsed
JSON. Ruff lint/format **161files** and Git whitespace passed (informational
LF→CRLF notices). Validation metadata/logs are ignored under `.pytest_cache/phase21`;
no secret/private content was added to plans/reports.

Cleanup verified the exact owned PG path before stopping loopback55421; removed
only Phase21 validation APKs, confirmed no reverse remained and stopped owned
read-only emulator5584. The existing runner removed its separate physical-named
validation package even when an emulator check failed. No task listeners remained
on19621–19624/19631–19634/19821/55421/18420/19420/18763/5173. Per-run temporary
SQLite/CA/private-key files were cleaned by their harnesses. No live service,
normal app, system trust, Docker/application DB, VPN, firewall, DNS or account
was changed. No deployment/commit/later phase; G-41 and the listed target gates
remain explicitly open.

### 2026-10-16 — Phase22 password login and revocable sessions — fed5d4b working tree

Scope: only phase-22-password-login-and-sessions.md. Read repository/planning rules,
architecture/roadmap/current source, OpenAPI, migration/recovery and client/test
baselines first. Preserved the existing uncommitted Phase21 work (559file initial
snapshot). No application migration, password assignment, grant change, deployment,
VPN/firewall/system trust change, external message or Phase23+ implementation.

Checkpoints A–E implemented:

- A/B: additive0016 separates password_credentials from unchanged users/display
  names/token hashes. NFKC/casefold explicit identifiers reject collisions;
  existing accounts stay disabled. Local interactive UUID-based set-password uses
  hidden confirmation; login-accounts exposes safe authority/count metadata.
  Argon2id25.1.0/bindings26.1.0 pinned;64MiB/3iterations/4lanes, independent salts,
  two hash slots, dummy verification and rehash-on-success. Exact15–1024character
  passwords are supported without composition/truncation. Five public synthetic
  hash+verify pairs112.79–117.14ms, median114.76ms; not a load/peak-RSS measurement.
- C: digest-only opaque access/rotating refresh families,15minute/30day/7day default
  access/absolute/idle limits.128families/4096rotations bound history; expired and
  oldest revoked entries can be reclaimed. User locks serialize reuse/reset/
  rotation. Consumed refresh reuse revokes even a concurrent winner; lost delivery
  requires password sign-in, with no replay grace/secret escrow. Owned list/revoke,
  current/all logout and current-password change are implemented. Reset revokes
  password families; legacy/device credentials retain separate explicit policy.
- D: four exact login/refresh POST exceptions,8192byte/5second/16inflight pre-auth
  bounds,120global/30IP/10identifier attempts per60seconds,4096hashed rate keys
  and separate hash admission. No permanent account lock. The launcher ignores
  proxy headers, retains one worker/no access logs. Auth metadata/revocation stays
  available during content deletion. Fresh principal/epoch and SSE-batch fencing
  continue; X-ADA-Owner fences cookie account changes before browser decoding.
- E: Android normal username/password, password cleared after submit, access only
  in memory, rotating refresh in v12 Keystore storage; v1–v11/advanced bearer
  compatibility retained. Reopen/foreground renewal clears views, verifies the
  same owner/epoch and performs GET recovery only. Settings reviews/revokes
  sessions, changes password and logs out current/all. Short configurable access
  lifetimes use a bounded renewal margin, avoiding a one-second refresh loop.
  Browser uses exact configured HTTPS origin and Secure/HttpOnly/Strict host-only
  cookies, custom-header/Origin CSRF, no token JSON/JS credential persistence.
  Auth queue/Web Locks serialize renewal/cancel cleanup; response owner fencing
  prevents cross-tab cache mixing. Monitoring remains read-only except auth.

Data/contracts: head0016/57tables; encrypted backupv2 quarantines recovered password
and session authority. Frozen0015/v1 and separate0005 inventories/recovery remain
supported; current erasure still covers45content tables and discloses retained
security metadata. All132existing schemas and96existing paths compare unchanged
except their intentional cookie security alternative; additive current contract
is105paths/138schemas. Released migrations/prompts/other phase plans/native trust
files were checked unchanged. No new LLM capability, prompt upgrade or replay
rewrite. See [PASSWORD-LOGIN-AND-SESSIONS](../docs/PASSWORD-LOGIN-AND-SESSIONS.md).

Checks completed before final regression closeout:

- Baseline: selected schema/client/security pytest33passed/31skipped28.48s (PG URL
  not supplied); Ruff passed. An initial misspelled test path collected nothing
  and was corrected, not counted as a pass. Initial new failure suite could not
  import the not-yet-implemented password service, as expected before writes.
- All database verification uses migrated SQLite/disposable schemas/databases in
  owned loopback PostgreSQL18.6:55421/ada_phase2_test with matching native18tools.
  Initial pg_ctl omitted the cluster's port override and failed to bind; corrected
  to its owned55421 socket. No application/native5432 service was changed.
- Focused PG18/SQLite security/recovery/legacy/client suite81passed/2SQLite-lock
  skips153.67s. Expanded password, populated upgrade, schema0015backup/restore/
  upgrade and corrected contract checks24passed/1SQLite-lock skip39.11s. Security/
  stream/admin-HTTP follow-up107passed/3SQLite-lock skips197.03s. Later auth/contract/
  admin follow-up61passed/3skipped94.03s; corrected full-run failure cases4passed13s.
  Real PG refresh races, expiry/reuse/reset, SSE batch loss, generic disabled/
  absent failures, CSRF/mixed identities, bounded admission, hidden operator input,
  history-capacity recovery and wrong-owner fences are covered.
- Intermediate monolithic full pytest:777passed/25skipped/3failed1182.24s. Two
  failures were old bearer-only OpenAPI assertions. One SQLite HTTP fake chat
  returned503; isolated SQLite/PG reruns passed. The subprocess fixture inherited
  a background worker unlike its harness; it now explicitly disables unrelated
  workers. This is fixture determinism, not proof of a product/G-41 repair. Final
  current-tree full collection818cases/57modules was checked in three
  independent disposable-data groups; their exact results are appended below.
- Android final normal-ID units236passed/0failed/0skipped; lint/debug/instrumentation
  and unsigned-release builds passed42s/240tasks25executed. Latest separate
  validation-ID build and API37 emulator5584 passed password UI/Keystore/Activity/
  explicit renewal13.019s, then actual force-stop/relaunch/renew/logout-all5.655s.
  Earlier corrected stages passed7.403s/3.514s. No normal APK was installed; runner
  checks APK application IDs and accepts emulators only. No physical phone/audio.
- Fresh npm ci270installed/271audited/0findings; contracts/types/lint,67units/8files
  7.61s and production build passed. Final PG18-backed built Chromium6passed33.6s.
  Actual TLS Caddy + built browser passed ordinary password login, HttpOnly/host-
  only cookie behavior, missing-CSRF denial, automatic short-lifetime renewal,
  reopen/rotation, logout, non-admin denial, two-tab owner switch and password
  change. Browser fixture leaf trust is pinned in that Chromium process only;
  independent standard-CA TLS negatives cover trust rejection. No credentialed
  recordings, system trust installation or production TLS bypass.
- Both Phase21 direct TLS and two-proxy boundary rehearsals passed again: real
  migrated ADA/fake provider, six durable SSE events, cursor/completed replay,
  role/owner isolation, ignored network identity, built SPA, certificate negatives
  and stopped-upstream unavailability. These are loopback laboratories, not live
  LAN/Tailscale policy/renewal evidence. Python pip check and Ruff lint/format
 168files passed.19UTF-8 documents/222local links and3new-guide PowerShell examples
  passed (syntax only, no installation commands executed). Git whitespace passed.

Corrected failed development checks remain part of the record: Android version11
fixture expectations/fake logout calls and a missing instrumentation import;
Activity recreation incorrectly expected to rotate a retained ViewModel; an empty
password assertion accidentally included its field label. Tests now use explicit
renewal, real force-stop and editable-value semantics. Web legacy tests needed the
advanced toggle/exact label matching. A preflight fetch receiver error was fixed
with a bound transport closure; an account-change message was being overwritten
and now explains reauthentication. Earlier browser text assertions were updated
for password/session wording. These failed runs are not relabeled as passes.

Remaining/skip policy: completed full group results/cleanup are appended below.
No physical S24 FE/Android16, positive system-trusted release HTTPS, actual Wi-Fi/
VPN/firewall/DNS/certificate renewal, manual password-manager/assistive review,
other-browser or sustained auth/load/peak-memory check. Opt-in real-Ollama health/agent probes were not enabled; fixture inference is synthetic. Existing
G-06/G-29 network target and G-41 reliability/voice gates remain open. Live0016
installation, hidden-password enrollment and exact ADA_BROWSER_ORIGIN setup need
separate operator execution; no live credential/data change was made. Stop at22.


Phase22 final closeout: all818collected cases across57test modules were covered
once by three independent migrated SQLite/PG18 disposable-data runs:257passed/
15skipped426.09s;187passed/3skipped363.96s;349passed/7skipped556.37s. Aggregate
**793passed,25skipped,0failed**. The25skips are17SQLite native-row-lock cases
(whose PG variants ran),2opt-in non-generating Ollama health cases and6opt-in real
agent-model cases. No missing PostgreSQL/recovery-tool skips. The existing
Starlette/httpx deprecation warning remains. These results supersede the failed
intermediate monolithic run without erasing it.

Final review added3web account-switch race cases before fixing late password-change
acknowledgements/logout errors: all3initially failed, then passed after generation
fences. Fresh final web contracts/types/lint, **70units/8files10.14s** and production
build passed. Rebuilt-current-UI PG18 Chromium **6passed22.0s** and the actual TLS
password/cookie/CSRF/automatic-renewal/reopen/logout/two-tab/password-change drill
passed again after those guards. Previous6passed33.6s and failed wording/locator
checks remain dated development evidence. No recordings or real credentials.

The legacy Android token adapter now refuses password-mode refresh material; its
existing encrypted-store test verifies this boundary. Final normal-ID **236units/
0fail/0skip**, lint/debug/instrumentation/unsigned-release build passed **24s/
240tasks25executed**. Latest emulator password stages remain13.019s/5.655s, including
actual force-stop. Normal artifact packaging also passed8s/217tasks; the validation
runner's negative guard rejected normal-ID APKs before installation. Only separate
validation APKs were ever installed on the owned emulator.

Frozen recovery inventories were checked explicitly against current metadata:
0015has54tables,0016has57, owner erasure45. No released migration, prompt, other
phase or native trust-file change; old132schemas/96paths remain identical except
the selected cookie security alternative. Final static/document/whitespace checks
are recorded below. All task validation services are stopped: owned PG55421 path
validated before stopping, emulator5584 terminated, validation APKs/reverse removed,
zero disposable schemas/restore databases left, no task listeners on18422/19422/
18423/19822/19621–19624/19631–19634/18763/5173/55421. Per-run CA/private-key/SQLite
fixtures were removed by their runners. Native5432, Docker/application5433, live
accounts/configuration and system trust were untouched. No deployment/commit or
later phase. Live0016 enrollment/installation and the previously listed physical,
network/manual/load/model/G-41 target gates remain pending.

Final static closeout: 22UTF-8 documents/243local links passed;3guide PowerShell examples and start.ps1 parsed without execution. 57released migration/prompt/other-phase/native trust/client-lock-wrapper paths remain byte-identical to the initial snapshot. OpenAPI105paths/138schemas passes the old132schema/96path compatibility comparison, with only the selected cookie security alternative. Ruff lint/format168files and Git whitespace passed.


## 2026-10-16 — authorized Windows/Tailscale private setup follow-up

Scope: the user explicitly requested local environment/TLS setup after Phase22,
including dotenv corrections, editable device IP references and a detailed guide.
This is separate authorization from earlier phase implementation/no-deployment
runs. Source HEAD remains fed5d4b plus preserved existing and current worktree
changes; no commit, public publishing, unattended service or Phase23+ feature.

Implemented/operator actions:
- Corrected the private, Git-ignored dotenv: exact HTTPS ADA_BROWSER_ORIGIN,
  literal absolute forward-slash ADA_ADMIN_DIST and editable laptop/phone/iPad
  LAN/Tailscale address reference keys. These IP keys are metadata, not bind or
  authorization settings. Removed unused direct-LAN/manual-cert variables.
- Rotated the exposed PostgreSQL role password without printing/storing it in
  plans. Updated both private dotenv credentials, restricted its Windows ACL to
  the current user/SYSTEM/Administrators and recreated only the Compose db
  container on the same named volume to synchronize its initialization environment.
  Fresh password-authenticated connections and matching secret settings passed;
  all57application-table inventories were identical across the rotation. No
  reset, account token/role change, data migration or live backup was performed.
- Fresh live database observation was already PostgreSQL17.11/head0016/57tables.
  The fresh standalone alembic check exposed missing login_models registration
  in migrations/env.py. Added a failing subprocess regression before fixing the
  import. Existing migration files, tables/API contracts and prompts are unchanged;
  current/check/doctor subsequently pass without schema changes.
- Installed archive/executable-checksummed Caddy2.11.7 under LOCALAPPDATA/ADA/tools,
  added pinned manual install/start/check-only helpers and linked the detailed
  PRIVATE-SETUP-WINDOWS-TAILSCALE guide from README/HOW-TO/network/password guides.
  No blanket dotenv evaluation/import, service registration or proxy TLS bypass.
- Started one-worker/no-access-log/no-proxy-header API on127.0.0.1:8000 and Caddy
  on127.0.0.1:18764. Existing Serve443 maps the actual tailnet hostname to18764;
  status JSON contains no enabled AllowFunnel. PostgreSQL/Ollama remain local.
  Normal system TLS validation passed; TLS1.3 certificate expires2027-01-14UTC.
  No manual certificate/key creation, custom CA installation or firewall change.
- Phone SM-S721U1/Android16 was USB-visible with version15/0.22.0-sessions already
  installed; no APK install/uninstall or app-data reset. The user connected it to
  Tailscale and Android peer100.126.191.82 was observed online; iPad100.90.118.114
  also online. Device account/HTTPS/chat verification remains separately recorded.

Checks actually run:
- Initial fresh-process SQLite regression failed1case as expected; after the
  import correction, password/session + fresh Alembic tests on migrated SQLite
  and disposable real PostgreSQL17.11: **29passed/1skipped33.43s**. Skip is SQLite
  row-lock concurrency; the PostgreSQL variant ran. Exact owned test database
  removed; zero ada_setup_test_* databases remain. Existing Starlette/httpx
  deprecation warning remains. Live alembic current0016/check no drift, doctor
  and pip check passed. Ollama model listing confirms qwen3.8:27b, not inference.
- Built web contracts/types/production build passed; lint and **70units/8files
  7.56s** passed. Live system-trusted HTTPS readiness/admin200, unauthenticated
  private401 and root404 verified. Actual TLS Chromium loaded the built sign-in
  form and exercised synthetic password/non-admin denial with normal CA trust.
- Real Serve -> Caddy -> ADA -> livePG17 synthetic HTTP checks passed browser
  password/no-token-JSON/Secure/HttpOnly/Strict/host-only cookies, exact-origin/CSRF
  rejection, rotation/current-owner/logout/401; native password protocol passed
  rotation, old-access rejection and logout. Exact synthetic owners and their
  credential/session rows were removed in finally blocks; legitimate security
  audit metadata is retained. No private user chat/credential was recorded.
- Ruff lint/format245files, Git whitespace, both new helper PowerShell AST parses,
  valid proxy check-only and invalid-archive checksum refusal passed. The new
  guide's21PowerShell examples parsed and5local links resolved. Optional fresh
  installs/migrations/rotation/release/device commands are instructions, not all
  rerun checks. Existing lockfiles/native network trust remain unchanged.

Corrected failures: first rotation staging tried fsync on a read-only Windows
handle; PostgreSQL rolled back and dotenv stayed unchanged. Writable flush/fsync
retry succeeded. Initial proxy launch in inherited WindowsPowerShell5 failed
module lookup and HTTPS returned502; running the helper in PowerShell7 restored
18764/HTTPS200. The first synthetic CSRF probe omitted JSON Content-Type and was
rejected415 before the origin check; corrected valid-JSON probe got expected403.
No product permission weakening was made. User's first enrollment was rejected
for fewer than15characters; password login remained disabled and a hidden-prompt
retry was opened. Successful completion must be confirmed from metadata.

Remaining checks: real owner enrollment and browser/phone sign-in results are
appended when verified. Positive signed-release Android HTTPS, actual on-device
reopen/refresh/chat/SSE/cellular handover, iPad Safari, manual accessibility,
certificate renewal, sustained auth/load and physical voice/G-41 gates are not
closed by host checks. No full793-case suite or Android rebuild was repeated for
these helper/docs/metadata changes; the earlier Phase22 evidence is preserved.
Native17 recovery tools/live encrypted backup/restore remain an operator follow-up
(native18 is not the matching backup pair). No later phase or automatic startup.


Setup enrollment follow-up: the initial short-password rejection was corrected
by the operator's hidden-prompt retry. Local metadata now confirms the existing
admin owner is password-enabled with login `gourishankar-admin`; its UUID/grant
and the two other accounts are unchanged. The local success receipt is timestamped
2026-10-17T00:35:35Z (2026-10-16 America/Phoenix). No password was captured by the
agent. Real owner browser/phone use remains pending user results, distinct from
the already passed synthetic live HTTPS protocol/browser checks. Final document
check:9updatedUTF-8 files/111local links passed; Git whitespace and affected Ruff
lint/format passed after recording the guide/status changes.


Physical setup confirmation: the user reports the S24FE server readiness check
and ordinary password sign-in both work through the real Tailscale HTTPS origin.
This is current debug app15/0.22.0-sessions evidence, not a signed-release,
reopen/refresh/chat/SSE/cellular/voice test. The user's console confirms successful
hidden-password enrollment; agent metadata independently confirms password-enabled
`gourishankar-admin` on the existing granted owner. Browser opening was not an
enrollment side effect: a shell URL launch was rejected as blocked by policy and
the browser connector had no available Chrome. The user was given the exact
clickable HTTPS/admin URL for manual opening/sign-in; that result is pending.
Final scan found no current DB secret/URL in changed/untracked repository files;
standalone live alembic check and Git whitespace passed again.


Private setup closeout, 2026-10-16 America/Phoenix: the user confirms the laptop
admin dashboard opens after ordinary username/password sign-in, in addition to
the S24FE's successful real HTTPS readiness/password sign-in. Backend metadata
confirms active Android and Admin browser password families for the same existing
granted owner; all3original owners remain and schema is0016. Manual browser opening
resolved the unavailable automatic-launch path; no credential UI was automated.
Services remain running for use on loopback API8000/Caddy18764/Ollama11434, with
private Tailscale443. Enrollment and these two actual sign-in gates are now closed;
the earlier pending entries above retain their chronology. Guide reflects the
confirmed setup. No new model generation, physical reopen/refresh/SSE/cellular,
iPadSafari, signed-release HTTPS, voice, certificate renewal/load or live encrypted
recovery claim. No further phase implemented.


## Phase23 answer quality and memory relevance — 2026-10-16 America/Phoenix

Code: `fed5d4b` plus the existing Phase21/22/setup working tree and this bounded
Phase23 change. Required/root/plans/Android instructions, README/architecture,
current source/OpenAPI, head0016 and prior scorecards were inspected before
implementation. Relevant baseline: retrieval, quality baseline, hybrid evaluation,
learning and proposal tests **82passed/4expected SQLite skips (97.31s)**. Existing
claims/documents/entities/review/episodes/continuity and session adapters satisfied
prerequisites. No later phase or physical phone was needed.

| Checkpoint | Implemented behavior and decision |
|---|---|
| A | Frozen public16case corpus,8development/8regression holdout, fixture and32native v4/v5 answers. Separate context/ranking/generation findings, exact-source isolation checks and Codex qualitative usefulness/entailment/uncertainty review. |
| B | Existing lexical/subject/entity/exact-hybrid fixture comparison and fallback/budget tests rerun. Matching supported embeddinggemma weights absent: no native embedding/index/GPU claim, no download; semantic remains disabled. |
| C | Explicit IANA timezone/reference and versioned yesterday/previous Monday-week resolution; displayed half-open intervals, missing/folded-midnight clarification, current-recorded valid-time overlap. Complete claim-conflict groups or omission. Old point lookup unchanged. |
| D | Optional audited v5, ranked original history/authorized original continuity, frozen omission diagnostics and existing source/correction links. No automatic durable memory. Original retry/replay fences preserved; v4 remains default due measured regressions. |
| E | Exact loaded pending-annotation grouping and same/different-value conflict cues, retained exact support and every separate accept/edit/reject. No auto approval or automatic completed-turn selection. |

Data/contracts: no migration/dependency/new storage table. Head0016/57table model
is unchanged. OpenAPI109paths/143schemas; all105old paths and137old non-capability
schemas compared equal. Capabilities has three additive defaulted properties.
V3/v4 baseline bytes, historical migrations, old evaluation artifacts, later-phase
plans and locks/wrappers/release trust files match the turn-start snapshot
(68protected files). Existing PromptChange/trace storage holds v5 audit/frozen
metadata; old snapshots are never reconstructed. New chat, point retrieval,
CLI --at, source trust/citation and recovery contracts remain supported.

Checks actually run:

- Failure-first new API tests:3failed/1passed/4deselected for missing routes before
  implementation. Initial implemented target:2failed/6passed due a test-only
  wrong source-version field path, then corrected. Affected old/new retrieval,
  learning/storage/baseline group **61passed/2expected skips (70.87s)**; expanded
  Phase23 target **17passed (16.52s)** on SQLite/PostgreSQL. Full suite and the
  later three manifest/runner guards are recorded in the closeout below.
- Ruff lint passed; final Ruff format **177files passed**. An intermediate format
  check found one new runner signature; formatted and rechecked. `pip check`
  passed. `alembic heads` reports0016. No application migration command run.
- OpenAPI export and generated web types refreshed. Web typecheck/lint,
  **70unit tests/8files**, and production build passed. No admin runtime source
  change in Phase23; production Chromium suite not rerun for type-only changes.
- Android app16/0.23.0-quality: **239unit tests, zero failures/errors/skips**;
  lintDebug, assembleDebug, assembleDebugAndroidTest and unsigned assembleRelease
  passed. First compile found a new adapter's serializer-name typo; corrected
  before successful builds. No dependency/lock/wrapper/native TLS change.
- Separate dev.ada.validation.phase23.debug API37 emulator with real disposable
  PostgreSQL HTTP/session fixture: **1instrumentation flow passed (11.002s)**,
  covering displayed interval, two exact conflicting Unicode source cards,
  verified original source and explicit audited v5 upgrade/document compatibility.
  The first install attempt raced emulator boot and failed; after boot-complete,
  the full retry passed. Validation APKs/reverse/schema removed, emulator stopped;
  normal debug/instrumentation APKs rebuilt and metadata restored. Physical
  device/normal application data were not used or installed/reset.
- Public comparison runners: initial SQLite fixture32outputs; final PG fixture32
  and native Ollama32outputs. Initial two-recent-pair ranking still lost the
  relevant old turn under budget; corrected to one recent pair before the final
  fixture/native comparison. Corpus stayed frozen; this is regression holdout,
  not independent unseen data. Existing13query hybrid fixture comparison passed
  its integrity checks. Full raw synthetic reports are ignored local artifacts;
  committed manifest/results contain reproducible aggregate/per-case findings.
- Thirteen changed documentation files decoded UTF-8 and191local links resolved;
  six PowerShell example blocks parsed. Git whitespace passed. A policy digest
  audit initially compared policy-only hashes with assembled personality prompts;
  the corrected documented definition matches both final baseline policy texts.

Model evidence and measured decision: installed qwen3.8:27b digest
`aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813`
matched before/after native comparison. Recall was1.0 for both policies over5
positive development/4positive holdout cases; MRR0.9/1.0. Zero detected owner,
project or deleted-source leaks/exact-span failures. Codex review: fully useful
v4/v5 development8/8→6/8, holdout5/8→8/8. V5 restored the original long-history
turn (5542prompt bytes vs v4's5850, under6000) but used ambiguous exclusive-date
wording and exceeded brevity in development. Citation entailment counts actual
used labels, not merely available cards. **Not independent human review**;
small eight-case intervals overlap, one sample per version/case, host validation
load uncontrolled. Native median development4.272→4.716s, holdout3.482→3.922s;
first cold v4 request55.55s. No SLA or general accuracy claim.

Hybrid fixture:13queries, lexical recall/MRR0.4286/0.4286 vs exact hybrid1.0/0.7857,
zero integrity/isolation violations; eight5D vectors/448JSONbytes. Synthetic
vectors, Python allocations and warmed/cold timings are not native model/index
or GPU measurements. Supported embeddinggemma:300m digest absent; **semantic off**
is the chosen valid exit. V5 stays **explicitly opt-in**, v4 default unchanged.

Skipped/remaining target verification: native embedding/resource comparison
requires separately selected installed supported weights; no download authorized
or attempted. Independent reviewer/larger freshly versioned corpus and repeated
warm latency/working-set/GPU measurement remain. Address native date-boundary,
brevity and irrelevant lexical-hit findings before any default activation.
Windowv1 intentionally excludes document availability/historical alias
interpretation and is read-only, not a chat interval option. Private evaluation
was not opted into. No fresh physical S24FE, TalkBack/large-font/release HTTPS,
voice/G-41, network handover or live recovery/soak result is claimed. The previously
running Phase22 API/proxy, app database, sessions and physical app were left in
place; Phase23 has not been deployed. Phase24–31 remain planned.

Usage, reproducible commands and details:
[quality guide](../docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md),
[manifest](../evaluations/answer-quality-manifest-v1.json),
[reviewed results](../evaluations/answer-quality-results-v1.json).


Phase23 verification closeout, 2026-10-16 America/Phoenix:

- Full `python -m pytest -q -ra` against migrated SQLite and disposable
  PostgreSQL18.6: **816passed/25skipped (1058.84s),841collected cases**. The25skips
  are17SQLite row-lock cases (PostgreSQL counterparts ran), two opt-in generation-free
  Ollama health probes and six opt-in legacy native-agent probes. Those opt-ins
  were not enabled; the separate32answer Phase23 native run is distinct evidence.
  One existing Starlette/httpx TestClient deprecation warning remains; no blanket
  dependency update. Environment: ADA_TEST_DATABASE_URL selected only the dedicated
  loopback55421/ada_phase2_test fixture and ADA_TEST_PG_BIN selected native18.
- Later `pytest -q tests/test_quality_phase23_evaluation.py`: **3passed (0.17s)**,
  run separately after the full suite had collected. New bounds/conflict and
  active-upgrade tests were included in the full run. No claim that the later
  three were part of that841case invocation.
- Disposable fixture schema/restore-database inventory was empty after teardown.
  Validation18423 listener absent, emulator/reverse/separate APKs removed and
  owned55421 PostgreSQL stopped after verifying its workspace data path/port.
  Existing application DB/API/proxy/Ollama and phone were not redeployed/modified.
- Final source checks: Ruff lint/format177files, pip check, compatibility and
  protected-file/prompt audits passed. Documentation/contract closeout follows
  below if additional metadata checks are recorded. Earlier local failures,
  skips and remaining target/model limits above are preserved.


Final Phase23 metadata checks: `npm run contracts:check` passed;13updated UTF-8
documents/197local links resolved and six PowerShell example blocks parsed.
All49changed/new phase files were scanned against configured credential values
with zero matches (values were never printed). Final Ruff lint/format177files
passed. Repository-configured `git diff --check` passed. A diagnostic attempt
that overrode autocrlf=false falsely flagged existing Windows CRLF as trailing
whitespace; it made no file/config changes and was replaced with the normal
repository-configured check. No line-ending mass rewrite was performed.
Full-suite/fixture teardown left no disposable schemas or restore databases;
owned PostgreSQL55421 and the API37 emulator are stopped. Normal APK metadata is
app16/0.23.0-quality, with no installation. This completes Phase23's bounded
local exit; all skips, native regressions and remaining target checks above remain.

## Phase24 — secure public web research, 2026-10-17 America/Phoenix

Baseline: clean `9e06312`;594repository file hashes and109path/143schema OpenAPI
saved before changes. Required root/scoped rules, README/architecture/current
state/standards/workflow/status/roadmap, requested phase, migration/source/test
state were inspected first. Existing Phase12 approval/receipt, Phase18 owner
erasure/recovery and Phase20 readiness plus installed0016-compatible protocols
met independent prerequisites. Baseline agent/storage/failure/security/recovery
tests on SQLite/nativePG18.6: **105passed/2expectedSQLite-lock skips,156.72s**.
Failure-first new route check:1failed/1passed/2deselected before implementation.

Implemented A–E: default-off immutable secret-free Docker broker with actual
default-drop firewall, public DNS/peer/TLS checks, privilege drop/seccomp/read-only
proof and no inherited secrets/proxies/host mounts/socket. Closed Python docs/
Wikipedia URL and no-key Wikipedia REST search; exact owner query/URL/header/
recipient/expiry preview and per-call approval. Three total calls/run, zero
automatic redirects,1MiB identity-only body,32768codepoint extraction/truncation
flag,15s network I/O with separate bounded DNS/setup, two slots and10starts/minute.
No private context is automatically exported and no model output authorizes calls.

Research is a separate `ada-web-research-v1` protocol in existing AgentRun/Step/
Approval/Receipt rows, already in45owner-content/57backup-table inventory.
Owned immutable W text/hash/Unicode-span/trust/terms/freshness snapshots, snippets
distinct from pages, no-refetch completed replay, credential/epoch/generation
fences and local answer using shared inference admission. Explicit note save
creates imported-untrusted document evidence, never an endorsed personal claim.
Admin sees existing metadata/counts only. Android17/0.24.0-research adds exact
approvals/source verification/note/cancel controls and encrypted journalv13 with
v1–v12 reads, storage-before-POST and GET-only identity-bound recovery.

Contracts/protected state:117paths/156schemas; all109earlier path definitions and
142non-capability schemas exactly preserved, two optional capability
fields defaulting to `disabled` added. Old prompts/chat inputs/fingerprints/M/D/C/replay, all migrations,
dependency locks/wrappers and later phase files unchanged. No new schema/table,
host dependency, model download, API restart, normal app install or deployment.
Ignored local configuration contains the user-authorized public contact only;
research remains disabled and no broker manifest was activated in the service.

Actual local checks:

- Final affected backend/contract/recovery run: **70passed/1expectedSQLite-lock
  skip,58.26s**. A subsequent socket peer/SNI/no-second-DNS test separately
  passed1test/37deselected. A later config error-redaction regression is included
  in the fresh full run recorded at closeout. Tests cover ownership/protocol,
  exact nonce/expiry/unknown/crash, hostile URL/IP/MIME/encoding/HTML, source
  integrity/trust, revocation, shared capacity, transaction-free network/model,
  native PG concurrent one-fetch approval, erasure and encrypted populated restore.
- Docker Desktop Linux29.8.2: startup9/9forbidden targets denied; reachable private
  synthetic canary positive control then restricted10/10denied. UID65534,
  effective/bounding capabilities0, read-only, seccomp, no-private-env/host files
  passed. Final immutable image35a12c82880775b20d8f0fd9d022e2215e45e2e6f05ee2c237f544edecb70898;
  manifest/source hashes use forward slashes and canonical LF on Windows.
- Actual corrected public pilot: Python ZoneInfo fetch completed with15139
  extracted codepoints, Wikipedia Jupiter search returned3snippets; no truncation.
  Public receipts are not evidence of general browsing or third-party availability.
- Actual native integrated HTTP/PG/Docker source/answer/replay passed using installed
  qwen3.8:27b digest aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813.
  Exact saved hash/span verified, answer contained IANA andW1, no citation warnings,
  completed GET/answer replay equal. This one public marker-checked sample is not
  general accuracy/entailment/injection immunity. Its image6542306808d8fc02caffcdde1daaa2c1398e5b9002b44faacbb0441f7a4b3fab
  predates the final disclosure-wording rebuild; final image isolation was rerun
  separately. No claim the native model was rerun on every wording-only rebuild.
- Android **244unit tests**, lintDebug/debug/instrumentation/unsigned release
  builds passed; final normal build after network-deadline copy change also passed.
  Owned API37 emulator separate phase24APK over realHTTP/PG with explicit synthetic
  broker/model: stage1approval/Unicode source/answer7.489s; actual force-stop;
  stage2encrypted restore/GET-only/source3.691s, **two tests passed**. Validation
  APK/reverse/fixture removed, normal APK rebuilt. No physical phone was present.
- Web typecheck/lint/**70unit tests in8files**/production build passed; final
  `npm run contracts:check` passed. Only generated web types changed, so no new
  Chromium runtime suite was run. Ruff lint/format**191files**, pip check and
  repository-configured whitespace check passed. Metadata/cleanup closeout follows.

Development failures and corrections retained: initial API ownership lookup used
the wrong Conversation key shape (8failed/36passed), corrected to owner-filtered
lookup. A transient missing import caused20setup errors/36passed and was restored;
a test-only deletion-preview route mismatch caused2failed/54passed, then corrected
targets59passed/1skip. Android compilation caught a positional capability DTO
compatibility issue; new default fields moved to the end. One in-flight cancel
test needed explicit coroutine scheduling. The first emulator restore assertion
incorrectly treated a substring as exact text; corrected test then both stages
passed. Ruff formatting/noqa issues were corrected; final checks pass.

Privacy correction: the first public pilot sent the configured operator-contact
header to Python documentation as well as Wikipedia. This was reported to the
user and corrected. Python now receives a contact-free User-Agent; Wikipedia
alone receives the approved public contact. An independent worker guard rejects
contact-bearing Python requests before connect. Regression checks and corrected
actual public fetch/search passed. No contact value is stored in these records.

Initial broad run was started before the export/header-fixture edits were frozen:
**872passed/6failed/26skipped,1124.10s**. Two stale contract assertions and four
old-collected header fixtures failed against newly changed files. Fresh contract
module5passed and fresh affected suite70passed/1skip. A clean full-suite rerun
against frozen behavior was started; its actual result is appended below, rather
than relabelling the earlier invocation as green.

Remaining/explicit skips: installation-host verification/restart/activation not
performed; feature stays disabled. Physical S24FE/Android16, TalkBack/large-font,
signed-release HTTPS/network handover, broader native hostile-source/answer quality,
sustained resources/daemon-failure/soak and earlier voice/G-41 remain target gates.
No private research dataset, general-site/IPv6 transport/compressed-body expansion,
provider key/purchase, live DB migration/backup/erasure or later phase was run.
The runbook is [SECURE-WEB-RESEARCH](../docs/SECURE-WEB-RESEARCH.md).

Final adapter review follow-up: a stalled Docker stdout read could outlive the
container-removal timer. New failure-first test failed1test/39deselected, then
the host adapter switched to a23s communicate deadline with bounded best-effort
removal and CLI cleanup. Cleanup failure cannot hide the unknown outcome or
skip CLI termination; no request retry. Policy/worker/image bytes were unchanged.
Fresh policy suite **40passed (0.10s)**; fresh combined policy/research/native
recovery/contracts **73passed/1expectedSQLite-lock skip (53.99s)**. Actual final
image isolation/private-canary and corrected public Python15139codepoints/
Wikipedia3snippets passed again after the adapter change. The broad run below
had already imported the earlier adapter and excludes this last new test; this
follow-up is distinct fresh evidence for the final adapter, not an inflated
full-suite count. A transient development failure had included the public contact
in one ignored test log; it was redacted, and subsequent configured-secret/contact
scan passed. No configured database password was found in those artifacts.

Final provenance follow-up: unfinished research now rejects a changed provider
ID/model instead of recording an answer under stale creation metadata. Completed
replay remains original. Failure-first2SQLite failures/2PGskips/26deselected (that
invocation had no PG URL); after the guard, fresh combined affected suite on
SQLite/nativePG18 **77passed/1expectedSQLite-lock skip (57.57s)**, including all
four provider/model drift cases and final Docker deadline test. The broad run
below predates these five final cases/host guards; its separate count is preserved.

### Phase24 broad regression and final broker proof

Fresh broad `python -m pytest -q -ra` on migrated SQLite and disposable native
PostgreSQL18.6: **886passed/26skipped,1082.68s (18m02s),912cases**. The26skips are
18SQLite row-lock cases (PG counterparts ran), two opt-in generation-free Ollama
health probes and six opt-in legacy native-agent probes. Those opt-ins were not
enabled; the separate real public research/native-model pilot is distinct evidence.
One existing Starlette/httpx TestClient deprecation warning remains; dependencies
were not upgraded. This is a new successful invocation, not a rewrite of the
earlier872passed/6failed run. Final targeted follow-ups are distinct as noted above.

Final read-only proof improvement: the old `/broker` write attempt could fail
from UID permissions alone. Startup now writes a synthetic probe in world-writable
`/tmp` and requires EROFS, rejecting EACCES. Failure-first2failed/40deselected;
fresh policy **42passed (0.11s)**. Rebuilt final immutable image
d494abd80498712e64dcdfeb6fd4560751ab2d4ff5526552d7d6227b4a3f725a:
actual EROFS/read-only, UID65534/caps0/seccomp/noenv/nohostfiles, startup9/9denied,
positive private-canary then10/10restricteddenied all passed. Public Python15139
codepoints/Wikipedia3snippets completed again, no truncation. Earlier image/native
reports retain their original IDs; the native answer was not rerun for this
self-test-only worker change. These two proof cases also postdate broad collection.
The final combined affected run and cleanup results follow.

### Phase24 final closeout

- Final combined policy/research/PG recovery/contracts on final source:
  **79passed/1expectedSQLite-lock skip (49.00s)**. This includes the seven cases
  added after broad collection: Docker wait1, provider/model drift4, EROFS proof2.
  No failures remain in these final invocations. Earlier failed checks and their
  narrower provenance above are retained.
- Ruff lint/format191files, pip check, web contract freshness and normal Git
  whitespace checks passed. Final compatibility/protected audit preserved139
  files,109old paths and142non-capability schemas. All51changed/new repository
  files scanned against configured credentials/contact with zero matches.
  Thirteen UTF-8 documents/205local links resolved;10PowerShell examples parsed.
  Current broker manifest uses canonical LF hashes/forward-slash paths and matches
  the final image source. Ignored validation artifacts were also scanned after
  contact-log redaction; no configured credentials/contact remain there.
- Cleanup found10empty fixture schemas left before migration by the earlier
  setup-error run. Verified the dedicated55421/ada_phase2_test database, fixture
  role/UUID names and zero relations/routines/types, then dropped only those empty
  namespaces with RESTRICT. Final all-non-system schema and disposable restore/
  recovery database inventories were empty. Owned nativePG55421 stopped after
  verifying workspace data path/loopback port. No application database accessed.
- Owned emulator5584 stopped; validation APK/reverse absent before stopping,
  fixture18423 listener absent, no `ada-web-` containers remain. Normal debug APK
  metadata is dev.ada.assistant.debug/version17/0.24.0-research; no normal install.
  Docker engine/unrelated containers and Ollama/private API/proxy left untouched.
- Local ignored configuration freshly verified: research disabled, broker manifest
  unset, public contact present as authorized. No deployment/activation/migration
  or later phase. A–E's bounded local exit is complete; all physical, installation-
  host, larger quality/soak and earlier voice/G-41 limits above remain open.

## 2026-10-17 — Phase25 conversational curiosity — local implementation

Code: HEAD9e06312 plus preserved uncommitted Phase24 and this Phase25 work.
Read root/client rules, required current-state/architecture/roadmap/workflow,
requested plan, source, migration/recovery inventory and117path OpenAPI first.
Existing Phase11 review,14/15 explicit expression/continuity and23 relevance
paths were present; relevant baseline **89passed/3expected SQLite-lock skips**
on SQLite/nativePG18.6. Planning did not authorize any later feature. Existing
release/physical/voice/G-41 gates remain open rather than being prerequisites
silently marked complete.

Implemented A–E:

- Default-off owner-global topic/depth/channel/frequency settings, per-topic
  pause/block and global off. One optional companion per eligible completed reply;
  concise/task-focused or already-questioning replies suppress it. Owner-wide
  two normal inbox drafts/day and ten explicitly requested interviews/day (UTC).
- Bounded versioned catalogue:30generic templates/five exact-source variants.
  Broad task topic or explicit topic/original-source choice, uncertain source
  wording, inspectable Unicode/hash spans, source owner/scope/time/current-support
  checks. No inferred intimate premise, hidden profile or new inference worker.
- Private inbox, reason/policy/expiry/dedup snapshots, skip/not-now/dismiss/
  permanent suppression/pause/feedback. Exact opening creates a real owned
  conversation without a user event. Explicit typed answers use ordinary chat
  outside transactions; no automatic claim, preference, document or memory search.
- Answer intents bind conversation and ordinary request fingerprint. Durable
  rejected pre-admission receipts permit reviewed new answers; unknown/failed
  requests retain exact recovery keys. Completed replay/bookkeeping reconciliation
  never generates twice or adopts an unrelated UUID collision. Android validates
  Unicode length, persists encrypted intents first, prevents duplicate answers,
  restores using GET only and fences owner/epoch/scope/late logout callbacks.
- New0017 only:60tables/48private-content inventory. Backup-v3/0017 verifies exact
  original rows before disabling restored curiosity and quarantining credentials;
  older0015/v1 and0016/v2 recovery remains supported. Dismissed text/pins scrubbed,
  minimal dedup30days then lazy cleanup; permanent suppressions/receipts until
  explicit owner erasure. Server/client bounds reserve final global-off capacity.
- OpenAPI126paths/168schemas, nine new paths/eleven methods/twelve schemas.
  All117old paths/155non-capability schemas unchanged; two optional capabilities
  added. Android18/0.25.0-curiosity, encrypted journalv14 retains v1–v13 reads.
  Admin remains unchanged/metadata-only. Notifications=false; no scheduler/push.

Checks actually run (separate invocations, not combined counts):

- Expanded affected backend after fixes: **105passed/2expected SQLite-lock skips**
  (187.17s). **Full pytest:930passed/27skipped** (1283.97s;957cases) on migrated
  SQLite/nativePG18.6. Skips:19SQLite-lock variants whose PG counterparts ran,
  two opt-in generation-free Ollama health probes, six opt-in legacy native-agent
  probes. Existing Starlette/httpx TestClient deprecation warning remains.
- Full collection predates twelve later failure-path cases. Answer-reservation curiosity/
  storage: **47passed/1expected SQLite quota-lock skip** (99.55s), including owner
  quota concurrency, opt-out/revocation during answer generation, failed exact
  retry without an open DB transaction, UTF-8 budget rejection/UUID collision,
  populated upgrade/downgrade/Alembic drift, erasure and native0016/0017 recovery.
- Android JDK21.0.12/API37 emulator: **254unit tests**, lint, debug/instrumentation
  APKs and unsigned release built successfully. Exact journal/storage failure,
  restore GET-only, off alongside unknown delivery/quota cooldown, late callbacks,
  answer receipt recovery and oversized Unicode input covered. No normal install.
- Separate validation APK used real HTTP/PostgreSQL/password/Keystore with an
  explicit FakeProvider. Two earlier complete emulator force-stop invocations
  passed (9.460s/4.585s and8.765s/4.935s); final answer-reservation flow passed
  (8.167s/4.103s). Latest post-input-guard refresh/cleanup is recorded below.
  A retained exact action after its real API write simulated a lost acknowledgement;
  process-stop restore read its receipt without another user statement/POST.
- Frozen public6development+3holdout corpus passed, including exact original,
  permissions, stale premise, task topic, repetition and synthetic feedback.
  Fresh final `evaluate_curiosity.py --native` passed nine cases plus one installed
  qwen3.8:27b answer/completed replay (model digest in aggregate report). Codex
  inspected the public sample: on-topic single question, no invented personal
  premise. Earlier native run also passed; neither is an owner helpfulness rating,
  independent premise-quality study, SLA or general model-quality result.
- Web contracts generation/freshness, TypeScript, lint, **70unit tests** and
  production build passed. No new browser runtime suite was run: web changes are
  generated contract/capability additions, with no curiosity admin UI.
- Ruff lint/format200files, pip check and Git whitespace passed. Contract/source,
  configured-secret/contact, UTF-8/link/PowerShell and cleanup audits below.

Corrected failed checks are preserved in WORKLOG: route/epoch/crash recovery,
primary-question suppression, restore consent, lower downgrade preflight, test
clock, reserved-off capacity/cooldown, pre-admission rejection/UUID collision and
Android Unicode input. Emulator setup first rejected a split PowerShell Gradle
property, then an explicitly unsuitable provider fixture, then exposed refresh
timing intermittency. Later passes do not close the existing G-41 reliability gate.

Remaining target verification: authorized installation/migration0017 and app18,
physical S24FE/Android16, TalkBack/large-font, signed HTTPS/private-network handover,
longer performance/soak and independent question relevance/premise/helpfulness
review with actual owner ratings. Earlier voice/G-41 limits remain. No physical
notification test applies until a later separately selected delivery phase.
See [usage/runbook](../docs/CONVERSATIONAL-CURIOSITY.md). Phase26–31 remain planned;
no deployment, live database operation, notification or feature activation.

Phase25 closeout: final post-input-guard emulator stages **6.809s/3.107s passed**;
254unit/0failure/0skip XML totals verified. Normal debug/instrumentation APKs
rebuilt as dev.ada.assistant.debug/version18/0.25.0-curiosity without installation.
Compared615-file pre-phase snapshot:56changed/new phase-scoped files, no deletions;
39explicitly protected files unchanged (all0001–0016 migration bytes, old prompts,
locks/wrappers, later plans and Phase24 research/broker source). All117old API
paths/155non-capability schemas exact; only two additive capability fields.
Fifteen UTF-8 documents/263local links resolved;69PowerShell blocks parsed.
Configured credential/contact scan of changed files and ignored Phase25 artifacts
found zero matches. Final whitespace and contract freshness checks passed.

Cleanup: owned55421/dedicated test database had no fixture schemas, empty public
schema and no restore/recovery fixture databases (only postgres/ada_phase2_test).
Stopped only that nativePG instance after resolved workspace datadir/loopback-port
checks. Separate validation APKs/reverse absent before stopping owned emulator5584;
fixture18423 listener absent. No normal phone/app install or app DB change. Native
Ollama, Docker/unrelated services, private API and proxy were left untouched.
Bounded A–E source/local exit complete; target/quality/reliability limits remain.

Final crash-edge follow-up: simulated process stop after a conflicting ordinary
request but before rejection bookkeeping initially failed1SQLite case/1PG-not-set
skip. A GET now returns `reconcile_required` until explicit exact replay commits
the rejection and reopens the question. This prevents premature journal removal;
it never adopts the unrelated request. Fresh final curiosity/storage run with
nativePG: **49passed/1expected SQLite quota-lock skip74.05s**. This includes all
twelve post-full-collection cases; the earlier930/27 and47/1 runs retain their
own provenance. Android/native public-model evidence predates this read-state-only
edge fix, with no client, schema, prompt or inference-path changes. OwnedPG was
restarted only for this disposable rerun, then re-inventoried/stopped again.

## 2026-10-17 — private proxy launcher quoting fix

HEAD844d560 plus this fix. Reproduced the reported Python SyntaxError using
Windows PowerShell5.1 with `start-private-proxy.ps1 -CheckOnly`. Pass the existing
Python dotenv reader through standard input instead of a quoted `-c` argument.
No dotenv evaluation, configuration, dependency or proxy behavior change.
CheckOnly now reports Valid configuration in Windows PowerShell5.1 and
PowerShell7.6.6. Targeted schema/contract pytest3passed (existing TestClient
deprecation warning); Ruff lint/format200files and whitespace passed. Existing
Caddy formatting warning remains nonblocking. Full backend/nativePG/client suites
not rerun for this launcher-only fix. No proxy started, deployment or DB operation.

## 2026-10-18 — Android Ambient Intelligence UI redesign

Scope: only [the requested UI plan](ADA-Android-UI-Redesign.md), HEAD844d560 plus
the preserved uncommitted proxy fix and this work. Audited actual Compose/Material3,
single Activity/navigation, state/controllers, HTTP/Keystore, voice, screens,
accessibility/insets, SDK/dependencies/OpenAPI/tests before broad UI changes.
Shared theme/primitives were built/tested before chat rollout, then feature views.
See [audit/design/files/usage](../docs/ANDROID-UI-REDESIGN.md).

Implemented app19/0.25.1-ambient:

- Dark-first violet Ambient identity for fresh installs; all saved legacy palette
  and mode keys/choices preserved. Four palettes/light mode, scaled native sans
  typography, shared geometry/spacing, restrained atmospheric/vector depth and
  selective glass. No new SDK, dependency, font, permission or bitmap asset.
- AdaPresence derives listening/processing/speaking/task/error/offline/unconfirmed
  state from current UI data. No invented amplitude, hidden activity or emotion.
  Text/semantics accompany color; motion respects lifecycle, viewport and system
  animator setting. Unknown delivery is never presented as confirmed inference.
- New sign-in/home hierarchy, quiet unboxed assistant replies, tinted owner
  messages, elevated keyboard-anchored composer and shared feature headings.
  Context scrolls; action shortcuts remain pinned in normal-height chats and
  scroll in very short windows. Same four destinations use compact navigation or
  a scrollable expanded rail; forms/reading have bounded width.
- Voice remains the existing permission/review/playback panel with state visuals.
  Proposal/research/curiosity collect lifecycle-aware state. All existing owners,
  capabilities, approvals, sources, retries, controller/data/audio implementations,
  journal keys/versions, request snapshots and API contracts remain unchanged.
  MainActivity keeps FLAG_SECURE and its existing audio/auth lifecycle handlers.

Checks actually run (separate invocations, not combined full-suite claims):

- Baseline Android254units/lint/debug/instrumentation builds passed. Initial new
  palette check failed1of257units; fixed low-contrast violet roles. Theme stage
 258units/lint/debug passed; chat stage258units/lint/debug/instrumentation passed.
  Final normal unit/lint/debug/androidTest/unsigned-release checks recorded below.
- Backend contract baseline6passed/2PG-not-configured skips14.00s; nativePG18.6
  rerun **8passed32.76s**, with only existing TestClient deprecation warning.
  No server or schema changes; full backend/web suites not repeated.
- API37 emulator, separate validation APK, real HTTP/PG/password/Keystore with
  explicit FakeProvider: latest portrait2stages, rotated landscape1, expanded1,
  MainActivity foundation1, curiosity recovery2 and password recovery2 all passed
  (nine selected stages across six runs). Full connected suite was not run.
  Actual durations/current artifact closeout are recorded below/WORKLOG.
- Portrait covers rendered dark/light heading ink, all eight presence semantics,
  ordinary UI style/conversation creation, multiline/emoji input, focus, IME
  anchoring, touch Send, streamed reply and same-request source navigation.
  Gesture navigation1080x2400/density420. Actual rotated landscape2400x1080,
  three-button navigation and1.3font scale passed13.399s. Extremely short viewport
  retains scrollable composer controls. Expanded2560x1800/density320/font1.6
  passed9.894s after completed build, with rail navigation and focused typing.
- Native MainActivity foundation passed10.291s with system animator disabled:
  all palettes, saved mode/palette recreation, status/navigation icon flags and
  FLAG_SECURE. Curiosity force-stop stages7.795s/4.595s; password renewal/force-stop/
  revocation7.487s/3.568s. No duplicate user statement after curiosity restoration.
- Earlier visual runs caught inherited black text through transparent containers;
  fixed explicit root content colors and added rendered-ink assertion. Test setup
  initially assumed a saved style; the disposable account required UI style
  creation. IME animation synchronization fixed missed test taps. Missing public
  image handling fixed a collector decoding error. Recovery exposed virtualized
  shortcut access, fixed by pinning normal-height actions. Initial artificial
  landscape size override left no app viewport under IME; actual rotation rerun
  passed. Failed/earlier runs remain in WORKLOG, not relabelled as passes.
- Public test-host images visually reviewed for dark/light, chat, typing and
  expanded layout. They capture the app surface, not the separate IME window;
  production secure-window policy was never disabled. No private account/content.
  Ruff lint/format201files, whitespace, protected-file/credential/link audits below.

Remaining verification: physical S24FE/Android16, manual TalkBack, physical IME/
keyboard variants, foldable live-resize, graphics/battery/long-scroll performance,
and inherited voice/focus/G-41 gates. Emulator checks do not close these. No native
model/audio inference was needed for this presentation change. No normal app
installation, application DB migration/write, deployment or later-phase work.

UI closeout: final normal `testDebugUnitTest lintDebug assembleDebug
assembleDebugAndroidTest assembleRelease` passed1m19s; XML258tests/0failures/
0errors/0skips. Debug ID dev.ada.assistant.debug/app19/0.25.1-ambient and unsigned
release artifact verified. Latest portrait stages10.570s/3.418s passed after the
action-row change; earlier17.8s/7.191s remains its prior invocation.
Against633pre-task files,29changed/new UI/docs/test files, no deletions;
391protected files unchanged, including entire backend/contracts, client data/
audio/controllers/ViewModels, migrations, locks/wrappers, later phase plans and
the preexisting proxy fix. OpenAPI remains byte-identical126paths/168schemas.
Ruff lint/format201files, pip check, whitespace,8UTF-8 docs/133local links and
15PowerShell blocks passed. Changed files/ignored non-image validation artifacts
scanned with zero configured credential/contact matches.

Cleanup verified: separate APKs/reverse absent; owned emulator restored to
1080x2400/density420/font1.0/gesture navigation/free rotation/unset animator scale,
then stopped. TestPG had only public0relations and postgres/ada_phase2_test, no
fixture schemas/restore databases; stopped owned55421 after workspace datadir/
loopback-option checks.55421/18423 listeners absent. No normal app install, live
database operation or service/proxy/Docker/Ollama change. Target limits above stay
open; no later-phase implementation or deployment.


## 2026-10-18 — Compact Android chat refinement

Scope: the user's screenshot-driven follow-up to ADA-Android-UI-Redesign.md;
HEAD844d560 plus the preserved proxy fix/first redesign and this refinement.
Reviewed rules, current Compose/state/controllers, OpenAPI0017/126paths/168schemas
and test baseline. No server contracts, data/audio/controllers/ViewModels,
Keystore journals, prompt/source snapshots, dependencies or migrations changed.

Implemented in the existing app19/0.25.1-ambient presentation:

- Compact conversation Back/title/overflow header replaces the permanent feature
  toolbar. Research, curiosity, tools, episodes, context/upgrades, refresh and
  Settings stay capability-gated and available on demand.
- One composer row contains paperclip/Add, editable text, microphone and Send;
  an owned active stream changes Send to Stop. Add opens separate options or the
  existing document imports. Imports still require explicit owned scope and text/
  Markdown review; there is no message attachment contract or arbitrary file claim.
- Options/context/voice use scrollable native dialogs. Memory/document/time guards,
  frozen pending options and explicit ASR approval remain. Capture prevents
  accidental dialog dismissal; closing a draft does not approve/send/discard it.
- Provisional replies/recovery now scroll in the thread. Stop remains reachable
  while reading earlier messages; check/retry keep exact keys. Near-limit/error
  counts replace the permanent empty counter. Short windows use an internally
  scrolling one-line editor; normal windows retain multiline entry. Native48dp
  labelled vector controls, theme roles and saved palettes remain.
- Smaller home hierarchy and concise scope/style metadata remove duplicate rows.
  Backend/audio/provider behavior and secure-window policy remain intact.

Checks actually run so far (final closeout below): initial units/lint/debug1m33s,
core units/lint/debug/androidTest36s, separate validation builds passed. Contract
baseline6passed/2PG-not-configured skips15.35s; nativePG18.6 rerun8passed24.73s.
Existing Starlette/httpx deprecation remains. Portrait real HTTP/PG/password/
Keystore21.866s/4.880s; final portrait22.324s/4.153s. Tests exercise collapsed and
capability-gated menus,48dp row geometry, options roundtrip without sending,
voice open/close, document import navigation, multiline/emoji/IME and original
reply sources. Curiosity force-stop recovery9.956s/6.145s passed.

Separate synthetic SQLite HTTP/native-window tests: streaming Stop/detach/exact
cancelled retry16.503s and voice review/approval/lineage/independent playback12.170s,
denial/background/encrypted recovery6.885s passed. Drivers are synthetic, not
physical microphone/speaker validation. Idle consolidation was disabled only in
that ignored fixture environment after a capacity race (below).

Expanded2560x1800/density320/font1.6 rail+typing15.842s passed. Landscape iterations
and final build/normal artifact/foundation results are recorded in closeout below;
initial captures required further visual investigation, not a blanket UI pass.

Corrections preserved: initial visual12.300s failed because the test expected
unadvertised tools; gate expectations now match capabilities. Returning from
imports failed28.225s, then32.861s with Unreachable metadata after a long dialog
review. Test-only admin helper now keeps idle sockets90s like the dedicated client
fixture; no production retry/network policy changed. Stream fixture25.413s saw
Busy then Missing before reservation. A forced disposable reproduction proved
idle consolidation can occupy its shared slot (503 then same-key404); no server
change. Worker-disabled fixture rerun passed. Intermediate landscape capture
clipping prompted the short-window editor and stricter touch-height assertions.
An additional labelled landscape invocation actually captured portrait; it is
not landscape evidence. Collector now checks landscape PNG dimensions. Earlier
runs/logs are retained under ignored .pytest_cache/ui-compact.

Ruff initially requested one formatting change in the collector; fixed, lint and
format282files passed, pip check and whitespace passed. Full backend/web/connected
suites, native model inference, physical S24FE, manual TalkBack/keyboard variants,
foldable live resize, performance/battery and inherited voice/focus/G-41 gates
remain separate. No normal app installation, application DB write/migration,
private-service change, later phase or deployment.


Compact UI closeout: final normal `testDebugUnitTest lintDebug assembleDebug
assembleDebugAndroidTest assembleRelease` passed53s;258units/0failures/0errors/
0skips. Android lint0errors/23existing warnings (dependency/localization notices);
no framework upgrade. Normal debug metadata dev.ada.assistant.debug/app19/
0.25.1-ambient and unsigned release verified. Password renewal/force-stop/revocation
stages8.921s/4.018s and native secure-window/palettes/system-bar foundation15.570s
passed. No full connected suite claim; other updated feature tests were compiled.

Final real landscape2400x1080/font1.3/three-button run24.455s passed with full48dp
focused control geometry, touch Send and source checks. OS fixed-to-user rotation
was needed to keep emulator orientation consistent; final PNG dimensions checked.
Earlier24.415s was actually portrait,25.512s was landscape; a subsequent25.514s
instrumentation pass was rejected by collector for portrait dimensions. They are
not substituted for the final configured result. Compose layer screenshots looked
cropped in the rotated window even when semantic controls were visible. Added
public-test-host-only UiAutomation keyboard/window capture: actual full-system
image confirms the entire compact one-line composer above the large OS keyboard.
Normal portrait remains multiline. MainActivity FLAG_SECURE was never disabled.
The new system-window capture is separate from earlier app-surface-only evidence.

Final protected-file audit against638pre-refinement files:21changed/new, no
deletions,391protected unchanged (backend/OpenAPI/client data/audio/controllers/
ViewModels/journals/migrations/locks/later phases/preexisting proxy fix). OpenAPI
byte-identical126paths/168schemas. FourUTF-8 docs/36local links; configured-secret/
contact scan zero matches. Final Ruff/pip/whitespace and cleanup recorded below.


Final cleanup/checks: Ruff lint/format282files, pip check, whitespace and protected/
credential/link audit passed after closeout edits. No fixture schemas/public
relations remained on owned PG55421; stopped it after workspace/loopback checks.
Separate validation packages/reverses absent. Emulator restored1080x2400/density420/
font1.0/gesture navigation/free rotation/default rotation policy/unset animator
scale, then stopped. Test ports55421/18423/18424/18425 absent. Preexisting normal
emulator apps were left untouched. Private services and application DB unchanged.


## 2026-10-18 — Android design-gap verification and hardening (app20)

Requested scope: verify `docs/ANDROID-DESIGN-GAPS.md` and fix genuine Android
presentation gaps. Baseline HEAD `b2a383e`; the user report was the only initial
untracked file. Read root/Android rules, README/architecture/current state and
planning workflow/status; inspected current UI, released OpenAPI and test state
before changes. Original report is preserved byte-for-byte beneath an inserted
banner and appended [verified disposition matrix](../docs/ANDROID-DESIGN-GAPS.md#8-verified-follow-up-2026-10-18).
The user requested automated checks only; no manual TalkBack/audio result is claimed.

Implemented app20/0.25.2-ui: shared readable live feedback and labelled loading,
merged selected/checked choices, explicit48dp button layout, destructive-action
review with safe initial keyboard focus, available-height chat dialogs, grouped
settings, readable status/preference/job/date copy and technical details. Added
Follow system appearance/Reduce ambient motion without changing old explicit
choices, dual swatches, adaptive/monochrome icons and mode-aware launch resources.
Navigation uses the shared icon family/600dp rail; compact Docs label avoids
large-font fragmentation while retaining Documents semantics. Streaming preserves
an older reading position and offers Latest message. Back hides the keyboard
before leaving chat. Literal fenced-code spans/explicit safe inline links retain
text/source fidelity. Server removal/rotation/erasure and voice-draft discard
require review; active recording discard remains immediate. Token Copy is explicit
and marks the clipboard sensitive; tests did not overwrite the user's clipboard.

Report corrections: Curiosity already renders controller errors through notice
and has no fault field; Tools really omitted its fault. Native LazyColumn already
supplies collection semantics, and native dialogs provide modal containment.
Material expands touch regions, but phone tests measured40dp of button layout;
shared buttons now reserve48dp. Decorative glass edges are distinct from the
functional composer boundary, which now uses the opaque outline. Distinct
provenance cards/captions, system font scaling, explicit Refresh, durable notices
and immediate destination changes remain intentional. No generic card framework,
blanket dp lint ban, Snackbar requirement or automatic appearance migration.

Checks actually run (each invocation retains its own evidence, not cumulative totals):

- Baseline Gradle units/lint/debug passed20s,258units. Baseline contract/schema
  pytest6passed/2PG-unconfigured skips12.26s; dedicated nativePG18.6 rerun8passed
  21.98s. Final focused nativePG/installer guards:12passed21.52s. An initial final
  command used nonexistent test filenames, so no tests ran; corrected invocation
  uses test_android_validation_guards.py/test_client_contract.py/test_schema_contract.py.
  Existing Starlette/httpx deprecation remains.
- S24FE SM-S721U1/Android16/API36, physical1080x2340/density450/gesture navigation:
  separate dev.ada.validation.designgaps.debug only; actual local authenticated
  HTTP/password/Keystore/disposable PostgreSQL, explicit fake provider/research/
  audio drivers and public synthetic data. MainActivity secure window retained.
- Native semantics/loading/48dp/Cancel Enter/explicit safe-link activation4.934s
  passed. Earlier1.802s detected native40dp layout;2.304s detected Cancel focus
  requested before the dialog window was focused. Both fixed and retested.
- Primary-screen Ambient dark20.140s/light20.480s and portrait dialogs9.716s
  passed. At system font1.6, dark27.159s/light26.074s, dialogs11.646s and keyboard
  Back/multiline-emoji draft9.915s passed. Visual review found Documents wrapping
  into fragments; compact label corrected. Final large-font dark21.421s passed
  with exact frozen M1 source card. One0.907s repeat correctly rejected a reset
  font configuration before testing UI; reapplying1.6 produced that final pass.
- Actual physical landscape2340x1080/font1.3: primary screens/source/safe
  confirmations21.324s, bounded details/options9.950s and keyboard Back/draft8.107s
  passed. Initial0.815s invocation rejected portrait configuration. The isolated
  test activity now explicitly requests landscape and checks actual dimensions;
  no claimed landscape pass depends only on a shell rotation command.
- Reviewed HTTP feature regressions on the phone passed: entities/merge/undo
  9.517s; exact document upload4.900s; proposal source/edit/accept/reject8.119s;
  streaming/Stop/detach/exact retry plus older-reading position13.002s; security
  device rotation/revocation/reviewed erasure7.289s (disposable owner only).
- Synthetic voice review/approval/lineage/independent playback7.606s and
  denial/background/encrypted recovery3.093s passed. Added draft-discard review
  3.738s proves Cancel preserves encrypted draft and Confirm clears it without
  chat submission. These exercise UI/controller invariants, not real ASR/TTS.
- Expression4.949s, approved/denied calculator5.760s, reviewed learning6.822s,
  Curiosity actual process-stop recovery5.186s+3.134s and synthetic research
  approval/source/recovery6.089s+1.852s passed. Expression's first11.225s failure
  used the emulator-only origin; test now accepts explicit fixture origin while
  preserving its old fallback. Learning's old raw-label expectation failed;
  corrected to human-readable labels, preserving API-value assertions.
- Real MainActivity secure-window/all palettes/saved mode/system bars8.555s and
  opt-in system appearance/reduced-motion/adaptive-icon persistence4.976s passed.
- Intermediate builds exposed a missing local draft flag, test opt-in and role
  imports; corrected, subsequent builds passed. Latest validation units/lint/
  debug/androidTest passed1m21s;5new unit invariants bring the suite to263.
  Final normal artifact, expanded emulator and cleanup results follow below.
- Ruff initially requested formatting of4changed Python files; applied and
  subsequent lint/format285files passed. Interim protected-file audit:640baseline,
  388protected byte-identical, no deletions; original report reconstruction hash
  matches. Final audit/checks follow below.

Safety/limits: backend/OpenAPI, ownership, client data/audio/controllers/ViewModels,
journals, migrations, lockfiles/wrapper and later phase plans remain unchanged.
Manifest changes only the icon resource; MainActivity changes launch presentation
while retaining secure-window/audio/lifecycle wiring. No normal app install,
application DB write/migration, private-service activation, external research or
native model inference. Manual spoken TalkBack/focus restoration, hardware
keyboard/switch traversal, alternate IMEs, physical tablet/foldable live resize,
graphics/battery/long-scroll and inherited voice/focus/G-41 release gates remain
pending. Full backend/web/connected suites were not run. Physical settings were
restored to font1.0/lock0/default rotation policy/accelerometer0/userRotation0;
animator scale remains unset. Separate phone packages/reverse absent; normal
app19/0.25.1-ambient last update03:57:24 remains unchanged.


Android design-gap closeout: expanded API37 emulator2560x1800/density320/font1.6
passed native feedback/selection/safe-link/Cancel keyboard semantics9.534s,
Ambient dark32.088s/light32.806s primary-screen/source walkthroughs, dialog
bounds16.425s and keyboard Back/draft14.112s. Representative physical and emulator public app-layer
images were reviewed; dimensions read directly from PNG headers. An auxiliary
Pillow-based dimension probe could not run (dependency absent); no dependency was
added. Windows console lint-message inspection needed JSON escaping for a Unicode
message. Neither auxiliary failure was counted as a passed check.

Final normal Gradle `testDebugUnitTest lintDebug assembleDebug
assembleDebugAndroidTest assembleRelease` passed1m3s, then26s after removing an
unused legacy icon and moving the adaptive default to unqualified mipmap-anydpi
(minSdk26 already guarantees adaptive-icon support). The first lint had25warnings;
a cached empty-folder warning remained after resource cleanup. Explicit final
`lintDebug --rerun-tasks` passed38s,0errors/23existing dependency/debug-localization
warnings. Final XML verifies263units/0failures/0errors/0skips. Normal debug APK
contents/metadata are dev.ada.assistant.debug/app20/0.25.2-ui; normal instrumentation
and unsigned release artifacts also verified. No normal phone installation.

Final audit against640pre-task files:64changed/new and one intentional deletion
(the obsolete drawable icon),388protected files byte-identical. OpenAPI remains
126paths/168schemas byte-identical. Manifest differs only by icon reference;
backend/controllers/audio/data/journals/migrations/locks/later phase plans and
preexisting proxy work are preserved. Seven UTF-8 docs/118local links checked;
configured-credential/operator-contact scan found zero matches in changed and
new ignored non-image artifacts. Original static report reconstruction matches
its initial hash. Final Ruff lint/format285files, pip check and whitespace checks
passed; no dependency upgrades or new production permissions.

Cleanup observed: zero disposable fixture schemas/public relations on owned
PG55421 before guarded workspace/loopback stop. Owned emulator reset1080x2400/
density420/font1.0/free rotation/default policy, then stopped. Fixture listen
ports55421/18423/18424/18425 absent; validation packages/reverses absent. S24FE
original font/rotation/animator settings and normal app version/update timestamp
verified unchanged. No application database, private service, normal app or
later phase was deployed. Manual and full-suite limits stated above remain open.


### 2026-10-19 — Phase 26 — always-on operations and recovery — b2a383e + working tree

Scope: only Phase 26. Read required instructions/plans, current source/OpenAPI,
migration and test baseline first. Preserve the pre-existing Android work and
private configuration. No live migration, application database writes, production
task installation, power-policy change or deployment.

Implemented checkpoints:

- A/B: native Windows owner-logon Task Scheduler plan/install/remove; one owned
  single-worker API and optional pinned Caddy child. Protected kernel and committed
  PostgreSQL advisory ownership prevent supported duplicate admission owners.
  Job Objects contain only assigned children. Bounded startup/backoff, persistent
  API crash stop, cooperative shutdown and existing request/stream/job fences
  retain exact completed replay. External Ollama/DB processes are never managed.
- C: fixed DB/schema/API/provider/residency and host metadata, honest unknowns,
  pressure/quiet-period discretionary gates and explicit snapshot/WhatIf/reversible
  AC tools. Empty consolidation polls no longer take an inference slot; the guard
  runs before private job reads/claims. No policy was applied.
- D/E: current-user DPAPI secret provider, independent encrypted recovery capsule,
  selected-profile backup path, consistent snapshot plus current encrypted erasure
  ledger, verified atomic receipts, singleton daily task and protected-key isolated
  restore. Failed/deferred attempts retain the last good point. No pruning/source
  retention change. Daily 03:00/26-hour freshness are proposed, not agreed RPO/RTO.
- F: disposable real Windows/PostgreSQL/HTTP harness with explicit fake/native
  modes, admission/restart/replay/proxy/identity/key/backup/restore measurements.
  The user explicitly authorized the four-hour soak; its result is recorded below.

Contracts/data: schema remains 0017/60 tables; OpenAPI 126 paths/168 schemas.
No HTTP/auth/prompt/snapshot/request-ID/source-trust, migration, archive-format,
recovery inventory or dependency change. Protected OS metadata/key files remain
installation state outside database inventory. PG backup preflight now bounds
connection/query time and timestamps the snapshot before reading its contents.
Three legacy test-only corrections isolate default-payload tests from changed
user .env settings and match the prior UI runner's physical opt-in wording.

Checks actually run; ignored evidence is under .pytest_cache/phase26:

| Check | Actual result |
| --- | --- |
| Targeted baseline without PG | 23 passed / 19 skipped, 25.18 s. |
| Initial native PG baseline | 41 passed / 1 connection error, 212.98 s; first fixture raced failed default-port startup. |
| Corrected native PG baseline | 42 passed, 84.12 s, explicit loopback 55421. |
| Failure tests before implementation | 8 failed / 2 skipped, 2.29 s; missing modules and old empty-poll admission confirmed. |
| Initial invariants | 8 passed / 2 skipped, 2.73 s. |
| First native checkpoint | 11 passed / 3 failed, 7.98 s; inherited PS7 module path broke PS5 ACL imports. Explicit native imports corrected it. |
| Corrected checkpoints | 14 passed, 13.87 s; then 15 passed, 19.22 s, including actual owned-child containment. |
| PG/Windows failure matrix | 20 passed, 57.10 s: wrong schema, DB/provider down, duplicate ownership/no open advisory transaction and bounded child crash loop plus earlier host tests. |
| Final affected/legacy checks | 40 passed, 48.23 s. |
| First full suite | 955 passed / 5 failed / 27 skipped, 1552.07 s. Two failures came from editing imported code during that run; two default-payload tests read user-modified settings; one stale quality guard expected old runner wording. Corrected, then source frozen. |
| Pre-soak full suite, original frozen source | 966 passed / 27 skipped / 1 existing warning, 1469.00 s (24:28). Later receipt/startup changes require the fresh run below. |
| Final full suite after failure hardening, new frozen source | 975 passed / 27 skipped / 1 existing warning, 1414.93 s (23:34), exit0. All1002 collected; same27 skip cases verified. |
| Native power tools | Snapshot and WhatIf passed after numeric-range parser correction; AC sleep/hibernate/lid values all zero. No Apply/Restore executed. |
| Ruff | Python lint/format passed before final run; final audit below. An accidental PS-file lint selection was corrected without file changes. |

Existing Starlette/httpx TestClient deprecation remains; no dependency upgrade.
The27 skips were19 SQLite variants requiring PostgreSQL locking (their native
counterparts ran), two opt-in generation-free Ollama admin probes and six opt-in
native agent/tool probes. Those optional switches were unset in the full suite;
the separate Phase26 public native rehearsal is not relabeled as those tests.

During-soak interim checks: Ruff lint passed and298 Python files formatted; pip check
found no broken requirements; whitespace check passed. All four affected PS
scripts parsed with zero errors in Windows PowerShell5.1.26100.9711 and
PowerShell7.6.6. Audit:651 initial files,637 protected unchanged,30 phase-specific
changed/new,225 frozen code hashes unchanged,141 local Markdown links resolved,
zero configured credential/operator-contact matches in103 checked source/evidence
files. These are interim audit counts; repeat after final records/cleanup.

Public/synthetic disposable host rehearsals:

- First fake: 30.22 s, 30 health checks/zero unavailable, three replies mean/max
  0.031 s; three HTTP 200/five 503 under eight concurrent requests. Backup
  202,248 bytes/0.546 s, restore 1.188 s. Scheduled identity/key, duplicate refusal,
  child crash/exact replay, quarantine and stop passed.
- First configured-native: 18.62 s, 11 health checks/zero unavailable, first reply
  18.172 s, two warm replies mean 3.7815 s/max 3.813 s; one 200/seven 503.
  Backup 201,744 bytes/0.812 s, restore 1.734 s. No model resident before,
  one configured model after.
- Final short fake with pinned proxy and Task Scheduler: 60.64 s, 60 health checks/
  zero unavailable, six replies mean 0.070 s/max 0.109 s; two 200/six 503.
  Backup 202,849 bytes/0.532 s; actual protected-key CLI isolated restore 2.969 s.
  Same-user demand-start key access, owned proxy, duplicate refusal, child crash/
  replay, quarantine and cooperative stop passed.
- Final configured-native: 18.75 s, 11 health checks/zero unavailable;
  qwen3.8-27b-uncensored, context 16,384/output 1,024; first reply 17.718 s,
  two warm replies mean 3.859 s/max 3.953 s; one 200/seven 503.
  Backup 201,811 bytes/0.640 s; actual protected-key CLI restore 3.328 s.
  Zero resident models before/one configured model after; duplicate, recovery,
  replay, credential quarantine and stop passed. User settings preserved.
- Last native host sample: AC true, battery 100%, RAM available 26.2%, NVIDIA
  VRAM 13,968/16,376 MiB, utilization 7%, temperature 53 C, about 989 GB free.
  Final short fake sample: RAM 41.6%, VRAM 405 MiB, GPU utilization 21%, 50 C.
  These are host observations, not peaks or isolated ADA attribution. CPU
  temperature is unknown; tiny fixtures do not establish production capacity.

**Original four-hour attempt — failed; successful rerun recorded below.** Authorized explicit-fake run started at
2026-10-19 08:20:46.054 UTC and ended11:35:46.788 UTC (01:20–04:35 Phoenix),
11,700.734 seconds wall time including startup/cleanup, approximately3h15.
ConnectError interrupted it before14,400 seconds; actual timed-loop counters
were not retained by that original harness. End-of-run backup/restore was not
reached. No availability percentage or completed four-hour result is claimed.
Disposable PG18.6/profile/proxy were used; owned API/proxy stopped and fixture DBs
were dropped. All225 original frozen source hashes still matched after failure.

The218 external observations included217 ready supervisor snapshots and one
stopped snapshot retaining last-known healthy fields. These partial samples do
not replace missing harness totals. Maximum observation gap103s includes observer
restarts; host sample minimum RAM available43.7%, maximum observed NVIDIA44C,
no sampled pressure. No sustained native inference was performed in this soak.

Skipped/remaining: installed reboot/logon and Docker startup order; actual sleep/
resume/lid and applied power rollback; pre-logon service/GPU access; a separately
authorized 24-hour trial; representative private quality/latency and sustained
thermal/RAM/VRAM budgets; large-data cap/growth and agreed RPO/RTO; selected
off-device copies and actual machine/profile-loss capsule recovery; hardware
disk-full/power-loss recovery. Synthetic pressure/key/corruption/stale-ledger/
restore failure coverage does not prove physical scenarios. The configured
application database was unavailable during read-only prerequisite inspection;
it was not started or modified. Native Ollama metadata/public inference worked.
Android/web suites and physical-device tests were not rerun because their code/
contracts are unchanged by this phase. Phases 27–31 remain unimplemented.

Additional closeout finding during the soak: an isolated foreground-launcher
reproduction confirmed that an occupied port still reaches the ownership/runtime
step (unreachable test DB, disposable profile). The supervised path already
refuses occupied ports. After the failed frozen run, added a start.ps1 preflight
and six native occupied/free-port cases across PS5/7 and IPv4/IPv6. No live DB used.

Failure hardening after the long attempt: a controlled real supervisor/HTTP reader
rehearsal reproduced PermissionError in receipt publication, five unavailable
health checks and failed graceful-stop assertion. It restored a quarantined
fixture before reporting failure. Reported19.91s included post-loop recovery and
shutdown; that original diagnostic elapsed value is not a completed soak duration.
The first long run lacked supervisor-error detail, so its exact original cause
cannot be established from its saved record. The reproduced sharing failure is
confirmed independently. Receipt writes now use distinct temporary files and
bounded3s retries for Windows sharing/access collisions. Persistent failure keeps
the prior complete receipt and exits within the bound. The harness now retains
failure stage/counters/child exits/supervisor exception types and preserves timed
loop duration; it retries only brief backup-lease contention, never pressure or
integrity failure.

Before these fixes: five new cases failed/three passed in39.92s (reader collision
and four occupied-port failures; free-port/concurrent cases passed). Afterward:
28 host checks passed in61.91s, plus all three atomic cases in3.46s including a
persistently held reader. Corrected reader-contention/Task Scheduler/proxy rehearsal:
60.47s,60health checks/zero unavailable, six public replies mean0.047s/max0.063s,
two200/six503, backup202842B/0.547s and protected-key isolated restore2.953s.
Duplicate/crash/exact replay/quarantine/clean stop passed, supervisor errors empty,
zero backup-busy retries. Host sample RAM available45.4%, GPU210MiB/0%/44C;
host counters only, not sustained native workload. Ruff lint/format300files passed.
Fresh227-file freeze backed the completed final suite. A new continuous four-hour
window is required; additional laptop-awake availability was requested separately
and has not been confirmed. No second long run was started.

Final cleanup observed: only the expected ada_phase2_test/postgres databases,
zero disposable fixture schemas/public relations, zero ADA26/validation tasks and
zero remaining fixture listeners. Verified workspace datadir/loopback55421/PID
identity before stopping only the owned native PG18 server. Power scheme and all
captured AC values matched their originals; no Apply/Restore was performed. No
production API/database/Ollama/Tailscale/phone/task configuration was changed.
Final Ruff lint/format300files, pip, native PS5/7 syntax and whitespace checks
passed. Scope/UTF8/link/secret audit:651 initial files,637 protected unchanged,
32 phase-specific changed/new,227 current frozen source hashes unchanged,
141 local Markdown links resolved, zero configured credential/operator-contact
matches across149 checked source/evidence files. OpenAPI remains126/168 and all
released migrations, dependencies, clients and prior UI edits retain their hashes.
At that preceding closeout, Phase26 source was implemented and its continuous
four-hour gate remained failed/open. The separately authorized rerun below closes
only the development-soak gate. Do not infer installed/unattended-production
readiness or advance automatically to Phase27.

### 2026-10-19 — authorized continuous four-hour rerun — passed

The user confirmed an additional plugged-in/awake window after the fixes.
Preflight verified all227 frozen source files unchanged, the earlier975/27 full
result and60.47s injected-reader success. Restarted only the owned native test
PG18.6 at127.0.0.1:55421 after verifying workspace path/free port; metadata showed
only expected base/postgres databases and zero fixture schemas/public relations.
Started a separate14400s explicit-fake run atabout15:03:39UTC/08:03:39Phoenix,
with pinned proxy, temporary same-user Task Scheduler key check and deliberate
receipt-reader contention. New evidence: ignored run-dbbe30e84a/result.json and
soak-four-hour-rerun.log. The prior failed attempt is preserved unchanged.
No live application DB, production task, external provider, power policy or
later phase was changed. Final measured result and cleanup:

| Check | Actual rerun result |
| --- | --- |
| Continuous timed soak | **14,400.39 seconds**, requested 14,400; passed, process exit 0. |
| Full harness wall window | 2026-10-19 15:03:39.282–19:04:23.459 UTC / 08:03:39–12:04:23 Phoenix; 14,444.177 s including startup/recovery/cleanup. |
| Timed health | **14,278 samples, zero unavailable**. This is sampled development availability, not a production SLA. |
| Public fake-provider chat | 1,428 replies, mean 0.0375 s / maximum 0.188 s; first public reply 0.047 s. Native-model readiness/latency explicitly not measured in this run. |
| Single-slot admission | Eight concurrent requests: two HTTP 200, six HTTP 503. |
| Recovery and identity | Temporary same-user Task Scheduler key access, pinned owned proxy, duplicate refusal, deliberate API crash recovery with exact completed replay, and native receipt-reader contention all passed. Two child starts total; child exit codes [1, 0] reflect the deliberate crash and final graceful exit. |
| Backup | Verified encrypted artifact 682,629 bytes / 0.984 s; zero backup-lease retries. |
| Restore | Protected-key CLI isolated restore 9.985 s; credentials quarantined. |
| Shutdown | Graceful supervisor stop, no supervisor errors, API/proxy PID fields null and no remaining fixture listeners on 59904/59905. |

Independent metadata observations: 285 snapshots, 284 ready and one final stopped;
maximum two child starts, no sampled pressure, minimum observed RAM available
35.0%, maximum observed NVIDIA temperature 43 C. These partial host observations
are not peak/ADA-only resource measurements and do not replace harness totals.
Last host sample: AC true, battery 100%, RAM available 47.2%, GPU 0/16,376 MiB,
0% utilization / 39 C, disk free 988,799,766,528 bytes. CPU temperature unknown.

Cleanup independently verified only ada_phase2_test/postgres databases, zero
fixture schemas/public relations, zero ADA26/validation tasks and zero remaining
fixture API/proxy listeners. Resolved workspace datadir, postmaster identity and
127.0.0.1:55421 owning PID were checked before stopping only the owned native
PG18.6 server; its listener is absent. A new read-only power snapshot matches
the original scheme and captured AC sleep/hibernate/lid values. No Apply/Restore
or production task installation was performed. Unrelated email.txt appeared
during the run; its contents were not displayed or edited and its hash is
preserved separately from Phase26 change accounting.

The earlier 975 passed/27 skipped full suite still applies to the same 227 frozen
source/script/config files; no source changed during the rerun. No redundant full
suite, client/device test, 24-hour trial or installed reboot/sleep test was run.
Final Ruff lint/format (300 files), pip check and whitespace passed. Final audit:
651 baseline files, 637 protected files unchanged, 32 Phase26 changed/new files,
227 frozen source/script/config hashes unchanged, 141 local Markdown links
resolved and zero configured credential/operator-contact matches across 167
checked source/evidence files. One unrelated file is preserved separately.
OpenAPI remains 126 paths/168 schemas; prior UI work, released migrations,
dependencies and client contracts retain their baseline hashes. The initial
scope check correctly flagged the unrelated new file before that accounting was
made explicit; it was not a phase implementation change.

**Four-hour development gate passed.** Remaining target verification is unchanged:
installed logon/reboot/Docker startup, real sleep/resume/lid and applied power
rollback, service-identity/GPU access, sustained native workloads and representative
backup size/RPO/RTO, off-device/lost-profile recovery, physical power/disk failure,
and a separately authorized 24-hour trial. Stop at Phase26; no deployment or
Phase27–31 implementation.


### 2026-10-19 — Phase27 durable scheduling — implementation in progress — b2a383e + working tree

Scope: only Phase27. Required instructions/current source/OpenAPI/schema/test state
inspected before implementation. Phase26 development-soak gate is closed; its
installed-host/physical/24-hour limits remain separate. Initial snapshot covers
670 files and OpenAPI126paths/168schemas. Existing Android/Phase26 changes and
unrelated email.txt are preserved. No live database, task installation or deployment.

Current implementation: migration0018 adds five private scheduling tables and an
additive admin audit action; finite previewed IANA/UTC plans, explicit owner
consent and originating-credential grants, deterministic occurrence keys, committed
leases/attempt fences, latest-only catch-up, quiet hours, expiry, pause/snooze/edit,
durable inbox/acknowledgement and explicit empty-conversation opening. Typed jobs
are reminders and existing Phase25 catalogue questions; no inference process,
backup scheduler, arbitrary executable kind, cloud registration or background push.
Windows uses the existing pinned tzdata2026.5, now a direct cross-platform dependency.
Current recovery-v4/0018 inventory includes all new private content and quarantines
restored schedules after original hash verification. Older recovery remains supported.
Android v15 encrypted exact-operation journal/controller/screens and read-only admin
aggregate view are being connected; client/complete regression verification pending.

Checks actually run so far (ignored evidence under .pytest_cache/phase27): existing
SQLite/nativePG baseline185passed/3skipped/one existing warning,314.06s. Calendar
invariants before implementation10failed/0.17s; afterward10passed/0.10s. Missing-API
probe1failed/1PGskip/10deselected,1.30s (that isolated probe omitted the PG env).
First new HTTP/calendar checks22passed,17.43s. Expanded matrix44passed/3failed/
1expectedSQLite skip,55.26s: additive audit action needed the database constraint,
and one SQLite table-count assertion included native FTS shadow tables. Corrected
matrix47passed/1skip,56.09s. Additional stale-auth/pruned-question fences first
4failed,5.84s, then4passed,5.62s. Native backup/restore checks and client builds
are running separately; their final results are not yet claimed.

Migration generation first caught native FTS indexes as spurious diffs and aborted
before writing the migration; applied the existing exclusions and generated only
five scheduling tables/three indexes, preserving released migration bytes. Extended
the released audit constraint only in0018. One auxiliary web-edit script hit Windows
locale decoding; explicit UTF-8 follow-up succeeded. Long pytest failure output
included ephemeral synthetic fixture credentials; those cache logs were redacted,
and subsequent test runs use short tracebacks. No configured/private credentials
were displayed or copied. No optional target gate is being counted as passed.

### 2026-10-21 — Phase27 verification reconciliation before Phase28

This closes the pending record from the preceding2026-10-19 implementation run;
it does not redate its tests as new executions. Frozen full regression passed
**1042/30 skipped/one existing Starlette warning in1600.15s**, all1072 cases accounted
for. Exact skip mapping preserves all27 prior skips and adds three SQLite copies:
native multi-claimer, abrupt process/lease recovery and MVCC inbox/read concurrency.
Total:22 SQLite lock/process copies (native variants executed) and eight opt-in
real-Ollama health/agent probes left off; no new inference path needed those probes.

After that full run, three pure calendar range probes failed0.41s and six real
HTTP/SQLite/PG cases failed11.52s with representable-date overflow. Normalize it
to the existing422 validation result, without reserving an operation. The host
wiring fixture initially tried adding middleware to a started app (two fixture
failures3.15s); a fresh unstarted app reproduced the actual provider/quiet gate
problem (two failures4.26s). Non-inference inbox/catalogue dispatch now retains
fresh database/resource gates without requiring model readiness/inference quiet;
consolidation's existing gates are unchanged. Five source/test files differ from
the frozen full run. **Final complete scheduling plus host-operation regressions:
107 passed/3 expected SQLite skips/one existing warning,171.76s**, exit0. All343
final-run source hashes remained unchanged. No second full run is attributed to
these small post-run corrections; every affected scheduling/host path was retested.

Android final275 units, lint0errors/23 existing warnings, debug/test/unsigned-release
builds and separate emulator HTTP12.857s +3.001s force-stop stages passed. Normal
APK outputs restored; validation package/reverse/schema removed and owned emulator
stopped after checking its AVD identity. No physical or normal-app installation.
Web contracts/type/lint/71 units/production build/seven real Chromium cases passed;
new Refresh focus failure/correction and prior failures remain above. Final Ruff
check/format313files, pip check and source/export OpenAPI equality passed. Contracts
138paths/181schemas retain126old paths/168schemas apart from two additive capability
fields and monitor.scheduling in the audit enum/query. Released migrations and
client dependency versions remain; existing tzdata2026.5 is now pinned on every OS.

Last observed cleanup after the final tests: only expected ada_phase2_test/postgres
DBs, zero fixture schemas/public relations, zero validation tasks/listeners on
18423/18763/5173; ADB inventory empty. The owned loopback55421 PostgreSQL cluster
had not yet been stopped when the next phase was requested. Its identity/state
must be checked afresh before reuse or stop; no production cluster may be adopted.
Early scope/link/secret audit is retained above; Phase28 must take a fresh baseline.

Remaining target verification: S24FE/API36 manual accessibility/layout/timezone/
offline use; selected installed-host0018 upgrade with matching PG-major tools,
logon/reboot/sleep/OS-clock behavior, representative RPO/RTO/off-device recovery,
sustained native inference and separately authorized24-hour operation. Push/doze/
provider-registration/lock-screen checks are not run because that channel remains
unavailable. No live DB change, system-task/power change, normal app deployment or
later-phase implementation was performed. Phase28 is now explicitly selected by
the user; its baseline/implementation is a separate run.


### 2026-10-21 — Phase28 idle reflection/review: final local record

Scope: only the selected Phase28, against b2a383e plus the preserved pre-existing
working tree. Existing13/18/23/25/26/27 source prerequisites were inspected; the
preceding Phase27 evidence retains its Oct19 provenance. A date-sensitive Phase27
test fixture was corrected for Oct21 note creation; no production calendar rule
or earlier implementation was expanded.

Implemented checkpoints A–E for the initial rule-only job set:

- Separate durable automation/reflection/completed-turn consent; owned scopes,
  included source types/lookback, IANA hours, resource/time/job bounds and empty
  selection policy. Owner/epoch/origin/version/hash/current availability checks
  precede payload and publication. Completed model turns remain unendorsed.
- Existing dispatcher/consolidation hooks, fresh host readings outside DB/model
  admission,15-minute ADA inactivity default, foreground cancellation/shared slot,
  finite leases/retry/quotas/reserved off and visible skip/capacity decisions.
- Owner-marker and possible-change reports, Phase25 question drafts and explicit
  Keep/Discard/Open with no factual claim or invented user turn. Owner-wide
  template metadata survives discard; changed catalogue wording cannot substitute
  for a reviewed question. Generated-summary/Phase13 Keep support is tested with
  synthetic providers but remains disabled for production use.
- New unreleased0019 adds five tables, native uniqueness/fencing and the audit
  action. Owner-content57 and backup-v5 include all new private rows; populated
  restore preserves dedup metadata and pauses authority/queues/provider attestation.
  Older formats remain supported; released-v4 restore/upgrade was rehearsed.
  Running reflection joins deletion quiescence. Released0001–0018 are unchanged.
- Android While you were away: source/time/resource controls, original quotes/
  hashes/scope/provenance, omissions/duration/empty outcomes and exact journal16
  mutation recovery, old versions readable. Admin projects fixed counts/budgets
  only under the existing current grant/audit checks.

Checks actually run, with provenance:

- Source-fixed full `pytest --assert=plain -q --tb=short`: **1161 passed /32 skipped**
  in2169.59s. This is before the final review guards/internal dedup column below.
- Final review first reproduced10 SQLite/PostgreSQL failures, plus one real TCP
  trickling-metadata cancellation failure. After the documented fixes, guard/
  provider/native-schema selection **33 passed in40.30s**. Final affected run:
  all then-current reflection tests plus security, recovery, consolidation,
  curiosity, schedules, streaming and host foreground/backup — **282 passed /
  4 expected SQLite skips in599.06s**. This includes populated0018→0019 upgrade,
  `alembic check`, original completed replay, downgrade refusal, owner erasure,
  native duplicate/crash fencing and real encrypted v5 restore with a question
  artifact plus running job. The separate final positive automatic-completed-turn
  and request-state-change selection passed **4 tests in6.89s**, on both databases.
  These runs overlap; their counts are not added into a fictitious full-suite run.
- Whole-tree Ruff/format and `pip check` passed. Dependency locks/wrappers stayed
  unchanged from the Phase28 boundary. Python retains one existing Starlette/httpx
  deprecation warning.32 broad-run skips cover SQLite counterparts of native
  concurrency cases and non-enabled unrelated local Ollama health/agent probes;
  the required native PostgreSQL cases and separate Phase28 public probe ran.
- Native PostgreSQL18.6 on an owned loopback disposable cluster. Latest host exercise
  **60.09s /29 foreground replies**, one report, one verified encrypted backup,
  one run and **zero factual claims**. Fake provider and explicit synthetic safe
  resource inputs; baseline median47ms, foreground p95=78ms, observed delta+31ms,
  below the500ms test budget. Hardware snapshot separately showed AC,51°C GPU,
  23.7% available memory. GPU time is unknown. Earlier61.97s exercise and its
  cold/warm timing limitation remain in WORKLOG; neither is a native-model soak.
- Constrained public qwen3.8:27b probe: client returned cancellation at1219ms,
  719ms after request. No private input, model launch/unload or live setting change.
  This is not server-GPU stop/usefulness proof; summaries stay disabled. Real TCP
  tests cover stall/trickling/deadline handling separately from native evidence.
- Android **283 units**, zero lint errors/23 pre-existing warnings, normal debug
  and separately identified validation APK builds. Final server's real owner HTTP/
  Keystore/actual force-stop stages passed **5.943s /2.969s** and verified exactly
  three reflection POSTs across restart. Earlier failed test synchronization,
  command quoting/build diagnostics and successful stages remain in WORKLOG.
- Web `npm ci`, contracts generate/check, typecheck/lint, **72 units**, final build
  and **8 real Chromium cases (26.1s)** passed. The first7/1 browser run exposed new
  navigation overflow at200% zoom; wrapping fixed it. No screenshots/traces or
  browser credential persistence were introduced.

Evaluation is deliberately narrow: one owner-marked report accepted per synthetic
backend; three non-conflict cases produced zero false flags and the overlapping
endorsed pair produced a possible-change flag without selecting truth. Same-source,
cross-scope and discarded-question cases produce no duplicate draft after the
final fix. Completed model TODOs produce no owner finding and all reflection paths
create zero factual claims. This does not establish broad personal-memory quality.

Skips/remaining target verification: physical S24 FE/TalkBack/new-screen large-font
and resize review were not performed; the connected phone/normal app were untouched.
Installed-host overnight/resource behavior, representative private-data usefulness,
native-summary quality/cancellation/GPU interference and sustained native operation
remain open. No production summary attestation/enabling workflow is supplied by
this smaller initial job set. Prior host/device recovery gates remain separate.
Global work remains off until an operator and owner explicitly configure it.

Cleanup: final validation APKs/reverse mapping removed; owned emulator stopped.
Only base ada_phase2_test remained, with zero fixture schemas/recovery databases;
resolved data directory/postmaster/listener/executable identity was verified before
stopping the owned PG cluster. No live application database/service/private-proxy configuration, scheduled
task, power, Tailscale, normal app or later phase was changed/deployed. Final
scope/contract/link/secret audit is recorded in WORKLOG.

### 2026-10-21 — Phase29 natural local speech: study/interface boundary

Base b2a383e plus the preserved existing working tree; a fresh boundary snapshot
covered715 files. Required/root/scoped instructions, architecture/current state,
OpenAPI145paths/193schemas, migration0019 and existing voice source/tests were
inspected before edits. Phase17 reviewed voice and17-A hardening are present;
17-A's physical audible focus/active permission gates remain unresolved. Fresh ADB
inventory was empty. This phase explicitly permits the study/interface exit without
a connected phone; no runtime choice is inferred from desktop or emulator results.

Checkpoint disposition:

- A: primary-source comparison of installed platform, sherpa-onnx1.13.8/English
  Zipformer20M, whisper.cpp1.9.5/tiny.en and a conditional Kokoro TTS route. Exact
  revisions, separate runtime/model/voice/phonemizer license findings, metadata
  sizes/digests and unresolved native/redistribution questions are in the guide.
  No model binary/package was downloaded or installed; no candidate is approved.
- B: local versioned ASR/TTS/task/system-managed status, fixed public voice preview,
  rate choice, explicit unsupported style and platform/text fallback. A strict
  manifest/byte checker enforces external pins, bounds, hashes and portable paths
  without writing/loading/executing. Opt-in download/import/staging/removal and
  activation are specified, not exposed as working controls or an installer.
- C: original ASR, editable endorsement/approval and safe completed-reply playback
  retain their existing lineage/journal/API. No cleanup LLM, shorter adaptation,
  extra synced private cache or audio upload. Default voice selection no longer
  chooses an unmatched language implicitly. Native playback rechecks installation
  and ignores stale utterance errors. Preview/Stop cannot cancel server generation.
- D: pending. Reopen17-A, measure the actual en-US platform baseline, then freeze
  device-specific quality/latency/resource/human thresholds before candidate
  scoring. Native permissions/focus/calls/routes, memory/removal/battery/thermals,
  privacy/lifecycle/late output and final bundle-license clearance remain gates.

Checks actually run (Windows; machine evidence2026-10-22UTC, displayed dateOct21
America/Phoenix):

- Existing focused SQLite baseline `pytest tests/test_voice.py
  tests/test_client_contract.py tests/test_schema_contract.py --assert=plain -q
  --tb=short`: **34 passed/30 skipped,55.20s**. The PostgreSQL parameterizations
  were unavailable to that command and not counted as passes.
- Same selection with owned native PostgreSQL18.6/disposable database:
  **64 passed,134.72s**, including real schema/replay/concurrency and exported
  contract checks. Separate validator guards: **4 passed,0.08s**. One existing
  Starlette/httpx deprecation warning remains; no dependency upgrade to hide it.
- Android baseline wrapper unit/lint/debug passed. New invariants first failed
  compilation because their contract/preview functions did not yet exist. Focused
  implementation checks passed, then full Android **292 units/zero failures,
  errors or skips**; lint **0 errors/23 existing warnings**, normal debug and
  unsigned release builds passed. JDK21.0.12.1, pinned Gradle8.13/SDK36; wrappers,
  dependency catalog/locks and minSDK26 unchanged. Final-source build evidence is
  appended to WORKLOG. App23/0.29.0-speech-study; encrypted journal16 unchanged.
- Separate emulator API37 validation app with synthetic audio drivers, real
  authenticated HTTP/native PostgreSQL/Compose/Keystore: **three checks passed**
  (8.307/13.740/9.074s): public preview/no capture/no event, reviewed Send and
  separate playback/generation Stop, denial/navigation/background/late callbacks
  and encrypted draft recovery. The runner force-stops between independent tests;
  this is not new evidence for the separately staged process-death journal test.
- Ruff lint/format passed; format reported248 Python files. Contract bytes are
  unchanged from the fresh boundary. Production backend/admin source, migrations,
  contracts, locks, later phase plans and pre-existing private file stayed intact.
  New guide/index/architecture links passed the local link audit.

Retained failures/corrections: the first emulator assertion needed an explicit
substring matcher; its node contained the correct status. The next attempt passed
preview but failed to find Record because the shared admin fixture deliberately
used a non-streaming provider. A new explicit **test-only** voice-fixture switch
uses the existing deterministic streaming driver; production capability gates
were preserved. The corrected three-check run passed. One new Python import-order
lint issue was fixed. A documentation patch failed context matching and made no
partial edit; corrected against current text.

Not run: full unrelated backend/web suites (no production server/web change),
physical S24FE/audio/permission/focus/TalkBack/older-API/battery/resource trials,
new native runtime builds/model inference/download/install/removal/pressure tests
and human ratings. No such adapter/installer is active. Candidate redistribution,
Kokoro converted-bundle/voice/phonemizer clearance and Android native-page alignment
remain unverified; retain platform speech until the explicit device gate is met.
No live schema/configuration/service change, normal phone installation, deployment
or Phase30/31 implementation. Schema0019/70tables, owner-content57, backup-v5,
OpenAPI145paths/193schemas, prompts and completed replay remain. No migration or
server upgrade is needed for this client/study change. Cleanup/final audit are in
WORKLOG; [usage/study/verification](../docs/NATURAL-LOCAL-SPEECH.md).


### 2026-10-22 — Phase30 projects and personal follow-through

Implemented A–D in source. The owner selected **balanced personal commitments and
development projects**. Inspected requested docs/current source/OpenAPI and the
0019 migration/test baseline first. Existing23 source relevance/private scopes,
18 erasure/recovery,25 question consent and27 scheduling prerequisites exist;
29 physical/native speech gates remain independent. A719-file starting hash
inventory preserved the preceding uncommitted work boundary.

Explicit reserved projects and scoped goals/tasks require authenticated exact
owner review, expected revisions and stable operation IDs. Status includes
planned/done/deferred/unknown/dismissed; time never completes work. Original pins
retain trust/hash/code-point spans. Requested chat Save starts blank and pins its
completed generated reply; review does not make it factual evidence. No tool or
background path creates commitments. Briefs deterministically project selected
revisions/source pins/changed fields, overdue and uncertainty; task T-labels are
navigation. Owner/scope/epoch/revision/calendar/overdue cache keys, immutable status
and day flags, source reauthorization and late-result fences preserve history.
Optional25 questions and27 reminder preview/confirmation retain current consent;
editing work pauses related automation and cannot revive a done task via generic
scheduling. No new background worker, model call or private admin reader.

Migration0020 adds four tables after immutable0019:74 total,61 owner-content.
Backup-v6 includes them; released0019/v5 restore then upgrade is tested. Erasure
covers all four tables, and restore preserves work/history while disabling
question/scheduling authority and quarantining schedules/credentials. Source
requires migration0020 before an operator later installs it; no live migration,
reset or deployment was performed. Existing145 paths/193 schemas are preserved
with only an additive work capability; current export157paths/206schemas.
Android24 /0.30.0-work uses journal17, reads1–16, encrypts before POST, checks GET
on reconnect and retries only the exact original operation after explicit action.

Checks actually run (Windows; native PostgreSQL18.6, isolated loopback55421):

- Prior relevant backend baseline45 passed/1 SQLite lock skip (85.17s); Android
  unit/lint/debug baseline passed10s. New write-path tests first failed before
  implementation (8 failed/10 skipped); subsequent focused runs are retained in
  WORKLOG rather than presented as separate final-source acceptance.
- Full backend **1206 passed/33 skipped**,2457.14s. This process imported source
  before final typed-source/calendar/storage-error/epoch/receipt guards. It is
  not relabeled as a full run of those later changes. Affected intermediate
  selection210 passed/5 skips471.53s; then post-guard selection **221 passed/5
  skips**,510.00s. The final safe calendar arithmetic was checked by a fresh
  Phase30 selection **49 passed/1 SQLite row-lock skip**,113.62s. Native row-lock
  and revision/idempotency cases ran. Final linked task/question/reminder encrypted
  backup-v6 restore check **1 passed**,4.67s, including preserved revisions and
  disabled/quarantined automation. Populated0019 upgrade, unchanged old replay,
  downgrade refusal, schema drift, erasure, v5 restore/upgrade, owner/scope/source/
  epoch/revocation, DST and sanitized storage failure are covered.
- Android final **300 units**,0failures/errors/skips; lint0errors/23existingwarnings;
  debug and unsigned release passed53s. Separate synthetic API37 emulator tests
  use real HTTP, Keystore and actual force-stop: final project creation, completed
  chat review/Save/brief stage10.429s and restoration/retry stage4.405s passed
  before the final receipt validation additions. Final rerun evidence follows in
  WORKLOG. Server POST counts proved restart made no work POST; explicit retry
  applied exactly one edit and preserved history.
- Admin `npm ci` baseline, regenerated contract/check/typecheck/lint,72 units and
  build passed; initial browser8cases passed35.8s. Final generated-contract checks,
  72units (32.11s total),build passed; corrected native fixture environment rerun
  **8 Chromium cases passed27.0s**. No private work view was added to admin.
- Whole-tree Ruff lint/format passed,348 files formatted. Strict OpenAPI comparison
  preserved every earlier path and non-capability schema. Dependency locks,
  wrappers and released migrations remain unchanged. Final audit/cleanup are in
  WORKLOG; they do not attest an installed service or physical app.

Retained failures/corrections: chat-review HTTP testing found an incorrect event/
source-version join; fixed against actual relations. LazyColumn collapsed/virtual
nodes needed explicit expansion/scrolling. Journal writes initially retained16
instead of17; the new recovery test caught it. Appending the capability field
preserved old positional Kotlin constructors. Legacy journal fixture versions,
a corrected UTF-8 read and menu indentation closed unit/lint failures. Final
receipt tests reject wrong revisions/definitions while accepting equivalent expiry
instants; a test reset required explicit scope refresh, corrected after two failed
runs. A final browser launch lacked the dedicated DB environment and timed out;
rerun with the isolated fixture succeeded. No failure is treated as a pass.

Skipped/remaining: five affected-selection skips are SQLite cases requiring native
row locks/MVCC/process behavior; native counterparts ran. The full run's33 skips
are retained as reported, without claiming individually unexpanded skip reasons.
No physical S24FE/TalkBack/older-API/real-content acceptance or sustained personal/
project usefulness study, native inference, long-running operation soak, installed
host reboot/dispatch or external actions were run. Synthetic held-out workflows
are correctness evidence, not human acceptance ratings. Prior29 speech/license/
physical gates remain open. Scope picker shows first100 scopes; retained work,
revision, brief and journal quotas are explicit. No automatic completion, push,
shared projects, model-synthesized brief or Phase31 work. See
[usage, migration, limits and verification](../docs/PROJECTS-AND-FOLLOW-THROUGH.md).


Phase30 final-source closeout (2026-10-22 America/Phoenix): after the receipt
revision/definition/normalized-expiry guards, separate validation APK build passed
23s and both actual HTTP/Keystore emulator stages reran successfully:
**9.389s /3.863s**. Project creation, chat Save, brief creation, real force-stop,
GET-only lost/unsent recovery and one explicit original retry passed. Earlier
failed and successful attempts retain their provenance. Normal debug/test APK
outputs were restored afterward (build passed, no installation). Final Android
300-unit/lint/debug/unsigned-release result above covers this production source.

Final audit: **57 changed/new files** relative to the719-file starting
inventory. Released migrations0001–0019, dependency locks/wrappers, Phase31 plans,
and existing auth/password/chat/curiosity/reflection/admin runtime files checked
against the baseline retained their bytes. The pre-existing email.txt was absent
at closeout; this work did not read, delete or restore it. The already-deleted
legacy icon remains outside the Phase30 change set. No unrelated deletion or
reset was used. Strict OpenAPI compatibility and local Markdown links passed;
configured-secret scan found **0matches** without printing values. Whole-tree
Ruff lint/format passed (348files); diff whitespace check passed with existing
Git LF/CRLF notices. No private chat/source quote/credential was added to plans.

Cleanup verified no Phase30 validation APK/reverse mapping,0fixture schemas and
only the base ada_phase2_test besides PostgreSQL system databases. Verified the
owned55421 listener/postmaster executable and resolved workspace data directory
before stopping that isolated18.6 cluster. Verified emulator5584's
Medium_Phone_API_37.0 identity before stopping it. Only owned test infrastructure
was stopped; no physical device, installed database/service/proxy, Ollama,
Task Scheduler, power policy or Tailscale setup was operated. Final checks found no listeners on owned test ports55421/18423/19822/5584/5585
and no ADB devices remaining. Normal APK output restoration passed22s.
No deployment/Phase31 work.


### 2026-10-22 — selected19A offline-draft study and31 text PDFs — source0021

Scope: user selected19A offline draft replies and31 text PDFs; after SmolLM2
failed, explicitly approved Qwen3-0.6B evaluation on the connected S24 FE. No19B
integration, later phase, production migration/reset or deployment. The existing
736-file starting inventory and Phase30 OpenAPI were retained under ignored
validation cache; unrelated edits were preserved. Root/Android/admin rules,
requested architecture/state/workflow/roadmap, source/OpenAPI/migrations/tests
were inspected before implementation.

Changed behavior: a real secret-free Docker parser, immutable original/derived
PDF hashes, parser/image identity, page/code-point maps, atomic publish, fail-closed
retrieval, exact binary Android review and page source cards. Text/Markdown routes
and old prompts/replay remain unchanged. OCR stays disabled; scans/blank or active,
encrypted/malformed input is unsupported, with a visible fixed failed state. No
filesystem crawl, URL/Office/archive ingestion or visual PDF renderer.

Selected19A adds owner/device P-256 enrollment/revocation, exact signed proposal
receipts and monotonic sequences, source/epoch/hash checks, encrypted recovery
and a dormant isolated-UID CPU JNI adapter. Generated drafts cannot create chat
turns, factual claims, tools or server replies. Both models failed quality, so
EDGE_QUALITY_APPROVED=false and edge_inference=false. Normal APKs omit JNI and
weights; PDF and draft sync are separately off by default. Protocol support is
not a model-quality claim. Guides: docs/PDF-INGESTION.md and ON-DEVICE-DRAFTS.md.

Data/API: new immutable migration0021 (released0001–0020 retained), nullable upload
extraction and two edge tables.76 installed/75 metadata tables;63 owner-content.
Backup-v7 includes all projections/drafts, reads v1–v6, and revokes device signing
registrations on restore. Owner erasure covers the new inventory. Export164paths/
216schemas; all157 earlier paths remain. Android25/0.31.0-documents-drafts,
journal18 reads1–17. No private admin reader, prompt upgrade or dependency/wrapper
upgrade; pypdf is a separate exact hash-locked container dependency.

Checks actually run before closeout (Windows, native PostgreSQL18.6 disposable
loopback55421; actual local Docker Engine29.8.2):

- Relevant baseline50passed/46skips81.75s without native env; relevant native
  baseline93passed/3SQLite-onlyskips303.18s. New PDF/edge red collection initially
  failed before their modules existed. Initial Android300-unit/lint/debug baseline
  passed before later PDF preview, edge and recovery additions.
- Actual PDF publication flow19passed71.79s; real boundary/egress/secret-env,
  crash/hang/stdout-flood/compressed-expansion selection5passed24.31s. The probe
  verified UID65534,256MiB memory/address-space,1CPU,16processes, no application
  environment and failed outbound connection. Fresh reviewed migration/backup/
  work/edge/PDF selection32passed133.82s. Later signature/source/sequence/erasure/
  PDF selection28passed/1SQLite-onlynative-race skip125.86s. Recovery and exported
  contract selection8passed40.74s, including populated0020 upgrade/replay and
  actual encrypted v7 original/map/draft restore with revoked registration.
- Admin regenerated contract/check/type/lint,72units27.98s and build passed;
  npmci completed270packages/0reportedvulnerabilities with existing encoding
  deprecation. Actual PostgreSQL/Chromium8cases passed27.6s. No runtime admin UI
  was added. Existing Starlette/httpx deprecation remains.
- New encrypted draft journal tests and Android unit/lint/debug passed2m19s;
  first native validation build collided with a concurrent Gradle R.jar lock.
  Sequential retry passed25s. The optional library builder compiled all77targets,
  verified AArch64/16KiB ELF loads, and produced source/library hash metadata.
  This is a build check, not packaged runtime acceptance.
- A separate API37 x86_64 emulator with real HTTP/Keystore/public PDF passed
  binary review/upload, page-linked source display and actual force-stop exact
  GET-only recovery/explicit identical upload retry:4.449s/4.461s. First attempt
  used an exact-text assertion against a longer correct preview; corrected to
  substring. No automatic upload, claim or private content was created.

Physical/model evidence: SM-S721U1, Android16/API36, arm64-v8a, SoC s5e9945,
4KiB pages,7397724KiB RAM, about2.18GiB initially available and12GB storage free.
Only public synthetic CPU CLI prompts, fresh processes and USB charging were used.
SmolLM2 Q8 (386404992bytes) ran roughly1–2s/~417MiB RSS but invented context,
leaked instructions or misdirected replies. An initial log-disable trial suppressed
output and is not quality evidence. Corrected public runs established the failure.
User-approved official Qwen Q8_0 (639446688bytes, full SHA verified) measured
2.515–3.515s/720.41–720.84MiB peak RSS,39.9→40.3C battery sensor. Fresh held-out
v2 after explicit first-person instructions:2.907–3.485s,3/4 met all constraints;
one missed the requested deadline question. The strict all-cases gate failed.
No larger model was selected or downloaded. Model licenses/support were checked
against official cards; pinned llama.cpp is MIT, model cards Apache-2.0, pypdf
BSD-3-Clause. Source lock and license/build details are in the study guide.

Retained failures/corrections: an intermediate storage/retrieval selection had
6failures/103pass/3skips from newly registered inventory and stale table counts;
fresh processes/counts corrected closure. Initial migration autogeneration included
unrelated native GIN index drops; these were removed from unreleased0021 only.
The first frozen-migration run3fail/14pass/15errors was followed by the reviewed
32-pass run above. Gradle MessageDigest shadowing and Long/Int PSS typing were
corrected. The broad backend run began before final receipt/model/principal guards
and before contract regeneration; early contract failures are not final evidence.
It also exposed the existing extraction benchmark racing unrelated background
transactions; its standalone corpus now disables those workers without weakening
the no-transaction provider assertion. Fresh SQLite/PostgreSQL corpus2passed12.90s
after an intervening1pass/1fail run. Fresh final affected checks follow below.

Remaining gates: the phone disconnected before the isolated-service APK/native
FD/UID/network-permission/cancellation/signed recovery probe could start. Its
physical runner failed the device-identity read and installed nothing. A reconnect
request is pending; CLI trials do not prove JNI/service behavior. No human draft
acceptance, sustained thermal/low-memory study, unplugged battery, physical PDF
layout/TalkBack, older Android/16KiB target, representative personal-document
acceptance, OCR need/quality, distributable-model approval or deployment was run.
PSS return checking is not an Android OS RSS cap. A future candidate needs fresh
quality and packaged-runtime evidence before activation. Full final-source suite
status, final affected checks, audits and owned infrastructure cleanup follow in
the closeout entry; no unfinished run is claimed as a pass.

### 2026-10-22 —19A/31 retained verification reconciled; Phase31 phone closeout

Source boundary: `04c5962` plus the Phase31 closeout changes. This entry preserves
the results completed before interruption, rather than claiming new runs. The
user had explicitly chosen to continue without the phone; that earlier reconnect
request was no longer pending. On resumption the user reconnected the S24 FE and
asked to finish Phase31 first. No additional model was evaluated or activated.

Previously completed final-source selections: affected document/retrieval/recovery/
schema/contracts/edge/PDF **170 passed/5 skipped**,728.83s; later principal/source/
capacity/restore guards **41 passed/1 skipped**,196.38s. A deliberately failing
cleanup test exposed capacity leakage/masked timeout; the fix was followed by
**8 passed**,26.50s, including actual Docker crash/hang/output/expansion/encryption/
xref limits, and **4 passed**,18.04s for publication/principal checks. A red PDF
support test exposed corrupt originals entering extraction context; the shared
lineage guard was followed by **87 passed/5 skipped**,375.73s across PDF/proposals/
work/edge. Future/expired PDF evidence is excluded before the model call.

The earlier broad backend run ended **5 failed/1248 passed/33 skipped**,4549.39s.
Two failures used the pre-regeneration contract; one extraction corpus assertion
raced unrelated workers; two tests inherited the operator's web-feature opt-in.
Regenerated contracts, worker isolation and explicit test-only feature-off defaults
closed the entire affected files in a fresh **36 passed/1 skipped**,66.64s run.
This is not relabeled as an all-green full-suite run. A fresh complete regression
run is in progress during this closeout; its result follows separately.

Previously completed actual API37 emulator HTTP/Keystore stages **7.521s/4.433s/
4.755s** passed PDF flow, real Android P-256 signing/enrollment/server verification,
encrypted receipt retention, actual force-stop, GET-only recovery, one explicit
original retry and revocation. Output in the signing fixture was explicitly
synthetic, with no native inference claim. Optional ARM64 library/APK provenance,
notices and16KiB ELF/zip alignment checks passed; packaged physical native FD/UID/
network/cancellation and real model-to-signed-draft verification remain open.
Both rejected candidates stay disabled;19A activation/exit remains open.

Fresh Phase31 closeout: inspected current source/OpenAPI/test baseline and
prerequisites. Added a PDF-specific real API/model-context/completed-replay test:
**2 passed/28 deselected**,6.18s on SQLite and native PostgreSQL. A new extraction
version cannot replace the old answer's original page/hash/citation snapshot;
the model is called only once and outside a transaction. Corrected Android error
and preview wording to include supported text PDFs when the capability is enabled.

Fresh S24 FE **SM-S721U1, Android16/API36** tests used only a separate synthetic
validation app, real HTTP/Keystore, isolated PostgreSQL and actual Docker parser.
Binary review/upload, two-page extraction/source card, visible scan rejection and
real force-stop GET-only restoration/one explicit original upload passed
**4.239s/2.943s**. The optional manual-review helper first failed to reselect its
scope after restart; corrected helper reran the automated stages successfully
**5.321s/2.475s**. Human visual evidence and final regression/cleanup follow below.
The normal app/data were not installed over, cleared or migrated.

Final normal Android build: `testDebugUnitTest lintDebug assembleDebug
assembleRelease assembleDebugAndroidTest` passed **1m41s**; **306 units**, zero
failures/errors/skips, lint0errors/24warnings. Warnings comprise23 retained warnings
and one dormant importer usable-space advisory. Normal APK identity was verified
and contains no native draft library, model weights or native attribution asset.
Whole-tree Ruff lint/format passed372files; whitespace check passed with Git's
existing LF/CRLF notices. Strict contract comparison preserves157 old paths,
required fields and old properties, apart from the compatible PDF media enum
extension. Released migrations0001–0020 and dependency locks/wrappers retain their
starting bytes. Interim audit:101 changed/new files versus736 starting files,
zero missing files/protected changes/configured-secret matches. The incidental
pre-existing editor CMake setting was preserved. Final audit follows below.

Cleanup already completed: verified the tracked public CLI/model directory's exact
resolved path and its three owned entries on the reconnected phone, then removed
only that directory. It had been left behind when the device disconnected; no
normal ADA app content was accessed. Owned test server/schema/APK/emulator/cluster
cleanup remains tied to the still-running validation processes. No live database
migration, service configuration, normal app upgrade, later phase or deployment.

### 2026-10-22 — Phase31 final code/shared regression evidence —04c5962 plus closeout

Shared backend command: `python -m pytest --assert=plain -q --tb=short -ra`, with
dedicated native PostgreSQL18.6 and the actual PDF image manifest. Result:
**1277 passed/34 skipped/1 existing warning**,2792.32s (46m32s), exit0. This run
began before the final parser-cleanup quarantine guard and additional layout
profiles; it is a passing shared snapshot, not a claim of one full final-source
run. Its34 skips were **8 opt-in Ollama checks** (2 generation-free health,
6 read-only native agent probes) and **26 SQLite cases requiring native row locks,
MVCC or abrupt-process recovery**. Native counterparts ran. The retained warning
is Starlette's existing httpx TestClient deprecation; no dependency upgrade.

The final fault review added a red test proving that an unconfirmed failed-worker
removal could admit another parse. The adapter now disables itself before
releasing host capacity when removal/exit cannot be confirmed. Timeout remains a
fixed error; later uploads/capability checks fail closed. Three fault modes cover
exception, nonzero removal and unreadable process status. The final complete PDF
selection after this guard passed **47/0 skips**,147.64s, covering actual Docker,
SQLite/native PostgreSQL, publication, malicious/unsupported input, authority,
page/context/replay, populated migration and encrypted restore. The prior46-pass
selection165.30s and red failure are retained separately, not relabeled.

The measurement checkpoint adds six reproducible public synthetic layout families
(columns, repeated-header table, Unicode and plain/compressed dense16-page text).
**6 checks passed**,6.88s; the metadata-only profiling command also completed with
all expected fragments/pages. Actual originals607–86572bytes, extracted16–50768
UTF-8 bytes,1–16pages/1–64chunks,437–531ms local parse/validate/chunk wall time
after initial verification. Plain dense text exceeds Android's64KiB quota;
compression preserves its extracted hash while changing its original hash. No
quota was raised. The checked [profile](../evaluations/text-pdf-profile-2026-10-22.json)
contains no document quotes, credentials or device serial. These developer
fixtures do not establish personal-file acceptance or visual table semantics.

Whole-tree Ruff lint/format passed **374 files** after the added profile helper/
script; a misplaced imported-fixture F811 suppression was corrected. Strict
OpenAPI compatibility still preserves157 released paths and existing required
properties, with only the documented additive media/page/capability fields.
Final-source setup/limits are in [PDF-INGESTION](../docs/PDF-INGESTION.md).
Final human review and owned infrastructure cleanup are recorded separately below.

### 2026-10-22 — Phase31 phone acceptance and owned cleanup — closeout

After the earlier manual window timed out waiting for Finish review, the user
explicitly reported **readable, no layout problems** and requested another window.
The reopened separate S24 FE validation app completed all three stages with exit0:
**4.213s/2.761s/111.542s**. The last duration includes human inspection/waiting,
not parsing latency. The user inspected document pages and the answer source,
then tapped Finish review. The prior scope-helper failure and timed-out manual
window remain recorded; neither is presented as a passing test. Public-sample
readability is confirmed; this is not TalkBack, table semantics or personal-file
acceptance. No further physical interaction is required for this bounded closeout.

Cleanup verified **0 fixture schemas and0 fixture databases** beyond the isolated
base/system databases; no phase19 validation/test package or tcp19822 reverse
mapping remained on the phone. Only the reserved public CLI/model study directory
had been removed earlier. Normal APK/test output restoration passed7s, with no
normal installation. Verified the task-owned emulator5584's AVD/API identity before
stopping it; its ports closed. Verified PostgreSQL18's executable, PID36032,
loopback55421 listener and resolved workspace cache data directory before stopping
only that cluster. Final checks found0listeners on55421/18423/19822/5584/5585 and
no residual PDF parser containers. Docker Engine/user containers were left running.
Normal ADA data/app, configured database/service, proxy, Ollama, Tailscale, Task
Scheduler and power settings were not operated or deployed.

Final audit: **104 changed/new files** against the original736-file Phase19A/31
inventory, no missing files, no released0001–0020/lock/wrapper changes and0configured
secret matches. The original editor setting was preserved. Whole-tree Ruff
lint/format374files and whitespace checks passed;85 Markdown files had no missing
local link targets. The existing157-path/schema compatibility audit passed.

Phase31's bounded text-PDF implementation/automated exit is complete; all four
checkpoint resolutions are recorded in its plan, with the permitted OCR-off
decision. PDF remains off by default, source requires0021/backup-v7/Android25/
journal18, and installation/enabling is a separate authorized operation described
in the guide. Remaining target acceptance: representative personal files and
reading order/table semantics, TalkBack, older API/device coverage and real-model
answer usefulness. No OCR, archives/Office/URL/directory import, normal app upgrade,
live migration, later-phase implementation or deployment.19A activation/exit remains
open after both failed quality trials; PDF completion does not change that gate.
