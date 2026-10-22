# ADA Android chat, memory, tools, episodes and interaction learning (Phase 17)

Phase30 app24 /0.30.0-work adds **Projects & next actions** from the chat menu and
Settings, plus requested **Save next action** on completed replies. Goals/tasks,
source review, revision history, project/day briefs and separately consented
questions/reminders use authenticated HTTP. Capability `ada-work-v1` gates the UI;
server schema0020 is required. Journal17 reads v1–v16 and encrypts exact work
operations before POST; restart checks only GET receipts. No direct provider/DB
access, inferred commitments or background push. See
[usage, limits and separate validation APK commands](../../docs/PROJECTS-AND-FOLLOW-THROUGH.md).
Physical layout/TalkBack and human usefulness remain separate target checks.

Phase29 app23/0.29.0-speech-study adds **Engine & model details** and an explicit
public **Preview voice** under the microphone controls. Platform ASR/offline TTS
remain; no candidate runtime/model/importer is enabled. The pure manifest checker
verifies pinned metadata/bytes without installation or activation. Default voice
selection requires an en-US match or an explicit voice choice. Journal16 and all
authenticated HTTP contracts are unchanged. See
[study, usage and isolated validation commands](../../docs/NATURAL-LOCAL-SPEECH.md).
S24 FE quality/resource/focus/permission measurements remain pending; no normal
phone installation or deployment is included.


Phase28 adds **While you were away** (Settings/chat menu), source-aware report and
question review, explicit Keep/Discard/Open, policy/source/time/resource choices
and encrypted journal16 exact recovery (v1–v15 readable). App22/0.28.0-reflection
uses authenticated ADA HTTP only. Model summary generation is disabled. See
[the guide](../../docs/IDLE-REFLECTION-AND-DREAM-REVIEW.md) and root STATUS/WORKLOG
for actual emulator checks and remaining physical/quality gates. No normal phone
installation is part of this change.


## Phase27 reminders and inbox

App21/0.27.0-scheduling adds **Reminders & inbox** under chat menu/Settings:
explicit owner consent, owned scopes, once/daily/weekly editor, DST/quiet-hour
preview and confirmation, pause/edit/snooze/delete/reauthorize, paged receipts and
inbox acknowledgement/opening. Opening never submits a user turn. Journal15
preserves v1–v14 and exact pending operations before POST; restart checks with GET
only, with explicit original retry. Late identity/scope/page callbacks are fenced.
Polling runs while foregrounded; no push provider, notification permission or
background delivery service is added. Global dispatch and owner consent default
off. See [usage and isolated emulator validation](../../docs/DURABLE-SCHEDULING-AND-REMINDERS.md).
Normal app installation and physical verification were not part of implementation.
Earlier version summaries below retain their original evidence boundaries.

## ADA Ambient Intelligence presentation

App19/0.25.1-ambient redesigns the existing Compose UI without changing routes,
authentication, controllers, data/journal formats or server contracts. Fresh
installs default to dark ADA Ambient; saved Oxford Blue/Dark Red/Olive Green and
light/dark choices retain their original preference keys. All four palettes and
light mode are selectable. Shared typography, surfaces, presence, chat treatment,
IME anchoring and expanded navigation retain the working feature flows. See
[audit/design/verification](../../docs/ANDROID-UI-REDESIGN.md). No new migration,
permission, dependency, speech model or app installation is part of this work.

Emulator-only validation uses a separate `dev.ada.validation.redesign` build,
dedicated `ADA_TEST_DATABASE_URL` and an explicit synthetic provider fixture:

```powershell
./gradlew.bat '-PadaValidationApplicationId=dev.ada.validation.redesign' assembleDebug assembleDebugAndroidTest
```

From the repository root with the dedicated test database configured:

```powershell
./.venv/Scripts/python.exe scripts/verify_android_redesign.py --device emulator-5584
```

This exercises the real HTTP adapter. The helper validates the emulator
and separate APK IDs before installing, then removes its APKs/reverse/schema.
Public-only test-host screenshots stay under `.pytest_cache/ui-redesign/screens`;
MainActivity's secure-window protection is never disabled. Use `--suite curiosity`,
`--suite password` or `--suite foundation` for the selected regression flows.
Restore normal APK outputs by rebuilding without the validation property.

