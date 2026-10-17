# Set up ADA on Windows with private HTTPS and password login

This guide uses your existing Windows laptop, PostgreSQL in Docker Desktop,
native Ollama, Tailscale Serve and the Phase22 Android/admin clients. Run commands
in **PowerShell 7** (`pwsh`), from the project root unless another location is shown.
Keep the laptop plugged in, awake and connected. This is manual operation; it does
not install an always-on service, scheduled task or automatic recovery worker.

For a fresh computer, first install the pinned prerequisites and Python environment
in [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md). For an existing installation, do not run a
database reset or regenerate `.env` just to enable HTTPS.

## 1. Understand the connection

```text
Phone / iPad / laptop browser, connected to the same Tailscale network
  https://windows-asus.tail110867.ts.net:443
    -> Tailscale Serve: HTTPS and certificate management
    -> Caddy: http://127.0.0.1:18764
         /admin/   -> built admin website
         /v1/...   -> ADA http://127.0.0.1:8000
         /health/* -> ADA readiness/liveness
    -> ADA uses PostgreSQL127.0.0.1:5433 and Ollama127.0.0.1:11434
```

The HTTP hops shown above stay inside the laptop. Clients use HTTPS. PostgreSQL,
Ollama, API8000 and Caddy18764 stay on loopback. Do not open router ports or add
firewall rules exposing these services to Wi-Fi. Tailscale membership provides
network reachability; ADA still authenticates accounts and enforces admin grants.

[Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve) provisions
TLS for its tailnet hostname. You do **not** need to create `fullchain.pem` or
`private-key.pem`, run `tailscale cert`, install a custom root certificate, or use
a certificate exception for this route. Your existing
`C:/Users/gouri/AppData/Local/ADA/tls` folder can remain empty. Certificates obtained
manually with `tailscale cert` would be a different operator-managed arrangement.

Use **Serve**, which is private to the tailnet. **Funnel** publishes services to
the internet and is not part of this setup. Both status commands may show the same
listener; the label **tailnet only**, together with no enabled `AllowFunnel` entry
in the JSON configuration, distinguishes this configuration.

## 2. Open the repository and start prerequisites

1. Open **PowerShell 7**, not a Python prompt or a PostgreSQL SQL prompt.
2. Change directory:

   ```powershell
   Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
   ```

3. Open **Docker Desktop** and wait for the engine to be running. Verify:

   ```powershell
   docker version
   docker compose up -d --wait db
   docker compose ps db
   ```

   The ADA mapping should be `127.0.0.1:5433->5432/tcp`. A separate native
   PostgreSQL on5432 can coexist. Do not stop it to fix ADA's Docker port.
   Do not run `docker compose down -v`: that deletes the database volume.

4. Start the **Ollama desktop app** if it is not running. Verify:

   ```powershell
   ollama list
   Invoke-RestMethod 'http://127.0.0.1:11434/api/tags'
   ```

   Your configured model is `qwen3.8:27b`. If it is already listed, there is no
   reason to download it again. If genuinely missing, `ollama pull qwen3.8:27b`
   downloads it and needs sufficient disk space/network time. Keep Ollama local;
   do not set `OLLAMA_HOST` to a LAN address or `0.0.0.0` for phone connectivity.

5. Start Tailscale on the laptop and sign in to your existing tailnet:

   ```powershell
   tailscale version
   tailscale status
   tailscale ip -4
   ```

   The observed laptop name is `windows-asus`, its Tailscale IPv4 address is
   `100.67.14.91`, and its HTTPS name is `windows-asus.tail110867.ts.net`.

6. For longer sessions, check Windows **Settings → System → Power & battery →
   Screen, sleep & hibernate timeouts**. Keep the plugged-in laptop awake while
   serving ADA; turning off the display is fine. Setup did not change your power
   policy. Closing the lid can still suspend the laptop, depending on its policy.

## 3. Correct `.env`

Open the existing file locally; it contains secrets:

```powershell
notepad .env
```

`.env` contains literal `NAME=value` assignments. It does not execute PowerShell.
Use the following network block, once, alongside your existing database/model
configuration:

