# Implementation work log

Append new entries. Do not replace user-reported evidence with an unperformed
local run. See CODEX-WORKFLOW for the entry format. No secrets or raw private text.

## 2026-10-08 — planning update and Phase 02A fixture fix

Scope: investigate three installer test failures; write backend, Android and
admin phase plans and persistent engineering instructions. No future app/server
features are implemented by this update.

Changed behavior: test manifests serialize relative migration paths with
`.as_posix()`; a regression exercises PureWindowsPath behavior on any host.
Production installer validation, source code and released migrations are unchanged.
Root and plans AGENTS instructions bind future Codex work to the phase boundary
and the current ownership/evidence/retry standards.

Initial checks: targeted installer suite 4 passed; targeted Ruff checks passed.
Final local checks: full Linux suite 61 passed/50 skipped/1 existing warning in
7.07 seconds; Ruff lint passed; Ruff formatting passed for 35 Python files.
PostgreSQL-dependent cases were not executed in this run. All links in the 28
planning Markdown files resolve locally, the catalog contains all 18 phase
documents, and the three released migration files match the original Phase 2
archive byte for byte.

Target evidence: user's pre-fix Windows/PostgreSQL run reported 105 passed,
3 failed, 2 skipped; the three failures share the manifest-key cause. Successful
real Ollama chat and a v3 prompt upgrade were also reported by the user.
Post-fix Windows/PostgreSQL execution remains unverified in this environment.

Next gate: apply this update, rerun the dedicated Windows suite, then select
Phase 03. A phone, Android build and admin dashboard have not been tested yet.

### 2026-10-08 — Phase 03 checkpoints A–C — base 6a6a278 + working tree

Scope: only contracts, Android/web workspaces, transport/state/design and
connection foundations. Verify the existing 02A target prerequisite and stop
before mobile chat, admin policy/monitoring or later feature work. No deployment,
publication, external messages or production database migration was performed.

Changed behavior/files: explicit output and sanitized error schemas in api.py,
contracts.py and retrieval.py; regenerated contracts/openapi.json; 47 captured
synthetic current/legacy payload fixtures with portable provenance manifest and
actual-response/schema/owner tests. apps/android and apps/admin-web now include
pinned toolchains/locks, scoped AGENTS, Windows READMEs, typed injected HTTP
adapters, test-only mocks, safe errors/unknown enums, 64-bit times, code-point
conversion, identity-change fencing and accessible connection/design previews.
Both enabled connection screens call /me and /capabilities. The web token stays
in memory; Android defines SecureTokenStorage without implementing persistence.
scripts/client_test_server.py supplies an explicit disposable loopback HTTP test
backend. Root/current-state/architecture/UI/decision/status documentation was
updated around the implemented boundary.

Data/API/prompt changes: no migration, route, admin role, enrollment scheme,
request fingerprint, prompt version, model context, transaction or Python
dependency change. Output typing retains historical personality keys, optional
candidate/budget fields and additive trace metadata. Released migrations,
requirements.lock, auth/service logic, Compose database bind and start script
remain unchanged. No schema or prompt upgrade is needed for the foundations.

Checks actually run and results:

- Initial native Windows baseline: pytest 61 passed/50 skipped/1 existing warning;
  Ruff lint/format passed for the original 35 files. scripts/test-postgres.ps1
  then ran the dedicated ada_phase2_test fixtures: 109 passed/2 expected SQLite
  row-lock skips/1 existing warning, closing 02A. This supplements the previous
  Linux/user-reported results; it does not replace them.
- After contract implementation, full scripts/test-postgres.ps1 (pytest -q)
  passed 114 tests with 2 expected SQLite row-lock skips and the same warning.
  The final additive-trace schema refinement was followed by the affected
  test_client_contract.py rerun with dedicated PostgreSQL: 5 passed/1 warning.
  Ruff check and format --check across src/tests/migrations/scripts passed for
  38 files; final scoped contract Ruff passed. OpenAPI equality, actual response
  schema validation, all synthetic fixtures, SQLite/PostgreSQL migration/schema
  checks and owner/replay/failure invariants ran in these suites.
- Android: verified wrapper distribution/JAR SHA-256; generated Gradle locks;
  resolveAndLockAll testDebugUnitTest lintDebug assembleDebug assembleRelease
  --write-locks passed. Fifteen unit tests, 0 failures/skips; lint 0 errors and
  14 dependency-version availability notices; debug and unsigned release APKs
  built. The no-write-lock emulator verification build also succeeded.
  verify-emulator.ps1 provisioned an ephemeral test credential without arguments
  or logs and ran 3 instrumented tests: 0 failures/skips, actual authenticated
  HTTP, real 401 UI and input/theme smoke. The installed debug app cold launched
  with Status: ok. Release APK/resources inspected: target 36, backups disabled,
  cleartext base false and no debug host exceptions.
  Final revised helper run at 2026-10-08 22:00:30 UTC also passed all 3 tests in
  landscape with system fontScale 1.5; cold launch took 1409 ms. Device settings
  and caller ANDROID_SERIAL/ADA_WEB_TEST_TOKEN restoration were verified.
  Final testDebugUnitTest lintDebug assembleDebug assembleRelease --console=plain
  passed with committed locks, without --write-locks (31 seconds; unit report
  2026-10-08 22:01:30 UTC still 15 passed/0 skipped). The helper/token file and
  session-created headless emulator were cleaned up after verification.
