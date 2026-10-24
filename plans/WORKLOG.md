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


### 2026-10-15 — gap audit + future planning (documentation only) — working tree based on2c242d1

Scope: read-only audit of all plans/ documents versus source, tests, contracts,
migrations and clients, plus a user-requested future-planning record.
Documentation only; no implementation, installation or deployment authorized or
performed. Session ran at clean HEAD fa2cbba (child of 2c242d1); the working
tree was left with only the three documentation changes below.

Changed behavior/files: created plans/GAPS-AND-FUTURE-PLANS.md (29 gaps
G-01…G-29, 13 future-plan proposals F-0…F-12, recommended sequencing, log
conventions); appended short pointer sections to plans/STATUS.md and this
WORKLOG entry. No product behavior change.

Data/API/prompt changes: none. No migrations, contracts, fixtures, prompts,
locks, wrappers or dependencies touched; released 0001–0015 and the exported
OpenAPI are unchanged by this session.

Checks actually run and results (all read-only):

- Read all plans/ documents (phase-02a…19, README, CURRENT-STATE, STANDARDS,
  CODEX-WORKFLOW, STATUS, WORKLOG, DECISIONS, SOURCES, UI-SPEC), root README,
  root and plans AGENTS.md, and docs/ARCHITECTURE.md.
- Glob migrations/versions confirmed all 15 files 0001–0015
  (0001_phase_0 … 0015_security_and_operations).
- Glob/read src/ada module inventory confirmed per-phase modules: documents,
  entities, embeddings/semantic, proposals, agents+tools, consolidation,
  expression, learning, streaming, voice, security plus models/contracts/api
  files.
- Read src/ada/api.py capabilities block (lines 394–454): shared_scopes false,
  edge_inference false, automatic_affect_inference false,
  automatic_memory_extraction false, voice_audio_uploads false, tools false,
  agent_registry calculator/memory_lookup/source_lookup,
  document_ingestion text_markdown_v1, semantic_retrieval config-dependent
  (disabled by default), device_credentials ada-device-credentials-v1,
  private_deletion ada-private-deletion-v1.
- Grep "password" in src/ada: matches only in operations.py backup-encryption
  helpers (seal/unseal/scrypt/backup/restore); no account password
  authentication exists.
- Grep scheduler/idle/dream (case-insensitive) in src/ada: no matches except
  IDLE_MS in expression.py (30-minute session-tone expiry constant); no
  scheduler, idle detection or dreaming code.
- Tool registry grep: calculator/memory_lookup/source_lookup only.
- Read scripts/start.ps1: loopback-only bind (ValidateSet 127.0.0.1/::1),
  exactly one Uvicorn worker, no access log.
- Read apps/android/app/build.gradle.kts: versionCode 13 / 0.18.0-security.
- Confirmed OpenAPI 96 paths/132 schemas per the 2026-10-14 entry above (not
  re-exported in this session).
- Citation checks: README.md and docs/PHASE2-RETRIEVAL.md document the "as of
  YYYY-MM-DD" date-parsing contract (G-18); the Phase 19B durable-schedule
  requirement was confirmed verbatim in
  plans/phase-19-edge-and-external-integrations.md (G-25).
- Git: HEAD fa2cbba, parent 2c242d1, working tree clean at session start.

Checks skipped/blocked and reason: no test suite rerun (documentation-only
session, no code changed); no live database query (installation is separately
authorized work, not part of this session); no device, browser or model
evidence collected.

Windows/PostgreSQL/device/model evidence: none new.

Remaining issues: none from this session — all findings are logged in
plans/GAPS-AND-FUTURE-PLANS.md.

Next eligible checkpoint: F-0 (close known gaps, including the authorized
installation) or a user-selected F-xx, upon explicit selection.

### 2026-10-16 — future roadmap review — source fa2cbba — documentation only

Scope: evaluate GAPS-AND-FUTURE-PLANS against actual source and propose future
plans starting at Phase 20. Exclude connected-Android and iOS validation. No
implementation, deployment or live installation. Preserved preexisting STATUS/
WORKLOG edits, the original gap audit and unrelated workspace files.

Changed behavior/files: no product behavior. Added FUTURE-ROADMAP and twelve
phase files 20–31: readiness/evaluation, private HTTPS, password sessions, answer
relevance, approved web research, conversational curiosity, always-on recovery,
durable schedules, idle reflection, local speech study, optional projects and
PDFs. Linked plans/root README; appended sources/decisions/status and this log.
Original 29 gaps mapped, dated corrections added, G-30–G-40 left Open. Phase 19
remains conditional; no old milestone renumbered or retroactively marked complete.

Data/API/prompt changes: none. Proposed password login preserves existing token
compatibility while hiding manual token handling from ordinary clients; admin
grants remain server-controlled. Web research needs exact disclosure approval,
network isolation and private saved citations. Curiosity can begin with generic
questions, with grounded premises for personalized ones; it is not automatic
memory/profile creation. Dreaming reuses explicit jobs behind new consent and
bounded scheduling/foreground priority. Preserve retain-until-owner-deletion and
require every new schema to extend erasure/backup/authority quarantine.

Inspection/checks actually run: read root/plans instructions and requested docs;
inspected phase statuses/checklists/deferrals, actual auth/security middleware,
backup/restore, inventory, tools/agents, consolidation/proposals, config/capabilities,
Android HTTPS-origin parsing/security config and web bearer transport. Parsed
existing OpenAPI: 96 paths/132 schemas; enumerated 15 migrations, head constant
0015. Read representative security/recovery tests and evaluation script inventory;
no test executions or OpenAPI regeneration. Saved 525 tracked-file hashes before
editing for a planning-scope comparison. An initial multi-file documentation patch
failed context verification and applied nothing; corrected patch succeeded.

Primary documentation browsed: Tailscale Serve/HTTPS, OWASP password/auth/session,
SSRF/prompt injection, Windows Task Scheduler and candidate local speech runtime/
model sources. References saved in SOURCES. These support proposed design choices,
not installed functionality or on-device benchmarks. No dependency/model download.

Checks skipped and reason: pytest/Ruff/application builds/PG/browser/model/device
suites not rerun because product source/tests/contracts remain unchanged. No
configured DB, account/secret, VPN, host settings or phone was accessed. Historical
0005 is not a fresh live-state observation. Detailed documentation/protected-file
validation follows in the closeout entry; no old test counts are presented as new.

User choices: laptop kept plugged in/awake initially; all three curiosity channels
(active chat, inbox, occasional initiated conversations/notifications). No automatic
live activation or chosen notification provider. Daily task shortlist, provider
selection/fees, exact topic/hours and deployment window remain future preferences.

Remaining issues: Phase 18 final audits/target gates are still open; this review
adds actionable plans rather than claiming those checks complete. Especially close
legacy backup-before-upgrade, future-head recovery, unattended secret access,
foreground fairness, quotas and pre-auth password throttles before enabling the
corresponding features. Physical speech activation and iOS remain deferred.
Next eligible checkpoint: select Phase 20, or another independent proposed phase
only with its actual prerequisite evidence. No implementation is authorized by
these documents.

Planning closeout — 2026-10-16 America/Phoenix: UTF-8/local-link validation passed
20 changed/new Markdown documents and 122 local links. Twelve proposed phases
20–31 have unique numbering, checkpoints, interfaces, failure tests and exits;
all 29 prior gaps mapped, eleven added risks remain Open. 519 tracked files outside
six intentionally edited tracked documents match their pre-review SHA-256 hashes,
including implementation/tests/contracts/migrations/prompts/dependency locks.
Unrelated preexisting files preserved. Git diff whitespace check passed, with
informational Windows LF→CRLF notices only. First documentation validator identified
an implicit rather than labeled failure-test section in optional Phase 30; heading
clarified and rerun passed. No pytest/Ruff/client/device/model execution, live
installation, account mutation or deployment performed. This closes the planning
request, not any future implementation or historical Phase 18 validation gate.

### 2026-10-16 — Phase20 readiness/recovery/evaluation — base fa2cbba

Scope: only phase-20-release-readiness-and-quality-baseline; read required docs,
source/OpenAPI/tests and preserve prior uncommitted roadmap/unrelated work.
No live installation/deployment, physical Android/iOS or later-phase feature work.

Changed behavior/files: separate ada.legacy_recovery encrypted0005 operator tool;
ada.recovery_policy reviewed0005/0015 table inventories; operations preflight for
matching PG major/known tables and stronger malformed manifest rejection. Existing
0015 format remains supported. Added invariant/failure/native legacy drill tests.
Added evaluate_quality runner, frozen canonical corpus manifest/new8-case heldout
and saved public aggregate scorecard, reusing five existing evaluation programs.
Added actual Caddy-template/CA-verified loopback proxy lab and pinned validation
binary metadata; reproduced/fixed bare `/admin`404 with308redirect to `/admin/`.
Android runtime untouched: safe streaming failure diagnostics and bounded
-RecoveryOnly/stage output added to the isolated runner. Reconciled current docs/
17-A implementation boxes versus dated target evidence, added RELEASE-READINESS,
updated how-to/security references, gap dispositions and open G-41. No new migration,
API/capability/schema/prompt, dependencies/lockfile or installed application version.

Checks actually run: baseline recovery/schema/client-contract11passed33.17s,
Ruff154files and source/export equality96paths/132schemas. Initial Android build
passed13s mostly cached. New recovery failures3failed/2passed/1native skip before
features; quality3failed/1PGskip before runner. Native recovery9passed27.10s.
Expanded native run1failed/21passed exposed non-citing fake seed; corrected to a
public M1-citing fixture (not a runtime change), then22passed66.46s. Added import/
lint issue corrected. Full PG18.6/SQLite760passed/24skipped/1warning1019.24s; final
focused23passed/1warning81.70s after final tests/assertions (the full run preceded
those additions). Skip breakdown16SQLite native-lock/concurrency variants and
8opt-in live-Ollama metadata/tool probes; PG variants ran. Starlette/httpx warning
retained. Ruff160files passed; CLI help and syntax/documentation audit below.

Native PostgreSQL evidence: isolated new cluster loopback55420 only. Populated
legacy19-table source with claim/document/source/cited request; encrypted backup,
new isolated restore and quarantine, injected mid-upgrade transactional failure
rolled back to0005, retry upgraded to0015 with no drift and original cited replay/
source hashes. Wrong passphrase creates no target; unknown table/head/format,
simulated binary-major mismatch/full-disk error, inconsistent encrypted manifest
and existing/unsafe targets refused. Restored tokens remain invalid even on
post-restore hash failure. Original0005 source/credential unchanged. Latest legacy
backup0.594s/restore0.859s (19tables/1request); current populated54-table recovery
backup0.765s/restore1.312s with original replay/revocation/latest deletion ledger.
These are small fixture timings, not production recovery promises.

Quality evidence: ran all5existing adapters plus heldout on disposable stores;
extraction adapter remains SQLite, labeled accurately. Claim recall/MRR@5=.8667,
documents1.0, heldout recall/MRR/exact evidence1.0, zero known isolation/negative
failures. Other fixture gold/vector/marker results are not real-model quality.
Frozen corpus hashes are canonical across Windows CRLF and reject native/traversal
paths. Aggregate reports contain case IDs/counts/metrics/model identity, no private
inputs; semantic usefulness/citation entailment/uncertainty/follow-up remain null
with rubric. Saved scorecard records actual run time/source and resource limits.
No model download/semantic activation/prompt upgrade or private corpus use.

Android/web evidence: fresh rerun224units0failed0skipped55s; final lint/debug/
instrumentation/unsigned release passed64s (123tasks31executed). Owned read-only
API37 emulator strict cold launches3371/2683/2332ms Status:ok/COLD. First2HTTP
attempts failed stream-provisional timeout; diagnostics showedMissing/NotFound.
Instrumented retry8passed55.072s plusOSgrant6.955s and denial/permanent6.379s.
Combined force-stop resume failed without useful stage output; focused recovery
runner then passed4prepare/resume checks across2actual force-stops and SecurityUI
7.812s. Earlier failures retained; G-41Open, no production Android fix claimed.
All audio drivers synthetic except native availability; no physical/device audio
or older-API claim. Web npmci/contracts/typecheck/lint/build passed,56units6.91s,
production Chromium6passed23.3s on PG. No credentialed recordings. Python audit
0known/41deps and npm0findings/295deps, no-deps/hash-lock/deprecation notices kept.

Proxy evidence: official Caddy2.11.7 archive SHA512 verified and pin recorded;
initial SHA256 assumption failed before execution. Actual template validation plus
isolated TLS routing/auth forwarding/JSON404/admin redirect/nested SPA/SSE and
untrusted-CA/wrong-host rejection passed. Tightened negative harness assertions
needed direct TLS instead of HTTP exception-wrapper introspection; corrected.
Test CA trusted per-process only, synthetic upstream, no system trust or live ADA
connection. Real server auth/isolation is separately covered by PG/browser tests.

Skips/limits: no maintained0005 server checkout in history (0004 then0006), so
matching old-server HTTP remains unverified; frozen schema/current forward replay
is demonstrated. Local model endpoint unavailable, no new real-model inference.
Manual screen-reader, actual trusted private HTTPS, intended live installation,
real sizing/capacity and physical/iOS gates remain separate. Preserve selected
retain-until-owner-deletion and 256MiB/retained quotas; no scheduler/pruning/new
runtime features. G-41 emulator intermittency needs controlled-load tracing before
operational release. Do not infer a fixed product from passed retries.

Cleanup: task-owned validation apps/test packages and USB reverse19822 removed;
read-only emulator5582 stopped. Verified owned PG data path/port55420 before stop;
startup controller held by Windows descendant-waiting stopped separately. No own
18420/19420/19822/55420 listener remained. Prior historical synthetic evidence kept;
no broad cleanup. Normal phone/data/profiles, user services/.env/live DB/grants/
credentials/firewall/VPN/trust store unchanged. No deployment/commit/external
message. Next eligible work: selected follow-up release verification or a separately
chosen later phase with its actual prerequisites; no automatic continuation.

Phase20 closeout — 2026-10-16 America/Phoenix: documentation UTF-8/205local links
passed across27Markdown files;66PowerShell examples and runner parsed without
execution.509tracked files outside16intentional tracked edits byte-identical to
the initial working tree, including all released migrations, contracts/fixtures,
prompts, locks and Android production source.12later-phase files (19,21–31) also
byte-identical. Prior planning/unrelated changes preserved. Whitespace passed;
Windows LF→CRLF notices informational. Code contract remains96paths/132schemas,
head0015; no deployment, live query/migration/backup, physical client or later
implementation. Final run artifacts remain ignored under .pytest_cache/phase20;
saved public scorecard is evaluations/quality-baseline-results-v1.json. All owned
services/emulator/resources cleaned up as described above. Phase20 tooling and
baseline delivered with recorded remaining release gates; stop here.

### 2026-10-16 — separately authorized local operation and DB guide — fa2cbba + Phase20 tree

Scope: user explicitly requested database changes/deployment, allowing a reset
if needed, and one step-by-step Windows database guide. Inspection found the
configured Docker PostgreSQL17.11 application database already at0015/54tables
on127.0.0.1:5433. No pending migration or destructive reset was necessary.

Changed behavior/files: started one current-source loopback API8000 worker,
Ollama11434 with installed qwen3.8:27b, and the freshly built admin preview5173.
Existing healthy Compose db remained running; native PostgreSQL5432 untouched.
Added docs/DATABASE-ADMINISTRATION-WINDOWS.md with access, safe queries, account
commands, migrations, matching17 recovery-client prerequisite, encrypted backup/
isolated restore, transaction practice, guarded optional reset and daily operation.
Linked it from README/HOW-TO/architecture/current state; refreshed G-01 with actual
installation evidence while preserving the original audit and Phase20 history.

Data/API/prompt changes: no schema/API/prompt/source-runtime change, `.env` edit,
model pull, existing credential rotation or existing grant change. No-op Alembic
upgrade and no-drift check completed on the verified intended target. Two original
accounts and all existing saved records retained. Device enrollment, erasure
worker, embeddings and consolidation settings preserved. Only ephemeral synthetic
validation account/content/grant writes plus normal monitoring audits occurred.

Checks actually run/results: Docker pg_isready and safe SQL metadata/head checks,
doctor, API live/ready200 and unauthenticated me401 passed. Through the built
preview proxy, synthetic authenticated me/capabilities, ordinary admin403,
explicit grant then five monitoring reads200, personality/conversation creation,
real Ollama chat and identical completed replay passed. First real generation
18.359s; final full rerun2.297s, two events. Initial final event-count assertion
failed because the one-off harness assumed an object instead of the contracted
list; fixed that harness and reran, with no product change. Both temporary owners,
their exact content/grants removed transactionally; original users/credential/
grant/history/source rows compared unchanged. Minimal monitoring audits retained.

