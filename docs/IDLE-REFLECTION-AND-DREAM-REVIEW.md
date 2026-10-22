# Idle reflection and dream review

Phase28 adds optional local jobs and an owner review area called **While you were
away**. The initial job set is rule-based reports and catalogue question drafts.
Generated episode-summary support is implemented behind a separate disabled
gate. A short native cancellation probe is not an attestation of GPU cancellation
or summary usefulness. Global reflection and each owner's consent default off.

“Dreaming” means bounded jobs over selected material. It does not train model
weights, watch your screen, choose hidden truths, or save an archive of reasoning.

## Developer setup

1. Follow [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md) and the
   [private network](PRIVATE-NETWORK-CONNECTIVITY.md) setup for the existing API,
   authentication and verified HTTPS connection. Clients contact ADA only.
2. Stop the owned API before a schema upgrade. Confirm that your selected
   `ADA_DATABASE_URL` points to the database you intend to maintain. Review a
   verified encrypted backup and its current deletion ledger using the
   [security runbook](SECURITY-AND-OPERATIONS.md). This phase's implementation
   only migrated disposable test databases.
3. From the repository root, with the pinned virtual environment installed, run:

   ```powershell
   ./.venv/Scripts/python.exe -m alembic current
   ./.venv/Scripts/python.exe -m alembic upgrade head
   ./.venv/Scripts/python.exe -m alembic check
   ```

   Current source requires **0019 /70 tables**. New tables are
   `reflection_policies`, `reflection_runs`, `reflection_artifacts`,
   `reflection_receipts` and `reflection_provider_state`. The first four join
   the **57-table owner-content inventory**. The last contains only a provider
   fingerprint and safety status; owner erasure cannot reset a cancellation ban.
   Released migrations0001–0018 stay intact. Android journals and backups are
   encrypted; PostgreSQL rows inherit the existing host-volume/access controls.
4. Keep these entries off until you choose to activate the initial job set:

   ```dotenv
   ADA_REFLECTION_ENABLED=false
   ADA_REFLECTION_SUMMARY_ENABLED=false
   # Leave ADA_REFLECTION_MODEL_DIGEST unset for the initial job set.
   ```

5. To permit reports/questions in a later operator-controlled installation, set
   `ADA_REFLECTION_ENABLED=true`, `ADA_SCHEDULER_ENABLED=true` and
   `ADA_CONSOLIDATION_WORKER_ENABLED=true`. Keep `ADA_MAX_PARALLEL=1` and a single
   Uvicorn worker. Restart through the existing
   [host operations](ALWAYS-ON-OPERATIONS.md) procedure. Do not create another
   scheduler or GPU daemon. The existing host observer supplies fresh resource
   readings; an unsupported direct Uvicorn launch has unknown readings and skips
   reflection. No live installation, task changes or deployment were performed
   as part of this phase.
6. Build Android with its pinned Gradle wrapper. The source version is
   `0.28.0-reflection` (22), encrypted journal16. Old journal versions1–15 remain
   readable. Build the admin SPA with `npm ci` and `npm run build` using its
   pinned Node/npm versions. Updating the normal device or private proxy is a
   separate operator action.

## Owner setup and review

1. Sign into Android, then open **Settings → Reminders & inbox**. Enable its
   separate automation consent if you want background work. That consent alone
   does not enable reflection or reauthorize old jobs.
2. Open **Settings → While you were away**, or the chat's expandable menu.
   Expand **Consent and input policy**.
3. Choose up to four owned scopes. Start with **My explicit notes**. Imported
   documents retain imported/untrusted provenance. Selecting completed messages
   requires both their source-type checkbox and the separate automatic-completed-
   turns consent. Only fully completed requests qualify; model replies remain
   unendorsed material.
