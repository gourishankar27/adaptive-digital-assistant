> Historical reference. For current setup use [HOW-TO-USE-ADA](../HOW-TO-USE-ADA.md).

# Release readiness and the quality baseline

Phase 20 adds operator/evaluation tooling without a new server API, migration,
prompt, authentication method or client capability. Current source head remains
**0015**. The historically observed application head0005 was not queried again
or upgraded during this phase. Read [STATUS](../../plans/STATUS.md) for actual results,
failures and skips; this guide is not authorization to operate on a live database.

## What changed

- `ada.legacy_recovery` protects a populated **0005** database before an upgrade.
  It writes a separately versioned encrypted artifact and restores only into a
  new isolated database with its old tokens invalidated.
- Current `ada.operations` remains the **0015** backup/restore interface, with
  an explicit schema inventory and matching PostgreSQL-major tool check. Valid
  Phase18 artifacts remain supported; unknown heads/tables do not become supported
  simply because a migration or model was added.
- `scripts/evaluate_quality.py` runs the five existing evaluation programs and a
  frozen held-out retrieval corpus, producing an aggregate scorecard. Fixtures,
  exact provenance and semantic answer quality are reported separately.
- `scripts/verify_private_proxy.py` validates the actual Caddy template and
  isolated CA-verified loopback routing. `/admin` now redirects to `/admin/`.
  This is a lab check, not VPN enrollment, system trust installation or deployment.

## Recovery formats and limits

| Tool | Accepted source/artifact | Restore and authority boundary |
|---|---|---|
| `python -m ada.legacy_recovery` | Schema0005; `ada-postgres-legacy-0005-v1`; `.legacy0005.adaenc` | New `ada_restore_legacy_*` target only; exact table/row hashes checked; all restored legacy token hashes replaced; no automatic upgrade or API start |
| `python -m ada.operations` | Schema0015; existing `ada-postgres-backup-v1` | New `ada_restore_*` target only; credential quarantine plus current post-backup erasure ledger reconciliation |

