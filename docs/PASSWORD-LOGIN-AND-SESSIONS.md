# Password login and sessions

Phase22 adds explicit local password enrollment, Android password sign-in and
browser cookie sessions. Source requires migration **0016** (57 tables). Installing
this checkout does not migrate an application database, set any account password,
change an admin grant or publish a service. See the dated verification in
[STATUS](../plans/STATUS.md).

## Installation and account setup

1. Stop the intended ADA API before installing the new schema. Keep the database
   private. Follow the [Windows database guide](DATABASE-ADMINISTRATION-WINDOWS.md)
   and take a verified encrypted backup with matching PostgreSQL-major tools.
   The recovery tool accepts installed0015 as well as0016; schema0005 still uses
   the separate legacy recovery workflow. Never use a blank database as an upgrade
   shortcut when you want to retain existing accounts or evidence.
2. From the repository root, install the pinned dependencies, migrate and inspect:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.lock
   .\.venv\Scripts\python.exe -m pip install --no-deps -e .
   .\.venv\Scripts\python.exe -m alembic upgrade head
   .\.venv\Scripts\python.exe -m alembic check
   .\.venv\Scripts\ada.exe login-accounts
   ```

   These are installation commands, not commands executed against your live
   database during Phase22 implementation. Existing owner UUIDs, display names,
   tokens, admin grants, prompts, request IDs and completed replay are retained.
   Password login initially stays disabled for every existing account.
3. Choose the exact owner UUID from the metadata listing. In an interactive local
   terminal, run the following with that UUID and the desired login identifier:

   ```powershell
   .\.venv\Scripts\ada.exe set-password ACCOUNT_UUID login-identifier
   ```

   Enter the new password twice at the hidden prompts. No password argument,
   environment variable, plan entry or transcript is needed. The command refuses
   noninteractive input. Use15–1024 Unicode characters; spaces, paste and password
   managers are supported, without composition rules or silent truncation.
   Password characters are used exactly, including leading/trailing spaces.
4. Usernames normalize with Unicode NFKC then casefold; surrounding whitespace is
   ignored, internal whitespace/control characters are rejected. The normalized
   identifier is distinct from the display name. Duplicate assigned identifiers
   and collisions with existing normalized display names fail before assignment.
   If several old names normalize alike, choose distinct explicit identifiers.
   Enrollment never chooses an account by a display-name guess.
5. For the browser, configure **one exact HTTPS origin** in the server environment:

   ```powershell
   $env:ADA_BROWSER_ORIGIN = 'https://ada.your-tailnet.ts.net'
   .\scripts\start.ps1
   ```

   Substitute the actual origin from your separately installed
   [private-network route](PRIVATE-NETWORK-CONNECTIVITY.md), including its port if
   needed, without a trailing slash or path. For persistence, set the same value
   in the protected local `.env`; it is origin metadata, not a secret. No wildcard,
   HTTP cookie exception or additional CORS origin is introduced. The proxy must
   preserve Host. The supplied start script uses one worker, no access log and
   `--no-proxy-headers`; forwarding headers cannot alter admission identity. Clients
   behind a proxy share its conservative30/minute authentication IP allowance.
   PostgreSQL/Ollama stay on the server; never expose their ports to clients.
6. Rebuild the admin web application and Android app using their pinned documented
   toolchains. Serve the built admin at that HTTPS origin. Loopback HTTP5173 still
   supports the explicit advanced token adapter for development, but password
   cookie sign-in requires HTTPS. Do not loosen cookie or TLS settings to bypass
   an installation error.

An admin grant remains a separate local `ada grant-admin ACCOUNT_UUID` action.
A password, login name, VPN identity or personality never grants monitoring.

## Android

1. Open ADA, choose/enter the verified server origin, then enter **Username** and
   **Password**. Tap **Connect**. Readiness is checked before sending the password.
2. ADA verifies the authenticated owner and capabilities before showing private
   state. The password input clears after submission. Only rotating refresh
   material is persisted in Android Keystore encrypted storage under noBackupFilesDir;
   access credentials remain in memory. No password or access credential enters
   the password-mode journal. Legacy bearer mode retains its earlier encrypted
   credential policy under **Advanced: legacy bearer token**.
3. Reopening after process exit refreshes once, verifies the same owner/epoch and
   reads the existing exact journal. It never resubmits a private POST. Foreground
   renewal also clears private views, verifies identity and performs GET recovery.
   Renewal stops while backgrounded; returning checks expiry before private reads.
   Activity configuration recreation may retain its still-valid ViewModel/access.
4. Settings offers signed-in-device review/revoke, password change, current sign-out
   and sign-out-all password sessions. Password change requires the current password.
   Revoking the current family returns to sign-in. CLI/device credentials have
   their separate existing explicit rotation/revocation controls.

The v12 encrypted record reads releasedv1–v11 records. Server/owner switches,
unauthorized access, unusable storage or changed data epochs clear private state;
recovery identity is never authority. Lost Keystore keys require reconnecting.

## Admin browser

1. Visit the configured HTTPS origin at `/admin/`. Keep **Browser server origin**
   equal to the address bar origin. Enter username/password and choose **Sign in**.
2. Readiness runs without credentials first. The browser receives only Secure,
   HttpOnly, SameSite=Strict, host-only `__Host-ada-access` and
   `__Host-ada-refresh` cookies (Path=/, no Domain). JavaScript receives no token
   JSON and stores no session secret in localStorage/sessionStorage. Appearance
   settings remain separate nonsecret local preferences.
3. Reopen/reload renews once through the refresh cookie. Visible monitoring reads
   renew before the server-reported access deadline, clear queries and verify the
   admin role again. Same-origin Web Locks coordinate auth operations across tabs
   when available; otherwise a refresh race fails closed and requires sign-in.
4. Settings offers password change and sign-out-all; **Sign out** revokes the current
   password family and expires both cookies. Authentication operations are the
   only new browser writes. Monitoring remains read-only.

Private cookie responses carry X-ADA-Owner; the adapter rejects an owner change
from another tab before decoding or caching its data. Cancelled login cleanup runs
inside the auth lock before another account can install cookies. Cookie mutations require both the exact configured Origin and `X-ADA-CSRF: 1`;
browser requests set Origin themselves. Ordinary protected GETs also require the
configured Host. Any simultaneous access cookie and bearer Authorization is
rejected, avoiding ambiguous principal selection. The separate advanced bearer
adapter omits cookies and keeps its credential only in memory.

## Lifecycle and limits

Access is opaque, revocable and defaults to15minutes. Refresh families have a
30day absolute lifetime and7day idle deadline, extended only by successful renewal
up to the absolute limit. Settings `ADA_SESSION_ACCESS_SECONDS` (60–3600),
`ADA_SESSION_ABSOLUTE_SECONDS` (3600–7776000) and `ADA_SESSION_IDLE_SECONDS`
(600–2592000) bound these values. Keep client/server clocks synchronized.

Only SHA256 verifiers of random access/refresh secrets are stored, separately from
Argon2id password verifiers. Every rotation invalidates prior access and consumes
the refresh verifier. A consumed refresh presented again revokes its entire family,
including a concurrent winner. At4096rotations, sign in again. There is no plaintext
escrow or grace replay. If a response is lost, **do not retry that refresh**: sign
in with the password. This is the bounded recovery policy for crash/race/theft.
Request journals retain exact IDs until an explicit account change or failure
requires local clearing; no private POST is automatically replayed.

Each owner retains at most128families. New login prunes expired families and can
replace the oldest revoked entry when full; an all-active history requires explicit
revocation/local password reset. Consumed refresh history is retained with its family.
Session labels are Android/Admin browser, with owner-scoped IDs/revocation times;
they are not a device attestation or account role.

Sign-out-all, authenticated password change and local password reset revoke all
password families for that owner. Current sign-out/revoke affects one family.
Legacy/device credentials remain valid until their separate explicit rotation,
revoke or expiry. Reset therefore is not a promise to revoke a leaked legacy token.
`login-accounts` exposes password-enabled/identifier/legacy-presence and active device/session counts to
the local operator, never password verifiers or token values.

Fresh authentication guards every private request and each outgoing SSE batch.
Refresh, logout, reset, revocation and expiry stop further batches. This cannot
withdraw bytes already delivered or undo an already committed operation. If the
server is unreachable during sign-out, clients clear local private state and say
server revocation was not confirmed; reconnect/revoke or use local reset.

Exact unauthenticated POST exceptions are `/v1/auth/login`, `/v1/auth/refresh`,
`/v1/auth/browser/login`, `/v1/auth/browser/refresh`. Other paths/methods retain
authentication. Before hashing:8192byte body cap,5second body timeout,16pre-auth
in-flight slots,120global/30IP/10normalized-identifier attempts per60second window,
4096hashed rate keys and2concurrent Argon2 operations. Forwarding headers are
ignored by the supplied launcher. Do not run multiple workers: limits are local.
Rate counters are transient admission metadata, not a persistent failed-login log.
Missing/disabled/incorrect-password accounts use generic401 and dummy verification.

Argon2id is pinned (`argon2-cffi25.1.0`, bindings26.1.0), with independent salts,
65536KiB memory,3iterations,4lanes and rehash on successful verification. Five local
hash+verify pairs measured112.79–117.14ms (median114.76ms) during development.
Two hashes budget128MiB of algorithm memory plus process/library overhead; this
is not a sustained-load or peak-RSS measurement. Parameters follow the
[Argon2 documentation](https://argon2-cffi.readthedocs.io/en/stable/parameters.html)
and exceed the [OWASP minimum](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

## Recovery and retained metadata

0016 adds password_credentials, login_sessions and refresh_verifiers without editing
released migrations. Content erasure retains these security records and explicitly
lists them in previews; all45owner-content tables retain their previous erasure
closure. Refresh verifiers are subordinate to a session, never factual evidence.

Encrypted recovery writes `ada-postgres-backup-v2` for0016. It still reads/writes
reviewed0015/v1 artifacts and supports the separate0005format unchanged. Exact
inventories fail closed on unknown revisions/tables. Restore verifies original row
hashes, randomizes legacy credentials, revokes device/password sessions, nulls
password verifiers and reapplies the latest deletion ledger in an isolated new
database. Explicit local credential recovery is required before serving it.
Never start the API against a restored0015database until its explicit0016 upgrade.

For the actual Windows/Tailscale route, dotenv corrections, managed TLS and local
enrollment, see [the private setup walkthrough](PRIVATE-SETUP-WINDOWS-TAILSCALE.md).
The dated setup follow-up in STATUS/WORKLOG is separate from implementation tests.

## Troubleshooting

| Symptom | Check/action |
|---|---|
| Sign-in failed | Confirm operator enrollment, normalized login and exact password; absent/disabled/wrong-password responses deliberately look alike. |
| Browser origin required/403 before sign-in | Match HTTPS scheme/host/port, ADA_BROWSER_ORIGIN and proxy Host; use same-origin app, without CORS workarounds. |
| Browser password sign-in rejects HTTP5173 | Install/use the private HTTPS route, or select the explicit legacy development adapter. |
| Database not ready | Install0016 into the intended database after backup, verify `alembic check`, then restart one worker. Do not reset by default. |
| TLS/DNS/readiness failure | Follow the private-network guide. Never enter credentials into an untrusted certificate exception. |
|429/503 authentication busy | Wait for Retry-After; do not loop/retry passwords automatically. Check aggregate proxy/global load. |
| Session expired or refresh response lost | Sign in again; a consumed refresh cannot safely be replayed. |
| Sign-out not confirmed | Local state is cleared. Reconnect and revoke, sign out all, or perform local password reset. |
| Ordinary account denied admin | Password login does not grant admin. An authorized local operator separately grants the exact owner UUID. |
| Restored password no longer works | Expected quarantine. Use local hidden-prompt enrollment after verified recovery/migration. |

Target verification still includes physical S24 FE/Android16, system-trusted release
HTTPS, real Wi-Fi/VPN handover, password-manager/manual accessibility review, other
browsers and sustained authentication load. Earlier voice/G-41 recovery gates are
unchanged. No Phase23+ capability, public signup, MFA, email reset or deployment.
