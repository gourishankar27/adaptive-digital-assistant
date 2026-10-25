# Phase 32 — private voice conversations and Hello Ada

Status: **source/host verified; target acceptance/exit open**, 2026-10-24,
America/Phoenix. This was explicitly selected for implementation. Source requires
0022/backup-v8 and Android27/journal19; it has not migrated the installed database,
upgraded the normal phone or deployed. Optional native release distribution is
blocked pending licensing and target acceptance. Earlier prerequisite/research
sections below describe the inspected baseline, not the new implementation.

## Implementation checkpoint matrix

| Checkpoint | Current evidence | Remaining acceptance |
|---|---|---|
| A: owner-controlled capture | Bounded AudioRecord/native streaming; silence commits internal segments; encrypted checkpoints; explicit Stop/release and editable composer. Owner confirms both public phrases survived a10s pause until Stop. Accelerated native2/10/30min streams preserved4/20/60 segments; host renewal/hold/expiry tests pass. | Paced2/10/30min actual microphone narratives; noisy names/dates, calls/routes, privacy/permission interruptions, storage/resource pressure and accessibility. |
| B: additive transport/recovery | New authenticated long protocol, full reviewed retention and exact selected context; atomic owner/epoch/idempotency fences; populated0021 upgrade/replay and native encrypted narrative restore/deletion passed; actual S24 HTTP/Keystore/force-stop review/Send stages passed. Old OpenAPI paths/schemas preserved except additive capability. | Full1268 passed/80 conditional skips; host/native336 Android units passed. Actual optional skips and native targets are in STATUS/WORKLOG. No live migration. |
| C: local voice/controls | Pinned optional JNI/ASR/KWS/Kokoro build, bounded local synthesis and explicit choices; Bella preferred and prompt Stop owner-confirmed on S24 FE. Fixed listen/questions/suggestions overlays and explicit completed-reply playback. | Full dependency/phonemizer/voice redistribution review, conversational intelligibility/latency and extended device resource acceptance; native Release remains blocked. |
| D: background/locked wake | Unexported visible-start FGS, local cue-only detector, Stop, scoped expiring authority and shared password renewal. Six isolated HTTP stages passed; pending marker prevents consumed refresh replay. | Initial human Hello Ada missed locked/unlocked; initial native set failed on acoustic input/prefix false wake. After readiness/trailing-blank fixes, the3-case native wake rerun passed, including the real microphone/service and four synthetic negatives. Human locked retry, broad false-wake/miss, lifecycle, unplugged battery/thermal and the new persistent-service renewal fixture remain pending; owner stopped S24 testing. |

**User decision:** persistent listening with shared session renewal, rather than
a fixed15min production lease. Shared UI/service coordination is implemented;
local wake authority remains bounded by the current verified session and is
extended only after checks. Public no-account fixtures still have bounded grants.
Owner explicitly deferred paced2/10/30min microphone tests and then stopped S24 testing; continue host work only. No narrower completed-phase decision is inferred. See dated STATUS/WORKLOG for
actual commands, failures, corrected reruns, skips and final open targets.

## Requested experience

- A warm, calm feminine English voice, initially en-US. Let the owner compare
  public voice samples before selecting a default. Naturalness is a listening
  test, not a property established by a model name.
- Conversation mode with patient pacing, room for personal stories and pauses,
  and an explicit choice of listening, questions or suggestions. Expression does
  not imply human identity, clinical expertise, factual certainty or authority.
- Hold the microphone to speak; release to finish. Tap/Record provides a latched
  alternative that finishes on Stop. Silence must not end either recording.
- Recognized words remain editable in the composer. Existing explicit Send
  endorsement remains; no automatic submission is inferred from this request.
- Opt-in **Hello Ada** detection while the app is backgrounded or screen locked.
  The phrase is an activation cue, never authentication or approval of a write.
- Local speech processing by default. No cloud speech provider, raw-audio upload,
  background conversation transcription or automatic factual-memory extraction.

## Actual prerequisite baseline

Source inspected at20cde93: schema0021, OpenAPI164 paths/216 schemas, Android app26
/0.31.1-voice-composer, journal18. The Phase29 speech study/manifest/preview exists,
but no additional ASR/TTS runtime, model installer or wake detector is activated.
The Phase19A failed text-generation trials do not decide speech-model suitability;
this phase does not enable that unrelated draft-generation feature.

`AndroidSpeechCapture` uses the system on-device SpeechRecognizer. Final results
end the current recognizer session, and its endpointing is controlled by the
installed service. `VoiceController` also stops capture at60seconds. The released
`TranscriptInput` requires duration1–60000ms, engine_id=android_on_device and
original text1–4000 characters. Client validators enforce the same bounds.
Removing only the timer, delaying onEndOfSpeech, increasing silence extras or
restarting the recognizer repeatedly cannot establish lossless continuous input.

