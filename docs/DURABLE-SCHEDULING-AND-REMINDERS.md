# Durable scheduling and reminders

Phase 27 adds private, reviewed reminders and optional curiosity questions to the
ADA inbox. The server dispatcher and each owner's scheduling consent are **off
by default**. Android checks the inbox while foregrounded; there is no background
push provider, device registration, notification permission or lock-screen text.
An offline or sleeping laptop cannot dispatch. An offline/backgrounded phone can
see durable items after reconnecting, without a promise of timely notification.

The implementation and isolated checks are recorded in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md). This guide does not
install or migrate your running service. The existing normal phone app and
private installation were not updated during implementation.

## 1. Prepare a selected installation

1. Read [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md),
   [private Windows/Tailscale setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md) and
   [always-on operations](ALWAYS-ON-OPERATIONS.md). Keep PostgreSQL and the API
   private. Android talks only to authenticated ADA HTTPS, never to PostgreSQL
   or Ollama. Preserve your private `.env`; do not copy credentials into logs.
2. Check the pinned environment and the intended database:

   ```powershell
   ./.venv/Scripts/python.exe -m pip check
   ./.venv/Scripts/ada.exe doctor
   ```

   Current source requires **0018 / 65 tables**, including `alembic_version`.
   Phase 27 adds five owner-content tables, bringing the content-erasure inventory
   to 53 tables. Released 0001–0017 are unchanged. No prompt upgrade is required.
3. Before upgrading, use the compatible, reviewed encrypted backup and erasure
   ledger procedure for your installed schema. See
   [release readiness](RELEASE-READINESS.md),
   [database administration](DATABASE-ADMINISTRATION-WINDOWS.md) and
   [security/recovery](SECURITY-AND-OPERATIONS.md). Verify a recovery point with
   PostgreSQL client tools matching the database server's major version.
   Retain the independently recoverable key; a copied Windows DPAPI blob alone
   does not recover a lost Windows profile.
4. Stop the selected installation's API through its existing owner-controlled
   startup mechanism. Apply the migration only as a reviewed installation action:

   ```powershell
   ./.venv/Scripts/python.exe -m alembic upgrade head
   ./.venv/Scripts/ada.exe doctor
   ```

   The supervisor never migrates automatically. Downgrade refuses to discard
   scheduling/revocation history. Do not bypass the guard to run older source.
5. Keep **one API worker** and one installation owner. Use the existing foreground
   `./scripts/start.ps1` or the separately installed Phase 26 supervisor, with
   external PostgreSQL/Ollama already available. Do not start both. The API owns
   one lightweight, non-inference dispatcher. There is no additional GPU/model
   worker and no second OS-backup scheduler.
6. Initially leave `ADA_SCHEDULER_ENABLED=false` in the protected `.env`. You can
   review plans with dispatch stopped. To enable delivery deliberately, set:

   ```dotenv
   ADA_SCHEDULER_ENABLED=true
   ```

   Restart only that selected single-worker service. To stop all future dispatch,
   set it back to false and restart. This global switch does not grant owner
   consent. Resource pressure or stale/unavailable database health can delay
   dispatch. Reminder/catalogue publication needs no model and does not wait for
   model readiness or the inference quiet period; consolidation keeps those gates.

## 2. Create a reminder in Android

1. Use a compatible app build, sign in, and verify the intended server/account.
   Source app version is 21 / `0.27.0-scheduling`. Build/install instructions remain
   in [the Android README](../apps/android/README.md). Release builds require
   verified HTTPS. The implementation run installed only a separate emulator
   validation app, not the normal app.
2. Open **Reminders & inbox** from the chat menu or Settings. The page identifies
   the current scope. Expand **Scope and conversation profile** to select an
   owned scope and the profile used when you explicitly open a conversation.
3. Turn on **Allow scheduled reminders and questions**. This is separate from
   curiosity consent. If the server dispatcher is stopped, the page explains that
   review works while delivery is unavailable.
