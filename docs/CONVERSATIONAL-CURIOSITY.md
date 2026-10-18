# Conversational curiosity — Phase 25

ADA can offer an optional question after a completed reply, prepare a later inbox
draft, or start a conversation from a draft you choose. Curiosity is **off for
every owner until explicit opt-in**. There are no timers, push notifications,
external messages, hidden profiles or automatic factual-memory writes.

This source needs migration **0017 / 60 tables**. It has not been installed in
the running private service or on the S24FE. Earlier installation and validation
records remain historical. See [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md) for actual checks, corrected failures, intermittency
and remaining target verification.

## Installation and developer checks

Use the [developer walkthrough](HOW-TO-USE-ADA.md) for the pinned Python/JDK/Android
tools and [private setup guide](PRIVATE-SETUP-WINDOWS-TAILSCALE.md) for HTTPS/login.
No dependency, wrapper, model download, Android permission or TLS change is needed.
Keep PostgreSQL/Ollama private and use one Uvicorn worker.

Before a separately authorized installation, back up the intended database using
the [recovery runbook](SECURITY-AND-OPERATIONS.md). Migration0017 adds three empty
owner-content tables; it does not enroll an account in curiosity, rewrite chats,
change prompts, grant admin or modify password/session credentials. Validate on
a disposable database first. These are operator instructions, not commands run
against the application database during this implementation:

```powershell
./.venv/Scripts/python.exe -m alembic upgrade head
./.venv/Scripts/python.exe -m alembic check
```

Build Android app **18 / 0.25.0-curiosity** from `apps/android`:

```powershell
./gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:assembleDebugAndroidTest :app:assembleRelease
```

The new server advertises `curiosity_protocol=ada-curiosity-v1` and
`curiosity_notifications=false`. An older server or missing capability disables
the controls. No `.env` flag activates curiosity for an owner. Installing this
checkout alone does not change the running service or an installed app.

For backend checks, set `ADA_TEST_DATABASE_URL` to the dedicated PostgreSQL test
database and `ADA_TEST_PG_BIN` to the matching native tools, then run from root:

```powershell
./.venv/Scripts/python.exe -m pytest -q -ra
./.venv/Scripts/python.exe -m ruff check src tests scripts migrations ops/web-broker
./.venv/Scripts/python.exe -m ruff format --check src tests scripts migrations ops/web-broker
./.venv/Scripts/python.exe scripts/export_openapi.py
./.venv/Scripts/python.exe scripts/evaluate_curiosity.py
```

The evaluation uses only temporary SQLite databases and frozen public examples.
`--native` adds one answer with the configured, already installed loopback Ollama
model. It does not download a model, access the application database, use private
owner history or enable web research. Results identify fixture checks and
synthetic feedback; they are not real owner ratings or general quality estimates.

## Enable and use it

1. Sign into ADA through your normal private server. Open **Settings → Questions
   & curiosity settings**, or **Questions & curiosity** inside an owned chat.
2. Choose **Allow curiosity**, chat/inbox channels, frequency, topic choices and
   depth. Save the settings. Interests, work and routines are available by default
   behind the global off switch. Relationships and reflection start blocked and
   also require personal depth. Each topic can be enabled, paused or blocked.
3. Chat normally. ADA's actual answer is recorded first. On an eligible new turn,
   the Android client can request one companion question. Default cadence is every
   third completed reply; rare is every fifth. Each eligible reply is an explicit
   settings choice. Concise and explicitly task-focused expression settings
   suppress companions. A reply already containing a question mark receives no
   extra companion. This bounds new curiosity cards; it does not rewrite arbitrary
   questions already generated in an ordinary model answer.
4. Use **Skip**, **Not now**, **Dismiss**, **Do not ask this again**, or **Pause this
   topic** without supplying a reason. Not now hides the premise for one hour,
   subject to the original expiry. Do not ask again suppresses that catalogue
   question type across scopes. Topic pause is reversible in settings.
5. For a later draft, select an owned conversation/scope and use **Prepare an inbox
   question**. A draft is private inbox content, not a sent assistant chat event.
   **Interview me: ask a question now** explicitly requests a question outside the
   normal cadence. It does not start a hidden continuing interview or schedule.
