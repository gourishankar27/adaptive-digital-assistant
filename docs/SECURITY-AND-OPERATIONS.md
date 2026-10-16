# Security, retention and recovery

Phase 18 implements schema **0015** and additive owner-authenticated security APIs.
This is a runbook, not an instruction to publish a server or erase a live account.
Use [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md) for the existing development setup.
The selected policy is **retain private content until explicit owner deletion**.
The selected encrypted backup directory is **`%LOCALAPPDATA%/ADA/backups`**.

Phase 20 adds a separate0005 pre-upgrade recovery tool and explicit supported
inventory/tool-major checks. Current0015 artifacts stay compatible. Follow
[RELEASE-READINESS](RELEASE-READINESS.md) for the applicable path and tested
installation checklist; do not use this0015-only backup command unchanged on0005.

## Installation and compatibility

1. Keep the existing `.env` private; never paste it into a ticket, plan or log.
2. Review the normal migration procedure in [README](../README.md). This change
   adds 0015 after released 0001–0014. It does not rewrite those migrations,
   archived prompts, existing request IDs, source trust or completed outputs.
3. Install the pinned requirements with the existing setup procedure. The scoped
   addition is `cryptography==50.0.2` and its pinned transitive dependencies.
4. Apply the migration to the intended installation only when independently
   authorized. This implementation rehearsed migrations on disposable databases.
5. Start one loopback worker:

   ```powershell
   ./scripts/start.ps1
   ```

6. Existing CLI-issued bearer tokens remain valid. They remain the independent
   recovery path; `ada rotate-token ACCOUNT_NAME` replaces the account's legacy
   token and does not revoke separately issued device credentials. Device
   revocation uses the owned security API. No name or personality grants admin.
7. To enable owner-authorized device enrollment, explicitly set
   `ADA_DEVICE_ENROLLMENT_ENABLED=true` in the protected configuration and restart
   the server. An already authenticated owner is required; there is no public
   signup or first-user admin flow. Keep it false when enrollment is unnecessary.
8. To enable explicit erasure processing, set `ADA_DELETION_WORKER_ENABLED=true`
   and restart. Preview remains available with the worker off; confirmation then
   returns `503 deletion_worker_disabled`, without creating a deletion job.

Rollback to 0014 is refused once credential/privacy records or an epoch change
exist. Do not bypass this guard or discard revocation/tombstone history to make
an old application run. Restore a tested compatible installation instead.

## Device credentials and lost delivery

On Android, connect with a valid bearer token, open **Settings → Devices and saved
content**, and tap **Refresh devices and deletion status**. Labels, issue/expiry
dates, last use and revocation are metadata, not evidence of physical device
identity. All active credentials authorize their owner equally; an existing
server-side admin grant still governs monitoring access.

1. Enter a device label and tap **Enroll device (30 days)**. The server stores a
   SHA-256 digest only. The secret is returned once, with `Cache-Control: no-store`.
   It is shown masked in memory; select it only to save it securely in your password
   manager or enter it on the intended client. Never record the secret in notes.
2. **Use issued token on this device** verifies `/v1/me` and capabilities again
   before atomically saving it in Android's Keystore-encrypted journal.
3. **Rotate** issues a replacement and immediately revokes the selected old
   credential. Keep an independent valid credential or local operator recovery
   access before rotating. A successful rotation of the current device installs
   its replacement through the same owner-verification path.
4. **Revoke** requires a confirmation dialog. Self-revocation returns a fixed
   acknowledgement and clears local recovery; subsequent HTTP/stream access fails.
5. A request that times out may have committed. Android reserves the operation UUID
   durably before POST. Refresh checks metadata with GET; it never automatically
   submits enrollment, rotation or deletion on reopening. An explicit retry uses
   the identical operation UUID and body.
6. Replaying an issue operation returns metadata and `token: null`. A digest-only
   server cannot recover its secret. Revoke an undelivered credential and explicitly
   enroll again. If self-rotation lost its response, reconnect with the independent
   credential/legacy token first. Clearing a local reservation does not undo a
   server operation.

Expiration is 30 days by Android default; API enrollment supports 1–90 days. Last
use writes occur at most once per minute. The owner has a maximum of 32 active
credentials and 100 historical issue records; the API returns a fixed limit error
instead of silently discarding revocation history. There is no refresh token,
OAuth service or automatic secret reissue. Admin-web accepts the same bearer
credentials and clears its in-memory session/query cache on authentication loss.