## Phase22 password sign-in

Version15/0.22.0-sessions uses server/username/password by default. Keystore v12
persists only refresh material in password mode, with access in memory and no saved
password; v1–v11 journals remain readable. Reopen/foreground renewal verifies the
same owner/epoch and performs GET recovery only. Settings reviews/revokes password
sessions, changes passwords and signs out current/all families. Advanced bearer
mode retains CLI/device compatibility. Follow
[the password guide](../../docs/PASSWORD-LOGIN-AND-SESSIONS.md) for explicit local
enrollment and0016 installation. Physical/release HTTPS checks remain separate.

For the step-by-step current installation, USB connection, feature instructions
and known phone issues, see [HOW-TO-USE-ADA](../../docs/HOW-TO-USE-ADA.md).

This Compose/Material 3 app verifies an issued ADA bearer credential with real
`GET /v1/me` and `GET /v1/capabilities`, then provides owned conversation
selection/creation, paginated history, complete chat replies, exact-request
recovery and source cards. Four light/dark palettes and system-scaled typography
remain available. Phase 07 adds owned memory browsing, exact evidence selection,
explicit Remember/correction previews and encrypted write recovery, plus new
static personality profiles. Phase 16 adds incremental replies, durable stream
recovery and explicit Stop. Existing profile editing, automatic extraction,
external writes and local language-model inference remain later selected phases.
Phase 17 adds reviewed on-device voice input and independent offline TTS.
Phase 21 (versionCode14/0.21.0-connectivity) adds saved named HTTPS server addresses,
explicit switch/clear, reviewed version1 JSON address import and public readiness
checks before login/recovery sends credentials. Open **Saved servers and connection
checks** on the connection screen. Profiles store label/origin only, separately
from Keystore credentials. Standard release TLS and debug-only local HTTP remain;
no QR/deep-link trust, discovery or certificate bypass. Read
[private-network connectivity](../../docs/PRIVATE-NETWORK-CONNECTIVITY.md) for
the Tailscale Serve and direct LAN routes and their separate deployment gates.
Phase 14 adds separately scoped interaction preferences and opt-in bounded session
tone under Settings; saved personality profiles remain unchanged.
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
| ADA Ambient | `#8A6CFF` | Yes |
| Oxford Blue | `#002147` | No |
| Dark Red | `#350616` | No |
| Olive Green | `#3C4C24` | No |

