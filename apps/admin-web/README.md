# ADA admin web — Phase 06

Read-only backend monitoring for a server-authorized operator: sign-in, overview,
provider/limit configuration, server-filtered request pages, composite owner/request
detail and audit metadata. All six enabled reads use existing `/v1/admin` routes.
No raw chats, source quotes, prompts or operational write controls are exposed.

## Windows setup and checks

Use pinned Node **24.12.0**, npm **11.6.2**, package-lock.json and the root Python
virtual environment. Browser integration requires reachable PostgreSQL and the
dedicated **ada_phase2_test** database. Prepare it with root
`scripts/test-postgres.ps1`, or supply `ADA_TEST_DATABASE_URL` privately in the
environment naming only that database. Never print credentials/connection strings.

```powershell
Push-Location apps\admin-web
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

E2e starts Chromium, loopback Vite :5173 and one-worker actual ADA HTTP :18763.
`scripts/admin_web_test_server.py` loads root connection settings, derives only
ada_phase2_test and creates a unique migrated schema. Explicit test URLs must
name that database; inherited search paths/arbitrary schema names are rejected.
Random credentials stay in inherited environment memory. Two synthetic operators
receive explicit grants; ordinary owners remain unprivileged. Local fixture actions
use the existing grant service, with no remote test mutation endpoint. Teardown
removes the exact schema even if Windows kills the server before its finally block.
Startup failure does not fall back to SQLite or mocked authorization.

Successful synthetic chats use FakeProvider through owned HTTP APIs. A failed
request and subsequent health probe encounter a real TCP refusal at a bound,
non-listening loopback socket. No live generation occurs. Fixtures include two
owners sharing a request UUID, recorded zero tokens and a missing legacy trace.
Sign-in/grants/revocation/pagination/detail/audit use real PostgreSQL/HTTP.
Intercepted 401/429/503 and unknown/degraded model metadata are separate UI tests.
The database-not-ready sign-in regression explicitly intercepts a synthetic 503,
then removes the interception and signs in through the real PostgreSQL-backed API.
Browser recording, traces, screenshots and video are disabled.

## Run with an existing backend

The backend must have the current schema head **0005** and an explicit monitoring
grant for your account UUID. Admin monitoring was introduced by migration **0004**;
the Phase 08 source now requires **0005** for readiness. See
[ADMIN-MONITORING.md](../../docs/ADMIN-MONITORING.md).
Phase 06 implementation does not migrate the application DB or grant real accounts.
Start ADA with root `scripts/start.ps1` (loopback :8000, one worker), then:

```powershell
Push-Location apps\admin-web
npm ci
npm run dev
```

Open **http://127.0.0.1:5173/admin/**. Keep the browser origin as shown and enter a
current bearer token. Admin-me verifies permission and operator UUID; the header
and Settings confirm principal/server. Ordinary users receive Access denied.

Relative `/v1` requests use a fixed Vite proxy to http://127.0.0.1:8000. To select
another development API, stop Vite, set a non-secret origin and restart:

```powershell
$env:ADA_API_TARGET = 'https://your-private-ada-host.example'
npm run dev
```

The proxy accepts HTTPS or loopback HTTP without userinfo/path/query. The UI
accepts only its current HTTPS/loopback browser origin, so entered values cannot
redirect credentials. Database/provider URLs are never browser inputs.

### If sign-in reports that monitoring or the database is unavailable

The browser origin **http://127.0.0.1:5173** is correct for this development setup;
the proxy connects to ADA on **:8000**. A running API can still have an older
database schema. Check **http://127.0.0.1:8000/health/ready**: HTTP 503 with
`database_not_ready` means connectivity or the required migration needs attention.
The older generic message, “The server is unavailable or busy,” also covered this
case. Current builds explain the fixed `database_not_ready` and
`monitoring_unavailable` codes without displaying private error bodies.

After backing up the intended database through your normal operator process,
stop ADA and run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic check
.\scripts\start.ps1
```

Use the current repository's required head **0005**. The reported login failure
was repaired by separately installing **0004** and granting the user-selected
account against the pre-Phase 08 backend. That repair does not install Phase 08:
running the new source requires a separately authorized **0005** installation.
Restart Vite if its proxy target changed, then sign in again. A subsequent
**Access denied** means the account needs an explicit local `grant-admin` using its
UUID as described in [ADMIN-MONITORING.md](../../docs/ADMIN-MONITORING.md). Applying
migrations does not grant a role, and waiting or changing the browser origin does
not repair a missing migration. Do not put your token in URLs or diagnostics.

