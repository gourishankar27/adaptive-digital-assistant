# Natural local speech — Phase29 study and contract

2026-10-24 follow-up: [Phase32 private voice conversations](PRIVATE-VOICE-CONVERSATIONS.md)
adds optional pinned native capture/voices/wake evaluation, long reviewed lineage
and shared session renewal. Ordinary builds retain platform speech. Its actual
checks and open wake/license/resource gates are recorded in STATUS/WORKLOG;
earlier descriptions below retain their original milestone boundaries.

Study date: 2026-10-21, America/Phoenix. This release retains Android on-device
recognition and installed offline playback. No additional runtime, model, voice or
phonemizer was downloaded, bundled, installed or activated. The S24 FE/Android16
activation decision remains open. An emulator can validate the interface and
review boundary, not audibility, accuracy, naturalness or battery use.

## What you can use now

1. Open an authenticated conversation, tap the microphone, then open **Engine &
   model details** for capability and installation limits. Android12/API31 or
   newer and an available on-device recognition service are required for Record.
   On API33+, ADA checks the selected language is installed before listening.
2. Leave recognition at **en-US**, or explicitly select an installed language.
   Missing language/service/permission leaves text entry available. ADA does not
   request a recognizer model download or use a network recognizer fallback.
3. Record only when ready. Stop, inspect **Original ASR words (generated)**, edit
   **Reviewed wording**, approve, then Send. Editing clears approval. Raw ASR stays
   unchanged; only the endorsed text becomes conversational input. Nothing sends
   merely because recognition finishes or a draft is restored.
4. Under **Reply playback**, explicitly choose an installed offline voice if no
   en-US voice was selected. ADA no longer silently selects a different-language
   voice when the default language has no match. Voice and recognition language
   remain independent choices. No engine or model is switched automatically.
5. Select 0.75×, 1×, 1.25× or 1.5×, then **Preview voice**. It reads a fixed public
   sample without a microphone, HTTP request, journal write or saved chat event.
   Preview uses the same native playback/focus path as **Read reply**. **Stop
   playback** stops audio; server generation has its own separate Stop.
6. Style is normal: the platform adapter has no independent style capability.
   Playback reads bounded safe completed text; no model paraphrase, shorter
   generated answer, text cleanup or source citation is invented. Full saved
   replies and source cards remain on screen.

Backgrounding, navigation, owner/server changes, focus loss and route interruption
stop local audio without automatic resume. A removed/unavailable system voice
fails closed when playback starts; an active system-engine failure stops playback.
ADA does not control or attest the internals of an OS speech service. Voice
metadata is client-reported playback metadata, not ASR or model-integrity proof.

## Candidate comparison and license study (A)

These are a **study shortlist**, not approved packages or S24 FE performance claims.
Primary upstream metadata/source were inspected without obtaining model binaries.
Existing platform speech is the baseline to beat, not an assumed inferior option.