Revocation fences fresh reads/writes, resumed stream access and each outgoing
stream batch. A generation already admitted may finish and persist an owned result;
the revoked observer receives no further private batch. This does not erase the
result or undo an action. Use an independent valid credential for recovery or Stop.

## Explicit retention and erasure

There is no automatic age-based deletion of audio/transcripts, documents, messages,
claims/history, proposals, episodes, traces or completed snapshots. ADA does not
receive/store raw microphone audio; reviewed generated transcripts and their
endorsements are private saved content. Existing bounded operational monitoring
audits retain minimal actor/action/outcome metadata under their documented limits.

`src/ada/inventory.py` explicitly inventories **45 owner-content tables** across
all installed feature phases. Unknown owner-content tables cause preview/processing
to fail closed until the inventory is reviewed. Erasure includes raw imported
bytes, normalized text/chunks, lexical projections, source versions/claims and
corrections, evidence and quote copies, prompt/request snapshots, events, vectors,
entity aliases/receipts, proposals/reviews/extractions, agent/tool payloads and
receipts, episodes/consolidation jobs, preference/affect/learning histories, stream
chunks/cancellation receipts and voice lineage. SQLite FTS triggers remove derived
index entries; PostgreSQL projections are erased with their owner rows.

1. Stop active generation and resolve active agent approvals or consolidation work.
   Preview/confirmation rejects concurrent owner HTTP operations and durable active
   work rather than racing erasure with an admitted publisher.
2. Open Android Settings and **Preview deletion of all saved assistant content**.
   Review counts and retained metadata. A preview expires after ten minutes and is
   bound to the content revision and current row inventory. New private write
   attempts conservatively require a fresh preview, including failed attempts or
   mutations that leave counts unchanged. Revision reservation precedes dispatch.
3. Check the explicit erasure acknowledgement and tap **Confirm deletion**.
   The exact job UUID/preview are stored encrypted before submission. The wire
   confirmation is the fixed literal `erase_saved_content`; arbitrary “yes” fails.
4. While queued/running, ordinary private routes return `409 private_deletion_pending`.
   Owned security status/job reads remain available. Refresh the original job.
5. The worker claims a durable 120-second lease. Erasure, tombstone publication,
   completion and account epoch increment commit atomically. A crashed claim can
   be reclaimed; stale attempt fences cannot publish. Storage failure rolls back
   erasure and records a fixed failure code, without reporting partial success.
6. Completion clears this Android client's private memory and encrypted recovery
   journals. A failed job requires a new preview/explicit new confirmation; replaying
   the old job returns its failure receipt, not a newly executed erasure.

The account, credential metadata/digests, explicit admin grants, minimal operational
audits, deletion counts/UUID receipts and UUID-only request tombstones are retained.
This action deletes **saved assistant content**, not the account or backup files.
Completed replay is normally immutable; explicit deletion is the documented
exception: old request reads/retries return **410 `private_content_deleted`**.
Source/claim references whose rows were erased become unavailable.

Android persists a content epoch beside its verified credential. A changed epoch
discards every old private journal before restoring it; authenticated private HTTP
responses are rejected before decoding when their epoch changes. Foreground return
revalidates the account. Admin monitoring receives a privacy epoch and clears its
query/session cache when a subsequent response observes an erasure. Offline clients
cannot be remotely wiped: disconnect/remove their local app data explicitly if they
will not reconnect. Older clients must be upgraded or have caches cleared. Exports,
copied text, device/OS backups outside ADA, and encrypted database backups may retain
copies. The job receipt and UI state disclose these limits; no secure media-overwrite
or remote-wipe claim is made.

## Single-worker limits and safe diagnostics

`start.ps1` accepts loopback addresses only, runs one Uvicorn worker, disables
access logs, bounds concurrency at 128, uses a five-second keepalive and bounds
incomplete HTTP headers at 16 KiB. PostgreSQL/Ollama remain loopback/private. No
client connects directly to either service.