```dotenv
# Tailscale Serve handles HTTPS; no trailing slash or /admin here.
ADA_BROWSER_ORIGIN=https://windows-asus.tail110867.ts.net
ADA_ADMIN_DIST=G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/apps/admin-web/dist

# Editable reference metadata, not network access controls or service binds.
ADA_TAILNET_HOST=windows-asus.tail110867.ts.net
ADA_TAILSCALE_IP=100.67.14.91
ADA_PHONE_TAILSCALE_IP=100.126.191.82
ADA_IPAD_TAILSCALE_IP=100.90.118.114
ADA_LAPTOP_LAN_IP=192.168.12.61
ADA_PHONE_LAN_IP=192.168.12.177
ADA_IPAD_LAN_IP=192.168.12.178
```

Keep `POSTGRES_PORT=5433` and the existing matching database URL. Keep the newly
rotated database password private; do not copy the exposed old value back into
either database setting. Existing model budgets can remain unchanged:

```dotenv
ADA_PROVIDER=ollama
ADA_OLLAMA_URL=http://127.0.0.1:11434
ADA_OLLAMA_MODEL=qwen3.8:27b
ADA_CONTEXT_TOKENS=8192
ADA_OUTPUT_TOKENS=512
ADA_TIMEOUT_SECONDS=180
ADA_MAX_PARALLEL=1
ADA_PROMPT_BYTES=6000
ADA_MEMORY_BYTES=2200
ADA_RETRIEVAL_LIMIT=8
```

What happened to the original last five settings:

| Original setting | For this setup |
|---|---|
| `ADA_PRIVATE_HOST=ada.example.net` | Removed. That is a placeholder for the separate direct-LAN template, not your Tailscale HTTPS hostname configuration. |
| `ADA_PRIVATE_BIND=192.168.12.61` | Removed. The tailnet template binds its internal HTTP listener to127.0.0.1. |
| `ADA_TLS_CERT=.../fullchain.pem` | Removed. Serve manages the certificate. An empty TLS folder is expected. |
| `ADA_TLS_KEY=.../private-key.pem` | Removed for the same reason. Never commit or share private keys. |
| `ADA_ADMIN_DIST=(Resolve-Path ...).Path.Replace(...)` | Replaced by the literal absolute forward-slash path above. |

Single quotes around a simple dotenv value are valid, and whitespace around `=`
is accepted by the parser. The problem was the unevaluated PowerShell expression
and mixing two proxy arrangements. The new proxy launcher reads only
`ADA_ADMIN_DIST` and exports it for Caddy. Python reads its ADA settings from
`.env`; PowerShell and Caddy do not otherwise import the file automatically.

The three LAN IPs are recorded as requested. ADA currently ignores these metadata
keys for runtime behavior. Editing them does not change DNS, DHCP, firewall rules,
the selected app origin or account permissions. The Tailscale DNS origin continues
to work when Wi-Fi addresses change. If the repository moves, update the absolute
`ADA_ADMIN_DIST` path. If the tailnet HTTPS hostname changes, update
`ADA_BROWSER_ORIGIN`, the Serve route and saved client origins, then restart ADA
and sign in again. Merely changing `ADA_TAILNET_HOST` does not change Serve.

Keep `.env` Git-ignored. Setup restricted its Windows ACL to your Windows account,
SYSTEM and local Administrators. Do not print the file into a shared terminal,
support log or chat. Environment variables already set in a terminal override
dotenv values; clear stale `ADA_DATABASE_URL`/`ADA_BROWSER_ORIGIN` overrides when
they point to another installation. Avoid `docker compose config` in shared logs:
it expands database secrets.

## 4. Check the installed database and Python environment

```powershell
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe -m alembic current
./.venv/Scripts/python.exe -m alembic check
./.venv/Scripts/ada.exe doctor
```

For this source, expect **0016 (head)**, **No new upgrade operations detected**,
and the configured model in the installed-model list. The fresh setup observation
already found0016/57tables; no database reset or upgrade was needed.

If another installation is older, stop its ADA API, create and verify an encrypted
backup with matching PostgreSQL tools, then explicitly upgrade:

```powershell
./.venv/Scripts/python.exe -m alembic upgrade head
./.venv/Scripts/python.exe -m alembic check
```