4. Select a lookback of1–30 days, an IANA timezone such as `America/Phoenix`, and
   an increasing same-day time window. The editor uses minutes from midnight:
   `0` =00:00, `60` =01:00, `1380` =23:00, `1440` =24:00. End is exclusive.
   For a window spanning midnight, choose one side of midnight in this v1.
   Allowed hours remain in that timezone when you travel. Job/time caps use UTC
   days; changing timezone does not reset them.
5. Choose reports, optional questions, or both. Questions also require existing
   **Questions & curiosity** topic/depth/inbox consent. Personal topics remain
   subject to those settings. Summaries stay unavailable until their own
   provider safety and usefulness gates pass.
6. Set resource/time bounds. Defaults require15 minutes without authenticated ADA
   foreground activity, AC power, at least1 GiB free disk,10% available memory and
   measured temperature below80°C. The current Windows observer uses available
   GPU temperature; it is not proof of every component's thermal state. Unknown,
   stale, nonfinite or unsafe readings skip work. Defaults reserve20 seconds per
   attempt, at most3 jobs and600 seconds per UTC day. Hard limits cannot be raised
   through the API. You may lower them; a unit must fit inside the nightly budget.
7. Choose whether an empty selection may do nothing, enable the consent toggle
   and press **Save reflection choices**. There is no owner “run now” or automatic
   memory-acceptance button. Leaving ADA unused and eligible lets the existing
   dispatcher/worker consider a bounded unit. Restart waits for inactivity again.
8. Return to **While you were away** and refresh. Each draft shows its scope,
   completion time, wall duration, fixed rationale, exact original quotes/trust,
   version references and selection omissions. Expand original sources to inspect
   them; source conversations can be opened. Existing memory proposals still use
   their separate explicit review area. Runs show skipped/cancelled/failed
   decisions. An empty report explicitly says no useful findings.
9. **Keep report** retains that report. **Keep as generated episode** reuses the
   Phase13 generated-navigation contract when that class is available. It never
   creates an endorsed claim. **Open question to answer** explicitly creates or
   resumes an owned conversation; it inserts no user message and performs no
   inference. You answer normally. **Discard** hides the draft's payload while
   leaving original evidence. Use the separate explicit deletion flow to erase
   private content.
10. **Stop idle reflection** disables owner policy and suppresses queued/current
    publication. Revoking the originating device, resetting a password, stopping
    all password sessions, withdrawing automation consent or changing the data
    epoch also suppresses authority. Turning something back on does not resurrect
    suppressed units. Ordinary session renewal/logout is distinct from those
    durable revocations, as in Phase27.

## What the jobs actually do

- **Reports:** inspect bounded selected material for explicit owner-authored
  `TODO:`, `OPEN:` and `DONE:` lines. They do not infer completion outside those
  sources. A bounded comparison of endorsed same-subject/predicate statements can
  flag differing values with overlapping recorded validity as a **possible change
  or disagreement**. It neither chooses truth nor changes a claim/source.
- **Questions:** prepare an existing Phase25 catalogue question with an original
  user-source pin when available. Owner-wide template metadata prevents repeats
  across scopes and survives discard without retaining the discarded text. A
  draft is not an offered question until the
  owner explicitly opens it. Opening rejects changed catalogue wording instead
  of substituting a different question. No unsolicited external message is sent.