6. A generic starter is labeled as having no personal premise. To revisit an
   earlier thread, choose an original statement from the current scope. ADA shows
   its exact selected source span separately and asks an uncertain follow-up. Use
   **Inspect exact original** to verify the original hash and Unicode span. A
   quotation proves what was recorded, not that it is true or still current.
7. Open the draft with an existing style. Opening atomically creates one real
   conversation under the same scope, using an exact durable operation ID. It
   creates **no user-authored message**. The starter is displayed separately from
   ordinary chat events. **Continue in chat** opens that conversation.
8. Type your answer and choose **Send my answer**. Only your exact typed text
   becomes an ordinary user chat statement, with the existing source trust and
   normal request UUID/replay. It remains in conversation history. Creating a
   saved factual claim or interaction preference still requires the existing
   explicit memory/review/settings paths. The answer route does not automatically
   search saved memory or documents.
9. Optionally rate a question Helpful/Not helpful. These owner-only counters do
   not train a model, infer psychology, change cadence or reward conversation
   length. **Turn all curiosity off** remains available with an unconfirmed
   delivery; only an acknowledged settings update confirms the server is off.

Catalogue questions are deterministic, bounded wording, not independently generated
personal insight. Version1 has30generic templates and five source-linked variants.
Relevance starts with the current task's broad topic or your explicit topic/source
choice. The system never infers feelings, diagnosis, attraction, intimate facts,
permissions or concern from missing memory. There is no claim ADA was privately
thinking about you. Broader naturalness/usefulness needs real owner feedback.

## Limits, privacy and retention

| Rule | Phase25 behavior |
|---|---|
| Default | Global off; no notification channel can be enabled |
| Ordinary inbox | At most two drafts per owner per UTC day across all scopes |
| Explicit interview | At most ten requested questions per owner per UTC day; topic permissions still apply |
| Reply | One saved companion per completed request; cadence/task-focus/question-mark checks |
| Repetition | Thirty-day owner-wide catalogue-key deduplication; explicit suppression persists until owner erasure |
| Draft |24h eligibility; unavailable, stale, revoked and deferred premises are hidden |
| Storage |100retained question rows/owner,5000minimal receipts including a reserved final global-off slot; eight encrypted pending client operations, with the last reserved for off |
| Model/context | No inference for selecting drafts; answering uses existing chat admission and whole prompt budget |
| Channels | Chat and inbox only; scheduling/notifications require a later selected phase and fresh consent |

UTC day boundaries are fixed, so switching scopes or timezones cannot multiply
the allowance. A backwards clock does not reset it. No automatic retries run
after timeouts or unknown outcomes. If the catalogue has no unasked permitted
question, ADA offers none rather than inventing a premise.

Source pins require an accessible, exact, owner/scope-bound original with
`user_explicit` trust and a valid current support window when claims reference it.
Assistant/generated/imported text cannot supply a personal premise. Hash/span
checks run before display and context; wrong-owner/scope, corrected, unavailable,
future or tampered sources are rejected/hidden. Source text never authorizes a
tool, unrelated private read, disclosure, memory write or topic change.

Changing the curiosity policy revokes and scrubs unanswered drafts; an already
admitted ordinary owner answer can finish. Skip/dismiss removes draft text,
source IDs/pins and policy payload. Expired drafts are hidden immediately and
scrubbed lazily on the next curiosity policy/create mutation. Closed draft rows
retain only topic, catalogue key, UUID/state/time metadata for30days, then lazy
cleanup removes them. This does not delete underlying chats, original sources,
saved claims or completed request snapshots. Minimal operation receipts and
explicit permanent suppressions remain until owner erasure. Limits stop further
curiosity writes rather than silently discarding exact recovery keys.

All three new tables are classified private owner content: the erasure inventory
now covers48content tables; encrypted recovery covers60total tables. Backup-v3
is paired only with0017. Old0015/v1 and0016/v2 artifacts retain their reviewed
inventories and credential quarantine. A0017restore verifies original row hashes,
then disables restored curiosity and increments its live policy revision. Pending
drafts cannot resume under restored consent. Historical completed chat replay is
preserved. No backup, erasure or migration of the live database was run here.

## Recovery and troubleshooting

Android journalv14 reads v1–v13 and encrypts exact operation bodies/UUIDs before
POST. Its bounded queue allows global off to coexist with an unconfirmed create
or answer. Owner/server/epoch changes fence private state; scope changes fence
late source/answer display. No credential or appearance-preference bypass exists.