Focused pytest schema/client/admin/admin-HTTP:37passed/2skipped/1warning46.31s,
SQLite plus disposable schemas in Docker17 ada_phase2_test. Two opt-in real-model
metadata probes then explicitly enabled:2passed/1warning2.00s, no generation.
Ruff lint/format160files passed. npm contract freshness/typecheck/build passed.
Guide's synthetic temporary-table practice ran against live PostgreSQL17 and
rolled back completely. New guide's commands were checked against source CLI
interfaces; destructive examples were not executed. Runtime smoke metadata only
is in ignored .pytest_cache/local-install; no secrets/content in reports. Runtime
process logs are local under %LOCALAPPDATA%/ADA/logs, API access logging disabled.

Checks skipped/limits: no actual live encrypted backup/restore, reset, pending
migration or GUI pgAdmin trial. Live PG17 needs matching Windows17 recovery
clients (only18 installed) and a separately retained passphrase before the backup
CLI can run; no new key/artifact was created. No full-suite repetition after the
earlier Phase20 evidence for this docs/operator-only work. No physical/iOS,
manual accessibility, remote HTTPS/LAN/VPN, firewall/trust change, unattended
service/scheduler, sustained-load or semantic-quality claim. G-06/G-09/G-41 stay
open. Ordinary process hosting is not Phase26 supervision or Phase21 connectivity.

Windows evidence: Docker port5433, API8000, preview5173 and Ollama11434 all remain
private/loopback. Services intentionally left running for user access, with
startup/shutdown instructions in the guide; not installed as auto-start services.
Remaining target verification and the local G-01 closure are detailed in STATUS.
Stop at this authorized operational follow-up; no later feature or commit.

Closeout:8UTF-8 documents/108local links and24new-guide PowerShell AST examples
passed. Windows18 psql queried live17 using protected environment, proving the
optional Windows query route while leaving recovery's17-tool requirement intact.
Final health/ready200, previewHTML200, unauthenticated proxy401, live OpenAPI exact
equality and zero leftover temporary owners passed; original counts2/3/4/14/27/
27/27(users/personalities/conversations/requests/events/sources/versions). Git
whitespace passed with informational existing LF→CRLF notices. Reset/restore
examples were parsed/reviewed, not executed; the tested temporary-table changes
were rolled back. Local services intentionally remain running for user access.

### 2026-10-16 — Phase21 A–D — fed5d4b working tree

Scope: implement only private-network connectivity; no deployment/later features.
Read root/plans/client rules, required status/roadmap/architecture/current source,
96-path/132-schema OpenAPI, migrations and test baseline first. Phase20/private
auth/readiness prerequisites exist; no schema/endpoint/prompt change required.

Changed behavior/files: Android ServerProfiles/ServerAddressPanel and transport
preflight add bounded named HTTPS metadata, explicit switch/clear/remove, reviewed
version1 JSON import, credential-free readiness and native TLS/DNS diagnostics.
Profiles do not contain credentials/trust overrides or auto-connect. Existing
server/owner/generation recovery fences and encrypted private journals remain.
Version14/0.21.0-connectivity. Web admin sign-in also probes readiness without
Authorization; native/public503 diagnostics avoid claiming an unknown proxy
failure is a DB failure. Fixed Vite `/health` proxy and strict original-path origin
validation keep development/preview same-origin. New Caddy tailnet template binds
loopback accepting forwarded Host; LAN template defaults to loopback until selected.
New PRIVATE-NETWORK-CONNECTIVITY runbook and disposable real-ADA/Caddy rehearsal.
Updated navigation/current/phase/decision/gap/source records. No camera/deep link,
discovery, login22, certificate bypass, native provider access or new permission.

Data/API/prompt changes: none on server; 0015/96paths/132schemas unchanged. Released
history, Python production source, contracts/prompts/locks preserved. No app DB
migration/write, `.env` edit, live account/grant/credential change, VPN/firewall/DNS/
trust enrollment or live proxy installation. All test writes used disposable
SQLite/owned PG fixtures; fake providers only, no external private data/model run.

Checks actually run: before edits, Android52selectedunits27s, web56units30.75s,
schema/client pytest6pass2PG-not-configured skips8.76s, Ruff passed. New Android
profile tests initially failed with missing types; new web invariants4failed.
Configured PG test DB unavailable; stopped incomplete PG run/recorded browser
startup timeout, then used owned PG18.6/55421 ada_phase2_test. Focused backend
35pass1SQLite-lock skip70.28s; security55pass1SQLite-lock skip78.01s, matching PG
variants ran. Existing Starlette/httpx warning. Not a full backend-suite rerun.

Final Android231units0fail0skip; validation lint/debug/instrumentation/unsigned
release build26s128tasks24executed (earlier full builds74/32/49s). Owned read-only
API37 emulator: profiles/recreation/import1pass8.765s, final profiles/DNS2pass
12.654s, standard platform rejection of laboratory CA/hostname. Host Caddy2.11.7
both layouts passed actual ADA auth/role/ownership/built SPA/six SSE events/cursor/
completed replay, root/host/expiry negatives and stopped-upstream availability;
old Phase20 two-SSE proxy regression passed. Only per-process CA trust/fake model.
Web64units7files8s; pinned contracts/types/lint/build and actual PG-backed built
Chromium6pass24s (keyboard/contrast/zoom/auth/revocation/cleanup). Initial five
browser failures exposed missing Vite health forwarding, then full run passed.
Fresh install/final artifacts/docs/protected-file/cleanup checks follow below.

Failures retained: two emulator recovery runs passed four force-stop stages but
failed SecurityUI deletion waits. Test now waits for confirmation acknowledgement
before owned GET polling and explicit Refresh, emitting safe status diagnostics.
Third full run passed four stages and SecurityUI8.767s; a repeated run failed
voice-draft resume line39. G-41 remains Open; successful reruns do not establish a
production fix. Additional implementation/fixture corrections (Compose context/
nested synchronization, host allowlist, dropped web public flag, wrong DTO,
PowerShell dotted Gradle property) and proxy harness wrong-SNI/header handling are
recorded in STATUS. Corrected actual template Host matching rather than hiding it
in the lab. Logs remain ignored under .pytest_cache/phase21; no secrets/private
transcripts or credential hashes in committed records.

Skipped/remaining target verification: actual Serve daemon/ACLs/VPN revoked route,
real LAN firewall/DNS/system-trusted release TLS, certificate renewal, physical
Wi-Fi/handover, manual assistive review and sustained load. TLS lab is not remote
deployment; emulator negative TLS is not positive release/system trust. G-06/
G-29 target parts and G-41 remain. No always-on, password, research, curiosity or
later phase. Cleanup/final checks follow; stop at21 with these limits.

Phase21 closeout: normal application-ID units/lint/debug/unsigned-release build
passed28s101tasks44executed,231units0fail0skip. Fresh npmci270installed/271audited/
0findings plus contracts/typecheck/lint/64units8.17s/build passed, with the existing
whatwg-encoding deprecation and no lock upgrade. Final direct TLS+emulator and
tailnet-boundary laboratories passed, including stopped-upstream checks; only
test-process CA trust and negative Android TLS evidence, no real Serve installation.

Documentation UTF-8/224local links across17changed/new Markdown files and13guide
PowerShell AST examples passed.199protected paths unchanged, including server
Python/released migrations/contracts/prompts/locks and phase19/20/22–31 plans;
524of551initial tracked paths unchanged outside27intended edits. Exact source/
exported OpenAPI equality96paths132schemas, Ruff lint/format161files and whitespace
passed; existing CRLF conversion notices informational. Logs/receipts remain
ignored under .pytest_cache/phase21, with metadata only in committed records.

Stopped exact owned PG18cluster/data path55421; uninstalled only own Phase21
validation apps and stopped read-only emulator5584. Runner cleaned its separate
physical-named test app/reverse19821. No own19621–24/19631–34/19821/55421/18420/
19420/18763/5173 listeners or device remained. Harnesses removed their temporary
SQLite/CA keys. No normal app/phone, live service/.env/DB, Docker, trust store,
firewall/DNS/VPN or real credentials/grants touched. Preserve mixed recovery
evidence and open G-41; next eligible feature is separately selected Phase22,
not automatic continuation. Stop at21, without deployment or commit.

### 2026-10-16 — Phase22 password/session implementation — fed5d4b + preserved Phase21 tree

Scope: selected22only. Read required rules/architecture/plans, current auth/OpenAPI,
migrations, owner/erasure/recovery and both clients/tests before writing. Initial
559file snapshot preserves prior Phase21 changes. No live migration/password/grant,
deployment, real account operation, external message or later phase.

Changed behavior/files: new login_models/passwords/login_api plus migration0016;
existing security gate/dependencies authenticate legacy/device/session credentials
and fence every stream batch. Exact pre-auth routes have body/time/rate/hash
admission. Distinct normalized operator-assigned login, pinned bounded Argon2id,
generic/dummy verification, digest-only rotating families, owner-locked reuse/reset,
expiry/revoke/current-all logout and current-password change. Refresh delivery loss
recovers by password sign-in. Auth metadata remains available during erasure;
launcher ignores forwarding headers. CLI hidden enrollment and safe credential
metadata keep admin grants and legacy/device policies separate.

Android15/0.22.0-sessions adds password mode, refresh-only v12 Keystore persistence,
memory access, owner/epoch-verified GET-only reopen/renewal and password/session
Settings. Advanced bearer/v1–v11 recovery remains compatible. Browser adds HTTPS
host-only HttpOnly/Secure/Strict cookies, exact Origin/header CSRF, serialized auth,
short-lifetime renewal, current/all sign-out/password change and cross-tab owner
response fencing before decoding. No private POST replay or JS token storage.
Scoped instructions/standards/UI spec now describe the selected cookie extension.

Data/API/prompt changes:0016/57tables; backupv2 with restored password/session
quarantine and frozen0015/v1/0005 compatibility; retained security inventory disclosed
in erasure previews. Contract105paths/138schemas; old132schemas/96paths unchanged
apart from additive cookie-security alternatives. Prompt/evidence/request/replay
history and released migrations/other phase/native trust files remain unchanged.
New password/session guide covers installation, hidden prompts, normal client use,
limits, revocation, encrypted recovery and troubleshooting; README/architecture/
current state/roadmap/gap/status/decisions/sources updated without rewriting prior
validation as a new run.

Checks actually completed: baseline33passed31skipped28.48s; focused81passed2skipped
153.67s; expanded password/old0015recovery24passed1skipped39.11s; security/stream/HTTP
107passed3skipped197.03s; later auth/contract61passed3skipped94.03s and corrected
failure cases4passed13s. Skips here are SQLite row locks, with PG18variants run.
Native matching-major encrypted recovery preserves completed replay and erasure
ledger, nulls recovered password authority and revokes families. Argon2 five
hash+verify samples median114.76ms, range112.79–117.14;2slots/64MiB each, no sustained
or peak-RSS claim. pip check/Ruff168files passed.

Intermediate full pytest777passed25skipped3failed1182.24s is preserved. Two failures
were old bearer-only OpenAPI expectations; one SQLite HTTP chat503 did not recur
in focused SQLite/PG checks. Fixed the fixture's inherited background-worker
mismatch, without claiming a product reliability fix. Final full818case/57module
collection ran in3independent disposable-data groups; exact closeout below.

Android final236units/0fail/0skip, lint/debug/instrumentation/unsigned-release
build42s/240tasks25executed; isolated API37 emulator password UI/Keystore/explicit
renewal13.019s then actual force-stop/reopen/revoke5.655s passed. Runner verifies
separate APK IDs, accepts emulators only, and cleans validation packages/reverse.
Earlier false recreation-rotation expectation and empty-field label assertion
failed, then were corrected; G-41 is not inferred fixed. Initial journal version/
fake/logout/import failures were resolved before final builds.

Fresh npm ci270installed/271audited/0findings;67units7.61s plus contracts/types/lint/
build. Final production PG18 Chromium6passed33.6s. Real Caddy TLS browser passes
password/cookie/CSRF, automatic renewal/reopen/logout, non-admin denial, two-tab
owner fencing and password change. Public-ready transport receiver and legacy/
message assertions were corrected after failed checks. No credentialed recording;
ephemeral leaf pin is per-browser-process only. Both Phase21 TLS/SSE routing
laboratories passed again.19docs/222links and3PowerShell examples parsed without
execution; contract/protected-file/whitespace checks passed.

Windows/PostgreSQL evidence: owned PG18.6 loopback55421 and dedicated disposable
schemas/databases only; old native5432 and application5433 unchanged. Initial
PG launch without its port override failed, then corrected. No Docker/live repair.
Final grouped verification/owned-service cleanup appended when complete.

Skipped/remaining: no application0016installation, real password enrollment or
browser-origin configuration; no physical S24FE/Android16, positive trusted release
HTTPS, real network/VPN/firewall/DNS/renewal, manual password-manager/assistive,
other-browser, sustained authentication/peak-memory or real-model evaluation.
Opt-in Ollama/long-model checks remain skipped. G-06/G-29 and G-41 remain open.
Next eligible work requires a separately selected phase; implementation stops at22.


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


### 2026-10-16 — authorized private Windows/Tailscale setup — fed5d4b + worktree
Scope: user-selected environment setup and repeatable guide after Phase22; local
private operation explicitly authorized. Preserve all pre-existing uncommitted
Phase21/22 work. No Phase23+ or unattended Phase26 service.
Changed behavior/files: ignored dotenv corrected/synchronized, address reference
metadata added and private ACL applied; exposed DB role credential rotated with
unchanged57table inventories and same-volume Compose recreation. Pinned Caddy
manual install/start/check helpers and executable hash; detailed Windows/Tailscale
runbook and entry links. Fixed missing login_models import in migrations/env.py
only after a fresh-process regression reproduced the operator check failure.
Data/API/prompt changes: live database was already0016/57tables; no reset/migration,
released migration edit, API/export change or prompt change. All existing owner
IDs, account legacy/device credentials and admin grants retained. Exact synthetic
validation owners/password/session rows removed; security audit metadata retained.
Checks actually run and results: affected SQLite/real disposable PG17 password/
fresh-process Alembic29passed1expectedSQLite-row-lockskip33.43s; fixture DB cleaned.
Live0016/check/doctor/pipcheck pass. Web contracts/types/build/lint and70units8files
7.56s pass. Actual Serve/system-trusted TLS1.3 route: readiness/admin200, private401,
root404; Chromium built password form/non-admin denial; HTTP browser cookie/CSRF/
rotation/logout/owner and native password rotation/old-access rejection/logout
pass. All temporary auth fixtures cleaned. Ruff245files/format/Gitwhitespace,
2helper AST checks, validCaddyconfig/invalidarchive refusal and21guidePowerShell
syntax examples/5local links pass. Optional guide commands were not all executed.
Checks skipped/blocked and reason: full backend/Android suites already ran for22
and were not rerun for this bounded helper/docs/metadata fix. No new inference,
physical voice/release-HTTPS/reopen/chat/cellular/SSE/iPadSafari/manual-accessibility/
renewal/load evidence, live encrypted backup or restore. Native18 backup clients
still mismatch live17. Earlier no-deployment test records remain historical.
Windows/PostgreSQL/device/model evidence: existing DockerPG17.11 loopback5433;
API8000/Caddy18764/Ollama11434 loopback, Tailscale443 private only/noAllowFunnel.
Existing S24FE Android16/version15 app and Tailscale Android/iPad online observed;
model listed, no new generation. Background launcher receipt/log paths in guide.
Corrected failures: read-only fsync staging rolled back before writable retry;
initial PS5 module lookup/HTTPS502 corrected by PS7 launcher; synthetic missing-
Content-Type415 corrected to valid-JSON CSRF403. Initial owner password too short
was rejected; hidden local enrollment retry opened, secret never captured.
Remaining issues: confirm retry enrollment plus real owner browser/phone checks;
retain physical/release/reliability and backup gates. Results will be appended.
Next eligible checkpoint: finish user-entered enrollment/client verification for
this setup. Later feature phases still require explicit selection.


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


### 2026-10-16 — Phase23 A–E — base fed5d4b plus existing working tree

