# How to use ADA — developer setup and everyday operation

For your current laptop, start with
[Windows + Tailscale private setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md): corrected
`.env`, managed TLS, exact HTTPS/password login, manual startup and device steps.
It records the separately authorized setup after the earlier implementation runs.

## Current Phase22 sign-in update

Current source requires0016. Follow the [password/session installation guide](PASSWORD-LOGIN-AND-SESSIONS.md)
for pinned installation, backup/migration, `ada login-accounts`, hidden-prompt
`ada set-password ACCOUNT_UUID login`, exact HTTPS browser origin, ordinary
username/password use and troubleshooting. This is now the normal client sign-in;
older token instructions below remain the explicit legacy/development path.
No password is derived from an existing token/name and no live password was set
by implementation. Preserve owner UUIDs and separate admin grants.

Updated **16 October 2026**, for Phase 20 readiness tooling and database head **0015**.
Phase21 now adds saved Android HTTPS addresses, pre-login readiness and separately
installed private routes; see [PRIVATE-NETWORK-CONNECTIVITY](PRIVATE-NETWORK-CONNECTIVITY.md).
No remote route was deployed by implementing that phase.
This guide covers the implemented server, Android app and admin dashboard through
Phase18. Phase17-A hardening is implemented with remaining physical audio gates;
Phase19 remains conditional and unimplemented. See [security and operations](SECURITY-AND-OPERATIONS.md)
for device credentials, explicit deletion, encrypted backups and isolated restoration.

Use this guide for the current end-to-end setup. Older phase documents describe
their own historical migration requirements; they are not instructions to stop a
current installation at 0004, 0005 or 0007. Check the actual head whenever you change
source versions. Writing this guide did not install, migrate or deploy anything.

For the separately authorized 2026-10-16 local startup and the actual Docker
database port5433, see [Windows database administration](DATABASE-ADMINISTRATION-WINDOWS.md).
That single guide covers database access, supported edits, migrations, encrypted
recovery, optional reset and daily service startup. The fresh database check found
head0015 already installed; earlier0005 observations remain historical.

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
through the web development proxy to that same API. Neither client connects
directly to PostgreSQL or Ollama.

For the local Windows workflow, only PostgreSQL is in Docker. Python and Ollama
run natively. There is no command here to start a Docker container for the API.

| Component | Default address | Purpose |
|---|---|---|
| ADA API on the computer | `http://127.0.0.1:8000` | Authentication, chat and owned data APIs |
| API explorer | `http://127.0.0.1:8000/docs` | Inspect and try the implemented API |
| API liveness | `http://127.0.0.1:8000/health/live` | Is the API process responding? |
| API readiness | `http://127.0.0.1:8000/health/ready` | Is the database reachable at the required schema? |
| PostgreSQL host port | `127.0.0.1:5432` | Server/operator access; configurable with `POSTGRES_PORT` |
| Ollama | `http://127.0.0.1:11434` | Server-side model provider |
| Admin web development page | `http://127.0.0.1:5173/admin/` | Browser dashboard |
| Admin **Browser server origin** field | `http://127.0.0.1:5173` | The browser's origin; omit `/admin/` |
| Android emulator API URL | `http://10.0.2.2:8000` | Emulator access to the computer's API |
| USB phone API URL, after ADB reverse | `http://127.0.0.1:8000` | Phone-to-computer forwarding over USB |

**8000 is the backend. 5173 is the web frontend.** The correct address depends on
the client and input field. On a phone, `127.0.0.1` refers to the phone unless
the documented USB reverse mapping is active.

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
| B — operator/client | Health checks, token/account operations and optional CLI chat |
| C — web | Foreground Vite admin development server |
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

For this source version, both head/current should report **0016**. `alembic check`
should find no new upgrade operations. Run the chain to the actual head; do not
edit released migration files or use `stamp head` to bypass missing schema changes.

### Step 5 — start Ollama and install/select the model

Open the installed Ollama Windows application. Its normal Windows installation
runs in the background and serves port 11434. Check it from terminal A or B:

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

Expected: database schema 0015, the configured model tag, and that model in the
installed list. `doctor` checks schema/model metadata; it does not prove that a
model can successfully complete every chat, tool or summary request.

If it says `FAKE provider selected`, no real model will run. Set
`ADA_PROVIDER=ollama` and restart the API when ready.

### Step 7 — start the API

In terminal A, from the root:

```powershell
.\scripts\start.ps1
```

Leave terminal A running. The script binds `127.0.0.1:8000`, uses **one Uvicorn
worker**, and disables access logging. A backend terminal that exits is not a
running backend. Configuration changes require an API restart.