Reopening performs GET-only policy/receipt recovery. A missing receipt or unknown
request is not permission for an automatic resend. **Check original delivery**
reads its saved key. **Retry exact delivery explicitly** reuses the encrypted body
and UUID. `reconcile_required` means bookkeeping needs explicit exact replay:
an answer may have completed before its question acknowledgement, or a collision
may have been detected before rejection was committed. Replay completes or rejects
that intent without adopting unrelated text or generating another answer.
Ordinary failed-request history/revision checks apply.
The intent also binds the ordinary request's conversation and exact content
fingerprint. It cannot adopt a different message using the same UUID. A definitive
pre-admission rejection (for example, a UTF-8 prompt budget overflow) has a durable
`rejected` receipt and reopens the eligible question for a reviewed new answer.
The first rejected POST still returns its original HTTP error; exact replay returns
the saved rejection. Android checks the receipt before clearing an answer journal,
and keeps unknown, running, failed and bookkeeping-pending deliveries. A saved
answer delivery prevents a second answer UUID for that question. Dismissing the
question does not cancel an already admitted chat request.

When a policy changed, refresh and review the current revision before saving a
new operation. Definitively rejected payloads are not silently rebound to new
values. On429wait for the daily quota/rate window. On401sign in again; never replay
private operations automatically. Stale/expired/paused questions can be dismissed
without exposing their old premise. Optional curiosity failure leaves normal
text-chat controls available.

## API and compatibility

All operations require a current authenticated owner. Versioned additions:

| Method | Path | Purpose |
|---|---|---|
| GET / POST | `/v1/curiosity/policy` | Read explicit controls / update with expected revision and operation UUID |
| GET | `/v1/curiosity/receipts/{id}` | Reconcile the original operation |
| GET / POST | `/v1/scopes/{id}/curiosity/questions` | Read owned questions / prepare a permitted question |
| GET | `/v1/curiosity/questions/{id}` | Inspect original saved state and source |
| POST | `/v1/curiosity/questions/{id}/actions` | Skip, defer, dismiss, suppress, pause or rate |
| POST | `/v1/curiosity/questions/{id}/open` | Atomically open a conversation without inventing user text |
| POST | `/v1/curiosity/questions/{id}/answer` | Reserve exact intent, then submit ordinary typed chat outside the transaction |
| GET | `/v1/conversations/{id}/curiosity/questions` | Read that conversation's companion/starter records |
| GET | `/v1/curiosity/metrics` | Read owner-only counts; no hidden rating inference |

Nine new path templates/eleven methods/twelve schemas export126paths/168schemas.
All117earlier paths and155non-capability schema definitions remain unchanged.
Two optional capability fields are additive. Chat inputs/fingerprints, old prompts,
M/D/C/W evidence, completed replay, credential rules and previous migration bytes
remain intact. New optional conversation context has its own version, source/policy
snapshot and trace budget marker. It is not factual evidence and is omitted when
it cannot fit without exceeding the whole prompt budget. Historical request
messages retain their exact original context. Admin views receive no curiosity
questions, answers, source quotes, topic choices or psychological profiles; this
phase adds only owner-facing metrics, with existing admin views unchanged.

## Validation and remaining gates

Local checks cover SQLite/native PostgreSQL controls/owner quota concurrency,
populated upgrade/downgrade guards, old/new encrypted restore, erasure, exact
Unicode pins, opt-out during generation, duplicate open/answer and client late
logout/scope callbacks. Separate emulator tests use real HTTP/PG/password/Keystore
with an explicit FakeProvider, including actual force-stop and retained-key
recovery. Actual counts, earlier failures and refresh intermittency stay in STATUS.

The frozen public6development+3holdout cases check topic permissions, generic
premises, exact sources, stale suppression, repetition, ordinary answers and
synthetic accepted/skipped/helpful counters. One installed qwen3.8:27b answer and
completed replay passed; Codex's review observed an on-topic single follow-up.
This is not independent owner-rated helpfulness or general premise/naturalness
accuracy. No real private dataset was used.

Still required: physical S24FE/Android16, TalkBack/large-font, signed HTTPS/handover,
larger independent question/premise/helpfulness review, repeated performance/soak
and the existing voice/G-41 release reliability gates. No physical notification
test applies yet because delivery/scheduling is not implemented. Phase26–31 remain
planned; no later-phase code, deployment or automatic activation was performed.
