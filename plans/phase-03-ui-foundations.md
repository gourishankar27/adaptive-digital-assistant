# Phase 03 — contracts, app scaffolds and UI foundations

Status: planned. Prerequisite: Phase 02A target closure.
Read UI-SPEC, STANDARDS, CODEX-WORKFLOW and current OpenAPI. Implement this phase
only; Android chat and admin monitoring are separate phases.

## Goal

Create reproducible Android/web workspaces and a reliable typed contract for the
existing API. End with buildable applications, connection scaffolding and agreed
screen state models. Do not fabricate an admin API or mark scaffold screens as a
finished chat/dashboard.

## Checkpoint A — formalize the existing contract

Inspect every endpoint used by clients: me/capabilities, profiles, conversation
creation/list/detail/events/upgrade, chat/status/trace, scopes, sources, claims and
corrections. Add explicit output schemas to currently untyped response shapes,
preserving field names, UUIDs, status codes, ordering, pagination and UTC
millisecond values. Export OpenAPI and add representative sanitized contract
fixtures for current and legacy responses. Avoid changing retry fingerprints.

Type error envelopes without exposing validator input bodies or credentials.
Document transport timeouts versus persisted request status, missing legacy
traces, unknown labels and prompt-version compatibility. Do not add presumed
streaming/cancel/admin routes. Include tests that compare actual responses with
the exported schema and exercise an authenticated owner boundary.

## Checkpoint B — reproducible workspaces

Create `apps/android/` with a Gradle wrapper/checksum, compatible locked JDK,
AGP/Kotlin/Compose versions, version catalog, test/lint/build tasks and README.
Use Kotlin/Compose/Material 3, coroutines, ViewModel/StateFlow, OkHttp and
kotlinx.serialization. Start with a small app/data structure; extract modules
when boundaries justify them. Choose the app ID and confirm the proposed
minimum SDK against the user's phone; record choices in DECISIONS.

Create `apps/admin-web/` with React/TypeScript/Vite, routing, TanStack Query,
package lock, supported Node version and typecheck/lint/test/build/e2e scripts.
Use a small accessible component system. Both scaffolds may show a clearly
labeled development start screen, not simulated production metrics/conversations.
No database/Ollama dependency or secret belongs in either client.

Add scoped `AGENTS.md` files for both apps: real HTTP adapters, safe rendering,
identity-bound caches, accessible states, explicit fixture adapters, exact
checks and no unrelated framework upgrades. Extend existing project instructions
rather than weakening root rules.

## Checkpoint C — transport, state and design

Implement typed ADA transport DTOs and error mapping, an injected API interface,
and a test-only mock transport. Preserve fields needed for request recovery and
citations. Use 64-bit milliseconds, UUIDs and documented code-point conversion.
Define connection/authentication and screen-state types in each client. Handle
unknown optional fields and future enum values safely; do not treat an unknown
request state as completed or allow unsupported write behavior.

Implement shared semantic design tokens within each platform, accessible basic
controls, theme/text previews and the screen map from UI-SPEC. Android connection
scaffolding needs a secure token-storage interface; Phase 04 completes storage and
real enrollment. Admin token state stays in memory; no sign-in endpoint is
invented. Real adapter errors must never activate demo data.

Document local backend/emulator/USB connections. Debug HTTP exceptions are
host-scoped and excluded from release builds. Provide a web development proxy
for same-origin API calls; do not enable permissive production CORS. Keep the
server's default loopback bind and one-worker deployment.

## Data/API compatibility

No schema migration is expected for typed outputs/scaffolds. If inspection finds
a true contract gap, implement a small compatible change with tests and document
it; an unrelated admin role or new auth system belongs to Phase 05/18. Current
CLI/chat, prompt upgrades and completed replay remain compatible.

## Verification

- Existing Python suite, Ruff and schema/OpenAPI checks; target PostgreSQL checks
  if server behavior changes.
- Android unit/lint/debug build and an emulator launch. Record unavailable SDK or
  emulator checks honestly; a generated project alone is not a successful build.
- Web clean install, typecheck/lint/unit/build; browser launch and keyboard smoke.
- Transport tests for valid/legacy JSON, unknown optional fields, 401, sanitized
  error bodies and no production fixture fallback.
- Repository review for secrets, unpinned tools, accidental public binds and
  changes to released migrations.

## Exit and Codex handoff

Both clients build with documented Windows commands; current responses are
typed/exported; state/transport/design boundaries are usable by the next phases;
baseline server checks still pass. Record exact tool versions and any remaining
device validation. Keep Phase 04/05/06 planned.

Suggested prompt: “Implement only plans/phase-03-ui-foundations.md using
AGENTS.md and plans/STANDARDS.md. Inspect the current API first, complete its
checkpoints, record actual build/test results and stop before chat or admin
feature implementation.”
