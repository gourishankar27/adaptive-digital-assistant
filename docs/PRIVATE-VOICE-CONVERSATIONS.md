# Private voice conversations — Phase32

Current private release:1.0.0/code28. Use the [build/install helper and current setup](HOW-TO-USE-ADA.md#7-build-and-connect-the-android-app); native speech remains evaluation-only.

Source milestone dated 2026-10-24, America/Phoenix. Implementation and native
acceptance are distinct. Consult the dated [status](../plans/STATUS.md) and
[work log](../plans/WORKLOG.md) for actual results and open gates. This checkout
does not migrate the installed database or upgrade the normal phone app.

## Available build paths

The ordinary Android build retains platform on-device ASR and installed offline
TTS. Their released one-minute protocol remains supported. Additional speech is
an explicitly prepared **local evaluation build**, not a production default or
approved redistribution. No cloud speech service, voice cloning or text LLM is
used. Android clients continue to contact only authenticated ADA HTTP APIs.

The optional build contains sherpa-onnx1.13.8, English20M streaming int8 Zipformer,
English3.3M keyword spotting and Kokoro Englishv0.19. The last offers Bella,
Nicole, Sarah and Sky as separately selectable feminine English voices. Bella
was preferred in the owner's public S24 FE listening comparison; the owner
confirmed prompt Stop. This does not measure conversational accuracy or battery.
These are candidate voices, not claims of human identity or clinical expertise.

The bundle is about399MiB of data, plus the pinned native runtime/APK. Model
installation copies APK assets into app-private no-backup storage; it sends no
network request and starts no microphone. Every file and the complete catalogue
are pinned by size/SHA-256. There is no arbitrary URL/import/archive loader in
the app. Removal waits for native handles to close; an active handle fails
removal visibly instead of deleting a model under inference.

## Why recording may still stop in your current app

The normal installed ADA app was preserved during development. An ordinary
Android Studio/Gradle build also excludes the optional native runtime/models;
a new version number alone does not enable continuous recording. Android's
platform recognizer can end on silence, and its legacy route still has a60s
limit. Increasing silence extras or restarting that recognizer cannot guarantee
one uninterrupted recording.

Open a conversation, tap the microphone and read the **Recording mode** label:

- **Android short recording**: pauses can finish recognition. If the label says
  continuous recording is not included, use the explicitly prepared native build
  described below; copying source or rebuilding the ordinary variant is insufficient.
- **Bundled files available/not installed**: install the verified local speech
  files in Voice controls. This action copies packaged data; it does not download
  a cloud speech service or start a microphone.
- **Continuous recording unavailable on this server**: the server must run the
  reviewed0022 source/migration and advertise `ada-long-reviewed-voice-v1`.
  Follow the normal backup/migration procedure deliberately; this task has not
  migrated your installed database or restarted/deployed your server.
- **Continuous recording off**: explicitly enable **Long-form local recording**.
  The label should then say **Continuous local recording** before a new recording.

The selected continuous mode survives same-owner renewal; logout/account switching
clears that choice. If capability/model availability is lost, choose **Android short
recording** explicitly rather than silently changing engines. Check the mode again
after reconnecting or restarting the app. The latest host-only fix preserves the
native recording and original hold lease
through a successful same-owner/epoch/scope sign-in renewal. It hides other private
views, fences old reads, blocks submission during renewal and keeps Stop usable.
A failed/expired/revoked/changed session still stops capture; an unknown refresh is
never retried. Permission/privacy loss, OS/process termination, audio contention,
backgrounding and actual resource limits can also interrupt recording. Completed
checkpoints survive ordinary audio/process interruptions when secure storage
succeeds; logout/invalid-authentication cleanup retains its existing privacy policy.
The post-fix physical microphone/renewal checks are pending at the owner's request.

## Using a prepared evaluation app

1. Sign into the selected ADA server and open a conversation. A server advertising
   `ada-long-reviewed-voice-v1` is required for long-form capture.
2. Tap the microphone to open Voice controls. Under Private speech models choose
   **Install bundled local speech files**. Allow room for staging and installed
   data. A verification/storage error leaves text and platform speech usable.
3. Choose **Bella** explicitly and use **Preview voice** before enabling reply
   playback. Other installed offline voices remain choices; missing models never
   cause a hidden engine/language switch.
4. Enable **Long-form local recording**. Initial language is en-US. Its visible
   limits are two hours,32,768 Unicode characters and512 internal segments.
   Limits stop visibly and preserve completed checkpoints; there is no unlimited
   hardware/OS guarantee. Ordinary silence is not a turn boundary.
5. Choose **Just listen**, **Gentle questions** or **Practical suggestions** for
   the next long-form turn. This is a fixed expression overlay, included in the
   saved request context/budget, not a psychological classifier. It does not
   change ownership, consent, tool permissions or factual memory. A long voice
   turn does not also request a separate automatic curiosity question.
6. Hold the chat mic; release to finish. Alternatively tap the mic, then Record,
   and finish with Stop. Words appear in the same editable composer. Recognition
   endpoints commit internal segments while the microphone stays open. Nothing
   sends on silence, release, Stop, wake detection, reconnection or restoration.
7. Inspect and edit the wording. For a story over4,000 characters, open Voice
   controls and select an exact **reply context** range. Positions are Unicode
   code points, zero-based, with an exclusive end. Preview the chosen excerpt.
   The whole reviewed story is retained on Send; only that explicit excerpt
   enters model context. It is not replaced by an invented summary or submitted
   as multiple turns. The server's UTF-8 prompt budget can require fewer than
   4,000 characters. A rejected excerpt leaves the encrypted review editable.
8. Press **Send** to endorse the reviewed story and selected excerpt. Exact
   payload/request identity is encrypted before HTTP. Completed reply Sources
   display the full generated originals and reviewed narrative separately.
   Only the selected endorsed event excerpt is ordinary conversational evidence;
   the retained narrative is not automatically indexed as factual memory.
9. Optionally enable **Conversation mode** to read newly completed voice replies.
   Playback uses the saved completed reply's safe plain text; provisional streams,
   private traces and ASR originals are never read aloud. Existing12,000-character
   safe-playback bounds remain visible; full text/source cards stay on screen.
   Stop playback is independent from Stop server generation. Starting capture,
   leaving/locking ADA, focus loss or route interruption stops playback.

## Hello Ada and lock-screen privacy

This first portable implementation is explicitly armed from the visible app,
with microphone and notification permission. It runs a microphone foreground
service with a visible Stop notification. It uses a small local keyword model,
not continuous story transcription. It stores no pre-wake audio or transcripts.

The owner selected **persistent listening with shared session renewal**. There
is no fixed fifteen-minute timeout in the signed-in path. Arming verifies the
current owner/epoch/conversation. Every thirty seconds the service rechecks owned
authentication and conversation metadata; password renewal uses the same
process-wide coordinator and encrypted credential store as the UI. It never
reads chat journals, fetches private conversation content or submits a turn.
The local mic grant contains identity/scope/epoch/session-family and expiry,
not a token or password.

One coordinator serializes refresh, saves an encrypted pending marker **before**
HTTP, verifies the rotated owner/epoch, and atomically replaces the exact stored
refresh secret before returning access. Simultaneous callers coalesce. An unknown
outcome or process death with a pending marker requires sign-in; it never replays
a consumed secret. Access stays in memory and passwords are never persisted.
The visible UI owns renewal so the service cannot invalidate its active requests.
Successful verified renewal during continuous capture preserves its local mic and
hold/Stop controls while other private views are hidden; failed verification or
the old access-expiry deadline stops it. On resume, the UI joins any background rotation and restores verified private
views. No private POST is automatically retried. Absolute session expiry,
revocation, unavailable network/authentication, family/epoch/scope change or
secure-storage failure stops listening and requires explicit re-arming. This
provides session continuity while authorized, not indefinite authentication.
The separate public test fixture still has a bounded synthetic grant and no
account/refresh access; that fixture does not establish renewal correctness.

While armed, background/screen-locked keyword detection can emit a short
nonprivate vibration and an Open ADA notification. It does not unlock Android,
launch a forbidden full-screen activity, read private history, begin a story
recording, endorse text or speak a private reply. Open/unlock ADA and pass its
normal current-owner checks before private interaction. Wake is an activation
cue, never authentication.

Recording/playback preempt the wake lease through one process-wide audio
coordinator. Wake never preempts them and never resumes automatically. Logout,
owner/server/conversation changes, expiry, task removal, permission/privacy loss
and interruption stop listening. Reboot/force-stop/process death require manual
re-arming. No boot receiver, default-assistant replacement, OEM low-power claim,
power-policy change or external speech provider is added. Background credential
renewal uses the existing authenticated ADA password protocol.

## Recovery, retention and server compatibility

App-owned AudioRecord feeds a bounded two-second PCM queue. Slow decoding fails
visibly instead of dropping frames. PCM is zeroed after consumption and is not
written to an audio file or sent to the server. Completed text segments are
incrementally checkpointed through authenticated, owner-bound Keystore storage.
Permission loss, calls, OS process death and storage exhaustion can interrupt
input. The app preserves successfully committed segments, not fabricated or
unacknowledged words. Explicit Discard removes the recording's checkpoints.

Journal19 retains readers for versions1–18, exact long reviewed input and stable
request IDs, with a1MiB encrypted-record bound. An identity-verified Restore only
reads recovery; explicit Connect/account switching clears old private journals.
Do not use Connect as a recovery shortcut. Key/storage failure never creates a
plaintext fallback or automatically submits a POST.

Server head0022 adds `long_voice_inputs`:77 tables,64 owner-content tables.
New routes are additive:

- POST `/v1/conversations/{conversation_id}/long-voice-requests`
- GET `/v1/requests/{request_id}/long-voice-input`

The transcript includes actual duration, client-reported runtime/model identity
and ordered immutable segment UUIDs, hashes, text and end positions. Separate
reviewed wording, exact context span, explicit approval, data epoch and stable
request ID bind one atomic reservation. Original ASR remains generated
interpretation; its digest is not an audio hash or runtime attestation. Failed
and completed retries retain their original request context and provenance.
Old voice/text DTOs, paths, prompts, snapshots and completed replay remain.

Owner deletion includes the new table in dependency order. Backup-v8 includes
the full narrative and old backup-v1–v7 remain readable. Restore quarantines
credentials and automation as before. No private admin reader is added.
Multi-revision downgrade preflights all lower history guards before SQLite DDL.

Installation, once separately selected, requires the usual reviewed encrypted
backup and `alembic upgrade head` against the intended database. This development
task does not run that command against the installed application database.

## Reproducing the optional native evaluation build on Windows

From the repository root, with the pinned Python/JDK/Android tools installed:

```powershell
# Downloads only the public pinned runtime/model artifacts, never private audio.
.\.venv\Scripts\python.exe scripts/prepare_private_voice.py --download

# Quote each complete Gradle property argument in PowerShell.
Push-Location apps/android
.\gradlew.bat '-PadaSpeechRuntimeDir=G:/Project/AgenticAIProject/Ada_Adaptive_Digital_Assistant/adaptive-digital-assistant/build/private-voice' '-PadaValidationApplicationId=dev.ada.validation.privatevoice' testDebugUnitTest assembleDebug assembleDebugAndroidTest
Pop-Location
```

Use your own absolute repository path for `adaSpeechRuntimeDir`. Preparation is
restricted to repository build/ directories and validates every extracted plain
file against the pinned catalogue. It does not install an APK, enroll an account,
activate models or modify the normal app. Without the property the normal build
uses platform speech. Native release tasks are blocked until redistribution and
device acceptance are closed; see [runtime review](../ops/speech-runtime/README.md).

To prepare the ordinary **debug app ID** with the same optional native bundle
for a later explicitly chosen private install, build it without the validation-ID
property (this command builds only; it does not install):

```powershell
$adaSpeechBundle = (Resolve-Path 'build/private-voice').Path.Replace('\', '/')
.\apps\android\gradlew.bat -p apps/android "-PadaSpeechRuntimeDir=$adaSpeechBundle" :app:assembleDebug
```

Its output is `apps/android/app/build/outputs/apk/debug/app-debug.apk`. Confirm
`output-metadata.json` identifies the intended application ID before any install.
A build without `adaSpeechRuntimeDir` produces the platform-only variant again,
although both variants use versionCode28. Native Release is intentionally blocked.
The final host verification leaves ordinary platform build artifacts; it does not
install either variant on your phone. A supporting server/migration and the
in-app install/long-mode steps above are still required. Device acceptance remains
open; these build instructions are not a successful installation record.

The public review activity runs only in a separate `dev.ada.validation.*` debug
package. Its microphone/wake fixtures are explicit public tests and carry no
private account credentials. They are not substitutes for production authorization
or the real HTTP/Keystore tests. Finish review/Stop releases local audio.

## Acceptance still required

Use the [Phase32 checkpoint matrix](../plans/phase-32-private-voice-conversations.md).
Record initial failures as failures, then the exact corrected reruns. Long decoded
PCM is not a real-time microphone/lifecycle soak. A preferred public sample does
not establish story accuracy, noisy names/dates, thermals, battery drain, calls,
active permission loss, TalkBack or background/locked reliability. Do not enable
the normal phone service or publish a native bundle from compilation alone.
