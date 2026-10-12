# Explicit preferences and bounded session expression

Phase 14 adds migration **0011** and policy **ada-expression-v1**. Expression
changes wording only. Ownership, admin roles, evidence trust, retrieval ranking,
valid time and tool approval remain independent. These are computational style
controls, not feelings, a diagnosis, or a durable psychological profile.

## Explicit preferences

The allowlist is verbosity (`concise`, `balanced`, `detailed`), initiative
(`respond`, `suggest`), formality (`casual`, `neutral`, `formal`), humor (`none`,
`light`), and cadence (`direct`, `stepwise`). Initiative can suggest; it never
authorizes execution. Cadence structures a reply; it never schedules messages.

Precedence is the saved personality, then explicitly selected account defaults,
knowledge-scope defaults, profile defaults, and conversation overrides. A null or
omitted field inherits; an empty values object resets that target's overrides.
Account-wide preferences require an explicit account-target write. Project facts,
chat content and learned suggestions never become account preferences implicitly.
No learned preference inference is implemented here.

New conversations freeze this inheritance, including each selected field's exact
owner-only settings receipt. Later account/scope/profile changes apply to new
conversations. Existing personality and system-prompt snapshots remain unchanged.
A conversation-target write explicitly refreshes inheritance and applies its
reviewed overrides to future replies. Its binding revision and immutable receipt
audit the update. A running chat returns `409 conversation_busy`. Expression-only
edits do not invalidate a failed request: retries keep its frozen original state,
messages, citations, input fingerprint and response mapping.

All preference writes require an operation UUID and the current target revision.
Same-key, same-content replay returns the original receipt; changed input or a
stale revision conflicts. The authenticated owner is the principal. Admin status,
personality IDs, submitted roles and model output grant no additional access.

## Opt-in session tone

Dynamic tone is off by default and enabled only by an explicit conversation
write. The vector is warmth, focus, energy, playfulness and concern, each an integer
from 0 to 100. Static defaults are warmth 60 (warm) or 30 (reserved), focus 60,
energy 50, playfulness 20 and concern 30. The UI describes tone, not happiness,
attachment or a bond score.

Sessions are partitioned by owner, profile and conversation, with a server-created
session UUID. Only one current session is retained per conversation. They expire
at 30 minutes idle or two hours total. Reading state does not extend or mutate a
session. Expired reads expose defaults; the next new request creates a new UUID.
There is deterministic decay of five points toward defaults per new reserved
turn and per complete five minutes elapsed. Clock rollback cannot reverse decay
or violate native ranges. Failed/completed retries do not advance the turn.

A signal is a proposal until an authenticated caller explicitly reviews it.
The typed signal write requires `reviewed: true`, the exact live session UUID and
latest completed source request. Unknown fields, forged permission/truth/tool
values, booleans masquerading as integers and malformed values are rejected.
Accepted integer targets within -1000..1000 are clamped to 0..100 and limited to
ten points of change per dimension. Only one signal is accepted per turn. Old
sessions, changed bindings, foreign requests and concurrent/in-flight updates
conflict. Signals never extend the existing expiry.

The API accepts `user_selected` or `reviewed_model_signal` reason codes. Normal
assistant text is never parsed into state, and no automatic mood classifier or
extra provider call was added. Android's explicit gentler/focused controls submit
user-selected signals. Model-produced vectors can use the same strict review
contract; a model cannot review or approve on the user's behalf. Native-model
wording compliance remains separate target verification.

Reset creates a new session UUID with defaults. Disabling dynamic tone also
resets the session; the prompt explicitly ignores the vector while disabled.
Resetting preferences clears only that target's overrides, preserving deliberate
inherited settings. Receipts retain fixed reason codes and request IDs, not raw
messages or psychological explanations. There is a hard limit of 5000 retained
expression receipts per owner; no automatic deletion or later retention feature
is implemented.

## Version and request compatibility

| Saved baseline | Expression policy | Factual retrieval |
|---|---|---|
| v1/v2 | Requires the existing explicit, audited baseline upgrade | Existing behavior retained |
| v3 | Explicitly selected expression-v1 overlay | Existing claim retrieval retained |
| v4 | Explicitly selected expression-v1 overlay | Claims and opted-in document retrieval retained |
| Historical request | Original nullable snapshot and messages | Original evidence/response retained |

Baseline v4 stays current; v3/v4 system prompts are byte-preserved. A separately
versioned expression overlay avoids silently upgrading saved prompts. Inactive
legacy/default conversations receive no overlay and store a SQL-null expression
snapshot. Active requests reserve a full typed state/provenance snapshot in the
same short transaction as the request. The expression policy uses exactly 800
UTF-8 bytes, within the existing whole-prompt budget, so different expression
values cannot vary the evidence allocation through their length. Activation adds
this fixed overhead; it does not change scope/time filters, ranking or truth.
All provider inference remains outside open transactions.

## Authenticated HTTP and Android

- `GET/POST /v1/preferences/{kind}/{target_id}`: inspect or explicitly edit/reset
  the owned account, scope, profile or conversation target.
- `GET /v1/conversations/{conversation_id}/expression`: inspect the frozen
  preferences, provenance, bounded current tone and expiry.
- `POST /v1/conversations/{conversation_id}/expression/signals`: accept one
  explicitly reviewed bounded proposal for the latest completed turn.
- `POST /v1/conversations/{conversation_id}/expression/reset`: reset the exact
  selected session with a new operation UUID.
- `GET /v1/expression-receipts/{operation_id}`: recover the original receipt.
- `GET /v1/requests/{request_id}/expression`: inspect original request state,
  including a null legacy snapshot. Reads are owner-only and use `no-store`.

Capabilities advertise `interaction_preferences=explicit_settings_v1`,
`session_expression=ada-expression-v1` and `automatic_affect_inference=false`.
Existing paths, required fields, enums, chat fingerprints and prompt versions
remain intact. Admin remains metadata-only and receives no private preferences.

Android **Settings → Interaction preferences** distinguishes all four targets,
shows inheritance and future-reply behavior, and provides explicit save/reset,
disable, session adjustment and receipt recovery. Format v8 encrypts the exact
operation under the existing Keystore record; v1–v7 remain readable. Restore only
GETs the original receipt. Retry is explicit and identical; local discard does
not undo server settings. Identity switching and 401 clear private state; late
results are fenced. Appearance storage contains no private preferences.

## Installation and verification

Validate migration 0011 on a disposable database before installing into the
intended application database through the normal backup/upgrade procedure. No
application installation or deployment occurred in this phase. Populated
expression history cannot be downgraded; lower history guards run before any DDL.
Default inactive bindings are discardable only when there is no expression
history. See [STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md) for exact
checks, intermediate failures, skips and remaining target verification. Phase 15
learning, streaming, voice and external integrations remain outside this phase.
