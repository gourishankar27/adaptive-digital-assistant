# How to use ADA 1.0 — laptop and Android

Current private personal baseline,24 October2026: application1.0.0, Android code 28,
API v1, database 0022, journal 19 and backup-v8. [Old walkthroughs](archive/README.md)
are historical. This is the current setup guide.

Already configured? Use [daily startup](#11-start-and-stop-ada-on-an-ordinary-day).
For the new voice APK, use [Android build/install](#7-build-and-connect-the-android-app).
The latest read-only laptop check found database 0022, healthy API/proxy and private
Tailscale Serve. Recheck after reboot; no fresh database is needed here.

## 1. Understand what runs where

| Component | Location/address on this installation |
|---|---|
| PostgreSQL | Docker Desktop;127.0.0.1:5433 |
| Ollama | Native Windows;http://127.0.0.1:11434 |
| ADA API | Native Windows;http://127.0.0.1:8000 |
| Caddy | Native Windows;http://127.0.0.1:18764 |
| Private HTTPS | https://windows-asus.tail110867.ts.net |
| Dashboard | https://windows-asus.tail110867.ts.net/admin/ |
| Android server field | HTTPS origin, **without `/admin/`** |

Phone/browser → Tailscale HTTPS → Caddy18764 → API8000. Clients use authenticated
ADA APIs; database/Ollama stay private to the laptop. Only PostgreSQL needs Docker
for ordinary chat. Tailscale supplies certificates for this route.

## 2. Install the developer tools

Check before reinstalling:

```powershell
py -3.12 --version
java -version
node --version
npm.cmd --version
docker version
tailscale version
```

Use Python 3.12, JDK 21 (pinned Temurin21.0.12.1), Node 24.12.0 and npm 11.6.2.
Android Studio's SDK Manager needs Platform 36, Build-Tools 35.0.0 and Platform-Tools;
set its Gradle JDK to21. Use the repository wrapper/locks. Start Docker Desktop's
Linux engine, Ollama's Windows app and Tailscale. Connect both devices to the same tailnet.

The normal SDK location is `%LOCALAPPDATA%/Android/Sdk`. If different, pass
`-SdkRoot 'YOUR_SDK_PATH'` to the Android build helper.

## 3. Clone the repository and open your terminals

Existing checkout:

```powershell
$adaRoot = 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
Set-Location $adaRoot
git status --short
```

Keep the reviewed release changes; do not pull/reset over uncommitted work.
For a genuinely fresh checkout only:

```powershell
git clone https://github.com/gourishankar27/adaptive-digital-assistant.git
Set-Location adaptive-digital-assistant
```

Use terminal A for API, B for proxy, C for checks/builds. Run commands from root
unless another directory is specified.

## 4. Set up a fresh backend

Existing installation: skip database/account creation and use section5.

```powershell
.\scripts\setup.ps1
```

This creates `.venv`, installs locked dependencies and creates `.env` only if
absent. Review it privately. Fresh default PostgreSQL port is5432; this laptop
uses5433. Match `POSTGRES_PORT` and `ADA_DATABASE_URL`; preserve the existing
password/volume on upgrade. Never paste `.env` secrets into chat or logs.

The private proxy needs literal dotenv values, for example:

```dotenv
ADA_BROWSER_ORIGIN=https://windows-asus.tail110867.ts.net
ADA_ADMIN_DIST=G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/apps/admin-web/dist
```

Use `KEY=value`, not PowerShell expressions. Old manual TLS certificate/key/bind
examples do not configure the current Tailscale/Caddy route; it needs no manual cert files.

```powershell
docker compose up -d db
docker compose ps
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check
Invoke-RestMethod http://127.0.0.1:11434/api/version
ollama list
```

Fresh schema should report `0022 (head)`. Do not delete the volume to fix startup.
`ADA_OLLAMA_MODEL` must match an installed tag. The example tag is `qwen3.8:27b`;
if that is your chosen model and it is missing, use `ollama pull qwen3.8:27b` once.
Use `ADA_PROVIDER=ollama` for real replies; fake is for isolated tests.

## 5. Upgrade an existing installation

**This laptop is already0022; the 1.0 version label needs no new migration.**

1. Finish active writes; Ctrl+C in the API/proxy windows before source/asset updates.
   Leave PostgreSQL running.
2. Preserve local work and review intended source/release notes.
3. Keep a verified encrypted backup before an actual schema change; see
   [database access/recovery](DATABASE-ADMINISTRATION-WINDOWS.md).
4. Refresh Python metadata and inspect schema:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m alembic heads
.\.venv\Scripts\python.exe -m alembic current
```

If current is 0022, continue. For an older revision, back up, then:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
```

ADA's encrypted recovery tool requires matching PostgreSQL-major tools. This
laptop's server is17; install17 client tools if needed, not another server.
PostgreSQL 18 tools are deliberately refused for it. Interactive backup example:

```powershell
$adaPgBin = 'C:/Program Files/PostgreSQL/17/bin'
$adaBackups = Join-Path $env:LOCALAPPDATA 'ADA/backups'
.\.venv\Scripts\python.exe -m ada.operations --pg-bin $adaPgBin backup --destination $adaBackups
```

Use the hidden passphrase prompt and retain the encrypted artifact/receipt.
Schema0005 uses the [separate legacy workflow](archive/RELEASE-READINESS-PHASE20.md).
Do not downgrade populated history or overwrite the live DB as a rollback drill.

## 6. Create an account and verify authentication

Here, use the existing **gourishankar-admin** login/passphrase. Enrollment is not
a daily step. Inspect safe local account metadata with:

```powershell
.\.venv\Scripts\ada.exe login-accounts
```

For a new owner only, `ada.exe create-user DISPLAY_NAME` returns a UUID and legacy
recovery secret; save that secret privately. Enroll the exact owner UUID:

```powershell
.\.venv\Scripts\ada.exe set-password ACCOUNT_UUID login-name
```

Replace placeholders. Type a15–1024-character passphrase twice in hidden prompts.
This also resets forgotten passwords and revokes password sessions; it is not
part of every startup. Saved owner content is retained. Grant dashboard access
only if needed, using the actual UUID:

```powershell
.\.venv\Scripts\ada.exe grant-admin ACCOUNT_UUID
```

Reuse this laptop's existing account/grant. Names/personality never grant admin.
Resolve name collisions with the exact UUID and a distinct login, not deletion/
merge. [Password/session reference](PASSWORD-LOGIN-AND-SESSIONS.md).

## 7. Build and connect the Android app

### Choose the build

| Profile | File under `dist/android/` | App ID | Speech |
|---|---|---|---|
| `PersonalVoice` |`ada-1.0.0-personalvoice.apk` |`dev.ada.assistant.debug` |Continuous local ASR, Bella, experimental wake |
| `CoreDebug` |`ada-1.0.0-coredebug.apk` |`dev.ada.assistant.debug` |Android short recognition/platform offline TTS |
| `CoreRelease` |`ada-1.0.0-corerelease.apk` |`dev.ada.assistant` |Standard speech; **unsigned** until signed |

Use **PersonalVoice** for new voice behavior on your own S24 FE. It is debug-signed
for personal use. Both debug profiles use the same ID; installing CoreDebug later
replaces native speech with the platform path. Native Release remains gated;
[signing/release details](RELEASE-READINESS.md).

### Build the personal voice APK

One-time public model/runtime preparation, then build:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_private_voice.py --download
.\scripts\build-android.ps1 -Profile PersonalVoice
```

Later rebuilds need only the second command while the cache is intact. The helper
tests/lints/builds, checks actual APK identity and bundled catalogue, then stages
the APK plus SHA256 receipt. It never installs. Model data is about 400 MiB plus
runtime. Use `-Profile CoreDebug` explicitly to exclude native speech.

### Connect and install when the phone is available

On the phone: enable Developer options by tapping Build number seven times;
enable USB debugging; connect a data-capable cable; unlock and accept the RSA prompt.

```powershell
$adaSdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$adb = Join-Path $adaSdk 'platform-tools/adb.exe'
& $adb devices -l
```

Copy the intended serial from its `device` row, select it explicitly and install:

```powershell
$adaDevice = 'YOUR_DEVICE_SERIAL'
$adaApk = (Resolve-Path 'dist/android/ada-1.0.0-personalvoice.apk').Path
$adaReceipt = Get-Content 'dist/android/ada-1.0.0-personalvoice.json' -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $adaApk -Algorithm SHA256).Hash.ToLowerInvariant() -ne $adaReceipt.sha256) {
    throw 'APK differs from its receipt. Rebuild before installing.'
}
& $adb -s $adaDevice install -r $adaApk
if ($LASTEXITCODE -ne 0) { throw 'Installation failed; read the error before continuing.' }
& $adb -s $adaDevice shell dumpsys package dev.ada.assistant.debug | Select-String 'versionCode=|versionName='
& $adb -s $adaDevice shell am start -n dev.ada.assistant.debug/dev.ada.assistant.MainActivity
```

Expect versionName1.0.0 and versionCode28. The explicit launch selects this app
even if another ADA profile/icon is installed. `-r` requests a data-preserving
update; app ID and signing key must match. Do not
uninstall/clear data as a signature-error shortcut: encrypted drafts would be lost.
Debug and production IDs are separate apps with separate sign-in. Retain this
computer's debug key for later personal updates.

### Sign in and enable continuous capture

1. Connect both devices to Tailscale; keep the laptop awake with API/proxy running.
2. Enter `https://windows-asus.tail110867.ts.net` as server, without `/admin/`.
3. Run **Check server without signing in**, then use the enrolled username/passphrase.
4. Open a conversation; tap the microphone for Voice controls.
5. Choose **Install bundled local speech files**. Allow staging/installed space;
   this copies from the APK, not a cloud speech service.
