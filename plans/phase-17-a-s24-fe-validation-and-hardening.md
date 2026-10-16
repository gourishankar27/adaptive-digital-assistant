# Phase 17-A — S24 FE voice validation and hardening

Status: **Hardening implemented; validation paused at the user's request on
2026-10-14 UTC. Native audible focus-stop confirmation and other target gates
remain open.** The original audit below is historical evidence, not a new run.
See the new checkpoint in [STATUS](STATUS.md) and [WORKLOG](WORKLOG.md).
This plan follows the user's
request to test the connected phone and record required changes, subsequently
authorized for implementation together with Phase18. Prerequisites:
implemented Phase 17 at `2c242d1`, Phases 04/16, and an owned disposable HTTP fixture.
Apply AGENTS, STANDARDS and CODEX-WORKFLOW. Phase18 was separately authorized;
Phase19 and deployment remain outside scope.

## Inputs and verification boundary

Physical device: Samsung S24 FE, model SM-S721U1, Android 16/API 36, primary user 0,
1080×2340, density 450. The installed ADA debug app is versionCode 12,
`0.17.0-voice`, target 36/minimum 26. Its package, data and microphone permission
were preserved. Tests installed a separately named validation app, using unchanged
production Kotlin code, a test-only application ID/label and USB loopback URLs.

The test server used migrated disposable SQLite head 0014, authenticated private
synthetic data, a deterministic fake model and one worker. Phone tests exercised
real HTTP, Compose, Keystore and explicitly identified native/synthetic audio.
They did not install/migrate the intended server or test Ollama, release HTTPS,
production account history or PostgreSQL concurrency. No bearer token or raw
speech was written to diagnostics or this plan. Private phone profiles, including
Secure Folder, were not accessed.

Machine evidence was collected on 2026-10-13 UTC; the session crossed midnight
in America/Phoenix. Detailed runs and earlier failures are preserved in
[STATUS](STATUS.md) and [WORKLOG](WORKLOG.md). Ignored local artifacts are under
`.pytest_cache/phase17a/`; they are diagnostic evidence, not a committed runner.

## Findings and planned changes

### 17A-01 — P1: preserve the recording intent across its permission dialog

**Confirmed product defect.** Starting with microphone permission revoked, tapping
Record opens the actual Android permission dialog. Verified Deny leaves permission
false with rationale true, but ADA returns `Interrupted` instead of `Denied`.
Verified first-time Allow grants permission but also returns `Interrupted`
instead of starting the requested foreground recording. Recording with permission
already granted works. The user can retry; the first action is lost.

Source diagnosis: `MainActivity.onPause` calls `observeForeground(false)`;
`VoiceController.interruptCapture` treats `Permission` as active capture and
invalidates it. `permissionResult` then ignores the result because the phase is
no longer `Permission`. Current unit tests invoke permission results directly
and do not reproduce the OS dialog's lifecycle transition.

Planned changes:

- Track a pending permission action separately from an active microphone session.
  Bind it to the verified owner/server, conversation, scope and action generation.
- Account for pause/resume caused by the app's own permission dialog. Process its
  result only when the same action/context is foreground and eligible. Never
  start the microphone while backgrounded or after navigation/account changes.
- Deliver ordinary/permanent denial to actionable text/settings states. Cancel
  stale grants and pending permission actions on real context/lifecycle changes.
- Add failure tests before changing this state machine: real OS first grant,
  first/repeated denial, permanent denial, settings return, revoke during capture,
  background/navigation/logout while a permission result is pending, and late
  callback rejection. Preserve text entry and require a new tap after cancellation.

### 17A-02 — P1: resolve the native playback focus-interruption failure

**Observed native-adapter contract failure; root cause remains unresolved.**
An isolated installed TTS probe played a long public synthetic sentence. A
separate UID's foreground fixture then received `AUDIOFOCUS_REQUEST_GRANTED`
with window focus. The native playback adapter did not invoke its interruption
callback within the observation window. The isolated assertion failed (6.489 s).
Two earlier combined probes also failed; a same-UID probe was inconclusive and
must not be used as proof of cross-app behavior.

This establishes a missing expected adapter callback on this device. It does not
establish whether Android muted the engine, how an actual phone call behaves,
or that ordinary background playback continues. Owned completed-reply playback
did stop on actual activity pause and did not resume automatically.

Planned changes:

- Reproduce with a verified separate foreground focus holder while recording
  request outcome, adapter/controller state and audible output separately.
- Investigate Samsung's installed TTS/focus behavior and ADA's `AudioSession`
  listener/attributes/engine coordination. Select a fix only after this evidence;
  do not infer a root cause from the failed callback alone.
- Ensure real loss/duck clears playback state and stops queued utterances without
  automatic resume. Check active microphone focus as well as TTS.
- Retest real foreground interruption, explicit Stop, background return, voice/
  speed changes and late completion. Playback Stop must remain independent of the
  owned server generation/cancellation API.

### 17A-03 — P2: make device verification reproducible and non-destructive

**Confirmed test portability gap.** The released voice verification script selects
an emulator, uses `10.0.2.2` and the normal debug package, and can uninstall/reset
that package. It is unsuitable for preserving this phone's installed account.
The streaming UI test additionally assumes request controls are inside the
compact history panel. This phone's noncompact panel is a separate scroll area;
the old locator failed twice. Layout-independent locators passed on the unchanged
production app, including 150% font. These are test changes, not a streaming API fix.

Planned changes:

- Add an explicit physical-device verification path with a selected authorized
  device/user, isolated validation application ID and injected authenticated HTTP
  origin. Preserve the user's installed app/data/permissions and other profiles.