| Candidate | Exact study identity and function | Compatibility, buffering and storage | License/redistribution disposition |
| --- | --- | --- | --- |
| Android platform | Current API31+ on-device ASR; installed, non-network TTS voices | App minSDK26, API33 language preflight; recognition endpointing belongs to the system service. ADA retains no PCM/file. Voice weights/storage and quantization are not inspectable by ADA. | Vendor/OS packages manage their own distribution. ADA does not redistribute or hash those models. Service metadata is not a license or privacy attestation. |
| sherpa-onnx ASR | Runtime **v1.13.8**, commit `11afbd009a7f8c08f4bcf2fc1b265d0df4670fbf`; streaming Zipformer English20M `2023-02-17`, model revision `d42f2d9f7ca24806fb667456a18a9f1b60f70d16` | Upstream Android ASR/TTS sample minAPI21 and arm64 build script exist. Streaming ASR candidate; int8 encoder/decoder/joiner + tokens total **43,649,301 bytes**, fp32 set **91,928,372 bytes** from file metadata, excluding runtime/overhead. | Runtime Apache-2.0 and model card Apache-2.0 checked independently. No voice or phonemizer is needed for this ASR candidate. Exact runtime/transitive notices and final artifact rights must be captured before distribution. |
| whisper.cpp ASR | Runtime **v1.9.5**, commit `d1be6fde11ac6e0407606b4e42fe72d34add8037`; `ggml-tiny.en.bin` / `ggml-tiny.en-q5_1.bin`, model repo revision `5359861c739e955e79d9a303bcbc70fb988958b1` | Upstream Android app minAPI26; JNI example lists arm64-v8a, armeabi-v7a, x86/x86_64. Batch/windowed ASR candidate, not a promise of streaming latency. Metadata sizes **77,704,715 /32,166,155 bytes**, excluding runtime/working memory. | Runtime and original Whisper MIT notices checked independently; converted model card also MIT. No TTS voice/phonemizer. Preserve notices for exact conversion/runtime dependencies; quantization benefit needs accuracy testing. |
| sherpa-onnx + Kokoro TTS | Same sherpa study runtime; upstream Kokoro82M v1.0 reference revision `f3ff3571791e39611d31c381e3a41a3af07b4987`, study voice `af_heart` | Upstream sherpa Kokoro Android/model route exists. Reference `.pth` (**327,212,226 bytes**) and voice `.pt` (**523,425 bytes**) are **not** an Android ONNX bundle. Conversion, voices.bin, tokens, phonemizer and resulting sizes/digests must be reconciled. Sentence synthesis/chunking differs from ASR streaming; do not assume low first-audio latency. | Model repository declares Apache-2.0, including its voice files under repository metadata; a separate voice-specific rights/notice review is still required. eSpeak-NG COPYING is GPLv3; do not infer whole-bundle Apache terms from the model card. Converted artifacts, voice rights, phonemizer/data licenses and linked-distribution obligations remain **unapproved**. |

Inference from the source study: sherpa offers a possible shared ASR/TTS integration
surface, while whisper provides an independent ASR comparator. Neither establishes
build compatibility with ADA's targetSDK36, actual arm64 device performance,
16KiB native-page alignment or human preference. Kokoro is eligible only for further
compatibility/license investigation. Retaining platform speech is a valid outcome.
No text LLM is selected: a text model does not itself recognize audio or synthesize
natural speech, and extra rewriting creates a word/provenance risk.

Primary references, checked during this study:

- [Android SpeechRecognizer](https://developer.android.com/reference/android/speech/SpeechRecognizer)
  and [offline voice metadata](https://developer.android.com/reference/android/speech/tts/Voice).
- [sherpa Android](https://k2-fsa.github.io/sherpa/onnx/android/index.html),
  [pinned ASR sample](https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/android/SherpaOnnx/app/build.gradle),
  [arm64 build](https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/build-android-arm64-v8a.sh),
  [runtime license](https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/LICENSE),
  [ASR model card/files](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17/tree/d42f2d9f7ca24806fb667456a18a9f1b60f70d16).
- [whisper Android JNI build](https://github.com/ggml-org/whisper.cpp/blob/v1.9.5/examples/whisper.android/lib/build.gradle),
  [runtime license](https://github.com/ggml-org/whisper.cpp/blob/v1.9.5/LICENSE),
  [original weights/code license](https://github.com/openai/whisper/blob/main/LICENSE),
  [converted model card/files](https://huggingface.co/ggerganov/whisper.cpp/tree/5359861c739e955e79d9a303bcbc70fb988958b1).
- [Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M/tree/f3ff3571791e39611d31c381e3a41a3af07b4987),
  [voice inventory](https://huggingface.co/hexgrad/Kokoro-82M/blob/f3ff3571791e39611d31c381e3a41a3af07b4987/VOICES.md),
  [sherpa Kokoro conversion/configuration](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html),
  [eSpeak-NG license](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING).

The study checked metadata digests for, among others, int8 Zipformer encoder
`3810755ce7c3ab26b42a8bcf39d191308fa27fb0f53358823ba46141d03b7eb3`
and tiny.en-q5_1
`c77c5766f1cef09b6b7d47f21b546cbddd4157886b3b5d6d4f709e91e66c7c2b`.
These are upstream metadata, **not** locally verified model files or a complete
approved manifest. Small token files also require independent exact hashes.

## Local interface and installation contract (B)

Implemented Kotlin metadata uses versioned IDs `android.on-device-asr.v1` and
`android.offline-tts.v1`, separate ASR/TTS tasks and an honest system-managed model
status. It does not extend server capabilities or claim an extra engine exists.
`LocalSpeechManifest` v1 and `verifyLocalSpeechBundle` are an executable **metadata
and byte-verification contract only**. There is no catalogue of approved bundles,
installer, download client, import/remove control, native loader or activation API.

The contract binds model/task/adapter, pinned runtime revision, minimumAPI, ABIs,
languages, quantization and a separately reviewed license-record ID. Every plain
artifact has a POSIX relative path, exact byte count, SHA-256 and license ID.
A manifest pin must come from a separately reviewed catalogue, never the import.
Checks cover all paths/metadata before opening files, strict unknown-field rejection,
16KiB manifest, 32-file/1GiB aggregate ceiling, exact bounded streaming hashes,
short/trailing data, case-colliding names, Windows reserved paths/ADS/traversal and
executable extensions. The checker creates no files, does not unpack archives and
never loads native code. It reports unsupported or awaiting-device-validation;
successful byte verification grants **no execution authority**.

Before any future installer is exposed, implement this transaction contract:

| Step/state | Required invariant and failure behavior |
| --- | --- |
| Not installed / unavailable | Text and the explicitly selected platform path remain usable. Show missing language/API/ABI/storage/license/device gate separately. Never silently change engine, language or external service. |
| Explicit download/import preview | Display exact model, all artifacts/digests/bytes/licenses, source and network disclosure; require a deliberate tap. No credentials, private text/audio or arbitrary manifest URL goes to a model host. HTTPS origin/redirect policy and finite transfer deadlines/quotas must be enforced in code. |
| Isolated staging / verifying | App-private no-backup storage, fixed bounded I/O worker, space check including staging+installed copy. Reject archives, links, native libraries, unknown catalogue identities and hash/size mismatches. Use file-descriptor/no-follow checks and immutable snapshots; cancellation/process death removes partial staging before any loader sees it. No untrusted path resolution or decompression. |
| Verified, awaiting device checks | Atomically publish a complete directory only after every byte verifies. Recheck exact runtime/model/voice/phonemizer fingerprint on open; partial/changed bundles remain unavailable. Metadata approval cannot enable capture/playback. |
| Explicit activation | Requires recorded per-device thresholds, quality/resource/focus evidence and a fresh user choice. Select ASR and TTS independently. No audio capture from installation or a preview without a tap. |
| Remove / model disappears | Cancel active local work, increment callback generation, stop audio, wait for owned native work to release handles, remove files and selections, then report not installed. Late callbacks cannot publish transcripts or restart speech. Do not automatically select another engine. |

These installation steps are specified, **not implemented**. A new JNI dependency
must be pinned with lock/checksum/native-transitive inventory and reproduce an
arm64 target build plus native-page-alignment checks. No import may install code.
Native buffer ownership must be explicit: maximum60s recording, finite PCM/ring
budget derived from sample rate/channels/width, bounded TTS text/chunks/output queue,
cooperative cancellation and deterministic release/zeroing on every exit. Never
spill private audio to shared storage, backups, diagnostics or server uploads.
The platform adapter currently retains no application PCM buffer or audio file;
OS service internals are outside ADA's buffer accounting. Future native allocation,
memory-pressure/process-death and staging cleanup must be tested before enabling.

## Words, lineage and authority (C)

No ASR cleanup model or shorter spoken adaptation is enabled. The Phase17 encrypted
voice draft/journal16 and `ada-reviewed-voice-v1` remain unchanged. The server still
accepts **only** `engine_id=android_on_device`. Local adapter IDs are not substitutes
for that field. A future adapter needs an explicitly versioned compatible lineage
extension and new failure tests; do not masquerade it as the platform engine.

If cleanup is later justified, original ASR stays immutable and visible alongside
a separately labeled generated editable draft. Names, numbers, dates and negation
require review; editing resets approval. Only explicit endorsement can Send.
Any synced draft must join owner/scope/privacy-epoch/erasure/recovery policy before
storage. Phase19/19A integrations are not prerequisites and are not claimed built.
Shorter spoken variants, if introduced, need a separate generated-adaptation label,
their own original completed-request link and no factual/citation authority.

## Target comparison and activation gate (D — pending)

Reopen [17-A](../plans/phase-17-a-s24-fe-validation-and-hardening.md) and
[VOICE-VALIDATION](VOICE-VALIDATION.md), especially the unresolved audible native
focus and active permission-revocation gates. The previous two quiet eight-word
successes are historical basic-operation evidence, not a representative baseline.

Use the same public/synthetic en-US corpus for each candidate and the installed
platform: everyday phrases, uncommon names, dates/numbers, negation, questions,
longer punctuation, silence, corrections and quiet/noisy conditions. Freeze sample
IDs and expected words before comparison. Human-ready Record taps only. Do not
export raw private audio or transcripts into reports.

Record per-device API/ABI, exact runtime/model/voice/digests, room/route/workload,
warmup/trial counts and failures. Measure WER=(substitutions+deletions+insertions)/
reference words; count names/dates separately. Separate setup, endpoint/final
latency, first-audio latency, total synthesis/playback time and real-time factor.
Collect app **and speech-service** RAM/storage/CPU, peak temperature/thermal state
and an actual unplugged battery comparison. Human rate naturalness/intelligibility
and errors independently; voice labels or desktop speed are not human ratings.

After measuring the baseline, agree and freeze the acceptable per-device WER,
critical-name/date errors, p95 latency, RAM/storage, thermal/battery budgets and
minimum human preference benefit **before** candidate scoring. No thresholds or
passing measurements are invented here. Require zero privacy/authority/late-output
failures. A quality benefit cannot override a broken Stop or focus boundary.

Repeat offline, unsupported language/API/ABI, denied/permanent/revoked permission,
settings return, explicit Stop, full/transient/duck focus, real calls, route changes,
background/navigation/owner/server change/revocation, engine crash, memory pressure,
model removal and late callbacks. Keep failed trials visible. A failed/unknown gate
leaves the new adapter disabled with explicit platform/text choices. No automatic
server generation cancellation. If no candidate clears all gates, document a
decision to retain the platform adapter.

## Reproduce the checks

From `apps/android` with the pinned JDK21/Gradle wrapper/SDK:

```powershell
./gradlew.bat testDebugUnitTest lintDebug assembleDebug assembleRelease
./gradlew.bat '-PadaValidationApplicationId=dev.ada.validation.phase29' assembleDebug assembleDebugAndroidTest
```

Start a disposable emulator; select your dedicated validation PostgreSQL using
`ADA_TEST_DATABASE_URL` (never the application database). From the repository root:

```powershell
./.venv/Scripts/python.exe scripts/verify_local_speech_android.py --device emulator-5584
./.venv/Scripts/python.exe -m pytest tests/test_voice.py tests/test_client_contract.py tests/test_schema_contract.py --assert=plain -q --tb=short
./.venv/Scripts/python.exe -m ruff check src tests migrations scripts
./.venv/Scripts/python.exe -m ruff format --check src tests migrations scripts
```

The runner uses only a separate validation APK, synthetic capture/playback, real
authenticated HTTP/Keystore and a disposable schema; it force-stops between stages
and cleans APKs/reverse mapping/schema. It refuses a physical serial. It does not
measure speech quality or replace the existing actual force-stop journal protocol.
Rebuild without the validation property to restore normal APK outputs; do not
install them as part of this phase. Actual outcomes/failures/skips are in
[STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md).

Schema0019, OpenAPI145 paths/193 schemas, backup-v5, private erasure inventory,
old prompt snapshots and completed replay remain unchanged. No deployment or
later-phase implementation is included.