See [database administration](DATABASE-ADMINISTRATION-WINDOWS.md) before doing
this on an older database. Server17 requires Windows17 `pg_dump` **and**
`pg_restore` for ADA's supported recovery path. The installed native18 tools do
not meet that matching-major policy. This setup did not create a live database
backup or test a live restore; no schema/data migration was performed.

If `alembic check` proposes removing the three login tables on0016, ensure the
current `migrations/env.py` imports `login_models`. A fresh-process regression test
now checks this. Do not generate or apply a migration that deletes those tables.

## 5. Build the admin website and install the pinned proxy

In the repository terminal:

```powershell
Push-Location apps/admin-web
npm ci
npm run contracts:check
npm run build
Pop-Location
./scripts/install-private-proxy.ps1
./scripts/start-private-proxy.ps1 -CheckOnly
```

`npm ci` uses the existing lockfile. Use the repository's Node24.12.0/npm11.6.2
versions. The build must produce `apps/admin-web/dist/index.html`.

The installer downloads pinned **Caddy2.11.7 Windows amd64** from its upstream
GitHub release and verifies the archive SHA512 and executable SHA256 against
`ops/validation-tools.json`. It extracts only `caddy.exe` into
`%LOCALAPPDATA%/ADA/tools/caddy-2.11.7`. It does not install a Windows service.
Re-running against an intact installation is safe; a checksum mismatch stops.
An already downloaded pinned archive can be supplied explicitly:

```powershell
./scripts/install-private-proxy.ps1 -ArchivePath .pytest_cache/phase20/caddy/caddy_2.11.7_windows_amd64.zip
```

That cache path is optional and is not required for future startup. Do not depend
on a test-cache executable as your installed proxy. `-CheckOnly` validates the
literal asset path, binary checksum and Caddy configuration without opening a
listener. If download/checksum validation fails, do not disable verification.

## 6. Start the API, Caddy and Serve

During this setup they were started in background PowerShell processes. If already
running, proceed to the checks below; do not start duplicate copies. For ordinary
manual startup after a reboot, use two PowerShell7 windows:

**Window A — API:**

```powershell
Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
./scripts/start.ps1
```

Leave it open. This starts exactly one worker on127.0.0.1:8000, with access logging
and proxy-header trust disabled.

**Window B — internal proxy:**

```powershell
Set-Location 'G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant'
./scripts/start-private-proxy.ps1
```

Leave it open. It listens only on127.0.0.1:18764, serves the production build at
`/admin/` and forwards the API paths. Its message that automatic HTTPS is disabled
is expected: Tailscale terminates HTTPS in front of this local HTTP listener.

**Window C — configure/check Tailscale:**

```powershell
tailscale serve status
```

Your route is already configured. On a fresh node, or after intentionally removing
it, run:

```powershell
tailscale serve --bg --https=443 http://127.0.0.1:18764
tailscale serve status
tailscale serve status --json
tailscale funnel status
```

If Serve is not enabled, follow its displayed Tailscale administration link and
authorize Serve/HTTPS for your own tailnet, then retry. Do not enable Funnel.
The expected route is:

```text
https://windows-asus.tail110867.ts.net (tailnet only)
|-- / proxy http://127.0.0.1:18764
```

`--bg` retains the Serve configuration; it does not make the API, Caddy, Docker or
Ollama start automatically. A sleeping/offline laptop cannot answer requests.

