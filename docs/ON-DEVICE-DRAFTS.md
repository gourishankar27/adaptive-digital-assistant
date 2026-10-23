# On-device draft study and synchronization

The user selected Phase19A only, starting with offline draft replies. Phase19B
external integrations remain conditional. There is no general personal-account
access, new tool, server response authority or automatic memory promotion.

**Local drafting remains disabled.** Both measured candidates failed the required
quality gate. Normal Android builds contain no native inference library or model;
`EDGE_QUALITY_APPROVED=false` prevents UI activation even in a runtime-enabled
development build. Server capability `edge_inference` remains false. Network chat
continues to work on supported and unsupported phones. This study concerns text
drafting, not Phase29 speech synthesis/recognition activation.

## Measured S24 FE study

The connected SM-S721U1 reported Android16/API36, arm64-v8a, SoC `s5e9945`, 4096-byte
pages, 7,397,724 KiB RAM and initially about 2.18 GiB available. Storage was about
105 GB total/93 GB used/12 GB free. Measurements used public synthetic prompts
only, two CPU threads, fresh processes, context512/output64 and USB charging.
No private phone content was read. The battery temperature is a device sensor,
not SoC junction temperature; short USB trials cannot measure battery endurance.

| Candidate | Exact public artifact | Result |
|---|---|---|
| HuggingFaceTB SmolLM2-360M-Instruct, Q8 | 386,404,992 bytes, revision593b5a2e04c8f3e4ee880263f93e0bd2901ad47f | Roughly1–2s and417MiB peak RSS; invented context/instruction leakage/misdirected replies failed quality |
| Qwen Qwen3-0.6B, Q8_0 | 639,446,688 bytes, revision23749fefcc72300e3a2ad315e1317431b06b590a | Initial4 cases:2.515–3.515s,720.41–720.84MiB peak RSS; one unclear question. Fresh v2 cases:2.907–3.485s,3/4 met all constraints; missed a requested deadline clarification |

Initial Qwen battery temperature rose39.9→40.3°C over the short trial; fresh v2
started39.4°C. The frozen resource gate is median≤15s, per-reply≤20s, peakRSS≤768MiB,
storage≤768MiB after user approval of the larger candidate, and stop at42°C.
Every reply must preserve supplied facts/uncertainty, ask requested questions,
avoid invented commitments/actions and remain under100 words. Fresh v2 results
do not replace the original failures. Greedy decoding is a deterministic study
choice, not an official recommended sampling preset.

An initial CLI run used `--log-disable`, which also suppressed draft output. Its
empty text is a harness failure, not model-quality evidence. Corrected unsuppressed
runs are distinguished in WORKLOG. Raw public trial artifacts stay in the ignored
validation cache; no private prompts or credentials enter plans.
The checked-in [aggregate public metrics](../evaluations/local-draft-s24-fe-2026-10-22.json)
omit device serial numbers and draft text.

## Boundaries and dormant Android adapter

The optional pinned CPU-only JNI adapter passes a read-only model file descriptor
and explicit prompt to a manifest-isolated, non-exported Android service. That UID
has no app storage/Keystore/network permission. The parent hashes exact model bytes
before every run, retains owner-bound signing keys in Android Keystore, and never
passes a credential to native inference. Output is generated/untrusted text.
Navigation/backgrounding cancels the local wait, unbinds and terminates the
isolated process; late results cannot enter another account or scope.

Context512, prompt≤384 tokens, output64 tokens/12,000 bytes, two threads and native
20s deadline plus22s process watchdog/25s parent wait bound work. Resource preflight
requires1GiB available RAM, acceptable Android thermal state and battery sensor
below42°C. Returned PSS over768MiB is rejected; **this is not an OS-enforced RSS
hard cap**. Android may kill the isolated process on resource pressure. CLI peak
RSS and packaged-service PSS are different measurements. The library has16KiB ELF
load alignment; the measured phone itself uses4KiB pages. Actual16KiB/older OS
compatibility remains a separate target gate.

The dormant importer validates exact size/digest and atomic private-file replacement;
there is no automatic download or active import control while quality is rejected.
Weights are not committed or bundled. They can be removed by deleting only the
optional model or uninstalling the separate validation app. Existing ADA private
data must not be cleared to remove a public candidate.

## Explicit device proposals

`ADA_EDGE_DRAFT_SYNC_ENABLED=false` is the default. An explicitly enabled host
advertises `device_draft_sync=ada-device-drafts-v1`; this means the typed receipt
protocol works, not that a model passed quality. Android Settings then exposes
Device drafts · study, registration/revocation and original recovery records.
There is no production Generate control with either rejected candidate.