6. Choose **Bella**, preview it, and optionally enable Conversation mode for replies.
7. Enable **Long-form local recording**. Verify **Continuous local recording** in
   the mode label. A new version number alone does not enable this path.
8. Hold the microphone and release to finish, or use Record then Stop. Pauses may
   commit internal segments but do not finish this mode.
9. Edit the composer, then Send explicitly. Nothing sends on release/wake/silence/
   reconnect. Above4000 characters, choose the exact reply-context excerpt before
   Send; the full reviewed wording is retained.

Visible limits:2h,32768 characters,512 segments. Same-owner successful renewal
keeps mic/hold/Stop alive. Failed auth, expiry, privacy/permission/audio/resource
failure or leaving ADA can interrupt it; committed checkpoints survive ordinary
interruptions when secure storage succeeds.

**Hello Ada is experimental and separately opt-in.** Arm from the visible verified
conversation; allow mic/notifications and wait for Armed. Background/locked wake
only gives a nonprivate cue/Open ADA notification. Unlock for private interaction.
Stop listening when finished. Reboot/force-stop requires re-arming. Human locked-
wake/long-mic/resource acceptance is pending. [Detailed voice guide](PRIVATE-VOICE-CONVERSATIONS.md).

## 8. Start and sign in to the admin dashboard