Run these checks in Window C:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
Invoke-RestMethod 'http://127.0.0.1:18764/health/ready'
Invoke-RestMethod 'https://windows-asus.tail110867.ts.net/health/ready'
Start-Process 'https://windows-asus.tail110867.ts.net/admin/'
```

All three readiness requests should succeed without a certificate warning. An
unauthenticated `/v1/me` or `/v1/admin/me` should return401. The bare hostname root
`/` returns404 intentionally; use `/admin/` for the website. Public readiness checks
confirm the API/database path, not successful model inference or account access.

## 7. Set your private login password

An existing account does not acquire a password automatically. List safe local
metadata:

```powershell
./.venv/Scripts/ada.exe login-accounts
```

Your database contains **two different owners**, `Gourishankar` and
`gourishankar`. The existing admin grant belongs to this account:

```text
Display name: Gourishankar
Owner UUID:   ea9f86d3-f8bc-4cf1-af76-c27e01dcb50d
```

Do not merge/delete the other account to solve sign-in. Both display names
normalize to `gourishankar`, so that identifier is deliberately rejected as a
collision. Enroll the existing admin owner with a distinct login, for example:

```powershell
./.venv/Scripts/ada.exe set-password ea9f86d3-f8bc-4cf1-af76-c27e01dcb50d gourishankar-admin
```

Type a chosen **15–1024 character** password/passphrase twice at the hidden
prompts. Nothing is echoed as you type. Save it in your password manager. Do not
put it into `.env`, command arguments, scripts, screenshots or this conversation.
Use a real interactive terminal; redirected input is intentionally rejected.

The setup opened an interactive enrollment window for this same operation.
Complete it there, or use the command above later. Success prints
**Password set; password sessions revoked. Legacy/device credentials are unchanged.**
A closed window or completing the prompts alone is not proof of a saved password.
Re-run `login-accounts` and
expect the chosen login plus `password_enabled: true`. Choose **that login** in
the clients, rather than the display name. No username automatically grants admin;
the existing server grant is what authorizes the dashboard.

`set-password` also resets a forgotten password and revokes that owner's password
sessions. It preserves UUID/data/admin grants and separately issued legacy/device
credentials. Do not repeat it during every startup.

During this setup the first short-password attempt was rejected; the subsequent
hidden-prompt retry succeeded. Local metadata confirmed `gourishankar-admin` is
enabled for the existing admin owner. You can use that login now; enrollment is
not an unfinished startup step on this laptop.

## 8. Sign in on the laptop and iPad

1. On the laptop, open:
   **https://windows-asus.tail110867.ts.net/admin/**
2. **Browser server origin** must be exactly
   `https://windows-asus.tail110867.ts.net`, without `/admin/` or a trailing slash.
3. Enter the enrolled login, such as `gourishankar-admin`, and its chosen password.
   Select **Sign in**. Keep advanced bearer-token mode off for normal password use.
4. Use Settings to change your password or sign out all password sessions. Normal
   sign-out revokes the current session. The browser receives Secure/HttpOnly
   cookies; you do not need to copy tokens.
5. On the iPad, open **Tailscale**, sign in to the same tailnet and connect. Then
   open the same `/admin/` URL in Safari and sign in. The iPad's observed Tailscale
   address is100.90.118.114. Its Wi-Fi address is not the ADA server address.

The current iPad option is the browser admin dashboard. A native iOS ADA/chat app
is not implemented. The admin dashboard monitors ADA; conversation chat is in the
Android client. Do not enter passwords into the HTTP5173 development preview:
ordinary browser password login requires the real HTTPS origin.

The user confirmed laptop dashboard sign-in succeeds with this setup. Backend
metadata also confirms Android and Admin browser sessions for the same existing
admin owner. iPad Safari sign-in was documented but not tested in this run.

## 9. Connect the S24 FE

1. Open Tailscale on the phone, sign in to the **same tailnet** as `windows-asus`,
   approve its Android VPN connection prompt and turn it on. Having the app
   installed is not the same as being connected. No exit node is needed.
2. On the laptop, `tailscale status` should show an Android peer once enrolled.
   This setup subsequently observed your S24 FE online at100.126.191.82.
   In the phone's browser, open the HTTPS readiness URL from Step6. If it fails,
   resolve Tailscale/DNS/policy first. Do not change ADA to LAN HTTP.
3. Open the current **ADA** app. The connected SM-S721U1/Android16 was observed
   with `dev.ada.assistant.debug`, version15/`0.22.0-sessions`, already installed.
   No reinstall or app-data reset was needed for this setup.
   The user subsequently confirmed the real HTTPS server check and ordinary
   password sign-in work on this phone. Reopen/chat/handover remain separate checks.
