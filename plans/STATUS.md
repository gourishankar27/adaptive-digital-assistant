# Phase status

Recorded 2026-10-12 UTC (2026-10-12 in America/Phoenix). Update after implementation and verification.
“Planned” means a specification exists, not that code or a working UI exists.

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
0015 before operational use. Phase 09 supplies explicit scoped identities and
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
