# ADA web foundations

The repository root AGENTS.md and selected phase remain authoritative. Read this
README and actual contracts/openapi.json before changing transport or screens.

- Use the real injected ADA HTTP adapter for enabled controls. Fixture adapters
  live under tests/e2e and must never be imported from production src.
- Keep bearer credentials in memory only. Never persist/log tokens or place them
  in URLs, analytics, traces, screenshots, fixtures or committed configuration.
- Use relative same-origin /v1 paths, reject redirects, and keep development
  proxy targets fixed outside user input. No direct database or provider access.
- Clear account/server state and query caches on reconnect, disconnect and 401.
  Preserve server/owner/scope/request keys and fence late async results.
- Phase 05 server monitoring requires an explicit current database grant. Names,
  profiles, route guards and ordinary tokens confer no admin access. Phase 06
  is read-only monitoring; changing permissions or configuration has no web control.
- Render untrusted content as text; allowlist link schemes. Do not add raw HTML
  rendering or executable code affordances. Preserve exact quotes and code points.
- Decode full int64 timestamps losslessly. Never pass unsafe integers through
  Number or JSON.parse; validate precision and normalize timestamps to bigint.
  Unknown request states remain unknown, never completed.
- Preserve request IDs, original citations, snapshots and missing legacy traces.
  A timeout/aborted wait leaves an unknown submitted outcome. No automatic POST
  retries or generation cancellation exist in this scaffold.
- Keep native semantic controls, meaningful labels, visible focus, accessible
  loading/error/offline/forbidden states, responsive layouts and system font zoom.
- Use package-lock.json and pinned Node/npm/dependencies. No unrelated upgrades.
  Regenerate DTOs with contracts:generate; int64 bigint transform is deliberate.
- Run npm ci, npm run contracts:check, npm run typecheck, npm run lint,
  npm run test -- --run, npm run build and npm run test:e2e from this directory.
  Install the pinned Playwright Chromium first with npx playwright install chromium.
  Browser integration starts a real HTTP server in a migrated disposable schema
  in the dedicated PostgreSQL ada_phase2_test database. Synthetic chat seeds use
  a fake model; failed request/health use actual loopback TCP refusal. Explicit
  intercepted UI error/health cases stay distinct from real authorization evidence.
- Review a browser launch and keyboard navigation. Never capture a credentialed
  browser trace/screenshot. Record checks actually run and remaining manual
  verification in the root plans/STATUS.md and plans/WORKLOG.md.
- Keep API binds loopback and one Uvicorn worker. No deployment is authorized.
