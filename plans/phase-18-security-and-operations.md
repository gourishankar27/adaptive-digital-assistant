# Phase 18 — device credentials, recovery and operational hardening

Status: planned. Prerequisites: Phases 05/06 and an inventory of whichever feature
phases are actually installed. This phase can be brought forward when exposure
or reliability needs require it. Apply STANDARDS and CODEX-WORKFLOW.

## Goal

Operate ADA across selected devices with explicit credential lifecycle, tested
backup/restore, retention/deletion and capacity controls. Baseline authentication,
ownership and private network defaults must be maintained in every earlier phase;
they are not deferred to this later milestone.

## Checkpoint A — device credentials

Design owner-bound credential records with digest only, device label, creation,
expiry/last use where needed and revocation. Admin grants remain server state;
device/user claims cannot invent a role. Enrollment requires a configured authorized
flow, not a public first-user-admin shortcut. Preserve or deliberately migrate
legacy CLI tokens with documented compatibility and rollback behavior.

Implement list/revoke/rotate/enroll contracts and client recovery. A revoked token
cannot resume private reads/writes/streams. Document treatment of already admitted
generation and completed outputs; do not confuse revocation with deletion or undo
of an external action. Protect refresh/enrollment material if that flow is selected;
do not assume an OAuth service or session-cookie infrastructure already exists.

## Checkpoint B — network, rate and shared capacity

Document a selected HTTPS/private remote access deployment while preserving local
development. Expose only intended API/UI ports; never publish PostgreSQL/Ollama
as a shortcut. Add bounded request/input/upload rate and body limits appropriate
to implemented endpoints, sanitized errors and operational telemetry.

Before increasing workers or starting another inference/job process, implement
shared admission/leases and test crash recovery, fairness, cancellation and GPU
capacity. Until that works, retain one Uvicorn worker. Queue limits/timeouts need
real metrics and rejection states; extra processes do not create extra VRAM.
Check dependency/security updates with scoped compatibility validation rather
than a blanket upgrade that changes working contracts silently.

## Checkpoint C — backup and restoration

Define database/blob/config/index backup boundaries and an encrypted destination
chosen by the user. Derived indexes may rebuild; immutable sources, prompt/request
snapshots and receipts must restore consistently. Keep credentials/signing keys
separate and protected. Validate backup completeness and integrity before pruning.

Write Windows/PostgreSQL restore instructions and rehearse restoration into an
isolated disposable environment. Test populated migrations, original request
replay/citations, source hashes, jobs and device revocation state after restore.
Record measured recovery time/data loss boundaries; do not call an untested dump
a proven recovery plan. Never overwrite the live database during a rehearsal.

## Checkpoint D — retention and deletion

Choose explicit user policy for audio/docs/messages/proposals/episodes/traces,
derived indexes and operational audits. Build a dependency inventory: request
messages/citations may contain copies of source quotes, and client caches may hold
private content. “Delete source” cannot claim complete erasure while these remain.

Implement authorized preview/confirmation, idempotent deletion job and propagation
to blobs, source/claim history as permitted, prompt/evidence snapshots, vectors,
episodes, job payloads and local caches. Tombstone/revoke inaccessible references
with an honest user-visible status. Preserve only minimal required audit metadata.
Deletion is an explicit exception to normal immutable-source/completed-replay
rules: document when a replay returns a tombstone rather than original private
content. A general immutable history promise cannot override an implemented
user-authorized deletion policy invisibly.

## Verification and exit

Test enrollment/revocation/switching, admin separation, rate limits, hostile upload
sizes, private-network defaults, restore/replay, crash admission leases and
deletion propagation through all installed features. Use actual PostgreSQL and
target-device checks. Run a restore drill and inspect logs/backups for secrets.

Exit with concrete operational runbooks, demonstrated recovery and truthful
retention/deletion status. Publication, external backup destination enrollment
and production destructive actions require the separately requested scope;
writing or testing a runbook does not authorize them.