In terminal B:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health/live'
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
```

Expected: `status: ok`, then `status: ready` and `schema: 0015`.
Readiness checks the database/schema, not model-generation success. A running
process with a failing readiness endpoint is not ready for client use.

### Step 8 — create your account and verify the token

Keep terminal A running and follow section 6 in terminal B. Account creation is a
local operator command using the configured database; subsequent token checks use
the running API. There is no public signup page.

## 5. Upgrade an existing installation

Skip account creation if you already have the account and its token. Keep existing
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
The normal recovery tool supports reviewed0015/v1 and0016/v2. Other older heads need their own
previously verified protected recovery procedure before migration; no tool upgrades
the source merely to make a backup possible. Verify the actual head privately.
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
chain to 0015. Adding code to the checkout never performs this upgrade automatically.
Do not downgrade populated history as a routine troubleshooting step.

## 6. Create an account and verify authentication

### New account

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

### Existing account/token

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

Alternatively, use the actual UUID returned in `$adaIssued.user_id` for a newly
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

### Step 3A — connect the Samsung S24 FE over USB

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
adb -d reverse tcp:8000 tcp:8000
adb -d install -r "$adaRepo/apps/android/app/build/outputs/apk/debug/app-debug.apk"
adb -d shell am start -n dev.ada.assistant.debug/dev.ada.assistant.MainActivity
```

Keep USB connected and terminal A's API running. Recreate the reverse mapping
after reconnecting/restarting the phone or ADB if it is no longer present.
Use `adb reverse --list` for diagnosis; it does not start the backend.

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
   - USB phone: `http://127.0.0.1:8000`, after the reverse mapping.
   - Emulator: `http://10.0.2.2:8000`.
   - Separately configured trusted HTTPS server: its HTTPS origin.
2. Enter your issued token in **Bearer token**, without a `Bearer ` prefix.
3. Tap **Connect**.
4. Wait for the verified account and conversation list.

Enter an origin only: do not append `/docs`, `/v1`, `/admin` or a query string.
Do not enter database credentials, an Ollama URL or the web frontend's port 5173.

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
token/account UUID. The current backend must be at head **0016**. Admin access
requires an explicit monitoring grant; migration alone never grants a role.

### Step 2 — install locked web dependencies and start Vite

In terminal C, initialized at the root:

```powershell
node --version
npm --version
Push-Location apps/admin-web
npm ci
npm run dev
```

Leave this terminal open. The npm engine check expects Node 24.12.0/npm 11.6.2.
Run `npm ci` after relevant lockfile updates, not on every daily launch. It replaces
the dependency installation; stop the running web server first.

Expected: Vite serves **`http://127.0.0.1:5173/admin/`**. The configured port is
strict; if another process owns 5173, Vite fails rather than silently choosing 5174.

### Step 3 — enter the two login fields

Open **http://127.0.0.1:5173/admin/** in the browser.

| Field | Enter |
|---|---|
| Browser server origin | `http://127.0.0.1:5173` |
| Bearer token | Your current token for the explicitly granted account; no `Bearer ` prefix |

The browser origin **5173 is correct**. Relative `/v1` calls go through Vite's
fixed proxy to **`http://127.0.0.1:8000`**. Do not replace the browser-origin field
with the backend's 8000 address to fix a database or proxy failure.

After sign-in, verify the displayed operator/server and open Overview, Requests,
request detail, Providers/limits or Audit. The dashboard is read-only monitoring;
it does not approve tools, grant roles, edit prompts or reveal another user's chat.

The token lives in browser memory. Reload/closing the page can require sign-in
again. Appearance settings persist separately; a saved theme is not a saved login.

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

Android's import limit is **64 KiB**; the server route accepts up to **256 KiB**.
PDF/OCR, archives and URL crawling are not implemented. Imported documents remain
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

1. Open an owned conversation and expand **Voice controls**.
2. Use **Recognition language: `en-US`**, or another installed on-device language.
3. Tap **Record voice** and choose microphone permission if prompted.
4. Wait until **Recording** appears before speaking. Choose **Stop recording**
   to finish or **Discard recording** to abandon it.
5. Review **Reviewed wording**. Use **Original ASR words (generated)** to inspect
   what recognition originally produced; edit any misheard words.
6. Select **I approve this wording for this conversation**.
7. Wait for encrypted storage to finish, then tap **Send reviewed voice**.

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

Initialize terminal B at the root, load your token as in section 6, and keep the
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

1. Start Docker Desktop and wait for its engine.
2. Start Ollama if it is not already running in the background.
3. At the repository root:

   ```powershell
   docker compose up -d --wait db
   .\.venv\Scripts\ada.exe doctor
   .\scripts\start.ps1
   ```

4. In another terminal, verify `/health/ready`.
5. For the USB phone, reconnect/unlock it. In an Android terminal, use your actual
   SDK path (the example is the default Windows location) and recreate forwarding:

   ```powershell
   $adbPath = Join-Path $env:LOCALAPPDATA 'Android/Sdk/platform-tools/adb.exe'
   adb -d reverse tcp:8000 tcp:8000
   ```
6. Open the installed Android app. A saved session is re-verified; enter a current
   token if reconnect is required.
7. If monitoring is needed, start `npm run dev` from `apps/admin-web`, open the
   `/admin/` page, and sign in with your explicitly granted account.