Playback currently offers installed non-network Android TTS voices and rate
selection. It speaks owned completed reply text, not provisional streams. The
manifest has RECORD_AUDIO but no microphone foreground service/wake support.
Native permission/focus and model-resource gates from17-A/29 remain open; past
emulator/quiet-room evidence is not acceptance of this new experience.

Prerequisites: read current AGENTS/README/architecture/OpenAPI/tests and the17-A,
29 and password-session contracts. Preserve old requests, prompts, citations,
owner/scope/epoch checks and recovery. Complete independent source/design work
when a phone is absent; do not claim native activation passed.

## A — owner-controlled long-form capture

1. Introduce app-owned microphone capture feeding a local streaming recognizer.
   Evaluate the Phase29 sherpa-onnx/Zipformer candidate and a measured alternative
   as needed. Select exact runtime/model/ABI/API/digests and validate the complete
   dependency/license bundle before redistribution. Do not install a moving
   upstream latest release or activate an unverified model.
2. Own the capture lifetime independently of recognition segment endpoints.
   Silence may finalize an internal text segment but must not close the microphone,
   finalize the owner's turn, approve words or contact the chat server. Preserve
   word order across segments without dropped/duplicated boundaries. Explicit
   release/Stop drains final frames and exposes the editable draft once.
3. Use bounded rolling PCM buffers and incremental encrypted text checkpoints;
   do not retain an entire long recording in memory or silently truncate it.
   No raw-audio file by default. Specify/test backpressure, slow decoding, storage
   exhaustion, resource pressure and model failure. Any actual limit must be
   visible before recording; ordinary silence is not a stop condition.
4. Preserve completed local transcript segments on interruption when authorized
   secure storage succeeds. Permission revocation, OS/process termination, audio
   contention and device failure can still stop input. Show the actual stopped
   state; never claim an uninterrupted hardware guarantee or fabricate a result.
5. Keep existing hold leases, tap/Record/Stop, keyboard/TalkBack route, native
   privacy indicators, editable words and text fallback. Allow manual interruption
   of ADA playback before capture. No automatic resume after privacy/audio loss.

## B — additive long-form transport and recovery

Specify this before expanding writes. The released one-minute reviewed-voice
route remains byte/semantic compatible. Do not clamp actual long duration to60000,
label a new engine as android_on_device, bypass review via plain text, or silently
cut a story into separately submitted user turns.

Design an explicitly versioned, capability-gated long-form draft/turn protocol:
owner/server/conversation/scope/epoch, actual duration, exact ASR/model metadata,
ordered immutable segment IDs/hashes and original wording, separately reviewed
wording, explicit approval and one stable operation/request identity. Document
per-segment/session/owner bounds and an atomic publication/retry/receipt strategy.
Choose concrete routes/DTOs only after reviewing the existing contracts; none is
implemented by this document. Add migrations after0021 only if required.

Very long stories also exceed current input/context budgets. Decide/test how
the full owner-endorsed narrative is retained while the model receives bounded
context. Generated summaries must be separately labeled navigation/adaptations;
they cannot replace original words, become factual claims or rewrite replay.
Long capture support must not conceal a later Send/context rejection.

Version client journals if their durable format changes; retain v1–v18 readers.
Save exact reviewed input before HTTP. Reconnect/restart reads original receipts
without replaying POST; original ASR/source trust and explicit Send are retained.
Include new private inventories in deletion/epoch/backup/restore policy, and
revalidate current principal within server writes. No private admin reader.

## C — natural local reply voice and conversation controls

- Compare installed offline voices with a reviewed neural TTS candidate. Kokoro
  English feminine voices, including af_heart, are audition candidates; neither
  warmth nor acceptable S24 FE speed/battery is established by their catalogue.
  Reuse Phase29's exact-model/runtime/voice/phonemizer/license/integrity study.
- Provide short public samples for owner selection; measure first-audio latency,
  naturalness, intelligibility, long/short sentence handling and names/dates.
  Rate, sentence grouping and pauses should sound steady without pretending to
  infer the owner's emotions from audio. No voice cloning is requested.
- Conversation mode explicitly opts into reading owned completed replies aloud.
  Keep the full saved text/source cards; no silent model paraphrase, hidden
  reasoning, source payload or generated shorter variant enters playback.
- Stop/interrupt must be immediate and independent from server-generation Stop.
  Keep platform/text fallback explicit if a model is missing/removed/unavailable.
- Let the owner choose listening, gentle questions or practical suggestions.
  Do not automatically turn personal disclosures into factual memory or increase
  curiosity depth. Existing chat retention/owner deletion remains in effect.

## D — explicitly armed background/locked wake listening