4. Tap **New reminder or question**, then **Reminder**. Enter up to 1000 code
   points of reminder text. Choose an IANA timezone such as `America/Phoenix` or
   `America/New_York` and a local start in `YYYY-MM-DDTHH:mm` form.
5. Select once, daily or weekly. Recurring plans have 1–100 candidate dates.
   Expand **Allowed hours, expiry and DST**. Allowed hours form a same-day interval
   with an exclusive end, initially 08:00–22:00; use 24:00 only for the end. An
   overnight interval must be expressed as separate reviewed schedules. Expiry is
   ISO 8601 with an offset, at whole-millisecond precision, no more than 366 days
   from preview. The first planned occurrence must not already be in the past.
6. Tap **Preview occurrences**. Check the text, timezone, pinned timezone-data
   version and exact local/UTC dates. Expand the remaining dates when needed.
   A preview is valid for 15 minutes. Editing the form clears it; expired or changed
   authority requires a fresh preview. Preview alone never schedules delivery.
7. Tap **Confirm schedule**. The list shows state, next instant, delivered/missed
   counts and any suppression reason. Use **Delivery receipts** to inspect actual
   occurrence states, attempts and suppression. Older inbox/receipt pages remain
   accessible; the client holds at most 100 entries per current page.
8. Use **Pause**, **Snooze 1 hour**, **Edit**, **Delete** or **Reauthorize** as
   appropriate. Edit requires a new preview/confirmation. Delete requires explicit
   confirmation and suppresses further occurrences; it is not full account erasure.

## 3. Schedule an optional question

Enable the separate **Questions & curiosity** policy, later inbox and intended
topic/depth first. Then choose **Optional question** in the schedule editor.
Existing topic, cadence, daily cap, scope and source checks still apply. A
scheduling switch never silently enables curiosity. Changing curiosity policy
pauses affected question schedules for explicit reauthorization.

Questions come from the existing bounded Phase 25 catalogue. There is no new
model-generated personal profile or background inference. The API also supports
an optional exact original-user-source pin; if present, preview displays its
original quote and trust. The Android new-question editor selects a topic;
it does not provide a new source picker. Original source/version/hash/scope
changes invalidate an old pin and require review. Source deletion or curiosity
cleanup makes dependent question content unavailable.

## 4. Understand time and recovery

| Situation | Defined behavior |
|---|---|
| Spring DST gap | A nonexistent one-time local time is rejected. Recurring plans either skip that candidate date or reject the preview, according to your choice. |
| Autumn DST fold | Preview rejects an ambiguous time until you explicitly choose the first or second occurrence. |
| Travel / phone timezone changes | The stored schedule keeps its selected timezone. Edit and preview to change it; phone location never silently moves it. |
| Timezone-data upgrade | Plans record pinned `tzdata-2026.5` UTC dates. A rules-version mismatch pauses dispatch for a new preview rather than silently recalculating. |
| Missed dates / forward clock change | Only the latest eligible missed date is delivered; earlier dates are marked missed. No catch-up flood. |
| Outside allowed hours | Due delivery waits until an allowed instant, subject to expiry and latest-only catch-up. |
| Backward clock change | Delivered occurrence keys remain deduplicated. Edited plans and snoozed work retain separate reviewed-plan/execution generations. |
| Expiry | No later delivery; expired inbox content is withheld. Snooze does not extend expiry. API snooze must be in the future and at most 7 days away. |
| Dispatcher crash | Atomic leases last 30 seconds and are fenced by generation/token. Abandoned work can be reclaimed, with at most 3 attempts. |
| Publication / lost acknowledgement | Publication commits the durable inbox item before client acknowledgement. Reusing the exact acknowledgement key returns its receipt; it does not create another item. |

