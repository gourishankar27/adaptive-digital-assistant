# Phase 19 — optional mobile inference and selected integrations

Status: conditional plan. Prerequisites: Phases 12/18 plus measured device or
explicit integration requirements. Apply STANDARDS and CODEX-WORKFLOW. Choose one
bounded subphase; do not implement every option in this document by default.

## A — optional on-device model assistance

First record the actual Android OS, RAM, SoC, storage, thermal/battery limits and
supported inference runtime. Verify model license/runtime/quantization support
from primary documentation and benchmark the target phone. Do not promise that a
desktop model fits or runs acceptably on an unseen device.

Useful initial tasks are local intent suggestions, draft summaries and offline
draft replies. PostgreSQL/server authorization remains authoritative. Show local
output as generated draft with its limitations. It cannot silently become a
user-authored chat event, durable claim, tool permission or server response.

Design a device-proposal synchronization contract with proposal ID, authenticated
device/owner, authorized input source IDs/hashes, task, model/digest and untrusted
output. Validate lineage, size, enrollment/revocation and scope on the server;
review/promote only through the established endorsement policy. Reconcile offline
sequence and deletion propagation before enabling synchronization. Unknown or
deleted sources leave a draft rejected/stale, not magically trusted.

Keep a network-only path on low-resource/unsupported phones. Capabilities remain
`edge_inference=false` until an actual tested device/proposal flow exists. Evaluate
quality, cold start, memory, battery and thermal behavior with real measurements;
disable the optional feature if its practical benefit is absent.

## B — one selected external integration

Choose a concrete service/task/account, such as read-only calendar lookup before
event creation. Follow the provider's current official authentication and API
documentation. Keep scopes/credentials minimal and server-managed. Resolve the
selected account and recipients/targets explicitly before a write.

Register typed read/write tools under Phase 12 with preview, exact argument-bound
authorization, provider receipt/idempotency and unknown-outcome recovery. Test
through a stub/sandbox first; real external actions need explicit user intent.
Do not add Gmail/calendar/filesystem/cloud access merely because an integration
is listed in a roadmap. Never reuse an admin monitoring role as permission to
act in another user's external account.

Scheduled/proactive actions require a separately implemented durable schedule,
timezone, consent, expiry/revocation and job receipt. A suggestion to remind the
user later is not a working reminder. Define missed-run and duplicate-run policy,
and prevent revoked credentials or changed approvals from authorizing a later
action. Use bounded jobs/shared capacity, not an untracked in-memory timer.

## Client, verification and exit

Android shows local/server provenance and pending sync/tool receipts. Admin shows
allowed operational metadata, not credentials or private provider payloads. An
optional iOS client may reuse the same contracts later; this phase does not require
rewriting the Android app into a cross-platform framework.

Test offline conflict/deletion, revoked devices, forged input hashes, unsupported
hardware, resource exhaustion and no local-model authority. For the selected
integration test account isolation, denied scopes, changed approval, provider
rate limits, duplicate callbacks and ambiguous write timeout. Record real device
or authorized sandbox evidence separately from mocks.

Exit only the selected subphase with measured benefit and reliable boundaries.
Leave the other option conditional. No general autonomous personal-account access
or unreviewed external side effects are authorized by this plan.
