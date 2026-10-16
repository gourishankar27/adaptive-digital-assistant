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

## 2026-10-10 UTC — admin login repair and Phase 08 — base `1ca228a` plus working tree

Scope: fix the reported admin login failure, then implement only Phase 08
text/Markdown checkpoints 1–4. Required/root/scoped instructions, current source,
OpenAPI, migration state and test baselines were read before changes. Phase 2 and
Android Phase 03/04/07 prerequisites existed. No later phase or Phase 08 deployment.

Changed behavior/files: safe fixed admin readiness guidance, without displaying
raw error bodies; new document service/API/contracts and migration 0005; exact
chunks and native lexical projection; typed imported document retrieval/cards;
Android Documents, exact preview, explicit upload/version/excerpt reads and
encrypted same-ID recovery; OpenAPI/web DTO export and related tests/corpus/docs.
Server/Android/web dependencies, locks, wrappers and catalog remain unchanged.

Data/API/prompt changes:

- Owner-bound raw blobs and upload fingerprints retain exact UTF-8 content,
  metadata, availability and stable source/new version identities. Reserve, parse
  outside transactions, validate then atomically publish all version/chunk/index
  rows. Failed/processing receipts remain private with no partial searchable text.
  Quotas count failures; 30-second leases and three attempts fence explicit replay.
- Migration 0005 follows byte-preserved released 0001–0004. Imported/untrusted
  evidence cannot support the existing user-claim writer. Dedicated authenticated
  raw/status/version/chunk routes preserve legacy source DTO trust enums.
- `use_documents` defaults false and requires memory enabled. Original hashes,
  claim arrays, exact v3 prompts and completed replay survive. v3 claim retrieval
  remains supported; v4 document context requires explicit audited upgrade for
  old conversations. New conversations freeze v4. D cards/snapshots are separate,
  owner/scope/publication/availability checked before candidates/context, and
  complete excerpts share existing budgets. Model I/O remains outside transactions.
- Android `0.8.0-documents`/versionCode 4 uses a stricter 64 KiB upload bound and
  encrypted record v3/256 KiB. It reads v1/v2, keeps exact pending chat/memory/document
  IDs/bytes, verifies identity and never automatically writes after restoration.
  Current capabilities gate controls; old request cards retain original versions.
- PDF checkpoint explicitly deferred. No OCR, archives, remote fetch, embeddings,
  extraction/promotion, new dependencies or automatic retention/deletion service.

Admin repair evidence and authorized application change:

- Read-only configured-database diagnosis found head 0003. In-process liveness
  200/readiness 503 reproduced `database_not_ready`; admin policy requires migration
  0004 and an explicit existing-account grant. Browser origin is the documented
  same-origin Vite proxy. No active 8000/5173 listener was available to verify the
  user's actual browser session.
- User explicitly selected account `gourishankar`. Unique existing-name lookup
  resolved its exact UUID; the server grant used that UUID, not name-based authority.
  A private custom-format pg_dump backup was validated with pg_restore listing
  before mutation. Native Windows path output attempts failed, with no DB mutation;
  Python-owned binary streams produced the verified 69,300-byte archive.
- At 03:51:22 UTC the configured application DB upgraded **0003→0004 only**, with
  the explicit audited admin grant. Existing table row counts were preserved.
  No private chat/source read, token rotation or provider generation was performed.
  The backup stays outside the repository. No secret/DSN is recorded here.
- **0005 is not installed in that application database.** Running this new source
  requires a separate backed-up 0005 installation and one-worker restart. The
  requested login repair and Phase 08 source readiness are distinct. No live
  user-browser success is claimed. Known web readiness errors now explain the
  operator action; unknown/private/HTML/malformed bodies remain generic.

Checks actually run and results:

- Initial pytest: **87 passed/69 skipped**, 17.78 seconds; Ruff **48 files** passed.
  Initial dedicated PostgreSQL suite: **152 passed/4 skipped**, 39.99 seconds.
  Existing web 45-unit/contract/type/lint baseline passed. Android baseline
  **98 unit tests**, no failures/skips, lint/debug build passed with all 53 tasks
  executed; evidence 03:43:30 UTC. Existing warning/notices remain visible.
- Failure tests preceded expansion: new API had three expected failures plus
  unconfigured PostgreSQL skips; storage/retrieval initially failed collection
  before models existed. Two synthetic retrieval fixtures were corrected for
  max-chunk size/date eligibility. Seven Windows-name tests and a line-end check
  failed before fixes; a temporarily mismatched evaluator line rule was corrected.
  Web had two expected readiness failures before implementation. Android journal
  initially had five expected failures/one rejection pass. Two later Android
  receipt/content-integrity regressions failed before strengthening validation.
- An early full ordinary run had **1 failed/122 passed/99 skipped** due to a stale
  admin head assertion; it was changed to the actual supported-head invariant.
  Early combined PostgreSQL run: **217 passed/5 skipped** before review additions.
  Storage focused PostgreSQL/SQLite: **71 passed/2 expected SQLite lock skips**;
  retrieval/compatibility/evaluation: **50 passed/2 expected SQLite shared-lock
  skips**. Portable corpus-provenance test: **1 passed**.
- Final ordinary `pytest -q`: **137 passed/114 skipped**, 33.96 seconds. Final
  `scripts/test-postgres.ps1`: **244 passed/7 skipped**, 69.46 seconds. Seven skips:
  five SQLite concurrency variants that require PostgreSQL row/shared locks and
  two opt-in real-provider health cases. Full PostgreSQL counterparts ran. Ruff
  lint/format: **58 files passed**. Existing Starlette/httpx warning remains.
- After the complete run, stronger response OpenAPI validation and actual HTTP
  upload→D citation→new version→old replay assertions were added; affected API
  rerun on SQLite and dedicated PostgreSQL: **6 passed**, 3.73 seconds. No backend
  runtime change followed the complete suite.
- `scripts/evaluate_documents.py`: nine versions/five positive/six negative
  queries; public repository README first paragraph at `1ca228a` copied for two
  synthetic owners plus seven synthetic inputs. SQLite and PostgreSQL recall@5,
  MRR@5/exact evidence all **1.0**; zero known-excerpt/isolation/negative failures.
  Existing PostgreSQL claim evaluator recall/MRR **0.8667**, exact **1.0**, zero
  isolation/negative failures. Small deterministic lexical measurements are not
  production latency, real inference or answer-entailment evidence.
- Web fresh `npm ci`: **270 packages**, audit **0 vulnerabilities**, existing
  whatwgencoding notice. Contract generation/freshness, typecheck/lint, **51 unit
  tests**, build passed. Dev Chromium initially **5 passed**. Added readiness test
  then final production-build Chromium **6 passed**, 18.2 seconds, 04:01:58 UTC.
  Synthetic 503 precedes real authenticated disposable-PostgreSQL sign-in; focus,
  token cleanup/cooldown/no silent retry and actual grants/revocation are checked.
  A root export command used the web cwd once and failed to locate `.venv`; the
  corrected root command exported successfully. No check was counted from that
  failed invocation. No credentialed screenshot/trace was retained.
- Final Android unit/lint/debug/unsigned release/test-APK builds: **120 unit tests**,
  zero failures/skips, lint zero errors/14 existing dependency availability notices.
  First small-layout emulator run: **21 passed/3 failed**, due to actual safe error
  code mismatch, an emulator/server clock assumption and preview text semantics.
  Second: **22 passed/2 failed**, due to a same-owner cross-scope test expecting 404
  where the declared conflict is 409, and an existing correction UI IME race.
  Corrected expectations/synchronization preserve contract/assertions. Final
  complete emulator/process-stop evidence is appended below. A transient adb
  offline install after daemon restart was retried on the explicit emulator.

Read-only final compatibility review against `1ca228a`: 27 original OpenAPI
paths/31 operations/43 schemas preserve existing parameters, fields, requirements,
enums, security and response definitions. Seven schemas add optional fields;
seven paths are new. Export matches actual routes. Released 0001–0004 have no Git
diff; retained v3 AST prompt string is byte-identical. Four legacy option/hash
cases match, including explicit `use_documents=false`. Ownership, historical
version exclusion, trust rejection, atomic publication and frozen traces were
reviewed without further runtime edits or a blocking defect.

Windows/PostgreSQL/device/model evidence: Windows host, Python 3.12, pinned JDK21/
Gradle8.13/SDK36, Node24.12/npm11.6.2. Dedicated disposable PostgreSQL schemas and
migrated SQLite were used for tests. Emulator is Android17/API37 WHPX, small
480×320 dp landscape and 1.5× text. Explicit FakeProvider HTTP is real API traffic
with synthetic owners/content, not real Ollama generation. A physical device
briefly appeared then disconnected before allowed read-only properties could
verify identity; no phone install/launch/settings/data action was performed.

Checks skipped/remaining issues: physical S24 FE/Android16 install/connect/upload/
cited-source/version/recovery/token checks, release trusted HTTPS, TalkBack/manual
visual/keyboard/IME/file-picker review, API26 behavior and real-model known-source
verification remain. Live-provider health checks were not opted in. Browser HTTPS,
manual accessibility/other browsers and operational load/backup-restore exercises
remain. Application 0005 installation is intentionally unperformed. Raw blobs,
failed receipts and snapshots are retained within quotas without an automatic
cleanup/delete service; PDF and later features are explicitly deferred.

Next eligible checkpoint: Phase 09 only if separately selected. Stop at Phase 08;
do not treat target checks or this implementation as deployment authorization.

### 2026-10-10 UTC — Phase 09 entities and aliases — 1ca228a + preserved Phase 08 tree

Scope: only the separately selected scoped identity milestone. Required planning,
root/client instructions, current source/OpenAPI/migration/test state and actual
Phase 03/current Phase 2 prerequisites inspected before implementation. Existing
uncommitted Phase 08 work was preserved. No later phase or deployment is included.

Changed behavior/files: `entity_models.py`, `entities.py`, typed entity contracts/
router, additive migration 0006, optional explicit memory reference/link history,
authorized alias retrieval/conflict grouping and frozen resolution. Existing
Android Memory hosts EntityController/EntityScreens with duplicate review, aliases,
rename, explicit self, subject link/clear, preview/confirmed merge and undo. Exact
operation/body recovery extends the existing Keystore record to v4/256 KiB and
preserves older journals. Old source cards keep original entity interpretations;
recorded retrieval shows ambiguous alternatives. OpenAPI/generated web types and
current docs/capabilities/gates updated. Dependencies/wrappers remain unchanged.