1. Add a separate opt-in local keyword detector for **Hello Ada**, evaluating
   sherpa-onnx customized keyword spotting or another reviewed local engine.
   Only a small bounded rolling audio window enters wake detection. Do not run
   full-time story transcription, contact a provider or upload pre-wake audio.
2. First portable Android route: an explicitly started microphone foreground
   service, armed from a visible authenticated activity. Declare and request
   appropriate microphone/foreground-service permissions and provide a persistent
   visible status/Stop notification. Handle notification denial, system privacy
   switch, permissions, battery restrictions and supported API differences.
3. Own one audio/session coordinator across UI and service. Use the existing
   password-session protocol with serialized rotation; UI and service must not
   consume the same refresh twice. Fence owner/server/scope/epoch changes, logout,
   revocation and unauthorized/expired sessions. Local recording/draft authority
   and offline behavior must be specified before background activation; a wake
   cue alone grants no private access or persistence authority.
4. Background/locked detection is supported only while the armed service is
   actually active. Do not promise automatic microphone startup after force-stop,
   reboot or arbitrary background launch. Clearly show stopped/not-armed state
   and the user action needed to re-arm. Do not change OS power policy silently.
5. While locked, wake can acknowledge activation with a nonprivate cue. Require
   unlock/current verified owner for private history, settings or endorsement.
   Private spoken replies on the lock screen remain off by default; any optional
   owner-enabled session policy needs explicit review and tests. Do not bypass
   keyguard/background-activity restrictions or use a false alarm full-screen UI.
6. Coordinate wake/capture/playback states to avoid ADA waking on her own voice,
   double-recording or accidental repeated turns. Measure false wakes/misses
   against public TV/music/conversation samples and actual en-US pronunciation.
7. Default-assistant/VoiceInteractionService integration is a separate optional
   decision if the portable route is insufficient. No default-assistant role
   change or OEM low-power hotword capability is assumed or authorized here.

## Verification and exit

Run appropriate Android unit/lint/build, backend pytest/Ruff, current/old-client
OpenAPI compatibility, populated PostgreSQL migrations and concurrency fixtures
when schema/write behavior changes. Test encryption/storage failure, exact
duplicate recovery, owner/scope switching, revoked/expired auth and consumed
refresh races before enabling new writes/services. Use separate validation APKs
and synthetic accounts; preserve normal app/data and live infrastructure.

Required native S24 FE/Android16 acceptance includes:

- Public2-,10- and30-minute narratives, multiple long silent pauses, long word
  boundaries, exact release/Stop and no missing/duplicated segments. These are
  test lengths, not a hidden proposed maximum duration.
- First-time grant/deny, active revocation/privacy switch, calls/focus/routes,
  background/lock/unlock/process death and no unauthorized restart/resume.
- Quiet/noisy en-US names/dates/corrections, offline behavior, actual selected
  feminine voice listening and speech interruption. Record aggregate measures;
  no private narratives/quotes or raw audio in plans/logs.
- Wake misses/false positives/self-wake, screen-locked behavior and battery saver;
  first measure baseline and set documented acceptance thresholds. Quantify idle
  wake battery/thermal/memory use over an extended real-device window. Do not
  promise Siri/Google low-power behavior from an emulator or model-size estimate.

Exit requires a usable consented capture -> edit -> Send -> natural playback loop
and measured background/locked wake mode, or an explicit documented narrower
decision by the user. Compilation, a model download or this plan is not completion.
Do not deploy or enable the normal phone microphone without a separate install/
activation operation. Record actual checks/skips/limits in STATUS/WORKLOG.

## Primary sources reviewed 2026-10-24

- [Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer): continuous-recognition limitations; current adapter is on-device only.
- [Microphone foreground service](https://developer.android.com/develop/background-work/services/fgs/service-types#microphone) and [background-start restrictions](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start): permission, visible-start and lifecycle constraints.
- [Foreground-service overview](https://developer.android.com/develop/background-work/services/fgs): visible ongoing work and notification requirements.
- [VoiceInteractionService](https://developer.android.com/reference/android/service/voice/VoiceInteractionService): separately user-selected assistant/hotword service route.
- [sherpa-onnx keyword spotting](https://k2-fsa.github.io/sherpa/onnx/kws/index.html) and [Android examples](https://k2-fsa.github.io/sherpa/onnx/android/index.html): candidate custom-phrase/native integrations, not device acceptance.
- [Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M), [voice inventory](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) and [sherpa conversion](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html): audition/runtime candidates; pin/review exact bundles during implementation.
- [Existing local speech study](../docs/NATURAL-LOCAL-SPEECH.md), [voice behavior](../docs/VOICE-INTERFACE.md), [17-A gates](phase-17-a-s24-fe-validation-and-hardening.md), [standards](STANDARDS.md).
