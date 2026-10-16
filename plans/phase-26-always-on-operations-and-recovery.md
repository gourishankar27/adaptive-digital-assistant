# Phase 26 — always-on operations and unattended recovery

Status: **Proposed; planning only.** Inputs: 20 safe upgrade/recovery, 18 operational
bounds, G-08/G-09/G-34/G-35.21 is needed for remote reachability. Follow
[shared rules](FUTURE-ROADMAP.md). Confirmed target: existing Windows laptop
plugged in and awake. This cannot provide availability while powered off/asleep.

## Outcome

ADA starts predictably, recovers after failure and protects its data without a
terminal left open. Show actual API/provider/database/backup health. Foreground
chat remains the priority; no background dreaming is required for basic uptime.

## Checkpoints

- **A — supervisor.** Select and pin a supported Windows startup mechanism after
  rehearsing the real provider/DB startup path. Prefer native Task Scheduler for
  an initial owner-logon startup/restart setup; if pre-logon availability is
  required, separately test a least-privilege service identity and provider GPU/
  model access. Docker Desktop login dependencies must be recorded; a boot trigger
  alone cannot make a login-dependent PostgreSQL container ready. Document native
  PostgreSQL/service or other measured alternative, rather than silently replacing
  the user's installation. Ensure only one API/inference admission owner runs.
- **B — health and recovery.** Check DB head/readiness and provider reachability,
  with bounded retry/backoff and crash-loop stop. Distinguish process liveness,
  API readiness and slow/model-unavailable states. Health probes never generate
  private prompts or accidentally load a second model. Stop/restart gracefully;
  reconcile durable jobs/requests with existing leases. Avoid killing user tools
  or restarting an external Ollama process owned by something else.
- **C — host availability controls.** Document explicit opt-in AC awake/lid/power
  settings, recorded originals and reversible setup. Do not silently change sleep,
  firewall, login or power policy. Detect battery/thermal/disk pressure and suspend
  discretionary work; report unavailable sensors as unknown. A disconnected phone
  is not evidence that the laptop or owner is idle. No Wake-on-LAN or uptime SLA
  is promised. Later dedicated-host migration is a measured option, not a purchase.
- **D — unattended backup.** ExtendPhase 18's interactive `getpass` path with a protected
  secret-provider interface scoped to the service/logon identity. Do not put a
  passphrase in scripts, scheduler arguments, env dumps or next to the artifact
  as plaintext. Rehearse Windows user/service credential access and independent
  disaster recovery for its wrapping key. Backups stay encrypted in
  `%LOCALAPPDATA%/ADA/backups` for the selected owner, not accidentally another
  service profile. Pair a consistent snapshot with a sufficiently current erasure
  ledger, verify integrity before marking success and perform isolated restore drills.
- **E — scheduling and operations.** An OS scheduled task may initially run the
  narrowly scoped backup command with a singleton lease/receipt.27 later reuses
  or replaces its trigger, never runs a duplicate scheduler. Propose daily backups
  and a26h freshness alert; agree RPO/RTO from data size before live use. Keep
  backup pruning off until the owner selects a policy; never prune before a newer
  verified recovery point, and never change source retain-until-deletion policy.
  Same-disk backups do not protect against laptop loss. Off-device copies need
  a separately chosen encrypted destination, not an automatic cloud upload.
- **F — capacity and soak.** Measure model cold/warm readiness, inference latency,
  queue rejection, memory/VRAM, disk and backup cost with public/synthetic tasks.
  Run a four-hour development soak then a24h trial if authorized. Report unknown
  GPU counters honestly. Set foreground-latency/thermal budgets from measurements;
  include retained-job/proposal quotas and the 256 MiB backup cap in growth forecasts.
  Keep one worker and no separate GPU daemon. Multiworker design is deferred.

## Data/interfaces, failures and exit

Use fixed health metadata, supervisor/backup receipts and protected local config;
no raw chat/URL/secret logs. Any new durable operation tables join the inventory,
backup version and privacy policy. Test reboot/logon readiness, duplicate start,
provider/DB down, wrong schema, crash loop, laptop sleep/resume, unavailable key,
disk full, corrupt archive, stale ledger and failed restore. Failure must never
look like a verified backup. Restore must quarantine all current credential types.
Run relevant PostgreSQL and Windows script validation; do not claim a real reboot/
soak from unit mocks. Installation/system-policy changes require selected scope.

Exit with a reproducible supervised setup and rehearsed recovery, measured uptime
limits and actionable health states. Dreaming28 remains off/unimplemented here.
Primary Windows reference: [Task Scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page).