Scope: only answer quality/memory relevance, preserving the pre-existing
Phase21/22/setup edits. Read root/plans/Android rules, requested phase, current
README/architecture/state/standards/workflow/status/roadmap and OpenAPI/source/test
baseline first. Existing0016/private memory/episodes/review/session adapters meet
prerequisites; no later dependency was implemented or live service deployed.

Changed behavior/files: temporal.py/quality_api.py add owner-only explicit calendar
resolution/whole-window claim lookup and request-frozen context diagnostics.
quality_context.py/service.py/learning.py rank original same-chat history and
already-authorized continuity for explicit v5. personality.py preserves old v3/v4
bytes/defaults and adds v5; existing PromptChange/revision/replay fences remain.
Android app16/0.23.0-quality adds interval/source/correction and explicit upgrade
controls, exact loaded-proposal grouping/conflict cues and typed API capabilities.
No automatic save/extraction/review approval or new background work.

Data/API/prompt changes: head0016, no migration/dependency/storage table. Four
additive paths/five schemas;105old paths/137non-capability schemas compared equal,
three additive capability properties. New chats remainv4; v5 opt-in. Windowv1 is
valid-time overlap/current recorded state, claim-only; old point/--at behavior
unchanged. V5 history50/continuity20 candidate bounds and exact source spans remain
under the whole prompt budget. Old completed replay and failed-revision fences
are tested. Sixty-eight protected files and old prompt bytes match turn start.

Checks actually run and results: initial relevant baseline82passed/4SQLite skips;
affected retrieval/learning/storage/baseline61passed/2skips; expanded Phase23
17passed; three later corpus/path/CRLF/emulator-package guards3passed. Full-suite
result/skip breakdown and disposable PostgreSQL closeout are appended below.
Ruff lint and final format177files passed; pip check passed; alembic heads0016.
OpenAPI exported/types regenerated; web typecheck/lint70unit tests/production build
passed. Android239unit tests, lintDebug, debug/instrumentation/unsigned release
builds passed. Separate API37 emulator real HTTP/PG/session flow1passed (11.002s):
interval/Unicode conflicting cards/exact source/explicit v5/document opt-in.
Validation app/reverse/schema removed, emulator stopped, normal APKs rebuilt;
no phone/normal app install/reset. UTF-8/local-link/PowerShell example/whitespace
checks passed; final documentation count follows at closeout.

Development failures preserved: missing new routes failed before implementation;
a test-only evidence field path and later pytest import were corrected. Android
serializer-name compile error corrected. First emulator install raced boot,
cleaned fixture and passed after boot completion. Initial two-recent-pair fixture
ranking still omitted old relevant history; one-recent-pair policy fixed that
before final native run. Ruff found one signature-format change and passed after
formatting. Initial policy-digest probe used assembled prompts rather than the
recorded policy-only bytes; the documented definition matches final source.

Windows/PostgreSQL/device/model evidence: owned PostgreSQL18.6 on55421/dedicated
ada_phase2_test plus migrated SQLite; original app PostgreSQL17/runtime untouched.
Pinned Windows Python3.12/JDK21/SDK37. Public corpus frozen8development+8regression
holdout, SHA256 in manifest; initial SQLite fixture32outputs, final PG fixture32,
native installed qwen3.8:27b32. Model digest aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813
confirmed before/after. No raw private data, credentials or quotes recorded here.

Measured decision: both policies recall1.0 (5positive development/4holdout),
MRR0.9/1.0; zero detected owner/project/deleted-source/exact-span failures. Codex
qualitative review of actual32answers is not independent human validation.
Fully useful developmentv4/v5=8/8→6/8, holdout5/8→8/8; intervals overlap and output
samples are single-run. V5 supplies the relevant old original turn but date-boundary
wording/brevity regressions remain. Medians4.272→4.716s development/3.482→3.922s
holdout, first cold55.55s and uncontrolled validation load: no SLA/general factual
accuracy claim. Keep v4 default, v5 explicit. Existing13query hybrid fixture shows
lexical recall0.4286 vs hybrid1.0 but synthetic vectors are not native evidence.
Supported embeddinggemma digest absent: no download, semantic remains disabled.

Checks skipped/blocked and reason: native embedding/index/GPU/working-set benefit
unmeasured without matching installed weights; private evaluation not opted in.
Independent larger/new-corpus review/repeated warm performance, native date/brevity
and lexical noise cases remain. No new Chromium runtime tests for type-only web
change. Physical S24FE/TalkBack/large-font/signed-release HTTPS/network handover,
voice/G-41 and live recovery/soak are not closed by this phase. Claim-only intervals
do not add chat interval options or document/historical-alias interpretation.

Remaining issues and next eligible checkpoint: details/commands in
[the quality guide](../docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md),
[frozen manifest](../evaluations/answer-quality-manifest-v1.json) and
[reviewed results](../evaluations/answer-quality-results-v1.json). Phase23 exits
with explicit opt-in/disabled decisions. Stop here; Phase24–31 remain planned.
No deployment, live migration, model download or automatic activation.


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

## 2026-10-17 America/Phoenix — Phase24 secure web research

User scope: only phase-24-secure-web-research; inspect source/OpenAPI/tests first,
preserve contracts, record actual checks/skips and stop without deployment. Started
clean at9e06312, recorded594file hashes/109paths/143schemas; read root/scoped rules
and required architecture/state/standards/workflow/status/roadmap/phase. Existing
approval/receipt, erasure/recovery and readiness prerequisites met independent
implementation needs. Baseline105passed/2expectedSQLite-lock skips156.72s on
SQLite/nativePG18.6; new missing-route failure-first1failed/1passed/2deselected.

Implemented a default-off actual isolated Linux Docker egress broker: three-file
secret-free digest/snapshot-pinned image, local daemon only, source-bound manifest,
default-drop firewall, post-setup UID65534/capability drop/seccomp/read-only, no
mounts/application env/proxies/socket. Validate all DNS addresses, pin publicIPv4
socket/TLS hostname and actual peer. No arbitrary sites, IPv6 transport, JS,
subresources, cookies, authenticated browsing or external writes. Python `/3/`
docs and English Wikipedia main pages only; no-key Wikimedia REST search after
primary terms/rate/privacy/User-Agent review. Owner-authorized public contact is
only in ignored local configuration and Wikipedia's exact outgoing-header preview.

New owner research protocol reserves exact preview/nonce before any fetch and
requires new matching unexpired authority for every call. Three total calls,
zero automatic redirects,1MiB identity-only body,32768codepoint extraction with
truncation flag,15s network I/O plus bounded DNS/setup, two slots/10starts per
minute. Network/model I/O outside transactions; cancellation/epoch/revocation/
lease/generation fences and unknown/no-auto-retry. Immutable untrusted W sources
with saved hash/spans/URL/time/parser/terms, snippets distinct, local answer with
shared admission and no-refetch completed replay. Explicit save creates imported
untrusted note, never personal factual memory. No automatic private context export.

Reused existing AgentRun/Step/Approval/Receipt inventory with separate protocol;
old agent routes reject it. Head0016/57tables unchanged; existing45content-table
erasure/encrypted recovery covers full private URL/query/source receipts. Added
8path templates/9methods/13schemas,117paths/156schemas total. All109old paths and
142non-capability schema definitions unchanged; optional web capabilities defaulting to `disabled`
only. Old prompts/chat/replay/citation contracts, migrations, dependency locks,
wrappers, release TLS and later-phase plans unchanged.

Android17/0.24.0-research implements real API preview/confirmation/receipt/snippet/
next-call/source/local-answer/note/cancel UI and encrypted v13 exact journal,
v1–v12 reads, identity/server/scope/epoch fences, storage-before-POST and GET-only
reopen. Independent UTF-8 hash/Unicode quote validation. Admin retains aggregate
metadata only; generated web types refreshed. Detailed setup/usage/boundaries in
[SECURE-WEB-RESEARCH](../docs/SECURE-WEB-RESEARCH.md), with current-state/architecture/
contract/roadmap/checkpoint/decision/reference records updated.

Actual checks: final affected SQLite/PG/contract/recovery70passed/1expectedSQLite
row-lock skip58.26s; peer/SNI/no-second-DNS1passed/37deselected separately. New
redacted-invalid-contact configuration test is included in fresh full rerun below.
Tests include actual PG concurrent single-fetch approval, revoke/cancel/unknown/
crash/expiry, owner/protocol boundaries, hostile URL/IP/MIME/HTML/compression,
source integrity/trust, capacity and no transaction across network/model, actual
erasure and populated encrypted native-PG restore/replay/credential quarantine.

Docker29.8.2 Linux: startup9/9denied, independent reachable private-canary positive
control followed by10/10restricted denials. UID65534/caps0/seccomp/read-only/noenv/
nohostfiles proof passed. Final image35a12c82880775b20d8f0fd9d022e2215e45e2e6f05ee2c237f544edecb70898.
Corrected public pilotPython15139codepoints/Wikipedia3snippets completed with no
truncation. Native integrated public API/PG/Docker/qwen3.8:27b answer/source/replay
passed; model digest aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813.
Exact source verified, answer hadIANA/W1, warnings empty, completed replay equal.
Its image6542306808d8fc02caffcdde1daaa2c1398e5b9002b44faacbb0441f7a4b3fab
predates final disclosure-copy rebuild; final image isolation tested separately.
One native public marker-checked sample is not general accuracy/entailment or
prompt-injection immunity. No model download/private evaluation was performed.

Android244unit tests and lint/debug/instrumentation/unsigned release builds passed;
normal APK rebuilt again after final deadline-copy change. Separate API37 emulator
real HTTP/PG fixture with explicit synthetic broker/model: approval/source/answer
stage7.489s and actual force-stop→restore/GET-only stage3.691s,2passed. Runner
removed validation APK/reverse/schema. No physical device/normal app install/reset.
Web typecheck/lint70units/8files/production build and finalcontracts:check passed.
No new Chromium run for generated-type-only web change. Ruff lint/format191files,
pip check and normal repository-configured git diff --check passed. Metadata and
service/emulator cleanup verification are appended at final closeout.

Earlier corrected failures retained:8failed/36passed from incorrect Conversation
key lookup fixed to owner-filtered select;20setup errors/36passed from transient
missing import;2failed/54passed from wrong test-only deletion-preview route.
Corrected targets59passed/1skip. Android positional capability constructor compile
failure fixed by appending default fields. Cancel test coroutine scheduling and
emulator exact-text assertion corrected; both force-stop stages then passed.
Ruff signature/noqa issues fixed and fresh checks passed.

Privacy incident/correction: first public pilot sent configured operator contact
to Python docs as well as Wikipedia. Reported to user; corrected recipient-specific
preview/header selection and independent worker before-connect rejection. Added
negative tests and reran actual corrected public fetch/search successfully. No
contact value, private source quotes or credentials are recorded in repository
plans/logs. The user-authorized contact remains only in ignored configuration.

Initial broad suite collected during evolving export/header changes returned
872passed/6failed/26skipped1124.10s:2stale-export contract failures and4old-collected
header fixture failures against updated worker guard. Fresh contract5passed and
affected70passed/1skip, followed by frozen-source full rerun, actual result below.
The failed invocation is not rewritten as a passing run.

Environment: owned nativePG18.6 loopback55421/ada_phase2_test, WindowsPython3.12,
JDK21/SDK37, ownedAPI37emulator5584, DockerDesktopLinux29.8.2 and existing native
Ollama/qwen. App PostgreSQL17/private API/Tailscale route, accounts, normal APK and
phone untouched. Local contact setting added as authorized, feature still disabled;
no service activation/migration/deployment, search purchase or later phase.

Skips/remaining: full-suite skip breakdown follows. PhysicalS24FE/Android16,
TalkBack/large-font/signedHTTPS/handover, broader hostile-source/native quality,
resources/daemon-failure/soak and earlier voice/G-41 remain. Reverify isolation on
installation host before explicit activation. No live backup/restore/erasure or
private dataset run; disposable native recovery is separate evidence. Phase25–31
stay planned. This session stops at Phase24.

Final adapter audit found a blocking Docker stdout read that could outlive the
removal timer. Failure-first1failed/39deselected; fixed host CLI communicate to
23s deadline plus bounded best-effort removal/termination. Unknown remains unknown
and cleanup failure cannot skip CLI kill; no retry. Worker/policy/image unchanged.
Fresh policy40passed0.10s; fresh affected policy/research/PGrestore/contracts
**73passed/1expectedSQLite-lock skip53.99s**. Repeated actual private-canary/isolation
and corrected public Python15139codepoints/Wikipedia3snippets passed on final
image/adapter. The ongoing broad run imported the earlier adapter and excludes
the last test; full-run provenance below remains separate from final affected
evidence. Public contact appeared in a transient ignored failure log, was redacted
and artifact scan rerun; no configured DB password was found. Final configuration
validation hides input values in errors. Owned emulator5584 stopped; no separate
validation APK/reverse or fixture18423 listener remained.

Provenance audit: added unfinished-run provider/model drift rejection, preserving
original completed replay after configuration changes. Failure-first2SQLite
failed/2PGskipped/26deselected without a PG URL. Fresh final combined policy/
research/native recovery/contracts **77passed/1expectedSQLite-lock skip57.57s**
with nativePG18 configured; all four drift cases and the stalled-Docker test ran.
These five final cases/guards postdate collection/imports in the broad run below;
do not combine their counts into a fictitious full-suite invocation.

Broad rerun completed: **886passed/26skipped1082.68s (18m02s),912cases** on migrated
SQLite/disposable nativePG18.6. Skips:18SQLite locking cases with PG counterparts
executed,2opt-in non-generating Ollama health probes and6opt-in legacy native-agent
probes (not enabled). Existing Starlette/httpx TestClient warning remains. The
public native research sample is separate evidence, not those opt-in probes.
Final host/provider guards and later proof tests remain separately verified;
earlier failed broad invocation is preserved, not relabelled.

Strengthened read-only proof before closeout: `/broker` directory permissions
could produce a false positive. Require EROFS from world-writable `/tmp` instead
of accepting arbitrary write errors. Failure-first2failed/40deselected, fresh
policy42passed0.11s. Rebuilt final image
d494abd80498712e64dcdfeb6fd4560751ab2d4ff5526552d7d6227b4a3f725a,
then actual startup9/9denied/private-canary positive control→10/10denied plus
UID/caps0/seccomp/EROFS/noenv/nohostfiles passed. Corrected public Python15139
codepoints and Wikipedia3snippets passed again with no truncation. Existing native
answer report retains older image provenance; no model rerun is claimed for a
self-test-only worker change. These two cases postdate broad collection. Final
combined affected result and cleanup follow.

Phase24 final closeout: final policy/research/nativePG recovery/contracts
**79passed/1expectedSQLite-lock skip49.00s**, including all7post-broad-collection
cases (Docker deadline1/provider drift4/EROFS2). Broad886passed/26skipped remains
its actual earlier invocation. Ruff lint/format191files, pip check, web contract
freshness and normal Git whitespace passed. Protected139files and all109old paths/
142non-capability schemas unchanged;51changed/new repository files scanned for
configured credentials/contact with zero matches. Thirteen UTF-8 docs/205local
links and10PowerShell blocks checked. Final manifest source hashes/current image
and Windows POSIX path serialization verified. Ignored artifacts scanned after
contact-log redaction; no configured credential/contact matches remain.

Cleanup:10empty schemas from initial setup errors verified under owned fixture
role in isolated55421/ada_phase2_test, with zero relations/routines/types; dropped
only those namespaces using RESTRICT. Final all-non-system schema/restore/recovery
database inventories empty. Owned nativePG55421 stopped after resolved workspace
datadir/loopback port check. Owned emulator5584 stopped; separate APK/reverse,
fixture18423 listener and broker containers absent. Normal debug APK metadata is
dev.ada.assistant.debug/app17/0.24.0-research, rebuilt without installation. Docker
engine/unrelated containers/native Ollama/private API/proxy and app DB untouched.
Ignored local feature config freshly checked: disabled, manifest unset, approved
public contact present. No live backup/erasure/migration, activation/deployment or
later phase. Phase24 bounded local exit complete; documented physical/host/quality/
soak/voice/G-41 limits remain open.

### 2026-10-17 — Phase25 A–E — HEAD9e06312 + working tree

Scope: only conversational curiosity. Read AGENTS/README/architecture/current
state/standards/workflow/status/roadmap/plans README, single requested plan,
Android rules, current source/OpenAPI/migrations/tests. Captured615-file filesystem
baseline including uncommitted Phase24, not only GitHEAD. Existing explicit review,
settings/continuity/relevance prerequisites present; physical/reliability gates
remain inherited limits. No subagents, new dependency/model, live DB operation,
deployment, external message or later-phase implementation.