- Web: npm ci passed (270 locked packages; audit 0 vulnerabilities), then
  contracts:check, typecheck, lint, test -- --run (28 passed), build and test:e2e
  (3 passed). Real Chromium exercised keyboard/validation focus, theme/large text,
  narrow layout, escaped fixture text, sanitized 401 and a non-intercepted HTTP
  account/capability flow against the disposable backend. Desktop light and
  narrow dark/large-text credential-free PNGs were visually inspected. Browser
  traces/video/credentialed screenshots were disabled; test/dev servers stopped.
- Repository review: released migration and sensitive server configuration files
  have no diff; no credentials/private chats/source quotes were added to plans
  or logs, production fixture fallback or database/provider client was introduced.
  New manifest paths use forward slashes and are checked with PureWindowsPath.
  Independent transport/state review covered account-switch races, unknown states
  and numeric precision; git diff --check passed (normal Windows CRLF notices).
  Local Markdown links in 32 root/plan/app/contract files resolved successfully;
  ports 5173, 18763 and 18764 had no remaining test/dev listeners.

Checks failed during implementation and corrected: Android fixture resource
wiring, MockWebServer IPv6 host, ambiguous internal AGP lock resolution, local
Windows properties escaping and PowerShell Gradle-property quoting; old
transitive Espresso 3.5.0 failed reflection on
API 37, fixed with the officially documented compatible 3.7.0 test pin. The web
real-browser run exposed fetch's receiver binding, fixed in the production
adapter. Review caught future fractional optional JSON rejection, corrected
without reducing int64 validation. Relevant tests were rerun after fixes; no
failing check was suppressed or recorded as passing. Existing Python dependency,
web transitive encoding and browser terminal-color warnings are separate notices.

Windows/PostgreSQL/device/model evidence: Windows 11, existing Python 3.12.10,
FastAPI 0.142.4/Pydantic 2.13.5/pytest 9.1.1/Ruff 0.16.10. Android Temurin
21.0.12.1+1, Gradle 8.13, AGP 8.11.1, Kotlin 2.2.21, Compose BOM 2025.10.00,
SDK 36 revision 2/Build-Tools 35.0.0; installed Medium_Phone_API_37.0 reports
Android 17/API 37 using WHPX. User confirmed Samsung S24 FE/Android 16, compatible
with minSdk 26; it was not physically tested. Web Node 24.12.0/npm 11.6.2,
React 19.3.0/TypeScript 5.9.3/Vite 8.3.4/Router 7.18.4/Query 5.104.1,
Vitest 5.0.3/ESLint 10.12.0/Playwright 1.64.0/Chromium 156.0.8078.4 (build 1248).
Both client HTTP flows used migrated disposable SQLite and FakeProvider without
generation; the server suite independently exercised PostgreSQL. No new real
Ollama, GPU, citation-quality or production-chat evidence is claimed.

Checks skipped/remaining target verification: the two SQLite lock variants skip
by design while PostgreSQL versions execute. Physical S24 FE installation and
actual-server USB/private-network flow, release HTTPS, TalkBack/manual screen
reader, target keyboard/display/zoom/landscape and long-content checks remain.
Keystore enrollment, encrypted pending journals, chat/source/memory workflows,
server admin authority and monitoring are later selected phases, not completed
by these foundations. Earlier real-model performance/quality limits remain.

Next eligible checkpoint: select Phase 04 for Android storage/enrollment/chat;
Phase 05 may separately add server admin authorization. Phases 04/05/06 remain
planned. Stop at Phase 03; no deployment is authorized or performed.

## 2026-10-08 — Android appearance follow-up — base 6a6a278 plus Phase 03 working tree

Scope: the user's Android theme-only request; Oxford Blue as the main/default
palette, with Dark Red and Olive Green choices in Settings. No later phase.

Changed behavior/files: Theme.kt defines complete semantic light/dark schemes
around #002147, #350616 and #3C4C24. AppearanceSettings.kt provides accessible
radio choices, color swatches, dark-mode switch and device-local preferences.
MainActivity applies the chosen theme around the entire scaffold and aligns
system-bar icons with the mode. FoundationScreen opens Settings and retains the
larger-text preview. Existing FoundationSmokeTest now verifies palette/mode
selection and reload after activity recreation. Android README and STATUS record
the flow and new evidence; earlier Phase 03 evidence is preserved.

Data/API/prompt changes: none. Appearance preferences store only a stable palette
key and dark-mode boolean; missing/unknown keys default to Oxford Blue. No private
ADA data or credentials are persisted. Existing secure-window/backup controls,
authentication/HTTP, migrations, OpenAPI and dependency locks remain unchanged
by this follow-up. No new dependency, server feature or architectural deviation.

Checks actually run and results:

- Inspected current Android sources, API/OpenAPI baseline, tests and repository
  instructions before edits. Baseline Android testDebugUnitTest/lintDebug/
  assembleDebug passed. Baseline `.venv/Scripts/python.exe -m pytest -q`:
  64 passed, 52 skipped, 1 existing Starlette/httpx deprecation warning. Ruff check
  and format --check over src/tests/migrations/scripts passed, 38 files formatted.