Enrollment binds an authenticated owner, stable device/operation UUID and P-256
public key. Synchronization binds owned scope, privacy epoch, proposal UUID,
device revision, monotonic sequence, exact prompt/output hashes, task, model/digest,
runtime and up to4 authorized source-version/span/hash pins. The newline canonical
signature includes the source-pin digest. A signature proves installation-key
possession, not that a model executed or that its output is true. The server
revalidates original lineage on both sync and reads. Deleted/changed evidence,
revoked devices or changed privacy epochs reject/stale a draft. One owner lock
serializes sequence consumption; a failed attempt does not advance it.

Five retained device records and300 proposals per owner are deliberate limits.
Android keeps at most4 exact pending operations,24,000 UTF-8 bytes each, in encrypted
journal18; released journals1–17 remain readable. It encrypts before POST, checks
GET only after restart and explicitly retries only the same original signed body.
Unknown outcomes block replacement sequence writes. Discard removes local recovery
only. A generated draft has no route to become a chat event, claim, tool approval
or server reply. Separate future endorsement must use established policy.

API routes: authenticated GET `/v1/edge/devices`, POST `/v1/edge/devices/{device_id}`,
POST `.../{device_id}/revoke`, POST `/v1/scopes/{scope_id}/edge/proposals/{proposal_id}`
and GET `/v1/edge/proposals/{proposal_id}`. No private admin reader is added.
Migration0021/backup-v7 includes both owner-content tables; restore preserves drafts
and revokes device registrations. No live migration or deployment occurred.

## Reproducing the optional developer library

Review [runtime.lock.json](../ops/edge-runtime/runtime.lock.json). Download only
its exact source and NDK archive URLs, plus CMake4.2.2 and Ninja1.13.2. The builder
verifies sourceSHA256, official NDK archiveSHA1, versions, safe extraction paths,
arm64 ELF and16KiB alignment. It extracts only into repository `.pytest_cache`.
Example from repository root, substituting actual local archive/tool paths:

```powershell
.\.venv\Scripts\python.exe scripts/build_edge_runtime.py --archive .pytest_cache/phase31/llama.tar.gz --ndk-archive .pytest_cache/phase31/android-ndk-r30-windows.zip --cmake 'C:/Program Files/CMake/bin/cmake.exe' --ninja .pytest_cache/phase31/native-tools/ninja/ninja.exe
Push-Location apps/android
.\gradlew.bat assembleDebug assembleDebugAndroidTest '-PadaValidationApplicationId=dev.ada.validation.phase19' '-PadaEdgeNativeDir=G:/your-checkout/.pytest_cache/edge-runtime/jni'
Pop-Location
```

Gradle verifies source/library hashes and runtime ABI before bundling. Only the
separate validation APK may be installed by `verify_pdf_edge_android.py`; it
requires explicit device selection, expected SM-S721U1 and the exact public model.
Use dedicated PostgreSQL `ADA_TEST_DATABASE_URL` and `ADA_TEST_PDF_MANIFEST`.
The runner installs/removes only its own packages, schema and ADB reverse mapping.
Normal `assembleDebug` omits JNI; no deployment is implied by building.

## License review and remaining gates

The separate API37 emulator passed the real Android Keystore/P-256 enrollment,
server signature verification, encrypted pending receipts, actual force-stop,
GET-only restoration, explicit identical retry and revocation flow. Its output
was explicitly synthetic; no model executed in that protocol fixture. Native
model-to-signature end-to-end verification remains open. The Phase31 S24 FE PDF
checks are separate evidence and do not authorize model activation.

The [official Qwen GGUF card](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF) identifies
Apache-2.0 and GGUF/llama.cpp support. The
[SmolLM2 card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF)
also identifies Apache-2.0. The pinned
[llama.cpp license](https://github.com/ggml-org/llama.cpp/blob/620d2225cc436ab0b001e3200e590e3b286ef9ab/LICENSE)
is MIT. Preserve upstream notices/licenses for any later distributable bundle,
including transitive third-party notices. No model or native binary is distributed
by this source change. Toolchains retain their upstream Android/LLVM/CMake/Ninja
license terms; no unreviewed model/runtime substitution is allowed.

Required next evidence before activation: an actually useful candidate passing a
fresh frozen reply set, real-user acceptance, packaged runtime/process isolation
and native model-to-signed-recovery flow, sustained thermal/low-memory recovery, unplugged
battery, older API/16KiB phones and accessible UI. Measured CLI success alone does
not close these gates. Check dated [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md) for which packaged checks actually ran.
