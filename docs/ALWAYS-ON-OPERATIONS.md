# Windows always-on operations and recovery

Phase26 supplies source and isolated rehearsals for an **owner-logon** setup on
the existing plugged-in laptop. It does not install production tasks, start the
application database, migrate it, change power policy or publish a service.
Actual checks and remaining gates are in [STATUS](../plans/STATUS.md). Sleeping,
hibernating, powered-off and logged-out hosts do not provide this availability.

## What runs and what stays separate

The selected mechanism is native **Task Scheduler2.0**, InteractiveToken,
LeastPrivilege, with the existing pinned Python3.12 environment. No downloaded
service wrapper, Windows account password, S4U fallback or pre-logon service is
introduced. Windows PowerShell5.1 is used for native ACL/scheduler commands;
PowerShell7 can launch those commands. The optional Caddy binary remains pinned
to2.11.7 and its SHA256 in `ops/validation-tools.json`. No dependency was upgraded.

The logon supervisor owns one single-worker API. The API takes a kernel file
lock and a database advisory lock before recovering abandoned requests. It never
holds a database transaction during inference. The supported foreground
`scripts/start.ps1` entry takes the same ownership gate. Do not run a parallel
direct `uvicorn` command or a second checkout against this installation.

An optional, checksum-verified Caddy child serves the existing admin build and
proxies API traffic on loopback. It reuses the Phase21 template, with its admin
interface disabled. Tailscale Serve remains responsible for HTTPS; ADA does not
enroll a VPN, enable Funnel or change a firewall. An occupied API/proxy port is
an operator action, not permission to adopt or kill another process.

External Ollama and PostgreSQL/Docker are **dependencies**, not processes ADA may
restart. Docker Desktop and a Desktop-hosted database normally require the owner
to log in and Docker to become ready. Select Docker Desktop's startup option
yourself if wanted. A boot trigger cannot remove that dependency. Native
PostgreSQL18.6 was used as an isolated measured alternative; your Docker database
was not replaced. Pre-logon service identity/GPU/model access remains a separate
target rehearsal, not a supported promise here.

## 1. Check the intended installation

1. Open PowerShell in this repository. Preserve local changes and the private
   `.env`; do not copy its contents into a plan, ticket or terminal transcript.
2. Use the existing environment and lockfile:

   ```powershell
   ./.venv/Scripts/python.exe --version
   ./.venv/Scripts/python.exe -m pip check
   ```

3. Make the selected database available using your normal installation procedure.
   With the existing Docker setup, that normally means opening Docker Desktop,
   waiting for its engine, then explicitly running:

   ```powershell
   docker compose up -d --wait db
   ./.venv/Scripts/ada.exe doctor
   ```

   Current Phase27 source requires schema **0018**; see
   [the scheduling upgrade guide](DURABLE-SCHEDULING-AND-REMINDERS.md).
   The supervisor never migrates a database.
   If doctor reports an older schema, follow the reviewed backup/upgrade procedure
   in [RELEASE-READINESS](RELEASE-READINESS.md) for that schema. Upgrade the intended
   installation only as a separately selected installation action.
4. Check Ollama without sending private content or loading another model:

   ```powershell
   ollama list
   ollama ps
   ```

   Its selected model must match the protected `.env`. Installed model metadata
   does not prove the model is loaded, fast or producing good answers.
5. Find Windows `pg_dump.exe` and `pg_restore.exe` matching the **server major**.
   The tools refuse a mismatch. For example, a Docker PostgreSQL17 database needs
   PostgreSQL17 client tools; the PostgreSQL18 tools used in validation are not a
   substitute. Review [database administration](DATABASE-ADMINISTRATION-WINDOWS.md).
6. Stop the previous manually started API before switching startup mechanisms.
   Resolve pending work consciously. Never terminate a process merely because
   it is named Python, Ollama or Docker.

## 2. Create protected local configuration

Use the actual matching client-tool folder in place of the example:

```powershell
./.venv/Scripts/python.exe -m ada.host_ops init `
  --repository (Get-Location).Path `
  --pg-bin 'C:/Program Files/PostgreSQL/17/bin'
$adaConfig = "$env:LOCALAPPDATA/ADA/operations/host.json"
./.venv/Scripts/python.exe -m ada.host_ops check-config --config $adaConfig
```