Changed behavior/files: new `curiosity.py`, typed API/contracts/models, Android
controller/settings/inbox/chat cards and encrypted journalv14 queue; exact policy/
question/action/open/answer recovery. Default-off five-topic controls, bounded
cadence/quota, generic/exact-original catalogue, uncertain source premises and
inspectable original spans. Actual answer precedes an optional companion. Opening
creates no user event. Typed answers remain ordinary owner chat with existing
trust; claims/preferences still require explicit review/settings. No hidden
relationship/psychological inference, timers, push or memory extraction. Global
off has reserved client/server capacity even after ordinary-write quotas.

Data/API/prompt changes: additive0017 (60tables/48owner-content), new explicit
backup-v3 retaining0015/v1 and0016/v2 compatibility. Restore verifies counts then
disables curiosity/requires fresh opt-in and quarantines credentials. Lower
released downgrade preflight copied into new0017 before any SQLite DDL; old
migration files preserved. Optional versioned budget-bound navigation context;
historical prompt versions/request snapshots/fingerprints/replay unchanged.
Nine new paths/eleven methods/twelve schemas;126paths/168schemas. Existing117paths/
155non-capability schemas preserved; two additive capabilities. Journalv14 reads
v1–v13. Android18/0.25.0-curiosity; wrappers/dependencies unchanged. Guides, roadmap,
current state, decisions, phase checkpoint evidence and generated contracts updated.

Checks actually run and results (each count is its own invocation):

- Relevant baseline expression/learning/storage/quality/recovery/contracts:
  89passed/3expected SQLite-lock skips133.11s, SQLite/nativePG18.6.
- Failure-first missing endpoint:1failed/1PG-not-configured skip/14deselected.
  Initial implementation16passed17.77s. Epoch/context/crash reconciliation:
  2failed/2PG-not-configured skips/16deselected before fixes. Existing-primary-
  question suppression1failed/1PG-not-configured skip/26deselected before fix.
- Native restore consent1failed/7deselected5.17s, fixed by post-verification
  opt-out. Expanded affected run102passed/3failed/2skipped198.11s: two deferred-
  clock tests anchored to creation instead of action time (fixed clock fixture),
  one old expected lower downgrade error (copied preflight into new0017/updated
  current-head expectation). Fresh affected105passed/2expected skips187.17s.
- Full pytest930passed/27skipped1283.97s,957cases; existing TestClient warning.
  Nineteen SQLite-lock skips have executed PG counterparts;2opt-in non-generating
  health/6opt-in legacy native-agent probes not enabled. This is not a claim that
  twelve subsequently added failure cases were present in that full collection.
- Reserved server-off capacity failure-first1failed/1PG-not-configured skip/
  30deselected; configurable reviewed cap/final off slot fixed. Fresh quota/
  failed-answer retry/provider-outside-transaction/revocation target43passed/
  1SQLite-lock skip71.20s. Pre-admission UTF-8 budget rejection and concurrent
  request-ID collision failure-first2failed/2PG-not-configured skips/36deselected.
  Fixed durable rejection/state rollback, exact conversation/content fingerprint
  binding and client receipt lookup before clearing answer intents. Final two
  modules47passed/1expected SQLite quota-lock skip99.55s, with PG enabled.
- Android builds/unit/lint ran repeatedly as behavior changed: initial244units,
  then249/250/251/252/253. Final254unit tests, lint/debug/androidTest/unsigned
  release passed. Failure-first reserved journal off slot and quota cooldown
  selected tests failed before their guards. Oversized Unicode answer selected
  test failed before friendly4000-codepoint validation; final test now passes
  without persistence/POST/exception. Client4xx recovery keeps unknown/failed
  exact intent, clears only durable rejection/completion, prevents second UUID.
- Separate emulator build initially rejected because PowerShell split an unquoted
  Gradle property; fixed by quoting the whole `-PadaValidationApplicationId=...`
  argument. First HTTP test used deliberately unavailable browser-provider fixture;
  added explicit curiosity-only FakeProvider flag in disposable fixture. Default
  production/provider behavior unchanged. Next two attempts exposed answer/
  question refresh timing (one stale assertion, one20s timeout). Added safe
  metadata-only timeout diagnostics and stronger existing timeout condition.
  Two complete force-stop passes:9.460s/4.585s and8.765s/4.935s. Following answer
  receipt fix fresh stages8.167s/4.103s. Final post-size-guard stages6.809s/3.107s
  passed. Each uses actual HTTP/nativePG/password/Keystore, separate validation
  package and real force-stop; lost acknowledgement simulated by retaining exact
  encrypted action after real write. Startup GET receipt checks caused no
  duplicate user event or POST. Passes do not prove G-41 reliability.
- Public frozen6development+3holdout corpus passed twice with native mode. Fresh
  final report includes one installed loopback qwen3.8:27b answer/replay, digest
  aaee06c39dcf2437cde036998d960e1fc1494b8191be7cc9657d01e509097813.
  Corpus SHA256e4f43bfe09a2ae4e67c3c305a48074f96ffe5727916697fa5b599b48290bc745.
  Codex reviewed public sample: on-topic single question, no invented private
  premise. Topic/source/dedup assertions and synthetic accepted/skipped/helpful
  counts are not independent relevance/entailment or actual owner helpfulness.
  Temporary SQLite only; no private corpus, application data or web research.
- Web contract generation/freshness/typecheck/lint,70unit tests/8files and build
  passed. Runtime Chromium suite not repeated: only generated contract/capability
  changes, no curiosity web UI. Ruff lint/format200files, pip check and normal Git
  whitespace passed; normal LF/CRLF conversion notices are not test failures.

Windows/PostgreSQL/device/model evidence: Python3.12.10/Ruff0.16.10,
JDK21.0.12, nativePG18.6 loopback55421/dedicated ada_phase2_test, owned API37
Medium_Phone_API_37.0 emulator5584. No physical S24FE, normal app install, signed
HTTPS/handover, accessibility or audio test. New native backup/downgrade/erasure
tests ran only disposable schema/database fixtures. Current `.env` untouched.
Research remains disabled/manifest unset; Phase24 egress worker/policy preserved.

Remaining issues: separate authorized installation0017/app18; physical Android16,
TalkBack/large font, signed HTTPS/network handover, longer performance/soak,
independent premise/relevance/naturalness review with actual owner feedback;
inherited voice and G-41 limits. Final audit/cleanup record follows.
Next eligible checkpoint: select later work explicitly; Phase26–31 remain planned.

Phase25 final closeout: final emulator6.809s/3.107s passed after last input guard;
normal debug/instrumentation APKs rebuilt (dev.ada.assistant.debug/version18/
0.25.0-curiosity), no installation. Unit XML254tests/0errors/0failures/0skips.
Comparison against615pre-phase files:56changed/new, no deletions.39reviewed
protected files unchanged, including released migrations0001–0016, old prompts,
dependency locks/wrappers, later-phase plans and Phase24 broker/research source.
Audit helper initially named Capabilities instead of CapabilitiesOutput; corrected
the helper's schema key, then exact comparison passed117old paths/155old non-cap
schemas plus only two additive capability properties.15UTF-8 docs/263local links
and69PowerShell blocks checked. Configured credentials/contact scan across changed
repository files and ignored Phase25 artifacts had zero matches. Final Ruff/
whitespace/contract freshness passed; no changes to `.env` or dependency versions.

Owned testPG55421 inventory: no fixture schemas, public0relations and no restore/
recovery fixture databases (only postgres/ada_phase2_test). Cleanup version probe
first had a harmless executable-path typo/no action; corrected path, reverified
resolved workspace datadir and127.0.0.1:55421 options, then stopped only ownedPG.
Final55421/18423 listeners absent. Validation APKs/reverse absent before owned
emulator5584 stop; ADB inventory empty afterwards. No normal app/physical-device
installation or live migration/backup/erase/restore. Docker/unrelated services,
native Ollama/private API/proxy and application DB untouched. Bounded local exit
complete; all recorded physical/host/quality/soak/voice/G-41 gates remain open.

Phase25 last crash-edge review: added a simulated process-stop case after a
conflicting ordinary Request commits but before rejection bookkeeping. Failure-
first1failed/1PG-not-configured skip/40deselected1.31s: GET returned a terminal
rejection without reopening the question. Changed only derived receipt read state
to reconcile_required; explicit exact replay durably rejects/reopens, without
adopting unrelated text or regenerating. Fresh full curiosity/storage target
**49passed/1expected SQLite quota-lock skip74.05s**, including all twelve cases
added after full957-case collection. Restarted only ownedPG55421 for this run;
schema/database inventory and verified stop repeated below. Android254units/
emulator and public native sample remain their actual prior invocations: no
client/schema/prompt/inference behavior changed by this edge-state fix.

Final re-inventory again showed only public0relations/no fixture schemas and
postgres/ada_phase2_test/no restore databases. Verified owned datadir/options and
stopped nativePG55421;55421/18423 listeners absent. Final protected-file/contract/
configured-secret/UTF-8/link audit and Ruff200files/whitespace passed again. No
later phase, normal app install, live data operation or deployment.

### 2026-10-17 — private proxy launcher — HEAD844d560 + working tree

Scope: fix only the reported PowerShell/Python quoting failure. Read root rules,
README/architecture, current schema/test state and launcher/proxy configuration.
Windows PowerShell5.1 `-CheckOnly` reproduced the unterminated Python string before
the fix. Changed the existing reader invocation to stdin (`python -`) so embedded
quotes survive legacy argument passing; dotenv remains parsed without evaluation.
Both Windows PowerShell5.1 and PowerShell7.6.6 CheckOnly passed with actual pinned
Caddy/config/built-admin path. Nonblocking Caddy formatting warning unchanged.
Pytest `tests/test_schema_contract.py`:3passed0.98s, existing TestClient warning;
Ruff lint/format200files and Git whitespace passed. No persistent new tests needed
for the small invocation fix; actual Windows reproducer validated directly.
Full pytest/nativePG/Android/web suites skipped: no backend/schema/client change.
No proxy launch, deployment, credential/config edit or database operation.

### 2026-10-18 — Android UI redesign — HEAD844d560 + working tree

Scope: only plans/ADA-Android-UI-Redesign.md. Read root/Android/plans rules,
README/architecture/current state/standards/workflow/status, requested full plan,
actual source/SDK/dependencies/navigation/voice/insets/OpenAPI/test state first.
633-file snapshot includes the prior uncommitted proxy fix and requested plan;
preserved those changes. Audit/design/screen plan/file map communicated before
broad rollout and recorded in docs/ANDROID-UI-REDESIGN.md. No subagents/deployment.

Changed behavior/files: Theme/Appearance, AmbientComponents, MainActivity frame,
ChatApp/VoicePanel and feature Screen headings/lifecycle collection. App19/
0.25.1-ambient, default dark violet for fresh installs, saved legacy palette/mode
keys retained. Shared typography/shape/spacing/glass/background, real state-derived
presence, quiet chat, keyboard anchoring and compact/expanded navigation. No
placeholder routes, fake production data, autonomous activity or inferred audio
amplitude. Existing controllers/ViewModels, HTTP/data/audio, auth, exact journals,
sources/approvals, APIs, migrations and dependency pins unchanged. Added focused
unit/rendered/native-HTTP tests and guarded separate-package verification runner;
existing runner's optional artifact callback leaves default behavior unchanged.

Data/API/prompt changes: none. No migration, credential/settings file edit, model
download/inference or application database operation. Phase26+ remains planned.

Checks actually run and results:

- Baseline Android254units/lint/debug/androidTest build passed14s; backend client/
  schema contracts6passed/2PG-not-set skips14.00s. Final nativePG contract rerun
 8passed32.76s; existing Starlette/httpx TestClient deprecation remains.
- New palette test initially1failed/256passed (257total), Ambient light contrast
 2.960885; corrected readable light/dark role pairings. Theme stage258units/
  lint/debug passed1m22s. Chat rollout258units/lint/debug/androidTest passed48s.
  Final all-build run258units/lint/debug/androidTest/unsigned release passed1m31s
  before last action-row placement; fresh closeout build below, not a new count
  attributed to this earlier invocation.
- First representative HTTP test timed out22.821s because new password account
  had no style. Diagnostic retry23.191s showed profile=false; collector also tried
  decoding a nonexistent image, fixed explicit existence/strict base64 handling.
  Added actual UI style creation; next24.785s showed profile=true but creation tap
  missed during IME animation. Accessibility creation run14.821s/4.671s passed.
  Wait for actual IME target/current insets, then restore touch creation. Fresh
  keyboard/creation stages13.223s/3.088s passed; later portrait17.8s/7.191s passed
  with multiline emoji input. Latest source portrait durations below.
- Visual QA caught black default ink through transparent Scaffold containers;
  fixed both explicit content colors and added a rendered TextLayoutResult contrast
  assertion. This was a real composition defect not detected by palette arithmetic.
  Root public images reviewed without weakening MainActivity FLAG_SECURE.
- First curiosity regression prepare7.669s passed, restored UI failed to locate
  open-curiosity after header virtualization. Kept capability actions pinned for
  normal heights, scrollable for short windows. Fresh actual force-stop stages
 7.795s/4.595s passed; original receipt/one user event preserved. Password renewal/
  force-stop restore/revoke7.487s/3.568s passed. Tests use native HTTP/PG/Keystore,
  an explicit FakeProvider and only a separate dev.ada.validation.redesign APK.
- MainActivity theme/control regression10.291s passed with animator scale0:
  all four palettes, stored mode/palette after recreate, status/navigation icon
  light/dark flags and FLAG_SECURE. System animator restored to prior unset value.
- Artificial landscape size override2400x1080/font1.3/three-button navigation left
  no app viewport under IME, Send not displayed (11.101s failed). Reset artificial
  size and used actual OS rotation;2400x1080/three-button/font1.3 flow passed
 13.399s, including Send after compact composer scrolling. App-surface captures
  exclude the system IME window. Expanded2560x1800/density320/font1.6 passed11.632s;
  first start overlapped build completion, so repeated after confirmed completed
  build:9.894s passed with focused-input/settled-IME assertions.
- Final selected instrumented coverage totals nine stages across six invocations,
  not a full connected suite. Earlier repeated visual passes remain separate
  provenance. No actual recognition/playback/native-model quality claim is made.
  Ruff lint/format201files and Git whitespace passed; final audits below.

Windows/device/database evidence: existing JDK21.0.12/SDK37 AVD5584, compile/target36
and min26 unchanged. Owned nativePG18.6 loopback55421/dedicated ada_phase2_test,
ephemeral UUID fixture schemas only. No physical device was connected. Public-only
test-host images retained under ignored .pytest_cache/ui-redesign/screens. Normal
app never installed/reset, release remains unsigned. Proxy fix source preserved.

Skipped/remaining: full backend and browser suites (no affected server/web code),
full connected Android suite, physical S24FE/Android16, TalkBack, physical IME/
keyboard/foldable live-resize, graphics/battery/long-scroll performance, inherited
voice/focus/G-41 reliability. These are separate target gates. Final artifact,
protected-file/secret/link checks and cleanup follow. Next work needs selection.

UI closeout: fresh normal all-unit/lint/debug/androidTest/unsigned-release build
passed1m19s. XML258tests/0failures/0errors/0skips; normal debug application ID and
version19/0.25.1-ambient verified, unsigned release exists. Latest portrait
10.570s/3.418s passed after action placement; total nine final selected stages
remain across separate runs. Screens visually reviewed for final portrait/light,
chat/source/typing and expanded1.6font settings. Captures are app surface only.

Final633-file snapshot comparison:29changed/new, no deletions;391protected files
unchanged (all backend/contracts, client data/audio/controllers/ViewModels,
migrations, locks/wrappers, later phase plans and the existing proxy fix).
OpenAPI byte-identical126paths/168schemas. Ruff lint/format201files, pip check,
normal whitespace,8UTF-8 docs/133local links and15PowerShell blocks passed.
Configured credential/contact scan of changed files and ignored non-image
validation artifacts:zero matches. No dependency or `.env` change.

Owned emulator package/reverse cleanup verified before restoring original
1080x2400/density420/font1.0/gesture/free rotation/unset animator settings and
stopping5584. Owned nativePG inventory:public0relations, no fixture schemas,
only postgres/ada_phase2_test/no restore DBs. Resolved workspace data/options
127.0.0.1:55421 verified, then stopped;55421/18423 listeners absent. Application
DB, normal Android package, private API/proxy, Docker and Ollama untouched. No
deployment or later phase. Physical/accessibility/performance/voice/G-41 limits
remain as recorded; source/local implementation complete.


