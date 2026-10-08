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