This creates owner/SYSTEM-only protected configuration under the current profile.
It refuses another SID/profile, redirected paths and unknown configuration
fields. Paths in configuration and manifests use forward slashes. It contains
no password/token/backup passphrase. Database/provider settings still come from
the private `.env`; do not copy them into the host file.

Defaults are API8000,30-second observation, daily backup03:00 local system time,
26-hour freshness alert,30-second graceful shutdown and **no backup pruning**.
Inspect/change the literal JSON before planning tasks. Unknown keys fail closed;
`prune_backups=true` is rejected. The selected destination is always the enrolled
owner's `%LOCALAPPDATA%/ADA/backups`, never a service account's accidental profile.

For private HTTPS/admin availability, first complete the separately selected
[Tailscale setup](PRIVATE-SETUP-WINDOWS-TAILSCALE.md), pinned Caddy installation and
admin build. Then set `tailnet_proxy` to `true`; `proxy_port` defaults to18764.
The supervisor renders only reviewed loopback port substitutions. The literal
absolute `ADA_ADMIN_DIST` must resolve to the built `index.html`. Keep proxy mode
off if you deliberately manage that process separately. This checkout does not
alter the existing Serve configuration or install the proxy.

## 3. Enroll the unattended key and independent recovery copy

Choose a location for an **encrypted recovery capsule** and keep a separately
recoverable copy away from this laptop. The example requires your chosen removable
drive to exist; no upload or drive is selected automatically:

```powershell
./.venv/Scripts/python.exe -m ada.host_ops enroll-key --config $adaConfig `
  --recovery-key 'E:/ADA-recovery/host-key.adaenc'
./.venv/Scripts/python.exe -m ada.host_ops check-key --config $adaConfig
```

Enter a distinct wrapping passphrase of at least16 characters twice in the hidden
prompts. Store it in your password manager. Do not put it in `.env`, scripts,
task arguments, logs or beside the artifact as plaintext.

ADA generates a random backup secret. Windows **current-user DPAPI**, with UI
forbidden and without machine-wide protection, protects the operational copy.
The portable capsule separately encrypts that secret using the existing
AES256-GCM/scrypt artifact scheme and your wrapping passphrase. It can recover the
backup secret after losing the Windows profile; copying the DPAPI blob alone is
not that independent recovery path. The secret is never printed. A new key cannot
silently overwrite an existing one. Preserve older capsules for older backups.

No task, live backup or power policy is enabled by enrollment. The ordinary
Phase18 interactive recovery commands remain compatible with their original keys.

## 4. Rehearse backup, integrity and restore before scheduling

```powershell
./.venv/Scripts/python.exe -m ada.host_ops backup --config $adaConfig
./.venv/Scripts/python.exe -m ada.host_ops verify-backup --config $adaConfig
./.venv/Scripts/python.exe -m ada.host_ops health --config $adaConfig
```

The backup command takes a singleton lease, checks AC/disk/memory/thermal pressure,
uses the existing consistent PostgreSQL exported snapshot and encrypted archive,
then exports an independent **post-snapshot, repeatable-read deletion ledger**.
Both artifacts are decrypted/read back and their inventory/hash/time checked
before `backup-latest.json` advances. Partial/corrupt files, key failure, disk full,
stale ledger or failed tools never publish a new verified point. A failed attempt
keeps the last good receipt and artifacts. Nothing is pruned.

The supervisor also refreshes a separate encrypted current ledger approximately
once per minute while it is running and the key/database are available. That is
privacy recovery metadata, not model work. Its failure is visible separately.
Backups are limited to256MiB; current snapshot queries have a30-second statement
timeout, and PostgreSQL tools have bounded execution. Scheduled backup execution
is limited to15minutes. A stopped attempt remains unverified.

Integrity verification is **not** a restore drill. Obtain the exact encrypted
artifact and sufficiently current ledger filenames from the protected receipt,
then explicitly restore to a fresh isolated name:

```powershell
./.venv/Scripts/python.exe -m ada.host_ops restore --config $adaConfig `
  --database ada_restore_drill_20261019 `
  --artifact '<absolute path to the selected .adaenc backup>' `
  --deletion-ledger '<absolute path to the latest verified ledger .adaenc>'
```

