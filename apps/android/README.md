# ADA Android chat, memory, documents and identities (Phase 09)

This Compose/Material 3 app verifies an issued ADA bearer credential with real
`GET /v1/me` and `GET /v1/capabilities`, then provides owned conversation
selection/creation, paginated history, complete chat replies, exact-request
recovery and source cards. Three light/dark palettes and system-scaled typography
remain available. Phase 07 adds owned memory browsing, exact evidence selection,
explicit Remember/correction previews and encrypted write recovery, plus new
static personality profiles. Existing profile editing, automatic extraction,
streaming, voice, tools and device inference remain later selected phases.
Phase 08 adds owned UTF-8 text/Markdown import, immutable version/status/chunk
reads, explicit encrypted upload recovery and request-frozen imported source cards.

Production transport is `HttpAdaApi`, injected through `AdaApi` into the
chat ViewModel. Test-only mocks and canonical server fixtures never enter
the app's main source set. There is no database, Ollama or provider connection.
The document path requires server migration 0005 and advertised document
capabilities. Existing claim-only chat stays compatible; document retrieval
requires the explicitly selected v4 saved prompt. This task does not install 0005
on the application database or deploy the app.

## Appearance settings

Open **Settings → Appearance** from the connection screen. Changes apply
immediately across the app, including Settings, cards, inputs and system-bar icon
contrast. Each palette has matching light and dark colors:

| Palette | Base color | Default |
| --- | --- | --- |
| Oxford Blue | `#002147` | Yes |
| Dark Red | `#350616` | No |
| Olive Green | `#3C4C24` | No |