- After implementation, testDebugUnitTest/lintDebug/assembleDebug/assembleRelease
  passed. Lint initially suggested the existing KTX preference editor; changed
  to that extension without adding a dependency. The final same command passed
  with 15 unit tests, 0 failures/skips, lint 0 errors and 14 existing dependency
  availability notices; debug and unsigned release APKs built without rewriting locks.
- `scripts/verify-emulator.ps1 -Device emulator-5554` passed all 3 instrumented
  tests, 0 failures/skips, and cold launched the actual debug activity (Status:
  ok). This included appearance controls and the existing authenticated/rejected
  real HTTP checks against disposable migrated SQLite and FakeProvider.
- Final appearance smoke at 2026-10-08 23:59:20 UTC: connectedDebugAndroidTest
  with the FoundationSmokeTest#launchesLabelsInputsAndThemePreview runner filter
  passed 1 test, 0 failures/skips, in landscape at system font scale 1.5. The test
  exercises all three palettes in both modes and saved preference reload after
  activity recreation. Emulator font scale/rotation and caller serial environment
  were restored.
- Local relative-luminance calculation: checked semantic text pairs exceed
  4.5:1 (minimum blue 6.38, red 6.42, olive 5.59); checked control outlines exceed
  3:1 (minimum 3.77, 3.98, 3.48). This is color calculation evidence, not a full
  manual accessibility or physical-device visual review.
- Final review: git diff --check and affected-file whitespace checks passed.
  The standalone checker initially used Windows' default text encoding; reran
  successfully with explicit UTF-8. The disposable HTTP listener was absent and
  the session-created emulator stopped successfully.

Checks skipped and reason: the baseline's 52 pytest skips reflect unprovisioned
PostgreSQL fixtures/SQLite lock variants. Dedicated PostgreSQL and web checks were
not rerun for this Android appearance-only change; no server/schema/concurrency
or web implementation changed. Physical-phone installation, TalkBack/keyboard,
visual/IME, release HTTPS and real-model checks were not performed.

Windows/PostgreSQL/device/model evidence: Windows 11; existing pinned JDK 21,
Gradle 8.13, AGP 8.11.1, Kotlin 2.2.21, Compose BOM 2025.10.00 and SDK 36.
The session-created emulator was Android 17/API 37 using WHPX. The helper/token
file and emulator were cleaned up. User's Samsung S24 FE/Android 16 remains the
physical target; no new physical-phone, production-database or Ollama evidence.

Remaining issues: target-phone palette appearance and manual accessibility/IME
review. Earlier Phase 03 target limits remain. Next eligible work: only another
explicitly selected task/phase; this theme follow-up stops here with no deployment.

## 2026-10-09 UTC — Phase 04 A–D — base 6a6a278 plus preserved Phase 03/theme working tree

Scope: only `phase-04-android-chat-mvp.md`, followed by the user's explicit
checkpoint verification request. Read root/scoped instructions, README,
architecture, CURRENT-STATE, STANDARDS, CODEX-WORKFLOW, STATUS and Phase 04;
inspected current Kotlin/server source, exported OpenAPI, released migrations
and tests. Existing authenticated routes and Phase 03 foundations satisfied
the prerequisites. Preserved all prior user/theme and Phase 03 edits/evidence.

Changed behavior/files:

- `SecureSessionStore.kt`: bounded atomic Keystore AES-256-GCM credential/exact
  pending record under noBackupFilesDir, identity fencing, UUID-bound cleanup,
  no plaintext fallback and reconnect after key loss/corruption. Store commits
  precede HTTP. Logout cleanup completes before another connection is allowed.
- `ChatViewModel.kt`/`ChatState.kt`: verified enrollment/restore/token replacement;
  owned paginated creation/history and explicit prompt upgrade; separate drafts,
  immutable reservations and server status; bounded same-ID GET polling, explicit
  original-payload retry/missing submission; owner/switch/revocation fences and
  stale-history choices. Unicode/historical options follow existing server limits.
- `ChatApp.kt`/`ChatSourceCard.kt`/`SafeChatText.kt`: real conversation/chat/settings,
  accessible request progress/actions, exact original source cards and separate
  retrieval details; selectable literal content and explicit safe HTTP(S) links.
  Short viewports scroll context/recovery with history; typing frees space for
  the composer. MainActivity consumes system insets and uses adjustResize while
  retaining FLAG_SECURE. Oxford Blue/Dark Red/Olive palettes remain intact.
- `AdaApi.kt`: fixed allowlist of sanitized error codes, numeric/HTTP-date
  Retry-After and one-shot POST bodies. Explicit retries preserve exact bytes;
  OkHttp cannot silently repeat creation/chat POSTs on immediate 503 follow-up.
- Added JVM/Keystore/Compose invariants and real HTTP smoke/recovery tests.
  The explicit test-only Android helper flag seeds synthetic owned evidence;
  the default web helper behavior is unchanged. The emulator script privately
  provisions a temporary credential, runs the full HTTP flow, then performs two
  distinct instrumentation stages with actual adb force-stop between them.
- App label is ADA, version `0.4.0-chat-mvp`/code 2. README, architecture/mobile
  boundary, plans and decisions describe implemented behavior and target limits.

