# Phase 21 — private-network connectivity

Status: **Implemented in source; local Windows/host/emulator checks recorded,
actual enrollment/release HTTPS/physical handover remain separate.** No deployment.
Inputs: Phase 20's transport/readiness audit,
18 credentials, current HTTPS-only release client, G-06/G-29. The user wants
same-Wi-Fi and Tailscale access. Follow [shared rules](FUTURE-ROADMAP.md).

## Outcome

Enter or import a server address, verify the trusted server, sign in and reconnect
from an authorized private network. Keep Uvicorn, PostgreSQL and Ollama on
loopback/private interfaces. Network membership never substitutes for ADA login.

## Checkpoints

- **A — two explicit routes.** Recommended first route: Tailscale Serve HTTPS
  forwarding to the existing loopback API/UI proxy, restricted by tailnet policy.
  It works for enrolled devices on Wi-Fi and away from home. Also support direct
  LAN HTTPS with a controlled hostname, trusted certificate and private firewall
  rule, without requiring Tailscale. Record certificate renewal and DNS ownership.
  An arbitrary `https://192.168.x.x` is not valid unless its certificate matches.
  Do not enable Funnel/public sharing or expose 8000/5432/11434/5173 as shortcuts.
- **B — connection UX.** Preserve existing valid HTTPS-origin parsing; add
  saved named server profiles, explicit switch/clear, server compatibility and
  health checks, certificate/hostname versus DNS/VPN/offline diagnostics, and
  retry guidance. No token/password until TLS and origin checks succeed.
  Do not claim generic network errors uniquely identify VPN or certificate cause.
- **C — safe address import.** Optional QR/deep link carries a versioned HTTPS
  origin and display label only, no credentials or trust override. Show origin
  and require explicit selection before connecting. Manual entry always works.
  No silent LAN scan/mDNS server trust. Discovery can be considered separately.
- **D — host validation and docs.** Rehearse both routes with isolated host/client
  processes and an emulator if practical; validate UI/API routing and SSE through
  the actual TLS proxy. Write verified Windows setup/renewal/troubleshooting steps.
  Physical Wi-Fi/VPN handover is recorded as deferred, not claimed passed.

## Data and interfaces

Client profiles contain origin/label, with credentials separately bound to the
verified owner and server. Reuse health/capability routes; expose only a minimal
unauthenticated compatibility response if a demonstrated need requires one.
Never publish account names, conversations, certificates' private keys or internal
provider details through discovery. Admin remains same-origin with relative API
paths; no blanket CORS. Server-identity changes require fresh verification/login.

## Failures and tests

Reject invalid/expired/wrong-host certificates, user-info/query/fragment URLs,
redirected sign-in, hostile QR content, cleartext LAN and a server swap during
login/recovery. Test IPv4/IPv6 origins, VPN absent/revoked, DNS change, proxy
failure, source-server binding and late old-server callbacks. Verify normal CLI/
USB development and current token API contracts remain valid. Login22 must use
this transport without requiring an incompatible URL format.

## Exit

Trusted HTTPS carries authenticated API and SSE on a demonstrated host setup;
emulator/HTTP/TLS evidence and untested physical routes are separately recorded.
No certificate bypass, direct provider access or automatic admin grant exists.
Installing a VPN, issuing real certificates or changing live firewall/exposure
requires separately selected execution scope.

Tailscale's [Serve documentation](https://tailscale.com/docs/features/tailscale-serve)
describes private tailnet proxying. Its [HTTPS documentation](https://tailscale.com/docs/how-to/set-up-https-certificates)
notes public certificate-name transparency: choose nonsensitive hostnames.
These product capabilities are not evidence that ADA networking is already set up.

## Implementation record — 2026-10-16

- [x] A: new loopback Caddy tailnet backend; existing LAN TLS template now defaults
  to explicit loopback binding. Windows runbook defines private Serve versus LAN,
  DNS/certificate ownership, selected firewall rules, renewal and withdrawal.
  Actual Tailscale enrollment/real certificates/firewall execution were excluded.
- [x] B: up to12 metadata-only Android profiles, explicit selection/removal/clear;
  bounded public readiness before native me/recovery and web admin-me; standard
  platform TLS, native TLS/DNS diagnostics, honest generic/browser retry guidance.
  Existing authenticated me/capabilities and all owner/server recovery fences remain.
- [x] C: strict version1 JSON label/origin import, review then explicit selection,
  manual entry retained. QR camera/deep-link/discovery are optional and not added.
- [x] D: actual Caddy with disposable ADA/built UI/SSE/auth/replay through direct
  TLS and a two-proxy Serve-boundary laboratory; negative root/host/expiry checks,
  Android profile UI/recreation and OS laboratory-CA rejection; backend/web/native
  regression evidence in STATUS/WORKLOG. No actual tailnet or physical handover claim.

No migration, new public discovery endpoint, certificate exception, provider
connection, password login or automatic role was added. Source OpenAPI remains
96paths/132schemas and head0015. See
[PRIVATE-NETWORK-CONNECTIVITY](../docs/PRIVATE-NETWORK-CONNECTIVITY.md) for the
operator guide and explicit laboratory/target distinction. Stop at21.