With the proxy stopped, build assets once and after web updates:

```powershell
Push-Location apps/admin-web
npm.cmd ci
npm.cmd run build
Pop-Location
.\scripts\install-private-proxy.ps1
.\scripts\start-private-proxy.ps1 -CheckOnly
```

Keep `ADA_ADMIN_DIST` pointing at the literal absolute `dist` directory. For
first-time Serve setup only, with Caddy on 18764:

```powershell
tailscale serve --bg --https=443 http://127.0.0.1:18764
tailscale serve status
tailscale funnel status
```

Approve Serve/HTTPS if asked. Keep it tailnet-only; Funnel is unnecessary. Existing
Serve configuration survives ordinary starts. [Private routing reference](PRIVATE-SETUP-WINDOWS-TAILSCALE.md).
Open `https://windows-asus.tail110867.ts.net/admin/` and use the enrolled admin
account. Browser server origin is the HTTPS origin without `/admin/`, not Vite5173.

## 9. Use chat, memory, documents and the other implemented features

- **Chat:** open/create a conversation; type/review speech and Send. Explicit Stop
  cancels an owned generation; disconnecting the view alone does not.
- **Memory:** review notes/claims and preserve correction history. Imported/model
  text is not automatically an endorsed fact.
- **Documents:** review scoped text/Markdown imports; PDFs need the separate
  isolated parser. Scanned PDFs/OCR remain unsupported.
- **Sources:** inspect frozen request evidence/provenance, not merely current memory.
- **Projects:** review goals/tasks; due dates do not automatically schedule reminders.
- **Settings:** palettes/preferences and explicit questions/learning consent.

