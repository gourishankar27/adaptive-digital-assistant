# Phase status

Recorded 2026-10-09 UTC. Update after implementation and verification.
“Planned” means a specification exists, not that code or a working UI exists.

| Phase | Status | Evidence / next gate |
|---|---|---|
| 00–02 | Implemented baseline | Packaged Linux run: 60 passed/50 skipped. User's Windows PostgreSQL run: 105 passed/3 fixture failures/2 skipped. Real chat reported by user. |
| 02A | Target gate verified | Prior Linux: 61 passed/50 skipped, four installer tests, Ruff passed. This Windows baseline: 61 passed/50 skipped; dedicated PostgreSQL 109 passed/2 expected SQLite lock skips. |
| 03 | Checkpoints A–C implemented; local verification passed | Typed/exported API and 47 synthetic fixtures; Android/web HTTP, connection/state/design foundations. Windows/PostgreSQL 114 passed/2 expected skips; final affected contract rerun 5 passed. Ruff passed. Android 15 unit + 3 emulator tests, lint/debug/unsigned release builds; web 28 unit + 3 Chromium browser tests, clean install/typecheck/lint/build. Physical phone and manual accessibility/HTTPS checks remain. |
| 04 | Checkpoints A–D implemented; local verification passed | Keystore credential/exact journal, owned conversations/history/chat, identity-verified recovery, explicit retries and original sources. Android 57 unit tests, lint/debug/unsigned release builds, 11 emulator tests + 2 actual force-stop stages passed in small landscape at 1.5× text. PostgreSQL/SQLite 116 passed/2 expected skips; Ruff passed. Physical phone/HTTPS/manual accessibility/real-model verification remains pending. |
| 05 | Planned | Phase 03; explicit server admin authorization. |
| 06 | Planned | Phase 05 metadata API; real browser/backend integration. |
| 07 | Planned | Phase 04; exact evidence and correction flows. |
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
Phase 05 can be separately selected for server admin authorization. Phases 05/06
and the later feature phases remain planned, with no deployment.
If work is incomplete, record the checkpoint and exact blocking condition; keep
the usable earlier feature active. Missing device/database checks stay visible.

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
