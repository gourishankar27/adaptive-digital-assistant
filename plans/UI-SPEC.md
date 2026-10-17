# UI specification

Design target, recorded 2026-10-08. Phase 03 implements the connection, transport,
state and design foundations; the feature screens below remain phase-gated.
Read each phase's dependency and verification gates before enabling a feature.

## Products and stack

| Product | Purpose | Default implementation | First usable phase |
|---|---|---|---|
| Android | Personal chat, sources and owned memory | Kotlin, Jetpack Compose/Material 3, ViewModel, StateFlow, coroutines, OkHttp and kotlinx.serialization | 04 |
| Admin web | Authorized backend monitoring | React, TypeScript, Vite, router, TanStack Query, accessible components | 06 |

Place them in `apps/android/` and `apps/admin-web/`. The existing Python backend
remains the API. Choose and lock compatible framework/tool versions during Phase
03; these plans do not prescribe unverified version numbers. Android API 26 is
the proposed minimum, subject to the user's actual phone and selected libraries.
Avoid a framework rewrite merely to add a second client later.

The Android app uses unidirectional state: screen action → ViewModel → repository
→ ADA API → typed result → screen state. Separate transport DTOs from presentation
models. The web app uses typed API adapters and query keys bound to the server,
authenticated principal and filters. Neither app holds database/provider secrets.

## Android navigation and screens

Use a compact phone layout with Chat, Memory and Settings destinations. Enable
Memory in Phase 07. Conversation selection is a sheet or a separate screen;
source detail opens from a reply. Tablet layouts may add a conversation pane
without changing the data contract. Keep a readable text-first interface: ADA's
warmth comes through its language, not artificial emotion gauges.

| Screen | Content and controls | Required states |
|---|---|---|
| Connect | ADA server URL, username/password, advanced token option, Connect, account/server confirmation | Empty, validating, connected, unreachable, invalid token, incompatible contract |
| Conversations | Paginated owned list, scope/style summary, New conversation | Loading, empty, loaded, error, refresh, pending conversation |
| New conversation | Title, owned scope or new personal scope, available profile | Selection, validation, creating, uncertain creation outcome |
| Chat | History, composer, Send, pending/status row, Retry, source chips | Loading history, ready, sending, running, reconnecting, failed, completed, access lost |
| Sources | Exact quote, source type/version, validity, optional technical detail | Available, unknown label, missing legacy trace, access denied |
| Memory, Phase 07 | Scope picker, facts/preferences/decisions, evidence and correction forms | Empty, loading, historical view, conflicting assertions, validation, save/recovery |
| Settings | Connection/account, theme/text settings, profiles, explicit prompt upgrade | Current values, changed local settings, new profile saved, upgrade conflict, logout |

Every loading/error state must have defined actions. Preserve the draft through
ordinary rotation/navigation; clear private state on logout/account/server switch.
Show the chosen knowledge scope near chat context. A new style selection must not
silently alter the scope or frozen personality of an existing conversation.

### Chat interaction

Generate a request UUID before sending and persist the exact conversation ID,
content, `as_of`, `use_memory`, normalized server and authenticated identity.
Protect this local journal and any cached content with encryption using a key
managed by Android Keystore. Commit the journal before network submission.
Preserve it through process death; never replay it as another principal.

| Observed condition | UI behavior |
|---|---|
| POST in progress | Show submitted text and an honest pending indicator; prevent accidental duplicate Send |
| HTTP timeout / connection lost | Outcome unknown; query the same request ID on reconnect |
| Request running | Poll with bounded backoff; navigating away does not cancel generation |
| Request completed | Reconcile one answer with its original source cards; remove pending journal after durable reconciliation |
| Request failed | Show sanitized error and an explicit retry action preserving the reserved payload |
| Request absent, correct identity verified | Offer submission with the same ID/payload; do not invent a new request automatically |
| ID/content/options conflict | Explain that retry data differs; recover the original payload or offer a consciously new message |
| Stale conversation history/revision | Refresh history; explain why a failed request cannot be treated as a new turn invisibly |
| 401 / revoked token | Stop retries, hide private loaded data and reconnect under the correct account |
| 403 / 404 for a resource | Clear inaccessible content; avoid disclosing whether another user's resource exists |
| 413 / 422 | Keep draft, show the relevant size/field issue, allow editing before a new submission |
| 429 / 503 | Respect Retry-After when present; bounded jitter/backoff, visible retry state |

There is no Stop generation button in the initial app. A local “stop waiting” or
leaving a screen is a client action only. Add a real Stop control in Phase 16 after
the server supports cancellation. Never display fabricated token streaming.

