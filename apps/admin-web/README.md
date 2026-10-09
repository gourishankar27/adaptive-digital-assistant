# ADA web UI foundations (Phase 03)

This local development SPA checks the authenticated account and capabilities
using the existing ADA HTTP API. It also provides light/dark/large-text previews
and the planned admin screen map. Admin monitoring needs the Phase 05 server
authorization contract and Phase 06 UI. This scaffold grants no admin role and
does not implement a dashboard, chat or user enrollment.

## Windows setup and checks

Use Node **24.12.0** and npm **11.6.2** (also pinned by .node-version, .nvmrc,
engines and packageManager). npm ci installs exactly package-lock.json. Python's
existing virtual environment is needed for the disposable integration server.

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

The e2e command launches Chromium, loopback Vite on 5173 and the repository's
client_test_server.py on 18763. The latter creates a disposable, migrated SQLite
database, a synthetic account and the actual FastAPI application with FakeProvider.
The test token is generated in memory, inherited by the server/workers, and never
printed. One browser test uses the actual HTTP adapter without interception;
separate fixture tests cover invalid credentials, escaping and keyboard states.
Recording, screenshots and video are disabled. A fake model integration is not
evidence of a real Ollama reply or PostgreSQL semantics.

## Run against your existing backend

Start ADA from the root using its existing scripts/start.ps1 (loopback :8000,
one Uvicorn worker). In another PowerShell window:

```powershell
Push-Location apps\admin-web
npm ci
npm run dev
```

Open http://127.0.0.1:5173. Keep the browser server origin as shown, then enter
a current ADA bearer token. Connect calls GET /v1/me and GET /v1/capabilities.
No credential is stored in localStorage/sessionStorage, a URL or persisted cache.
Reload, logout, changing account/server and 401 clear private state. Editing the
server also clears the token field. Leaving a screen does not cancel generation.

The Vite proxy forwards same-origin /v1 requests to http://127.0.0.1:8000. To use
another development API server, stop Vite and set its fixed target before restart:

```powershell
$env:ADA_API_TARGET = 'https://your-private-ada-host.example'
npm run dev
```

The target accepts HTTPS or loopback HTTP only and rejects credentials, query
strings and paths. It is a non-secret origin, never a database/Ollama URL.
The UI accepts only its current browser origin so a user-entered URL cannot
redirect bearer credentials. No production CORS or deployment is configured.
`npm run preview` is a local build preview; it has no development API proxy.

Android emulator and USB connection instructions are in ../android/README.md.
The backend's loopback default remains unchanged.

## Contract and state boundaries

- src/api/generated.ts includes DTOs/paths for every current OpenAPI route. Run
  npm run contracts:generate after an authorized contract change. Its explicit
  int64 → bigint transform preserves all signed 64-bit UTC milliseconds.
- src/api/decode.ts runtime-validates implemented reads, tolerates unknown fields
  (including future numeric values) and safely retains future request enum values.
  Unknown states cannot be interpreted as completed. Supported connection API
  version is v1 with server authority. Optional older flags never enable features.
- HttpAdaApi implements the injected AdaApi interface for account/capability and
  owned request-status reads. Redirects are errors; transport failures never load
  fixtures. Errors use actionable fixed wording, never server/private body text.
  401 disconnects. Retry-After is parsed for visible manual reconnect guidance;
  reads have no automatic retry. Timeout/network loss is an unknown submitted
  outcome; status reconciliation must use the original request ID and payload.
- ConnectionSession binds query keys to server/owner/scope/request, clears all
  private caches before switching identity and rejects late old results. Tokens
  stay solely in the live adapter; the entry field clears upon submission.
- ScreenState defines empty/loading/loaded/stale/offline/forbidden/error/deferred
  and unknown-outcome states for subsequent phases. There are no client writes,
  journals, streaming or cancellation controls. API creation POSTs lack idempotency
  keys; later screens must reconcile uncertain creation rather than blindly retry.
- Completed requests retain their original citations. sourceForLabel searches only
  that response; unknown labels and legacy missing traces never create a card.
  Baseline v1/v2 remain frozen until explicit audited upgrade; v3 retrieval is
  available according to capabilities, never silently upgraded by the client.
- Text rendering escapes HTML, and safeHref allowlists HTTP(S) without userinfo.
  Unicode selection offsets are converted from UTF-16 to code points; selecting
  inside a surrogate pair is rejected. Exact quote whitespace is preserved.

All dependencies are exact pinned versions. Chosen versions were checked against
[Vite requirements](https://vite.dev/guide/), [React documentation](https://react.dev/versions),
[React Router](https://reactrouter.com/start/declarative/installation),
[TanStack Query](https://tanstack.com/query/latest/docs/framework/react/installation),
[Vitest](https://vitest.dev/guide/), [Playwright](https://playwright.dev/docs/intro),
[OpenAPI TypeScript](https://openapi-ts.dev/node) and
[lossless-json](https://github.com/josdejong/lossless-json) on 2026-10-08,
with npm metadata used for exact published versions and compatible peer ranges.
TypeScript 5.9.3 is compatible with typescript-eslint's <6.1 range; jsdom 26.1.0
supports the pinned Node. Native controls and interaction tests cover accessibility;
manual screen-reader and additional browser verification remain required before
a usable admin release.
