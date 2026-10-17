# Private-network connectivity — Phase 21

For the subsequent authorized Windows/Tailscale installation with Phase22 password
login, use [the step-by-step setup guide](PRIVATE-SETUP-WINDOWS-TAILSCALE.md).
The token/schema0015 instructions and no-deployment statements below describe the
original Phase21 boundary; current source requires0016.

Phase 21 adds Android server-address bookmarks/import, credential-free readiness
checks before login, specific native TLS/DNS diagnostics, and two proxy templates.
The server API, schema0015, credentials, ownership checks and saved replay remain
unchanged. Username/password login belongs to Phase22.

This is an operator runbook for a **separately authorized installation**. Phase21
implementation/tests do not install Tailscale, enroll devices, issue a real
certificate, change firewall/DNS, start a live proxy or publish ADA. The laboratory
uses disposable data and test certificates trusted only by its test processes.

## Choose one connection route

| Route | Client address | HTTPS terminates at | Local path to ADA |
|---|---|---|---|
| Tailscale Serve | Full device/tailnet HTTPS hostname | Tailscale Serve | Serve → loopback Caddy18764 → loopback API8000, built admin files |
| Direct LAN | Controlled DNS hostname resolving to the laptop's private address | Caddy with a system-trusted matching certificate | Private-interface Caddy443 → loopback API8000, built admin files |

Both routes expose the same origin root to Android, `/admin/` to the browser,
and `/v1/…` to their authenticated HTTP adapters. Only the intended private HTTPS
entry point is reachable from other devices. PostgreSQL, Ollama, API8000,
development5173 and the internal18764 proxy stay local. Use one Uvicorn worker.
VPN membership and `Tailscale-User-*` headers never grant ADA account/admin access.

Tailscale is the first route when you do not already own/control a suitable DNS
name and certificate. It can carry the same HTTPS origin over home Wi-Fi or an
enrolled connection away from home; do not promise availability when either host
is asleep/offline. Direct LAN needs its own DNS and certificate prerequisites.

## Android connection and saved servers

1. Open the connection screen and enter an **origin**, for example
   `https://ada.example.net`, with an optional explicit port. Leave out paths
   such as `/admin`, userinfo, query strings and fragments. IPv6 uses brackets,
   for example `https://[fd00::1234]:8443`; the certificate must match that address.
2. Open **Saved servers and connection checks**. **Check server without signing
   in** sends only `GET /health/ready`, without credentials. A ready response
   establishes reachability/readiness, not account permission or model availability.
3. Enter a current bearer token and select **Connect**. The HTTP adapter repeats
   a bounded, credential-free readiness check before `/v1/me`, including encrypted
   session recovery/token replacement. TLS chain/hostname validation applies to
   every HTTPS request. Authenticated me/capabilities then verify owner and API
   compatibility before restoring private state. No credential is sent on a
   failed readiness/TLS check; redirects are refused.
4. To bookmark an address, enter a **Server name** and use **Save server address**.
   At most12 distinct HTTPS origins are stored. Labels/origins are local metadata,
   separate from Keystore-encrypted credentials and private recovery journals.
   Bookmarks are retained when signing out; remove them explicitly when desired.
5. **Use NAME: ORIGIN** selects an address, clears the token field and disconnects
   private state. It does not sign in. **Clear selected address** also clears
   the current login; **Remove NAME** removes only the bookmark. Use Settings →
   Disconnect before switching an already connected account/server. Old pending
   requests may continue on their original server and are never resubmitted to
   the selected server.