### 2026-10-18 — compact Android chat — HEAD844d560 plus working tree

Scope: user's supplied UI issues and compact reference hierarchy; follow-up to
ADA-Android-UI-Redesign, preserving the existing proxy fix/first redesign.
Changed behavior/files: ChatApp compact home/header/menus/composer, in-thread
pending with persistent Stop, options/context dialogs; VoicePanel modal review;
ChatIcons vector48dp actions; relevant instrumentation and public fixture
collector/idle timeout; redesign guide. Current app19/0.25.1-ambient unchanged.
Data/API/prompt changes: none. Source trust, exact request/voice lineage, auth,
capabilities, journal formats and released migrations remain unchanged. File
shortcut opens separate scoped text/Markdown import, not chat attachments.

Checks actually run: initial Gradle units/lint/debug1m33s; core units/lint/debug/
androidTest36s; validation APK builds passed. Baseline contract/schema pytest6pass/
2PG skips15.35s; PG18.6 rerun8pass24.73s (existing TestClient deprecation).
Portrait21.866s+4.880s, then22.324s+4.153s real HTTP/PG/Keystore tests passed:
collapse/capabilities, modal options roundtrip/no pending or events, voice modal,
imports and same conversation,48dp row/thread-space, focus/IME/multiline/emoji,
Send and same-request sources. Curiosity actual force-stop9.956s+6.145s passed.
Streaming16.503s, voice review/lineage/playback12.170s and denial/background/draft
recovery6.885s passed with actual HTTP/SQLite and synthetic audio drivers.
Expanded2560x1800/density320/font1.6 rail and typing15.842s passed. Additional
landscape/window and final build/artifact results follow in closeout.

Failures/corrections: unsupported-menu expectation12.300s corrected to actual
capabilities. Import return28.225s then32.861s exposed Unreachable after idle;
kept test-only helper sockets90s, with production networking unchanged. SQLite
stream25.413s failed Busy->Missing; idle consolidation polls acquire the shared
single slot even without queued jobs. Forced disposable overlap produced503
capacity_busy then404 unreserved key (2.99s); ordinary fresh stream also passed
5.58s. Worker disabled via ignored Stream/Voice child env, then all three tests
passed. Episode fixture behavior unchanged. Fixed temporary UTF-8 rewrite
artifacts before final builds; added explicit UTF-8 writes. First landscape
screenshot clipping prompted a short-window internally scrolling editor and
stronger control geometry checks. One later labelled-landscape run was actually
portrait; do not count it as landscape. Collector now checks dimensions.

Ruff initial collector-format failure corrected; lint/format282files, pip check,
whitespace passed. Windows JDK21.0.12.101/Gradle8.13, API37 owned emulator, separate
dev.ada.validation.redesign.debug only. Synthetic screenshot host never disables
MainActivity FLAG_SECURE. User-supplied private screenshots were not copied into
fixtures/logs/docs. Pre-task hashes protect backend/contracts/ownership/audio/
controllers/journals/migrations/locks and unrelated proxy edits.

Skipped/remaining: full backend/web/connected suites, physical S24FE, manual
TalkBack/IME variants, foldable live resize, graphics/battery/long-scroll and
inherited voice/focus/G-41 gates. No native model inference required. No live
application database write/migration, normal app install, deployment or later
phase. Current verification and cleanup closeout follow below.


Compact closeout: normal Gradle all258units (0failures/errors/skips), lint/debug/
androidTest/unsigned-release passed53s; lint0errors/23existing warnings. Normal
APK metadata dev.ada.assistant.debug/19/0.25.1-ambient verified. Password stages
8.921s/4.018s and MainActivity foundation15.570s passed. Final real rotated
landscape24.455s passed full48dp focused controls, Send and sources; dimensions
2400x1080, font1.3, three-button. One earlier24.415s labelled landscape captured
portrait;25.512s was real landscape;25.514s stage passed but collector rejected
portrait dimensions. Final emulator fixed-to-user rotation made orientation
reproducible. Existing Compose rotated layer capture misleadingly cropped the
composer; new public-only UiAutomation whole-window image confirms full composer
above actual OS keyboard. No MainActivity screenshot flag change. Earlier records
remain app-surface-only. Portrait normal multiline22.324s/4.153s passed.

Audit:638baseline/21changed-new/no deletions,391protected unchanged; OpenAPI still
126paths/168schemas byte-identical. FourUTF-8 docs/36local links, zero configured
credential/contact matches in changed/ignored non-image artifacts. Other updated
feature suites compiled but not separately run. Full-suite/physical/performance
limits above remain open. Normal emulator package observed preexisting with last
update13:26:28 (before this refinement), left untouched; separate validation
packages removed by helpers. Final Ruff/pip/whitespace and owned resource cleanup
follow below.


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


### 2026-10-19 — Phase 26 checkpoints A–F — b2a383e + working tree

Scope: implement only always-on operations/recovery after required instructions,
source/OpenAPI/migration inspection and baseline. Preserve prior uncommitted
Android design work. The user separately authorized a four-hour isolated soak;
production installation/deployment remains outside this task.

Changed behavior/files: host_security/config/runtime/health/supervisor/proxy/
backup/ops modules add protected installation state, current-SID DPAPI and
independent encrypted key recovery, one API admission owner, owned child Job
Objects, finite recovery and truthful metadata. Windows ACL/task/power scripts
provide reviewable logon/daily tasks and explicit reversible AC controls.
start.ps1 uses the same ownership gate. Consolidation checks discretionary
eligibility before private reads/claims and takes no slot for an empty poll.
operations.py adds bounded PG preflight/snapshot queries and honest snapshot time.
The disposable HTTP harness and native failure tests exercise actual children,
identity/key access, proxy, admission, crash/replay, backup and protected restore.
See docs/ALWAYS-ON-OPERATIONS.md for reproducible setup/recovery and limits.
The guide includes explicit scenario arithmetic for the256MiB per-snapshot cap
and accumulated full backups; these are labeled assumptions, alongside current
retained-job/context/extraction/proposal quotas, not private-data forecasts.

Data/API/prompt changes: none; head0017/60 tables, OpenAPI126 paths/168 schemas.
Existing snapshots, IDs, owners, source trust, restore credential quarantine,
retention, migrations, lockfiles and archive inventory remain unchanged.
No new general scheduler, dreaming worker, client behavior or provider daemon.
Three legacy tests were corrected for .env-independent defaults and existing
physical-runner wording; no runtime configuration was changed.

Checks actually run/results (full evidence table in the matching STATUS entry):

- Baseline: without PG23 passed/19 skipped (25.18s); first PG run41 passed/one
  setup error (212.98s) after default-listener startup failed; corrected explicit
  loopback55421 PG18.6 baseline42 passed (84.12s).
- Before implementation8 failed/2 skipped (2.29s), then8 passed/2 skipped (2.73s).
  Native checkpoint11 passed/3 failed (7.98s) exposed inherited PS7 module lookup
  in PS5 ACL helper; fixed explicit native imports, then14 passed (13.87s) and
  15 passed (19.22s). Expanded PG/Windows matrix20 passed (57.10s).
  Final focused core/affected/legacy tests40 passed (48.23s).
- First full pytest955 passed/5 failed/27 skipped (1552.07s): two import-version
  mismatches from source edits during the run, two default-payload tests affected
  by the user's changed model/budgets, one stale quality/runner guard. Corrections
  verified in focused checks; froze225 source/script/config hashes before the
  final complete run. Final full suite:966 passed/27 skipped/one existing warning
  in1469.00s (24:28). All225 frozen source/script/config hashes remain unchanged.
- Existing Starlette/httpx warning retained. Ruff Python lint/format passed.
  An initial accidental PS-file lint selection produced syntax noise; corrected
  without changing files. Final lint/format/audit result recorded below.
- Native power Snapshot and ApplyAcAwake -WhatIf passed after fixing numeric-range
  parsing; AC standby/hibernate/lid originals all zero. No applied policy.
- Real same-identity demand-start Task Scheduler DPAPI access passed; temporary
  validation tasks removed. No production startup/backup tasks installed.

Full-suite skips:19 SQLite variants of native PG-locking cases (PG counterparts
executed), two opt-in Ollama admin metadata probes and six opt-in native agent/
tool probes. Their switches were unset; the Phase26 native harness remains
separate evidence. Interim closeout: Ruff lint/format298files, pip check and
whitespace passed; four PS scripts parsed with zero errors in PS5.1.26100.9711
and7.6.6. Protected audit651baseline/637unchanged/30phase changes,225frozen hashes
unchanged,141links resolved, zero configured credential/contact matches across
103source/evidence files. Final record/cleanup audit still required.

Windows/PostgreSQL/model evidence: native PostgreSQL18.6, dedicated
ada_phase2_test at127.0.0.1:55421 plus disposable fixture/restore databases.
The configured application DB was unavailable during read-only inspection and
was not started/modified. Actual Ollama metadata and public inference succeeded.
Initial fake30.22s/30health/zero unavailable, three replies mean/max0.031s,
three200/five503; backup202248B/0.546s, restore1.188s. Initial native18.62s/
11health/zero unavailable, first18.172s, warmmean3.7815s/max3.813s, one200/
seven503; backup201744B/0.812s, restore1.734s. Preserve these earlier results.

Latest short fake60.64s/60health/zero unavailable, six replies mean0.070s/
max0.109s, two200/six503; backup202849B/0.532s, protected-key CLI restore2.969s.
Pinned owned proxy, Task Scheduler identity, duplicate refusal, API child-crash/
exact completed replay, credential quarantine and cooperative stop passed.

Latest native18.75s/11health/zero unavailable used the unchanged configured
qwen3.8-27b-uncensored/context16384/output1024. First reply17.718s from no
resident model; two warm replies mean3.859s/max3.953s, one200/seven503.
Backup201811B/0.640s; protected-key CLI isolated restore3.328s. Afterward one
configured model resident. Duplicate/recovery/replay/quarantine/stop passed.
Last host sample ACtrue/battery100%, RAM available26.2%, NVIDIA13968/16376MiB,
GPU7%/53C, about989GBfree. Short fake RAM41.6%, GPU405MiB/21%/50C. Host samples
are not peaks/ADA-only consumption; CPU thermal unknown.

Four-hour gate failed/open: explicit-fake run08:20:46.054–11:35:46.788UTC
(01:20–04:35Phoenix),11700.734s wall time including startup/cleanup, about3h15.
ConnectError ended it before14400seconds; original timed-loop counts were not
retained and end-of-run backup/restore was not reached. Do not claim uptime or
four-hour success from218 partial monitor observations (217ready, one stopped
with retained prior health). Owned children stopped/fixture DBs dropped; all225
original frozen hashes verified unchanged after failure.

Checks skipped/blocked and reason: real installed reboot/logon/Docker startup,
sleep/resume/lid, applied AC rollback, pre-logon identity/GPU, hardware power/disk
failure, selected off-device copies and actual lost-profile capsule recovery,
large representative backup/restore/RPO/RTO and sustained native thermal/latency.
A24-hour trial needs separate authorization/installation. Client builds/device
tests not rerun: Phase26 changes no client/contracts. Synthetic failure tests do
not replace physical/installed validation.

Remaining issues: a new continuous four-hour window, final protected source/
secret/link audit and owned fixture cleanup; preserve target gates above.
Next eligible checkpoint: close Phase26 evidence, then await explicit selection.
No Phase27–31 implementation, production key/task enrollment, migration or deployment.

During-soak failure audit: the cached foreground reproduction held an occupied
loopback listener, used a disposable LOCALAPPDATA and an unreachable test DB.
It returned1, created the runtime directory and reached the database ownership
gate instead of refusing the occupied port. This confirms a foreground safety
gap; the supervisor already has the preflight. Added/tested the independent
start.ps1 guard after the failed frozen run; configured DB untouched.

Post-soak failure hardening: a controlled real metadata-reader rehearsal reproduced
PermissionError in the supervisor, five unavailable health checks and a final
graceful-stop assertion failure. That diagnostic run reported19.91s through
recovery/shutdown; it is not a completed continuous soak. The first long run did
not retain its supervisor exception/counters, so its exact cause remains unknown.
Windows receipt sharing is confirmed separately and now retries within3s using
unique temporary files. Persistent contention fails boundedly without replacing
the prior receipt. Harness failures now keep safe stage/timing/counters/child
exit/supervisor error types; timed-loop duration survives later failures and only
brief backup-lease contention is retried. No private exception strings/logs added.

Before correction:5failed/3passed in39.92s (one reader/four occupied-port cases).
After correction:28host cases passed in61.91s; three atomic cases passed in3.46s,
including persistent-reader bound. Ruff lint/format300files passed. Newly frozen
227source/script files back the final full suite:975passed/27skipped/one existing
warning,1414.93s (23:34), exit0. All1002collected; same27skip cases confirmed.
Corrected real reader-contention
rehearsal passed60.47s/60health/zero unavailable, six public replies mean0.047s/
max0.063s, two200/six503; Task Scheduler key access, pinned proxy, duplicate,
owned crash/replay, backup202842B/0.547s, CLI isolated restore2.953s, credential
quarantine and clean stop passed. Supervisor error list empty; backup busy retries0.
Additional four-hour laptop-awake availability was requested; do not start the
dependent rerun until supplied. No answer was received before closeout, and no
second long test started. No failed/short result closes that gate.

Cleanup observed: only expected ada_phase2_test/postgres DBs, zero fixture schemas/
public relations, zero ADA26/validation tasks, zero remaining fixture listeners.
After checking resolved workspace datadir, postmaster identity and loopback55421
PID, stopped only the owned native PostgreSQL18 server. Captured AC values and
scheme matched originals; no applied power policy. Production/private DB/API/
Ollama/Tailscale/phone settings untouched. Final Ruff lint/format300files, pip,
native PS5/7 syntax and whitespace checks passed. Final audit651baseline/
637protected unchanged/32phase changes/227current frozen hashes unchanged,
141local Markdown links resolved, zero configured credential/contact matches in
149source/evidence files. OpenAPI126paths/168schemas and released migration/
dependency/client/prior-UI hashes preserved. Source implementation stops at26;
at that preceding closeout the continuous four-hour gate remained failed/open
pending a new awake window. The separately authorized result follows.

### 2026-10-19 — Phase26 authorized four-hour rerun — b2a383e + same frozen source

User confirmed the additional laptop-awake window. Scope: rerun only the fixed
isolated Windows/PG/HTTP/proxy/key/recovery harness, not production deployment.
Preflight227source hashes unchanged; no implementation/dependency/contract edits.
Owned test PG18.6 restarted on explicit loopback55421/free port, expected base/
postgres DBs only and zero fixture schemas/public relations. New14400s fake-provider
run began about15:03:39UTC/08:03:39Phoenix with --with-proxy --task-scheduler
--reader-contention. Evidence run-dbbe30e84a/soak-four-hour-rerun.log is separate
from the preserved failed run. Completion: continuous timed soak **14,400.39 s**,
process exit 0; full harness 15:03:39.282–19:04:23.459 UTC
(08:03:39–12:04:23 Phoenix), 14,444.177 s including setup/recovery/cleanup.
14,278 health samples/zero unavailable; 1,428 public fake replies mean 0.0375 s,
max 0.188 s, first 0.047 s. Eight-request capacity check: two 200/six 503.
Same-user task/DPAPI access, pinned owned proxy, duplicate refusal, deliberate
owned-child crash/exact completed replay and injected receipt-reader contention
passed. Exactly two child starts; exit codes [1, 0], no supervisor errors.
Encrypted verified backup 682,629 B/0.984 s, zero busy retries; protected-key CLI
isolated restore 9.985 s, credentials quarantined. Graceful stop passed; API/proxy
PID fields null. This closes the four-hour **development** gate using an explicit
fake provider, not four-hour native inference or installed production uptime.

Independent 285 metadata observations: 284 ready/one final stopped, max two child
starts, zero sampled pressure, min observed RAM available 35.0%, max GPU 43 C.
Last host sample AC true/battery 100%, RAM 47.2%, GPU 0/16,376 MiB / 0% / 39 C,
disk free 988,799,766,528 B; CPU temperature unknown. Host samples are not peaks
or isolated ADA resource use; harness counts establish the timed result.