Both use the existing authenticated AES256-GCM/scrypt envelope, a hidden passphrase
prompt, bounded custom-format PostgreSQL dump and in-memory plaintext handling.
Only encrypted database artifacts reach disk.256MiB/artifact and five-minute
subprocess bounds remain; this is not a large-dataset streaming backup solution.
Tools conservatively require the same client/server PostgreSQL major. A mismatch
is refused before dumping/creating a restore target. PostgreSQL supports some
other combinations, but they have not been rehearsed by this tool policy.
See [the PostgreSQL reference](https://www.postgresql.org/docs/18/app-pgdump.html).

The source database is never rewritten by backup or restoration. Existing artifact
files and existing restore databases are never overwritten. Failed restores may
leave a task-owned isolated target for inspection; do not start an API against it.
Authenticated but inconsistent row inventories leave restored tokens quarantined.
A failed encrypted file write is a failure, not a successful backup receipt; an
incomplete file must never be selected as a recovery point.

### Supported inventory and future changes

`src/ada/recovery_policy.py` explicitly covers the frozen0005 inventory and current
0015 inventory; `src/ada/inventory.py` classifies owner-content versus minimal
security metadata. Unknown actual database tables or owner models fail closed.
Future migrations must explicitly add a reviewed format/head policy and tests;
do not merely replace the accepted head string or regenerate a list blindly.

Before accepting a future head, rehearse populated upgrade and old artifact recovery,
source/hash/citation/completed replay, erasure propagation and current authority
quarantine. Password sessions/refresh families and automation consent, if later
implemented, must also be disabled or reconciled after restore. Update client
epoch/cache cleanup and all new blob/job payload copies. Retain original artifact
readers; unsupported downgrade is not rollback. Immutable released migrations and
prompt history remain protected. Current table counts are not timeless constants.

## Pre-upgrade protection and isolated rehearsal

These are operator steps for a separately selected installation window. Commands
below were verified as existing CLI interfaces, not run against the live account.
Keep credentials/connection URLs out of logs, command history and plan text.

1. Identify the **actual** current schema/server major using the intended protected
   installation. Do not rely on old0005 records. Stop new writes for the final
   installation window and preserve protected configuration/key material separately.
2. Select the matching supported recovery path. For0005:

   ```powershell
   $adaPgBin = 'C:/Program Files/PostgreSQL/18/bin' # Match the actual server major.
   $adaBackups = Join-Path $env:LOCALAPPDATA 'ADA/backups'
   ./.venv/Scripts/python.exe -m ada.legacy_recovery --pg-bin $adaPgBin backup --destination $adaBackups
   ```

   Enter a strong password-manager passphrase at the hidden prompt. The receipt
   reports path/count/time, not a secret. For0015 use the existing
   [operations runbook](../SECURITY-AND-OPERATIONS.md). Other heads need their own
   validated path; never upgrade just to make the backup command accept them.
3. Copy the returned encrypted artifact path into a local variable and restore
   to a **new** isolated target, never the source or an existing database:

   ```powershell
   $adaArtifact = 'path/from/the/receipt.legacy0005.adaenc'
   $adaRestoreName = 'ada_restore_legacy_rehearsal_01'
   ./.venv/Scripts/python.exe -m ada.legacy_recovery --pg-bin $adaPgBin restore --database $adaRestoreName --artifact $adaArtifact
   ```

   This verifies original rows and invalidates restored tokens. It does not start
   the old application. Rehearsal in this repository used the released0005 schema
   and original stored history; no standalone source checkout with head0005 exists
   in the available Git history. Matching old-server HTTP is therefore **not** a
   claimed result. Current-server replay is tested after forward upgrade.
4. Point **only the rehearsal process** at the protected isolated connection URL.
   Keep the real `.env` unchanged. After reviewing that target, run:

   ```powershell
   ./.venv/Scripts/python.exe -m alembic upgrade head
   ./.venv/Scripts/python.exe -m alembic check
   ```

   These commands use `ADA_DATABASE_URL`; verify its target privately first.
   Never copy the live URL into a plan/log. The populated drill injects a failure
   during forward migration and verifies PostgreSQL rolls back to0005 before a
   successful retry. This is transactional failure injection, not a power-loss test.
5. Before serving a recovered legacy copy, reconcile erasures that happened after
   that old snapshot. If later0015 operation/deletion history exists, the legacy
   artifact alone is insufficient. Keep the copy isolated: upgrade it, create a
   current-format backup of that copy, obtain a fresh current deletion ledger from
   the authoritative installation, then use the current restore flow into another
   new isolated target. That flow quarantines credentials and applies later erasure.
   A missing/stale ledger or unknown history is a recovery blocker, not permission
   to resurrect content. Do not invent empty erasure history. Independent legacy
   and current-ledger drills are evidence of their own tested boundaries.
6. Review restored sources/hashes, original citations/replay, counts, grants,
   jobs and erasure receipts. Provision fresh access through separately selected
   local operator recovery; restored credentials are intentionally unusable.
   Never use a successful restore receipt as automatic permission to start service.

## Concrete intended-installation checklist

No item here was performed on the live installation during Phase20.

- Select the installation window and verify the exact database, schema, binaries,
  code/config versions and independent access/recovery material privately.
- Produce an encrypted pre-upgrade recovery point with the applicable supported
  tool; authenticate/read it and rehearse a new-database restore before changes.
- Save key/config material independently; retain the original artifact. Agree
  acceptable loss, downtime and rollback target from actual data-size measurements.
- Rehearse populated upgrade, schema drift, original replay and erasure/authority
  handling. A newer populated schema must not be downgraded past a lossy guard.
- Stop new writes, take the final recovery point and required current deletion
  ledger, then apply the already-rehearsed upgrade to the explicitly verified target.
- Start one loopback worker. Check readiness/capabilities/authentication and an
  owned saved-request/source smoke test without logging private data.
- Verify the separately authorized trusted HTTPS/VPN route and current client
  compatibility. Do not expose provider/database ports or enable later features.
- Keep enrollment, erasure processing and embeddings at their explicitly selected
  settings. Do not change retention or schedule backups/dreaming implicitly.
- If a gate fails, stop serving, preserve artifacts and use the tested isolated
  recovery procedure. Never overwrite the live database merely to test rollback.

## Reproduce the quality scorecard

The default uses only committed public/synthetic corpora and disposable SQLite;
it never evaluates private account data or downloads a model:

```powershell
./.venv/Scripts/python.exe scripts/evaluate_quality.py --output .pytest_cache/quality-scorecard.json
```

For the dedicated disposable PostgreSQL test database, set its protected
`ADA_TEST_DATABASE_URL` (database name `ada_phase2_test`) and add `--postgres`.
The extraction adapter remains SQLite and is labeled as such. Each component
owns its temporary database/schema. Resource numbers cover Python allocations
and elapsed runtime, excluding PostgreSQL/native/GPU/other processes.

`evaluations/quality-baseline-v1.json` pins canonical JSON digests, portable `/`
paths and development/heldout splits. Corpus changes fail until an explicit new
version is reviewed. The heldout set is a public regression set frozen before
future relevance tuning, not proof of unseen model training data. Do not tune on
it and then keep calling the result independent validation.

Five component programs are reused: claim retrieval, documents, hybrid comparison,
reviewed extraction and episode summaries. Additional holdout checks cover current/
historical correction, Unicode evidence, owner/scope/future isolation, no evidence
and ambiguous dates. Exact-evidence/isolation checks are hard gates; fixture gold
precision and marker coverage remain fixture measurements. Useful answers,
citation entailment, justified uncertainty and follow-up helpfulness stay explicitly
unassessed until an appropriate reviewer evaluates them. No aggregate "intelligence"
score or private text export is produced.

An explicitly installed local model can be probed with
`--generation-provider ollama`; record model/digest and availability separately.
No automatic model download, semantic activation, prompt upgrade or inference
service start occurs. Do not present a fixture run as model quality. Private
evaluation needs a separately consented corpus/sanitization/review protocol.

## Reproduce the proxy laboratory check

Use the exact official Caddy release and checksum recorded in
[validation-tools.json](../../ops/validation-tools.json). Verify its SHA512 before
execution; the binary is not vendored or installed as a service.

```powershell
$adaCaddy = 'path/to/verified/caddy.exe'
./.venv/Scripts/python.exe scripts/verify_private_proxy.py --caddy $adaCaddy --output .pytest_cache/private-proxy.json
```

The harness validates the unchanged template, then adapts only listening/upstream
addresses to explicit loopback ports19420/18420. It refuses occupied ports, creates
an ephemeral test CA, trusts it only in the test client and stops its own processes.
Checks include API authorization-header forwarding, JSON errors, `/admin` redirect,
nested SPA routing, SSE frames, untrusted CA and wrong-host rejection. Its upstream
is a synthetic protocol fixture; actual ADA ownership tests are separate.
No system certificate trust, physical release client, remote private network,
public CA renewal, live server or deployment is verified by this laboratory test.

Primary Caddy references: [CLI validation](https://caddyserver.com/docs/command-line)
and [official release](https://github.com/caddyserver/caddy/releases/tag/v2.11.7).
