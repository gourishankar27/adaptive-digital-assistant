# How to use ADA — developer setup and everyday operation

Updated **24 October 2026** for source head **0022 / 77 tables**,
backup-v8 and Android27/journal19. This source update has not migrated the installed
database or upgraded the normal phone. Phase32 native speech is optional private
evaluation; follow [its preparation/use guide](PRIVATE-VOICE-CONVERSATIONS.md)
and acceptance gates before selecting that build. Ordinary builds keep platform speech. Earlier phase documents retain their historical
schema requirements; compare `alembic current` with `alembic heads` for this checkout.

**Already set up on your laptop? Start at [section 11](#11-start-and-stop-ada-on-an-ordinary-day).**
You need Docker/PostgreSQL, Ollama, the API window and the private-proxy window.
The API and proxy stay in the foreground: no returned PowerShell prompt is normal.
The startup banner identifies the listening API; `/health/ready` confirms database
readiness. A quiet window alone proves neither success nor failure.

The normal phone/browser workflow uses **username/password over Tailscale HTTPS**:
Android server `https://windows-asus.tail110867.ts.net`, dashboard
`https://windows-asus.tail110867.ts.net/admin/`. These are this laptop's configured
addresses; use your own `tailscale serve status` origin on another installation.
The advanced token/Vite/USB instructions below are optional developer workflows.

For first-time private routing and managed TLS, use
[Windows + Tailscale setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md). Its original setup
observations are dated; use the current head above for an upgrade. For account
enrollment and sessions, see [password login](PASSWORD-LOGIN-AND-SESSIONS.md).
For database access, supported changes and recovery, see
[Windows database administration](DATABASE-ADMINISTRATION-WINDOWS.md).

Text PDFs require the separately enabled [bounded parser](PDF-INGESTION.md).
[On-device draft generation](ON-DEVICE-DRAFTS.md) remains disabled after failed
model-quality trials; OCR remains off. This guide does not enable optional
features, migrate data or install a deployment.

## Contents

1. [Understand what runs where](#1-understand-what-runs-where)
2. [Install the developer tools](#2-install-the-developer-tools)
3. [Clone the repository and open your terminals](#3-clone-the-repository-and-open-your-terminals)
4. [Set up a fresh backend](#4-set-up-a-fresh-backend)
5. [Upgrade an existing installation](#5-upgrade-an-existing-installation)
6. [Create an account and verify authentication](#6-create-an-account-and-verify-authentication)
7. [Build and connect the Android app](#7-build-and-connect-the-android-app)
8. [Start and sign in to the admin dashboard](#8-start-and-sign-in-to-the-admin-dashboard)
9. [Use chat, memory, documents and the other implemented features](#9-use-chat-memory-documents-and-the-other-implemented-features)
10. [Use the command-line client](#10-use-the-command-line-client)
11. [Start and stop ADA on an ordinary day](#11-start-and-stop-ada-on-an-ordinary-day)
12. [Troubleshoot setup and runtime problems](#12-troubleshoot-setup-and-runtime-problems)
13. [Run developer verification](#13-run-developer-verification)
14. [Find implementation details and current limits](#14-find-implementation-details-and-current-limits)

Run the steps in order. If a command fails, stop at that step and resolve the error
before continuing. Commands labelled as examples/placeholders need your actual
account, model, device or path values.

## 1. Understand what runs where

Your computer runs the Python API, PostgreSQL and Ollama. Android sends
authenticated HTTP requests to the Python API. The admin browser sends requests
through the private HTTPS proxy to that same API. Neither client connects
directly to PostgreSQL or Ollama.

For the local Windows workflow, only PostgreSQL is in Docker. Python and Ollama
run natively. There is no command here to start a Docker container for the API.

| Component | Default address | Purpose |
|---|---|---|
| ADA API on the computer | `http://127.0.0.1:8000` | Authentication, chat and owned data APIs |
| API explorer | `http://127.0.0.1:8000/docs` | Inspect and try the implemented API |
| API liveness | `http://127.0.0.1:8000/health/live` | Is the API process responding? |
| API readiness | `http://127.0.0.1:8000/health/ready` | Is the database reachable at the required schema? |
| Private internal proxy | `http://127.0.0.1:18764` | Caddy forwards API requests and serves built admin assets |
| Tailscale HTTPS origin | `https://windows-asus.tail110867.ts.net` | Normal Android server URL; also the browser server origin |
| Admin dashboard | `https://windows-asus.tail110867.ts.net/admin/` | Normal browser/password login |
| PostgreSQL host port | `127.0.0.1:5433` on this laptop | Fresh default is5432; use the matching `POSTGRES_PORT`/database URL |
| Ollama | `http://127.0.0.1:11434` | Server-side model provider |
| Optional admin development page | `http://127.0.0.1:5173/admin/` | Vite with advanced bearer login; not password login |
| Android emulator API URL | `http://10.0.2.2:8000` | Emulator access to the computer's API |
| USB phone API URL, after ADB reverse | `http://127.0.0.1:8000` | Phone-to-computer forwarding over USB |

The normal route is **phone/browser → Tailscale HTTPS → Caddy18764 → API8000**.
Docker runs only the database. Tailscale Serve supplies TLS; this arrangement
does not need manual certificate/key files, Vite or USB forwarding. On a phone,
`127.0.0.1` refers to the phone unless the optional USB reverse mapping is active.

## 2. Install the developer tools

The commands below use **PowerShell 7 on Windows**. Open a new terminal after
installing a tool so that its PATH changes take effect.

| Tool | Needed for | Version/configuration to use | Official installation page |
|---|---|---|---|
| Git | Clone/update | Git for Windows | [Git for Windows](https://git-scm.com/install/windows) |
| Python | Backend | Python **3.12**, with the Windows `py` launcher | [Python Windows releases](https://www.python.org/downloads/windows/) |
| Docker Desktop | Default PostgreSQL setup | Linux containers; a supported Windows/WSL setup | [Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/) |
| Ollama | Actual model replies | Native Windows installation | [Ollama on Windows](https://docs.ollama.com/windows) |
| JDK | Android build | JDK **21**; repository pin: Temurin **21.0.12.1+1** (`.java-version`: `21.0.12.1`) | [Temurin releases](https://adoptium.net/temurin/releases/) |
| Android Studio/SDK | Android build/device | SDK Platform **36**, Build-Tools **35.0.0**, Platform-Tools | [Android Studio installation](https://developer.android.com/studio/install) |
| Node.js/npm | Admin web | Node **24.12.0**, npm **11.6.2** | [Node.js downloads](https://nodejs.org/en/download) |

Python requirements, npm packages and Android dependencies are already pinned in
the repository. Use `requirements.lock`, `npm ci` and the Gradle wrapper. Do not
replace these with unpinned package installations or accept unrelated IDE upgrades.

### Check the tools that you installed

In PowerShell:

```powershell
$PSVersionTable.PSVersion
git --version
py -3.12 --version
docker version
docker compose version
ollama --version
node --version
npm --version
```

Expected: Python reports 3.12; Node reports `v24.12.0`; npm reports `11.6.2`.
`docker version` must show a reachable **Server**, not only a Client.
Android/JDK setup is checked in section 7.

If Node is correct but npm differs, install the repository's npm pin:

```powershell
npm install --global npm@11.6.2
npm --version
```

### Start Docker Desktop

1. Open **Docker Desktop** from the Windows Start menu.
2. Complete its first-run setup.
3. Use **Linux containers**. The PostgreSQL image in this repository is a Linux image.
4. Wait for the Docker engine to report that it is running.
5. Run `docker info` in PowerShell. Resolve engine errors before starting PostgreSQL.

For a WSL-backed installation, check `wsl --version`; follow Docker's documented
WSL/virtualization requirements if first-run setup asks for them. Docker Desktop
must be started after installation. See [Docker's Windows guide](https://docs.docker.com/desktop/setup/install/windows-install/).

If you already operate native PostgreSQL, you can use it instead. Configure its
existing database/role privately in `.env` and skip the Docker database steps;
do not start another database on an occupied port.

## 3. Clone the repository and open your terminals

### Clone once

This example uses a `source` directory under your Windows user profile:

```powershell
$adaWorkspace = Join-Path $env:USERPROFILE 'source'
New-Item -ItemType Directory -Path $adaWorkspace -Force | Out-Null
Set-Location $adaWorkspace
git clone https://github.com/gourishankar27/adaptive-digital-assistant.git
Set-Location adaptive-digital-assistant
```

If Git requires repository access, authenticate through your normal Git credential
manager/SSH setup. Do not embed an access token in the clone URL.

If you already have a checkout, use its actual path instead of cloning over it.
Check `git status --short` before updating; preserve your local work.

### Recognize the repository root

It contains `AGENTS.md`, `README.md`, `compose.yaml`, `alembic.ini`, `scripts/`,
`src/`, `apps/` and `plans/`. Server setup commands run from this directory.

At the beginning of **each new PowerShell window**, run:

```powershell
$adaRepo = Join-Path $env:USERPROFILE 'source/adaptive-digital-assistant'
Set-Location $adaRepo
```

Change `$adaRepo` if you cloned elsewhere. Variables and environment changes in
one terminal do not automatically appear in another.

| Terminal | Use |
|---|---|
| A — backend | Initial setup, then the foreground Python API |
| B — private proxy | Foreground `scripts/start-private-proxy.ps1` |
| C — operator/client | Health checks, local account operations and optional CLI chat |
| D — Android | JDK/SDK setup, Gradle and ADB commands |

You do not have to activate `.venv`: commands use its executable paths explicitly.
You do not need to run every terminal as Administrator.

## 4. Set up a fresh backend

**Use this section for a new installation.** If a database already contains your
accounts/history, follow section 5. Do not replace an existing `.env` or delete its
Docker volume to make the setup look fresh.

### Step 1 — create the Python environment

In terminal A, from the repository root:

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\python.exe --version
```

The setup script creates `.venv`, installs `requirements.lock`, installs ADA as an
editable package without independently resolving dependencies, and creates `.env`
from `.env.example` **only if `.env` does not exist**. A new `.env` receives a
generated database password.

Expected: the script reports that the Python environment is ready. If it fails,
resolve that error before continuing.

### Step 2 — review `.env`

Open the file in an editor:

```powershell
notepad .env
```

Check these settings without copying passwords into logs or support messages:

| Setting | What to check |
|---|---|
| `POSTGRES_PASSWORD` | For a fresh Docker database, keep the generated password. |
| `POSTGRES_PORT` | Default `5432`; select another free host port if needed. |
| `ADA_DATABASE_URL` | Its host, port, database, user and password must match the intended PostgreSQL instance. |
| `ADA_PROVIDER` | Use `ollama` for real model replies. `fake` is a synthetic test provider. |
| `ADA_OLLAMA_URL` | Default `http://127.0.0.1:11434`. |
| `ADA_OLLAMA_MODEL` | Exact installed model tag, including its suffix. |
| `ADA_MAX_PARALLEL` | Start with `1`. |
| `ADA_EMBEDDING_ENABLED` | Leave `false` for the baseline workflow. |
| `ADA_CONSOLIDATION_WORKER_ENABLED` | Keep `true` if you want explicitly queued summary/proposal/index jobs to process. |

The default database name/user are `ada`. `POSTGRES_PORT` is the computer's host
port; the container still uses 5432. If you use host port 5433, update **both**
`POSTGRES_PORT` and the port in `ADA_DATABASE_URL`. URL-encode special characters
in a manually supplied connection-string password.

`.env` is ignored by Git. Do not run plain `docker compose config` into a shared
log: its expanded output can contain the database password. Use `--services` for
a non-secret service listing.

### Step 3 — start PostgreSQL

Make sure Docker Desktop is running, then:

```powershell
docker compose config --services
docker compose up -d --wait db
docker compose ps db
docker compose exec -T db pg_isready -U ada -d ada
```

Expected: the service listing includes `db`; PostgreSQL becomes healthy and
`pg_isready` reports that it accepts connections. Compose stores database data
in the `ada_pgdata` volume.

If port 5432 is occupied, determine whether it is your existing intended database.
Do not kill that process indiscriminately. Either use that database with matching
configuration or choose a different Docker host port as described above.

### Step 4 — install the schema

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m alembic heads
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic check
```

For this source version, both head/current should report **0021**. `alembic check`
should find no new upgrade operations. Run the chain to the actual head; do not
edit released migration files or use `stamp head` to bypass missing schema changes.

### Step 5 — start Ollama and install/select the model

Open the installed Ollama Windows application. Its normal Windows installation
runs in the background and serves port11434. Check it from an operator terminal:

```powershell
ollama list
Invoke-RestMethod 'http://127.0.0.1:11434/api/tags'
```

If Ollama is not running and you use its CLI directly, open a separate terminal
and run `ollama serve`, leaving it open. If 11434 is already serving Ollama, do not
start a second server. See [Ollama's Windows setup](https://docs.ollama.com/windows).

The repository's `.env.example` currently defaults to `qwen3.8:27b`. If you intend
to use that tag and it is available for your installation:

```powershell
ollama pull qwen3.8:27b
ollama list
```

The important requirement is that `ADA_OLLAMA_MODEL` exactly matches an installed
tag. If the default tag cannot be pulled, select an available model deliberately,
edit `.env` to its exact tag, and validate its chat and structured-output/tool
behavior. The configured default is not a claim that every machine can download
or efficiently run it. Model size, available memory and actual latency matter.
The [Ollama CLI reference](https://docs.ollama.com/cli) documents pull/list commands.

### Step 6 — check the backend configuration

```powershell
.\.venv\Scripts\ada.exe doctor
```

Expected: database schema 0021, the configured model tag, and that model in the
installed list. `doctor` checks schema/model metadata; it does not prove that a
model can successfully complete every chat, tool or summary request.

If it says `FAKE provider selected`, no real model will run. Set
`ADA_PROVIDER=ollama` and restart the API when ready.

### Step 7 — start the API

In terminal A, from the root:

```powershell
.\scripts\start.ps1
```

Leave terminal A running. Progress messages cover loading, ownership checks,
application recovery and listener startup. After the socket opens, expect
`ADA API is running at http://127.0.0.1:8000 (one worker).` It also prints the
readiness URL and, when configured, the conditional HTTPS connection addresses.
Access logging stays disabled. This is a foreground server, so the PowerShell
prompt does not return until it stops. Configuration changes require a restart.

In a separate operator terminal:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health/live'
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
```

Expected: `status: ok`, then `status: ready` and `schema: 0021`.
Readiness checks the database/schema, not model-generation success. A running
process with a failing readiness endpoint is not ready for client use.

### Step 8 — enroll password login and configure private HTTPS

Keep terminal A running and follow section 6 in an operator terminal. Then follow
section 8 and the private setup guide to build/serve the dashboard over HTTPS.
There is no public signup page. Existing enrolled users can simply sign in.

## 5. Upgrade an existing installation

Skip account creation if you already have an account. Keep existing
database credentials, volumes, accounts, grants, prompts and saved history.

1. Stop the ADA API with **Ctrl+C** in its own terminal. Stop Vite before updating
   its installed packages. Keep PostgreSQL running for backup/migration.
2. Run `git status --short`. Preserve local work before pulling or changing branches.
3. Back up the intended database through your operator process.
4. Update to the source version you intend to run. For a normal clean checkout,
   `git pull --ff-only` updates without inventing a merge. Resolve a divergent or
   modified checkout consciously; do not reset it to discard work.
5. Refresh the locked Python dependencies in the existing environment.
6. Compare the configured database revision with this checkout's head, migrate,
   and check schema drift.
7. Run `doctor`, restart ADA and confirm readiness.
8. Rebuild clients as needed. Existing server tokens remain valid unless rotated.

### Encrypted backup before an upgrade

Use the Phase18 encrypted backup procedure in [SECURITY-AND-OPERATIONS](SECURITY-AND-OPERATIONS.md).
It stores verified encrypted artifacts under `%LOCALAPPDATA%/ADA/backups`, uses a
separately protected passphrase and rehearses recovery into a new isolated database.
Use PostgreSQL client binaries matching the intended server major version. A raw
`pg_dump` file or `pg_restore --list` result alone is not the selected recovery procedure.
For an installation at0005, Phase 20 now provides a separate encrypted pre-upgrade
tool and isolated restore/upgrade rehearsal in [RELEASE-READINESS](RELEASE-READINESS.md).
Current recovery supports versioned v1–v7 artifacts and reviewed heads0015–0021;
use the current schema's format. See [PDF recovery](PDF-INGESTION.md) and
[always-on operations](ALWAYS-ON-OPERATIONS.md). Older heads need their previously
verified protected recovery procedure; no tool upgrades the source just to back up.
Do not overwrite live databases or delete the existing Docker volume during a drill.

### Refresh dependencies and migrate

After the backup and intended source update, from the root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m alembic heads
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\ada.exe doctor
.\scripts\start.ps1
```

For this guide's source, an old 0005 installation must advance through the complete
chain to 0021. Adding code to the checkout never performs this upgrade automatically.
Do not downgrade populated history as a routine troubleshooting step.

## 6. Create an account and verify authentication

### Normal sign-in — username and password

If you already enrolled a password, **reuse that account and password**. On this
laptop the previously verified admin login is `gourishankar-admin`; a display name
and a login identifier may differ. Do not recreate the account to resolve a proxy
or startup failure.

For an existing account that has not enrolled, use a local interactive terminal:

```powershell
.\.venv\Scripts\ada.exe login-accounts
.\.venv\Scripts\ada.exe set-password ACCOUNT_UUID login-identifier
```

Replace both placeholders with the intended owner UUID from the listing and a
distinct chosen login identifier. Enter a **15–1024 character** password twice at
the hidden prompts. Expected: `Password set; password sessions revoked.` Keep the
password out of commands, `.env`, chat and logs. Resetting it revokes password
sessions; it does not change the owner or grant admin access.

For a genuinely new account, create it with the advanced command below, capture
the issued output privately, then enroll using its `user_id`. A dashboard account
also needs an explicit `grant-admin ACCOUNT_UUID`. See
[the session guide](PASSWORD-LOGIN-AND-SESSIONS.md) for recovery/revocation.

### Advanced developer path — create a new account/token

In an operator terminal at the root, replace `developer` with your chosen account
name. Capture the output in memory so the bearer secret is not echoed by default:

```powershell
$adaIssued = .\.venv\Scripts\ada.exe create-user developer | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Account creation failed; resolve the error before continuing.' }
$adaIssued.user_id
$env:ADA_TOKEN = $adaIssued.token
```

Save the token in your password manager. If you need to paste it into Android or
the browser, copy it deliberately:

```powershell
Set-Clipboard -Value $adaIssued.token
```

Paste the **token value only**, without `Bearer `, into client token fields. Clear
the clipboard after pasting (`Set-Clipboard -Value ''`) and avoid clipboard-history
retention of secrets. The server stores only a hash and cannot show the old token
again. Do not write this output into a transcript, log, tracked file or issue.

### Advanced developer path — existing account/token

Do not run `create-user` again for an existing account. In a new client/operator
terminal, load your saved token without entering it as a literal shell command:

```powershell
$adaTokenInput = Read-Host 'Paste your ADA bearer token' -AsSecureString
$env:ADA_TOKEN = [System.Net.NetworkCredential]::new('', $adaTokenInput).Password
Remove-Variable adaTokenInput
```

### Verify the token and discover your account UUID

With the API running and `$env:ADA_TOKEN` set in this terminal:

```powershell
$adaHeaders = @{ Authorization = "Bearer $env:ADA_TOKEN" }
$adaMe = Invoke-RestMethod 'http://127.0.0.1:8000/v1/me' -Headers $adaHeaders
$adaMe.id
Invoke-RestMethod 'http://127.0.0.1:8000/v1/capabilities' -Headers $adaHeaders
```

Expected: your account UUID and implemented feature capabilities. `/v1/me`
returns `id` and `name`; use **id** for admin grants. A 401 means the supplied token
is missing/invalid/revoked. A name, personality or account UUID is not a token.

### Optional — inspect the API in the browser

Open `http://127.0.0.1:8000/docs`, click **Authorize**, paste the token value,
confirm and close the dialog. Expand `GET /v1/me`, click **Try it out**, then
**Execute**; a valid token should return 200. Use the exported route schemas for
later developer requests rather than inventing JSON fields. The API explorer is
not the admin login page, and authentication does not override ownership checks.

### Grant admin monitoring only if you need the dashboard

In the local operator terminal using the intended database:

```powershell
.\.venv\Scripts\ada.exe grant-admin $adaMe.id
```

For password-only enrollment, use the exact UUID from `login-accounts` in place
of `$adaMe.id`. Alternatively, use `$adaIssued.user_id` for a newly
created account. **Do not pass an account name to `grant-admin`.** The account
keeps its existing token. An explicit grant enables monitoring; it does not give
access to another owner's chats/documents or turn the dashboard into a control panel.

To revoke monitoring later, use `ada.exe revoke-admin` with that same account UUID.

### Lost or compromised token

The local operator can issue a replacement for the exact existing account name:

```powershell
$adaRotated = .\.venv\Scripts\ada.exe rotate-token developer | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Token rotation failed.' }
$env:ADA_TOKEN = $adaRotated.token
$adaHeaders = @{ Authorization = "Bearer $env:ADA_TOKEN" }
Set-Clipboard -Value $adaRotated.token
```

Rotation invalidates the old token. Save the new secret and reconnect clients.
If Android has a pending operation, use **Replace token for this account** to
re-verify the same owner/server before retaining its reserved operation. Do not
log out merely to test rotation: logout clears local private recovery state.

## 7. Build and connect the Android app

### Step 1 — install the SDK components and select JDK 21

1. Install Android Studio and complete its initial SDK setup.
2. Open **Tools → SDK Manager**.
3. Install Android SDK Platform **36**, Android SDK Build-Tools **35.0.0**,
   Android SDK Platform-Tools, and Command-line Tools if you want CLI SDK management.
4. Open the Gradle project at **`apps/android`**, not a new empty Android project.
5. Set Android Studio's **Gradle JDK** to your JDK **21** installation under
   Settings → Build, Execution, Deployment → Build Tools → Gradle.
6. Accept the SDK licenses. Keep the checked-in Gradle wrapper/catalog/lockfiles.

The repository wrapper uses Gradle **8.13**, AGP **8.11.1** and Kotlin **2.2.21**.
It checks the runtime Java major version. Android Studio's bundled JBR may be a
different major version; explicitly selecting JDK 21 matters.

In terminal D, at the root, set local paths. Enter the actual installed JDK folder
when prompted, for example the JDK directory under `C:/Program Files/Eclipse Adoptium`:

```powershell
$env:JAVA_HOME = Read-Host 'Full path to your installed JDK 21 directory'
$env:ANDROID_HOME = Join-Path $env:LOCALAPPDATA 'Android/Sdk'
$env:PATH = "$env:JAVA_HOME/bin;$env:ANDROID_HOME/platform-tools;$env:PATH"
& "$env:JAVA_HOME/bin/java.exe" -version
$adbPath = Join-Path $env:ANDROID_HOME 'platform-tools/adb.exe'
adb version
```

Adjust `ANDROID_HOME` if SDK Manager shows a different location. If using CLI SDK
management after installing Command-line Tools:

```powershell
$adaSdkManager = Join-Path $env:ANDROID_HOME 'cmdline-tools/latest/bin/sdkmanager.bat'
& $adaSdkManager --licenses
& $adaSdkManager 'platform-tools' 'platforms;android-36' 'build-tools;35.0.0'
```

Android Studio may create an ignored `local.properties`. If writing it manually,
use Java-properties escaping, for example
`sdk.dir=C\:/Users/developer/AppData/Local/Android/Sdk`. Do not commit this machine path.

### Step 2 — build and check the debug app

From terminal D, with the JDK/SDK variables set:

```powershell
Push-Location apps/android
.\gradlew.bat --version
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug
Pop-Location
```

Expected: Gradle runs under Java 21 and ends with `BUILD SUCCESSFUL`. The APK is:

```text
apps/android/app/build/outputs/apk/debug/app-debug.apk
```

The debug package is `dev.ada.assistant.debug`. Use it for local HTTP development.
An unsigned release build is not a signed/distributed app and does not enable
debug cleartext exceptions.

### Step 3A — install on the Samsung S24 FE over USB

1. On the phone, enable Developer options. On Samsung, find **Build number** under
   About phone → Software information and tap it seven times if needed.
2. Enable **USB debugging** in Developer options.
3. Connect a data-capable USB cable and unlock the phone.
4. Accept the phone's **Allow USB debugging** RSA prompt for your computer.
5. Check the connection:

```powershell
& adb devices -l
```

Expected: the phone appears with state **device**, not `unauthorized` or `offline`.
Windows may require the manufacturer's ADB USB driver; use Android Studio's
Connection Assistant if detection fails. See [Android's hardware-device instructions](https://developer.android.com/studio/run/device).

With **one physical USB phone** connected, use `-d` to avoid accidentally selecting
an emulator. With multiple phones, replace `-d` with `-s YOUR_DEVICE_SERIAL`.

Create the forwarding rule, install the APK without clearing its data, and open it:

```powershell
adb -d install -r "$adaRepo/apps/android/app/build/outputs/apk/debug/app-debug.apk"
adb -d shell am start -n dev.ada.assistant.debug/dev.ada.assistant.MainActivity
```

USB is needed for this install, not normal Tailscale connectivity. For the optional
HTTP/bearer developer route only, also run `adb -d reverse tcp:8000 tcp:8000` and
keep USB connected. Recreate that mapping after reconnect/restart if needed.
`adb reverse --list` diagnoses forwarding; it does not start the backend.

### Step 3B — use an emulator instead

Create/start an Android virtual device with Device Manager, then run the `app`
configuration from Android Studio or install the debug APK onto that emulator.
For one running emulator, `adb -e install -r PATH_TO_APK` selects it.

In the emulator app, use **`http://10.0.2.2:8000`**. This differs from the USB
phone URL. No phone USB reverse mapping is needed for the emulator's host alias.
For voice input, use API 31+ with an available installed on-device engine/language;
an arbitrary emulator image may not provide one.

### Step 4 — sign in on Android

On **Welcome back.**:

1. In **ADA server URL**, enter:
   - Normal S24 FE/Tailscale use: `https://windows-asus.tail110867.ts.net`.
   - Another installation: its verified private HTTPS origin.
2. Connect Tailscale on the phone to the same tailnet as the laptop. Tap
   **Check server without signing in** and confirm readiness.
3. Enter **Username** and **Password**, then tap **Connect**.
4. Wait for the verified account and conversation list.

Enter an origin only: do not append `/docs`, `/v1`, `/admin` or a query string.
Do not enter database credentials, an Ollama URL or the web frontend's port 5173.

For the optional developer bearer path, expand **Advanced: legacy bearer token**
and enter only the issued token. A USB debug phone can use
`http://127.0.0.1:8000` after the reverse mapping; an emulator uses
`http://10.0.2.2:8000`. Password sign-in requires HTTPS.
Debug HTTP exceptions cover only the documented loopback/emulator hosts. An
ordinary `http://192.168...` LAN URL is not the supported debug setup. For remote
use, configure authenticated trusted HTTPS separately; this guide does not deploy
a server or add certificates/firewall rules.

Android encrypts the verified credential and reserved operations with Keystore.
Logout/account-server changes clear local private state. Preserve pending work
before clearing app storage or uninstalling.

## 8. Start and sign in to the admin dashboard

### Step 1 — check backend readiness and your explicit grant

Before starting the web UI, verify section 4's readiness check and section 6's
password enrollment/account UUID. The current backend must be at head **0021**. Admin access
requires an explicit monitoring grant; migration alone never grants a role.

### Step 2 — build once, then start the private proxy

After a fresh checkout or web-source/dependency update, use the pinned
Node24.12.0/npm11.6.2 toolchain in an operator terminal:

```powershell
node --version
npm --version
Push-Location apps/admin-web
npm ci
npm run build
Pop-Location
.\scripts\install-private-proxy.ps1
.\scripts\start-private-proxy.ps1 -CheckOnly
```

Set these nonsecret values in `.env` using a literal path; PowerShell expressions
such as `(Resolve-Path ...).Path` are not evaluated inside dotenv files:

```dotenv
ADA_BROWSER_ORIGIN=https://windows-asus.tail110867.ts.net
ADA_ADMIN_DIST=G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/apps/admin-web/dist
```

Substitute your actual origin/checkout on another computer. Restart the API after
changing its origin. The proxy installer pins and verifies Caddy; no Windows
service is installed by these commands. Follow
[private setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md) if Caddy/Serve is not installed.

For daily use, leave the API running in window A and run this in window B:

```powershell
.\scripts\start-private-proxy.ps1
```

Leave both windows open. Caddy listens on loopback18764; Tailscale Serve forwards
the tailnet HTTPS origin to it. Section11 verifies each layer. No manual TLS
certificate/key, public Funnel or Vite server is needed for this route.

### Step 3 — sign in over private HTTPS

Open **https://windows-asus.tail110867.ts.net/admin/** with Tailscale connected.

| Field | Enter |
|---|---|
| Browser server origin | `https://windows-asus.tail110867.ts.net` (no path/trailing slash) |
| Username | Your enrolled login identifier, such as this laptop's `gourishankar-admin` |
| Password | Your enrolled private passphrase |

The origin must match the address bar and `ADA_BROWSER_ORIGIN` exactly.
Sign in using the normal password form. Do not enter port8000,18764,5173 or
`/admin/` in that field for this HTTPS setup.

After sign-in, verify the displayed operator/server and open Overview, Requests,
request detail, Providers/limits or Audit. The dashboard is read-only monitoring;
it does not approve tools, grant roles, edit prompts or reveal another user's chat.

Password sessions use Secure/HttpOnly cookies; the browser renews a valid session
on reload. Appearance settings persist separately; a saved theme is not a login.

### Optional — Vite with advanced bearer login for web development

This is a separate local workflow for editing the web UI. From `apps/admin-web`,
run `npm run dev` and leave that terminal open. Open
`http://127.0.0.1:5173/admin/`, keep **Browser server origin** equal to
`http://127.0.0.1:5173`, expand the advanced bearer form and enter the token for
an explicitly granted account. Loopback HTTP does not support password-cookie
login. Vite proxies `/v1` to8000 by default and refuses an occupied5173.
The advanced token stays in browser memory, so reloading may require sign-in.

### Optional — point Vite at a different supported backend

Stop Vite with Ctrl+C. In the same `apps/admin-web` terminal, change the proxy
target to an existing trusted API origin and restart:

```powershell
$env:ADA_API_TARGET = 'https://your-private-ada-host.example'
npm run dev
```

That domain is a **placeholder**, not a deployed ADA host. The setting accepts
HTTPS or loopback HTTP and rejects credentials/path/query/fragment. The browser
origin remains the origin where Vite is serving your page.

To restore the default proxy, stop Vite, remove `ADA_API_TARGET` from that terminal's
environment and restart:

```powershell
Remove-Item Env:ADA_API_TARGET -ErrorAction SilentlyContinue
npm run dev
```

### Optional — preview the built web app locally

Stop the dev server, then from `apps/admin-web`:

```powershell
npm run build
npm run preview -- --port 4173
```

Open `http://127.0.0.1:4173/admin/`. Its login origin is now
`http://127.0.0.1:4173`. Preview is a local build check, not production deployment.

## 9. Use chat, memory, documents and the other implemented features

These Android controls are enabled by the authenticated server's capabilities.
A disabled/unavailable feature is not made available by asking the model to enable
it. Confirm the intended schema/provider/capabilities when a screen is missing.

### 9.1 Create a conversation and send your first message

1. Open **Chat → New conversation**.
2. Enter a **Conversation title**, for example `Developer test`.
3. Choose a **Chat style**. For an empty account, enter a **New style name** and
   tap **Create chat style**, then select the created style.
4. Under **Knowledge scope**, choose **New personal scope** for an isolated
   conversation, or choose your existing project scope to reuse its evidence.
5. Tap **Create conversation**.
6. Enter a short synthetic test message and tap **Send**.
7. Wait for the completed reply. Partial streaming text is labelled provisional;
   it is not yet a completed answer or verified source card.
8. Open the reply's source chips/cards when present to inspect original evidence.

Styles change expression. They do not share another user's knowledge or grant
permissions. A conversation preserves its selected style and prompt snapshot.
New personal scopes do not automatically reuse evidence from another project.

If creation has an uncertain outcome, refresh and inspect the conversation/style
list before creating another. Unlike message sending, these creation routes do
not have an exact request-ID replay contract.

### 9.2 Handle a running, disconnected or failed message

1. Return to the original conversation or **Return to pending message**.
2. Use **Check request** for an unknown outcome; the app checks its saved request ID.
3. If running, wait or choose the explicit generation **Stop** when offered.
4. If failed, **Retry original request** keeps the original message/options/ID.
5. If missing after verification, **Submit original request** uses that same ID.
6. Start a consciously new message only if you intend a different request.

A connection timeout does not prove generation failed. Repeated Send, logout,
clearing storage or editing the reserved operation are not recovery procedures.
Leaving/backgrounding chat detaches the stream observer; it does not cancel server
generation. **Stop generation** and **Stop playback** are different actions.

### 9.3 Save explicit memory and correct it

1. Open **Memory** and choose the same owned scope as the conversation.
2. Choose **Remember**.
3. Enter your note or select an exact passage from an owned user source.
4. Supply the subject, predicate, value and kind, plus effective dates if needed.
5. Review the exact evidence/annotation and explicitly save it.
6. Browse current, dated or history views and open an item for its source/version.
7. To correct a statement, review the replacement value, new evidence and effective
   time before confirming the correction.

Chat does not automatically extract durable facts. Model-generated text is not
eligible evidence for the direct user-assertion writer. A correction preserves
history instead of editing an old quote. Effective intervals are half-open;
timestamps must include a timezone. A dated validity query does not reconstruct
exactly what the server had stored at that historical date.

### 9.4 Import a text or Markdown document

1. Open **Documents** and choose the target owned scope.
2. Tap **Import text / Markdown**.
3. Choose a `.txt`, `.md` or `.markdown` UTF-8 file, or paste the document text.
4. Review the filename/type and optional availability dates.
5. Tap **Review upload**, inspect the exact content/scope, then **Upload reviewed document**.
6. Wait for the receipt to become **Ready**. Failed/incomplete imports are not
   searchable completed evidence.
7. In a conversation in that scope, enable the document-use option with memory
   enabled. New conversations use v4; old prompts need their explicit upgrade
   before document retrieval.
8. Open returned `[D...]` source cards to inspect the matching immutable version.

Text/Markdown imports retain their **64 KiB** Android / **256 KiB** server bounds.
Selected text PDFs have a separate capability, parser and limits; follow
[PDF ingestion](PDF-INGESTION.md) before enabling them. OCR, archives and arbitrary
URL crawling remain unavailable. Imported documents remain
untrusted; importing a file does not assert that every sentence is true. Use
**Upload a new version** to preserve a stable document identity with immutable
versions. Original saved replies keep their original source mappings.

### 9.5 Review memory suggestions and entities

For suggestions: open **Memory → Review memory suggestions**, choose the scope and
owned source/excerpt, then **Suggest memories from selected excerpt**. Review
each pending suggestion, its exact support and annotation; edit and preview the
specific revision if necessary, then explicitly accept or reject. Accepted wording
becomes a new endorsement, not a rewrite of the generated proposal/source.

For identities: open **Memory → People, projects and aliases**. Review an entity
and its scoped aliases before saving changes. Ambiguous identity choices require
explicit selection; merges and their reversal are reviewed operations. Names and
aliases never authorize access to another owner.

### 9.6 Use the read-only tool session

1. Open an owned conversation, then **Read-only tools**.
2. Enter the task and choose the allowed tools: calculator, owned memory lookup
   and/or owned source lookup.
3. Tap **Request tool session**.
4. When an exact step requires approval, tap **Review approval** and inspect its
   tool, arguments, scope and limits.
5. Explicitly approve or deny that step, then inspect its result/receipt.

Tools are a separate bounded session, not a promise that ordinary chat may run
arbitrary actions. Shell execution, external writes and automatic approval are
not available. A changed intent needs new approval; retry/restart checks the exact
saved operation before any explicit retry.

### 9.7 Generate a source-linked episode or queue maintenance

1. In a conversation, open **History & episodes**.
2. Select up to four complete messages for a supported summary/suggestion job.
3. Choose **Preview summary job** or **Preview memory suggestion job**.
4. Inspect the original source selection and explicitly tap **Queue job**.
5. Refresh/check the saved job until its actual state is terminal.
6. Open **Read summary and original sources** for the generated episode.

**Preview search index rebuild** is a separate scoped lexical-index operation;
it does not enable embeddings or change facts. Jobs need the bounded consolidation
worker enabled and available shared model capacity. Generated episodes are
navigation interpretations; they do not automatically become factual chat memory.
A suggestion job still requires the separate memory-review approval.

### 9.8 Change appearance, preferences and reviewed learning

For colors, open **Settings → Appearance** and choose **Oxford Blue** (default,
`#002147`), **Dark Red** (`#350616`) or **Olive Green** (`#3C4C24`), then the desired
light/dark mode. Android saves this locally. The admin dashboard has its own
appearance settings. Theme selection never changes accounts or permissions.

For wording, open a conversation and then **Settings → Interaction preferences**:

1. Select **This conversation**, its **knowledge scope**, its **chat style**, or
   **Account-wide defaults**.
2. Choose the available verbosity/initiative/formality/humor/cadence values.
3. Review and **Save reviewed preferences**.
4. Opt into bounded session tone only if desired; it starts disabled and can be reset.

Defaults apply to new conversations; reviewed conversation changes affect future
replies. Old prompts/completed replies retain their snapshots. These choices do
not alter factual retrieval or model/tool permissions.

For **Interaction learning and continuity**, first open a conversation so its
scope is selected. Learning starts off. Opt in, choose completed user messages as
wording evidence and save tentative observations. Review eligible suggestions
before approving/rejecting them. The default gate needs three distinct interactions;
retries/copies do not create independent evidence. Cross-scope reuse exports only
reviewed wording enums into opted-in scopes. Pause/reset controls affect live
derived learning; original sources/audit/historical replay can remain.

### 9.9 Record, review and send voice

1. Open an owned conversation. The microphone sits beside the message field.
2. **Tap** the microphone to open voice controls. Choose the installed recognition
   language (`en-US` by default), then tap **Record voice**. Allow microphone
   permission if asked. Wait for **Recording** before speaking; tap **Stop recording**
   to finish. The controls close when the final transcript reaches the composer.
3. For quick **push-to-talk**, **press and hold** that same microphone. Wait for
   **Recording**, speak, then **release** to finish. Partial words appear in the
   message field if the installed engine provides them. Releasing before setup
   finishes cancels the attempt; after allowing permission, hold again or use
   the tap/Record route. A recognizer may finish early on silence.
4. The final words appear in the ordinary **Message ADA** field. Existing typed
   text is included before the transcript. Correct, add or remove wording there.
   Partial recognition is provisional; editing becomes available after capture.
5. Wait for encrypted draft saving, then press the ordinary **Send** button.
   **This explicit Send approves exactly the displayed wording.** Recording,
   release, silence and editing do not send a message or approve a transcript.
6. Tap the microphone again for options: inspect **Original ASR words (generated)**,
   change language/voice, or **Discard voice draft**. Discarding restores the
   pre-recording typed text. The advanced review/approval controls remain available.

If a held gesture is cancelled or you leave the screen, incomplete recognition
is discarded. The final draft uses encrypted recovery and returns to the composer
after reconnecting to the same account/conversation; it never submits itself.
The original generated recognition remains separate from your final wording in
the reviewed-voice request, even though both text and voice now share an editor.

Input needs Android12/API31+ and an installed on-device recognition engine.
API 33+ also preflights the installed language. ADA does not download a model,
fall back to network ASR or upload audio. Text chat remains available without
microphone permission. Recording is bounded to 60 seconds; leaving the screen
or backgrounding cancels capture. Editing wording removes its earlier approval.

**Permission recovery:** Phase17-A now keeps the Record intent across ADA's own
microphone dialog and cancels it on real background/navigation/account changes.
Ordinary and permanent denial leave text available and explain settings recovery.
New hardware results and remaining gates are recorded in [STATUS](../plans/STATUS.md);
older installed APKs still need their own explicit upgrade. Use
[VOICE-VALIDATION](VOICE-VALIDATION.md) for the isolated device runner.

On the S24 FE/Android16, basic quiet en-US and airplane-mode recognition passed
two short controlled samples. This does not establish noisy-room/accent accuracy
or battery efficiency. Reviewed text is an explicit endorsement; the separate
original remains a generated interpretation, with no server audio hash.

### 9.10 Listen to a completed reply

1. Wait for an owned reply to complete.
2. Under Voice controls, choose an installed offline playback voice and speed
   (0.75×, 1×, 1.25× or 1.5×).
3. Tap **Read reply** on the completed reply.
4. Use **Stop playback** to stop local audio. Use generation **Stop** only when
   you intend to cancel a still-running server request.

Provisional streams, original ASR records and debug/source payloads are not read
as reply audio. Missing offline TTS voices leave text usable; install/select them
through the phone's speech-engine settings, not an ADA audio-upload service.

The S24 FE audit verified basic offline speaker rates, explicit Stop and activity
pause/no automatic resume. A native focus-interruption callback failed even when
a separate foreground app received audio focus. Root cause/audible call behavior
remain unresolved; use explicit **Stop playback** when changing audio activity,
and verify the new attribute/listener hardening on the intended engine. Unit or
emulator results alone do not close the physical interruption gate.

## 10. Use the command-line client

Initialize an operator terminal at the root, load your token as in section6, and keep the
API running in terminal A:

```powershell
.\.venv\Scripts\ada.exe chat --title 'Developer CLI test'
```

The CLI creates or opens an owned conversation and prints its conversation/scope
IDs. `/sources` shows actually cited evidence; `/trace` shows selected evidence
and omissions; `/retry` reuses the last request ID. Use `/quit` to leave chat.

Resume an actual saved UUID:

```powershell
$adaConversationId = Read-Host 'Conversation UUID to resume'
.\.venv\Scripts\ada.exe chat --conversation $adaConversationId
```

### Create a project scope and a clearly synthetic memory example

These examples deliberately save test evidence in a new scope. They are not facts
about your real project. Run them in a token-equipped client terminal:

```powershell
$adaScope = .\.venv\Scripts\ada.exe scopes create 'Developer memory demo' | ConvertFrom-Json
$adaScopeId = $adaScope.id
.\.venv\Scripts\ada.exe memory remember --scope $adaScopeId --subject 'Developer demo' --predicate color --value 'Oxford Blue' --kind preference --text 'The developer demo uses Oxford Blue.' --valid-from '2026-10-01T00:00:00Z'
.\.venv\Scripts\ada.exe memory list --scope $adaScopeId
.\.venv\Scripts\ada.exe memory search 'Developer demo color' --scope $adaScopeId
.\.venv\Scripts\ada.exe chat --scope $adaScopeId --title 'Developer memory demo'
```

To test a correction, retain the actual claim UUID returned by `remember`:

```powershell
$adaOldClaimId = Read-Host 'Actual claim UUID from the demo'
.\.venv\Scripts\ada.exe memory correct $adaOldClaimId --value 'Olive Green' --text 'The developer demo now uses Olive Green.' --effective-at '2026-10-08T00:00:00Z'
.\.venv\Scripts\ada.exe memory list --scope $adaScopeId --at '2026-10-05T00:00:00Z'
.\.venv\Scripts\ada.exe memory list --scope $adaScopeId --history
```

A historical query before the correction sees the older value. Source/claim IDs
printed before a write must be reused with identical input on an uncertain retry.
Do not invent a new ID just to suppress a conflict.

### Explicitly upgrade an old conversation's prompt when needed

```powershell
.\.venv\Scripts\ada.exe upgrade-prompt $adaConversationId
```

This is an audited change for that selected conversation, not routine daily startup.
New conversations use `ada-baseline-v4`; old ones retain their existing version.
v3 supports claim retrieval; document retrieval requires v4, memory enabled and
explicit document use. The CLI chat options currently cover claims/time/no-memory;
use Android or the documented HTTP contract for document opt-in and later UI flows.

## 11. Start and stop ADA on an ordinary day

### Startup after the one-time setup

Use **three PowerShell windows**: A for the API, B for the proxy, C for checks.
In each, first enter the actual checkout:

```powershell
Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
```

#### 1. Window C — check prerequisites

Start Docker Desktop and wait for its engine. Start the Ollama Windows app if
it is not already running. Connect Tailscale on the laptop, then run:

```powershell
docker compose up -d --wait db
docker compose ps db
ollama list
.\.venv\Scripts\ada.exe doctor
tailscale status
tailscale serve status
```

Expect `db` running/healthy, schema0021, and the **exact** `ADA_OLLAMA_MODEL` tag
installed. This laptop was observed using `qwen3.8-27b-uncensored:latest`; preserve
your deliberate model choice. Do not pull the older example tag merely to start
ADA. If11434 already responds, do not start a second `ollama serve`.

Serve should show your HTTPS hostname, **tailnet only**, proxying to
`http://127.0.0.1:18764`. If it says `No serve config`, enable the route once:

```powershell
tailscale serve --bg --https=443 http://127.0.0.1:18764
tailscale serve status
```

Complete the Tailscale approval link if requested. The background Serve setting
normally persists; this is not a command to repeat on every launch. Do not enable
Funnel. If `tailscale funnel status` repeats the same **tailnet only** route, that
wording does not indicate a public route.

If an API/proxy is already healthy, reuse it instead of starting a duplicate.
An optional reviewed supervisor may already own it; use its
[operations procedure](ALWAYS-ON-OPERATIONS.md), rather than competing with it.

#### 2. Window A — start the API

```powershell
.\scripts\start.ps1
```

Expect progress followed by:

```text
ADA API is running at http://127.0.0.1:8000 (one worker).
  Readiness: http://127.0.0.1:8000/health/ready (expect status: ready)
  Local API explorer: http://127.0.0.1:8000/docs
  With the private proxy and HTTPS route running:
    Admin: https://windows-asus.tail110867.ts.net/admin/
    Android server: https://windows-asus.tail110867.ts.net
Leave this window open. Press Ctrl+C to stop ADA.
```

The script stays in the foreground. **The absent PowerShell prompt means it has
not returned; it does not mean startup is stuck.** Earlier versions could remain
entirely blank because console/access logging was disabled. The new banner means
the listener opened; it does not prove the database or model is ready. In window C:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health/live' -TimeoutSec 10
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready' -TimeoutSec 10
```

Expect `ok`, then `ready` with schema0021. Resolve failure here before testing
the phone. A cold startup may take time; progress identifies its last stage.
If no progress appears at all or it stops responding, use section12's checks.

#### 3. Window B — start the private proxy

```powershell
.\scripts\start-private-proxy.ps1 -CheckOnly
.\scripts\start-private-proxy.ps1
```

Expect `Valid configuration`, then Caddy running on127.0.0.1:18764. Leave this
window open too. `-CheckOnly` validates and exits; it does not start a proxy.
Warnings about disabled automatic HTTPS or an unformatted Caddyfile are nonfatal
with this template: Tailscale supplies external HTTPS. A bind/checksum/validation
error is a failure. If Caddy is already running, do not launch another copy.

#### 4. Window C — verify the complete route

```powershell
Invoke-RestMethod 'http://127.0.0.1:18764/health/ready' -TimeoutSec 10
Invoke-RestMethod 'https://windows-asus.tail110867.ts.net/health/ready' -TimeoutSec 10
Start-Process 'https://windows-asus.tail110867.ts.net/admin/'
```

Both checks should report `ready`/0021. Opening the dashboard HTML alone does not
prove its API works: Caddy can serve `/admin/` while8000 is unavailable and API
calls return502. `/` may return404; use `/admin/` for the dashboard.

#### 5. Connect the clients

- **Laptop browser:** use the opened HTTPS `/admin/` page. Browser server origin
  is `https://windows-asus.tail110867.ts.net`. Sign in with your enrolled username
  and password; this laptop's previously verified admin identifier is
  `gourishankar-admin`.
- **S24 FE:** connect Tailscale to the same tailnet. In ADA use server
  `https://windows-asus.tail110867.ts.net` without `/admin/`, check the server,
  then sign in with username/password. A valid saved session can renew itself.

Tailscale needs to be connected on both devices. USB debugging, ADB reverse,
Vite5173 and manual TLS files are unnecessary for this route. Keep the laptop
awake and connected; a sleeping/powered-off laptop cannot serve ADA. The startup
script does not change Windows power settings or install automatic startup.

You do **not** clone again, recreate accounts, reset passwords, reinstall
dependencies, rebuild unchanged clients, re-pull an installed model or run
migrations on every launch. Use section5 when source/schema requirements change.

### Shutdown

1. Finish or deliberately stop the operations you want stopped. Merely closing
   Android does not cancel server generation or a queued job.
2. Stop your private-proxy terminal with **Ctrl+C**.
3. Stop your ADA API terminal with **Ctrl+C**.
4. If you used the optional Vite/USB developer workflow, stop Vite and remove only
   the USB mapping you created:

   ```powershell
   adb -d reverse --remove tcp:8000
   ```

5. If you want to stop the repository's database while preserving its data:

   ```powershell
   docker compose stop db
   ```

Do not use `docker compose down -v` as ordinary shutdown/troubleshooting: `-v`
removes the database volume. Do not clear/uninstall Android to hide a pending
request; doing so removes local credentials/drafts/recovery but not server records.

When ending a token-equipped operator session, remove the in-memory token/header
variables and clear the clipboard as appropriate:

```powershell
Remove-Item Env:ADA_TOKEN -ErrorAction SilentlyContinue
Remove-Variable adaHeaders, adaIssued, adaRotated -ErrorAction SilentlyContinue
Set-Clipboard -Value ''
```

## 12. Troubleshoot setup and runtime problems

### First isolate which layer is failing

Run these from a computer terminal at the root, in this order:

```powershell
docker compose ps db
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic heads
ollama list
.\.venv\Scripts\ada.exe doctor
Invoke-RestMethod 'http://127.0.0.1:8000/health/live'
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
Invoke-RestMethod 'http://127.0.0.1:18764/health/ready'
tailscale serve status
Invoke-RestMethod 'https://windows-asus.tail110867.ts.net/health/ready' -TimeoutSec 10
```

Then check password sign-in, your admin grant if relevant, and the client origin.
For the optional bearer path, verify `/v1/me`. Keep secrets/private bodies out of shared
diagnostics. Environment `ADA_...` values override `.env`; a stale shell override
can point an otherwise correct checkout at a different database/provider.

### Common problems and concrete remedies

| Symptom | Check and next step |
|---|---|
| `git`, `py`, `docker`, `node`, `npm` or `ollama` is not recognized | Install the relevant tool, reopen PowerShell, and repeat section 2's version check. Python specifically needs `py -3.12` for setup. |
| PowerShell refuses to run `.ps1` files | Inspect the repository script. If your policy permits, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` for this terminal; managed machine policy may require your administrator's help. No machine-wide execution-policy change is needed. |
| Docker daemon/engine cannot be reached | Open Docker Desktop, wait for the engine, and check `docker info`. Resolve its WSL/virtualization setup before retrying Compose. |
| PostgreSQL remains unhealthy | Check `docker compose ps db` and `docker compose logs --tail 50 db` locally. Verify disk/service initialization and intended credentials. Do not delete the volume as a first fix. |
| Database authentication fails after editing `.env` | Existing PostgreSQL volumes retain the initialized role password; changing `.env` does not rotate it. Restore matching credentials or perform an explicit operator-controlled password change. Check the connection URL's port and URL encoding. |
| `start.ps1` stays running with no prompt | Normal for a foreground server. Look for startup progress and the running banner, then check8000 `/health/ready` from another terminal. Older code can remain blank while healthy. Leave the window open. |
| Startup stays on one progress line and8000 never responds | Check Docker health and `doctor` in a separate terminal; note the last stage. `Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue` shows listeners. If it remains unresponsive, Ctrl+C in that window and retry once, retaining the fixed error/status code. Do not run duplicates or reset the database. |
| The API window stops or returns to a prompt by itself | It is no longer serving. Preserve the last fixed status/exit code and time, then check8000. A proxy window or installed Docker container does not keep the API alive. A recurring unexplained exit requires investigation; no crash cause was confirmed in this startup session. |
| Port5433/8000/18764/5173 is occupied | Inspect with `Get-NetTCPConnection -State Listen -LocalPort 5433,8000,18764,5173 -ErrorAction SilentlyContinue`. Identify the owner before stopping anything. Reuse a healthy existing instance. Vite uses strict5173. |
| `inference_owner_already_running` or `already_running` | Another foreground/supervised runtime holds the ownership gate. Identify it and use its normal stop procedure before starting another. Never delete a lock to bypass a live owner. |
| API address8000 needs to change | Start with `scripts/start.ps1 -Port 8001`; also change the upstream8000 in the selected Caddyfile and restart Caddy. Update optional direct Android/USB/Vite paths too. Keep the external HTTPS origin unchanged when only the internal port changes. |
| `/health/live` refuses the connection | The API is not listening there. Check terminal A, its startup error, working directory and configured port. Docker PostgreSQL alone does not start ADA. |
| Liveness works, but `/health/ready` returns503 `database_not_ready` | Check database connectivity and `alembic current` versus `heads`. Back up/stop API/migrate the intended database using section5; current source expects0021. Never stamp over missing tables. |
| Admin opens, but sign-in says unavailable; proxy readiness is502 | Test8000 first, then18764, then HTTPS. Caddy can serve HTML with its API upstream down. Restore the missing layer; keep browser origin equal to the HTTPS address bar. For the optional Vite workflow, check its target instead. |
| Local18764 works but tailnet HTTPS fails | Check Tailscale connected on both devices, `tailscale serve status`, exact hostname and target18764. A certificate failure is not fixed by disabling TLS verification. |
| Caddy warns automatic HTTPS is disabled | Expected for `Caddyfile.tailnet.example`: it is loopback HTTP behind Tailscale Serve. Confirm the outer HTTPS readiness check. Do not replace it with a LAN/public bind. |
| `Cannot read the built-admin directory` | Set `ADA_ADMIN_DIST` to a literal absolute forward-slash path in `.env`; build with `npm ci`/`npm run build` from `apps/admin-web`. Current proxy code passes Python through stdin to preserve quotes in PowerShell5.1. Check that your script includes that correction. |
| Password sign-in fails over HTTP or origin mismatch | Use the private HTTPS origin for password login. Match `ADA_BROWSER_ORIGIN`, browser address and origin field exactly, omitting `/admin/`. Restart the API after environment changes. HTTP5173 is the advanced bearer workflow only. |
| Admin says monitoring is unavailable | Confirm supported current schema/source and proxy reachability. Apply intended migrations after backup, restart the backend, and retry; older monitoring-readiness problems are not fixed by repeated login. |
| Token rejected/HTTP401 | Use the current secret for an existing account, without `Bearer ` in client fields. Rotation revokes the old token. A username/account UUID/password is not a bearer token. |
| Admin Access denied/HTTP403 | A valid login still needs an explicit monitoring grant. Inspect `login-accounts` locally and grant the intended exact UUID. User/style names do not grant roles. |
| `create-user` reports an existing name | Reuse its saved token, or deliberately rotate for that exact existing name if lost. Do not create a different account to recover its data. |
| `grant-admin` rejects the argument | It accepts an account UUID, not the name. Use `create-user.user_id` or authenticated `/v1/me.id` from the intended server. |
| `doctor` reports configured model missing | Start Ollama, inspect `ollama list`, and match `ADA_OLLAMA_MODEL` exactly. Pull an available intended tag if needed; restart ADA after configuration changes. |
| `ollama pull` reports manifest/tag not found | The requested tag is unavailable to that installation. Choose a verified available tag, update `.env`, run `doctor`, and separately validate structured features. Do not treat the repository's default as an availability guarantee. |
| Model generation is slow or fails/HTTP502 | Check the exact installed model, model-server reachability, available memory and timeout. Metadata health does not prove inference. Keep one worker/initial parallelism 1; measure before increasing limits. |
| HTTP503 busy or429 throttled | Respect Retry-After and preserve the original request/operation ID. Chat/tools/jobs share bounded capacity. Repeated immediate Send/login/refresh can worsen contention or throttling. |
| Android `SDK location not found` | Check `ANDROID_HOME` or ignored `local.properties` and SDK Manager's actual path. Install Platform 36/Build-Tools 35.0.0 and accept licenses. |
| Gradle says JDK 21 required or uses another Java version | Set `JAVA_HOME` in that terminal and Android Studio's Gradle JDK, then check `gradlew.bat --version`. Do not fix it by upgrading Gradle/AGP indiscriminately. |
| npm refuses the engine, or `npm ci` fails on lock consistency | Use Node 24.12.0/npm 11.6.2 and the committed package lock. Investigate an actual manifest/lock mismatch; do not regenerate locks merely to bypass the check. |
| Phone absent, `unauthorized` or `offline` in ADB | Unlock it, enable USB debugging, accept the RSA dialog, check a data-capable cable/USB driver, and use Android Studio's Connection Assistant. |
| ADB reports more than one device | Use `-d` for a single physical phone or `-s` with the intended device serial. Do not select the first device blindly. |
| Phone cannot reach localhost while computer health checks work | Keep API running, reconnect USB and recreate `adb -d reverse tcp:8000 tcp:8000`. Phone URL is127.0.0.1:8000; emulator URL is10.0.2.2:8000. |
| Android rejects cleartext or server URL | Use the debug build/documented loopback URLs, or a separately configured trusted HTTPS origin. Omit paths, userinfo/query/fragment; do not substitute an arbitrary LAN HTTP URL. |
| APK install reports incompatible signature | Use the same intended signing/debug key/build source. Uninstalling clears local account/recovery state; review pending work before deliberately replacing an installation. |
| Android Send stays disabled | Check empty/oversized input, active recording, pending request, encrypted-storage save/failure and capabilities. Resolve/check the original operation; do not clear storage to force a new ID. |
| HTTP409 after retry | Reuse the original ID with identical payload/options; check conversation revision/history. A changed payload under an existing ID conflicts deliberately. |
| HTTP413/422 on import or forms | Check actual byte/Unicode limits, strict UTF-8, file type and timezone-bearing dates. Android import limit 64 KiB; server 256 KiB. Review the bounded input instead of renaming a binary file. |
| Memory/document not used in a reply | Check owner/scope, ready/availability/valid time, memory/document toggles, saved prompt version and retrieval/source details. Saving in another scope does not enable cross-scope retrieval. |
| Tool/proposal/episode unavailable or fails | Check advertised native capabilities, selected sources, structured model support, prompt/size bounds and shared capacity. A normal text reply does not prove every structured feature works. |
| Consolidation job stays queued | Check `ADA_CONSOLIDATION_WORKER_ENABLED=true`, API lifespan still running and admission capacity. Restart after changing settings; inspect the exact saved job. |
| Microphone Allow/Deny returns Interrupted | Permission-intent hardening is implemented; confirm you installed the intended app version and check OS microphone permission. Retry from the same owned foreground conversation or use text. Active revocation/settings-return target checks remain open in17A. |
| Missing language/recognition engine or no transcript | Check Android 12+, installed on-device engine and selected installed language. Install language through the speech service's own settings if available; ADA has no network fallback. Wait for Recording before speaking, or use text. |
| No offline playback voice/audio | Check an installed eligible TTS voice, media volume and current output route. Native focus behavior remains under 17A-02 investigation; use explicit Stop playback. |
| A pending reply seems lost after restart | Reconnect the same verified account/server, open its conversation and Check request. GET recovery retains the ID; an uncertain transport result is not a license to send a duplicate. |

### Operator recovery of genuinely stale legacy requests

Only after determining that an old request is genuinely interrupted, the local
operator can mark it retryable:

```powershell
.\.venv\Scripts\ada.exe recover-stale --older-than-seconds 300
```

300 seconds is appropriate for the default 180-second timeout; the CLI requires
an age at least `ADA_TIMEOUT_SECONDS + 60`. Adjust upward if your configured
timeout differs. This is an operator mutation, not routine startup or a shortcut
for a slow healthy request. The client still explicitly retries the original ID.

## 13. Run developer verification

Run checks appropriate to the change. They are not daily prerequisites for simply
using the installed app. Keep validation data and credentials separate from real
accounts. Source/tests/OpenAPI determine implemented behavior; roadmap files do not.

### Python/SQLite and formatting

From the root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests migrations scripts
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations scripts
```

Default fixtures use migrated SQLite. PostgreSQL copies are skipped without a
dedicated fixture URL; a green SQLite run is not PostgreSQL concurrency validation.
Native-model probes have separate opt-in conditions; inspect the actual skips.

### PostgreSQL verification

With the intended PostgreSQL connection configured, run:

```powershell
.\scripts\test-postgres.ps1
```

The helper prepares the dedicated **`ada_phase2_test`** database and runs the full
suite with that test URL in its child environment. It never points fixtures at
the application's database. Its operator needs permission to create that test
database, or must pre-create it on the intended instance.

For the repository's default Docker instance, if the test database does not yet
exist and automatic creation is unavailable, an operator can create it with:

```powershell
docker compose exec -T db createdb -U ada ada_phase2_test
```

Do not set `ADA_TEST_DATABASE_URL` to the real `ada` database. See
[the test helper](../scripts/test_postgres.py) and [validation notes](VALIDATION.md).

### Android build/UI verification

With JDK 21/SDK configured:

```powershell
Push-Location apps/android
.\gradlew.bat testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest
Pop-Location
```

The existing `apps/android/scripts/verify-*-emulator.ps1` helpers are for a
**disposable emulator**, not your daily-use phone. For example, only after creating
and selecting an actual disposable emulator with that ID:

```powershell
Push-Location apps/android
.\scripts\verify-voice-emulator.ps1 -Device emulator-5556
Pop-Location
```

The script uses a disposable fake-model HTTP server and synthetic audio adapters;
it may reset/uninstall the normal debug package on its selected emulator. It does
not prove real microphone/speaker accuracy. Bounded separate-package physical
verification exists; use its explicit procedure in the
[17A plan](../plans/phase-17-a-s24-fe-validation-and-hardening.md) and Android README.
Do not pass a personal phone into an emulator-only helper.

### Admin web checks

Stop a conflicting Vite listener before checks that use its port. Use the pinned
toolchain and a reachable dedicated PostgreSQL test database for E2E:

```powershell
Push-Location apps/admin-web
npm ci
npm run contracts:check
npm run typecheck
npm run lint
npm run test -- --run
npm run build
npx playwright install chromium
npm run test:e2e
Pop-Location
```

E2E uses disposable migrated PostgreSQL schemas, synthetic operators/data and
explicit fake inference. It does not validate the real model or migrate your
application. See [admin web details](../apps/admin-web/README.md).

## 14. Find implementation details and current limits

| Topic | Reference |
|---|---|
| API ownership, transactions, snapshots and capacity | [Architecture](ARCHITECTURE.md) |
| Exact current HTTP contract | [OpenAPI](../contracts/openapi.json), [contract notes](../contracts/README.md) |
| Android dependencies/build/recovery | [Android README](../apps/android/README.md) |
| Admin web/proxy/monitoring | [Web README](../apps/admin-web/README.md), [monitoring policy](ADMIN-MONITORING.md) |
| Memory/evidence/history | [Memory policy](PHASE1-MEMORY.md), [retrieval policy](PHASE2-RETRIEVAL.md) |
| Document constraints/versioning | [Document ingestion](DOCUMENT-INGESTION.md) |
| Selected text PDFs and parser setup | [PDF ingestion](PDF-INGESTION.md) |
| Projects, tasks and reviewed briefs | [Projects and follow-through](PROJECTS-AND-FOLLOW-THROUGH.md) |
| Optional questions, reminders and idle review | [Curiosity](CONVERSATIONAL-CURIOSITY.md), [reminders](DURABLE-SCHEDULING-AND-REMINDERS.md), [idle review](IDLE-REFLECTION-AND-DREAM-REVIEW.md) |
| Private routing and password sessions | [Windows/Tailscale setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md), [password login](PASSWORD-LOGIN-AND-SESSIONS.md) |
| Reviewed host supervision and recovery | [Always-on operations](ALWAYS-ON-OPERATIONS.md) |
| Optional hybrid retrieval, disabled by default | [Embedding policy and evaluation requirements](EMBEDDINGS-AND-HYBRID-RETRIEVAL.md) |
| Entities/reviewed suggestions | [Entities](ENTITIES-AND-ALIASES.md), [memory review](MEMORY-PROPOSALS-AND-REVIEW.md) |
| Tool approval/receipts | [Tools and agent loop](TOOLS-AND-AGENT-LOOP.md) |
| Generated episodes/jobs | [Episodes and consolidation](EPISODES-AND-CONSOLIDATION.md) |
| Preferences/learning | [Interaction preferences](INTERACTION-PREFERENCES-AND-AFFECT.md), [learning and continuity](INTERACTION-LEARNING-AND-CONTINUITY.md) |
| Streaming/reconnect/Stop | [Streaming and cancellation](STREAMING-AND-CANCELLATION.md) |
| Voice/privacy and pending phone fixes | [Voice interface](VOICE-INTERFACE.md), [Phase17-A plan](../plans/phase-17-a-s24-fe-validation-and-hardening.md) |
| Checks actually run/skips/remaining targets | [STATUS](../plans/STATUS.md), [WORKLOG](../plans/WORKLOG.md) |

Basic S24 FE/Android16 recognition/offline speaker/recovery/font checks are recorded.
Permission-intent/lifecycle hardening is implemented; active revocation/settings
and audible native focus-stop gates remain open. Representative
speech, accessory/call routing, speech-service resource/battery, older Android,
release HTTPS/manual accessibility and intended installation checks remain distinct
from the successful local tests. This guide does not claim those gates passed.

Automatic background listening, arbitrary external/shell actions, public signup
and OCR remain unavailable. Local mobile draft generation remains disabled.
PDFs, public web research, reminders and idle work require their explicit
capability/setup/consent; a running server does not enable them all. Keep one
Uvicorn worker, authenticated owned API access and deliberate reviewed writes.

### How this guide was checked

Commands/paths/options were checked against setup/start/configuration scripts,
CLI help, actual Alembic head, OpenAPI, client source/pins and current test/status
records. The22October startup check observed database readiness at0021 through
API8000, Caddy18764 and Tailscale HTTPS, plus the admin page and installed model
metadata. A temporary upstream interruption was observed; its cause was not
confirmed. Native PowerShell5.1/7 failure paths and isolated real IPv4/IPv6
listener/bind-failure checks cover the new banner. Official installation/device
pages retain their13October review date. Exact results/skips are in
STATUS/WORKLOG. A fresh
installation, production migration, model download/inference or deployment was
not performed while writing this document.
