# Explicit Android voice input and reply playback

Phase 17 adds optional push-to-talk and reply playback. Text chat, source access,
ownership, prompts, factual memory and tool approvals keep their existing rules.
The default recognition language is **English (en-US)**. The S24 FE/Android 16
is the intended phone; its engine, language pack and audio behavior still need
physical-device verification. No background listening, wake word, voice cloning,
emotion inference or external transcription service is configured.

## Engine choice and support

Input uses **Android on-device SpeechRecognizer only**, through
`createOnDeviceSpeechRecognizer` on API 31+. There is no generic system recognizer
or network fallback. API 26–30 continue to support text and eligible offline TTS;
voice input explains that Android 12+ is required. Hardware and installed engine
availability are checked. On API 33+, `checkRecognitionSupport` must report the
selected tag among installed on-device languages before recording begins. On
API 31–32, language support is established by the on-device recognition result
or its sanitized language error. ADA never triggers a model download. Install an
appropriate language through the device's speech settings if it is missing.

This choice avoids uploading audio or adding an ASR server, model dependency,
GPU admission queue or external provider account. It depends on the phone's
installed recognition service; accuracy, resource use and battery consumption
are not established by the API availability check. There is no application-level
guarantee that every Android device has an offline engine or English pack.

Primary sources used for the implementation decision:

- [SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer): on-device factory/availability from API 31, support checks from API 33, main-thread use and destroy lifecycle.
- [RecognitionSupport](https://developer.android.com/reference/android/speech/RecognitionSupport): installed on-device language list.
- [RecognizerIntent](https://developer.android.com/reference/android/speech/RecognizerIntent): selected language and recognition options.
- [TextToSpeech](https://developer.android.com/reference/android/speech/tts/TextToSpeech) and [Voice](https://developer.android.com/reference/android/speech/tts/Voice): voice installation/network requirements and bounded utterances.
- [AudioManager noisy-output broadcast](https://developer.android.com/reference/android/media/AudioManager#ACTION_AUDIO_BECOMING_NOISY): stop before audio becomes audible on a different output.
- [Audio focus](https://developer.android.com/media/optimize/audio-focus): foreground restrictions and interruption behavior.

## Record, review and send

Open an owned conversation and expand **Voice controls**. Recognition language
accepts a language tag such as `en-US`; the service checks installed support.
**Record voice** requests microphone permission at that action. Denial leaves
text available; a permanent-denial state offers Android app settings. No
microphone permission is requested at startup or connection.

Recording displays duration, **Stop recording** and **Discard recording**.
Capture stops at 60 seconds; setup and final recognition each have a 15-second
deadline. Leaving the conversation, pausing the activity, changing identity,
losing audio focus or changing an audio device cancels capture. Late callbacks
cannot repopulate an old conversation/account. Nothing records in the background.

Final words become a separate **generated transcript**. The original is preserved
and displayed on demand. Edit **Reviewed wording**, then explicitly select
**I approve this wording for this conversation**. Any edit removes approval.
**Send reviewed voice** requires valid wording and confirmed encrypted storage.
It sends through the reviewed-voice route, with current normal chat options,
and never falls back to plain authored text. Invalid/rejected input returns to
unapproved voice review. A separately typed composer draft is preserved.

The Keystore-backed, no-backup journal v10 binds draft, original text, edited text
and approval to normalized server, verified owner, conversation and scope. A
single atomic write consumes the approved draft and reserves the exact pending
voice payload/UUID before HTTP POST. Versions 1–9 remain readable. Draft recovery
requires verified identity and does not send; pending recovery only reads the
original server request. Explicit retry uses that exact ID, original transcript,
wording/options and frozen server context. Duplicate taps cannot allocate another
turn. Storage failure blocks sending. A draft whose save is interrupted is hidden
until the saved state is checked on resume, rather than claimed successfully discarded.
A saved draft in another conversation blocks new capture and offers Open saved
voice draft or explicit local discard; draft recovery finishes before recording
can start.

## Provenance, privacy and retention

The app does not retain audio files or buffers, provide an audio URI, or upload
audio. Android's selected on-device service handles microphone buffers; ADA
cancels/destroys the recognizer at completion/discard/interruption. ADA cannot
attest the service's internal buffer erasure or its implementation. There is no
app audio retention option or server audio hash. Recognition confidence is not
treated as truth or approval.

Server metadata is explicitly **client reported**: engine kind `android_on_device`,
Android platform release/API level, selected language and client-measured duration.
It does not attest the service's binary version, identify an audio recording, or
prove what was spoken. Original ASR text has origin `asr_generated` and trust
`generated_interpretation`; it is stored separately from evidence candidates and
model context. Only the explicitly approved wording becomes the ordinary
`user_explicit` event/source version, with `user_reviewed` lineage linking it to
the original transcript. Approval establishes an endorsement, not factual truth.
No claim or proposal is created automatically by recording or reviewing.

Migration **0014** adds immutable owner/request/conversation/scope-bound
`voice_inputs`, with exact transcript ID and content hashes and a foreign-key link
to the endorsed event/source version. Migrations 0001–0013 and old snapshots remain
unchanged. A populated voice history cannot be downgraded; lower history guards
also run before any voice-table DDL. Intended application installation is pending;
the configured database was read as **0005** during this phase and was not changed.

The server caps voice history at **1,000 reviewed inputs per owner**. Text fields
are bounded at 4,000 Unicode code points and duration at 1–60,000 milliseconds.
The transcript remains part of durable private request lineage. The count bound
is not an automatic deletion policy. This phase adds no server deletion or account/
backup erasure path. **Discard voice draft** deletes the local encrypted review
draft; logout/account changes clear local private state. It does not delete a
submitted request or its server lineage. Keep retained transcript text under the
same private database/backup controls as chat evidence. Nothing private is logged.

## Compatible HTTP contract

All routes require the authenticated owner. Foreign private resources remain 404
even for a granted administrator. Client owner/scope/trust/audio fields are not
accepted as authorization or provenance overrides.

| Route | Behavior |
|---|---|
| `POST /v1/conversations/{conversation_id}/voice-requests` | 202 `StreamStatusOutput`; normal chat fields plus required `review: "approve"` and typed `transcript`. |
| `GET /v1/requests/{request_id}/voice-input` | Owned `VoiceLineageOutput` with original and reviewed text/hashes, trust/origin, endorsed source version and explicit absent audio. |
| `GET /v1/conversations/{conversation_id}/voice-inputs` | Owned lineage list, default 25, maximum 50, offset bounded at 100,000. |

The transcript carries `transcript_id`, `engine_id`, `engine_version`, `language`,
`duration_ms` and `original_text`. Unknown fields, unapproved input, external
engine identifiers and audio payloads are rejected before reservation. Voice
fingerprints bind both the old content/options fingerprint and the exact original
metadata. Changed approval wording, metadata or transcript ID conflicts, including
completed replay. A transcript ID cannot be submitted under another request ID.
The unreviewed original record is never used as chat input; only the explicitly
approved wording is submitted, including when the user approves it unchanged. Existing GET/stream/cancel routes and
the Phase 16 retry/capacity/publication rules are reused.

Capabilities add optional `voice_input: "ada-reviewed-voice-v1"` when streaming is
supported, otherwise `"unsupported"`, and `voice_audio_uploads: false`. Older
clients/server payloads keep their defaults. No existing route, required field,
legacy request enum, plain-text fingerprint, citation mapping or prompt changes.

## Optional reply playback

**Read reply** loads an owned completed canonical response afresh; provisional
stream text, original ASR records, raw source cards, tool/debug payloads and hidden reasoning are not
playback input. Code fences, reasoning blocks, links/URLs and citation labels are
removed from the plain spoken rendering. Up to 12,000 characters are split into
bounded utterances without splitting supplementary Unicode. The full reply and
source cards remain available visually and through accessibility.

Only installed TTS voices reporting no network requirement are offered. Select
voice and speed (0.75×, 1×, 1.25×, 1.5×). Playback requests transient foreground
audio focus. Focus loss/duck, audio-device connection changes or noisy-output broadcasts,
leaving chat or backgrounding
stop it without automatic resume. **Stop playback** affects only local playback;
**Stop generation** remains the explicit owned Phase 16 server operation. Starting
recording stops playback. Missing TTS voices leave text chat fully usable.

## Verification boundary

Backend tests use actual HTTP responses on migrated SQLite and PostgreSQL, with
synthetic input. Android unit tests cover review/journal failure paths and audio
controller transitions. Emulator HTTP/Keystore/UI/restart tests inject explicitly
synthetic capture/playback adapters; they do not establish recognition quality,
real offline audio processing, focus behavior of an installed speech engine,
speaker/headset behavior, latency, CPU/RAM or battery use on the phone.

Run `apps/android/scripts/verify-voice-emulator.ps1` on a disposable emulator;
`-UiOnly` selects the focused voice UI tests. It uses a loopback fixture server and
ephemeral app-private credentials. Staged draft and pending-request tests use
actual adb force-stop, then production cold recovery with no automatic submission.
Exact checks, earlier failures, skips and final outcomes are preserved in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md).

Remaining target checks: S24 FE/Android 16 engine and installed en-US pack;
permission denial/permanent denial/revocation through Android dialogs; microphone
samples in quiet/noisy conditions and corrections; offline/airplane-mode ASR and
TTS; hardware focus/call/headset/Bluetooth/route interruptions; real speaker
voices/speeds; background/process interruption; API 26/31/33 compatibility;
TalkBack/keyboard/font zoom; release HTTPS; repeated-use resource/battery and
retention/installation review. Record actual measurements and misrecognitions.
Stop at Phase 17; no later phase or deployment is included.