Creation endpoints for profiles/scopes/conversations do not currently take
idempotency keys. Do not blindly retry their POST after an ambiguous timeout.
Refresh the relevant list and help the user resolve the outcome. Only enable
automatic creation retry if a separately tested server contract makes it safe.

### History and sources

Page the actual event endpoint with its existing ordering; merge by event ID and
request ID. Reconcile local pending items with persisted user/assistant events so
neither appears twice. Keep incomplete and failed turns visually distinct from
completed assistant replies. Do not derive a missing answer from a trace.

Source labels such as `[M1]` belong to one request. Resolve them using that
request's returned `citations`, including when browsing history after restart.
Selected but uncited material belongs in an optional retrieval detail view.
Unknown labels get a plain unavailable-source explanation, never an invented card.
Show “Source” rather than implying a citation proves the sentence is correct.

Keep exact source text, UTF-8 hashes and code-point offsets intact. Convert
Android UTF-16 selection boundaries before making a memory write. Store epoch
milliseconds as Long; present a local timezone while preserving the original
instant. Never silently normalize a quote's whitespace to make a span match.

## Admin information architecture

Admin UI entry requires the server's explicit admin authorization from Phase 05.
An ordinary bearer token and a user named Gourishankar do not imply that role.
Client route guards improve navigation; the server enforces every admin operation.

| Screen | Metadata shown | Boundaries |
|---|---|---|
| Sign in | HTTPS server, username/password, advanced token option, admin check, current operator | Token held in memory; no public account enrollment |
| Overview | Backend readiness, actual request counts, capacity, last update | Unknown/degraded metrics distinct from zero |
| Requests | Server-filtered/pageable states, owner ID, request ID, attempt, model, timestamps | No raw messages or source quotes in list results |
| Request detail | Persisted state, recorded error, known timing, retrieval counts/budgets | Route includes owner ID and request ID; no hidden model reasoning |
| Providers/configuration | Safe provider/model tag and reported limits | No credentials, secret URLs, shell actions or invented GPU measurements |
| Audit | Metadata for role changes and authorized monitoring access | No bearer tokens, private body text or automatic admin mutations |

The first admin release is read-only. Add an operational action only in a future
selected phase with an explicit server endpoint, authorization rule, preview,
receipt and failure tests. A dashboard button must never disguise a direct
database command, CLI command or remote shell.

Poll bounded endpoints at a documented interval; pause expensive refresh while
the page is hidden and allow manual refresh. Show the last successful update,
stale data and failed refresh separately. Filter/page on the server instead of
downloading the database. Label queue, end-to-end and provider durations according
to what is actually measured. Do not infer GPU use or tokens/sec from wall time.

Use exact same-origin HTTPS `/admin` hosting for Phase22 ordinary password login.
Host-only Secure/HttpOnly/SameSite=Strict cookies and exact-origin/CSRF checks use
the selected Phase22 backend contract. Reopen/renew clears queries and verifies
the admin grant. The advanced bearer adapter remains memory-only and supports
the fixed loopback development proxy. Broad CORS remains unsupported.

## Visual and accessibility rules

Define a small token set: semantic colors, typography, spacing, corner sizes,
focus and error styles, light/dark themes. Android and web share intent, not
platform-inappropriate pixel layouts. Use clear contrast, readable long quotes,
system text scaling, meaningful touch targets and visible keyboard focus.

Test Android TalkBack, large font/display size, keyboard appearance, landscape,
long messages and small displays. Test web keyboard navigation, screen-reader
labels, zoom, narrow desktop windows and accessible table/filter controls. Move
focus to validation messages deliberately; do not announce every polling tick.
Charts need real data, units and a text/table equivalent.

Escape/safely render message and source content. Link schemes are allowlisted;
opening an external link is a user action. Code blocks are selectable text, never
an execution affordance. Keep IDs/hashes behind Details and preserve source labels
for assistive technology. No animations that obstruct reading or request status.

## Connection and release checks

The backend keeps its loopback default. For development, document an Android
emulator host connection and USB `adb reverse tcp:8000 tcp:8000` for a physical
phone. Allow HTTP only for explicitly listed development hosts in debug builds.
Release builds use HTTPS or an explicitly configured encrypted private access
method; never disable TLS verification to make a phone connect.

A usable Android release requires a tested emulator flow and a real-phone smoke
test against ADA. A usable admin release requires an HTTP integration flow with
the real authorization layer, plus browser interaction checks. Report fake
provider tests separately from a real Ollama reply. Keep signing credentials out
of Git; release distribution is a later explicit decision.
