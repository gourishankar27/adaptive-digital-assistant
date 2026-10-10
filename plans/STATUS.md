# Phase status

Recorded 2026-10-09 UTC. Update after implementation and verification.
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
| 08 | Planned | Phase 03/current Phase 2; safe versioned upload and provenance contract. |
| 09 | Planned | Phase 03/current Phase 2; scoped entity/alias migration. |
| 10 | Planned | Phase 08; scoped semantic quality measurements; Phase 09 for entity-aware work. |
| 11 | Planned | Phases 07/08; review-based promotion; Phase 09 for canonical links. |
| 12 | Planned | Phase 03 and relevant client; permission and receipt contracts. |
| 13 | Planned | Phases 08/11; durable consolidation jobs. |
| 14 | Planned | Phase 07; explicit preference and bounded session-state contract. |
| 15 | Planned | Phases 11/13/14; consent and provenance for learning. |
| 16 | Planned | Phase 04; stream/reconnect/cancel contract; Phase 06 for monitoring. |
| 17 | Planned | Phases 04/16; explicit audio/transcript boundaries. |
| 18 | Planned | Phases 05/06 and installed feature inventory; recovery/deletion/device credentials. |
| 19 | Conditional plan | Phases 12/18 plus measured device or selected integration requirements. |

Phase 02A's Windows fixture gate is closed. Phase 03's foundation builds and
local HTTP/browser/emulator gates passed. Phase 04 now implements the Android
chat MVP; target-phone/release verification remains distinct from local checks.
Phase 05 now supplies server admin authorization and monitoring metadata.
Phase 06 now supplies the read-only web dashboard. Phase 07 now supplies Android
explicit memory and new static personality profiles. Later feature phases remain
planned, with no deployment.
If work is incomplete, record the checkpoint and exact blocking condition; keep
the usable earlier feature active. Missing device/database checks stay visible.

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