Data/API/prompt changes: no backend source, schema, migration, API/capability,
provider, request-fingerprint or prompt-snapshot change. Eight server/OpenAPI/
released-migration SHA-256 hashes matched the phase-start values. No native
database/provider connection or new dependency/lock refresh. The only private
client persistence is encrypted credential/pending intent; appearance preferences
remain nonprivate. No memory writer, streaming, cancellation, voice, tools, admin
authority or device inference was added.

Checks actually run and results:

- Baseline Android testDebugUnitTest/lintDebug/assembleDebug passed with 15 unit
  tests. Baseline `.venv/Scripts/python.exe -m pytest -q`: 64 passed/52 skipped/
  1 existing Starlette/httpx warning; Ruff lint/format passed for 38 files.
- Added-helper regression: one SQLite case passed/one PostgreSQL case skipped
  before provisioning fixtures. Full `scripts/test-postgres.ps1` then passed
  116 tests with 2 expected SQLite-only row-lock skips and the existing warning.
  Ruff check/format --check over src/tests/migrations/scripts passed for 39 files.
- Android full build/check runs passed first 49 and then 51 unit tests. The
  pinned OkHttp creation regression failed before the one-shot fix; the scoped
  HTTP suite then passed all 12 tests. Full suite later passed 55 tests.
  Final checkpoint audit added two explicit prompt-update tests: the scoped
  28-case ViewModel suite initially failed those two because refresh erased the
  result notice; preserving feedback after refresh fixed both. Final
  `testDebugUnitTest lintDebug assembleDebug assembleRelease --console=plain`
  passed all 57 tests (4 contract/12 transport/9 storage/28 chat/4 foundation),
  no failures/skips; lint 0 errors/14 existing dependency notices; both APKs built.
- Initial compile checks failed on a nonpublic directory-open constant and an
  invalid test import; corrected both without suppressions. Initial emulator
  run: 8/10 passed, 2 UI assertions failed and were corrected. A complete normal
  run then passed 11 ordinary tests and both actual force-stop stages/cold launch.
- Smallest-width 320dp landscape/font1.5 run initially passed 6/11, exposing
  lazy-scroll and keyboard viewport gaps. Actual layout/inset fixes and explicit
  IME/composition waits yielded 9/11, then 10/11, then all 11/11 plus both staged
  force-stop checks with no skips. Font/density/rotation were restored. A normal
  rerun initially passed 10/11 because a navigation action raced keyboard
  dismissal; corrected the wait instead of bypassing real UI submission.
  Final restored normal-layout helper run at 2026-10-09 09:04:54 UTC passed all
  11 ordinary tests/0 failures/0 skips, both actual force-stop stages and cold launch.
- aapt2 inspected release manifest/resources: code 2/version 0.4.0-chat-mvp,
  SDK 36, disabled backup/cleartext and full backup/transfer exclusions. Debug
  had exactly the three documented local HTTP hosts. Release optimization renamed
  XML entries, so the first resource-path query failed; the resource map resolved
  the actual entries and their inspections passed. PowerShell script syntax,
  git diff --check and UTF-8/whitespace/local Markdown link checks passed.
- Final cleanup verified removal of the temporary credential and synthetic
  encrypted session/journal, absence of the helper listener, restored emulator
  font/density/rotation and successful shutdown of the session-created emulator.

Checks skipped/blocked and reason: baseline's 52 pytest skips reflected missing
PostgreSQL/SQLite lock variants; final dedicated fixtures left only the two expected
SQLite skips. No physical device was attached. S24 FE/Android 16 install, real
network interruption, release HTTPS, real Ollama/known-memory demonstration,
TalkBack/hardware keyboard/manual visual/IME/copy selection and API 26 testing
remain unperformed. Web checks were skipped because web behavior was unchanged.
No unavailable check is recorded as passing.

Windows/PostgreSQL/device/model evidence: Windows 11, Python 3.12.10, pinned JDK
21.0.12.1+1, Gradle 8.13, AGP 8.11.1, Kotlin 2.2.21, Compose BOM 2025.10.00,
SDK 36/minimum 26. PostgreSQL fixtures were real dedicated test schemas. Emulator
was Android 17/API 37/WHPX; landscape density 540 on 1080×2400 gives smallest
width 320dp. HTTP was the actual migrated ADA server with disposable SQLite,
ephemeral synthetic owner, explicit test evidence and FakeProvider. Delivery loss
was simulated after a real commit; process death between stages was real. No
production data, real Ollama generation, latency/GPU/battery measurement or
physical-phone outcome is claimed.

Remaining issues: target verification listed above; this is an implemented,
locally checked MVP, not a completed signed/distributed release. Prior validation
evidence remains historical. Next eligible checkpoint: only separately selected
work, such as Phase 07 memory forms or Phase 05 admin authorization. Stop at
Phase 04; no later implementation, commit, deployment or external message.

### 2026-10-09 UTC — Phase 05 checkpoints A–C — base b828192 + working tree

Scope: only plans/phase-05-admin-monitoring-api.md. Read root/scoped instructions,
README/architecture/current-state/standards/workflow/status and actual source,
OpenAPI and tests first. Phase 03 prerequisite was present; starting Git tree was
clean. No delegation, later phase, deployment, application DB migration or actual
user grant was performed. Earlier work-log entries remain historical.