The target must be a **new `ada_restore_*` database** and cannot be the configured
database. Verify counts/hashes and application behavior in isolation. Credentials
are quarantined: legacy digests replaced, devices/sessions revoked, password
verifiers disabled, and restored curiosity off. Restore does not re-enroll an
owner, grant an admin role or resume scheduling authority. Failed restore targets
stay isolated; do not point an API at them. Use the existing recovery tests and
database guide for cleanup and controlled recovery.

The protected restore interface accesses the DPAPI key internally. After losing
a Windows profile, create fresh protected configuration under the new selected
identity, then use the hidden prompt to recover the capsule first:

```powershell
./.venv/Scripts/python.exe -m ada.host_ops recover-key --config $adaConfig `
  --recovery-key 'E:/ADA-recovery/host-key.adaenc'
```

Do not confuse the wrapping passphrase with the generated backup secret. Do not
print/decrypt the latter manually to feed it through a shell.

**Erasure safety:** a ledger must be at least as new as the snapshot, within the
configured freshness bound, and include the latest known completed erasures.
The minute refresh is a bounded recovery window, not zero-loss erasure replication.
If you cannot establish freshness after a disaster, keep restored credentials
quarantined and do not restore owner access to possibly erased content. Obtain a
current ledger from the source when available. Same-disk artifacts/ledger/key do
not survive laptop loss. Choose off-device encrypted copies separately.

## 5. Review power settings explicitly

ADA does not silently change sleep, lid, login, firewall or Wake-on-LAN policy.
For a separately chosen AC-awake setup, capture originals first:

```powershell
$adaPower = "$env:LOCALAPPDATA/ADA/operations/power-original.json"
powershell.exe -NoProfile -File ./scripts/host-power.ps1 `
  -Action Snapshot -Snapshot $adaPower -IncludeLid
powershell.exe -NoProfile -File ./scripts/host-power.ps1 `
  -Action ApplyAcAwake -Snapshot $adaPower -IncludeLid -WhatIf
```

After reviewing the snapshot and choosing this policy, rerun the second command
without `-WhatIf`. It changes only the active scheme's AC sleep/hibernate timeout
and, when explicitly included, lid action. Display timeout and battery/DC settings
stay unchanged. Firmware/thermal/enterprise policy can still make the host sleep.

Restore the captured AC originals with `-Action Restore -Snapshot $adaPower`.
The tool refuses another active scheme or independent changes it would overwrite.
It does not overwrite an existing snapshot. A disconnected phone never indicates
host/owner idleness. Actual sleep/resume must be rehearsed separately.

## 6. Plan, then independently install the selected tasks

Default mode creates reviewable XML only:

```powershell
powershell.exe -NoProfile -File ./scripts/install-host-operations.ps1 -Config $adaConfig
```

Review `Supervisor.task.xml` and `Backup.task.xml` in the protected directory.
They use the exact selected SID, InteractiveToken, LeastPrivilege, `pythonw.exe`,
an explicit working directory, IgnoreNew and no WakeToRun/boot trigger. No secret
is in their arguments. Two bounded OS restarts recover a supervisor failure;
the API's own crash-loop stop persists across launches until operator reset.

Only after selecting the installation, startup dependencies and measured RPO/RTO:

```powershell
powershell.exe -NoProfile -File ./scripts/install-host-operations.ps1 `
  -Config $adaConfig -Mode Install
```

This registers the logon supervisor and daily backup; it does not start them
immediately. Use the exact Supervisor task name printed by Plan/Install with
`Start-ScheduledTask -TaskName '<exact name>'`, or log on during the separate
target test. Existing names are not silently replaced. Do not create a second
backup scheduler; Phase27 must reuse or replace this narrow trigger.

Inspect state without opening a terminal that has to remain running:

```powershell
./.venv/Scripts/python.exe -m ada.host_ops health --config $adaConfig
Invoke-RestMethod http://127.0.0.1:8000/health/live
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

The public API endpoints preserve their contracts: liveness is process HTTP;
readiness is database/schema readiness. Local host health separately reports
provider installed/loaded metadata, backup age/latest attempt/ledger state and
actual host sensors. Unknown sensors are null. NVIDIA counters are host counters,
not proof of ADA-specific consumption. No health probe generates a prompt or
loads/unloads a model. A live but unresponsive API or missing model is not a reason
to kill an external provider. Database startup retries/backoff and API child
restarts stop at finite budgets. Jobs retain their original leases/fences; no
private POST or completed reply is automatically replayed.

Discretionary consolidation is deferred on battery/unknown AC, under1GiB free
disk, under10% available RAM or NVIDIA temperature at/above85C. Missing thermal/
GPU counters remain unknown; backup is not presented as a thermal certification.
The supervised worker also waits for a quiet interval after server-observed chat
traffic and never occupies capacity for an empty poll. Foreground chat keeps the
shared admission budget; an already-running job is not preempted. Explicit erasure
recovery metadata is not discretionary model work. No dreaming is implemented.

## 7. Stop, diagnose and roll back

```powershell
./.venv/Scripts/python.exe -m ada.host_ops stop --config $adaConfig
```

Wait for `supervisor.json` to say `stopped`. The API drains first. Only owned
children may then be stopped; an admin-disabled owned proxy is terminated after
the API's grace period. A Windows Job Object also contains only assigned children
so supervisor death cannot orphan them. External Ollama, Docker, PostgreSQL and
user-started proxies are never assigned or killed.

| State/code | Action |
| --- | --- |
| `schema_upgrade_required` | Review/migrate the selected database separately; never edit its version row to bypass readiness. |
| `database_startup_budget_exhausted` | Check Docker Desktop/login dependency or the selected PostgreSQL service and `.env`; restart deliberately after it is ready. |
| Provider unreachable/model unavailable | Check the existing provider/model; API metadata can remain reachable. No automatic provider restart or substitute model. |
| `api_port_owned_elsewhere` / proxy equivalent | Identify the old installation and stop it through its own controls. Do not kill processes by name. |
| `api_crash_loop_stopped` | Review fixed receipts/configuration. After fixing the cause, `reset-crash-stop` permits a deliberate new start. |
| Backup missing/stale/failed/deferred | Inspect the separate last verified point and latest attempt; fix key/resource/tool issues and run a conscious retry. |
| `backup_key_unavailable` / protected directory failure | Use the enrolled Windows identity/profile and restrictive ACL; independently recover the capsule when necessary. |
| Integrity/stale-ledger failure | Keep all targets isolated; select authenticated artifacts and a sufficiently current ledger, then repeat the drill. |

After cooperative stop, remove only the exact planned tasks:

```powershell
powershell.exe -NoProfile -File ./scripts/install-host-operations.ps1 `
  -Config $adaConfig -Mode Remove
```

Preserve configuration, encrypted artifacts and recovery capsule. Restore power
originals separately if you changed them. Ordinary foreground startup remains
available through `scripts/start.ps1`. No automatic source retention/pruning or
backup cleanup policy is introduced.

## Capacity, growth and release gates

The latest public native rehearsal used the configured
`qwen3.8-27b-uncensored` model, 16,384 context tokens and 1,024 output tokens.
It observed a first reply of 17.718 seconds with no model resident beforehand,
then a mean of 3.859 seconds and maximum of 3.953 seconds across two warm replies.
Eight concurrent requests returned one HTTP 200 and seven HTTP 503 responses
under the single-slot admission limit. Its encrypted fixture backup was
201,811 bytes in 0.640 seconds; the protected-key CLI restored an isolated,
credential-quarantined database in 3.328 seconds. These small public-fixture
figures are not an RPO/RTO agreement or a quality benchmark for private work.