UTC dates use the pinned Python `tzdata` package on Windows and other platforms,
not whichever timezone database happens to be installed on the host. See the
[Python timezone documentation](https://docs.python.org/3.14/library/zoneinfo.html)
and [tzdata project](https://tzdata.python.org/). Native concurrent-claimer tests
exercise PostgreSQL locking; the underlying locking semantics are documented in
[PostgreSQL SELECT](https://www.postgresql.org/docs/current/sql-select.html).

## 5. Read and open the inbox

While the scheduling screen is foregrounded, Android polls about every 30 seconds;
**Refresh** requests a current page. There is no background polling service or
timely wake-up promise. Reopening can recover already committed items. Inbox IDs
and occurrence IDs deduplicate display. Acknowledgement means the server recorded
your explicit action, not that a push was delivered or that someone read it.

**Acknowledge**, **Dismiss** and **Snooze 1 hour** are explicit saved operations.
**Open conversation** creates or resumes an owned conversation using the selected
profile. It never fabricates a user message, submits a reply or silently starts
inference. **Continue conversation** navigates to the resulting conversation;
you decide what to send. Expired/revoked/unavailable content cannot be reopened
as a new question premise. Wrong-owner IDs are not a route around authorization.

Android reserves exact operation IDs/bodies in the Keystore-encrypted v15 journal
before POST. Older v1–v14 journals remain readable. After interruption, reconnect
to the verified same server/owner/epoch and use **Check saved result**. Recovery
performs GET only. **Retry original change** is explicit and uses the same key and
body. **Review saved preview** selects its original scope before presenting it.
An unknown result is not permission to create a replacement schedule or key.

## 6. Stop authority and inspect metadata

| Action | Effect on durable scheduling |
|---|---|
| Ordinary password-session logout, expiry or refresh | Does not erase an intentionally confirmed durable grant. Private client access still ends when its session ends. |
| Revoke/rotate/expire the originating device credential | Pauses schedules originating from that credential. A replacement token does not inherit the grant. |
| Rotate a legacy credential | Pauses grants originating from that legacy credential. |
| Set/reset/change password or revoke all password sessions | Turns scheduling consent off and pauses automation by default. |
| Turn owner scheduling consent off | Pauses all of that owner's schedules and suppresses pending publication. Turning it on alone does not resume them. |
| Reauthorize a paused schedule | Rechecks current owner, epoch, consent, scope, source, timezone rules and originating credential. Changed/expired intent requires a new preview. |
| Global operator stop | Prevents further claim/publication. Other owners cannot override it. |

These changes increment execution generations, fencing late workers. Checks run
again before private background payload loading and publication. Owner/scope/source
deletion and epoch changes cannot be bypassed by an old lease or receipt.

The admin dashboard's **Scheduling** view reads only aggregate state counts,
global enabled state, loop liveness and fixed process-error metadata. It does not
expose reminder text, quotes, owner identifiers, delivery registrations or tokens.
The server requires a current explicit admin grant and audits `monitor.scheduling`;
the screen provides no configuration/write control. A live loop alone does not
prove timely delivery, availability of the laptop or notification receipt.

## 7. Retention, limits and restore

The five new private tables are `schedule_consents`, `schedules`,
`schedule_occurrences`, `schedule_inbox` and `schedule_receipts`. All participate
in owner-content erasure and versioned encrypted recovery. They are not factual
memory or retrieval evidence. A schedule deletion scrubs its definition/source
snapshot but retains applicable operation receipts and already-created inbox
history under the existing explicit-owner-deletion policy. Full saved-content
erasure removes the entire closure; backups use the independent erasure ledger
before restored access may be considered. There is no new automatic pruning.

Per owner: 100 retained schedules, 1000 occurrence rows, 1000 inbox rows and 5000
operation receipts. The final receipt slot is reserved for consent off. Android
keeps at most 8 exact pending operations, likewise reserving an off slot. Hitting
a bound produces a fixed error; deleting a schedule does not recycle retained
history. There is no silent retention deletion or unlimited recurrence. Plan
capacity consciously; explicit full content erasure is broader than clearing a
reminder and requires its own reviewed workflow.

Current schema uses **`ada-postgres-backup-v4` /0018**. Existing v1/0015, v2/0016, v3/0017
and the separate legacy 0005 path remain supported with their own inventories.
Restore verifies the original archived row hashes first, then quarantines access,
turns scheduling consent off, increments schedule generations, quarantines
schedules and suppresses pending/running occurrences. It never delivers recovered
work automatically. After a reviewed installation and re-established identity,
inspect recovered intent and create a fresh preview whenever authority/source/
timezone/expiry changed. Use only a new isolated destination for recovery tests.

## 8. Troubleshoot

| Symptom | Check |
|---|---|
| Schedules unsupported | Verify server capabilities report `ada-scheduling-v1`, the compatible app, and database head 0018. Do not connect to the provider URL. |
| Nothing arrives | Check global dispatcher, owner consent, active schedule, scope, allowed hours, expiry, snooze, server awake/online and foreground refresh. Inspect receipts before retrying. |
| Schedule paused | Read its reason: owner/device/password/source/policy/epoch/timezone changes require deliberate reauthorization or a new preview. |
| Preview rejected | Check future local time, canonical IANA zone, DST choice, allowed hours, count, expiry and whole-millisecond precision. A one-time spring-gap time cannot be skipped. |
| Optional question suppressed | Check separate curiosity inbox/topic/depth consent and daily cadence/cap. These limits are independent of reminder consent. |
| Unknown submitted result | Keep the encrypted pending key; check the receipt, then explicitly retry the original. Do not clear data or submit a new ID to hide ambiguity. |
| Old history missing | Use older inbox/receipt pages. A current-page cache is intentionally bounded. Content may also be expired, dismissed, erased or source-revoked. |
| Capacity error | Review retained-history bounds. No automatic pruning is enabled; do not delete database rows manually to bypass receipts. |
| Worker error / busy | Admin fixed error metadata distinguishes loop/storage failure. Resolve DB readiness/host resource pressure, then inspect durable lease/receipts. Do not enable extra workers. |

## 9. Reproduce isolated validation

Use a **dedicated disposable** PostgreSQL database, never the application's `.env`
URL. The tests use temporary schemas; recovery tests also require matching client
tools. Substitute your explicit test URL/tool path without logging credentials:

```powershell
$env:ADA_TEST_DATABASE_URL='postgresql+psycopg://ada_validation@127.0.0.1:55421/ada_phase2_test'
$env:ADA_TEST_PG_BIN='C:/Program Files/PostgreSQL/18/bin'
./.venv/Scripts/python.exe -m pytest -q --tb=short
./.venv/Scripts/python.exe -m ruff check src tests migrations scripts
./.venv/Scripts/python.exe -m ruff format --check src tests migrations scripts
```

Android, from `apps/android`, with the pinned JDK/SDK:

```powershell
./gradlew.bat testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest assembleRelease
./gradlew.bat '-PadaValidationApplicationId=dev.ada.validation.phase27' assembleDebug assembleDebugAndroidTest
```

From the root, with only an emulator selected (replace its ID if needed):

```powershell
./.venv/Scripts/python.exe scripts/verify_scheduling_android.py --device emulator-5584
```

The guarded runner uses real authenticated HTTP, a fake provider, an explicitly
loaded test-only clock/tick fixture and a separate validation package. It tests
preview/confirmation, inbox publication, explicit empty-conversation opening,
then force-stop and exact acknowledgement recovery. It removes its APKs/reverse/
schema. The fixture route is absent from normal production startup. Rebuild
without the validation property afterward to restore normal APK output paths;
that does not install the normal app.

From `apps/admin-web`, with the same dedicated test environment:

```powershell
npm ci
npm run contracts:check
npm run typecheck
npm run lint
npm run test -- --run
npm run build
npm run test:e2e
```

Actual run counts, failures and corrected checks belong in STATUS/WORKLOG.
Physical S24FE/TalkBack/manual time/airplane-mode behavior, installed-host reboot/
sleep timing, representative owner usefulness, large-data recovery/RPO/RTO,
off-device recovery and a separately authorized 24-hour trial remain target gates.
Push/doze/provider/permission/lock-screen tests are unrun because that channel
is unavailable. No Phase 28 reflection, later integrations or deployment is included.