4. If another phone has an old app, use the pinned JDK/SDK and build/install from
   this checkout:

   ```powershell
   $env:JAVA_HOME='C:/Program Files/Eclipse Adoptium/jdk-21.0.12.101-hotspot'
   $env:ANDROID_HOME=Join-Path $env:LOCALAPPDATA 'Android/Sdk'
   Push-Location apps/android
   ./gradlew.bat :app:assembleDebug
   Pop-Location
   $adaAdb=Join-Path $env:ANDROID_HOME 'platform-tools/adb.exe'
   & $adaAdb devices
   & $adaAdb -s R5CX91BV6DH install -r apps/android/app/build/outputs/apk/debug/app-debug.apk
   ```

   Change the serial for another device. Enable Developer options/USB debugging
   and approve your laptop on the phone first. `install -r` preserves app data;
   if a signing-key mismatch occurs, stop and inspect it instead of uninstalling
   and losing encrypted recovery data. The USB connection is only for installing;
   ordinary network use does not need ADB reverse or the USB cable.

5. If already connected to another server/account, use Settings → Disconnect.
   On the connection screen use **Server**:
   `https://windows-asus.tail110867.ts.net` — no `/admin/`, `/v1` or port8000.
6. Open **Saved servers and connection checks**. Use **Check server without
   signing in**. Optionally save the label **Home laptop**. Bookmarks contain only
   an address/label, not a password or an authorization grant.
7. Enter your enrolled username and password and select **Sign in**. Password
   mode manages access/refresh credentials internally. The app keeps encrypted
   refresh material using Keystore and does not save your password.
8. Create/select a personality and conversation, then send a short test message.
   A first model load can be slow. Check admin/provider readiness if generation
   fails; successful preflight alone does not prove the model is loaded.
9. Close/reopen ADA, verify renewal, then explicitly test sign-out. For an
   away-from-home trial, keep Tailscale connected on both devices, turn off phone
   Wi-Fi and use cellular. Reconnect existing requests using their retained IDs;
   do not repeatedly submit the same message with new IDs after a timeout.

The build command is a developer debug installation, not a signed production
release. Physical login/reopen/chat, cellular handover and release-HTTPS checks
need their own recorded results; the host's HTTPS check is not a substitute.

## 10. Daily start, stop and update

**Start:** laptop awake → Docker Desktop → `docker compose up -d --wait db` →
Ollama → Tailscale connected → API window → proxy window → HTTPS readiness → sign
in. You normally do not reinstall dependencies, rebuild unchanged clients,
re-enroll a password or reconfigure Serve each day.

**Stop:** in foreground API/proxy windows press Ctrl+C. For the background
processes started during this setup, identify the exact listener first:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,18764 |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Inspect those specific PIDs with `Get-Process -Id PID` and stop only ADA's Python
API/Caddy processes. Do not kill every Python, PostgreSQL or Tailscale process on
the computer. The setup's nonsecret launcher receipt is
`%LOCALAPPDATA%/ADA/run/private-setup-processes.json`; listener PIDs are more
useful than launcher PIDs and must be rechecked because Windows can reuse PIDs.
Setup logs are in `%LOCALAPPDATA%/ADA/logs/private-api.*.log` and
`private-proxy.*.log`; no access log was enabled.

To disable just this Serve route deliberately:

```powershell
tailscale serve --https=443 off
```

Do not reset the whole Tailscale configuration or enable Funnel as a fix. Stop
Docker's ADA database with `docker compose stop db` if desired; this preserves
the volume. Losing laptop power/Internet/sleep stops access. Supervision and
automatic startup remain later Phase26 work.

**After source updates:** review migration requirements, back up before schema
changes, stop the API, install the pinned Python requirements if changed, run the
required migration/check, rebuild admin/Android if changed, then restart and test
the same HTTPS origin. Editing `.env` needs an API restart; changing the static
directory needs a proxy restart. Caddy serves rebuilt files from disk.

## 11. Troubleshooting