- Own only fixture ports, USB reverse mappings, packages and temporary phone
  settings created by the runner. Restore them in failure-safe cleanup.
- Use layout-independent pending-panel locators for compact/noncompact layouts.
  Make streaming fixture timing/IME preconditions observable; retain the initial
  voice stream timeout as a flaky run until a reproducible cause is established.
- Verify the actual OS permission action and resulting permission flags. A later
  denial attempt with no verified Deny click or unexpected grant is inconclusive,
  never a permanent-denial pass. Account for platform dialog variants.
- Stage microphone checks behind a human-ready Record tap. Report counts, timing,
  aggregate error metrics and safe states only. Separate synthetic drivers from
  native audio and availability from recognition accuracy.
- Capture app versus recognition/TTS-service CPU/RAM separately. Define repeatable
  workload/thermal conditions and a real unplugged battery protocol; do not use
  USB charging or simulated unplug as battery-drain evidence.

## Completed target observations

| Check | Actual result |
|---|---|
| Native support | On-device factory available; en-US installed; 15 eligible offline TTS voices, 10 en-US. |
| Quiet microphone sample | One exact 8-word sample: 0 word errors; readiness 386 ms; result 7,625 ms; capture 7,238 ms. |
| Airplane-mode microphone sample | Exact 8-word sample: 0 word errors; readiness 504 ms; result 5,825 ms; capture 5,276 ms. Wi-Fi/mobile data off; USB fixture retained. |
| Initial microphone attempt | User was not ready; excluded from quality metrics. Review/no-send boundary observed. |
| Native review and owned send | No event before approval; original ASR preserved separately; edited endorsement; duplicate Send yielded one voice input; audio hash absent. |
| Offline speaker | Installed en-US voice completed at 0.75×/1×/1.25×/1.5×: 5,589/4,664/3,758/3,157 ms. User confirmed clarity, rates and stopping. |
| Playback lifecycle | Explicit native Stop suppressed late completion; owned completed reply stopped on activity pause and did not resume. |
| Native capture lifecycle | Actual capture paused/resumed and left chat without restoring a draft or creating events; missing installed language produced a safe error. |
| Durable recovery | Four real prepare/force-stop/resume stages passed for reviewed draft and exact submitted request; no automatic new submission. |
| UI/Keystore | Physical voice/memory/platform/store checks; corrected streaming locators; 5 portrait checks at font 150%, 2 landscape voice checks at font 150% passed. Palette selection/persistence included. |
| One cold debug launch | Status ok/COLD; 575 ms. Not a release or distribution benchmark. |
| One app memory snapshot | PSS 120,751 KiB; RSS 217,965 KiB; swap PSS 584 KiB after cold foreground launch. Not peak audio/service memory. |
| Idle CPU context | 4 app CPU ticks over approximately 2 seconds; tick frequency not measured; excludes speech services. |

Two short quiet samples establish basic operation only, not representative accuracy,
accents, noisy-room performance, sustained latency or battery efficiency.

## Remaining verification checkpoints

- [ ] Implement and physically recheck 17A-01, including reliable permanent-denial
      and active permission-revocation/settings-return cases.
- [ ] Resolve 17A-02 with verified OS focus and audible-output evidence; test call,
      duck and noisy-route interruption when appropriate hardware is available.
- [ ] Implement the bounded physical runner/test portability changes in 17A-03.
- [ ] Expand en-US samples across speakers/noise/corrections; measure recognition
      setup, endpoint and final latency independently. Physically reach or explain
      the 60-second cap and setup/final deadline paths. Existing unit bounds are
      not a completed native-duration test.
- [ ] Measure repeated-use app/service CPU/RAM, temperature and unplugged battery
      behavior. USB charging was true throughout; charge increase is not a drain test.
- [ ] Test wired/Bluetooth routing, disconnect/noisy output and real calls with
      available accessories. The user selected the phone mic and had no headset.
- [ ] Verify API 26–30 text/TTS fallback and API 31/32/33 native/language paths on
      suitable devices; Android 16 does not prove older-API behavior.
- [ ] Complete manual TalkBack traversal, actual keyboard/IME access and spoken
      labels/source access; automated semantics/font checks alone are insufficient.
- [ ] Verify an authorized intended installation at required head 0014, release
      HTTPS and live owned API recovery. No application migration/deploy occurred
      in this audit; the historical 0005 observation was not refreshed here.
- [ ] Review retained transcript/account/backup policy within existing capabilities;
      do not add Phase 18 deletion or credentials features in this phase.

## Contracts, failure tests and exit criteria

No new server route/schema/migration is currently indicated by these findings.
Preserve all 89 OpenAPI paths/125 schemas, reviewed-voice provenance and immutable
original text, exact request IDs/replay, ownership/scope checks, prompt snapshots,
no-audio-upload policy, encrypted v10 recovery and v1–v9 reads. Personality and
palette choices do not change permissions. No external ASR fallback, background
listening, implicit Send, automatic memory extraction or direct provider/database
connection may be introduced.

Before implementation, rerun focused invariant/failure tests. Then run Android
unit/lint/APK checks, real OS dialog/native audio checks and owned HTTP/Keystore/
force-stop tests with the portable runner. Run pytest/Ruff; PostgreSQL fixtures
are required if a subsequent approved change actually touches schema/concurrency.
No such server change is planned merely to fix Android lifecycle behavior.

Exit only when the permission action is reliable and context-fenced, native focus
behavior is resolved, the physical runner preserves user data, and remaining
target gates have actual evidence or an explicitly recorded limitation. Retain
earlier failures/skips; do not rewrite this audit as a successful fix run.