[Feature guides](README.md#using-implemented-features) explain reminders, research,
reflection and other optional services. Their configuration/consent gates remain.
On-device text generation stays disabled after quality failures; speech is separate.

## 10. Use the command-line client

Normal phone/browser use needs no token handling. Operator enrollment/recovery is
above. Inspect advanced developer commands with:

```powershell
.\.venv\Scripts\ada.exe --help
.\.venv\Scripts\ada.exe chat --help
```

Keep bearer secrets private. The old Phase1→Phase2 installer is historical, not
the normal 1.0 update path.

## 11. Start and stop ADA on an ordinary day

Start Docker Desktop/Ollama and connect Tailscale. Terminal C:

```powershell
Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
docker compose up -d db
docker compose ps
Invoke-RestMethod http://127.0.0.1:11434/api/version
tailscale serve status
```

Terminal A, same root:

```powershell
.\scripts\start.ps1
```

Wait for the startup/listening banner and leave it open. No returned prompt is
normal for this foreground server. Terminal B, same root:

```powershell
.\scripts\start-private-proxy.ps1
```

Leave it open. Terminal C verifies all layers:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/ready
Invoke-RestMethod http://127.0.0.1:18764/health/ready
Invoke-RestMethod https://windows-asus.tail110867.ts.net/health/ready
```

Expect `ready`, schema 0022. After restart with this source, `/openapi.json` reports
application1.0.0 under `info.version`. Normal use needs no USB/ADB reverse; devices
may be on different networks within the same tailnet.

Shutdown: stop speech, finish writes, Ctrl+C in A/B; optionally `docker compose stop db`.
Keep the volume. [Managed always-on operation](ALWAYS-ON-OPERATIONS.md) is a separate
intentional setup, not required for this manual flow.

## 12. Troubleshoot setup and runtime problems

| Symptom | Check/action |
|---|---|
| Scripts blocked | Review/unblock the specific trusted file and follow local PowerShell policy. |
| Docker cannot connect | Start Docker Desktop; wait for Linux engine; check `docker version`. |
| Database error | Check Compose status, private password/port and schema; retain the volume. |
| API has no prompt | Expected foreground behavior; check8000 readiness separately. |
| Port already used | Another API/managed instance owns it; check or deliberately stop that instance. |
| Proxy502 | Check8000; its API upstream may be stopped. |
| Admin blank/404 | Build assets, check `ADA_ADMIN_DIST`, proxy `-CheckOnly` and `/admin/`. |
| Password403 | Check the actual admin grant; username grants nothing. |
| Phone server check fails | Same tailnet, laptop awake; check8000→18764→HTTPS; no `/admin/` in Android URL. |
| Slow/no answer | Ollama, exact tag, RAM/VRAM and timeout. Do not change request ID merely for a timeout. |
| Recording stops on silence | PersonalVoice/files/Long-form are required; standard profiles use Android short recognition. |
| Long toggle missing | Check installed files, authenticated conversation and0022 capability. |
| ADB unauthorized | Unlock, accept RSA, enable debugging and use a data cable. |
| Multiple devices | Select `-s YOUR_DEVICE_SERIAL`. |
| UPDATE_INCOMPATIBLE | Signature mismatch: use original key/profile; preserve app data. |
| VERSION_DOWNGRADE | Select/rebuild current code 28 APK, not a forced downgrade. |
| Unsigned APK rejected | Sign CoreRelease first; PersonalVoice debug is already signed. |
| Native Release rejected | Intentional gate; PersonalVoice is the private debug route. |
| Backup major mismatch | Use PostgreSQL 17 tools with this laptop's server17. |

## 13. Run developer verification

From root, without using the application database as a test fixture:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\apps\android\gradlew.bat -p apps/android testDebugUnitTest lintDebug assembleDebug
```

PostgreSQL tests need a dedicated `ADA_TEST_DATABASE_URL`; native recovery also
needs matching `ADA_TEST_PG_BIN`. [Status/work log](../plans/STATUS.md) records actual
runs/skips. In `apps/admin-web`: `npm.cmd run lint`, `npm.cmd run test -- --run`,
`npm.cmd run contracts:check`, `npm.cmd run build`. Physical tests stay deferred.

## 14. Find implementation details and current limits

[Documentation index](README.md), [architecture](ARCHITECTURE.md),
[release/signing](RELEASE-READINESS.md), [status](../plans/STATUS.md),
[work log](../plans/WORKLOG.md), [release notes](../CHANGELOG.md).

This personal baseline retains open voice/wake/lifecycle/accessibility/resource
acceptance and native redistribution review. These instructions do not claim
a phone install, live migration or public publication.

Official references: [ADB](https://developer.android.com/tools/adb),
[signing](https://developer.android.com/studio/publish/app-signing),
[apksigner](https://developer.android.com/tools/apksigner),
[Tailscale Serve](https://tailscale.com/docs/reference/tailscale-cli/serve).