| Problem | What to check |
|---|---|
| `.env` path seems ignored | It must be literal text. Use `start-private-proxy.ps1` to export the single asset path for Caddy; do not dot-source `.env` or evaluate its contents. |
| Caddy missing/checksum mismatch | Run the pinned installer. Do not run an unchecked binary or substitute an arbitrary latest release. |
| Get-FileHash/cmdlet not found in a launched shell | Use a fresh PowerShell7 (`pwsh`) terminal and run the scripts there; mixing inherited module paths between Windows PowerShell5 and7 can break module loading. |
| Port8000/18764 already in use | Inspect the exact listener PID. Existing setup processes may already be running. Do not start a second copy or change to an unrestricted bind. |
| HTTP502 from HTTPS | Tailscale is reachable but its upstream is not. Test local18764, then8000, then Docker readiness. Start the missing service. |
| `/admin/` gives404/blank page | Build `dist/index.html`, correct `ADA_ADMIN_DIST`, validate/start Caddy, and use `/admin/` rather than `/`. |
| Database authentication fails after editing `.env` | Changing `POSTGRES_PASSWORD` does not change the existing PostgreSQL role. Its password and `ADA_DATABASE_URL` must match; see rotation below. Check stale terminal overrides too. |
| Browser sign-in403/origin rejected | Match the HTTPS address bar origin exactly with `ADA_BROWSER_ORIGIN`. Restart ADA after editing it. Use the same proxy/hostname for app and API. |
| Password sign-in401 | Ensure enrollment completed and use its login identifier, not an ambiguous display name or a legacy token. Generic failure messages intentionally do not identify which credential was wrong. |
| Normalized login collision | Use the exact owner UUID and a distinct login such as `gourishankar-admin`; keep both existing accounts. |
| Admin403 after successful login | Authentication worked; that owner lacks an explicit admin grant. Select the existing granted owner. A username does not grant a role. |
| Phone has no route/DNS/TLS connection | Connect Tailscale to the same tailnet; check the laptop is online and the node is authorized/unexpired. Verify tailnet policy permits this device to laptop443. Do not bypass certificate checks. |
| VPN conflict on Android | Check whether another VPN app is taking the Android VPN slot. Use the intended Tailscale connection while accessing ADA. |
| Certificate error | Confirm exact `.ts.net` hostname, device clock, Tailscale HTTPS setup and connectivity. Do not use `-k`, ignore-certificate flags or a manually installed untrusted root as a shortcut. |
|429/503 | Honor Retry-After and wait. Do not loop password attempts. Check API/model capacity and local service health. |
| Chat generation timeout | Keep the original request ID, inspect its status/reconnect, and check Ollama/model availability. Do not infer that a timed-out request definitely failed. |
| Password reset/sign-out invalidates sessions | Expected. Sign in again. A lost refresh response requires password sign-in; do not replay a consumed refresh. |
| Wi-Fi IP changed | Update reference metadata if useful; keep using the same tailnet DNS origin. Direct LAN operation would require a separate DNS/certificate plan. |

### Database password rotation

The exposed database password was replaced during this setup without resetting
the database or changing ADA account passwords/tokens. New settings are only in
your private `.env`; the Docker container was recreated against the same volume
to synchronize its initialization environment.

For a future intentional rotation, stop the ADA API, choose a new independent
database secret, and open the local database operator console:

```powershell
docker compose exec db psql -U ada -d ada
```

At its SQL prompt, use `\password ada` and enter the new database password at
the hidden prompts, then `\q`. Update `POSTGRES_PASSWORD` and the password
component of `ADA_DATABASE_URL` locally in `.env`. URL-encode reserved characters
in the URL only; a long random hexadecimal secret avoids that encoding issue.
Do not put `ALTER ROLE ... PASSWORD 'secret'` into a shared log or shell history.
Then run:

```powershell
docker compose up -d --no-deps --force-recreate --wait db
./.venv/Scripts/ada.exe doctor
./.venv/Scripts/python.exe -m alembic check
```

Restart the API and verify readiness. Recreating this container preserves its
named database volume. Merely editing dotenv or recreating a container does not
rotate the password of an initialized database. See the
[PostgreSQL17 role documentation](https://www.postgresql.org/docs/17/sql-alterrole.html)
and [database guide](DATABASE-ADMINISTRATION-WINDOWS.md) for recovery details.

## 12. Verification boundary

The dated setup results, including actual checks, corrected failures and remaining
device checks, are recorded in [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md). Earlier phase records saying “no deployment”
describe those earlier implementation runs; this follow-up explicitly authorized
the local private setup. No public exposure, unattended service, native iOS app
or Phase23+ feature is introduced here.
