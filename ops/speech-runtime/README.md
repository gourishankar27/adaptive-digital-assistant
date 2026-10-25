# Pinned private speech evaluation inputs

Phase32, reviewed2026-10-24. This directory contains a byte catalogue and source
policy, not model binaries, downloaded code or an approved distributable bundle.
`scripts/prepare_private_voice.py` verifies fixed public artifacts into build/.
The Android importer copies only pinned packaged data, never native code.

| Component | Evaluation identity | Distribution disposition |
|---|---|---|
| sherpa-onnx |1.13.8 / commit11afbd009a7f8c08f4bcf2fc1b265d0df4670fbf; AAR SHA256633c24321e06b1fe79feafa03ea16cbc0f8a286641e2da3559bac91bdb13bd96 | Upstream Apache-2.0; AAR native/transitive obligations require a complete inventory before redistribution. Four arm64 PT_LOAD sets measured16KiB aligned. |
| English streaming ASR |20M2023-02-17 int8 encoder/decoder/joiner and tokens; HF revisiond42f2d9f7ca24806fb667456a18a9f1b60f70d16 | Upstream model card Apache-2.0. Preserve exact notices/model card with any distributable package. |
| English wake |GigaSpeech3.3M2024-01-01 archive SHA256f170013b4716e41b62b9bfd809687c207cef798ef9bc6534d524e17af9b6561a | Archive README declares Apache-2.0. Authored Hello Ada BPE tokens are pinned separately; misses/false-wake gates remain device tests. |
| Kokoro | Englishv0.19 archive SHA256912804855a04745fa77a30be545b3f9a5d15c4d66db00b88cbcd4921df605ac7 | Archive includes Apache-2.0 LICENSE. Voice-specific provenance/rights and conversion notices remain a separate distribution gate. Bella preferred in the public owner audition. |
| eSpeak-NG phonemizer/data | Exact data bytes pinned individually in catalogue; linked runtime comes from the pinned AAR | GPLv3 obligations cannot be inferred away from Kokoro's model license. Complete corresponding-source, data-license and combined-binary distribution review is still open. No blanket relicensing of ADA is performed. |

The exact catalogue SHA256 is
`403b9e4b16a87eedaec87bcd5219c02f7f2bc44e274092fc2a237cc0a9036038`.
Its371 files total418,464,052 bytes. Model data and native libraries are absent
from ordinary builds. Optional native release tasks fail closed; local private
evaluation does not grant an external distribution permission or close licensing.

The Kotlin2 JNI callback must be an explicit function object with the typed
`invoke(float[]): Integer` bridge. The first real-device TTS run exposed that the
upstream JNI cannot reflect Kotlin's default invokedynamic lambda; the corrected
callback is tested against the exact AAR, not a different runtime version.

Primary sources:

- [Pinned sherpa release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/v1.13.8)
  and [runtime license](https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/LICENSE).
- [ASR files/model card](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17/tree/d42f2d9f7ca24806fb667456a18a9f1b60f70d16).
- [KWS release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/kws-models)
  and [customized keywords](https://k2-fsa.github.io/sherpa/onnx/kws/index.html).
- [Kokoro configuration and v0.19 voice mapping](https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html#kokoro-en-v0-19-english-11-speakers)
  and [eSpeak-NG license](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING).

The pinned [feature extractor implementation](https://github.com/k2-fsa/sherpa-onnx/blob/v1.13.8/sherpa-onnx/csrc/features.cc)
discards processed feature frames when the decoder advances. Source inspection
and the accelerated ASR stream measurements do not establish extended wake
memory/thermal/battery acceptance. The wake configuration now waits8trailing
blanks, with the original keyword threshold unchanged; the controlled microphone
and confusable-phrase rerun passed, while human locked retry remains pending.

The catalogue has an explicit LF Git attribute because verification hashes its
exact bytes. Windows checkout with core.autocrlf=true was checked against the
pinned digest; ordinary text line-ending conversion must not change the bundle.
