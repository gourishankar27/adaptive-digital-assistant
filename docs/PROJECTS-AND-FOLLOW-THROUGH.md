# Projects and personal follow-through (Phase 30)

Source implementation, 2026-10-22 America/Phoenix. This phase supports a balanced
brief of personal commitments and development projects, as requested by the owner.
It does not execute tasks or infer that a suggestion is an agreed commitment.

## Before using it

The source requires migration **0020**, following released 0019. It adds
`work_items`, `work_revisions`, `work_receipts` and `work_briefs`: 74 total tables,
61 in the owner-content inventory. Android is **24 / 0.30.0-work**, with encrypted
journal **17** and reads of versions 1–16. Dependencies and wrappers are unchanged.
The server advertises `work_protocol: ada-work-v1`; older servers leave the
Android feature unavailable. The admin dashboard has no private work reader.

Implementation/testing did not migrate the installed database, update the normal
phone app or deploy the server. During a separately authorized installation:

1. Follow the existing [Windows setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md) and
   [database guide](DATABASE-ADMINISTRATION-WINDOWS.md). Keep database/provider ports private.
2. Stop the installed API and background workers cleanly. Use the established
   encrypted backup plus deletion-ledger procedure in
   [security and operations](SECURITY-AND-OPERATIONS.md).
3. From the repository root, in PowerShell, activate the existing environment
   (`.\.venv\Scripts\Activate.ps1`) and check `python -m alembic current`.
   Confirm it identifies the intended database before changing anything.
4. Run `python -m alembic upgrade head`, then `python -m alembic check`.
   Expected head is 0020. Do not use `create_all`, reset the database or edit
   released migrations. Downgrade refuses retained work/history.
5. Restart through the existing private host procedure with one Uvicorn worker.
   Build the Android app with the pinned wrapper and install through the normal
   developer workflow. Sign in using the existing private HTTPS origin.
6. Check the capability and try a synthetic task before entering real work.
   No new LLM setting, web permission or speech model is required.

These are installation instructions, not evidence that installation was performed.
For older backups, restore into an isolated database first: released head0019
backup-v5 remains readable and can then be upgraded to0020.

## Create a project and a next action

1. Open **Projects & next actions** from the chat menu or Settings.
2. Expand the scope/project section. Choose an existing personal/project scope,
   or enter a project name and select **Create project**. Project creation is an
   explicit authenticated write with its own reserved identifier.
3. Select the scope. Create a task or goal and enter a specific description.
   A goal is an optional same-scope parent; it does not grant access to anything.
4. Select a status: **planned**, **done**, **deferred**, **unknown**, or
   **dismissed**. Only your explicit revision changes that status. Passing a due
   date never completes work. Finishing a goal does not finish its children.
5. Optionally enter both a local due time (`YYYY-MM-DDTHH:mm`) and an IANA timezone
   such as `America/Phoenix`. Leave both blank for no due time. A skipped daylight
   saving time is rejected; for a repeated time choose **first** or **second**.
6. Optionally choose **Review a reminder after Save**. This only opens the separate
   reminder review after a confirmed Save; it creates no schedule by itself.
7. Select **Review exact Save**. Check the scope, description, status, due instant,
   reminder choice and any exact original excerpts. Then select **Confirm Save**.
   Editing any field invalidates the preview.
8. Use **Edit status or action** for a new reviewed revision. **Revision history**
   preserves earlier descriptions/statuses. Work edits conservatively pause the
   linked reminder and unresolved question, so their old wording cannot continue.

Scope selection currently shows the first 100 owned scopes. Work pages contain
50 items (up to 200 retained items per owner); revision pages contain 100 entries
(up to 2,000 total retained revisions). Parents are chosen from goals on the
current page. Quotas return a visible limit; there is no silent history pruning.

## Save a next action from chat

1. Open a completed ADA reply and select **Save next action**.
2. Write the next action yourself. The editor starts blank: the model's reply is
   not silently copied into a commitment.
3. Review the original generated excerpt, scope, description, status, optional
   time and reminder choice, then use the exact preview and confirmation above.
4. The source link pins the original reply version/hash and first up to400 Unicode
   code points. **Resume original conversation** opens that conversation.

Generated/imported text retains its original trust. Saving a task is not a factual
memory endorsement. No tool registry entry, extracted instruction or background
reflection can create this commitment. Existing completed answers, prompts,
citations and request replay remain immutable.

## Make a balanced project/day brief

1. Select **Include in project/day brief** on relevant personal and development
   tasks/goals. Selection can span at most30 items across4 owned scopes.
2. Expand **Balanced project/day brief**, enter the day and IANA timezone, then
   select **Generate selected-work brief**.
3. Inspect each task's status, overdue indicator, due-on-day grouping, changed
   field names and original source excerpts. **Unknown** items need a decision;
   nothing is marked done by the brief. Follow the original conversation link
   when more context is needed.

This is a deterministic projection of explicitly selected work, without an LLM
call or external access. `[T1]` labels navigate task records; they are not factual
citations. It reports changed fields since the previous revision, rather than
inventing a narrative of progress. The chosen day groups due dates; current status
and overdue are frozen at the snapshot time, not reconstructed for a past day.
Owner/scope/data-epoch/task-revision/timezone-rule and overdue-state cache keys
prevent reuse across those boundaries. Old snapshots retain their original status
and calendar flags. Original sources are reauthorized on every read; deleted,
changed, future or unavailable evidence is withheld visibly. A task can remain as
explicit owner work even after its origin becomes unavailable.

