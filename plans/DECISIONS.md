# Architecture decisions and open inputs

Recorded 2026-10-08. Change a decision with rationale, compatibility impact and
verification; do not silently rewrite the historical reason.

## Adopted defaults

| Decision | Reason and boundary |
|---|---|
| Keep Phase 0–2 as the baseline | The user's server and real chat work. Fix the fixture without weakening migration validation. |
| Ship interfaces before broader memory/agent work | The user wants a phone client and a separate operator UI. Existing HTTP APIs support a useful chat client. |
| Native Kotlin/Compose Android | Direct Android lifecycle, accessibility and secure-storage integration; no iOS requirement yet. |
| React/TypeScript/Vite admin SPA | Existing FastAPI owns data/auth; a small operator SPA can use typed adapters and same-origin deployment. |
| Server-enforced admin role; metadata-first monitoring | No role currently exists. A normal account token must not expose cross-user private content. |
| Manual token enrollment initially | Compatible with today's CLI-issued bearer tokens. Multi-device enrollment/revocation is Phase 18. |
| Single worker remains | Capacity is process-local today. More processes/jobs require a shared admission design. |
| Static warm persona now; dynamic state later | Existing style config is usable. Affect/learning needs bounded validation and opt-in provenance. |
| Proposed routes are not capabilities | OpenAPI/current code define the implemented contract; clients gate unsupported features. |
| Phase numbers are identifiers | Dependencies, not arbitrary numbering, determine eligible work. Streaming may follow the first Android release. |

## Resolve during the relevant phase

- Phase 03: actual phone OS, development JDK/Android SDK/Node availability,
  compatible pinned tool versions, app package identifier and debug connection.
- Phase 04: physical-phone test access and the desired private remote access
  method. Use emulator/USB development without exposing database/provider ports.
- Phases 05–06: which account receives an explicit locally granted admin role,
  monitoring retention and any approved metadata beyond the minimum.
- Phase 08: first accepted document formats and content/storage quotas. Begin
  with text/Markdown; PDF parsing is a separate checkpoint.
- Phase 10: available embedding model/resources, exact versus approximate search
  tradeoff, evaluation dataset and measured recall/capacity.
- Phase 12: first selected tools; read-only built-ins before external writes.
- Phases 14–15: user-selected preference controls and consent/reset behavior.
- Phase 18: device credential lifecycle, retention/deletion policy, backup target
  and release exposure. Operational policy needs explicit user choices.
- Phase 19: whether local mobile inference or any particular integration is
  needed at all, using actual phone hardware and authorized accounts.

These inputs do not block writing the plans. A Codex implementation should
progress with the documented defaults where reversible, and ask only for a
material missing product choice instead of inventing credentials or hardware.