Data/API/prompt changes: no inferred backfill. Owner/scope composite constraints,
exact NFKC/case/whitespace policy, permitted collisions, explicit candidate/self
selection, retained historical intervals/lineage/receipts and scope row locks.
Every write reserves one operation UUID with frozen 200 replay/201 new receipt;
changed inputs, foreign IDs, stale previews, redirect cycles and quota failures
cannot produce a partial audit/side effect. Merge does not move original evidence.
Missing correction references remain null and preserve legacy fingerprints.
Ambiguous roots are withheld before ranking/context; truncation is conservative.
v4/current and v3 claim prompts, old traces, hashes and completed replay survive.

Checks actually run and results:

- Fresh backend baseline: ordinary **137 passed/114 skipped**, Ruff 58 files.
  Initial PostgreSQL preparation failed on refused local connectivity without
  executing tests. Started the existing compose `db` service and reran against
  the dedicated test database: **244 passed/7 skips**, 198.07 s. No application
  migration was run. Android baseline unit/lint/build succeeded; its 121-unit
  artifact was cached and is recorded as such.
- Full changed ordinary pytest **150 passed/129 skipped**, 185.74 s; full dedicated
  PostgreSQL/SQLite **271 passed/8 skips**, 304.92 s. After two new history/truncation
  tests, the final affected entity/storage/history/corpus/document-upgrade suite
  was **35 passed/1 SQLite lock skip**, 47.21 s. Actual PostgreSQL foreign-key,
  opposite-merge row-lock, populated upgrade/check/downgrade and old replay checks
  passed. Offline PostgreSQL 0005→0006 SQL compiled. Final Ruff lint/format check
  passed **112 files**. Existing Starlette/httpx deprecation warning remains.
- Explicit synthetic alias corpus **11/11 on SQLite and PostgreSQL**, zero false
  resolution, isolation and exact-evidence failures. This is deterministic policy
  verification rather than production relevance, truth or model quality.
- Android pinned JDK21/Gradle8.13/SDK36 final unit/lint/debug/unsigned-release/test-
  APK build passed: **134 unit tests**, zero skips; lint zero errors/14 existing
  dependency notices. APK metadata: `0.9.0-entities`, code 5, minimum 26/target 36.
  Actual-emulator script final **25 ordinary passes**, then **2 chat + 2 memory +
  2 document + 2 entity force-stop stages passed** and successful cold launch.
  Real HTTP and production Compose/Keystore are exercised against disposable
  SQLite with explicit synthetic evidence and FakeProvider; no Ollama call.
- Web generated contract/freshness, typecheck, lint, **51 unit cases**, production
  build and **6 production-build Chromium cases** passed. Browser integration used
  disposable PostgreSQL for current grants/denial/revocation and the existing safe
  readiness flow; synthetic provider failures/health remain clearly labeled.
  Final pinned `npm ci`: **270 packages, audit zero vulnerabilities**, with the
  existing whatwg-encoding deprecation notice; post-install contract/type/lint/
  build checks passed. No web runtime behavior changed in Phase 09 beyond types.
- Compatibility audit: **34 old paths/all operations and 48 schemas** retained;
  original fields/required lists/parameters/security/response references unchanged.
  Optional additions in six schemas and 13 new paths. **76 protected hashes**
  matched the phase-start capture, including prior 0001–0005, original fixtures,
  prompts and pinned dependencies/wrappers/later phases. Diff whitespace check
  passed with Windows autocrlf notices. No old validation evidence was rewritten.

Intermediate failures preserved: missing entity routes and alias expansion were
red before implementation. An optional-reference DB argument was fixed. Empty
0006 rollback required a document-upgrade test to restore head after 0005 correctly
refused data loss. Android journal/interface/UI syntax and test constructor
compilation errors were fixed before successful reruns. Initial emulator **23/25**
passed; lazy scrolling and partial-label assertion were corrected, then **25/25**
passed. Document force-stop resume subsequently reached an off-screen D quote and
failed (including a run compiled before the final source-scroll fix); the final
complete run passed all eight stages. Synthetic history tests corrected a route
and citation-producing provider fixture. Read-only operator-check shell quoting,
schema column and case assumptions were fixed without any database write.

Carryover evidence: preceding Phase 08's 120-unit result remains historical. Its
late 121-case artifact compiled, but its last final document resume/emulator work
was unfinished at the phase boundary. The Phase 09 regression now closes that
automated recovery check on code 5, including late SAF identity/draft fencing and
document source cards. Prior 24 ordinary and four chat/memory staged passes plus
the failed document resume remain recorded separately.

Windows/PostgreSQL/device/model evidence: Windows host/Python3.12, pinned JDK21,
Gradle8.13/SDK36, Node24.12/npm11.6.2. Task-created Android17/API37 WHPX emulator,
480×320 dp landscape and 1.5× text. No physical-phone action or actual-model run.
Final read-only application inspection found schema **0005**, one unambiguous
case-normalized selected account match and one active grant. This phase performed
no application migration or grant; current source needs **0006** separately.
Dedicated test schemas were removed (zero remaining); final cleanup below records
helper/credential/emulator/database state.

Checks skipped/remaining issues: physical S24 FE/Android16 and API26 install/
connect/entity/canonical-source/ambiguity/recovery/token/logout behavior; verified
release HTTPS, TalkBack, hardware keyboard and manual visual/IME accessibility;
actual server/network interruption and Ollama known-source checks. Opt-in provider
health cases were not enabled; SQLite cannot prove PostgreSQL scope locking.
Browser HTTPS/manual accessibility/other browsers, production load and operational
backup/restore remain unverified. Identity histories count toward retained quotas;
no automatic deletion/cleanup, inference, cross-user graph or later feature exists.

Next eligible checkpoint: Phase 10 only after a separate request. Stop at Phase 09;
remaining target verification does not authorize deployment or further milestones.

Final refinement and cleanup, **2026-10-10 10:08:59 UTC**: added a null-character
negative check before encrypted entity reservation. Final build/unit/lint checks
again passed all 134 unit cases; focused real-HTTP entity UI passed one case and
all eight chat/memory/document/entity force-stop stages passed again, with successful
cold launch. This follows the separate full 25-case emulator pass. Clean web
install was followed by successful contract/type/lint/build checks. Expanded audit
matched **85 protected hashes** and verified **57 changed UTF-8/NUL/Markdown-link
files**. A command-local autocrlf override produced CRLF-only whitespace failures;
the repository-configured diff check passed and no line-ending rewrite was made.

Final read-only state: application schema 0005 and selected active grant preserved,
zero disposable PostgreSQL schemas, no helper listener, test credential or encrypted
journal. Emulator display/font reset; task-launched emulator shut down. Existing
compose DB restored to its initially stopped state with its volume/grants retained.
No 0006 application installation or physical-phone/deployment action was performed.

### 2026-10-10 — Phase 10 checkpoints 1–4 — base 13a0cb3 + working tree

Scope: only embeddings and measured hybrid retrieval. Read required/root/plan
documents, actual source/OpenAPI/migrations and fresh baselines. Existing Phase 08
documents and Phase 09 scoped identities met the prerequisites. No new agents,
later phases, model download, application installation or deployment.

Changed behavior/files: new embeddings/provider, derived index models and semantic
service; migration 0007; bounded owned rebuild route; compatible retrieval/chat
integration and capability/trace/candidate fields; new synthetic evaluation corpus/
runner and provider/storage/failure/replay tests. Existing identity downgrade test
now restores newer disposable head before checking schema after a retained-history
refusal. Source/OpenAPI/generated web DTOs, example configuration, current policy,
architecture/plans/contracts and installation docs updated. All prompts, earlier
migrations, Android files, dependency locks/wrappers and later plans are preserved.

Data/API/prompt changes: 0007 adds discardable scope-bound JSON vectors with exact
evidence IDs/hashes and full digest/dimension/index namespace. Bounded history
snapshot/inference/recheck/atomic publication preserves sources and old traces.
`POST /v1/scopes/{scope_id}/semantic-index/rebuild` is owner-only and shares process
generation admission. Exact filtered cosine ranking merges by lexical-first RRF60;
failures use the unchanged baseline. Reserved diagnostics and evidence freeze
across retry/replay. No prompt version, input fingerprint or automatic upgrade.
Semantic is disabled by default because real-model measurements are unavailable.

Checks actually run and results:

- Ordinary baseline 152 passed/131 skipped (215.88 s); dedicated baseline 275
  passed/8 skipped (333.52 s), excluding the two initially added Phase 10 modules.
  Ruff baseline lint/format passed, 67 files. Compose DB was started from stopped.
- Expected missing-module red test; focused 21 passed/4 failed then 23 passed/2
  failed while correcting corpus default binding and entity/document fixture fields;
  all fixed. Affected 32 passed (64.22 s). Full ordinary changed run 171 passed/
  143 skipped/1 old downgrade-head failure (258.16 s), corrected by restoring head.
- Full `scripts/test-postgres.ps1`: **307 passed/8 skipped**, 411.31 s. Final
  affected provider/semantic/storage/evaluation/old-populated-upgrade rerun:
  **37 passed/0 skipped**, 71.85 s. Includes subsequently added connection-pool
  assertions (embedding outside transactions), DB guard, stable evaluation UUID
  ordering and frozen original semantic M/D citations after a new document version.
  Full runtime remains unchanged after that successful full run; final refinements
  affect tests/evaluation. Eight full skips are six SQLite concurrency/lock cases
  and two opt-in health tests, not failures suppressed from the suite.
- Native composite FK rejection, populated 0006→0007/downgrade/re-upgrade/Alembic
  check, historical hashes and completed/failed replay passed. Offline PostgreSQL
  0006→0007 SQL compiled separately. Ruff lint/format passed for 76 files; Python
  compileall and normal repository whitespace check passed.
- Final 13-question fully synthetic comparison on SQLite/PostgreSQL: lexical
  recall@5/MRR@5 0.4286/0.4286; explicit five-component fixture vectors hybrid
  1.0/0.7857; 18/18 exact evidence, zero isolation/negative failures, degraded
  fallback rate 0. Hybrid traced median/max HTTP ms: SQLite 132.229/286.993,
  PostgreSQL 159.884/290.051. Corpus covers historical changes, conflicts,
  ambiguity, imported evidence, foreign owners/scopes and unknown/time negatives.
  No real embedding model, private ADA content or answer entailment was measured.