The **Dark mode** switch works with every palette. The palette and dark-mode
choice are saved locally across app restarts; new installations start with
Oxford Blue in light mode. An absent or unrecognized palette key falls back to
Oxford Blue. Appearance preferences contain only the palette key and a boolean;
credentials and ADA data remain outside this store. Android backups stay disabled.
Colors use [Material 3 semantic roles](https://developer.android.com/develop/ui/compose/designsystems/material3)
and do not follow dynamic wallpaper colors, so the selected palette remains consistent.

## Reproducible tools

| Tool | Pinned version |
| --- | --- |
| JDK runtime/toolchain | Eclipse Temurin 21.0.12.1+1; `.java-version` 21.0.12.1 |
| Java/Kotlin output bytecode | 17 |
| Gradle | 8.13; wrapper distribution and JAR SHA-256 verified |
| Android Gradle plugin | 8.11.1 |
| Kotlin / Compose compiler / serialization plugin | 2.2.21 |
| Compose BOM | 2025.10.00 |
| SDK / build tools | compile 36, target 36 / 35.0.0 |
| Minimum SDK | 26 |
| OkHttp / kotlinx serialization / coroutines | 4.12.0 / 1.9.0 / 1.10.2 |
| AndroidX runner / JUnit extension / Espresso | 1.7.0 / 1.3.0 / 3.7.0 |

The application ID is `dev.ada.assistant` (`dev.ada.assistant.debug` for debug).
The user's Samsung S24 FE runs Android 16, which meets minSdk 26. Physical-phone
installation and behavior are still unverified. The catalog pins all direct
dependencies, while settings/buildscript/app Gradle lockfiles pin resolved
dependencies. No dynamic version or automatic JDK download is used. Gradle checks
the runtime major version; explicitly select the pinned JDK instead of Android
Studio's bundled JBR (the installed Studio bundles JDK 25).

Compatibility was checked on 2026-10-08 against the official
[AGP 8.11 compatibility table](https://developer.android.com/build/releases/agp-8-11-0-release-notes),
[Kotlin Gradle/AGP compatibility table](https://kotlinlang.org/docs/gradle-configure-project.html),
[Gradle Java compatibility](https://docs.gradle.org/current/userguide/compatibility.html),
[Compose compiler setup](https://developer.android.com/develop/ui/compose/setup-compose-dependencies-and-compiler),
[Compose BOM mapping](https://developer.android.com/develop/ui/compose/bom/bom-mapping),
[Kotlin serialization](https://kotlinlang.org/docs/serialization.html) and
[Android network security](https://developer.android.com/privacy-and-security/security-config).
The [AndroidX Test release notes](https://developer.android.com/jetpack/androidx/releases/test)
confirm Espresso 3.7.0's public InputManager access fix; Compose's old transitive
Espresso 3.5.0 failed on the installed API 37 emulator, so the compatible test
dependency is explicitly pinned to 3.7.0.
The compatible pin set is deliberate; availability notices do not authorize an
unrelated dependency upgrade.

## Windows build

Use PowerShell 7, JDK 21, Android SDK Platform 36 and Build-Tools 35.0.0 with accepted
SDK licenses. From the repository root, adapt your local installation paths:

```powershell
$env:JAVA_HOME = 'C:/Program Files/Eclipse Adoptium/jdk-21.0.12.101-hotspot'
$env:ANDROID_HOME = "$env:LOCALAPPDATA/Android/Sdk"
Push-Location apps/android
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug
Pop-Location
```

Android Studio may create an ignored `local.properties`; Windows drive colons
must be escaped in that Java properties file, for example
`sdk.dir=C\:/Users/your-user/AppData/Local/Android/Sdk`. Do not commit machine paths,
signing keys or tokens. On Linux/macOS use `bash gradlew` with the same tasks.
Release compilation is `assembleRelease`; this produces an unsigned artifact and
does not distribute a release. Refresh locks only when deliberately changing the
catalog: `gradlew.bat resolveAndLockAll testDebugUnitTest lintDebug assembleDebug
assembleRelease --write-locks`. The lock task resolves the relevant build/test
dependency graphs rather than ambiguous internal AGP artifact configurations.

## Connection and credentials

Keep ADA's default `127.0.0.1:8000` bind and one Uvicorn worker. In a debug build:

- Emulator: enter `http://10.0.2.2:8000`.
- USB phone: run `adb reverse tcp:8000 tcp:8000`, then enter
  `http://127.0.0.1:8000`. Remove the mapping with `adb reverse --remove tcp:8000`.
- HTTPS: use the real trusted ADA server URL. The base URL must be an origin,
  without credentials, path prefixes, query strings or fragments.

HTTP is accepted only for `10.0.2.2`, `127.0.0.1` and `localhost` in debug resources
and input validation. Release resources forbid cleartext for all hosts. TLS
verification uses the platform defaults; there is no trust-all certificate or
hostname override. Credential-bearing redirects and automatic connection retries
are disabled. Requests have 10s connect, 60s read and 65s total timeouts.
Every POST has a fresh one-shot body: the
[pinned OkHttp follow-up behavior](https://raw.githubusercontent.com/square/okhttp/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/http/RetryAndFollowUpInterceptor.kt)
can otherwise repeat `503` with `Retry-After: 0` even when connection retries are
off. Explicit retries create another body with the same reserved UUID/bytes/options.

Token input is masked and cleared on submission. Tokens never enter state bundles,
appearance preferences or logs. `AndroidSessionStore` encrypts a bounded atomic
record with an [Android Keystore](https://developer.android.com/privacy-and-security/keystore)
AES-256-GCM key under `noBackupFilesDir`; it stores
the verified normalized server/owner credential and at most one exact pending
message, memory write and document upload. File and directory commits complete before network submission. There is
no plaintext fallback. Missing keys, tampering, unknown local formats or reinstall
discard unusable state and require reconnect. The activity blocks screenshots;
cloud backup and device transfer explicitly exclude app data, following the
[Android backup controls](https://developer.android.com/identity/data/autobackup).

Logout and ordinary account/server switching clear private drafts, caches and the
encrypted journal, fencing late results. An explicit **Replace token for this
account** action re-verifies the same owner/server before retaining a pending
reservation. Restoring a saved session also checks `/me` and capabilities before
reading its pending outcome; a saved local owner is never authorization.

Untrusted error bodies are discarded by real transport; only a fixed allowlist of
protocol codes influences recovery wording. The app maps HTTP statuses to fixed
messages, stops at a rejected token and never substitutes fixtures.
Typed error DTOs describe code or validation-list envelopes for contract tests.
A transport timeout is an unknown transport outcome, not a persisted request
failure. Chat recovery queries the original request ID with bounded polling and
respects numeric/HTTP-date Retry-After. It does not stream or cancel generation.

## Conversations, recovery and sources

Choose an owned style and an existing scope, or explicitly choose **New personal
scope** when creating a conversation. A new chat style can be created with the
current default expression settings; it does not edit existing conversation
snapshots. Profile/conversation creation has no server idempotency key: an ambiguous
failure refreshes the list and requires review instead of automatically repeating POST.
An older saved prompt has an explicit confirmed update action affecting future replies.

History pages retain server ordering and merge by event ID. The composer counts
Unicode code points (maximum 4,000), supports the existing memory option and an
advanced timezone-aware historical instant with millisecond precision. Before
Send, the app allocates a UUID and encrypts its exact conversation/content/options
with the verified account/server. A second tap, rotation or navigation cannot
create a second submission. Drafts survive rotation/navigation in ViewModel memory;
only the submitted recovery payload survives process death.
On short windows the context/recovery panels join the scrollable history. While
typing, the composer uses the available space and nonessential navigation chrome
is hidden; dismissing the keyboard restores it. The activity follows Android's
[IME resize setup](https://developer.android.com/develop/ui/compose/system/setup-e2e)
and [consumed Scaffold insets](https://developer.android.com/develop/ui/compose/system/material-insets).

After connection loss/restart, the same ID is queried: running waits, completed
reconciles once, failed offers explicit original-payload retry, and missing offers
explicit same-ID submission. A changed draft becomes a consciously new UUID;
stale-history/ID conflicts require review. A 401 stops automatic recovery and hides
private loaded state. Polling never automatically repeats a message POST.
If a completed reply is received but local journal removal fails, Send stays
blocked and **Check request** re-reads that same ID before trying cleanup again.

Replies and source quotes are selectable literal text; fenced code/Markdown are
displayed as text. Only explicit HTTP(S) link buttons open a browser; credentialed
URLs, executable schemes, HTML actions and remote previews are rejected. Source
chips resolve against the same request's returned citation cards, including after
history reload. Unknown labels/legacy missing cards are unavailable. Exact quotes,
version/origin and validity remain intact; optional Details show IDs/hashes/UTC
milliseconds. Selected but uncited context is in a separate retrieval detail view.
Source provenance does not guarantee truth or answer correctness.

## Explicit memory and static personality (Phase 07)

Open **Memory**, choose an owned scope and browse current statements, a timezone-
bearing date or all history. Pagination stays on the server. Effective intervals
are half-open; a superseded record can still be current before a future correction.
History describes valid time rather than reconstructing what ADA knew at a date.
Overlapping different values are competing assertions, never a truth ranking.
Detail shows the exact quote/full source version and an available replacement link.

**Remember** accepts a user note or a selection from an owned user source, plus
subject, predicate, value, kind and optional effective bounds. Existing source
text is read-only; selection preserves emoji, combining marks, CRLF and non-Latin
text without normalization. Model-generated sources cannot support user writes.
Review the annotation and quote, then press **Save** to explicitly endorse it.
Corrections preview the old/new values, effective time and new evidence, then use
the real atomic supersede endpoint. Source editing/deletion and automatic
extraction are unavailable.

Before any POST, the app encrypts the exact source/claim IDs and input. After the
note succeeds it durably records that returned source version before submitting
the claim. A failed second step can leave a raw note; it is not reported as a
saved claim. Restart verifies the owner/server and offers **Check saved write**
or **Resume with original IDs**, with no automatic memory POST. Resume uses identical
payloads and server replay fingerprints, including a committed claim subsequently
corrected by another client. 409/422 retain the reservation and actionable review
state. A failed journal cleanup blocks another write. Explicitly discarding local
recovery preserves input for editing and never deletes remote notes or claims;
review owned history before knowingly creating a new assertion.

The bounded encrypted record is now v2 (128 KiB maximum plaintext). It reads the
existing v1 credential/chat journal with the same file/key/AAD, then writes v2
on the next update. Downgrading to a v1-only app requires reconnecting. Both
journals remain bound to verified server/owner, with memory additionally bound to
scope. They coexist during chat and explicit memory writes; logout/switch/401
clear both. Unsubmitted form drafts remain only in ViewModel memory through
rotation/navigation, not process death or Android saved-state bundles.

**Settings → New chat style** exposes name, direct/conversational/formal,
reserved/warm and concise/balanced/detailed. Create a new server profile and select
it for a new conversation. Existing chats keep their frozen style and prompt;
their active saved style/scope remains visible. Ambiguous profile creation requires
refresh/review because that endpoint has no idempotency key. Appearance preferences
remain local expression settings and grant no knowledge permissions.

## DTO and state boundaries

`data/Contract.kt` preserves UUIDs, Long UTC milliseconds, exact evidence text,
hashes, source versions, request options, citations and retrieval snapshots. All
existing client endpoint adapters are typed. This UI uses authentication,
capabilities, owned profiles/scopes/conversations/events, chat/request status,
explicit prompt updates and per-request source reads. Unknown JSON fields are ignored;
wire enums remain strings and
an unknown request status maps to `Unknown`, never `Completed`. Unknown capabilities
do not enable controls. Legacy responses can omit optional citation collections.
Document cards have a separate typed collection with D labels and no fabricated
claim IDs. Document use defaults off, and false is omitted from the chat network
payload to preserve the older claim-only wire shape.

`utf16ToCodePointOffset` and `codePointToUtf16Offset` explicitly bridge Android
selection indices and ADA evidence spans. They preserve combining characters,
CRLF and emoji and reject selection boundaries inside a surrogate pair. Input
instants remain timezone-bearing ISO strings; output milliseconds remain Long.
No whitespace normalization is applied to evidence.

`ChatViewModel` follows action → injected API/store → typed result → StateFlow,
using the [ViewModel lifecycle](https://developer.android.com/topic/libraries/architecture/viewmodel)
to retain drafts across activity recreation;
`ChatState` separates drafts, immutable submitted payloads, status and history.
Private caches/journals include normalized server and verified owner, plus request
and conversation where applicable. Phase 03's state map remains a historical
foundation; Phase 07 enables the owned Memory destination. UI labels use ordinary words; private text
is rendered as Compose text and never executed.

## Immutable imported documents (Phase 08)

**Documents** is enabled only for `document_uploads` and
`document_ingestion=text_markdown_v1` on the verified server. Choose an owned scope,
then select a `.txt`, `.md` or `.markdown` file with Android's document picker or
paste exact text. The mobile limit is **64 KiB**, stricter than the server's 256 KiB.
Reading is bounded and strict UTF-8; CRLF, BOM, combining characters and emoji are
preserved. The picker reads a content URI and display metadata, never treats the
filename as a filesystem path, and needs no broad storage permission.

Review the exact text, scope, availability and reserved IDs, then press
**Upload reviewed document**. Availability is a version's accessibility interval,
not a truth interval or endorsement of every sentence. The app reads real
processing/ready/failed receipts; failed or incomplete versions never appear as
searchable evidence. Details verify parsed-text/raw hashes, chunks and exact
code-point spans before displaying verified content. **Upload a new version**
retains the stable source ID and allocates a new upload ID. **All immutable
versions** reads exact prior versions rather than replacing them with latest text.

Before POST, the exact bounded bytes (base64 within encryption), filename/type,
availability, upload/source IDs and owner/server/scope binding commit to the
Keystore-backed journal. The encrypted **v3** record is bounded at **256 KiB** and
reads prior v1/v2 records with the existing key/file/AAD. All three journals coexist;
token rotation retains them only after the same owner/server is reverified.
Logout, account/server changes, tampering and key loss clear or fail closed.
Restoration offers **Check saved upload** or explicit **Resume with original bytes
and IDs**, never an automatic upload. Unknown/mismatched or incomplete receipts
retain recovery; ready-state cleanup failure blocks another upload. Discarding
local recovery does not delete remote documents, and keeps exact input for review.

In **Message options**, **Use imported documents** is off by default. It needs
document retrieval/citation capabilities, saved memory enabled and a v4 conversation
prompt. Existing v1/v2/v3 conversations retain their saved prompt until the explicit
audited update action is confirmed. `[D1]` source cards show imported/untrusted
origin, filename, immutable version, line location, availability and exact excerpt.
They resolve only against the original request's frozen cards, including after
reupload or history reload. Original `[M1]` claim cards and conflicts stay separate.
PDF, OCR, archives, embeddings, extraction and statement promotion remain deferred.
See [document API/storage/limits](../../docs/DOCUMENT-INGESTION.md).

## Emulator verification

With a booted emulator and the repository's Python environment installed:

```powershell
Push-Location apps/android
.\scripts\verify-emulator.ps1 -Device emulator-5554
Pop-Location
```

The script builds and installs debug/test APKs, starts the repository's test-only
HTTP helper on loopback port 18764 using a disposable migrated SQLite database,
and pipes a random temporary token into an app-private test file. It does not put
the token in arguments, logs or committed fixtures. Instrumentation exercises
real authenticated `/me` and `/capabilities`, rejected credentials and the
connection/chat/source UI, then deletes the temporary credential and stops the
helper. The explicit `--android-chat-fixtures` flag adds a synthetic owned style,
scope and user-backed claim plus a deterministic fake-provider reply. It exercises
actual server generation/reservation/replay APIs without Ollama or production
data. The ordinary suite also simulates loss of the HTTP response after an actual
server commit, retaining the original journal across navigation. Two separate
instrumentation stages then leave a committed reply journaled, force-stop the
app with adb, and cold-restore through the production activity. Recovery verifies
the original request, one server attempt, the same event pair and original sources
without another Send. The default helper remains unchanged for web tests.
Phase 07 adds four real-HTTP memory tests, four synthetic Compose memory/profile
flows and two more Keystore invariants. Two additional staged memory checks save
a real note, simulate failure before claim submission, force-stop the app, then
restore through MainActivity and explicitly resume the original IDs without a
duplicate note or claim. Long Unicode evidence and correction validation are
exercised through the restored UI. All model replies in this helper are fake.
Port 18764 must be free.

Plain `gradlew.bat connectedDebugAndroidTest` runs the UI smoke; the authenticated
HTTP tests explicitly skip unless their helper prerequisites are provisioned.
The four chat/memory force-stop stages require the script's explicit staging arguments.
Use the script for a complete HTTP integration run. A physical-phone smoke with
the actual server/connection method, TalkBack, hardware-keyboard traversal, large
display settings and long content still needs target verification. The script
targets the selected `ANDROID_SERIAL` and restores the caller's environment.
Phase 08 adds two real-HTTP document checks and one production Compose paste,
preview, explicit upload and detail check. Two further stages commit a real
upload, simulate delivery loss, force-stop the app, restore through MainActivity
and explicitly replay identical bytes/IDs. They verify one immutable version and
real request-frozen imported source cards. All helper replies remain explicitly fake.

## Historical Phase 03 checks (2026-10-08, Windows 11)

- JDK 21.0.12.1+1, Gradle 8.13, SDK 36 revision 2 and Build-Tools 35.0.0.
- `resolveAndLockAll testDebugUnitTest lintDebug assembleDebug assembleRelease
  --write-locks`: passed; 15 unit tests, no failures/skips; lint 0 errors and
  14 dependency availability warnings; unsigned release compiled.
- After the test-tool fix, `testDebugUnitTest lintDebug assembleDebug
  assembleRelease` passed again using the committed locks without `--write-locks`.
- Unit coverage includes actual current/legacy/additive server fixtures, future
  fields/enums, 64-bit times, exact Unicode spans, HTTP authentication/status
  sanitization, no fixture fallback, redirect refusal, reserved POST payloads,
  timeout without automatic retry, revoked credentials and late account switching.
- The installed `Medium_Phone_API_37.0` emulator reports Android 17/API 37 and
  uses WHPX. `scripts/verify-emulator.ps1` passed all 3 instrumentation tests,
  0 failures/0 skips, and launched the actual debug activity (`Status: ok`, cold
  launch). Tests cover input labels, invalid server URL, real HTTP 401 display,
  dark/larger-text previews and authenticated real ADA `/me`/`capabilities`.
- The final emulator run (2026-10-08 22:00:30 UTC) repeated those 3 checks in
  landscape with system font scale 1.5 and passed. Caller environment restoration
  was verified; font/rotation were restored after the check. This basic smoke is
  separate from a full TalkBack, hardware-keyboard and physical-phone review.
- `aapt2 dump` verified the packaged release's cleartext base is false and it has
  no debug host exceptions. The debug APK contains exactly the three documented
  HTTP hosts. The release manifest targets SDK 36 and disables backup/cleartext.
- During scaffolding, initial fixture resource wiring, MockWebServer's IPv6 host,
  internal AGP lock resolution, a local Windows property escape, transitive
  Espresso 3.5's removed InputManager API and an unquoted PowerShell Gradle
  property argument failed checks; each was corrected and the checks rerun.
  No test/lint error was suppressed.

Physical Samsung S24 FE, release HTTPS, TalkBack, visual/IME review and real-model
evidence are still pending; successful scaffolding is not a finished Android chat
release. The headless test emulator and disposable HTTP helper were stopped after
verification; the debug APK remains available under the ignored build output.

## Appearance follow-up checks (2026-10-08, Windows 11)

These checks supplement the Phase 03 evidence above:

- Before this change, `testDebugUnitTest lintDebug assembleDebug` passed.
- Final `testDebugUnitTest lintDebug assembleDebug assembleRelease --console=plain`
  passed with unchanged dependency locks: 15 unit tests, 0 failures/skips; lint
  0 errors and the existing 14 dependency availability notices. A new KTX editor
  suggestion was resolved using the already installed extension.
- `scripts/verify-emulator.ps1 -Device emulator-5554` passed all 3 tests without
  skips on Android 17/API 37 and cold launched the debug activity. The updated
  appearance smoke checks default selection, palette switching, dark mode and
  persisted selection after activity recreation; real HTTP checks also passed.
- The final appearance smoke alone passed at 2026-10-08 23:59:20 UTC in landscape
  with system font scale 1.5, including selection of all three palettes in both
  modes. Command: `connectedDebugAndroidTest` with
  `-Pandroid.testInstrumentationRunnerArguments.class=dev.ada.assistant.FoundationSmokeTest#launchesLabelsInputsAndThemePreview`.
  Font scale and rotation were restored afterward.
- A local WCAG relative-luminance calculation checked palette text/background
  pairs and control outlines. Minimum text ratios: Oxford Blue 6.38:1, Dark Red
  6.42:1, Olive Green 5.59:1; minimum outline ratios: 3.77:1, 3.98:1 and 3.48:1.

Samsung S24 FE/Android 16 appearance, TalkBack, keyboard and visual/IME review
remain target checks. No physical-phone installation or deployment was performed.

## Historical Phase 04 checks (2026-10-09 UTC, Windows 11)

- Prerequisites/source/OpenAPI were inspected before changes. Android baseline:
  15 unit tests/lint/debug build passed. Baseline Python `pytest -q`: 64 passed,
  52 skipped because PostgreSQL was not provisioned and SQLite lacks row locks;
  Ruff lint/format passed for 38 files. Earlier evidence above remains historical.
- Final `testDebugUnitTest lintDebug assembleDebug assembleRelease --console=plain`
  passed with unchanged dependency pins/locks: 57 unit tests, no failures/skips;
  lint 0 errors/14 existing dependency availability notices. Both APKs are version
  `0.4.0-chat-mvp` (code 2); release is unsigned, not distributed.
- Unit coverage includes 28 ViewModel invariants, 12 real MockWebServer transport
  cases, 9 encrypted-store invariants, 4 contracts and 4 historical connection
  tests. New checks cover journal ordering/failure, UUID/payload retries, Unicode,
  bounded status recovery, logout/switch races, key loss, prompt-update feedback
  and preservation, legacy/unknown sources and one-shot POST replay prevention.
- Complete `scripts/verify-emulator.ps1 -Device emulator-5554` runs passed all
  11 ordinary instrumentation tests plus two separately invoked recovery stages
  separated by an actual adb force-stop, with no skips and successful cold launch.
  The small landscape run used the Android 17/API 37 emulator at density 540
  (1080×2400 physical pixels, smallest width 320dp), rotation 1 and font scale 1.5.
  Settings were restored to font 1.0, density 420, automatic rotation 1/user 0.
  The final normal-layout run at 2026-10-09 09:04:54 UTC passed all 11 ordinary
  tests plus both force-stop stages/cold launch using those restored settings.
- Integration used actual authenticated ADA HTTP and migrated disposable SQLite
  with explicit synthetic evidence and FakeProvider. One test simulates response
  delivery loss after a real commit; the staged process recovery verifies original
  request ID, attempt 1, stable event pair/cards and journal removal without Send.
  The tests also exercise owned/personal conversations, resume, draft recreation,
  validation focus, literal unsafe markup, unknown source labels and all palettes.
- Required server gate: `scripts/test-postgres.ps1` passed 116 tests/2 expected
  SQLite-only lock skips/1 existing Starlette/httpx warning; Ruff lint/format
  passed for 39 files. Eight server/OpenAPI/migration hashes matched the baseline.
  Packaged release backup/transfer and cleartext policy were inspected with aapt2.
  The temporary credential/synthetic journal and disposable HTTP listener were
  removed/stopped, settings restored and the session-created emulator shut down.
- Initial compile/annotation and UI scroll/IME timing failures were corrected and
  rerun, not suppressed. The immediate-503 replay regression and two prompt-update
  feedback tests failed before their fixes. See STATUS/WORKLOG for run history.

Pending target verification: physical Samsung S24 FE/Android 16 (not attached),
actual-server network interruption, token rotation/logout, verified release HTTPS,
real Ollama with known explicit memory/source cards, TalkBack, hardware keyboard,
manual visual/IME/copy-selection review and API 26 behavior. Automated emulator
focus/labels/scrolling do not substitute for those checks. Web checks were skipped
because this phase changes no web behavior. No signing, deployment, later phase,
production-data migration or real-model performance/battery claim is included.

## Phase 07 checks (2026-10-09 UTC, Windows 11)

- Current source/OpenAPI/scoped instructions and Phase 04 prerequisites inspected;
  ordinary Python baseline 87 passed/69 skipped, Android baseline tasks succeeded
  with unit/lint tasks cached. No backend or dependency change was needed.
- Final `testDebugUnitTest lintDebug assembleDebug assembleRelease
  assembleDebugAndroidTest`: **98 unit tests passed, 0 skips**, lint **0 errors/14
  existing dependency notices**, debug, unsigned release and test APKs built.
- Final `scripts/verify-emulator.ps1`: **21 emulator tests passed, 0 skips**, then
  **2 chat + 2 memory actual force-stop stages passed**. Android 17/API 37/WHPX,
  small 480×320 dp landscape and font scale 1.5. Four new Compose tests use explicit
  synthetic API/storage; four new memory tests use real authenticated HTTP against
  migrated disposable SQLite. FakeProvider replies remain explicitly fake.
- Real HTTP covers note/claim/correction identical replay and changed-ID-input
  conflicts, exact multilingual/emoji/combining/CRLF evidence, unauthorized ID
  guesses, model source rejection, correction boundaries including the old end,
  future current/as-of/history and original saved request citation preservation.
  Recovery commits a real note, simulates failure before claim POST, force-stops,
  then restores through the production activity and explicitly resumes exact
  source/claim IDs once. Long evidence and validation focus also passed.
- Initial emulator run was 19 passed/2 failed: focus loss collapsed the readonly
  selection before preview and keyboard dismissal raced navigation. Both were
  fixed and the full checks rerun. Regression tests also caught late 401 handling,
  corrected-after-commit replay and newly created profiles beyond page one.
- Backend dedicated PostgreSQL suite **152 passed/4 documented skips**; Ruff lint
  and format passed (48 files). **31/31** captured server/OpenAPI/migration/lock/
  catalog files are unchanged from the phase starting tree. Release APK inspection
  confirms versionCode 3/name 0.7.0-memory, target 36, backup/cleartext disabled,
  no release HTTP exceptions; debug retains exactly its three allowed hosts.
- At 22:30:46 UTC the temporary test credential was absent, disposable HTTP
  listener stopped, display/font settings reset and task emulator shut down.

Physical S24 FE/Android 16, API 26 behavior, trusted release HTTPS, TalkBack/manual
visual/hardware-keyboard checks and actual-server/Ollama/network-loss verification
remain pending. No deployment, signing/distribution or later feature was performed.
See [STATUS](../../plans/STATUS.md) and [WORKLOG](../../plans/WORKLOG.md) for checkpoint
mapping, actual failures/checks/skips and preserved earlier evidence.
## Phase 09 scoped entities and aliases

App version `0.9.0-entities`/code 5 adds **People, projects and aliases** from
Memory. The current server must support scoped identity writes; legacy servers
keep these controls disabled. Choose an owned scope, check names for collisions,
review new entities/aliases/renames/self/claim links, preview a same-scope merge and
confirm it separately. Undo retains the lineage. Names grant no permissions.

The existing encrypted record is v4/256 KiB, with one exact entity operation
journal alongside chat, memory and document journals. Recovery verifies the
server/owner, never automatically submits, and supports checking the frozen
receipt or explicitly resuming identical input. Saved source cards retain their
request's canonical interpretation; retrieval details show frozen ambiguous choices.
See [identity policy](../../docs/ENTITIES-AND-ALIASES.md) and
[STATUS](../../plans/STATUS.md) for executed checks and physical S24 FE/Android 16,
HTTPS, TalkBack and real-model verification still pending.