Independent cleanup: only expected base/postgres DBs, zero fixture schemas/public
relations, zero ADA26/validation tasks, no listeners on fixture API/proxy ports
59904/59905. Checked workspace datadir, postmaster identity and loopback 55421 PID
before stopping only owned PG18.6; no remaining test PG listener. New read-only
power snapshot matches original scheme/AC sleep/hibernate/lid values; no policy
Apply/Restore. Unrelated email.txt appeared during the run and was left untouched;
cache-only audit accounts for its preserved hash separately. Initial scope audit
reported that new unrelated path; no implementation change or scope expansion.

Ruff lint/format 300 files, pip check and whitespace passed after completion.
The earlier full 975 passed/27 skipped result is retained for unchanged frozen
source; no redundant full run or client/device test. Final audit: 651 baseline /
637 protected unchanged / 32 phase changed-new / 227 frozen hashes unchanged;
141 local links, zero configured credential/contact matches in 167 checked
source/evidence files, one unrelated file preserved separately. OpenAPI remains
126 paths/168 schemas; prior UI, migrations, dependencies and client hashes match.
Installed logon/reboot/sleep, applied power
rollback, service/GPU access, sustained native thermal/latency, representative
RPO/RTO, selected off-device and lost-profile recovery, physical failure and
separately authorized 24-hour verification remain open. No deployment, private
application DB change, installed task or later phase was performed.


### 2026-10-19 — Phase27 checkpoints in progress — b2a383e + working tree

Scope: only durable scheduling/reminders, after required document/source/OpenAPI/
migration inspection and a fresh185passed/3skipped nativePG/SQLite baseline314.06s.
Preserve670 initial files, prior Android/Phase26 work, unrelated email.txt and all
released migrations. No deployment/live DB/system task/power changes authorized.

Changed behavior: new schedule contracts/time/models/service/router,0018 private
inventory and audit constraint, owner/session/device/epoch/source fences, previewed
finite timezone plans, durable leases/cancellation/receipts, latest-only catch-up,
quiet hours and owned inbox/explicit conversation opening. Existing Phase25 question
creation/opening now have shared short-transaction helpers; source/question cleanup
also scrubs/detaches dependent scheduling inbox rows. Global dispatcher is default
stopped; owner consent is off. Background push remains unavailable, with foreground
in-app polling selected. OS backup task remains its sole existing owner. No dreaming,
model inference worker, external messages or arbitrary executable payload added.
Recovery-v4 includes five new private tables and restore quarantine; old formats
remain. Android journal15 preserves v1–v14 and reserves exact operations before
POST; restore performs GET only. Client and admin view validation remains pending.

Actual checks: red calendar10failed/0.17s ->10passed/0.10s; missing HTTP probe1failed/
1skip/1.30s; initial new checks22passed/17.43s. Expanded native/SQLite matrix
44passed/3failed/1skip/55.26s exposed audit constraint and FTS-count fixture issues;
corrected47passed/1skip/56.09s. New stale actor/pruned-question tests4failed/5.84s
before correction,4passed/5.62s after. Native recovery and client checks are running;
no final success claimed yet. PostgreSQL is only owned native18.6 on55421, dedicated
ada_phase2_test plus disposable schemas/databases. No application data used.

Auxiliary issues: initial autogeneration aborted on spurious native FTS index diffs;
existing exclusions corrected it before migration output. A Windows locale web-edit
read failed; explicit UTF-8 follow-up passed. Synthetic fixture credentials echoed
by verbose assertion expansion were redacted in ignored failure logs; later runs
use --tb=short. No real configured secret/private content was copied. Remaining:
full backend/PG/migration/recovery/contract regressions, Android and web checks,
actual HTTP client inbox flow, scope/secret/link audit, documentation and fixture
cleanup. Physical push/doze and installed-host gates remain unverified/off.

### 2026-10-19 — Phase27 client verification and additional fences — b2a383e + working tree

Further genuine findings were added as failing tests before correction. Native
recovery initially4passed/1failed23.95s and a correction attempt1passed/1failed
12.54s exposed an old-format test seeding current API data after prematurely
downgrading. Seed at current head, assert its original200, then downgrade only at
the archive boundary. Expanded checks65passed/3skipped112.14s include old v2/v3,
new v4, native process/lease recovery and Windows protected-key backup/restore.
Consistently changed source text+hash after claim:2failed/2passed5.88s before
exact preview/source-snapshot fencing;4passed5.81s after. Backward-clock edit then
snooze:2failed3.08s before separate plan-generation handling;2passed2.95s after.
Additional payload/read/paging checks:5failed/1skip10.06s before correction,
5passed/1skip8.20s after. Background consent/origin/epoch/expiry metadata now fences
payload loading; inbox GET avoids scope-write locks; retained history is paged.
The skip is the SQLite copy of a native MVCC concurrency test, not missing PG.

Android's initial new full build reported263 units/10 failures, BUILD FAILED
1m49s, due to written-format fixture expectations still14 after journal15.
Preserve legacy-version fixtures while updating current-write expectations.
Targeted48 units then caught one real consent-off/cooldown issue; corrected off
bypasses cooldown while retaining an encrypted reserved operation. Subsequent
normal272-unit/lint/build checks passed32s. New real HTTP flow first timed out
25.658s at preview because equivalent ISO expiry strings compared textually.
Its new unit probe failed once (7 tests/1 failure,7s); compare instants while
retaining the exact pending body, and use whole-millisecond default/snooze values.
Seven corrected units and build passed4s; real emulator flow then passed12.788s
and3.001s across actual force-stop. Final client adds saved-preview recovery in its
original scope, stale-page fences and bounded inbox/occurrence paging. Final normal
Gradle test/lint/debug/test-APK/unsigned-release run passed1m: **275 units, zero
failures/errors/skips**, lint0errors/23 existing warnings. A validation-build attempt
used a nonexistent JAVA_HOME and failed before Gradle; rerunning with the actual
environment passed4s. Final separate emulator HTTP stages passed **12.857s and
3.001s**, with no fabricated user event and exactly recovered acknowledgement.
Validation APKs/reverse/schema were removed; normal APK outputs rebuilt4s.
Checked the owned emulator-5584 AVD identity before stopping only that emulator.
No physical device or normal application installation was used.

Web clean npm install270 locked packages/zero audit vulnerabilities passed earlier.
Contracts generation/check, typecheck, lint,71 units (7.76s) and production build
passed. First real Chromium run6passed/1failed32.2s caught lost keyboard Refresh
focus in the shared monitor query. Restore the originating button after fetch only
when focus has not moved elsewhere; retain native disabled/cooldown behavior.
Corrected **7 Chromium tests passed27.7s** against real disposable PG/HTTP, including
the aggregate-only scheduling page and existing account/auth/failure flows.

Ruff check/format313files, pip check and whitespace passed (Git CRLF conversion
notices only). Live source OpenAPI equals export:138paths/181schemas. All126old
paths/168old schemas compare unchanged after removing only two additive capability
fields and monitor.scheduling from the existing audit enum/query. Released
migrations, later-phase files, lock versions and unrelated email.txt hashes remain
unchanged. Early audit resolved271local Markdown links and found zero configured
credential/contact or literal bearer matches in118 changed/evidence files.
Added the detailed scheduling usage/upgrade/recovery guide and current overview/
roadmap/contract notes. Full backend regression is running on343 frozen files;
no source mutation during that run. Three additional cache-only date-range probes
failed0.41s with genuine overflow at the calendar's lower/upper representable
boundary. Correction and affected rerun will follow the full run to preserve its
source provenance. Final cleanup, exact skips/counts and remaining gates follow.

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


### 2026-10-21 — Phase28 implementation and intermediate verification — working tree after b2a383e

Scope: only phase-28-idle-reflection-and-dream-review.md. Read root/scoped rules,
requested baseline/roadmap, plans README and actual OpenAPI/source/tests first.
Preserved existing uncommitted Phase26/27 and Android design work. Reconciled the
preceding Phase27 checks using their original Oct19 provenance, not a new run.

Prerequisites: existing Phase13 consolidation, Phase18 erasure/versioned recovery,
Phase23 evaluation, Phase25 catalogue questions, Phase26 host observer/single-worker
admission and Phase27 durable origin consent/leases are present. Installed-host,
physical and sustained-native-inference gates remain separate. Initial source
snapshot contains689 file hashes; OpenAPI138 paths/181 schemas and head0018 were
the Phase28 boundary. Restarted only the previously owned disposable native PG18.6
cluster on127.0.0.1:55421; application DB/services/tasks/power/Tailscale were untouched.

Changed behavior: existing dispatcher/consolidation idle hooks, strict separate
owner input/job/time/resource policy, metadata-before-payload/source availability
and publication fences, stable source-set IDs/leases/quotas/reserved off receipt,
rule-only reports/question drafts, explicit review and Phase13 generated-summary
Keep adapter, default-disabled cancellable digest-bound local provider class,
Android22 encrypted journal16 review/recovery, aggregate-only audited admin view.
New migration0019 has five tables; owner-content inventory57, total70. Versioned
backup-v5 restores paused/quarantined and invalidates provider attestation; v1–v4
remain supported. Old prompts, completed replay and released migrations stay.

Checks actually run so far (final runs recorded separately):

- Existing relevant baseline180 passed/4 failed/4 expected SQLite skips in264.08s.
  Four failures were a Phase27 fixture date mismatch (Oct20 calendar vs Oct21
  note creation); fixed only that test clock, then4 passed/44 deselected in6.35s.
- New policy12 failed before module, then12 passed. HTTP tests8 failed before
  routes; combined20 passed. First failure matrix2 failed/15 passed/1 skip found
  missing consolidation-worker switch. After fixing that gate/activity tracking,
  affected consolidation/streaming/reflection104 passed/2 skips in161.63s.
- Added transaction/input/publication barriers:6 failures showed in-transaction
  sensor reads and expired imports poisoning selection/publication;2 further
  failures showed late private JSON reads after off. Moved sampling outside DB/
  model admission, reused fresh host observer data, added pre-payload metadata
  and current availability barriers. Combined51 passed/1 skip in69.71s.
- First review tests2 failed/4 passed due absent admin route; added the existing
  grant/audit projection route. Question opening and generated-summary Keep already
  passed on both DBs and created no factual claims.
- Provider/storage first20 passed/2 failed in22.87s (test regex mismatch only);
  corrected expected refusal wording. Native/SQLite migration, erasure, encrypted
  reflection/schedule restore, released-v4 compatibility and host backup26 passed
  in60.93s. New set-order test failed2 cases; normalized unordered policy choices
  in the job key. Evaluation/review/failure selection57 passed/1 skip in114.18s.
- Native public loopback metadata probe found available qwen3.8:27b. The first
  probe selection found no configured matching tag; the explicitly selected
  available public model then returned reflection_cancelled at1219ms,719ms after
  a500ms request. No private inputs, model launch/unload or production setting
  changes. This measures client return only; server GPU cancellation/usefulness
  are unproven, so summary generation remains disabled.
- Android first build failed on a shadowed completion-lambda variable; corrected.
  Unit/lint/debug build then succeeded. A separate validation build's first command
  was rejected by its ID guard due PowerShell unquoted property parsing; quoted
  property build passed. First real HTTP stage timed out because the test submitted
  while navigation refresh was busy; added synchronization, not a transport bypass.
  Final two emulator-only stages passed6.500s/2.692s: real owner HTTP report Keep,
  actual force-stop, Keystore pending-off receipt recovery and no duplicate POST.
  The connected physical phone and normal app were untouched.
- Web npm ci, regenerated contracts/check, type/lint,72 units and build passed.
  First Chromium run7 passed/1 failed: adding navigation exposed a200% zoom overflow.
  Added wrapping; final browser rerun is pending. Initial Ruff diagnostics were
  fixed; final whole-tree check will be recorded with final evidence.

Skips/remaining: full Python/native suite and one-minute isolated interference
exercise running; final browser/Android/check audits pending. No physical/TalkBack,
installed overnight/private-data usefulness/native GPU/cancellation quality or
later-phase/deployment work. Model summary class remains off. Do not treat these
intermediate counts as a completed final source validation.


### 2026-10-21 — Phase28 frozen broad suite and final source review — working tree after b2a383e

The source-fixed broad run passed **1161 tests /32 expected skips** in2169.59s,
with the pre-existing Starlette/httpx deprecation warning. It includes the new
bounded native host exercise and the earlier default-off report/question/review,
source/consent/lease/resource, migration/replay/erasure and backup cases. New final
review tests added after collection are not attributed to this broad run.

The one-minute isolated native PostgreSQL/fake-provider exercise took61.97s:
30 foreground replies, one reflection report, one verified encrypted backup,
one retained run and zero factual claims. Baseline median156ms vs foreground
p95=63ms (observed delta−93ms) mixes cold/warm measurements; it is not evidence
that reflection improves latency. Resource inputs were explicit synthetic safe
values. A separate hardware snapshot showed AC on,47°C GPU and only2.3% available
memory during validation, which is below the10% eligibility minimum. After owned
emulator cleanup, a read-only sample showed20.6% available memory and the pure
resource gate accepted it with other conditions simulated. GPU time remains
unknown; no real private content or background native summary was used.

Final review reproduced10 failures on SQLite/PostgreSQL: cross-scope/dismissed
question duplication, changed catalogue text being substituted on explicit Open,
deletion preview accepting a running publisher, and foreground arrival during
selection not stopping dispatch. A separate real loopback trickling-metadata
probe failed its cancellation bound (1 failed/10 deselected in3.02s). These are
new tests after the fixed-source broad collection. Corrected by retaining an
owner-unique question-template field in unreleased0019, metadata-based owner-wide
dedup with publication backstop, exact reviewed-question comparison/rollback,
reflection publisher quiescence, a post-selection foreground gate and checking
cancellation/deadline while reading provider metadata. Released0001–0018 remain
byte-identical. The first final guard/provider/native-schema selection passed
33 tests in40.30s. A broader final affected/native/recovery run is pending; its
results will be recorded separately rather than relabeling the earlier full run.

Android final source has283 passing units, zero lint errors/23 existing warnings,
debug and separate validation APK builds. After review-layout refinements, real
HTTP/Keystore/force-stop stages passed5.793s/3.772s; these precede the final server
guards and internal dedup field. The separate emulator was stopped and the normal
app/connected physical phone were untouched. Final server/client integration will
be checked after the affected run. Web72 units/type/lint/contracts/build passed;
first Chromium7/1 exposed the new navigation's200% zoom overflow, wrapping fixed
it and all8 Chromium cases passed26.1s. Final CSS build is being verified.

Compatibility audit: old schema names retained; only additive reflection capability
and audit action/filter enum extensions change existing contract shapes. No
configured-secret matches found in changed/new files. Prior689-file snapshot has
no missing file; migrations0001–0018, later phase files and email.txt are unchanged.
No live DB/service/task/power/Tailscale change or deployment. Final cleanup and
source/link/secret audit will follow the pending final checks.


### 2026-10-21 — Phase28 final affected/native/client verification and cleanup — working tree after b2a383e

The final affected run passed **282 tests /4 expected SQLite skips in599.06s**:
all then-current reflection files plus test_security, test_recovery,
test_consolidation, test_curiosity, test_schedules, test_streaming,
test_host_foreground and test_host_backup. This follows the post-broad-run
question-template/schema, explicit-question, deletion/dispatch and provider
metadata guards; includes native populated upgrade/check/replay, erasure,
lease/process-crash fencing and actual encrypted restore. The updated recovery
case contains both a question artifact (template metadata preserved) and a running
report (quarantined). Separate final completed-turn opt-in/trust and request-state
publication checks passed4 tests on SQLite/PostgreSQL in6.89s. No further server
behavior changed after these checks. Earlier1161/32 broad and33 guard selections
remain distinct overlapping evidence, not a rebranded final full run.

Latest isolated host exercise:60.09s,29 in-process ASGI foreground requests through
FastAPI TestClient/native PG, one report, one encrypted backup verified, one retained run,
zero factual claims. Explicit fake provider/synthetic safe resource readings;
baseline median47ms, foreground p95=78ms, delta+31ms within500ms. Hardware snapshot
separately showed51°C GPU/23.7% available memory on AC. GPU time is unknown.
The earlier61.97s/30 exercise and its cold/warm−93ms delta are preserved above;
no speedup or sustained native-GPU claim is made.

Android final283 units/0 failures or skips, lint0 errors/23 prior warnings;
debug/validation builds passed. Final server real HTTP/Keystore/force-stop stages
passed5.943s/2.969s, including report Keep, encrypted exact pending-off receipt
recovery and server-side count of3 reflection POSTs across restart. This uses only
dev.ada.validation.phase28.debug on owned emulator5584. Normal app/physical phone
untouched. Web final contracts check/type/build passed after the CSS correction;
72 units and8 Chromium cases26.1s remain the appropriate unaffected logic/keyboard/
zoom evidence. Dependency versions/locks/wrappers were preserved. Whole-tree
Ruff/format and pip check passed; one old Python deprecation remains.