## Build and same-origin smoke

```powershell
npm run build
npm run preview -- --port 4173
```

Open **http://127.0.0.1:4173/admin/**. Loopback preview serves built assets,
`/admin` route fallback and the same fixed `/v1` proxy. To exercise the production
build against disposable PostgreSQL with the whole browser suite:

```powershell
$env:ADA_WEB_BUILD_SMOKE = '1'
try { npm run test:e2e }
finally { Remove-Item Env:ADA_WEB_BUILD_SMOKE }
Pop-Location
```

For separately authorized HTTPS hosting, serve `dist` under `/admin/`, resolve
only client routes to its index, and forward `/v1/` to ADA on the same origin.
API errors must keep their JSON/status, never SPA fallback HTML. Preserve bearer
headers/no-store responses and exclude credentials/private bodies from logging
and analytics. Vite base and BrowserRouter basename are `/admin`. No CORS, cookie,
login or refresh endpoint is assumed. Preview is a local smoke arrangement;
hosting/deployment and release HTTPS verification were not performed.

## State, data and appearance

- Credentials live only in the active HTTP adapter; the input clears on submission.
  Reload/pagehide requires sign-in. Logout/reconnect/server change and 401/403 abort
  reads, clear all queries and fence late results. Revoked detail disappears on
  the next denial. A hidden tab learns of revocation when server reads resume.
- Query keys include server, verified principal, session epoch, filters and both
  owner/request UUIDs. Only allowed DTO fields enter caches; unknown extensions are
  dropped. Int64 times/durations remain bigint; values outside Date's range display
  exact epoch milliseconds. Unknown statuses remain unknown. Nothing persists
  except appearance enums; no token/results in storage, URLs or error bodies.
- Visible mounted views poll every **30 seconds**, without automatic retry,
  focus/reconnect triggers or background polling. Hidden tabs disable refresh.
  Retry-After extends intervals and establishes a session cooldown across view
  changes/manual reads/sign-in. Transient failures retain last success labelled
  stale; 401/403 clear it and 404 hides detail. Unmounted caches are discarded.
- Requests use server UUID/state/provider/UTC-window filters, 10/25/50/100 rows
  (server default 50), offset capped at 10,000, maximum 7-day window (default last
  24 hours). Pagination freezes returned bounds; detail/back restores safe filters.
  Creation-descending/composite order stays authoritative. Offset pages are
  observations, not an immutable snapshot while requests change.
- Counts have windows, units and last-success/server observation times. Token sums
  include known-value coverage. Null/zero/unknown/unavailable/degraded differ.
  Request elapsed includes context/database overhead; retrieval time measures its
  recorded step. Legacy missing values say Not recorded. Selected memories are
  not citation counts. GPU/throughput and synthetic charts are absent.
- Provider limits and audit are read-only. Audit shows fixed actor/action/target/
  outcome/time metadata with server 30-day/10,000-event retention. Permission checks
  remain server-enforced. No shell/retry/cancel/purge/token/prompt editing exists.
- Settings defaults to **Oxford Blue #002147**, with **Dark Red #350616** and
  **Olive Green #3c4c24**. Each supports system/light/dark brightness and larger
  text. Only enum preferences persist under `ada.appearance.v1`; disabled storage
  still permits changes in the current tab. System brightness follows the OS.
- Native labels/headings/table captions/column headers, labelled horizontal table
  regions, skip link and focus styles support keyboard/narrow/zoom layouts.
  Navigation focuses main; refreshing keeps focus and does not announce ticks.
  Model/error text is escaped, with no raw HTML insertion.

Earlier Phase 03 compatibility transport/state tests remain. The live app uses
HttpAdminApi, AdminSession and TanStack Query monitoring views. Server contracts,
capabilities, prompts, migrations and dependency pins are unchanged in Phase 06.
Manual screen-reader/other-browser review, real release HTTPS and sustained
polling/performance remain target checks; see [STATUS](../../plans/STATUS.md) and
[WORKLOG](../../plans/WORKLOG.md).

## Phase 11 operational proposal counts

Overview optionally shows pending/accepted/rejected counts within its selected
creation window; older servers show an unavailable state. The closed decoder
discards private proposal, annotation and support fields. No admin review UI or
cross-user proposal access is added. Server grants, audits, memory-only bearer
storage and same-origin HTTP remain required. See
[the policy](../../docs/MEMORY-PROPOSALS-AND-REVIEW.md) and
[checks](../../plans/STATUS.md).