Release continues to require standard platform-trusted HTTPS. Debug HTTP remains
limited to the existing localhost/127.0.0.1/10.0.2.2 development hosts; those
cleartext development origins are not saved as remote profiles. No LAN cleartext,
custom trust manager, certificate exception or user-CA release override was added.
See [Android network security](https://developer.android.com/privacy-and-security/security-config).

### Review a server-address import

Paste this versioned metadata into **Server address import (JSON)**:

```json
{"version":1,"label":"Home laptop","origin":"https://ada.example.net"}
```

Use **Preview address import**, inspect the full label/origin, then explicitly
select **Use reviewed address**. This only fills the address; save/check/sign in
separately. Invalid versions, unexpected fields (including tokens/passwords or
trust overrides), cleartext origins, malformed/oversized content and URLs with
paths/query/userinfo/fragments are rejected. No automatic scan, discovery,
deep-link handler or camera/QR permission exists. A QR tool may display this JSON
as text for manual review; this app does not silently handle external QR links.

### Admin browser

Open the selected server's **`https://HOST/admin/`**. Enter only its current
**browser origin** (`https://HOST`, including a nondefault port if applicable)
and your existing admin bearer token. The adapter checks readiness without a token
before authenticated admin-me. API responses retain their schemas and server-side
role checks. Web uses relative paths and no cross-origin credential forwarding or
blanket CORS. To change servers, sign out and open the other server's own page;
ordinary browser bookmarks can name those pages. Tokens stay in tab memory.

## Prepare the Windows host

From the project root, follow [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md) for pinned tools,
database/head0015 and Ollama. This phase requires no migration/config change to
the API. Check the intended installation separately before enabling networking.

```powershell
./.venv/Scripts/ada.exe doctor
./scripts/start.ps1
```

Keep that one-worker loopback API running. In another PowerShell window:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health/ready'
Push-Location apps/admin-web
npm ci
if ($LASTEXITCODE -ne 0) { throw 'Pinned web installation failed.' }
npm run build
if ($LASTEXITCODE -ne 0) { throw 'Admin build failed.' }
Pop-Location
$env:ADA_ADMIN_DIST = (Resolve-Path apps/admin-web/dist).Path.Replace('\', '/')
```

Use the pinned Caddy version/checksum in
[validation-tools.json](../ops/validation-tools.json), currently2.11.7. Download
from its recorded official release, verify the Windows archive's SHA512 before
extracting/executing it, and keep the binary outside Git. Set its actual path:

```powershell
$adaCaddy = 'C:/Tools/Caddy/caddy.exe' # Replace with your verified binary path.
& $adaCaddy version
```

Only run the following route's exposure-changing steps in a selected installation
window. Commands are reviewed/source-backed instructions; actual tailnet, real
certificate and live firewall execution were excluded from this implementation.

## Route A — Tailscale Serve

1. Install/enroll Tailscale on laptop and Android using your intended private
   account. Record its version, use nonsensitive device/tailnet names, enable
   MagicDNS/HTTPS and restrict tailnet access to the selected users/devices and
   the server's TCP443. Review existing sharing and Serve/Funnel configuration
   before changing it. Public certificate names are visible in Certificate
   Transparency; this is not a promise of hostname privacy.
   [Serve](https://tailscale.com/docs/features/tailscale-serve),
   [HTTPS setup](https://tailscale.com/docs/how-to/set-up-https-certificates).
2. Review status locally; these commands can reveal private network metadata, so
   do not paste their complete output into a plan/support log:

   ```powershell
   tailscale version
   tailscale status
   tailscale serve status
   tailscale funnel status
   ```

3. From the project root with `ADA_ADMIN_DIST` set, validate and start the supplied
   loopback-only API/UI proxy. The host matcher accepts Serve's original hostname
   while `bind 127.0.0.1` restricts the socket; do not replace it with a public bind:

   ```powershell
   & $adaCaddy validate --config ops/Caddyfile.tailnet.example --adapter caddyfile
   if ($LASTEXITCODE -ne 0) { throw 'Tailnet backend template failed validation.' }
   & $adaCaddy run --config ops/Caddyfile.tailnet.example --adapter caddyfile
   ```

4. In a second window, verify the loopback proxy before selecting exposure:

   ```powershell
   Invoke-RestMethod 'http://127.0.0.1:18764/health/ready'
   ```

5. In the selected installation window, enable private Serve for that backend:

   ```powershell
   tailscale serve --bg --https=443 http://127.0.0.1:18764
   tailscale serve status
   ```

   Use the **full HTTPS hostname printed by Serve** as the Android origin, and
   append `/admin/` in the browser. Follow its consent/setup page if required.
   Do not enable Funnel, public node sharing or an insecure HTTPS upstream. This
   route's HTTP hop is strictly local. The CLI's background flag persists Serve
   configuration across restart; it does not supervise ADA, Caddy or the laptop.
6. Verify current policy from an allowed and a nonallowed client. Check missing
   credential401 and ordinary owner403 for monitoring. Disable just this Serve
   route when finished, retaining the original flags:

   ```powershell
   tailscale serve --bg --https=443 off
   ```

   Do not reset an unrelated Serve configuration. Commands and persistence behavior
   follow the [Serve CLI reference](https://tailscale.com/docs/reference/tailscale-cli/serve).

Serve manages its HTTPS endpoint. Check its certificate status/renewal operationally
and keep the enrolled daemon healthy. If you choose exported `tailscale cert`
files instead, their renewal/reinstallation is the operator's responsibility;
that is a different route from the supplied Serve topology. Machine-name/DNS
changes require reviewing the new full origin and signing in again.

## Route B — direct same-LAN HTTPS

1. Control a DNS name such as `ada.example.net`. Arrange for clients on the
   selected LAN to resolve it to the laptop's reserved private address. Verify
   DNS ownership and any DNS-01 certificate credentials separately. Do not use a
   raw private IP unless its certificate has the matching IP subject alternative
   name. No domain purchase, certificate issuance or DNS update is automated here.
2. Obtain a certificate/private key whose hostname and full chain are accepted by
   Android's **system trust store**. A browser exception or user-installed CA is
   insufficient for this release app. Keep the key outside the repository and
   give file access only to the selected operator/proxy identity.
3. Set these protected/local values from the project root. The names/IP/paths below
   are examples to replace with your controlled installation:

   ```powershell
   $env:ADA_PRIVATE_HOST = 'ada.example.net'
   $env:ADA_PRIVATE_BIND = '192.168.12.61'
   $env:ADA_TLS_CERT = 'C:/Users/YOUR_USER/AppData/Local/ADA/tls/fullchain.pem'
   $env:ADA_TLS_KEY = 'C:/Users/YOUR_USER/AppData/Local/ADA/tls/private-key.pem'
   $env:ADA_ADMIN_DIST = (Resolve-Path apps/admin-web/dist).Path.Replace('\', '/')
   & $adaCaddy validate --config ops/Caddyfile.private.example --adapter caddyfile
   if ($LASTEXITCODE -ne 0) { throw 'LAN TLS template failed validation.' }
   ```

   The template defaults to binding127.0.0.1 unless `ADA_PRIVATE_BIND` is explicitly
   supplied. API/provider/database binds are unaffected. For IPv6, choose the
   intended private interface and matching DNS/certificate/firewall policy.
4. Before starting the listener, select a **Private** Windows network profile
   appropriate for the trusted LAN and review existing firewall rules. An
   Administrator PowerShell example for one selected IPv4 subnet is:

   ```powershell
   $adaApprovedSubnet = '192.168.1.0/24' # Replace with the deliberately allowed subnet.
   New-NetFirewallRule -Name 'ADA-Private-HTTPS' -DisplayName 'ADA private HTTPS' -Direction Inbound -Action Allow -Profile Private -Protocol TCP -LocalAddress $env:ADA_PRIVATE_BIND -LocalPort 443 -RemoteAddress $adaApprovedSubnet -Program $adaCaddy
   ```

   This example was not executed. Review other allow rules that might widen access;
   one narrow rule does not override an existing broad rule. No router port
   forwarding or database/provider port allow rule is needed. See Microsoft's
   [New-NetFirewallRule reference](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule).
5. Start the selected proxy in a normal operator window:

   ```powershell
   & $adaCaddy run --config ops/Caddyfile.private.example --adapter caddyfile
   ```

6. From an allowed client, use `https://ada.example.net` in Android and
   `https://ada.example.net/admin/` in the browser. Verify readiness, authentication,
   source ownership and SSE/reconnect. From a nonallowed network, verify denial.
   Disabling Wi-Fi/using a different LAN should not be presented as a working
   connection unless another explicitly configured private route is available.
7. Record who owns DNS, the certificate issuer, expiry and renewal method outside
   the public plan. Renew/replace the full chain and protected key before expiry,
   revalidate configuration, then deliberately restart this proxy to load them.
   The templates disable Caddy's management API; `caddy reload` is not the restart
   procedure here. Test the renewed certificate from both clients. No renewal
   scheduler or service supervisor was installed by Phase21.

To withdraw this route, stop its Caddy process with Ctrl+C and remove only the
rule you deliberately added, in Administrator PowerShell:

```powershell
Remove-NetFirewallRule -Name 'ADA-Private-HTTPS'
```

## Diagnostics and retry

| Observation | Meaning and next check |
|---|---|
| Native TLS/secure identity failure | Certificate chain, hostname, expiry, clock or handshake failed. Check the exact origin and trust; never bypass validation. |
| Native DNS failure | Name resolution failed. Check spelling/private DNS, Wi-Fi/VPN and DNS ownership. This alone does not prove VPN revocation. |
| Generic network/proxy failure | Host, route, firewall, VPN or proxy may be unavailable. Restore the connection and check readiness again. |
| Browser fetch failure | Browser does not expose a reliable TLS-versus-DNS cause to the app. Inspect its certificate warning/network tools locally without logging credentials. |
| Ready503/database_not_ready | The trusted endpoint was reached; the backend/database needs operator attention. Do not keep retrying login as a credential fix. |
| Ready200 followed by incompatible response | Readiness alone is not ADA identity/contract proof. Verify API versions and proxy routing, and ensure `/v1` did not become SPA HTML. |
| Login redirect | Refused. Use the final operator-verified origin directly; a redirect must not forward a bearer. |
| 401/403 | Network access succeeded; check current ADA credential/explicit server admin grant. Network membership supplies neither. |
| Existing stream disconnects | Restore access, check its original request and reconnect with the same attempt/cursor. Do not send a new turn just to resume viewing. |
| Selected hostname/server changed | Disconnect, review/check the new origin and sign in afresh. Credentials/private recovery are never copied between named profiles. |

The CLI and USB/emulator development paths keep their previous formats. Use the
existing [how-to](HOW-TO-USE-ADA.md); changing transport does not upgrade archived
prompts, refresh completed citations or approve model/tool actions.

## Repeat the isolated host checks

Build admin assets first. With the verified pinned Caddy binary, run:

```powershell
./.venv/Scripts/python.exe scripts/verify_private_connectivity.py --caddy $adaCaddy --route lan --output .pytest_cache/private-lan.json
if ($LASTEXITCODE -ne 0) { throw 'LAN laboratory failed.' }
./.venv/Scripts/python.exe scripts/verify_private_connectivity.py --caddy $adaCaddy --route tailnet --output .pytest_cache/private-tailnet.json
if ($LASTEXITCODE -ne 0) { throw 'Tailnet-boundary laboratory failed.' }
```

These checks migrate disposable SQLite, use synthetic owners/fake generation,
bind only loopback, and clean up their processes/temp databases/keys. They test
real ADA auth/admin/ownership, built SPA/API routing, streamed events/cursor replay,
untrusted CA, wrong hostname and expired certificates through actual Caddy.
The tailnet variant uses a local TLS edge to rehearse Serve's protocol boundary;
it does **not** test an installed Tailscale daemon, ACL policy, certificate renewal,
real LAN firewall or handover. Host tests trust a temporary CA only per process.

An optional owned emulator with separately built `dev.ada.validation.phase21`
APKs can use `--android-device emulator-PORT` to demonstrate Android rejecting that
laboratory CA. This does not establish a positive system-trusted release TLS path.
Never install the test CA into system trust to turn that rejection into a pass.

Actual runs, intermediate failures, skips and target verification remain in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md). Physical S24FE
Wi-Fi/VPN handover, allowed/denied enrolled devices, positive release/system-trusted
HTTPS, expiry/renewal in the selected installation and sustained networking remain
separate execution gates. No later phase or deployment is implied.