Authenticated owner reads and writes have independent one-minute buckets (default
2400 reads/600 writes). The process retains at most 4096 rate buckets, admits at
most 64 operations per owner/128 total, and returns `429`/`503` with Retry-After.
Actual streamed request bytes are counted, not just Content-Length: the default
maximum is 512 KiB, which preserves the existing 256 KiB document upload contract.
Non-identity request encodings are rejected, body delivery is bounded to 15 seconds,
and JSON nesting is bounded to 64 levels. Upload ownership is checked before body
buffering. Fixed error codes omit private inputs; client validation never renders
server echo text. No token/body/quote SQL diagnostics are added.

`GET /v1/security/status` reports the authenticated owner's active/rejected HTTP
operations and clearly identifies process scope/one-worker support. Existing admin
monitoring provides generation slots, durable running/failure states and elapsed
times. These are actual queue/rejection states, not GPU throughput measurements.
They are not distributed counters. Do not increase workers/start another inference
or job process until shared admission, lease fairness and real GPU capacity have
been implemented and tested under separately requested scope.

## Selected remote access: private HTTPS with a system-trusted certificate

The selected topology is a private VPN/firewall-restricted Caddy HTTPS endpoint
serving the built admin UI and proxying the loopback ADA API. Only TCP 443 is
reachable from enrolled private clients; API8000, development5173, PG5432 and
Ollama11434 are not exposed remotely. Obtain a system-trusted certificate for a
domain you control through an independently authorized certificate flow (for
example DNS verification). Keep the certificate private key and VPN credentials
separate from database artifacts. No domain registration, firewall change, VPN
enrollment, CA installation or service publication occurred in this phase.