Changed behavior/files: add explicit server admin grants, fixed-field rolling audit
and serializing state row, six typed metadata GETs, bounded indexed filters/window/
pagination, SQL JSON scalar retrieval summaries, rate-limited/no-store monitoring,
pre-response audit/current-role recheck, sanitized DB/provider/audit failures and
cached generation-free Ollama health. Preserve private owner APIs, request IDs,
frozen prompts, evidence/replay and one-worker semaphore. Safe tag/error allowlists,
null/zero distinction and explicit unknown GPU/throughput are documented. Add
operator/API guide; update current docs/plans and export OpenAPI/web DTOs only.

Data/API/prompt changes: new migration 0004 after immutable 0003; no implicit grants
and no edits to released 0001–0003 (baseline/final SHA-256 matches). Local grant-admin/
revoke-admin take UUIDs and audit atomically. Audit uses real HTTP principal IDs
or a reserved trusted local-operator ID; no individual human attribution is claimed.
Audit is bounded to 10,000 logical rows/30 days, lazily pruned on audited operations;
queries hide expired rows. Monitoring allows 60/principal and 600/global calls per
sliding minute, with bounded/suppressed throttle audit volume. Existing 21 paths
remain identical in OpenAPI; existing schema comparison shows only an additive
admin_monitoring capability. No input fingerprint/prompt upgrade/auth-token change.
FastAPI minimum is now 0.121 for function-scope dependencies; pinned 0.142.4 and all
lockfiles remain unchanged. The old upgrade-smoke expected target head is now 0004.

Checks actually run and results:
- Baseline pytest -q: 65 passed/53 skipped/1 existing warning. Dedicated baseline
  scripts/test-postgres.ps1: 116 passed/2 expected SQLite lock skips. Ruff lint and
  format clean for 39 files.
- Final ordinary pytest -q: 80 passed/69 skipped/1 existing warning. Final dedicated
  scripts/test-postgres.ps1 with process-local ADA_TEST_OLLAMA_HEALTH=1: 147 passed/
  2 expected SQLite lock skips/1 existing warning (38.06 s). Initial implementation
  dedicated run was 137 passed/4 skipped; later interim real-probe run was 143 passed/
  2 skipped. These are separate actual runs, not reused baseline evidence.
- After the final bare-model-name/latest matching refinement, the affected mocked
  cached/failure probes and actual local Ollama cases reran: 4 passed/25 deselected
  on SQLite/PostgreSQL. Final Ruff lint/format: passed for 46 files.
- Tests cover populated 0001/0003 upgrades and alembic check, immutable replay/prompt/
  token snapshots, composite duplicate IDs, owner-only access, every admin route's
  unauthenticated/ordinary/granted/revoked cases, forged claims and model expression,
  atomic audit failure, parallel grants/revocation during network I/O, index EXPLAIN,
  filters/pagination, aggregation/null/zero values, actual evidence-summary leakage,
  legacy traces, retention/rates, unavailable DB/audit/provider and bounded probes.
- Actual socket HTTP/CLI subprocess flow passed on disposable SQLite and PostgreSQL:
  one-worker loopback server, actual grant/revoke commands, fake-model request,
  cross-owner metadata, private owner-only 404 and immediate revocation. Synthetic
  body/token/digest scans of runtime output passed. Actual local Ollama GET /api/tags
  probes passed; ADA request counts unchanged and no generation invoked. Connection
  pool assertions in mocked probes verify no open DB transaction during network I/O.
- OpenAPI regenerated, all existing paths/schemas compared against pre-change export,
  closed admin response schemas validated against HTTP responses, released migration
  hashes checked, git diff --check passed. Temporary schemas cleanup checked.
- Retrieval evaluation scripts ran on disposable SQLite and PostgreSQL: recall@5
  0.8667 both, MRR@5 0.8667/0.8333, exact-evidence coverage 1.0 and zero scope/negative
  failures. Ignored reports under .pytest_cache retain this run's synthetic evidence.
- Web: npm ci installed 270 locked packages (audit 0 vulnerabilities); generated DTO
  check, typecheck, lint, 28 unit tests, production build and 3 Chromium tests passed.
  Browser tests include keyboard/narrow foundation and actual migrated SQLite HTTP.
  Final regenerated int64 DTOs passed contracts:check/typecheck/lint. No dashboard
  transport, screen or workflow was implemented. Package lock remained unchanged.
- Early collection failed on an omitted Boolean import; it was fixed. A streamed
  probe test initially used an already-consumed MockTransport response; the fixture
  was corrected to a byte stream and tests passed. Interim Ruff format failures were
  corrected and final checks passed. Standalone PostgreSQL evaluation initially
  lacked ADA_TEST_DATABASE_URL; a process-local dedicated URL rerun passed. A shell
  quote error in DB-version inspection was corrected with a single-quoted Python
  here-string; the actual metadata read then passed. No credentials were printed.

Checks skipped/blocked and reason: ordinary-run PostgreSQL/SQLite-lock/opt-in skips
are distinct from the final dedicated run's two expected SQLite exclusions. The
legacy standalone smoke script needs an old Phase 1 tree and was not run; populated
upgrade/replay tests plus the new socket/CLI test ran instead. Android/emulator/
physical-phone checks were skipped because Android source/themes were unchanged.
No production migration/grant, release/private HTTPS, actual inference/citation,
GPU/throughput, sustained monitoring load or backup/retention measurement ran.

