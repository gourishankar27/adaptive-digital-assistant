# Phase 17 — explicit Android voice input and output

Status: planned. Prerequisites: Phases 04 and 16.
Apply STANDARDS and CODEX-WORKFLOW. Voice is an optional input/output mode; text
chat and source access remain complete without microphone permission.

## Goal and checkpoints

1. Add user-initiated microphone capture with clear recording/stop/discard states.
2. Select and validate an ASR engine and transcript-review contract.
3. Let the user review/edit/send a transcript through honest provenance handling.
4. Add optional TTS with independent playback controls and interruption behavior.

Start with push-to-talk. Always-listening wake words, background recording,
biometric/emotion inference and voice cloning are outside this phase. Choose
on-device/system versus server ASR after checking device support, privacy behavior,
language needs and resource use in primary documentation.

## Provenance and API

ASR text is generated interpretation of an audio input, not automatically a user
assertion. Add a typed transcript/draft record or endpoint carrying owner/scope,
engine/version, audio reference/hash if retained, transcript and trust/origin.
The user explicitly approves the edited text before Send. Preserve original ASR
output separately from the reviewed endorsement; never bypass the boundary by
posting unreviewed device-model output as a plain authored user message.

Define a reviewed-transcript submission that creates a normal conversational
turn plus appropriate source lineage/endorsement. This may be a new compatible
route using the existing request ID/payload rules. Keep current text chat unchanged.
If audio stays only on the phone, document the available provenance and delete
it after the user's selected retention point. Do not pretend a server audio hash
exists when the server never receives audio.

For server audio, enforce authenticated owner/scope, size/duration/type limits,
non-public storage, bounded decode/ASR and sanitized errors. External transcription
providers require an explicit configuration/account and visible data handling.
Network/ASR calls run outside transactions and use the appropriate shared capacity.

## Android UX

Request microphone permission at the recording action with meaningful states for
denial, permanent denial and unavailable hardware. Show recording duration and
stop/discard controls. Stop capture on the documented lifecycle transitions;
no accidental background recording or auto-send after reconnect. Preserve an
encrypted reviewed draft with identity isolation, or explicitly discard it.

The review screen makes uncertain words editable and offers text entry. Sending
uses one durable request ID and the standard pending/retry state machine.
Streaming reply and TTS are separate: stopping playback does not cancel server
generation, while Stop generation uses Phase 16. Read completed safe response
text; keep sources available visually/accessibly and avoid reading raw debug
traces or hidden reasoning. Configure audio focus, headset changes, interruptions
and user-controlled playback speed/voice without blocking text chat.

## Verification and exit

Test permissions, lifecycle interruption, max-duration/audio rejection, malformed
audio, offline ASR where selected, server timeout, transcript edit/approval,
identity switch, duplicate Send, TTS interruption and independent generation
cancellation. Test trust labels and source lineage through actual API responses.
Run Android instrumented/device checks with real microphone/speaker/headset and
language samples; report transcription limitations, measured resource/battery
behavior and engine availability rather than unsupported guarantees.

Exit with an explicit record→review→send flow and optional controllable playback.
No background listening, unreviewed transcript memory or implicit external upload.
Update privacy/user documentation, capabilities and actual validation evidence.