The **Dark mode** switch works with every palette. The palette and dark-mode
choice are saved locally across app restarts; new installations start with
ADA Ambient in dark mode. An absent or unrecognized palette key falls back to
ADA Ambient. Follow system appearance is optional; existing explicit palette/mode
choices stay unchanged. Reduce ambient motion supplements the system animation
setting. Appearance preferences contain only palette/mode/motion settings;
credentials and ADA data remain outside this store. Android backups stay disabled.
Colors use [Material 3 semantic roles](https://developer.android.com/develop/ui/compose/designsystems/material3)
and do not follow dynamic wallpaper colors, so the selected palette remains consistent.

## Interaction preferences and session tone

Settings distinguishes this conversation, its knowledge scope, its chat style,
and deliberately account-wide defaults. Defaults apply to new conversations;
reviewed conversation changes apply to future replies without rewriting saved
personality, prompts or request snapshots. Explicit preferences override temporary
session tone. Tone is off by default, bounded, decaying and expiring; the user can
disable/reset it or explicitly request a gentler/more focused next turn.

Expression journal v8 encrypts the exact operation before HTTP, reads its original
receipt after restart and never automatically submits. v1–v7 remain readable.
An unknown outcome offers check/same-key retry/local discard. Account/server
switching clears private state. The real API requires migration 0011 and advertised
expression-v1 capabilities. There is no automatic mood inference or psychological
score. See [policy](../../docs/INTERACTION-PREFERENCES-AND-AFFECT.md) and
[actual checks/targets](../../plans/STATUS.md). Emulator-only verification:
`./scripts/verify-expression-emulator.ps1 -Device emulator-5556`.

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
basic audio/HTTP/recovery/font behavior was partly verified in the 2026-10-13 UTC
audit; permission/focus hardening and remaining target gates are tracked in
[Phase 17-A](../../plans/phase-17-a-s24-fe-validation-and-hardening.md). The catalog pins all direct
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
respects numeric/HTTP-date Retry-After. This legacy polling path does not stream or cancel generation; Phase 16 uses
the optional stream contract described below.

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

## Phase 11 selected-source review

Version 0.11.0-review adds Memory → Review memory suggestions when the server
advertises selected_sources_v1, memory_review and review-v1 provenance. Select an
owned note or document excerpt, explicitly request suggestions, inspect exact
support/origin/dates/conflicts, save edits and inspect the new revision, then
confirm accept or reject with a decision annotation. Acceptance creates new
explicit endorsement evidence; original model/imported support remains untrusted
and distinguishable. Reviewed cards show User reviewed. No bulk/automatic approval.

Keystore persistence advances to v5 (same 256 KiB bound, v1–v4 readable), with
one unsent private draft and one exact extraction/edit/review operation. Restore
never POSTs. Check the original receipt or explicitly retry identical input after
identity verification; logout/account/server/key loss clears private state.
Inbox/scope pagination is available; source/document/entity/excerpt pickers are
bounded to the first 50 items. The native selector submits one excerpt per
extraction; the API supports four. See
[the server policy](../../docs/MEMORY-PROPOSALS-AND-REVIEW.md).

The existing verify-emulator.ps1 script includes the new real-HTTP review flow
and two approval-delivery-loss stages separated by actual adb force-stop (ten
staged checks including prior chat/memory/document/entity recovery). ProposalOnly
focuses the ordinary proposal UI test while retaining those recovery stages.
The disposable helper labels model extraction as a deterministic fixture; it
never uses the configured application database. Actual final checks and failures
are in [STATUS](../../plans/STATUS.md). Physical S24 FE/Android 16, release TLS,
manual TalkBack/keyboard accessibility and real-device resources remain pending.

The disposable HTTP helper keeps idle sockets alive for 90 seconds to cover UI
review pauses in this emulator environment. Production redirect/POST-retry policy
is unchanged. verify-emulator.ps1 requires Status ok from an actual cold launch;
an exit-zero timeout is a failed smoke check. Real-phone/HTTPS and short-idle
connection behavior remain target verification, distinct from fixture passes.

## Phase 12 read-only tools

Open an owned conversation, then **Read-only tools**. This entry requires the exact
server agent capability/registry and saved v3/v4 compatibility. Task/tool selection
creates a separate run. Review the account, scope, version and exact arguments,
then explicitly approve or deny. Actual receipts distinguish completed, failed,
revoked and unknown outcomes; the final model answer remains untrusted.

Journal v6 extends the existing Keystore/AES-GCM 256 KiB no-backup record; v1–v5
remain readable. Exact run and approval/recovery keys commit before POST. Restore
only GETs the verified owner's run/receipt; it never writes automatically. Normal
chat and source snapshots remain unchanged. No provider/database access or external
integration is added. Server source requires migration 0009, not installed by this
task. See [the policy](../../docs/TOOLS-AND-AGENT-LOOP.md).

Run `scripts/verify-agent-emulator.ps1 -Device emulator-5556` with an existing,
task-owned emulator for focused actual HTTP approval/denial, staged force-stop
receipt recovery and strict cold launch. It rejects physical-device serials and
uses only a disposable fixture server. This does not replace physical S24 FE /
Android 16, HTTPS, TalkBack or target resource checks in STATUS/WORKLOG.

## Phase 13 history and episodes

From an owned conversation open **History & episodes**. Select up to four complete
messages, review exact excerpts, then explicitly queue a summary or pending-memory
suggestion job. The same view offers a scoped lexical index rebuild and paginated
episodes/jobs. Generation requires current server capabilities. Generated labels,
exact original versions and measured states keep interpretation separate from facts.

Version 0.13.0-episodes/versionCode 8 uses encrypted journal v7, with v1–v6 readable.
One exact job reservation is saved before POST; restart only GETs its original key.
Timeouts retain unconfirmed delivery for explicit check/identical retry. Local
discard does not stop/delete server work. Existing palettes and normal chat remain
unchanged. Source head 0010 installation is separate from client builds.

`scripts/verify-episode-emulator.ps1 -Device emulator-5556` verifies actual fixture
HTTP, generated source inspection, staged force-stop recovery and strict cold
launch on a task-owned emulator only. It keeps newly created fixture directories
inside ignored workspace storage. See [policy](../../docs/EPISODES-AND-CONSOLIDATION.md)
and STATUS/WORKLOG for actual runs and physical-phone/release limits.

## Phase 15 reviewed learning and continuity

Open a conversation, then Settings → Interaction learning and continuity. Choose
scope consent, optionally enable source-linked continuity, select completed user
messages and review tentative wording suggestions. The configurable default gate
requires three distinct interactions, never retries/copies or weak guesses.
Approve/edit/reject is explicit. Account reuse is a separate choice carrying only
wording enums into other opted-in scopes. Pause stops reuse; reset deletes live
learned state and discloses retained audit/original sources/historical replay.

Version 0.15.0-learning/versionCode 10 uses encrypted journal v9 with v1–v8
compatibility. Exact learning operations are saved before HTTP; restart checks
receipts only, with explicit check/identical retry/discard. Approved original
evidence remains inspectable until reset. C source cards belong to the original
reply and keep source trust, uncertainty and bounded omissions. Generated episode
summaries remain separate navigation. No automatic classifier or bond score exists.

Run `scripts/verify-learning-emulator.ps1 -Device emulator-5556` for disposable
actual HTTP review/source inspection, process-stop receipt recovery and strict
cold launch. Use the pinned JDK and normal Gradle gates above. Source head **0012**
installation is separate; physical Samsung S24 FE/Android 16, release HTTPS,
TalkBack/network and native-model quality/resource checks remain target work. See
[policy](../../docs/INTERACTION-LEARNING-AND-CONTINUITY.md) and STATUS/WORKLOG.

## Phase 16 incremental replies and Stop

Version **0.16.0-streaming**, versionCode **11**, adds bearer-authenticated OkHttp
SSE only when the server advertises `ada-stream-v1` and generation cancellation.
Older servers retain legacy chat/polling. Source installation needs **0013**;
the application database was not upgraded by this implementation.

Chat labels partial text provisional/incomplete; partial citation labels and links
never create source cards. Stop sends the original owned request/attempt and shows
cancel requested until canonical terminal status. Cancelled requests remain
outside completed assistant history and offer an explicit same-payload retry.
Leaving Chat, switching conversations or backgrounding only detaches the observer.
Returning/foregrounding uses GET of the same request and reconnects after its
checkpoint. Duplicates are ignored; gaps/expired cursors replace partial text from
GET. No reconnect or restart automatically submits or cancels generation.

The encrypted record remains **v9**, retaining v1–v8 compatibility; its existing
exact PendingMessage suffices for stream recovery. Identity/server changes and
401 clear private state; bounded reconnect/backpressure and Retry-After apply.
Run normal unit/lint/debug gates and:

```powershell
.\scripts\verify-streaming-emulator.ps1 -Device emulator-5556
```

The script uses an explicit delayed synthetic provider on 18765, five focused
HTTP UI cases, two actual force-stop recovery stages and strict cold launch.
Compact 900x500/240 dpi/1.5x font verification is recorded separately. Real-model
measurements, native GPU acknowledgement limits, retained partial-text policy and
remaining S24 FE/Android16/HTTPS/TalkBack gates are in
[the policy](../../docs/STREAMING-AND-CANCELLATION.md) and STATUS/WORKLOG.


## Phase 17 explicit voice

Expand Voice controls in an owned conversation. Record requests microphone
permission only at that action; en-US is the default selected recognition tag.
Android12+ needs an installed on-device engine; API33+ also checks installed
language support. There is no network recognizer fallback or audio upload.
Stop/discard and a 60-second limit bound capture. Navigation, activity pause,
audio focus/device interruption and account changes cancel it.

Edit generated words in the separate review field and explicitly approve before
Send reviewed voice. The original stays generated interpretation; approved text
becomes user-reviewed endorsement lineage. Keystore journal v10 consumes the
approved draft and reserves one exact voice request atomically. Restore never
sends a draft or changes the pending ID. Versions1–9 remain readable. A rejected
voice input returns to unapproved review without replacing a typed composer draft.

Read reply uses a fresh owned completed response and installed offline TTS voices;
choose voice/speed and Stop playback independently of Stop generation. No partial
reply, original ASR record, raw source card or debug trace is passed to playback. See
[VOICE-INTERFACE.md](../../docs/VOICE-INTERFACE.md) for privacy, platform metadata,
limits, source inspection, retention and required physical audio checks.

`./scripts/verify-voice-emulator.ps1` runs real HTTP/Compose/Keystore flows with
explicit synthetic capture/playback adapters, and draft/pending force-stop stages.
`-UiOnly` selects the two voice UI tests. It is not a physical ASR/TTS quality test.
Actual normal/compact checks and target gates are recorded in root STATUS/WORKLOG.


## Phase18 devices and privacy

Source0.18.0-security/versionCode13 adds Settings → Devices and saved content.
Enrollment and explicit deletion processing require server opt-in at head0015;
legacy bearer tokens still connect. One-time device secrets remain masked/in-memory
until explicitly installed through verified same-owner encrypted storage. v11
journals preserve v1–v10 reads and fence all private recovery by content epoch.
Revocation/epoch changes clear cached state; a lost issue secret needs independent
credential/CLI recovery. Reopening checks saved security operation IDs by GET only.
See [security and operations](../../docs/SECURITY-AND-OPERATIONS.md).

Use [VOICE-VALIDATION](../../docs/VOICE-VALIDATION.md) and
`scripts/verify-physical.ps1` for selected-device/user0 isolated APK/loopback checks.
The normal debug application is preserved. The debug native focus probe and separate
focus-fixture module use public synthetic speech only and are not release features.
Never run concurrent Gradle builds against the same Android output directories.

## Phase 20 verification

The source app remains versionCode13/0.18.0-security; no runtime Android behavior
changed. Phase20 re-exercised the current build on an owned read-only API37 emulator.
Three strict cold launches passed; fresh224unit tests, lint/debug/instrumentation/
unsigned-release builds passed. HTTP/OS-dialog/recovery/security evidence and
intermittent failures are preserved in root STATUS/WORKLOG; no physical pass is
claimed. Safe streaming diagnostics contain fixed codes/states/counts only.

The isolated selected-device runner accepts `-RecoveryOnly` to skip the HTTP/dialog
suite and exercise both actual force-stop prepare/resume pairs plus SecurityUI.
It now emits stage results before a failure; exact UUIDs are metadata, not tokens.
Always select an authorized isolated emulator/device explicitly. Never use a normal
app ID, reset a user's app or run concurrent Gradle builds to reproduce these checks.


## Phase23 calendar lookup and explicit quality context

Source app16/0.23.0-quality adds Memory → Explore a calendar interval and an
explicit conversation context-upgrade confirmation. These controls require the
server's new capabilities; v4 new chats, existing journals and session transport
stay compatible. Exact source/correction review and loaded proposal duplicate/
conflict cues preserve individual review. See
[the quality guide](../../docs/ANSWER-QUALITY-AND-MEMORY-RELEVANCE.md).

Local verification recorded239unit tests, lint/debug/instrumentation/unsigned
release builds and a separate API37 emulator HTTP flow. The normal debug APK was
rebuilt after validation; it was not installed on the user's phone. To repeat the
isolated flow, start an owned emulator, set the dedicated ADA_TEST_DATABASE_URL,
then build and run serially:

```powershell
./gradlew.bat -PadaValidationApplicationId=dev.ada.validation.phase23 :app:assembleDebug :app:assembleDebugAndroidTest
../../.venv/Scripts/python.exe -X utf8 ../../scripts/verify_quality_android.py --device emulator-5584
./gradlew.bat :app:assembleDebug :app:assembleDebugAndroidTest
```

Use the selected running emulator serial. The runner rejects physical devices and
normal application IDs, validates APK metadata and uses disposable synthetic
HTTP/PostgreSQL fixtures. It removes only its validation APKs, reverse and schema.
Wait for Android to finish booting before running it. Physical accessibility,
large-font/TalkBack and signed-release HTTPS remain target checks.

## Phase24 public research

Source app17/0.24.0-research adds Chat → Public research, capability-gated exact
outgoing-request previews, explicit approvals, search-snippet/follow-on controls,
verified saved W sources, local answers and explicit imported research notes.
The server feature stays disabled until actual Docker/network isolation passes.
Journalv13 retains v1–v12 reads, binds exact operation/nonce to verified
server/owner/scope/conversation and restores through GET only. Cancellation fences
late responses. No direct internet/provider/database access was added to Android.
See [the guide](../../docs/SECURE-WEB-RESEARCH.md).

Local verification:244unit tests, lint/debug/instrumentation/unsigned release
builds; two real HTTP/PostgreSQL approval/recovery stages on a separate API37
emulator APK, with an actual force-stop between stages. The network broker and
model in those client tests are explicitly synthetic; actual Docker/native public
checks are separately recorded in STATUS. One initial restore assertion compared
a substring as an exact string; correcting it produced both passing stages.
For the isolated runner, start an owned, fully booted emulator and select the
dedicated `ADA_TEST_DATABASE_URL`, then run serially from this directory:

```powershell
./gradlew.bat -PadaValidationApplicationId=dev.ada.validation.phase24 :app:assembleDebug :app:assembleDebugAndroidTest
../../.venv/Scripts/python.exe -X utf8 ../../scripts/verify_research_android.py --device emulator-5584
./gradlew.bat :app:assembleDebug :app:assembleDebugAndroidTest
```

Select the actual owned emulator serial. The runner rejects a physical device or
normal app ID, creates disposable fixtures and removes only its APKs/reverse/schema.
The normal APK was rebuilt without installing it on the user's phone. Physical
S24FE/Android16 approval/recovery, TalkBack/large font, signed-release HTTPS and
the earlier voice/G-41 gates remain open.


## Phase25 opt-in conversational curiosity

Source app18/0.25.0-curiosity adds Settings/Chat → Questions & curiosity: global
off, topic pause/block, depth and cadence controls, optional companions, a later
inbox, original-source inspection and explicit conversation opening/ordinary
answers. Server source needs0017. The feature defaults off and requires the
ada-curiosity-v1 capability. There are no notifications or timers.

Encrypted journalv14 reads v1–v13. The bounded eight-operation queue reserves its
last slot for off, preserves each exact owner/server/scope-bound UUID/body, and
restores through GET only. Receipts bind operation/question/request/conversation
identity. Epoch/logout/scope fences prevent late private display. Answer text is
saved as ordinary conversation history, with no automatic claim or preference.
See [the guide](../../docs/CONVERSATIONAL-CURIOSITY.md) for use/retention/limits.

Local unit/build, real HTTP/PostgreSQL/emulator and native evaluation results are
recorded in STATUS/WORKLOG; preserve earlier refresh failures/intermittency. The
separate API37 emulator uses explicit FakeProvider with real password/session,
HTTP, Keystore and actual force-stop. It simulates a lost action acknowledgement
by retaining the exact encrypted key after a real server write. Reopen reads the
receipt and does not invent another message. No normal app/physical phone reset.

To repeat, start an owned, fully booted emulator, set the dedicated test database
environment, and run serially from apps/android. Quote the complete Gradle
property argument in PowerShell so dots are not split:

```powershell
./gradlew.bat '-PadaValidationApplicationId=dev.ada.validation.phase25' :app:assembleDebug :app:assembleDebugAndroidTest
../../.venv/Scripts/python.exe -X utf8 ../../scripts/verify_curiosity_android.py --device emulator-5584
./gradlew.bat :app:assembleDebug :app:assembleDebugAndroidTest
```

Choose the actual owned emulator serial. The runner checks APK/application IDs,
rejects physical/normal apps and owns only its fixture/reverse/packages. Rebuild
normal APKs after verification. Physical S24FE/Android16, signed HTTPS/handover,
TalkBack/large font and earlier voice/G-41 reliability gates remain separate.