The latest short fake-provider rehearsal ran for 60.64 seconds, with 60 health
samples, no unavailable sample and six public replies (mean 0.070 seconds,
maximum 0.109 seconds). It also verified the owned pinned proxy, temporary
Task Scheduler key access, child-crash recovery, exact completed replay, backup,
CLI restore and cooperative stop. Earlier measurements remain in STATUS and
WORKLOG. Short native/fake runs do not establish four-hour or 24-hour uptime.
The authorized four-hour fake-provider attempt stopped early with ConnectError
after about3h15 wall time; it did not reach its final backup/restore. Its original
harness did not retain timed-loop totals. A controlled
reader test independently reproduced a Windows receipt-sharing failure; bounded
publication retries and richer safe failure diagnostics now address that path.
The original long attempt's exact cause is not recoverable from its saved record.
After correction, the authorized continuous rerun passed 14,400.39 seconds on
2026-10-19 (08:03–12:04 Phoenix, including startup and final recovery). It used
the explicit fake provider, synthetic accounts, native PostgreSQL, an owned
pinned proxy and a temporary same-user Task Scheduler key check. All 14,278
timed health samples were ready; 1,428 public replies averaged 0.0375 seconds
(maximum 0.188 seconds). The eight-request admission check returned two HTTP 200
and six HTTP 503 responses. Duplicate refusal, deliberate API crash recovery,
exact completed replay and injected receipt-reader contention passed. The final
682,629-byte encrypted backup took 0.984 seconds; protected-key CLI restore into
an isolated database took 9.985 seconds and quarantined credentials. Cooperative
shutdown, task/database/listener cleanup and unchanged power settings were
verified. This closes the four-hour development gate; it does not measure four
hours of native-model inference or installed production uptime.

Use `scripts/verify_host_operations.py` with a dedicated
`ADA_TEST_DATABASE_URL`/matching `ADA_TEST_PG_BIN`. Default duration is four hours;
`--seconds` reports the actual shorter development sample. `--task-scheduler`
adds a temporary demand-start key-access task, removed afterward. `--with-proxy`
copies only the already installed pinned binary into the fixture profile and
tests an owned loopback route. `--native-model` refuses the ordinary API/proxy
ports or a different resident model and uses only public authenticated tasks.
No normal application account/database is used. The24-hour target trial needs a
separately selected test window and installed configuration.

`--reader-contention` deliberately holds the public supervisor receipt briefly
to verify native Windows publication recovery. Transient sharing collisions retry
for up to3seconds; persistent failure preserves the old complete receipt and
fails visibly. Failure reports retain stage, elapsed counters, supervisor error
types and owned child exit codes without raw private payloads/exception strings.
The earlier corrected 60.47-second fault rehearsal passed 60 health checks with
zero unavailable samples, backup/isolated restore and cooperative stop. Preserve
it as short fault-path evidence alongside the separate completed four-hour run.

Before live use, select acceptable data loss and measure representative backup/
restore size/time. Daily backup and26-hour alert are proposals. Forecast growth
against256MiB: current retained quotas include100 consolidation jobs and100
episode contexts per owner/scope,100 extraction runs and400 proposals per scope.
Those counts are not byte limits; chats, imported documents and history also
consume space. Do not raise limits, prune content or add a second model daemon to
hide growth. Establish foreground latency/thermal budgets from sustained actual
work; the current85C/1GiB/10% guard thresholds are conservative initial controls,
not measured safe limits for every host.

Use the size of the **encrypted full snapshot**, rather than row count alone,
for a growth forecast. For illustration, starting at 10 MiB with a 256 MiB cap:

| Assumed snapshot growth | Approximate time until the cap |
| --- | --- |
| 1 MiB/day | 246 days |
| 5 MiB/day | 49 days |
| 10 MiB/day | 24 days |

These are arithmetic scenarios, not measurements of your data or a reason to
wait until the last day. Recalculate from actual verified snapshots and leave
headroom for a single large import. The retained-job/proposal quotas above do not
bound the rest of the database. With pruning off, 30 daily full backups averaging
50 MiB also consume about 1.46 GiB on disk, plus separate ledgers and recovery
metadata, even if the live database stops growing. Measure source growth and
artifact accumulation separately. Raising the archive cap or choosing retention
requires a reviewed operational change and another representative restore drill.

Still required before unattended-production claims: actual reboot/logon and
Docker Desktop startup order, real sleep/resume and lid behavior, representative
large backup cost/RPO/RTO, sustained native workload budgets,
a separately selected 24-hour trial and
off-device disaster recovery. No uptime SLA or Wake-on-LAN is claimed. Android/
iOS/device and later scheduler/dreaming phases remain separate.

## Primary platform references

- [Task Scheduler2.0](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
  and [task principals](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtaskprincipal?view=windowsserver2025-ps).
- [Current-user DPAPI](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata)
  and [authenticated unprotection](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptunprotectdata).
- [Owned process Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
- [Generation-free Ollama residency metadata](https://docs.ollama.com/api/ps).