Windows/PostgreSQL/device/model evidence: Windows workspace, Python 3.12.10,
PostgreSQL 17.11 (dedicated ada_phase2_test with disposable schemas), existing pinned
Python/Node/npm/browser tools. PostgreSQL server reports Debian 17.11, not a native
Windows database build. Backend fixtures separately exercise SQLite. Actual local
Ollama metadata was read only; fake model used for socket/browser generation tests.
Synthetic timings and null performance fields are not real-model performance data.
All subprocess servers were stopped and temporary schemas disposed. Environment
probe flags/test URLs were scoped/restored; production configuration was unchanged.

Remaining issues: install migration 0004 into the intended backed-up application DB
and intentionally grant the chosen account when installation is requested. Verify
HTTPS/target operations, sustained polling/audit contention and real performance
separately. Preserve prior physical S24 FE/Android 16/release/accessibility limits.
See STATUS and docs/ADMIN-MONITORING.md for operational role/retention boundaries.
Next eligible checkpoint: separately selected Phase 06 admin web dashboard; stop
at Phase 05 now. No deployment or later implementation is authorized/performed.

Final record review at 2026-10-09 10:01:10 UTC: UTF-8/NUL checks passed for all
29 changed/new files; relative links passed for 13 Markdown documents. Final
git diff --check passed and disposable test/evaluation schema cleanup was rechecked.

### 2026-10-09 — Phase 06 checkpoints 0/A–D — base b828192 + preserved Phase 05 working tree

Scope: implement only phase-06-admin-web-ui.md, including its user-added palette
checkpoint. Read root/plans/web instructions, README/architecture/current state,
standards/workflow/status/UI-SPEC/phase and current source/OpenAPI/tests. Verified
Phase 03 scaffold, six implemented Phase 05 admin routes and migration head 0004.
Preserved all pre-existing Phase 05 and user plan edits. No subagents or later
phase work, application DB migration, real account grant, deployment or messages.

Changed behavior/files: HttpAdminApi projects safe typed metadata only; AdminSession
verifies admin-me, holds credentials outside caches and fences/clears/aborts state
on identity change or 401/403. `/admin` sign-in/overview/provider/request/detail/
audit/Settings routes now call actual APIs. Query keys include server/principal/
epoch/filters and composite owner/request identity. Views use server pagination,
bounded UTC filters, actual counts/coverage/timeline/retrieval budgets and explicit
legacy/unknown/zero/unavailable/degraded/stale states. Polling is 30-second visible
only, without automatic retries, with a session Retry-After cooldown. Text stays
escaped; no private chat/prompts/quotes/retrieval endpoint or production fixture.

Settings defaults to Oxford Blue #002147, with Dark Red #350616 and Olive Green
#3c4c24; each has light/dark/system brightness and standard/large text. Only those
enum preferences use localStorage. Native labelled controls, skip link, captions/
column headers/scrollable table regions and stable focus support keyboard/zoom.
Configuration/audit are read-only; no operational write controls or invented charts.
Updated web/root READMEs, architecture/current state/status/phase and references.

Data/API/prompt changes: none. SHA-256 comparison matched all **10** Phase 06
baseline files (server API/monitoring/admin/models, exported OpenAPI, Python lock
and migrations 0001–0004). Web package lock/pins stayed unchanged. Phase 05
uncommitted additions remain present; they are not new Phase 06 server changes.
No capability/schema/prompt/replay/provider contract changed. New browser helper
and seven guard tests operate only on dedicated PostgreSQL disposable schemas;
existing Android/SQLite helper behavior is unchanged.

Checks actually run and results:

- Baseline ordinary pytest: **80 passed/69 skipped/1 existing warning** (17.68 s).
  Ruff lint/format passed for 46 files. Web contracts:check/typecheck/lint/unit/
  build/e2e passed: **28 unit**, **3 Chromium** foundation tests.
- Clean npm ci installed **270 locked packages**, audit **0 vulnerabilities**.
  Contracts check, typecheck/lint, **43 interim unit tests** and build passed. Unit
  invariants cover current/late revoked auth, switch/abort/cache cleanup, Retry-After
  including sign-in/navigation, hidden polling, stable focus, composite detail keys/
  response identity, allowed-field projection, int64 precision, filters/back/empty
  states, literal model text, null/zero/unknown/legacy metadata and preferences.
- Actual development-browser intermediate run: **4/4 passed**, followed by a
  **5/5** run (15.4 s) after the escaping test was scoped to rendered main. Built-SPA
  same-origin preview (`ADA_WEB_BUILD_SMOKE=1 npm run test:e2e`) passed **5/5**
  Chromium tests, **14.2 s** initially. `/admin` deep-route fallback/assets and fixed `/v1`
  proxy use real one-worker ADA HTTP plus migrated dedicated PostgreSQL schema.
  Actual sign-in, ordinary denial, local grant/revoke, second operator switch,
  stale-state removal, two owners sharing UUID, pagination, legacy/known summaries,
  recorded zero tokens, failed request and audit are server/DB evidence. 401/429/
  503 and unknown/degraded tags are explicitly intercepted UI fixtures.