Android release uses system trust and HTTPS; a Caddy internal/user-installed CA
is not sufficient for this release client. Do not weaken trust validation or add
cleartext LAN hosts to bypass certificate errors. Use the existing loopback-only
debug exceptions/USB reverse for development. Caddy supports explicitly supplied
certificates; its [TLS documentation](https://caddyserver.com/docs/caddyfile/directives/tls)
and [proxy documentation](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
describe these options.

Review [Caddyfile.private.example](../ops/Caddyfile.private.example), supply protected
`ADA_PRIVATE_HOST`, `ADA_TLS_CERT`, `ADA_TLS_KEY` and `ADA_ADMIN_DIST` values, and
validate it with an operator-approved pinned Caddy version before any authorized
installation. Paths use forward slashes. The template disables automatic HTTP
redirects and Caddy's management API; it does not configure request access logging.
The API matcher is handled before the SPA fallback, so API failures stay JSON.
SSE flushes promptly. Admin sign-in's browser origin must equal the HTTPS UI origin;
the Android server URL is the same origin root. No bearer is placed in a URL.

## Encrypted backup boundary

The backup command uses PostgreSQL custom format and an exported repeatable-read,
read-only snapshot. Immutable sources, raw document blobs (stored in PostgreSQL),
original prompt/request/evidence snapshots, citations, jobs, receipts, credentials'
digest/revocation state and migration history are included consistently. All public
schema tables are inventoried with row counts and sorted per-row SHA-256 hashes.
Derived search/vector projections are included and may be rebuilt with existing
commands if a separately verified rebuild is necessary. [PostgreSQL documents
snapshot-based dumps](https://www.postgresql.org/docs/18/app-pgdump.html).

The encrypted archive has exactly `manifest.json` and `database.dump`; member names
always use forward slashes. A small fixed configuration allowlist is included.
Plaintext tokens, database passwords/URLs, `.env`, TLS/signing/private keys and
Android Keystore/cache are excluded. Keep protected configuration/key material
separately, with a password manager/restricted ACL and independent recovery access.
The portable envelope uses AES-256-GCM with authenticated header, random salt/nonce
and fixed scrypt parameters n32768/r8/p1. The passphrase is read by `getpass`, never
from command-line arguments or logs. Use a strong random password-manager secret
of at least 16 characters; protect it separately from the encrypted folder.

Only encrypted artifacts reach disk; dump/archive/decryption remain in process
memory. The tool bounds each artifact to 256 MiB and subprocess time to five minutes.
For larger installations, this bounded implementation refuses the backup; design
and rehearse a streaming encrypted alternative before relying on it. Existing files
are never overwritten. Writes are flushed/fsynced and decrypted for read-back
verification. Files remain sensitive despite encryption; restrict local directory
ACLs and prevent unapproved cloud sync. This local folder is not disaster recovery
against loss of the entire computer. No automatic pruning or backup scheduling exists.

## Windows PostgreSQL backup and isolated restoration

The commands below operate on the protected `ADA_DATABASE_URL`; never print it.
Use the matching PostgreSQL major version's client binaries. The implementation
requires the default `public` schema and head0015; query/search-path URLs are refused.

1. Activate the configured virtual environment. Confirm `ada doctor` and readiness
   using your normal local setup. Keep one application worker.
2. Create an encrypted artifact at the selected default destination:

   ```powershell
   python -m ada.operations --pg-bin 'C:/Program Files/PostgreSQL/18/bin' backup
   ```

   The tool asks for the backup passphrase without echo. It prints only artifact
   path, snapshot time, table count and elapsed seconds. Save that manifest metadata,
   not private rows/quotes. Never prune the previous known-good artifact just because
   a new filename exists; require read-back verification and a restore rehearsal.
3. Maintain a **current** separately encrypted deletion ledger after completed
   deletion and immediately before any recovery. It contains only owner/epoch,
   request UUID tombstones and minimal completed-job metadata:

   ```powershell
   $adaBackupFolder = Join-Path $env:LOCALAPPDATA 'ADA/backups'
   $adaLedgerPath = Join-Path $adaBackupFolder ('deletions-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.adaenc')
   python -m ada.operations --pg-bin 'C:/Program Files/PostgreSQL/18/bin' deletion-ledger --output $adaLedgerPath
   ```

   Use the same separately protected passphrase for the backup and this ledger.
   Keep the newest verified ledger available independently. Timestamp validation
   requires it to postdate the backup; only the operator can establish that it is
   actually the latest ledger. If the latest deletion state was lost, keep the
   restored database quarantined and reconcile privacy operations before access.
4. Select an existing verified artifact path and a **new** database name:

   ```powershell
   $adaArtifactPath = Join-Path $adaBackupFolder 'REPLACE-WITH-VERIFIED-ARTIFACT.adaenc'
   python -m ada.operations --pg-bin 'C:/Program Files/PostgreSQL/18/bin' restore --database ada_restore_rehearsal_20261014 --artifact $adaArtifactPath --deletion-ledger $adaLedgerPath
   ```

   Restore requires PostgreSQL operator permission to create a database. It accepts
   only a new `ada_restore_*` name, rejects the configured/source database and any
   existing target, authenticates the artifact before creating the database, restores
   in one transaction, and verifies every table's row counts/hashes. No live database
   is overwritten or dropped. A failed new target stays isolated; never point the
   application at it or retry by overwriting it. Review/drop that explicitly named
   disposable database separately when authorized.
5. Restore preserves original digest/revocation metadata during integrity validation,
   then quarantines **all** restored credentials: legacy digests are randomized and
   every device credential is revoked. It reconciles later content deletions and
   tombstones from the supplied ledger. This intentional quarantine prevents an old
   backup from resurrecting a valid credential that was revoked after the snapshot.
6. In an isolated test environment, verify schema0015, source hashes, citations,
   original completed replay without inference, durable jobs and revocation/deletion
   state. Review unfinished restored generation/consolidation/deletion leases before
   enabling any background worker. Use recovery commands only for actual stale work;
   do not erase historical completed receipts. Reissue an owned legacy credential
   through the local CLI only after the restoration/privacy review succeeds. Do not
   grant admin automatically. A rehearsal does not authorize switching the live URL.
7. Record backup/restore elapsed time and the last committed exported snapshot.
   The recovery-point boundary is that snapshot, plus the supplied latest deletion
   ledger. Later ordinary writes require a newer backup; this is not continuous WAL
   recovery. The measured disposable synthetic drill is recorded in STATUS/WORKLOG,
   not a performance promise for the production database.

## Target verification still required

Before intended use, verify installed head0015, owner enrollment/expiry/revoke,
independent-token recovery, the HTTPS certificate/hostname chain on the release
phone and browser, reconnect cache cleanup, intended database restore size/time and
the latest deletion-ledger procedure. Run realistic rejection/cancellation/GPU load
measurements with the approved worker count. Hardware microphone/focus, TalkBack,
older Android and unplugged battery gates remain separate Phase17-A target checks.

Implementation logs/status distinguish actual disposable Windows/PostgreSQL/emulator
checks from these gates. No production erasure, live backup, deployment or Phase19
implementation is authorized by this document.