Evaluation: per backend, owner accepts1/1 public marker report;3 negative pairs
produce no conflict flag,1 overlapping endorsed pair gives only a possible-change
flag. Same-source, cross-scope and discarded drafts do not repeat; changed
catalogue Open rolls back without a question/user turn; automatic completed-user/
model selection retains trust and model TODOs never become owner findings/claims.
These are small synthetic criteria, not a representative personal-quality study.

Remaining target checks: physical TalkBack/large-font/resize, installed overnight
host behavior and representative data; native-summary usefulness, verified GPU
stop/foreground interference and sustained native operation. Summary generation
remains disabled with no production attestation workflow. Old host/device gates
remain open and no later phase is started.

Cleanup verified PostgreSQL18.6 data directory, postmaster PID32088, listener55421
and executable identity; only ada_phase2_test remained and fixture schema count
was0. Stopped that owned cluster. Validation packages/reverse mapping were removed,
owned emulator23244/5584 stopped; no normal app, production task/power/Tailscale or
application DB/service changes. Scope/contract/link/secret audit follows below.
Next eligible work: user review/optional future operator setup and the explicit
target gates; this task stops at Phase28 with no deployment.


Final audit (2026-10-21):80 changed/new files against the Phase28-start snapshot;
no prior file missing, no changes to migrations0001–0018/later phase plans or
email.txt. No configured-secret matches in changed/new files. Existing OpenAPI
paths/schemas are identical after removing only the additive reflection capability
and audit-action enum/filter extension; no old schema removed (145 paths/193
schemas). Ten changed guide/index/architecture documents passed UTF-8/local-link
checks with zero missing targets. Final Ruff: all checks passed/333 files formatted;
pip: no broken requirements. Validation/API/web/PG/emulator listeners are absent.
Only owned validation processes were stopped; physical phone and normal app were
not operated. The one-minute exercises use in-process ASGI TestClient, native PG
and fake chat; they are not supervised TCP availability or installed-host trials.

### 2026-10-21 — Phase29 A–C study/interface — b2a383e plus preserved working tree

Scope: only phase-29-natural-local-speech.md; required/root/plans/Android rules,
source/OpenAPI/migration/test baseline inspected first. Fresh snapshot715 files;
no connected ADB device.17/17-A source exists, with unresolved physical audible
focus and native permission gates. The selected phase permits architecture/license/
interface and host/emulator closure while runtime selection/activation remains open.

Changed behavior/files: new NATURAL-LOCAL-SPEECH guide compares pinned sherpa1.13.8,
Zipformer20M, whisper.cpp1.9.5/tiny.en and conditional Kokoro model/runtime/voice/
phonemizer licenses, compatibility, storage and metadata digests. No binaries or
models obtained. Kotlin LocalSpeechManifest provides externally pinned versioned
metadata and bounded exact byte verification only, with no approved catalogue,
installer, native loader or activation permission. Host failure tests cover paths
including Windows ADS/reserved/case collisions, traversal, executable extensions,
corruption/partial/trailing bytes, overflow, unknown schema/fields and unsupported
device/language metadata. UI adds expandable engine/model status and public voice
preview, uses existing rate choices and explicitly explains unsupported style.
Playback rechecks installed offline voices, avoids implicit different-language
selection and fences stale utterance errors. Read reply requires a selected voice.
Controller invariants cover no HTTP/mic/write on preview, late completion, recording,
navigation/background/owner changes and explicit language choice. Existing transcript
review/encrypted recovery and independent generation cancellation remain unchanged.

Data/API/prompt changes: none. Android app23/0.29.0-speech-study; journal16 unchanged.
All production Python/admin code, contracts/OpenAPI, migrations0001–0019 and old
prompts/replay preserved. No new private storage, erasure/backup inventory, runtime
dependency or lock change. No live DB/service/app setup or deployment.

Checks actually run/results:

- SQLite voice/client/schema baseline34passed/30skipped55.20s. Native PostgreSQL18.6
  same selection64passed134.72s; validator guards4passed0.08s. Existing Starlette/
  httpx warning retained. No production database used or migrated.
- Pinned Android baseline unit/lint/debug passed27s; new failure tests first red at
  missing contract/preview compilation. Focused unit checks passed29s. Full units
  **292/0failures/0errors/0skips**, lint0errors/23oldwarnings, debug/unsigned-release
  passed; final platform-source run65s before the selected-voice enable guard.
  Final guard rebuild/verification results follow below. Existing deprecated TTS
  callback compiler warning retained. No dependency upgrade or suppression.
- Explicit separate validation APK: first UI status assertion failed because the
  test omitted substring=true. Corrected preview passed6.694s; next review stage
  failed at Record because the generic admin fixture intentionally advertised no
  streaming voice. Added ADA_WEB_TEST_VOICE_FIXTURE only in the disposable helper,
  reusing AndroidChatProvider, with an explicit capability assertion in the test.
  Production runtime/authority unchanged. Corrected real HTTP/Keystore emulator
  checks passed8.307/13.740/9.074s (synthetic audio), with actual force-stop between
  independent checks and APK/reverse/schema cleanup. These are not native audio
  quality measurements or a new staged journal process-death pass.
- Full-tree Ruff passed;248files reported formatted. One new import-order issue
  was corrected. A multi-file documentation patch initially failed a context match
  atomically; corrected without losing existing edits. Snapshot audit confirmed
  OpenAPI byte identity and protected source/migration/contract/later-plan bytes;
  local Markdown links passed. Final scope/secret/cleanup audit follows below.

Checks skipped/remaining: no full unrelated backend/web rerun; no server/web runtime
changed. No new runtime/model download/inference/install/removal; those controls
are specified and unavailable. Final distributable licenses/transitive notices,
Kokoro conversion/voice/eSpeak/data rights, target ABI/API/native alignment and
per-device thresholds await evidence. S24FE en-US accuracy/name/date/endpoint/first
audio/naturalness/app+service RAM/storage/CPU/unplugged battery/thermal comparison,
17-A audible focus and native revocation/settings/call/route/Stop/lifecycle cases,
memory pressure/removal/late native output, manual TalkBack and older APIs remain
pending. Model metadata or desktop speed cannot satisfy these. No installer means
no staged audio/model temp cleanup is claimed tested. Current platform adapter
retains no app audio file/PCM buffer; OS internals are not attested by ADA.
Next eligible checkpoint: Phase29 D only after physical baseline, frozen thresholds,
approved exact bundle/runtime and explicit activation choice; alternatively record
the measured decision to retain platform speech. No Phase30/31 work or deployment.

Phase29 final-source closeout (machine evidence2026-10-22UTC; local dateOct21):
after the explicit selected-voice Read reply guard, full Android292 units, lint
0errors/23existingwarnings, normal debug and unsigned release rebuilt successfully
in29s. Separate validation APKs rebuilt; all three actual HTTP/Keystore emulator
checks reran and passed **7.372/12.571/6.390s**, with synthetic capture/playback.
Earlier failed and successful attempts above retain their own provenance. Normal
debug/test APK outputs were restored afterward without installation.