- Successful test chat seeds use FakeProvider through owned APIs. A real local TCP
  refusal produces a recorded provider_unavailable failed request and unhealthy
  provider metadata; it does not exercise successful inference. Separate opt-in
  local Ollama **GET-only** health tests passed **2/27 deselected** on SQLite and
  PostgreSQL, unchanged request counts. No real inference/GPU/throughput test ran.
- Keyboard skip link/form feedback/main focus/table traversal, refresh focus,
  390px layout, 200% CSS zoom and system-media preference checks passed. All six
  palette/brightness combinations passed checked semantic text/muted/button 4.5:1
  and focus/boundary 3:1 thresholds. Wide blue/light, wide red/dark and narrow
  olive/light signed-out Settings captures were visually inspected. No credentials
  or monitoring identities appeared in them; no credentialed capture/trace/video.
- Final ordinary pytest: **87 passed/69 skipped/1 warning**, **20.15 s**. Targeted
  browser-fixture safety: **7 passed**. Dedicated scripts/test-postgres.ps1:
  **152 passed/4 skipped/1 warning**, **44.21 s**. Skips: two expected SQLite row
  locks and two opt-in real-health cases, the latter checked separately as above.
  The full suite exercises schema/populated upgrade/drift/replay/ownership,
  monitoring role/rate/concurrency/audit failures and real socket/CLI boundaries.
  Ruff lint/format passed for **48 files**.
- Corrected interim failures: mock literal types and an ambiguous unknown label;
  helper .env resolution from the web cwd caused DB authentication failure (fixed
  root resolution, sanitized errors); audit selector matched a hidden option;
  production contrast parser omitted 3-digit minified hex; final dev escaping
  assertion matched Vite's own inline script (scoped to rendered dashboard main).
  None of these failures or required assertions were suppressed. Existing
  Starlette/httpx, whatwg-encoding and NO_COLOR notices remain separate warnings.

Checks skipped/blocked and reason: Android/emulator/physical S24 FE tests because
Android is unchanged. Manual screen-reader/full assistive review, Firefox/Edge/
other browsers, real HTTPS hosting, target-network/offline recovery, production
data sizes, sustained polling/audit/performance are pending. CSS zoom/semantic
tests are automated evidence, not manual assistive-device certification.

Windows/PostgreSQL/device/model evidence: Windows/Python 3.12.10, PostgreSQL
17.11 (Debian server on this host) using dedicated ada_phase2_test and disposable
schemas; pinned Node 24.12.0/npm 11.6.2 and Playwright Chromium. Fixture successes
are fake-model; connection-refusal failures and local metadata probes are actual
network evidence. No synthetic timings imply real-model or production performance.

Remaining issues: intended Phase 05 application-DB install and real UUID role grant
remain a separately requested installation step. Release HTTPS and manual/browser/
load checks remain visible in STATUS. Preserve prior physical-phone/Android limits.
Next eligible checkpoint: only a separately selected later phase. Stop at Phase 06;
no deployment or operational write controls were performed.

Final review follow-up at 2026-10-09 20:09:58 UTC: two new regression tests failed
before fixing millisecond loss when reapplying a returned pagination window and
chat-submission wording inherited by monitoring errors. Date inputs now preserve
seconds/milliseconds and the admin adapter uses fixed read-only error messages.
Malformed non-string provider health states are rejected at decoding. After these
refinements, typecheck/lint, **45 unit tests**, build and **5/5** production-build
Chromium tests passed (**14.3 s**). Server/OpenAPI/schema/locks remain unchanged.

Final verification/cleanup at **2026-10-09 20:13:52 UTC**: added actual-browser
reapplication of frozen millisecond filter bounds; final dev **5/5** (**15.4 s**)
and preview **5/5** (**14.6 s**) passed. Measured Oxford Blue input-background
border contrast was **2.9601:1**; a small border-color adjustment raises it to
**3.1998:1**. Typecheck/lint/build and the final **5/5** built-SPA browser run passed
(**14.5 s**) with input-background boundary coverage for all six palette/mode
combinations. Unit suite remains **45 passed**; CSS/test-only follow-up did not
change Python/server behavior. UTF-8/NUL checked **53 changed/new files** across
preserved Phase 05 + Phase 06; **53 relative links/14 documents**, git diff --check,
all **10** baseline SHA-256 values and unchanged web lock passed. Final disposable
browser/suite schema count was zero; all task API/Vite/preview listeners stopped.
Appearance artifacts are ignored signed-out local captures; no credentialed
recording was retained. No production data/grant/deployment or later phase changed.

### 2026-10-09 — Phase 07 checkpoints A–D — base b828192 + working tree

Scope: only Android memory/evidence/correction and static personality screens.
Preserved all prior Phase 05/06/user working-tree changes. Read requested/scoped
instructions, current source/OpenAPI/migration head and test baseline first;
Phase 04 and existing memory/personality endpoints met prerequisites. Stop here;
no later feature, deployment, production migration or real-account grant.

