# Phase 29 — natural local speech, with a measured device gate

Status: **Study/interface and platform-preview source locally checked; new runtime
selection and physical activation pending (2026-10-21).** Inputs: 17/17-A source, en-US primary
language, target S24 FE/Android16, G-22/G-27. The current review excludes connected
phone testing. Follow [shared rules](FUTURE-ROADMAP.md). Do not mark voice ready
or select a device runtime solely from desktop/emulator results.

## Outcome and model distinction

Improve naturalness and recognition accuracy while retaining private on-device
audio, explicit transcript review and fallback text chat. ASR maps audio to text;
neural TTS produces speech. A small text LLM may improve phrasing but does not
replace either speech model or guarantee natural prosody.

## Checkpoints

- **A — offline design study now.** Compare installed platform speech with a small
  candidate set: sherpa-onnx Android ASR/TTS adapters, whisper.cpp as an ASR option,
  and a supported local neural TTS such as a Kokoro-family model only if its runtime
  compatibility is demonstrated. Verify exact model/runtime/voice/phonemizer
  licenses and redistribution rights independently. Check supported ABI/API,
  quantization, streaming, storage and model integrity. Candidate names are not
  selections or performance promises. No package/model is installed by this plan.
- **B — modular product contract.** Define ASR/TTS capability and installed-model
  status, integrity-checked opt-in download/import/removal, voice preview, rate/
  style controls and graceful platform/text fallback. No silent engine switch,
  external ASR fallback, background microphone or server audio upload. Bound audio
  buffers and remove temporary audio reliably. Explain unavailable languages.
- **C — preserve words and provenance.** Show original ASR unchanged. If a local
  text model proposes cleanup, retain a separately labeled editable draft and
  require endorsement before Send; never silently change names, dates or meaning.
  Prefer improving TTS/model/voice choice before summarizing the answer. Optional
  shorter spoken variants are generated adaptations, distinguishable from the
  saved completed reply, and cannot invent citations or become source evidence.
  ReusePhase 19A's proposed lineage/authority principles if local drafts sync; do not
  claim Phase 19 implemented or require its unrelated integrations.
- **D — measured activation later.** Reopen17-A's audible focus/native permission
  gates before enabling a new adapter on the phone. Compare identical en-US
  samples for word errors, name/date accuracy, endpoint latency, time to first
  audio, human-rated naturalness/intelligibility, RAM/storage, real-time factor,
  battery and thermals. Test offline, focus/calls/route changes, explicit Stop,
  owner/navigation/revocation and unsupported devices. Keep failed cases visible.
  Use per-device thresholds chosen from the baseline, not advertised model size.

## Data/interfaces and failures

Version installed-model manifests/digests and ASR/TTS adapter IDs. Imported model
content is not executable plugin authority. Protect downloads against tampering,
path traversal, decompression overflow and partial install; keep pinned runtime
dependencies reproducible. Voice metadata is not ASR attestation. Any new synced
draft/cache joins erasure/backup/epoch policy; audio itself remains local/ephemeral.
Test memory pressure, unsupported hardware, engine failure, late callbacks and
model removal mid-playback with text always available. Do not couple playback
Stop to server-generation cancellation. No speculative GPU/CPU performance claim.

## Exit

Without a phone, close only the architecture/license/interface study and host/
emulator contract checks; leave runtime choice and activation pending. Later exit
requires measured quality benefit and acceptable resource/focus behavior on the
actual target, or a documented decision to retain the platform adapter. Physical
verification is deliberately deferred, not an excuse to block Phases 21–28 planning.

Primary candidates: [sherpa-onnx Android](https://k2-fsa.github.io/sherpa/onnx/android/index.html),
[whisper.cpp](https://github.com/ggml-org/whisper.cpp),
[Kokoro model card](https://huggingface.co/hexgrad/Kokoro-82M).
Recheck exact versions/licenses at implementation; none establishes S24 FE quality.

## Selected implementation boundary — 2026-10-21

[Study, local contract, usage and target protocol](../docs/NATURAL-LOCAL-SPEECH.md)
records exact candidate revisions, separate license findings and unresolved bundle
clearance. A is closed as an evidence-qualified study, **not** runtime selection or
permission to redistribute a final bundle. B defines opt-in installation/removal,
buffers/failures/fallback; implements versioned adapter/task/status metadata,
strict pinned manifest/byte validation and platform public preview/rate choices.
No downloader, importer, installer, model loader or activation control exists.
Style remains normal and explicitly unsupported as a separate platform control.
C preserves original ASR, explicit endorsement and completed reply; generated
cleanup/shorter adaptations remain off. D is deferred as this phase's exit permits:
no phone is connected and no new model is enabled. Reopen17-A's audible focus and
native permission gates, then measure baseline/thresholds before candidate scoring.
Host/emulator evidence and retained failures/skips are in STATUS/WORKLOG. No server
contract, schema, journal, dependency, live configuration or later-phase change;
no deployment.
