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

## Phase 20 onward planning references — checked 2026-10-16

Primary documentation was read for the planning review, not as proof of an ADA
installation or device benchmark. Recheck versions, terms, licenses and syntax at
implementation time. No package/model was selected, downloaded or installed here.

- [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve) and
  [Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve): private
  tailnet access to a loopback service; distinguish public Funnel, preserve ADA
  account authentication and test the actual Windows topology.
- [Tailscale HTTPS](https://tailscale.com/docs/how-to/set-up-https-certificates):
  MagicDNS/certificate setup and public certificate-name transparency; hostnames
  should not contain private names. No tailnet enrollment was performed.
- OWASP [Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  and [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html):
  adaptive password hashing, TLS, generic errors and bounded verification attempts.
  The exact Argon2id parameters must be measured on the target, not guessed from
  existing SHA-256 random-token verifiers.
- OWASP [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html):
  secure cookie/session handling, renewal, revocation and CSRF considerations.
  New password sessions are distinct from a claim that tokens disappear internally.
- OWASP [SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
  and [LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html):
  application/network target restrictions and untrusted-content handling; prompts
  alone cannot provide safe network authority or prevent all disclosure.
- Microsoft [Task Scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
  and [boot triggers](https://learn.microsoft.com/en-us/windows/win32/taskschd/boot-trigger-example--scripting-):
  supported startup building blocks. Actual pre-login provider/GPU, Docker/service
  readiness, account secret access and restart behavior still require host trials.
- [sherpa-onnx Android](https://k2-fsa.github.io/sherpa/onnx/android/index.html),
  [runtime license](https://github.com/k2-fsa/sherpa-onnx/blob/master/LICENSE),
  [whisper.cpp](https://github.com/ggml-org/whisper.cpp) and
  [Kokoro model card](https://huggingface.co/hexgrad/Kokoro-82M): candidate speech
  tooling/model research. Runtime and exact model/voice/phonemizer licenses are
  separate checks. No source establishes quality, latency or battery use on S24 FE.

## Phase 20 implementation references — checked 2026-10-16

- PostgreSQL18 [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html) and
  [SQL dump recovery](https://www.postgresql.org/docs/18/backup-dump.html): consistent
  snapshots, custom dump/restore and cross-version limits. ADA deliberately tests
  matching client/server major versions; upstream's broader possibilities are not
  automatically accepted by the operational tool.
- Caddy [CLI validation/adaptation](https://caddyserver.com/docs/command-line) and
  [official2.11.7 release](https://github.com/caddyserver/caddy/releases/tag/v2.11.7):
  actual template validation and loopback proxy laboratory. Official Windows archive
  was verified using the release's **SHA512**, recorded in ops/validation-tools.json.
  Initial SHA256 assumption was rejected before binary execution, then corrected to
  the published algorithm. No service or system CA was installed.

## Phase21 implementation reference check — 2026-10-16

Rechecked primary Tailscale [Serve](https://tailscale.com/docs/features/tailscale-serve),
[Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve) and
[HTTPS setup/renewal](https://tailscale.com/docs/how-to/set-up-https-certificates):
private versus public exposure, full hostnames, persisted `--bg`/matching `off`
flags, certificate-name transparency and operator renewal of exported cert files.
These references support the runbook, not a claim of an installed Tailscale daemon.

Caddy [bind](https://caddyserver.com/docs/caddyfile/directives/bind) and the existing
pinned2.11.7 binary were used to validate explicit loopback/private-interface
configuration. Microsoft [New-NetFirewallRule](https://learn.microsoft.com/en-us/powershell/module/netsecurity/new-netfirewallrule)
supports the unexecuted narrowly scoped LAN example. Android
[network security configuration](https://developer.android.com/privacy-and-security/security-config)
supports keeping release platform trust and the existing local-only debug HTTP
exceptions. No dependency upgrade, VPN enrollment, system-CA installation or live
firewall command was performed.

### 2026-10-16 — Phase22 implementation references checked

- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): Argon2id, salts and work-factor guidance.
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): opaque session authority and cookie attributes.
- [argon2-cffi parameters](https://argon2-cffi.readthedocs.io/en/stable/parameters.html) and [API](https://argon2-cffi.readthedocs.io/en/stable/api.html): low-memory profile, verify/check-needs-rehash and exceptions; installed25.1.0/bindings26.1.0 pinned.
- [MDN Web Locks](https://developer.mozilla.org/en-US/docs/Web/API/Web_Locks_API): HTTPS same-origin tab coordination. Failure/race still requires bounded sign-in recovery when unavailable.

These references informed design; actual local cost and integration evidence are
in Phase22 STATUS/WORKLOG. No reference substitutes for a live target test.


### 2026-10-16 — Phase23 implementation references checked

Python3.12 [zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html) documents
IANA zones, folds and tzdata portability. Existing pinned tzdata supports Windows;
local boundary round-trip/fold,23/25hour DST and missing/repeated-midnight behavior
were verified in tests. No dependency upgrade was needed.

Ollama's [embedding API](https://docs.ollama.com/api/embed) is the primary reference
for the existing embedding adapter. Installed tags/digests were inspected locally;
the supported embeddinggemma digest was absent. No native embedding result or
model download is inferred from the exact-hybrid fixture comparison.
