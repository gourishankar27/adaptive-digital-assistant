# Private Windows and Tailscale setup

Current routing reference for the private1.0 baseline. The full laptop/app/build
walkthrough is [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md). Older account/IP/trial observations
are [archived](archive/PRIVATE-SETUP-OBSERVATIONS.md), not current setup requirements.

## Current route

`https://windows-asus.tail110867.ts.net` → Tailscale Serve → loopback18764 Caddy →
loopback8000 ADA. `/admin/` serves the built admin website. Android uses the origin
without `/admin/`. PostgreSQL and Ollama are not exposed through this proxy.

Both devices need Tailscale connected to the same tailnet; they need not share
Wi-Fi. The laptop must be awake. Tailscale provides TLS; no manual cert/key files
or LAN-IP certificate are required for this selected route. Keep Funnel off.

## Configure literal values

Review `.env` locally. Use your actual hostname and absolute checkout path:

```dotenv
ADA_BROWSER_ORIGIN=https://windows-asus.tail110867.ts.net
ADA_ADMIN_DIST=G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/apps/admin-web/dist
```

Do not put PowerShell expressions in dotenv. Optional `ADA_LAPTOP_LAN_IP`,
`ADA_PHONE_LAN_IP`, `ADA_IPAD_LAN_IP`, `ADA_TAILSCALE_IP` and `ADA_TAILNET_HOST`
are address-reference metadata; they do not bind services or authorize clients.
Changing a LAN address does not require changing the Tailscale HTTPS origin.

## Build assets and validate Caddy

With the existing proxy stopped, from root:

```powershell
Push-Location apps/admin-web
npm.cmd ci
npm.cmd run build
Pop-Location
.\scripts\install-private-proxy.ps1
.\scripts\start-private-proxy.ps1 -CheckOnly
```

The pinned installer verifies Caddy; validation checks literal `ADA_ADMIN_DIST`
and the reviewed template. It does not install a public service or enable Funnel.

## Start the route

Start Docker/PostgreSQL and Ollama. In separate terminals, leave these running:

```powershell
.\scripts\start.ps1
```

```powershell
.\scripts\start-private-proxy.ps1
```

For initial Serve configuration only:

```powershell
tailscale serve --bg --https=443 http://127.0.0.1:18764
tailscale serve status
tailscale funnel status
```

Approve Serve/HTTPS in your Tailscale account if prompted. Expected status is
tailnet-only forwarding to18764. An existing correct configuration needs no reset.

## Verify and sign in

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/ready
Invoke-RestMethod http://127.0.0.1:18764/health/ready
Invoke-RestMethod https://windows-asus.tail110867.ts.net/health/ready
```

Expect ready/schema 0022. Open the dashboard at the HTTPS `/admin/` URL, using the
enrolled username/password and explicit admin grant. Tailscale does not replace
ADA authentication. Existing `gourishankar-admin` enrollment need not be repeated.
For new owners/recovery, use the exact UUID and hidden password prompts in the
[password guide](PASSWORD-LOGIN-AND-SESSIONS.md).

If HTTPS gives502, check8000 first, then18764. If only admin fails, check built
assets/path/admin grant. If only the phone fails, check Tailscale connection and
the origin field. Do not expose database/provider ports or disable TLS to bypass it.

Alternative manually managed TLS/LAN routing remains a separate advanced option in
[private connectivity](PRIVATE-NETWORK-CONNECTIVITY.md). It is not an extra step
for this Tailscale setup. [Official Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve).
