# Official planning references

Checked 2026-10-08. These references support architecture choices, not installed
versions or completed validation. Recheck primary documentation when implementing
a phase and record the exact compatible dependencies actually selected.

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations):
  Compose, ViewModel, unidirectional state, lifecycle-aware collection and layers.
- [Android architecture guide](https://developer.android.com/topic/architecture):
  separate UI/data responsibilities and design for lifecycle/process recreation.
- [Android Keystore](https://developer.android.com/privacy-and-security/keystore):
  protect encryption keys; the token/pending payload itself needs encrypted storage.
- [Android network security configuration](https://developer.android.com/privacy-and-security/security-config):
  explicit debug connection policy and release transport boundaries.
- [React: building an app from scratch](https://react.dev/learn/build-a-react-app-from-scratch):
  Vite/TypeScript as a build option and the additional routing/data work for an SPA.
- [TanStack Query React overview](https://tanstack.com/query/latest/docs/framework/react/overview):
  server-state loading, caching, invalidation and refresh for the admin dashboard.
- [FastAPI security scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/):
  permissions must be checked in application code; this roadmap uses the existing
  bearer scheme plus an explicit server role before considering OAuth enrollment.

Repository references are the more specific source of current behavior:
`docs/ARCHITECTURE.md`, `docs/MOBILE-CONTRACT.md`, `docs/PHASE1-MEMORY.md`,
`docs/PHASE2-RETRIEVAL.md`, `contracts/openapi.json`, tests and migrations.
Do not present a framework recommendation as evidence that an ADA app works.

## Phase 05 implementation references — checked 2026-10-09 UTC

- [Ollama list models](https://docs.ollama.com/api/tags): GET-only metadata probe;
  no inference endpoint is called by monitoring health.
- [Ollama API model names](https://github.com/ollama/ollama/blob/main/docs/api.md):
  normalize an omitted final model tag to latest when comparing installed models.
- [FastAPI yield dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#early-exit-and-scope):
  function scope closes before response delivery, allowing audit/current-grant
  failure to block a read. Existing lock pins FastAPI 0.142.4; project minimum is
  now 0.121 for this feature. No package version or dependency lock changed.

## Phase 06 implementation references — checked 2026-10-09 UTC

- [TanStack Query useQuery](https://tanstack.com/query/latest/docs/framework/react/reference/useQuery):
  bounded refetch intervals, disabled retries/focus/reconnect triggers and query signals.
- [TanStack Query polling](https://tanstack.com/query/latest/docs/framework/react/guides/polling):
  visible/background refresh behavior. ADA additionally gates document visibility
  and applies its existing server Retry-After across views.
- [TanStack Query disabled queries](https://tanstack.com/query/latest/docs/framework/react/guides/disabling-queries):
  `enabled` gate for current authorization/visibility; manual refresh is also gated.
- [React Router BrowserRouter](https://reactrouter.com/api/declarative-routers/BrowserRouter)
  and [useSearchParams](https://reactrouter.com/api/hooks/useSearchParams): `/admin`
  basename and safe server-filter navigation. Existing React Router 7.18.4 and
  TanStack Query 5.104.1 pins remain unchanged; no dependency update was needed.

Repository OpenAPI/admin contracts and actual tests define the exposed metadata,
permission, paging and timing semantics. These references do not establish an
ADA deployment or manual accessibility result.