- Capacity at 256×768: 32 batches, SQLite build/query 2374.736/2493.530 ms and
  10,096,858 peak traced Python bytes; PostgreSQL 2498.062/2366.315 ms and 9,206,837
  bytes. Item 257 falls back/rejects; model vectors are synthetic constants and
  tracing excludes DB/GPU. No production throughput/resource claim.
- `evaluate_hybrid.py` fixture and disabled CLI modes ran on disposable SQLite;
  disabled kept the baseline. Unchanged `evaluate_retrieval.py` CLI retained
  recall/MRR 0.8667, exact evidence 1.0, zero isolation/negative failures. Generated
  output was moved into ignored task artifacts. PostgreSQL comparison ran through
  the reproducible benchmark test, not a separate `--postgres` CLI invocation.
- Web pinned clean install 270 packages/audit zero vulnerabilities; contracts
  generation/check/typecheck/lint, 51 unit cases, build and six real disposable
  PostgreSQL/HTTP Chromium cases passed (21.9 s). Final int64 metadata regeneration/
  typecheck passed. No UI/lock changes beyond generated contract DTOs.
- Compatibility audit: 47 prior paths/all operations and 63 schemas preserve old
  shapes/security/required fields; optional additions in four schemas and one new
  path. 276 protected file hashes match. UTF-8/NUL/Markdown links and whitespace
  checks passed; final complete record/cleanup review is appended below.

Windows/PostgreSQL/model evidence: real PostgreSQL 17 fixtures/disposable schemas
on this host; SQLite supplements them. Local runtime 0.40.1, i9-14900HX/31.62 GiB
RAM/RTX 4090 Laptop 16,376 MiB, observed GPU use 552 MiB. Official docs and registry
manifest checked; selected 300M/768 digest fixed to
85462619ee721b466c5927d109d4cb765861907d5417b9109caebc4e614679f1; layer bytes
621,875,501 are download metadata. Selected model is absent; actual adapter probe
failed safely before inference with embedding_model_changed. No dependency added.
Initial inline shell probe quoting, fixture assumptions, formatting and patch
context errors were corrected; no private data was printed or test disabled.
Existing Starlette/httpx/npm encoding/terminal color warnings remain separate.

Checks skipped and reason: real embedding load/quality/GPU/CPU measurements (model
not installed), ANN/pgvector (bounded exact design selected), standalone legacy
checkout smoke (populated migration/replay tests instead), Android/emulator/phone
(all Android source unchanged). Prior phone/HTTPS/manual accessibility remains
target evidence, not a fresh result. PostgreSQL CLI mode was not separately rerun;
the benchmark function executed on both actual database fixtures.

Remaining issues: intended application stays at observed 0005 with its selected
grant active; installation needs head 0007. Keep semantic disabled until real-model
quality/threshold/resource measurements support activation. Representative
authorized ADA corpus, sustained load and operational install/backup checks remain.
No application migration, grant/token change, phone action or deployment.

Next eligible checkpoint: target verification/installation is separate; Phase 10
stops with its documented disabled exit. Any later implementation needs explicit
selection. Final cleanup follows below; historical logs are retained.

Final review/cleanup — **2026-10-10 18:59:16 UTC**: compatibility still matches
47 paths/63 schemas and 276 protected hashes. Completed records included in
35 UTF-8/NUL file checks and 14 Markdown documents/68 local-link checks; normal
whitespace and Ruff lint/format (76 files) passed. Application head 0005/selected
active grant unchanged, zero disposable schemas, inspected fixture/API/preview
ports stopped. Existing compose DB restored to its original stopped state without
removing volumes or data. Semantic remains off, model absent, no application
migration, later phase, phone action, external message or deployment.

### 2026-10-10 — Phase 11 checkpoints — 13a0cb3 plus preserved Phase 10 working tree

Scope: only selected-source memory proposals and explicit user review; read all
required/current/scoped instructions, source/OpenAPI/test/migration baselines.
Phases 07/08/09 prerequisites exist. Application head 0005 was inspected, not
upgraded. Prior uncommitted Phase 10 source and validation records are preserved.

Changed behavior/files: proposal/extraction/review contracts/service/API/models,
additive migration 0008, support integrity in fresh retrieval, optional reviewed
provenance, Android inbox/edit/confirm/recovery v5 and admin counts only. New
endorsement evidence preserves original generated/imported trust; exact scoped
review receipts and specific corrections commit atomically. No unreviewed factual
retrieval, automatic extraction/approval, dependency or prompt upgrade.

Data/API/prompt changes: seven owned paths; optional proposal/review/review-v1
capabilities, claim/card provenance and closed admin state counts. Old operations,
origin enums, required fields, write/request hashes and frozen request replay
remain intact. Detailed bounds/compatibility in
[MEMORY-PROPOSALS-AND-REVIEW](../docs/MEMORY-PROPOSALS-AND-REVIEW.md).

Checks actually run: unchanged ordinary 174 passed/144 skipped (268.39 s), real
PostgreSQL/SQLite baseline 310 passed/8 skipped (432.35 s), baseline Ruff 76 files,
cached Android baseline build. Test-first missing service/storage red checks.
Canonical date failures fixed; affected progression 21/1 (24.41 s), 29/1 (39.43 s),
59/1 (72.21 s). Full changed PostgreSQL suite **349 passed/9 skipped** (559.23 s),
then late publication/admin/FK/rollback checks **45 passed/1 skip** (57.96 s).
Populated upgrade/downgrade refusal, Alembic check, owner FK and concurrent
approval passed. Offline 0007→0008 PostgreSQL SQL and compileall passed; Ruff
lint/format 87 files and normal whitespace passed. Web clean locked install
270/audit zero vulnerabilities, contracts/typecheck/lint, **52 unit cases**, build
and **6 real PostgreSQL-backed built Chromium cases** passed (23.7 s).

Android: initial compile and two v5 expectation failures fixed, then **143 unit
cases**, lint 0 errors/14 warnings, debug/test APK build passed (2 m 3 s). Two
further partial-draft/date recovery cases and final gate are pending. Emulator
runs each had **20 passed/6 failed** (5 m 16 s; 5 m 8 s); old chat/document/entity
flows failed, and the new flow first had an incorrect container assertion, fixed,
then failed at empty-claims HTTP check. Diagnostic verification continues; no
recovery-stage pass is inferred after suite failure. Intermediate helper-not-yet-
defined compilation and a Windows-default text-decoding error were corrected;
UTF-8 history was restored, not discarded. Existing runtime/tool warnings remain.

Windows/PostgreSQL/device/model evidence: PostgreSQL 17 dedicated disposable
schemas, SQLite supplement, task-launched headless Android 17/API 37 emulator at
480×320dp landscape/1.5× text. Physical Samsung S24 FE/Android 16 is untouched.
Eight synthetic corpus cases: fixture **5 exact supported proposals/5 explicit
endorsements**, strict-string precision/recall 1 by construction on both DBs.
Real qwen3.8:27b: **4 proposals/4 exact supports/0 failures**, four independent
explicit annotation edits and four endorsements. Strict gold-string precision/
recall 0 because the output field wording differs. It abstained on the tentative
model-output case and the three negatives. First two-case real probe had two
exact proposals/zero endorsements before explicit review edits were implemented.
No representative/private evidence quality or entailment claim.

Checks skipped and reason: standalone older-checkout smoke (populated migration/
replay tests instead), physical phone/HTTPS/manual accessibility and operational
load (separate target environments), deployment/signing/install (unauthorized),
semantic activation/ANN (preserved Phase 10 disabled exact design). Full pytest
skips are seven SQLite locking exclusions and two opt-in provider health probes;
new affected skip is SQLite concurrent review, executed on real PostgreSQL.

Remaining issues: final Android gate, record/compatibility/cleanup review;
application head 0008 installation (observed 0005/grant unchanged), independent
representative model annotation, target phone/HTTPS/TalkBack and sustained load.
Next eligible checkpoint: finish these Phase 11 checks and stop. Later phase,
external messages and deployment require separate explicit selection.

Phase 11 final refinements: strict extraction type tests red (2 failures) before
rejecting boolean confidence/numeric dates; affected 55 passed/1 skip (74.32 s).
PostgreSQL edit-versus-review race passed (1 passed/1 SQLite skip, 0.87 s).
Owner nonce-reuse regression red (1 failure/1 unavailable-PG skip) exposed derived
ID collision; owner namespace was added to proposal/endorsement/claim/link IDs.
Final affected suite **58 passed/2 SQLite race skips**, 74.35 s, includes actual
PostgreSQL and all proposal/extraction/corpus/schema/client contracts. Real-model
corpus run predates these type/namespace refinements; final fixture/DB checks
cover them, and the extraction prompt/transport is unchanged.

Emulator: focused proposal run failed Unreachable (1 failure, 1 m 12 s); the same
synthetic empty list returned loopback 200 in 15 ms. Test helper idle keep-alive
increased from 5 to 90 s; production adapter retry/redirect policy unchanged.
Focused UI flow then **1 passed**, 4 m 17 s, and **ten actual force-stop stages
passed**, zero skips, including lost approval delivery with one claim/endorsement
and original receipt. Temporary safe diagnostics removed; older test files
restored exactly. A separate launch reported timeout despite exit zero, recorded
as a failure; script now requires Status ok after an actual cold launch.
Final Android **145 unit tests**, lint 0 errors/14 old warnings and debug/test APK
build passed (1 m 29 s). Full ordinary emulator/final strict launch still running.

Final contract regeneration/freshness/typecheck passed after schema refinements.
Ruff lint/format 87 files, compileall, 48 old paths/65 schemas and **271 protected
baseline hashes** passed. 62 UTF-8/NUL files, 13 Markdown documents/78 local links
passed. Read-only application 0005/selected active grant unchanged, zero fixture
schemas. Short-idle real-phone/HTTPS reliability joins existing device/manual
quality targets. Final complete record/cleanup remains; no later phase/deployment.

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

Final finished-source ordinary emulator suite: **26 passed, zero failures/skips**,
command duration **21 m 46 s**. Actual HTTP proposal editing, explicit accept/reject
and older chat/memory/document/entity flows passed. The ten separate force-stop
stages and strict cold launch are still running. Android 17 emulator evidence is
separate from the pending S24 FE/Android 16, release HTTPS and real-model targets;
the disposable helper supplies synthetic extraction and 90-second keep-alive.

