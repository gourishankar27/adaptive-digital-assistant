# Phase 06 — backend monitoring dashboard

Status: planned. Prerequisite: Phase 05 and the Phase 03 web scaffold.
Apply UI-SPEC, STANDARDS and CODEX-WORKFLOW. The first release is read-only.

## Goal and flow

An authorized operator signs in, sees actual backend health, filters requests and
inspects recorded status/error/retrieval metadata. Every enabled view calls the
implemented admin API. Monitoring must remain useful when the provider is down
or a metric is unavailable; it must not show fabricated success or private chat.

## Checkpoint A — authentication and routing

Implement a token-entry screen with account/server confirmation through the
admin-me endpoint. Keep the bearer token in memory only; refresh means sign in
again. Do not place it in local/session storage, URLs, query caches, analytics or
errors. On 401 stop queries and clear private metadata; on 403 show access denied.
Account/server switch and logout clear all queries and detail state.

Use same-origin `/admin` hosting or the documented development proxy. Client
route guards do not replace backend permission checks. Prefer ordinary HTTP
adapters with typed Phase 05 DTOs. There is no cookie/login/refresh endpoint to
assume; changes to authentication belong to a selected backend phase.

Choose route names such as overview, requests, request detail, providers and audit.
Request-detail URLs/keys include both owner ID and request ID. Handle direct
navigation, expired access and missing records. Do not keep a forbidden detail
visible underneath a toast after role revocation.

## Checkpoint B — overview and provider state

Show API/database readiness, provider availability when measured, configured
model/provider, actual in-flight limit and recent-window request counts. Display
units, time range and last successful update. Represent unknown, unavailable,
degraded, stale and zero distinctly. Do not call `/health/live` a guarantee that
chat or PostgreSQL is ready.

Use documented bounded polling and manual refresh; pause expensive refresh when
the page is hidden. Preserve last successful data with a stale marker during a
transient error. Stop polling on authentication loss. Avoid a health poll that
initiates generation or bypasses admission.

Add charts only for server-reported time series, with a table/text alternative.
The initial API may provide counts without a history series; do not synthesize a
chart from random samples. GPU percentage and tokens/sec stay absent unless
Phase 05 actually measures and defines them.

## Checkpoint C — requests and retrieval summary

Build a paginated, server-filtered table with state, owner/request identity,
conversation, attempt, provider/model and known timestamps/duration. Include
filter reset, bounded date window, stable sort and empty/error/loading states.
Keep selected filter/page in safe navigation state; never cache credentials there.
Do not fetch every request to filter in the browser.

Request detail shows a timeline of recorded states/times, sanitized error code,
attempt count, recorded tokens, trace availability and retrieval counts/budgets.
Label request elapsed and retrieval time according to actual server definitions.
Missing legacy values are “Not recorded,” not zero. Selected/cited counts should
reflect their different meanings.

Never render full user text, raw prompt/history, source quotes or hidden model
reasoning in this dashboard. Do not substitute the user's private retrieval
endpoint for missing admin summaries. Show an unavailable state until the server
provides the required authorized metadata.

## Checkpoint D — configuration, audit and accessibility

Display safe provider/limit configuration as read-only text with help that
explains reported capacity. Audit view shows metadata for role and monitoring
events. No shell, database query box, rotate-token button, arbitrary retry,
cancel, purge or prompt editing in this release. A later action needs its own
server contract, permission and receipt before a control can be enabled.

Support keyboard navigation, visible focus, screen-reader table headers/filter
labels, readable contrast, zoom and narrow-window layouts. Keep focus stable
while polling. Do not announce all refresh ticks. Escape text from all errors and
models; safe links are explicit operator actions.

## Implementation structure and data

Use React/TypeScript routing, typed adapters, TanStack Query and small view
components from Phase 03. Query keys include server/principal/filter/composite
request identity. Keep auth state outside persistent query serialization.
No database migration should be needed; contract gaps are Phase 05-compatible
changes with tests, not ad hoc direct database access.

## Verification

Run clean install, typecheck/lint/unit/build and browser end-to-end tasks. Tests
cover normal sign-in, ordinary token rejection, revoked role, failed refresh,
unknown metrics, legacy traces, server pagination, direct request-detail navigation
and two owners with the same request UUID. Test logout/server switch for stale
metadata leakage and absence of persisted tokens.

Exercise a real ADA HTTP server with migrated PostgreSQL and actual admin-role
checks; fixture-only browser screenshots do not establish authorization. Use
sanitized test requests, including a real provider failure if practical. Perform
keyboard/zoom/accessibility review and production-build smoke via the documented
same-origin serving arrangement. Run affected backend checks for any adjustment.

## Exit and handoff

The operator can monitor a real running/down/degraded backend with accurate
metadata, and denied users cannot access it. No mock production fallback or raw
private content is exposed. Document startup/build/serving commands and observed
limits, update STATUS/WORKLOG and stop. Hosting/deployment and future operational
write controls require an explicit selected task.