- **Summaries:** use Phase13 schema/support validation and generated provenance.
  The separately digest-bound literal-loopback streaming adapter requests
  structured output with thinking/tools disabled. Source text is untrusted data.
  [Ollama chat documentation](https://docs.ollama.com/api/chat) and
  [streaming documentation](https://docs.ollama.com/capabilities/streaming)
  describe those request features; they do not guarantee cancellation latency.
  No production attestation/enabling workflow is supplied by this smaller initial
  job set. Do not manually edit safety rows to bypass its disabled state.

Each source set is at most4 complete sources/6000 UTF-8 bytes, selected from at
most100 metadata candidates. Oversized complete sources are omitted rather than
truncating their quotes. Owner/scope/version/hash/current import availability
checks happen before payload use and again before publication. A corrected,
expired or deleted source suppresses the job and withholds stale review content.
No model inference occurs in a database transaction. No job performs research,
an external action, automatic preference mutation or automatic factual acceptance.
Later memory-proposal automation is outside Phase28.

## Recovery, quotas and foreground priority

The existing dispatcher queues deterministic source-set/policy/kind UUIDs. The
existing consolidation worker consumes them when explicit work has priority.
Native owner/row locks fence leases and attempts. Retries reuse that run ID, are
limited to3 attempts, and expire after24 hours. Unknown output never receives a
fresh success-looking ID. A changed source set can create a different bounded job.

Reflection shares the foreground inference semaphore. Authenticated foreground
arrival stops dispatch and requests cooperative cancellation. Capacity remains
held until the provider actually returns. Ignoring the2-second cancellation
budget suspends that provider class; a second inference is never admitted merely
because the user requested priority. This can temporarily return busy to chat.
The initial rule-only job set avoids background GPU inference altogether.

There are at most100 retained reflection runs per owner. New reflection dispatch
also defers when existing reflection and explicit consolidation total100 jobs in
a scope; explicit consolidation retains its existing separate quota. Receipts
cap at5000, reserving the
last slot for owner-off. Capacity decisions remain visible. There is no age-based
erasure or automatic archive invented to make room. Discard does not bypass the
retained-history limit.

Android saves each exact mutation before HTTP in a server/owner/epoch-bound
Keystore journal, with8 operations and one slot reserved for off. On restart,
**Check saved result** performs GET only. **Retry original change** explicitly
reuses the saved operation ID/body. Reconnecting never automatically POSTs an
unknown mutation. Late responses cannot repopulate a different identity/page.

Backup format **ada-postgres-backup-v5** covers0019; formatsv1–v4 remain readable
at their original schema heads. Restore verifies original hashes before pausing
reflection policies, quarantining queued/running work and clearing provider
attestation. Current credentials are also quarantined. Review content remains
owner data, and the separately supplied latest deletion ledger still applies.
Downgrade refuses retained reflection/safety history before any DDL. A running
reflection publisher also blocks a deletion preview/confirmation through the
existing quiescence guard; withdrawal and epoch fences still reject late output.

## Monitoring and troubleshooting

The admin **Reflection** page uses the existing current server grant/audit checks.
It projects only global status, provider suspension, enabled-policy count, fixed
run/artifact state counts and hard budgets. It contains no private report, topic,
source, scope selection or question. Admin permission never grants owner review.

| Visible condition | Check |
|---|---|
| Server globally stopped | All three global worker switches and supported supervised host readings; owner review can still work. |
| Automation consent missing/changed | Review Reminders & inbox and explicitly save fresh reflection consent. |
| Foreground active | Leave ADA unused for the selected idle interval; polling does not imitate user activity. |
| Outside allowed hours | Check selected IANA zone and minute values; endpoints are half-open. |
| AC/resource state unknown | Inspect existing host health. Do not replace unknown values with invented safe readings. |
| Source changed/unavailable | Inspect current source/version/availability. A new selection is separate from an old receipt. |
| Summary class disabled/suspended | Leave summary generation off. Native return timing alone is insufficient proof. |
| Retained job/receipt limit | Stop or inspect existing history; use explicit erasure only when deletion is intended. |
| Unconfirmed Android change | Check its saved result; explicitly retry only its original operation. |
| Nothing produced | Inspect runs/omissions. Empty inputs, no catalogue choice or no useful finding are valid outcomes. |

## Verification boundary

Actual checks, dated failures/corrections and remaining target gates are in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md). Synthetic fixture
resource values and fake providers are distinct from native hardware/model
evidence. A small public corpus measures narrow report acceptance and duplicate
questions; it does not establish broad personal-memory accuracy. Native GPU time
is unknown. Physical-phone/TalkBack, installed-host overnight/resource behavior,
representative private-data quality and long-running native cancellation/GPU
interference remain target work. These limits keep model summaries disabled.