Phase 11 final result: **ten actual force-stop stages passed**, including the
lost-review-delivery recovery with the original key/receipt and one claim. The
strict cold-launch gate then **failed**; complete emulator script exit **1** is
retained as a failure. The emulator was absent on follow-up, so cold launch has
no successful retry. Final lint/format/compileall/whitespace and old-contract/
baseline-hash/UTF-8/link checks passed. Last read-only application check showed
0005/unchanged selected grant/zero disposable schemas. Application 0008,
S24 FE/Android 16, cold launch, short-idle HTTPS, manual accessibility and
representative model quality remain. The user subsequently selected Phase 12;
this closes Phase 11 implementation without claiming all device gates passed.

Resource follow-up: task emulator/helper ports absent, physical phone left alone,
externally restarted PostgreSQL kept running and application head/grant unchanged.
Automatic approval review blocked removal of five synthetic helper Temp
directories; that cleanup is skipped. Emulator display reset was unavailable.

### 2026-10-11 UTC — Phase 12 baseline/read-only server checkpoint — 13a0cb3 plus preserved Phase 10/11

Scope: selected calculator and owned memory/source tools, separate opted-in
bounded agent mode; no external write integration or later phase. Required
instructions/current source/OpenAPI/prerequisites inspected first. 333 baseline
file hashes and exact actual/exported **55 paths/76 schemas** recorded privately.

