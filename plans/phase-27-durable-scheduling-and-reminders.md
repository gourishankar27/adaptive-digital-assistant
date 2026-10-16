# Phase 27 — durable schedules, reminders and controlled delivery

Status: **Proposed; planning only.** Inputs: 13 leased jobs, 18 erasure/revocation,
26 operational readiness, 22 session lifecycle if installed, G-25/G-38. Follow
[shared rules](FUTURE-ROADMAP.md). User wants occasional initiated conversations
and notifications as well as chat/inbox; channel delivery must be explicit.

## Outcome

An owner can schedule a private reminder or question, pause it and inspect its
receipt. A restart or timezone change does not silently lose or duplicate it.
This is an ADA inbox/notification product, not authority to email or message others.

## Checkpoints

- **A — owner consent and time.** Store one-time or bounded recurring schedule,
  IANA timezone, local-time expression, UTC occurrence, DST ambiguity choice,
  allowed hours, expiry, channel, cap and owner/scope authorization. Preview next
  occurrences before confirmation. Define spring gaps, autumn folds, edits,
  travel/timezone changes and missed-run catch-up. Default: one latest eligible
  missed occurrence, no flood of old questions, no delivery outside allowed hours.
- **B — durable dispatcher.** Atomic claim/lease/attempt fencing with deterministic
  occurrence keys, receipts, bounded retries and cancellation. A single dispatcher
  coordinates existing jobs; it is not another inference process. Crashes after
  enqueue/delivery acknowledgement have known recovery states. Schedule edit/pause/
  delete increments a generation and suppresses late publication.25 question drafts
  and Phase 28 reflection enqueue through typed bounded job kinds, not executable strings.
- **C — authority across time.** An explicit schedule grant is separate from an
  expiring access session; ordinary logout need not erase a deliberately scheduled
  reminder. Bind its creation to owner/device and consent version. Revoke its
  originating device or explicit schedule consent to pause further occurrences
  until the owner reauthorizes; password reset/all-session revocation also pauses
  automation by default. Recheck owner/scope/source/epoch before reading or delivery.
  Restored schedules are paused/quarantined, not automatically reactivated.
- **D — inbox first, notification channel second.** Commit the durable inbox item
  before attempting a wake-up notification. Opening it explicitly starts/resumes
  an owned conversation; never fabricate a user turn. Deduplicate UI display by
  item/occurrence, with acknowledgement. Treat transport delivery as at-least-once;
  do not promise exactly-once push or that a user actually read it.
- **E — explicit notification choice.** Foreground polling/private connection can
  show in-app notices; background polling may be delayed by Android power policy.
  Do not present either as guaranteed timely background push. If timely background
  notices are required, separately select and review a supported wake-up transport
  (for example generic FCM data signals) and disclose provider-visible device
  tokens/timing metadata. Send no personal text, topic, source or question in the
  wake-up payload; fetch actual content through authenticated ADA HTTPS. Handle
  denied notification permission/offline devices/invalid registrations/rate limits.
  No chosen cloud provider or real registration is implied by this plan.
- **F — owner/admin controls.** Owner sees schedules, next runs, missed/suppressed
  deliveries, snooze/pause/off and generic lock-screen defaults. Admin sees queue/
  failure counts only. Keep a global automation stop and per-owner consent off.
  Never auto-enable notifications because the user enabled curiosity in chat.

## Proposed data/interfaces

Schedule, consent generation, occurrence/lease, owner inbox item, delivery receipt
and protected device delivery registration. Proposed authenticated create/preview/
list/update/pause/status operations require exact idempotent IDs. All private
payloads/registrations enter erasure, data epochs and versioned backup; retain
only justified minimal non-content audit. OS backup trigger in Phase 26 must have one owner,
not a parallel duplicate schedule. No arbitrary code, external writes or browsing.

## Failure tests and exit

Use real PostgreSQL multi-claimer/crash tests for duplicate claim, expired lease,
clock jump, DST, reboot, offline backlog, consent revocation during execution,
deletion between draft and delivery, session refresh and replayed acknowledgement.
Test notification spoofing, wrong-owner deep links, private lock-screen text,
invalid provider receipt and no automatic chat submission. Run actual HTTP/client
inbox flows and stubbed delivery failures. Physical push/doze verification stays
deferred in this review; record unverified channel timing separately.

Exit with restart-safe consented schedules and complete inbox/acknowledgement flow.
Any enabled notification channel must have demonstrated delivery behavior and
honest limits. Unavailable channels stay off. Reminders do not imply unrestricted
future tools, emotional profiling or external-person messaging.