Final boundary audit: **20 changed/new files**, no original file missing. Production
backend/admin source, contracts/OpenAPI, migrations0001–0019, dependency locks/
wrappers, later phase plans and the pre-existing private file remain byte-identical
to the Phase29-start snapshot. OpenAPI remains145paths/193schemas. Local Markdown
links and diff whitespace checks passed (Git's existing LF/CRLF notices retained).
Configured-secret scan reported0matches without printing values. Whole-tree Ruff
lint/format passed,248files reported formatted. No new migration or server upgrade.

Cleanup: validation APKs and reverse mapping removed. Verified0fixture schemas
and only base ada_phase2_test besides normal PostgreSQL system databases. Matched
the owned loopback55421 listener, postmaster executable and resolved in-workspace
data directory before stopping that disposable PostgreSQL18 cluster. Verified
the owned5584 emulator's AVD identity before stopping it. No physical device,
normal app, production database/service/proxy, Ollama, task/power/Tailscale setup
or later-phase work was operated or deployed. The only remaining work for Phase29
is the explicit license/native/physical measurement and activation gate described
above; platform speech remains the usable path.


### 2026-10-22 — Phase30 A–D — schema0020 / Android24 / ada-work-v1

Scope: only requested projects/personal follow-through. Owner selected balanced
personal commitments and development projects. Read root/scoped instructions,
README/architecture/current state/standards/workflow/status/roadmap/phase30 and
actual source/OpenAPI/test state first. Starting snapshot:719 existing files,
head0019/70tables/57owner-content/backup-v5,145paths/193schemas,Android23/journal16.
Preceding phases26–29 had substantial uncommitted changes; no reset/clean/commit.
No delegation or later-phase implementation.

Changed behavior/files: new work models/contracts/service/router/migration0020;
owner locks, immutable revisions and exact reserved receipts, preview/source/time
validation and explicit project creation. Requested completed-chat Save starts a
blank reviewed draft with original generated provenance. Selected personal/project
briefs are deterministic projections with source reauthorization, immutable
calendar/status snapshots and owner/scope/revision/epoch/overdue cache bindings.
Optional25 questions and27 reminders retain consent and work binding; edits pause
linked automation. Existing generic schedule paths cannot bypass the binding or
revive completed work. New owner-content inventory, recovery-v6/older-format
support, erasure and downgrade preflight retain released history. Android typed
HTTP/controller/Compose destination, menus and Settings use encrypted journal17,
old-version reads and GET-only restart recovery. No private admin page/model/tool
write or new worker was added. Docs/PROJECTS-AND-FOLLOW-THROUGH.md includes usage,
recovery, endpoint map and future installation commands. Other docs/status/phase
checkpoints updated, with earlier evidence retained.

Data/API/prompt changes:0020 adds work_items/work_revisions/work_receipts/work_briefs
(74tables/61owner-content). Backup-v6, readablev1–v5, restored authority quarantine.
157paths/206schemas; strict comparison preserved145prior paths and193prior schemas
except additive CapabilitiesOutput.work_protocol. Old chat prompts, snapshots,
completed replay and factual trust remain unchanged. Android24/0.30.0-work;
no dependency/wrapper/lock upgrade or normal installation.

Checks actually run and results (logs under ignored .pytest_cache/phase30):

- backend-baseline.log:45passed/1SQLite lockskip85.17s; Android baselineunit/lint/
  debug10s. New work red baseline8fail/10skip before implementation. First work
  selection17/1(26.66s), work+question+schedules41/1(79.03s), initial native storage
  7pass20.36s, source-corrected23/1(46.18s), work-complete38/1(85.07s).
- backend-full.log: **1206passed/33skips**,2457.14s, native fixtures enabled. Imported
  before the final guards; its provenance is retained. backend-final-affected.log:
  **210/5**,471.53s before latest calendar/storage guards. A command with obsolete
  test_client.py/test_schema.py names collected nothing; corrected actual filenames.
  backend-closed-source.log: **221passed/5skips**,510.00s. Last Windows-safe due
  conversion was made after its import; work-closed-source.log then passed
  **49/1**,113.62s. work-linked-recovery.log: **1passed4.67s**, after extending the
  nativev6 test to linked question/reminder quarantine and three preserved revisions.
  All use --assert=plain to avoid token-bearing rewritten assertions. Existing
  Starlette/httpx deprecation retained. The five affected skips are SQLite-only
  owner-row-lock/MVCC/abrupt-process cases; PostgreSQL versions ran. Full33skip
  count is reported without inventing unexpanded individual reasons.
- Android encrypted work tests first caught journal version16 on write; corrected17.
  Source/preview HTTP run found a nonexistent event source-version column; corrected
  actual SourceVersion→Source→Event relation. Collapsed LazyColumn locators were
  expanded/scrolled explicitly. Work+brief+force-stop then passed9.353/4.625s;
  later UI project creation stage and recovery passed **10.429/4.405s**. Restart GETs
  did not increase server work POST counts; explicit exact retry increased byone.
  APKs/reverse/schema cleaned by the safe runner. Final receipt-guard rerun follows.
- Android intermediate allunit/lint/debug/unsignedrelease77s preceded the final
  timezone DTO/receipt guards. Final **300units/0failures/0errors/0skips**, lint
  **0errors/23oldwarnings**, debug/unsignedrelease **53s** (android-final-verified.log).
  New receipt-definition test had two failed attempts: scope was absent after
  controller reset, so valid recovery was deliberately withheld. Fixture refresh
  corrected; equivalent expiry instants and wrong definitions/revisions are tested.
  Old CapabilitiesDto positional construction required adding the field at theend.
  Legacy journal fixture version expectations and menu indentation were corrected.
  One unencoded Python read briefly rewrote a test's Unicode as mojibake; reversed
  that transformation and used explicitUTF-8 thereafter. Original Unicode test
  assertions passed. No dependency suppression or failed check claimed successful.
- Admin baseline npmci/contractgenerate/check/type/lint/72units/build/8browsercases
  passed35.8s; final regenerated DTO/check/type/lint/72units (total32.11s)/build
  passed. Browser startup without ADA_TEST_DATABASE_URL timed out60s; corrected
  fixture environment rerun8Chromiumcases **27.0s**. Existing Starlette and terminal
  color notices retained. Final runtime admin source stayed unchanged.
- Whole-tree Ruff lint/format passed **348files**. OpenAPI strictold/new audit passed
  (145oldpaths/193oldschemas, one additive capability). Final boundary, links,
  configured-secret and owned-process cleanup evidence follows below.

Windows/PostgreSQL/device/model evidence: native18.6 disposable cluster55421,
owned schemas/databases only. Populated0019→0020 upgrade/check preserves old reply;
concurrent CAS has one winner; exact duplicate receipts do not duplicate work;
v6 encrypted linked-work restore and released0019v5 restore/upgrade passed.
Separate headless API37 emulator5584/Medium_Phone_API_37.0; synthetic fake provider,
real HTTP/Keystore/force-stop. No physical phone was operated. Brief path makes no
network inference and has no authority to invoke one.

Checks skipped/remaining: physical layout/TalkBack/older Android APIs, human useful
workflow/acceptance ratings and sustained personal/development outcome measurement,
installed-host reboot/dispatch/soak and native model checks. Existing Phase29
speech/license/device gates stay open. No full backend rerun after final guards;
the broad result plus fresh affected/Phase30 selections are distinguished above.
Scope picker first100, work200/revisions2000/receipts5000/brief100 perowner, local
pending4/24000UTF8bytesperoperation are deliberate bounds, not silent pruning.
No live migration, deletion/reset, normal app install, provider operation, task/
power/Tailscale modification, deployment or external action. No Phase31 changes.
Next eligible checkpoint: real-owner acceptance/physical accessibility and a
separately requested installation; later phases need separate instructions.


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

### 2026-10-22 — Phase31 resumption and retained19A evidence —04c5962 plus closeout

Scope: user reconnected the S24 FE and asked to finish Phase31 before future
planning. The earlier instruction to continue without the phone had superseded
the old reconnect question. No new model,19B integration, later phase or deployment.

Changed behavior/files: added a direct PDF completed-answer/new-extraction replay
regression; corrected PDF-capable file-error/preview wording. Added an optional
public-data human review stage to the separate validation runner, using existing
document/source components and an explicit Finish review button. Updated the PDF
guide with reproduction commands, checkpoint evidence and acceptance limits; the
draft guide distinguishes actual synthetic signed-protocol evidence from pending
native inference. No new API, migration, prompt or dependency change on resumption.

Retained checks reconciled from the interrupted run, not newly rerun: affected
backend170pass/5skip728.83s, final guard41pass/1skip196.38s, Docker cleanup/limits
8pass26.50s, publication/principal4pass18.04s, central PDF source-lineage/proposal/
work/edge87pass/5skip375.73s. Red cleanup and corrupt-source tests preceded their
fixes. Earlier broad run5fail/1248pass/33skip4549.39s had stale contract, corpus
worker-race and operator web-opt-in fixture failures; their entire files then
passed36/1skip66.64s after corrections. These facts do not claim a final full pass.
Current complete regression is running; result/skip reasons follow separately.

Retained Android actual API37 HTTP/Keystore protocol stages7.521s/4.433s/4.755s
passed real signing, server verification, encryption, actual force-stop, GET-only
receipt restoration, exact explicit retry and revocation with synthetic output.
Optional ARM64/16KiB ELF/APK/notices checks passed. Physical native FD/isolated UID/
no-network/cancellation and actual model-to-signed-draft evidence remain open.
Both model quality failures remain; generation and edge_inference stay disabled.

Fresh checks: PDF-specific page/context/replay test2pass/28deselected6.18s, both
SQLite/native PostgreSQL. S24 FE SM-S721U1/API36 real HTTP/Keystore/Docker/disposable
PG stages4.239s/2.943s passed binary review/upload, two-page source mapping, visible
scan failure, actual force-stop, GET-only reopen and one original explicit upload.
Manual-helper attempt first failed a scope-selection wait (automated stages had
passed5.66s/2.741s); corrected helper stages5.321s/2.475s passed and opened the
optional review. Human result is recorded separately, never inferred from a timer.

Normal Android units/lint/debug/unsigned-release/test APK build passed1m41s:
306units,0failures/errors/skips; lint0errors/24warnings (23retained, one dormant
model-importer usable-space advisory). Normal APK identity/no-native/no-weights
verified; no normal installation. Whole-tree Ruff lint/format passed372files;
strict additive OpenAPI/whitespace checks passed. Interim audit101 changed/new
versus736 baseline files,0missing/protected/secret matches; released0001–0020,
locks/wrappers unchanged. Editor CMake setting preserved. Formatting the pre-existing
extraction benchmark settings block closed an initial formatting-only check failure.

Data/API/prompt changes on resumption: none. Source remains0021/76tables/63private
inventory/backup-v7/OpenAPI164paths216schemas, Android25/journal18. PDF/sync off by
default; OCR disabled by documented decision. Final complete-run result, visual
review, audit and owned infrastructure cleanup follow in the closeout entry.
Verified and removed only the prior tracked public CLI/two-model directory from
the reconnected phone after checking its resolved path/owned entries. No normal
app, private file, installed database/service, proxy, Tailscale or host policy change.

### 2026-10-22 — Phase31 final code/shared checks —04c5962 plus closeout

Changed behavior: quarantine the parser adapter when a failed worker's removal/
exit is unconfirmed, preventing another admitted parse alongside unknown work.
A red fault test preceded this change. Three fault modes preserve fixed timeout,
release the host slot and reject subsequent parsing until reinitialization. No
new API, schema, prompt, quota or production feature flag change.

Checks actually run: full shared `pytest --assert=plain -q --tb=short -ra` with
native PostgreSQL18.6/actual PDF manifest **1277pass/34skip/1warning**,2792.32s,
exit0. It imported the parser before the final quarantine guard and profiles;
this is not presented as a full final-source rerun.34skips:8 opt-in Ollama checks
(2health/6native agent) and26 SQLite-only native-lock/MVCC/process cases; native
counterparts ran. Existing Starlette/httpx deprecation remains. After the guard,
fresh entire PDF selection **47pass/no skips**,147.64s; the earlier46pass165.30s
and red failure remain distinct. Actual parser isolation/faults, both DBs,
authority, version/context/replay, upgrade and encrypted restore all ran.

Measurement checkpoint: added fixed developer-generated public layouts and a
metadata-only profiling tool/report, no database/model or third-party files.
Six layout tests passed6.88s; profiler verified expected fragments/pages and
identical dense text hashes across compression. Original sizes607–86572bytes,
extracted16–50768bytes,1–16pages/1–64chunks; local post-verification parse/validate/
chunk437–531ms, excluding upload/model/cold image download. The uncompressed dense
sample needs smaller sections on Android; byte quotas stay unchanged. Column/
table semantics and personal-document acceptance remain unproven. Output stores
public metadata/hashes only in evaluations/text-pdf-profile-2026-10-22.json.

Static checks: whole-tree Ruff lint/format374files passed after correcting the
new fixture suppression; strict existing path/schema compatibility passed.
Final normal APK-output restoration, human visual evidence, audits and cleanup
follow below. No new model activation, later phase, live migration or deployment.

### 2026-10-22 — Phase31 human acceptance/cleanup and stop —04c5962 plus closeout

Manual evidence: the earlier nine-minute window expired without Finish review;
the user later explicitly confirmed readable/no layout problems and requested a
reopened check. Separate S24 FE/API36 real HTTP/Keystore/Docker stages passed
4.213s/2.761s/111.542s, exit0. Last stage includes human inspection/waiting; the
phone's Finish review button completed it. Earlier helper scope error and timeout
remain failures, not relabeled passes. Confirmed public-sample page/source
readability does not claim TalkBack, personal-file or table semantic acceptance.

Cleanup: normal APK/test outputs restored by a successful7s build, no normal
installation. Phone validation/test packages and tcp19822 reverse removed;
0fixture schemas/databases beyond the isolated base/system DBs. Previously owned
public CLI/model directory removed only after path/entry verification. Verified
Medium_Phone_API_37.0/emulator5584 before stopping it; ports closed. Verified native
PostgreSQL18 executable/PID36032/port55421 and resolved workspace-cache data path,
then stopped only that isolated cluster.0listeners on55421/18423/19822/5584/5585,
no residual PDF containers. Left Docker Engine/user containers, physical phone's
normal ADA, configured DB/API/proxy/Ollama/Tailscale, tasks and power policy alone.

Final audit/static results:104 changed/new versus736 Phase19A/31 starting files;
0missing/protected-migration/lock/wrapper changes and0configured-secret matches.
Preserved the original editor setting. Ruff lint/format374files and whitespace
checks passed;85 Markdown files had0missing local targets. Existing157 API paths
and required schema properties preserved except documented additive PDF enum/fields.
This current closeout did not change schema, API or prompt history from04c5962.

Outcome: complete Phase31's bounded text-PDF implementation/automated exit with OCR
off as explicitly permitted. Source remains0021/76tables/63owner-content/backup-v7,
Android25/journal18; PDF defaults off and installation/enabling remains separate.
Remaining verification: representative personal files, visual reading-order/table
semantics, TalkBack/older targets and real-model answer usefulness.19A remains
disabled/open after the failed candidate trials. No later phase or deployment;
future planning can be a separately selected task.

### 2026-10-22 — manual startup diagnosis, progress and usage guide — 04c5962 + existing workspace

Scope: help the user run `start.ps1` and `start-private-proxy.ps1`, investigate a
blank foreground window and update HOW-TO-USE-ADA. The user requested an explicit
address/port/connection banner. Existing Phase31 and other local edits retained;
no next-phase work or deployment.

Changed behavior/files: `scripts/start.ps1` prints progress before invoking
unbuffered Python. `src/ada/host_runtime.py` prints fixed loading/gate/recovery
stages and announces the address only after Uvicorn's lifespan and bind succeed.
It shows local readiness/explorer URLs, conditional `ADA_BROWSER_ORIGIN` admin/
Android URLs and a stop notice. Ctrl+C matches the prior quiet Uvicorn wrapper;
interrupted/failed startup remains nonzero. No root/access/exception logging was
enabled. Existing worker count, kernel/PostgreSQL ownership locks, request
recovery, concurrency limits and HTTP behavior remain. Tests use temporary
profiles, unavailable synthetic DB endpoints or public ASGI fixtures on free
ports, never live request recovery.

`docs/HOW-TO-USE-ADA.md` now provides the normal password/Tailscale route first,
current0021 setup/upgrade expectations, literal dotenv examples, exact client
origins and a detailed A/API, B/proxy, C/checks daily sequence. It distinguishes
foreground waiting from health, HTML availability from API readiness and internal
HTTP from Tailscale TLS; advanced token/Vite/USB routes remain explicit options.
Updated stale PDF/permission/physical-runner statements against current source.

Data/API/prompt changes: none. Generated in-memory OpenAPI equals the checked-in
export exactly:164 paths/216 schemas. Released migrations, dependencies/locks,
request IDs, prompts/snapshots and replay were not changed by this task.

Checks actually run and results:

- Existing six native foreground tests passed15.42s after the initial console
  edit; this was not a pristine pre-edit test run. Extended intermediate runs
  passed9/15.57s and10/15.57s. Final command
  `python -m pytest tests/test_host_foreground.py tests/test_schema_contract.py -q`
  passed **15 / 0 skipped in19.57s**, including native PowerShell5.1/7 occupied-port
  and unavailable-database paths, real isolated IPv4/IPv6 HTTP listeners, late
  bind/lifespan failures and Ctrl+C before/after startup. One existing Starlette/
  httpx deprecation warning. Earlier Phase31 full-suite results are not a new run.
- `ruff check src tests migrations scripts` and matching `ruff format --check`
  passed;283 Python files formatted. The first targeted format check identified
  style-only differences; formatted and rechecked successfully. PowerShell
  startup parsing and `git diff --check` passed.
- In-memory OpenAPI equality passed. All63 local guide links/anchors resolve;
  code fences balance. Proxy `-CheckOnly` passed its pinned-binary/dist/config
  validation; automatic-HTTPS-disabled/unformatted-config messages are expected
  with this existing Tailscale template. `pip check` found no broken requirements;
  `alembic heads` reported0021, without migration.
- Read-only live probes initially found readiness/0021 on8000/18764. A later
  check found no8000 listener and502 upstream while `/admin/` still served200.
  The user said they had not stopped it. The later user-launched foreground
  runtime was then observed listening; final8000/18764/tailnet HTTPS readiness
  all returned200/ready/0021. HTTPS admin HTML returned200 with normal certificate
  validation. Docker `db` was healthy on loopback5433; Ollama tags returned200
  and included the configured exact model. No generation or private API read.
- Process/event metadata did not establish the interruption cause. A separate
  unique empty-folder probe confirmed Store-Python/native LocalAppData visibility
  differs; the probe was removed. No causal ACL failure was confirmed in the
  subsequently running foreground instance, so runtime paths/ACLs were not changed.

Checks skipped/remaining target verification: no full backend/PostgreSQL fixture
matrix, Android/web build/device/accessibility, password enrollment/sign-in or
real-model inference rerun; this change adds console reporting/documentation,
not schema, ownership or client behavior. No live process was stopped/restarted
to demonstrate the new banner. The user will see it at the next manual start.
Recurring unexplained exits require fresh timing/fixed status evidence; no crash
root cause or automatic restart guarantee is claimed. Existing physical/model
acceptance gates remain as previously recorded.

Outcome: current route is healthy and startup behavior is visible/reviewable.
No database reset/migration, secret/env edit, APK install, Caddy/Serve service
configuration, scheduled task, power-policy change or deployment was performed.

### 2026-10-22 — Android tap/hold voice and shared composer — 48728a1 + workspace

Scope: implement the user's same-button tap controls / hold-to-record request,
show recognized words in the ordinary editable message field, and send only on
explicit Send. Initial inspection used04c5962; HEAD advanced to48728a1 containing
the earlier startup/PDF work during this task. No commits/resets were performed
by this task; existing work was retained. No future phase or deployment.

Changed behavior/files: Android versionCode26/versionName0.31.1-voice-composer.
`PushToTalkButton` retains native button/keyboard/accessibility actions and owns
the physical tap/hold/up/cancel sequence with a stable gesture callback. A tap
opens controls; a held press starts foreground recognition; release finishes it.
Cancellation and disposal cancel only that capture lease. A late grant/readiness
after release cannot start recording, and an old release cannot stop a new one.
The existing60-second capture and15-second setup/final limits remain.

`AndroidSpeechCapture` requests and forwards optional on-device partial results.
`VoiceController` bounds/fences these memory-only provisional words; final words
retain the original transcript while including the typed prefix in reviewed text.
Over-limit combined wording must be edited before encrypted saving/Send. Partial
and stale/interrupted results never become plain authored input. Existing owner,
conversation/scope, lifecycle, audio focus, language and storage checks remain.

The composer displays partial/final voice wording, routes edits to the voice draft
and treats ordinary Send as explicit review approval. It first saves the exact
approved encrypted draft, then reserves the original voice payload/request ID,
then uses the reviewed-voice HTTP route. Duplicate taps cannot reserve twice; a
storage error blocks HTTP. Included typed text clears only after successful local
reservation and only if it still matches; discard preserves it. Existing advanced
original-word inspection, approval, discard, playback and GET-only recovery stay.
Final transcripts close controls to expose the editor. Controls stay anchored at
the row bottom as partial text grows; a one-line status slot avoids shifting the
held target. README/architecture/voice/HOW-TO guides and CURRENT-STATE updated.

Data/API/prompt changes: none. In-memory OpenAPI still exactly equals the exported
164 paths/216 schemas. Server0021, encrypted journal18, released migrations,
dependencies/locks, original ASR provenance, prompt snapshots and replay unchanged.

Checks actually run/results:

- Existing `VoiceControllerTest`/`ChatViewModelTest` baseline passed before edits.
  Full Android unit run after implementation passed **313 /0 failures /0 skips**
  (306 existing +7 new), including prefix/discard, explicit composer approval,
  exact journal-before-HTTP, duplicate Send, in-flight edit/save failure, early
  release, stale release/result and over-limit editing checks. No inference mock
  was introduced into production code.
- `testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest` passed in
  the initial implementation build. Lint XML: **0 errors /24 warnings**, matching
  the earlier baseline count. Separate validation app/test APK builds passed with
  `-PadaValidationApplicationId=dev.ada.validation.voicecomposer`. Final normal
  build/results and cleanup are appended below after completion.
- Without PostgreSQL configured, `pytest tests/test_voice.py -q` passed28/skipped28
  in34.21s. A subsequent isolated PostgreSQL17 Docker instance on loopback55422
  ran **56 passed /0 skipped in87.10s**, including both database variants. One
  existing Starlette/httpx deprecation warning in each run. The database/provider
  were disposable/synthetic; no application DB or native model was used.
- Separate headless Medium_Phone_API_37.0/emulator5584 and validation APK exercised
  actual touch, real authenticated HTTP, Compose and Android Keystore against the
  disposable server. The initial successful held-flow stage took6.945s; its next
  cancellation stage failed9.325s because a cancelled long gesture was treated as
  release. Replaced reliance on combined-click press completion with explicit
  physical Up/cancel handling. The subsequent five-stage run passed:
  hold/edit/Send8.986s, cancelled/early release6.442s, tap Record/advanced review/
  lineage/playback12.856s, confirmed discard7.115s, public preview6.509s.
- A later expanded multiline/IME attempt timed out11.284s before the recorder
  callback. Added explicit draft-recovery completion and stable microphone bounds
  before test presses, so the fixture does not press during keyboard movement.
  Final four-line partial/IME/Send stage passed9.600s; cancel/early release passed
  6.975s. Final physical short tap plus semantic long-click/public preview passed
  7.890s. Semantic long-click opens controls without a physical capture/Up lease.
  These earlier failures remain failures, not relabeled native-device passes.
- Ruff lint/format of `src tests migrations scripts` passed283 files; whitespace
  check and exact in-memory OpenAPI equality passed.157 local links across the
  five changed product/developer guides resolved in the intermediate link audit.

Skips/remaining target verification: no S24 FE install/native recognition/audio,
actual on-device partial-result availability, permission-dialog hold behavior,
human TalkBack, large-font/landscape acceptance or real-model inference this task.
The on-device engine may finalize on silence and is not guaranteed to provide
partial results. No full backend suite/admin-web regression beyond the scoped
voice checks; server schemas/auth/provider/contracts were unchanged. Prior
physical evidence remains historical and does not verify this new interaction.

Operations: all device actions targeted the separate emulator APK; the connected
physical phone and its normal ADA data/permissions were untouched. Every runner
attempt removed its owned PostgreSQL container and validation app/reverse/schema
in finally cleanup. No .env/secret/account, live database/API/proxy/Tailscale,
startup tasks or power-policy changes. Final normal output restoration and owned
emulator cleanup are recorded below.

Final completion: normal `testDebugUnitTest lintDebug assembleDebug
assembleDebugAndroidTest` passed again after the final gesture/layout changes.
Final XML:313 tests/0 failures/0 errors/0 skips; lint0 errors/24 warnings. AAPT
verified the normal artifact is `dev.ada.assistant.debug`, versionCode26,
versionName0.31.1-voice-composer, target/compile36, rather than the validation ID.
No installation was performed on the physical phone. Confirmed the owned
emulator5584's Medium_Phone_API_37.0 identity before stopping it. Validation
package/reverse listings were empty; no owned PostgreSQL containers or listeners
remained on55422/18423/19822/5584/5585. The normal API/proxy/database and phone
were not stopped. Updated usage and local implementation are complete; native
S24 FE recognition/partial words/permission/TalkBack acceptance remains pending.
Final Ruff lint/format283 files and `git diff --check` passed;225 local links
across the eight changed documentation/status files resolved.
