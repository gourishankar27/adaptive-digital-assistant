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