Baseline checks: dedicated SQLite/PostgreSQL **361 passed/11 skipped**, 179.90 s;
Ruff lint/format **87 files**; Android unit/lint/build **18 s**, 9/53 tasks
executed, unit/lint cached; web contract freshness/typecheck/**52 unit tests**,
7.56 s. Existing Starlette/httpx warning remains. App read-only head 0005,
selected grant unchanged, zero disposable schemas. PostgreSQL was restarted
externally and remains running; detected physical phone was not operated.

Implementation/tests: constrained exact calculator and native tool adapter,
typed registry/agent inputs, additive migration 0009 and scoped fenced
run/step/approval/receipt service/router. Missing module/service red checks
**1 failed** each (0.13/0.52 s); first SQLite flow plus provider/calculator checks
**3 passed/1 unconfigured-PG skip**, 0.56 s. Expired model lease test red
**1 failed**, 0.65 s; late publication is now fenced. Affected SQLite/real-PG
agent/tool/provider/schema suite: **17 passed**, 5.57 s. Client/monitoring,
broader failure/concurrency/populated migration, real-model read-only flow and
target checks remain. No new full-suite pass, application migration, phone
installation, deployment or external effect claimed.


### 2026-10-11 — Phase 12 expanded verification — 13a0cb3 + working tree

Scope: only selected read-only tools, bounded separate agent runs and relevant
Android/admin controls. No later phase, external write/integration or deployment.
Implemented migration 0009, fixed registry/limits/native protocol, scoped exact
approvals, durable outcome receipts, shared admission and lease/generation fences.
Inference occurs outside transactions. Tool evidence is untrusted and does not
promote claims. Plain chat/v3/v4/replay and all released migrations remain intact.
Android adds capability-gated intent/approval/denial/receipt state and encrypted
journal v6, backward-readable and GET-only restore. Admin adds only closed state
counts. API changes are additive; source needs head 0009, not installed here.

Checks actually run: affected PostgreSQL/SQLite suites expanded to 71 passed/7
documented skips (35.21 s); native privacy/protocol 8 passed; full suite first
423 passed/12 skips/1 SQLite deeper-downgrade failure, then 430 passed/18 skips
(267.11 s) after new-migration preflight. Two additional actual HTTP/OpenAPI checks
passed. Real qwen3.8:27b calculator/memory/source functional probes: 3 passed,
3 deliberate SQLite skips, completed receipts and answers, 38.91/53.28/53.17 s;
updated memory-result probe passed, 54.95 s. No real-model result is inferred from
fixtures. Migration red/green and fixture corrections are detailed in STATUS.

Android build/unit/lint/test APK gate passed (23 s then 35 s); actual disposable
HTTP tool approval/denial, two real force-stop stages and Status:ok cold launch
passed both normal portrait and compact 900×500/240dpi/1.5×text on task-owned
Android 17 emulator-5556. Initial two script staging failures exposed Gradle APK
cleanup; explicit reinstall/private test provisioning fixed the runner lifecycle.
Web clean npm ci, contract/typecheck/lint, 53 units/build and six actual PostgreSQL
Chromium scenarios passed. Known warnings remain; no pinned dependency changes.

Final source availability/tampering review added red invariants and explicit
terminal rejection: future/expired imports cannot enter a preview/context; a
changed immutable pin cannot authorize execution. Actual source suite passed
18 tests; full final regression is in progress. Fresh OpenAPI preserves 55 old
paths/76 old schemas, now 63/85. Ruff/compileall and the 333-file scope/hash audit
passed. Prior validation is preserved rather than relabeled as these runs.

Skipped/remaining: configured application installation (observed 0005), physical
S24 FE/Android 16, release HTTPS, manual TalkBack/screen reader and sustained
target model/resource/network checks. Physical phone untouched; externally
running PostgreSQL remains running. Prior automatic approval review rejected
cleanup of five synthetic helper directories (blocked by policy); that cleanup
remains unperformed, not a phase success. Final regression/resource/doc results
will be appended. Next eligible work requires the user's selection; stop at 12.

### 2026-10-11 — Phase 12 final close-out — 13a0cb3 + working tree

Scope: requested tools/agent phase only; prerequisite 03/04/06 verified from
actual source/contracts/tests. Preserve all pre-existing Phase 10/11 changes and
all later plans. No external write/integration, deployment or application upgrade.

Changed behavior/files: versioned calculator/memory/source registry, constrained
arithmetic parser, separate native ada-agent-v1 adapter/contracts/API/service,
additive scoped run/step/approval/receipt migration 0009, capacity and deterministic
limits, immutable intent/receipt replay, expired lease and late-worker fencing.
Every proposed read-only command requires exact principal/version/hash approval;
denial is durable, recovery never reexecutes. Imported half-open availability and
immutable source integrity are checked before preview/context and approval.
Tool results remain untrusted evidence, not claims. Android adds exact scoped
intent/approval/state/receipt views and backward-readable encrypted v6 journal;
restoration GETs only. Admin only gains closed creation-window state counts.
Policy/docs/OpenAPI updated; existing chat prompts and contract fields unchanged.

Checks actually run: final full dedicated PostgreSQL/SQLite **440 passed/18
documented skips**, **223.69 s**, including new source guards and historical
chat/CLI/migration/schema/permission/concurrency/failure invariants. Ruff lint and
format **103 files** clean; compileall clean. Final Android unit/lint/debug/test
APK build **47 s**; XML **155 passed/zero failures/errors/skips**, 20 suites;
lint zero errors/fatal and 14 existing warnings. Actual focused emulator HTTP
approval/denial, two separate force-stop stages and Status:ok launch passed in
portrait and 900×500/240dpi/1.5×text. The final as-of preview refinement reran the
compact flow (23 s Gradle gate), both stages and cold launch successfully. Earlier
full instrumentation was not relabeled as a new Phase 12 suite.

Web clean npm ci, current generation/freshness/typecheck/lint, **53 units/build**
and **six actual PostgreSQL Chromium scenarios** passed. Real local installed
qwen3.8:27b used only synthetic disposable PostgreSQL: calculator/memory/source
each returned an owned completed receipt and final answer; 38.91/53.28/53.17 s,
with updated memory metadata probe 54.95 s. Functional evidence is distinct from
quality/throughput/GPU placement. Red checks, corrected fixtures, initial deeper
downgrade failure and failed runner setup attempts are preserved in STATUS.

Contract/scope review: source/export **63 paths/85 schemas**, preserving **55
old paths/76 old schemas**, exact required fields and old properties. All 333
baseline files retained; released migrations, old chat/model/prompt/provider,
lockfiles/wrappers and later phase plans unchanged. UTF-8/doc review **12 files/81
local links**, whitespace clean. Android version **0.12.0-tools** / code **7**.

Skips/remaining: SQLite concurrency copies and opt-in provider tests are explicit;
real agent probes were run separately. Intended application migration to 0009
not performed (observed 0005); S24 FE/Android 16, release HTTPS/network/TalkBack,
screen reader/signing and sustained model/resource/concurrent quality checks
remain. Semantic embedding activation is still disabled pending its earlier
target gate. External writes are unselected, so external-effect tests are not an
exit gate. No private transcripts, source quotes or credentials are recorded.

Resource evidence: unchanged selected grant, zero disposable PostgreSQL schemas
and HTTP listeners; owned emulator display settings reset, emulator-5556 stopped.
Physical phone untouched; externally running PostgreSQL left running. Automatic
approval review previously rejected removal of five synthetic helper directories
as blocked by policy; these and five additional stopped Phase 12 helper directories
remain in Windows Temp. No deletion retry or cleanup success is claimed.

Next eligible checkpoint: only a separately requested later phase or target
installation/verification task. Stop at Phase 12.


### 2026-10-11 — Phase 13 baseline — 13a0cb3 + preserved working tree
Scope: only episodes and bounded explicit consolidation, no later phase/deployment.
Changed behavior/files: implementation in progress; source/version, job lease,
generated-map, owner/scope and failure invariants precede new writes.
Data/API/prompt changes: additive 0010; original chat/prompt contracts preserved.
Checks actually run and results: unchanged PG/SQLite 440 passed/18 skipped,
219.11 s; Ruff 103 files clean; Android cached baseline 11 s; web typecheck/53
units 7.37 s. Initial red and corrected fixture/constraint results are in STATUS.
Checks skipped/blocked and reason: target phone, release network/accessibility/
load pending; live summary corpus/client integration and final regression pending.
Windows/PostgreSQL/device/model evidence: Windows actual PostgreSQL baseline;
no application migration or physical device interaction.
Remaining issues: final Phase 13 gates and installation distinction.
Next eligible checkpoint: finish only the selected phase's verification.

### 2026-10-11 — Phase 13 local exit — 13a0cb3 + preserved working tree

Scope: only source-linked generated episodes and bounded durable consolidation;
prerequisite source/contracts/tests inspected first; no later phase or deployment.

Changed behavior/files: new consolidation service/contracts/provider/routes and
four-table static migration 0010; explicit episode/pending-proposal/lexical jobs,
lease/attempt/checkpoint/fenced receipts and one shared-admission lifespan worker.
Exact original source maps, time/trust/policy checks and immutable navigation
snapshots keep generated summaries separate from factual retrieval. Full proposal
batches validate before publication; only Phase 11 explicit review endorses claims.
Android history/source previews and encrypted v7 recovery retain v1–v6 records;
startup navigation and local discard do not lose the reservation or create server
writes. Admin shows bounded counts/job metadata without private inputs/outputs.
Policy, architecture, client contracts, CURRENT-STATE, DECISIONS and phase
checkpoint evidence updated; palettes/ordinary chat remain unchanged.

Data/API/prompt changes: head **0010** only on disposable fixtures, **69 paths/94
schemas**; saved baseline comparison preserves all **63 old paths/85 old schema
shapes**, released/prior migration files, lockfiles/wrappers and normal chat
source/prompts/replay. Additive optional capabilities/metadata only. Navigation
contexts have their own protocol; no implicit prompt upgrade or factual promotion.

Checks actually run and results: full actual PostgreSQL 17/SQLite **516 passed/19
expected skips**, **291.26 s**; Ruff **115 files** lint/format clean; compileall,
OpenAPI export/web generation and compatibility/whitespace checks passed. Android
**164 unit tests, zero failures/skips**, lint **0 errors/14 old dependency
advisories**, debug/test build **13 s**. Current task-owned emulator API37/Android17
runs passed **two actual HTTP UI cases plus two staged lost-response/force-stop
recovery checks** in both standard portrait (**20 s** connected) and compact
900×500/240dpi/font1.5 (**21 s** connected), plus strict cold-launch Status ok.
Focused prior tool approval/denial verifies changed navigation. Web clean install,
contracts/typecheck/lint/**54 units** (27.56 s)/production build passed; actual
PostgreSQL production-preview Chromium **six cases** passed, final **20.1 s**,
including private-input exclusion, grant revocation, table focus/narrow/200% zoom.
Native qwen3.8:27b evaluation: **4/4 synthetic cases completed at attempt 1**,
**5 exact support checks**, **13/13 lexical markers**, **0 endorsed claims**.
Manual synthetic review preserved uncertainty and disagreement attribution;
small-corpus mapping/marker coverage does not establish broad semantic quality.

Corrected failures remain recorded in STATUS: initial missing implementations,
JSON-null constraint, fixture import/source-route/downgrade-message issues, old
hardcoded head, invalid inferred interval with a partial batch, Unicode tags,
thread-insensitive connection observer, stale export (506 pass/19 skip/2 fail),
lower imported-source downgrade preflight red, size fixture mistakes (47 pass/
1 skip/4 fail), wrong Android trust-label assertion, offscreen lazy test target,
startup journal-navigation and post-discard selection reds. No failing test was
disabled. Final full/client checks supersede those intermediate failures.

Checks skipped/blocked and reason: **11 SQLite row-lock variants** are checked by
actual PostgreSQL counterparts; **6 opt-in prior native tool probes** and **2
opt-in generation-free health cases** not repeated for this phase. Entire old
Android instrumented suite/release variant not freshly run; changed HTTP/recovery
and navigation flows selected. Physical Samsung S24 FE/Android16, minimum API26,
release HTTPS/short-idle and real-provider Android UI, manual TalkBack/accessibility,
sustained concurrent worker/model resource/load and representative summary quality
remain target checks. Application head-0010 installation was not performed.

Windows/PostgreSQL/device/model evidence: read-only configured application remains
**0005**, exact selected admin grant active; dedicated disposable PG schemas **0**.
Fixture HTTP listeners are stopped; task-owned emulator settings restored/emulator
stopped. External PG/Ollama left available, no physical device interaction.
Automatic approval review rejected deletion of six new ignored workspace fixture
directories under `.pytest_cache/client-fixtures` as **blocked by policy**; retained
without retry. Prior blocked Windows Temp directories remain untouched.

Remaining issues: explicit installation and target checks above; retained synthetic
fixture storage. No automatic approval/deletion, external effect, semantic
activation, prompt upgrade, later phase, publication or deployment.

Next eligible checkpoint: only a separately requested target verification,
installation or later phase. Stop at Phase 13.

Final audit 09:17 UTC: 14 changed/new Markdown files have valid UTF-8/local links; repository-configured whitespace check and web contract/type/lint checks passed. An extra autocrlf-disabled check flagged existing CRLF as whitespace; no mass newline rewrite. Owned emulator stopped, no attached devices or fixture HTTP listeners; six blocked synthetic workspace directories retained.


### 2026-10-11 20:38 UTC (13:38 Phoenix) — Phase 14 — base 4df9a72 + working tree

Scope: only explicit interaction preferences and bounded session expression.
Phase 07 prerequisite verified from current source/contracts/tests; its physical
phone checks remain target work. Initial working tree clean.

Changed behavior/files: owner-target typed settings, frozen precedence/source
receipts, audited future-reply conversation updates, opt-in native-bounded sessions,
reviewed signal clamps/decay/expiry/reset and exact request expression snapshots.
Android Settings, encrypted journal v8/v1–v7 recovery, HTTP/force-stop tests,
OpenAPI/56 synthetic fixtures and policy/current-state/architecture documentation.
Admin remains metadata-only; dependencies/locks/wrappers unchanged.

Data/API/prompt changes: additive 0011; six new private paths and three optional
capabilities; 75 paths/105 schemas preserve 69 old paths/94 old shapes. Independent
ada-expression-v1 overlay uses fixed 800 bytes; saved v3/v4 personality/system
prompts and chat fingerprints unchanged. Model signals are proposals until explicit
review; normal model text never updates state. No classifier or learning pipeline.

Checks actually run: SQLite baseline 290/245 skips, isolated native PostgreSQL 18.6
baseline 516/19 skips; baseline Ruff and fresh Android units/web 54 units. New
invariant failed before wiring. Full changed PostgreSQL/SQLite 562 passed/21 skips
(508.94 s), followed by final affected 74/3 (76.71 s) for late clock/provenance/HTTP
fixture refinements. Ruff lint/format 121 files, compileall, populated upgrades,
Alembic check/native constraints/concurrency/rollback and old replay; contract/hash/
whitespace audit. Android final XML 174/0/0, lint zero errors/14 old advisories,
debug/test builds; emulator five HTTP UI cases, two force-stop stages and strict
cold launch in portrait and compact 1.5x text. Web clean install (zero reported
vulnerabilities), generated contracts/type/lint/54 units/build and six actual PG
Chromium cases. All exact durations and intermediate failures are retained in the
Phase 14 STATUS section. Obsolete v7 assertions, wrong test adapter/import and
pre-export/old-head test expectations were corrected; no unresolved local failure.

Checks skipped/blocked: configured application PostgreSQL port5433 and Ollama
metadata unavailable, no target DB migration or native inference. Full backend
skips: 13 SQLite locking variants with PG counterparts, six native-tool opt-ins,
two Ollama-health opt-ins. Final affected skips are three SQLite locking variants.
No release build/signing/distribution, whole old instrumented-suite rerun, physical
S24 FE/Android16/minimumAPI26/HTTPS/TalkBack/manual model or sustained load run.

Windows/PostgreSQL/device/model evidence: task-owned PostgreSQL18.6 on loopback
55414/dedicated test DB, separate from application and existing port5432 server.
API37 Android17 emulator; actual fake-provider HTTP is explicitly distinct from
native-model wording evidence. Earlier observed application0005 is historical;
current source needs0011. No real account/role changes or deployment.

Remaining issues: backed-up intended installation and target checks above. Prior
blocked fixture cleanup is untouched; new synthetic test artifacts remain ignored.

Next eligible checkpoint: separately requested target verification, installation
or Phase15. No later phase implemented. Stop at Phase14.


Final audit — 2026-10-11 20:43 UTC (13:43 Phoenix): 12 changed/new Markdown files
passed UTF-8/local-link checks; Ruff/format 121 files, normal whitespace, web
contract freshness/typecheck and protected history hashes passed. Restored legacy
fixture bytes were rechecked by the final Android unit/lint/debug gate (3 s;
53 tasks, 3 executed/50 up-to-date), XML still 174/0/0. Disposable schemas count
was zero. Task-owned PostgreSQL stopped successfully; emulator stopped and no
fixture HTTP/web/test-PostgreSQL listeners remained. The pre-existing PostgreSQL
service was untouched. New ignored synthetic validation artifacts remain retained;
no prior blocked cleanup was attempted. No local check failure remains. Stop at14.

### 2026-10-11 21:56 UTC (14:56 Phoenix) — Phase 15 — base 4df9a72 + working tree

Scope: only opt-in interaction learning and source-linked continuity. Required
instructions/source/OpenAPI/migration/test baseline inspected first. Prerequisites
11/13/14 present in code; their target gates remain visible. Existing uncommitted
Phase 14 work and earlier evidence were preserved.

Changed behavior/files: owned selected-user-event observations with confidence/
time/version/purpose/provenance, independent-interaction deduplication, weak expiry,
CAS enrollment/pause/off/reset and exact review/edit/reject/account reuse. Reviewed
lineage freezes revision/observation IDs; pending/unreviewed values never affect
chat. Reset deletes live derived learning and disables reuse, retaining minimal
ID audit and historical request/source records for existing replay contracts.
Android Settings and v9 encrypted exact recovery (v1–v8 reads), C source cards,
aggregate-only admin counts and policy/source/contract documentation added.

Data/API/prompt changes: additive **0012**, seven authenticated learning paths,
nullable frozen request selection and optional capabilities/C citations/counts.
OpenAPI 82 paths/118 schemas preserves all 75 prior operations/105 schema shapes;
23 protected migrations/prompt/locks/wrappers/later plans and 53 old fixture bytes
unchanged. There are 68 synthetic fixtures, 12 new learning cases. Fixed 1,024-byte
learning policy fits the whole budget and preserves v3/v4 baselines. Continuity
uses bounded exact authorized original episode sources with uncertainty/trust/
omissions; generated summary text is not recollection context. Explicit settings
and current instructions take precedence; replay freezes selected messages/cards.

Checks actually run/results: baseline PostgreSQL/SQLite **563 passed/1 failed/
21 skips** (428.09 s); pre-existing hybrid recall fluctuation passed unchanged
focused rerun (3/0, 4.23 s). New consent invariant failed before wiring. Initial
nullable JSON/old-head expectations and PostgreSQL JSON GROUP BY binding failure
were corrected; intermediate outcomes retained in STATUS. Full changed suite
**587 passed/22 skips** (500.62 s), followed by final affected **172 passed/6 skips**
(164.77 s) for later lineage/time/C-card refinements. Synthetic threshold comparison
**27 passed/1 skip**, 20 measured eligibility decisions across two thresholds/two
backends, zero automatic promotions; no preference-accuracy/optimal-threshold claim.
Final Ruff lint/format **180 files**, compileall, whitespace and compatibility
audit passed. Actual SQLite HTTP fixture export **1 passed/1 unavailable-PG skip**.

Android **186 units/0 failures/0 skips**, lint zero errors/14 existing advisories,
debug/test APK builds. Actual portrait and compact **900x500/240 dpi/1.5x text**:
**seven focused HTTP UI cases**, **two force-stop receipt-recovery stages**, cold
launch **Status ok**; reviewed instrumentation gates 53 s/51 s. Compact initially
failed because the test asserted an offscreen LazyColumn quote before scrolling;
its first child-scroll attempt could not find an uncomposed item. Scrolling the
Sources list to the quote then the child passed; no product layout workaround.
Geometry/font settings restored. Web clean install reported zero vulnerabilities,
contracts/type/lint/**54 units** (23.92 s)/build and **six PostgreSQL HTTP Chromium
cases** (22.2 s) passed; final schema freshness/type/lint passed again.

Checks skipped/blocked: full backend 14 SQLite locking variants with executed
PostgreSQL counterparts, six prior opt-in native agent probes, two Ollama-health
opt-ins. Final affected four SQLite locking variants/two health opt-ins. Configured
application database and Ollama metadata unavailable; no application migration or
Phase 15 native inference. Whole old instrumentation suite, release signing/build/
distribution, standalone old-checkout smoke, physical S24 FE/Android16/HTTPS/network/
manual TalkBack/model resource-load/representative consented accuracy not run.

Windows/PostgreSQL/device/model evidence: migrated disposable native PostgreSQL
18.6 on task-owned loopback 55414, plus SQLite; actual Android API37/Android17
emulator and deterministic HTTP provider, production-build Chromium with isolated
PG/HTTP. Existing port5432 PostgreSQL untouched. Application0005 is only earlier
historical evidence; source now requires0012. No credentials/private transcripts
were recorded; validation inputs are synthetic.

Remaining issues: intended backed-up installation; physical/HTTPS/accessibility/
native-model quality/resource and representative learning/continuity evaluation;
explicit final account/backup/historical-snapshot retention policy. Reset is not
complete account erasure and the UI discloses that. Prior blocked synthetic
Phase11–13 cleanup untouched; new ignored artifacts retained.

Next eligible checkpoint: separately requested target verification/installation or
Phase16. No automatic extraction/factual promotion, diagnosis, semantic activation,
real account/role change, external message, later phase or deployment. Stop at15.

Final audit — 2026-10-11 21:57 UTC (14:57 Phoenix): 14 changed/new Markdown files
passed UTF-8/local-link checks; final API/protected-history/53-old-fixture-byte and
normal whitespace checks passed. Compact seven HTTP UI cases/two force-stop stages/
cold launch passed and geometry/font settings restored. Disposable PG schemas
count zero; task-owned PG and emulator stopped, no fixture HTTP/web/test-PG
listeners remained. Existing user PG and prior blocked storage untouched. No
unresolved local failure; intended installation and target/retention gates remain.


### 2026-10-12 — Phase 16 durable streaming and Stop — base 4df9a72 + working tree

Evidence at 04:17 UTC (2026-10-11 21:17 Phoenix). Scope: only Phase16, preserving
prior Phase14/15 local work, API/CLI contracts and released migration history.
Required documents, scoped client instructions, source/OpenAPI/migrations/test
baseline inspected first; Phase04/06 source prerequisites present. No deployment,
intended application migration or later phase.

Changed behavior/files: stream_models/contracts/provider/service/API, migration
0013 and existing reservation/API/provider/admin wiring; Android incremental
reply/Stop/checkpoint/reconnect/observer lifecycle plus real HTTP/unit/force-stop
fixtures; closed admin metadata decoding/view; exported OpenAPI/fixtures/generated
DTOs and policy/current-state/phase docs. Android 0.16.0-streaming/code11, encrypted
journal remains v9. Dependency locks/wrappers and migrations0001–0012 untouched.

Data/API/prompt changes: four additive authenticated submit/status/SSE/cancel
operations over exact old ChatInput/RequestOutput. Owned sequenced checkpoints,
immutable same-attempt Stop receipt, defined completion/intent winner and instance/
attempt/revision/deadline fencing. Frozen prompt/retrieval/expression/continuity and
source snapshots retained; final response/source event/revision/event atomic.
Cancelled -> failed/request_cancelled, explicit original-payload retry only.
Provider inference/observer connection outside DB transactions; delayed shutdown
keeps admission until iterator closes. Partial text is provisional, never factual
memory or a completed assistant event. Admin projects five metadata fields only.

Checks actually run/results: baseline **601 passed/2 failures/22 skips** (535.78s);
pre-existing admin503/hybrid recall fluctuation focused **5 passed** (10.70s), no
unrelated fix claim. Ruff129, Android186 baseline, web54 baseline passed. Full
changed PostgreSQL/SQLite **631 passed/23 skips** (539.09s), before final defenses.
Red/green checkpoint, operator-recovery/quota and final-only deadline invariants
caught and fixed defects; one quota assertion used the wrong legacy error shape.
Final affected **92 passed/2 skips** (88.03s), later real TCP unread-observer/final
commit replay **2 passed** (10.08s). Old-file command collected no tests; stale
OpenAPI expectations failed before regeneration. Export **1 passed/1 unavailable-PG
skip**; final PG contract checks passed. OpenAPI86paths/122schemas; old82operations/
118schemas unchanged except three optional fields; eight additional fixture
payloads, 66 old JSON files unchanged except capabilities/readiness/manifest.
Ruff138, compileall, whitespace,22protected hashes and16UTF-8/local-link docs passed.

Android reviewed **194 units/0 failures/0 skips**, lint0errors/14existingadvisories,
debug/test APKs. A conversation-detach invariant failed before transition fixes.
Portrait and compact900x500/240dpi/1.5x actual emulator: **five focused HTTP UI
cases**, **two force-stop GET-only recovery stages**, cold launch **Status ok**;
53s/51s instrumentation gates. Compact label assertion initially missed an
uncomposed offscreen item; scrolling actual list/child passed. Settings restored.

Web root clean install hit a Windows locked DLL owned by pre-existing Vite and
removed some other dependencies. Kept that process running; isolated same-lockfile
npm ci270packages/zero vulnerabilities succeeded, missing workspace dependencies
restored without overwriting the matching locked DLL. Isolated generation/freshness/
type/lint/**55 units** (29.26s)/production build and **six PostgreSQL Chromium
cases** (21.3s, port5174) passed; generated contract copied back and workspace
freshness/type/lint passed. User port5173 process remains active. No credentials,
raw private text, screenshots or browser traces recorded.

Windows/PostgreSQL/device/model evidence: migrated disposable native PostgreSQL
18.6 on task-owned55414 plusSQLite, API37/Android17 emulator, deterministic HTTP
fixtures and production Chromium. Native **Ollama/qwen3.8:27b** separately passed
incremental completion/Stop/original receipt/local admission release and old
nonstreaming follow-up. Final provider review measured firstdelta/total17,281/
18,703ms (691input/14outputtokens), Stop2,125/2,235ms (countsunknown). Earlier
smoke16,547/18,485ms (691/16tokens), Stop2,172/2,265ms retained. Native smoke predates
final finish-time defense; final affected provider/legacy/expiry tests passed.
Local iterator shutdown is measured, remote GPU acknowledgement/quality/load is not.

Checks skipped/blocked: full15SQLitelocking copies with executed PG counterparts,
sixprior nativeagent opt-ins/twoOllama-health opt-ins; finaltwoSQLitelocking copies.
Whole old instrumentation, API26/physical S24FEAndroid16, HTTPS/network/manual
TalkBack/release signing/otherbrowsers/representative native load/quality not run.
Fresh application read observed0005; installing0013 is pending and not performed.
Existing test-client/npm/lint warnings retained, no unrelated dependency upgrade.

Remaining issues: backed-up intended installation and target checks; count-bounded
private stream retention. 24hcursor expiry is not physical erasure; account/backups/
historical snapshot retention requires a separately selected policy. Old blocked
synthetic cleanup artifacts untouched; new ignored verification artifacts retained.

Next eligible checkpoint: separately requested installation/target verification
or Phase17. Stop at16; no voice, autonomous background tasks, external effects,
later phase implementation or deployment.

Final Phase 16 audit — 2026-10-12 04:20 UTC (2026-10-11 21:20 Phoenix):
Ruff lint/format138files,16UTF-8/local-link Markdown checks and whitespace passed
after the final changes. OpenAPI/protected-history/fixture compatibility audit
passed. Disposable PG schemas count zero; only the task-owned PG55414/emulator5556
were stopped. No task fixture HTTP18763–18765 or isolated web5174 listeners remain.
The pre-existing user Vite5173/PID636 and PostgreSQL5432 were retained. Prior blocked
synthetic artifacts and new ignored validation evidence retained. No unresolved
local check failure; intended installation and target/retention gates remain.


## 2026-10-12 — Phase 17 explicit Android voice input/output

Scope: only plans/phase-17-voice-interface.md, no later phase/deployment. Read root
and scoped rules, README/architecture/current state/standards/workflow/status,
plans README and the requested phase. Inspected clean source at 18690f0, migrations,
OpenAPI 86 paths/122 schemas and 76 fixture payloads plus manifest. Final inventory
is 79 payloads plus manifest. Captured protected hashes before editing. Phases 04/16 were
implemented; target installation/device gates from those phases remain distinct.
User confirmed English(en-US); it is the recording default, with selectable,
validated language tags. S24 FE/Android 16 remains the intended physical target.

Decision: Android API 31+ on-device SpeechRecognizer only, API 33+ installed-language
support preflight, no model download/system-network fallback/server audio. Primary
SpeechRecognizer/RecognitionSupport/RecognizerIntent/TTS/Voice/audio-focus/noisy
broadcast documentation informed the choice; links and support/resource/privacy
limits are in [VOICE-INTERFACE.md](../docs/VOICE-INTERFACE.md). SDK/platform version
and elapsed duration are client reported, not an attested binary/audio provenance.
No app audio file/buffer or server hash is manufactured.

Changes: additive0014 typed immutable owner/scope/request/capture lineage with
separate generated original text and exact endorsed user event/source; compatible
review-required POST and owned GET/list routes. A separate fingerprint domain
binds original metadata and old chat options, preserving old completed replay.
Reservations/lineage are atomic and inference remains outside transactions;
quota/foreign keys/duplicate capture/approval/downgrade errors fail closed. No
ASR original is factual memory or model context. Old migrations/prompts unchanged.

Android0.17.0-voice (versionCode 12) adds record/check/transcribe/review states,
runtime denial/permanent-denial/unavailable states, editable original-preserving
review, explicit approval and encrypted v10 atomic pending commit. Old journals
remain readable. Recording is bounded at 60s with 15s setup/final deadlines and
lifecycle/audio fences. Unconfirmed background saves recover on resume; recovery
blocks recording and another conversation's saved draft offers Open/discard.
Normal text composition remains independent. Rejected voice never drops into
plain authored text; old servers cannot enable or fallback the voice write path.
Optional installed offline TTS reads fresh completed safe replies, with bounded
Unicode-safe utterances, voices/speeds and separate Stop/focus/noisy/device/pause
handling. Server generation retains explicit Phase 16 Stop.

Validation actually run (logs/artifacts ignored under .pytest_cache/phase17):

- Baseline SQLite+PG 18.6:639 passed/23 skipped/one existing warning, 579.88s; Ruff 138
  files; Android baseline 194 units/lint/debug build; web contracts/55 units.
- Server initial red:2 missing-route failures. Journal initial red:2 absent-store
  failures. First invariant set 52 passed/2 failures caused by a test using an
  incomplete Request composite key; corrected the assertion. Voice+streaming 79
  passed/1 expected SQLite skip. Populated 0013→0014, Alembic check, old replay,
  native FKs, guarded downgrade, authorization/admin separation, corruption,
  approval/malformed metadata, atomic quota rollback, concurrent differing input,
  cancel/retry and original-vs-reviewed model context are covered.
- Fixture export initially failed for the new test helper call signature, then
  for a synthetic provider branch that intentionally waits on non-completion
  content. Corrected test arguments and bounded completion fixture branch; export
  passed. Preserved old payload bytes except capabilities/readiness; added three
  schema-checked HTTP voice payloads. Final suite checks SQLite and PostgreSQL.
- First full suite 694 passed/23 skips/one failure, 683.92s: PostgreSQL hybrid fixture
  fallback 1/13 rather than its zero-fallback expectation, with integrity/ownership
  passing. No retrieval implementation or expected assertion changed. Focused
  hybrid+voice 59 passed 54.11s, repeated full 695 passed/23 skips 645.99s. Skips15
  SQLite lock copies/6 opt-in native agent copies/2 opt-in native health copies;
  PostgreSQL lock/schema cases ran. Existing Starlette/httpx warning unchanged.
- Final Ruff/format 144 files, compileall and diff whitespace passed. Compatibility
  audit: all 86 old paths identical; only two optional capability properties change
  among 122 old schemas ; 3 new routes/3 new schemas.22 protected hashes unchanged.
- Android compile/test fixes were test-class name collisions, a MockWebServer
  IPv6 credential fixture and an incorrect source API method name. Initial lint
  caught GET_DEVICES_ALL's annotation; used the input/output flag union. Removed
  the new URI/KTX lint warning. Final 211 units passed, 0 skipped; lint 0 errors/14
  existing pinned-dependency warnings; debug/test APKs passed. v9/v10, foreign
  scope, interrupted save and recovered-draft/old-server gates are covered.
- Final normal emulator suite 7 passed, 0 skips; final compact 900×500/240dpi/font1.5
  voice suite 2 passed, 0 skips;4 actual force-stop prepare/resume stages passed.
  Explicit synthetic capture/playback adapters exercise real HTTP/Compose/
  Keystore/review/lineage and independent generation Stop; actual activity pause
  and late callback rejection are asserted. Native factory probe reports
  Available on Android 17/API 37; en-US pack/recognition/audio quality was not tested.
  Final actual cold launch Status:ok/COLD,TotalTime2517 ms. Restored geometry/font.
- Web pinned isolated npm ci passed 13s (270 packages, 0 audit findings); root clean
  install skipped to preserve the existing user Vite installation. DTO freshness,
  typecheck/lint,55 units 18.72s, production build and Chromium installation passed;
  six real PG-backed Chromium checks 27.4s on build preview 5174. Temporary test
  config first failed because Node refuses type stripping under node_modules,
  then because server cwd was the config directory; moved it under ignored build
  and set explicit cwd. Final browser run passed. Locks/wrappers unchanged.
- Updated privacy/user/architecture/current-state/decision/contract documentation,
  requested phase checkpoint record and status; UTF-8/local-link checks passed.

Remaining target work: S24 FE/Android 16 physical mic/speaker/headsets, installed
on-device en-US and speech samples/corrections, airplane-mode ASR/TTS, Android
permission dialogs/revocation, real focus/calls/Bluetooth/noisy-route handling,
latency/resources/battery, older API 26/31/33, release HTTPS/manual accessibility
and retained transcript/account/backup policy. Server audio decoding/malformed
file/provider ASR checks are inapplicable to this no-audio route; forbidden audio
JSON and text/metadata limits are tested. Native real-model opt-ins were skipped;
only a generation-free read confirmed installed configured native model. Fresh
configured application read observed 0005; no application migration was performed.

Cleanup 11:44 UTC: 0 remaining disposable PG schemas. Only own PG 55417/emulator 5556
stopped; own fixture HTTP 18763/18765/web 5174 absent. User PG 5432/PID 8868 untouched;
no user Vite 5173 stop command issued (final inventory found no listener). Prior
records and ignored validation evidence preserved. No unresolved local check
failure after the recorded reruns; target readiness remains pending. Stop at Phase 17.


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


## 2026-10-13 UTC — Phase 17-A S24 FE audit/planned hardening — 2c242d1

Scope: physical target tests and a follow-up plan requested by the user. Session
crossed midnight America/Phoenix. No authorization to implement fixes/later phases
or deploy. Required instructions/docs, current source/migration/contract/test
baseline inspected. User supplied real en-US samples via phone mic; no headset.

Changed behavior/files: product behavior unchanged. Added
`plans/phase-17-a-s24-fe-validation-and-hardening.md` as Planned; indexed it in
plans/README and updated STATUS, CURRENT-STATE, Phase17 audit note and voice
policy. Temporary ignored test-copy package/origins/native diagnostics and a
separate UID focus fixture were used solely for validation. They were removed
from the phone at cleanup; no production test/source fix was committed.

Data/API/prompt changes: none. Protected353 files unchanged. Actual fixture HTTP
OpenAPI equals committed89-path/125-schema contract. Disposable SQLite head0014,
authenticated owner and fake model; no intended application migration or private
account inspection. Historical configured0005 was not refreshed in this audit.

Checks actually run/results:

- Focused backend voice/streaming pytest40 passed/42 skipped/29.19s; one existing
  Starlette/httpx warning.41 absent PostgreSQL fixture copies plus1 SQLite native
  lock copy skipped. Current Android isolated unit XML211/0failures/0skips;
  unit/lint/debug/test-APK build110s; lint0errors/14existing dependency warnings.
- Native inventory1 passed/2.72s: on-device available, installed en-US and15
  eligible offline TTS voices,10en-US. R1 quality invalid because user not ready;
  review/no-send observed. R2 exact quiet8words:0errors,ready386ms/result7625ms,
  capture7238ms; R3 real airplane/Wi-Fi/data-off:0errors,ready504ms/result5825ms,
  capture5276ms.1test each passed19.498/29.953s. User confirmed conditions.
  Review/edit/approval/duplicate-Send/owned lineage assertions ran over real HTTP.
- Offline installed speaker/rates/explicit Stop and owned reply actual activity
  pause/no resume:1passed25.586s; rate durations5589/4664/3758/3157ms. User confirmed
  clarity/rates/stopping. Same-UID focus probe explicitly inconclusive.
- Native capture pause/navigation/missing-language plus layout-adapted streaming
 2passed18.587s. Four true force-stop prepare/resume stages passed1.156/2.120/
  1.194/7.051s. Saved draft and original pending request recover without new POST.
- Selected physical suite16:13passed/1integration-flag skip/2failures61.476s.
  Flag-enabled retry5:4passed/1locator failure19.919s. Voice wait timeout did not
  recur; streaming compact-container assumption reproduced. Correcting only
  temporary test locators passed unchanged production noncompact layout.
  Physical memory4/platform1/Keystore6 passed. Font150% portrait5passed36.277s;
  landscape voice2passed8.442s; palettes and persistence included.
- Verified real first Allow/first Deny failed expected state:Interrupted instead
  of Checking/Recording or Denied. Multiple verified Deny repros. Second/third
  denial attempts without verified clicks/unexpected grants remain inconclusive
  for permanent denial. Do not attribute their results to a proven product defect.
- Separate-UID combined TTS focus probes failed twice. Final isolated focus
  probe1failed6.489s: foreground competitor result=granted/window focus=true;
  adapter interruption callback absent. Root cause and audible behavior unresolved;
  lifecycle stopping passed independently. Native focus remains an open gate.
- Cold debug575ms and final538ms. Foreground post-launch PSS120751KiB,
  RSS217965KiB/swap584KiB; idle app CPU4ticks/~2s without tick-frequency conversion.
  USB charging throughout47→64%, temperature36.2→39.7C; not a drain/energy or
  speech-attributable thermal benchmark. Speech-service CPU/RAM not measured.
- Final Ruff `src tests scripts migrations` lint/format144files passed; broader
  `.` lint/format198files also passed. Final UTF-8/local-link/protected-file and
  whitespace checks are recorded at closeout below.

Harness failures preserved: initial SDK path absence fixed in ignored copy;
initial native interruption test failed to re-expand voice controls after Settings,
then passed; unreliable external dialog synchronization/early manual choice and
synthetic setup timeouts excluded; compact-only streaming locators adapted in
ignored tests. Final product permission/focus failures remain visible, not erased
by successful unit/emulator evidence. No transcript contents/tokens in logs/plans.

Checks skipped/remaining: full PostgreSQL/web/native model reruns (no product/schema
change); noisy/representative speech,60s native cap/setup/final deadlines, reliable
permanent denial/revocation/settings return, real call/headset/Bluetooth/noisy-route,
speech-service resource profile/unplugged battery, API26/31/33, manual TalkBack/
keyboard, release HTTPS, intended installation/retention review. Only phone mic
available; USB charging prevents drain attribution. Server audio decode/upload
checks inapplicable. Old Phase17 full-suite evidence stays historical.

Windows/device evidence/cleanup: SM-S721U1/Android16/API36 primary user0;
1080×2340/450dpi. Protected user's ADA v12/0.17.0-voice and RECORD_AUDIO=false.
Restored airplane0/Wi-Fi1/data1/font1.0/rotation0/auto-rotation0; Bluetooth unchanged1.
Stopped only verified owned fixture18767; removed owned reverse18764/18765 and
uninstalled only validation runner/app/focus fixture for user0. No Secure Folder,
production DB/provider/service or user's app data modification. Ignored safe
artifacts retained. No deployment or later phase work.

Remaining issues:17A-01 confirmed permission-dialog lifecycle defect;17A-02 native
focus callback failure needs investigation/fix;17A-03 physical runner/locator/
dialog verification changes. Full target readiness is not claimed.
Next eligible checkpoint: explicitly select Phase17-A implementation, starting
with permission invariants/failure tests; later phases remain planned.


Audit closeout — 2026-10-13 07:44 UTC (00:44 America/Phoenix):
Seven changed/new Markdown files passed UTF-8 and53 local-link checks;
protected353 files remain byte-identical to the pre-audit baseline at2c242d1.
Git whitespace check passed. Fresh cleanup verification found no validation
packages, owned reverse18764/18765 mappings or fixture18767 listener; all modified
phone settings matched the recorded originals. Prior records remain preserved.
No production fix, intended database migration, later phase or deployment.


## 2026-10-13 — developer HOW-TO-USE-ADA guide — 2c242d1

Scope: user requested a detailed developer walkthrough with concrete commands,
client field values, startup requirements and troubleshooting. Documentation only;
no phase17-A fix or later-phase implementation authorized or performed.

Changed files/behavior: added docs/HOW-TO-USE-ADA.md; linked root/Android/admin
READMEs, corrected current admin readiness requirements in its README and monitoring
policy to0014, appended STATUS/WORKLOG. Guide covers fresh setup versus preserving
existing data, private Docker backup outside Git, account UUID versus token/name,
USB8000 versus emulator10.0.2.2 and admin5173 fixed proxy, source-matched UI labels,
review/retry/provenance boundaries, CLI/demo memory, daily operation, troubleshooting
and optional developer checks. Known S24 FE permission workaround/native focus
failure and pending verification are retained. Earlier audit edits/evidence intact.
Data/API/prompt/dependency changes: none. No real secrets, chats or quotes added.

Checks actually run: pytest memory CLI/upgrade installer/client contract **8passed,
3skipped in3.26s** (3 missing PostgreSQL fixture copies), existing Starlette/httpx
warning. Ruff src/tests/migrations/scripts lint/format144files passed. Eleven CLI
help invocations verified illustrated commands/options; actual Alembic heads0014
matched src/ada/schema.py and current OpenAPI `/v1/me` fields. Native PowerShell AST
parse passed48 fenced examples, no example execution;14contents anchors and135
local links/UTF-8 across12 combined changed/new Markdown files passed. Protected
415implementation/test/contract/wrapper/lock hashes unchanged; Markdown-only diff
and whitespace passed. Official installer/device/provider/Compose documentation
checked via web; repository pins remain unchanged. First validator attempts used
Windows default text encoding and missed indented fences; corrected UTF-8/fence
extraction passed, with no guide command-syntax failure.

Skipped/limits: no complete install/runtime rehearsal, PostgreSQL full suite,
Android/web rebuild/UI/physical audio, model download/inference or release HTTPS.
No application database revision read/migration, account/token/admin mutation,
backup or service launch; such commands are instructions for the developer, not
new execution evidence. Doc-only scope and unchanged implementation do not justify
reinstalling clients/dependencies or repeating prior physical tests. Historical
Phase17 and17-A validation remains evidence of its own sessions.
Windows evidence: PowerShell parser checked examples on this Windows workspace;
portable links use forward slashes and private values stay out of text. Current
machine/client date13October2026, America/Phoenix; machine checks timestamped UTC.
Remaining issues: current17-A permission/focus/physical-runner plan and previously
recorded target installation/older API/accessory/resource/battery/accessibility/TLS
gates. Next eligible work is user-selected; this guide does not authorize it.


Documentation closeout — 2026-10-13 08:42 UTC (01:42 America/Phoenix):
Final UTF-8/local-link check passed12 Markdown files/136 local links (including
preserved prior audit edits);415 protected implementation/contract/test/wrapper/
lock hashes unchanged and whitespace check passed. Guide is linked from the main
and client READMEs. No runtime setup, application migration or deployment performed.

### 2026-10-14 — Phase17-A and Phase18 — working tree based on2c242d1

Scope: authorized17-A hardening followed by18 only. User selected encrypted local
backup directory `%LOCALAPPDATA%/ADA/backups` and retain-until-explicit-deletion.
**User requested testing stop to disconnect the S24 FE and resume tomorrow.**
This checkpoint saves implemented work and actual evidence; final verification
is incomplete. Earlier uncommitted audit/how-to documents are preserved.

Changed behavior/files: Android permission-dialog context/lifecycle fencing,
per-acquisition focus leases, speech/media attributes and isolated native public
probe; selected-device safe runner, OS permission/HTTP/Keystore/force-stop tests,
fixture-origin and layout/IME fixes. Phase18 adds security models/services/gate/API,
explicit45-table erasure inventory/worker and epochs, encrypted PostgreSQL recovery
CLI, Android security contracts/controller/settings/v11 journals, admin privacy
cache fencing, start bounds, contract fixtures and operational runbooks. Device
labels/expiry appear normally; raw IDs/table counts are optional technical details.

Data/API/prompt changes: additive0015 after untouched released0001–0014; legacy
CLI tokens and archived prompts remain compatible. Digest-only device enrollment
is configured off, erasure processing off, one worker retained. Rotation revokes
immediately; replay never reissues a stored secret. Owner-authorized deletion is
an explicit immutable-history exception, with UUID tombstones/410 and cache epochs.
Account/credentials/grants/minimal operation metadata remain. Backups/offline
clients may retain copies. OpenAPI96paths/132schemas versus89/125; defaulted epoch/
capability fields are additive. Nine synthetic fixtures added, no issue secret
captured. Cryptography50.0.2 plus pinned transitives is the scoped dependency change.

Checks actually run and results: baselineSQLite382passed/336skipped; focusedPG18
81passed/1SQLite-lockskip. New permission tests failed3 before fix, then13passed.
New security invariants failed9/9skipped before implementation. Expanded nativePG
and graph/restore tests passed after failures in admin SQL projection, safe lower
migration downgrade preflight, restore public-schema setup/typed ledger binds and
fixture isolation were fixed. FullPG18/SQLite747passed/23skipped/1warning978.20s;
subsequent affected62passed/1skip112.80s; final narrow standalone-inventory fix
covered by closeout **63passed/1skip/1warning130.00s**. Ruff lint/format154files
passed. Existing Starlette/httpx warning remains; skipped cases are deliberate
SQLite/provider/optional fixture limits, not completed PostgreSQL passes.

Android latest unit/lint/debug/instrumentation/unsigned-release/fixture build
passed38s,161tasks27executed; unit report224passed/0failed/0skipped. Earlier lockfile
fixture version expectations, MockWebServer host, Windows concurrent Gradle file
lock and late optional-detail UUID-to-Text compile error were corrected; subsequent
builds passed sequentially. Validation APK IDs were checked before installation.
No normal app was installed or reset. API37 isolated emulator passed8HTTP/Compose
checks,2real OS-dialog cases,4actual force-stop stages and SecurityUI. S24 FE/API36
retry passed8checks43.148s, first OSgrant3.238s, denial/permanent2.607s,4force-stop
stages, SecurityUI6.295s. Initial phone run failed window-focus preconditions;
user unlocked before retry. OS-dialog cases use synthetic capture, not native ASR.

User heard clear public native TTS and explicit Stop. Earlier manual trials had
stale/non-overlapping competitor focus and remain inconclusive. Latest native-start
staged full-focus probe recorded a new granted competitor request, native transient
loss and interruption callback about6.6s after speech start. User said speech
continued in the fixture, then paused testing before confirming whether it stopped
after a delay. **Audible full-focus stop is not passed; transient/duck trials remain
open.** No native microphone quality sample was newly recorded in this session.

Web clean install/typecheck/lint/build/contract generation/check and56units passed.
An initial bad fixture environment variable caused E2E timeout; corrected full
run had5passed/1refresh-focus failure, focused retry passed, final fullPG-backed
Chromium **6passed25.5s**. Python lock audit0known vulnerabilities/41deps; npm audit
0findings/295deps. Audit-time results are not a general security guarantee.

Windows/PostgreSQL/device evidence: nativePG18 populated54-table snapshot/restore
with original replay/citations/source hashes/jobs and credential quarantine,
later deletion reconciliation and rollback tests. Latest completed drill measured
backup0.516s/restore1.25s on small isolated fixture; committed exported snapshot+
latest supplied ledger is the data-loss boundary, not a productionRTO/RPO guarantee.
Physical test device modelSM-S721U1/API36 primaryuser0; no serial in durable records.
Portable paths/forward slashes and historical prompt/replay behavior are preserved
by design; final protected-file byte/newline audit remains pending.

Checks skipped/remaining: native audible focus overlap confirmation, settings-return
and active native microphone revocation, real calls/headsets/noisy routing,
representative speech/native cap/deadlines, app/service resources and real unplugged
battery, olderAPI26–33, manual TalkBack/IME. Caddy template syntax and actual private
HTTPS remain unverified. Final source/contract/protected-history/doc audits and
installation/capacity/live operations remain separate. Do not present prior native
model or historical phone results as new Phase18 passes.

Cleanup at pause: isolated physical app/test/focus packages removed foruser0;
reverse19820 and owned fixture removed. Normal debug versionCode12 unchanged.
Owned read-only emulator stopped. After the already-started final affected run
completed, ownedPG18 loopback55418 was shut down using its checked task data path.
No user PostgreSQL/Ollama/application service, normal Android data/permission or
private profile was changed. No live backup/migration/erasure, deployment,
publication, external message or Phase19 work.

Next eligible checkpoint: resume remaining17-A/18 verification from this saved
state when user is ready. Recreate only disposable fixtures/validation packages;
collect a fresh overlapping granted focus trial and human audible observation.
Do not restart implementation or proceed toPhase19.