Changed behavior/files: MemoryController/MemoryState/MemoryScreens and ChatApp/
ChatViewModel navigation, owned scope/claim/source pagination, current/as-of/
history, exact source detail and replacement links. Remember/correction forms
preview annotation/value/time/evidence before explicit Save. Read-only UTF-16
selection converts to code points without altering source bytes. User trust,
scope, SHA-256 and quote checks reject model-source promotion. Effective intervals
and future superseded rows follow server semantics; competing assertions are
advisory and loaded slot grouping avoids unrelated pairwise comparisons.

PendingMemory/SecureSessionStore add immutable owner/scope reservations and a
durable returned-note stage, preserving original IDs/input across interruptions.
401 halts writes and clears private state, including a late same-session read
from an old view. Conflicts/validation retain input for checking/identical replay;
explicit recovery discard deletes no remote evidence. Failed secure commit stops
POST; failed cleanup blocks a new write. Original chat citation maps never change
after correction. Settings exposes all current static enums/name, creates new
profiles for new conversations and keeps verified selection beyond page one.
Existing personality/prompt snapshots and explicit supported upgrade remain frozen.

Data/API/prompt changes: only additive encrypted local record v2; reads v1
credential/chat recovery with unchanged file/key/AAD and a bounded 128 KiB record
for two concurrent journals. Token rotation retains both only for verified same
server/owner; switch/logout/401 clears them. Form drafts stay in ViewModel memory
through rotation, not plaintext saved state. Android versionCode 3/name
0.7.0-memory. No server/OpenAPI/migration/prompt/dependency changes; all 31 captured
baseline hashes match, including released migrations and current locks/catalog.

Checks actually run/results:

- Baseline pytest 87 passed/69 skipped/one existing warning. Android unit/lint/
  debug tasks succeeded with cached unit/lint tasks identified as up-to-date.
  Ruff lint/format passed for 48 files at baseline and final review.
- Invariants added before write expansion: 1 expected transport-code red test,
  9 expected journal red tests, then 26 contract/HTTP and 22 storage focused tests
  passed. Later regression checks failed before fixes for changed-after-commit
  recovery, late 401 and off-page profile selection. Updated an old creation test
  to select an actually owned profile under the strengthened guard.
- Final Android unit/lint/debug/unsigned release/test-APK build passed: 98 unit
  tests, zero failures/skips; lint zero errors/14 existing dependency notices.
  Repeated after a real emulator selection defect; final full build passed again.
  A transient Windows R.jar lock was resolved by stopping Gradle/rebuilding.
- scripts/test-postgres.ps1: 152 passed/4 skips/one existing Starlette/httpx warning,
  41.08 seconds. Two SQLite row-lock and two opt-in provider-health skips remain;
  no skipped case was presented as executed. No production data/schema change.
- First emulator: 19 passed/2 failed. Pinned Compose collapses readonly selection
  on focus loss: Preview now reserves the reviewed span before clearing focus.
  The other failure was a test IME/navigation race; explicit keyboard dismissal/
  nav wait resolves it. No failing check was disabled or suppressed.
- Final emulator script: 21 passed/zero skips, followed by 2 original chat and 2
  new memory actual force-stop stages passed. Four new synthetic Compose flows
  use injected fixtures; four new memory tests exercise real authenticated HTTP
  and migrated disposable SQLite. Unicode/replay/conflict/denied IDs/model trust,
  future history, correction end boundary, frozen personality and original saved
  fake-chat citations passed. Long evidence/validation focus passed through the
  production restored memory UI. Note-success/claim-failure recovery retains exact
  source/claim IDs/input and verifies one note/claim after explicit Resume.
- APK policy/version inspection and PowerShell script parse passed. Release is
  unsigned; no cleartext host exception or backup. Debug has only its three
  documented hosts. Markdown/link and diff/encoding review are recorded in STATUS.

Windows/PostgreSQL/device/model evidence: pinned JDK21/Gradle8.13/SDK36, Android
17/API37 WHPX emulator, 480×320 dp landscape with 1.5× system text. This is local
emulator verification, not the user's Samsung S24 FE/Android16. Test server is
one-worker loopback with explicit FakeProvider; no actual Ollama generation was
performed for this phase. Prior actual-model evidence remains historical above.

Final cleanup at 2026-10-09 22:30:46 UTC: temporary app-private credential absent,
disposable HTTP listener stopped, display/font settings reset, task emulator
shut down. Debug cold launch passed. No private screenshot/recording retained.

Checks skipped/remaining issues: physical phone is not attached; trusted release
HTTPS, TalkBack/hardware keyboard/manual visual/selection review, API26 behavior,
actual-server token/network interruption and real Ollama/source-quality smoke
remain target checks. Admin web checks were not rerun because web code is unchanged
in this phase. Intended application migration/HTTPS setup remains outside this
client implementation. Optional retrieval preview/search was omitted; no document
upload, extraction/proposals, mood/relationship learning, tools or deployment.

Next eligible checkpoint: Phase 08 only if separately selected; all later phases
remain planned. Phase 07 target verification remains visible in STATUS.

Final documentation/encoding review: 43 Markdown files/59 local links all resolve;
79 combined preserved Phase 05/06 + Phase 07 changed/new text files are UTF-8/NUL
clean, 31 baseline hashes still match and later phase files are unchanged.
Repository-configured git diff --check passed. A preliminary override disabling
autocrlf treated existing CRLF endings as trailing whitespace; the correct check
used the repository's normalization, without rewriting preserved files.