You do **not** clone again, recreate users, rotate tokens, reinstall dependencies,
re-pull an installed model or run migrations on every launch. Migrate when the
intended source/schema version changes, using section 5.

### Shutdown

1. Finish or deliberately stop the operations you want stopped. Merely closing
   Android does not cancel server generation or a queued job.
2. Stop your Vite terminal with **Ctrl+C**.
3. Stop your ADA API terminal with **Ctrl+C**.
4. Remove only the USB mapping you created when you no longer need it:

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
```

Then verify your token via `/v1/me`, your admin grant if relevant, and finally the
client's URL/USB mapping/proxy. Keep secrets/private response bodies out of shared
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
| Port5432/8000/5173 is occupied | Inspect with `Get-NetTCPConnection -State Listen -LocalPort 5432,8000,5173`. Identify the owner before stopping anything. Existing native PostgreSQL may be intentional. Vite uses strict port 5173. |
| API address8000 needs to change | Start with `scripts/start.ps1 -Port 8001`; update Android URL/USB reverse and Vite `ADA_API_TARGET` together. Changing only one client setting leaves other paths pointing at 8000. |
| `/health/live` refuses the connection | The API is not listening there. Check terminal A, its startup error, working directory and configured port. Docker PostgreSQL alone does not start ADA. |
| Liveness works, but `/health/ready` returns503 `database_not_ready` | Check database connectivity and `alembic current` versus `heads`. Back up/stop API/migrate the intended database using section 5; current source expects0016. Never stamp over missing tables. |
| Admin login says “The server is unavailable or busy” | First check readiness on 8000, not 5173. Then check Vite's proxy target and the API's capacity/Retry-After. A running backend with old schema is still not ready. Keep browser origin 5173; do not substitute 8000. |
| Admin says monitoring is unavailable | Confirm supported current schema/source and proxy reachability. Apply intended migrations after backup, restart the backend, and retry; older monitoring-readiness problems are not fixed by repeated login. |
| Token rejected/HTTP401 | Use the current secret for an existing account, without `Bearer ` in client fields. Rotation revokes the old token. A username/account UUID/password is not a bearer token. |
| Admin Access denied/HTTP403 | The token may be valid but its account lacks a current explicit monitoring grant. Obtain its authenticated `/v1/me.id`, then the local operator grants that exact UUID. User/style names do not grant roles. |
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
| First microphone Allow/Deny returns Interrupted | Known 17A-01. Confirm actual phone permission; if granted, tap Record again from the same owned foreground conversation. Denial/text/settings handling remains a planned fix. |
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
not prove real microphone/speaker accuracy. A non-destructive physical runner is
planned in 17A-03; do not pass a personal phone into an emulator-only helper.

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
| Optional hybrid retrieval, disabled by default | [Embedding policy and evaluation requirements](EMBEDDINGS-AND-HYBRID-RETRIEVAL.md) |
| Entities/reviewed suggestions | [Entities](ENTITIES-AND-ALIASES.md), [memory review](MEMORY-PROPOSALS-AND-REVIEW.md) |
| Tool approval/receipts | [Tools and agent loop](TOOLS-AND-AGENT-LOOP.md) |
| Generated episodes/jobs | [Episodes and consolidation](EPISODES-AND-CONSOLIDATION.md) |
| Preferences/learning | [Interaction preferences](INTERACTION-PREFERENCES-AND-AFFECT.md), [learning and continuity](INTERACTION-LEARNING-AND-CONTINUITY.md) |
| Streaming/reconnect/Stop | [Streaming and cancellation](STREAMING-AND-CANCELLATION.md) |
| Voice/privacy and pending phone fixes | [Voice interface](VOICE-INTERFACE.md), [Phase17-A plan](../plans/phase-17-a-s24-fe-validation-and-hardening.md) |
| Checks actually run/skips/remaining targets | [STATUS](../plans/STATUS.md), [WORKLOG](../plans/WORKLOG.md) |

Basic S24 FE/Android16 recognition/offline speaker/recovery/font checks are recorded.
Permission lifecycle and native focus hardening are still planned. Representative
speech, accessory/call routing, speech-service resource/battery, older Android,
release HTTPS/manual accessibility and intended installation checks remain distinct
from the successful local tests. This guide does not claim those gates passed.

Automatic background listening, arbitrary external/shell actions, public signup,
mobile LLM inference, PDF/OCR and later operations/integration features are not
implemented by the instructions above. Keep one Uvicorn worker, authenticated
owned API access and deliberate reviewed writes.

### How this guide was checked

Commands/paths/options were checked against setup/start/configuration scripts,
CLI help, actual Alembic head, OpenAPI, client source/pins and current test/status
records. Official tool installation/device pages were checked on 13 October 2026.
Documentation checks and focused tests are recorded in STATUS/WORKLOG. A fresh
installation, production migration, model download/inference or deployment was
not performed while writing this document.