## Optional questions and reminders

**Prepare optional follow-up** uses existing Phase25 question consent, topic and
cadence controls. Choose work/routines and confirm the exact question. It creates
a Questions inbox draft with no fabricated user turn or new factual memory.
Disabled consent/cadence does not produce a successful question.

**Review a reminder** uses only Phase27 scheduling. Enter timezone, future local
start, expiry instant with offset and repeated-time choice. Preview the exact
schedule, enable separate Reminders consent if necessary, and explicitly confirm.
The reminder text is bound to the reviewed task description/revision. A generic
schedule confirmation cannot bypass that binding. Completion/dismissal and other
task edits pause related automation; rescheduling requires fresh review/consent.
Delivery remains the existing private foreground inbox, with no background push.
Server dispatch must separately be enabled under the Phase27 host policy.
An assistant saying “I'll remind you” does not schedule anything.

## Connection loss and recovery

Every confirmed write is encrypted locally before HTTP with the exact body,
operation ID, item ID and scope. There are at most four pending work operations;
an encrypted operation is bounded to24,000 UTF-8 bytes.

- Reopening/reconnecting checks the original receipt or brief using **GET**. It
  never automatically creates a task, project, question, reminder or brief.
- If no receipt exists, **Retry original change** resubmits the same identifier
  and body only after your action. Repeated delivery is idempotent.
- **Discard local recovery record** requires confirmation. It deletes only that
  local record; it does not delete anything already stored on the server.
- A409 means revision, source, preview or consent changed. Check the original
  result, then reopen current work and review a new edit. Do not change the body
  under a pending identifier. A422 requires correcting time/description/input.
- After401, sign in again; writes do not continue under a new account. Busy/rate
  responses apply bounded retry delays. A timeout or503 is an unconfirmed result,
  never proof that the work was not saved.
- Hidden/obsolete brief results are withheld and keep their recovery record.
  Explicit **Check saved result** can retrieve the original snapshot. Account,
  server, scope and lifecycle fences prevent a late response replacing new work.

Owner erasure includes all four new tables. Privacy-epoch changes invalidate old
work and briefs. Backup-v6 includes the new inventory; v1–v5 remain supported.
Restore preserves explicit work/history while quarantining credentials, question
and scheduling authority. It never silently resumes follow-ups.

## Developer verification

The endpoint map below uses UUID placeholders. Authentication and owner/scope
checks apply to every private operation; the caller never supplies an owner ID.

| Method/path | Purpose |
|---|---|
| POST `/v1/work/projects/{scope_id}` | Create a reserved project scope with an exact operation receipt |
| GET `/v1/scopes/{scope_id}/work` | Page current owned work (offset, 50 rows) |
| GET `/v1/work/{item_id}` and `/history` | Current work and immutable revision pages |
| POST `/v1/scopes/{scope_id}/work/{item_id}/preview` | Validate exact proposed fields and return a bound preview hash |
| POST `/v1/scopes/{scope_id}/work/{item_id}` | Confirm that reviewed proposal, with expected revision and reserved operation ID |
| GET `/v1/work/receipts/{operation_id}` | Resolve an original write outcome without resubmission |
| POST `/v1/work/briefs`; GET `/v1/work/briefs/{brief_id}` | Create a selected-work snapshot; recover by original operation ID or snapshot ID |
| POST `/v1/work/{item_id}/followup` | Explicit Phase25 question under current consent |
| POST `/v1/work/{item_id}/reminder-preview` and `/reminder-confirm` | Phase27 calendar preview and separately confirmed task binding |

History and receipts retain original meaning. Reusing an operation ID with a
different payload returns409. Duplicate exact confirmation returns the original
receipt. A preview has no commitment/scheduling side effect. Brief creation stores
only the selected revision snapshot, not another copy of private source quotes.

Use a disposable PostgreSQL database, never the installed private database.
The dated [status](../plans/STATUS.md) and [work log](../plans/WORKLOG.md) record
the actual runs, earlier failures and remaining target checks.

```powershell
$env:ADA_TEST_DATABASE_URL='postgresql+psycopg://ada_validation@127.0.0.1:55421/ada_phase2_test'
$env:ADA_TEST_PG_BIN='C:/Program Files/PostgreSQL/18/bin'
python -m pytest --assert=plain -q --tb=short tests/test_work.py tests/test_work_evaluation.py tests/test_work_failures.py tests/test_work_followup.py tests/test_work_storage.py
python -m ruff check src tests scripts
python scripts/export_openapi.py
Set-Location apps/android
./gradlew.bat --no-daemon :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:assembleRelease
./gradlew.bat --no-daemon '-PadaValidationApplicationId=dev.ada.validation.phase30' :app:assembleDebug :app:assembleDebugAndroidTest
Set-Location ../..
python scripts/verify_work_android.py --device emulator-5584
```

Use the actual owned emulator serial, not a connected personal device by default.
The runner checks the separate validation package, synthetic fixture, real HTTP,
encrypted journal and actual force-stop boundaries. It removes only its own
APKs/reverse mapping/disposable schema. Rebuild normal APK outputs afterward
without installing them. Native PostgreSQL tests cover schema upgrade/drift,
revision/idempotency concurrency, erasure and encrypted recovery. Held-out
synthetic workflows do not establish human acceptance or long-term usefulness.
Physical layout/TalkBack and real personal/project outcome evaluation remain
separate checks. No external task execution, shared projects or Phase31 work is
included.
