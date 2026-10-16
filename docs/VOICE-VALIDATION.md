# Repeatable isolated Android voice checks

Use the pinned Android wrapper/JDK21/SDK and an explicitly selected authorized ADB
device. The phone's normal ADA package/data/permissions and private profiles must
remain untouched. The runner refuses an existing validation package, occupied
fixture port/reverse mapping and a non-primary current user. It verifies the built
APK's separate identity before installation. It owns only its validation APKs,
loopback fixture process and USB reverse mapping, and cleans them in `finally`.
It changes no airplane mode, font scale, screen timeout or battery settings.

```powershell
adb devices
./apps/android/scripts/verify-physical.ps1 -Device SELECTED_AUTHORIZED_SERIAL -IncludePermissionDialogs
```

Do not put a device serial/token/private transcript into a shared report. A custom
port in19000–19999 can be supplied with `-Port`. The injected instrumentation origin
is USB-loopback, never a production/provider/database URL. The fixture credential
is ephemeral, provisioned through stdin into validation-app-private storage, and
removed with the validation package. The normal app is never reset/uninstalled.

The HTTP suite uses **synthetic** capture/playback drivers with real Compose,
Keystore, owner-authenticated HTTP, streaming and exact force-stop recovery. The
OS-dialog tests use real permission dialogs and verified grant/rationale flags;
they never activate a microphone. Missing/variant dialog controls fail the check,
not a fabricated denial pass. Permission tests refuse normal ADA package IDs.
Permanent-denial variants on older Android require their own verified protocol.

For a separate-UID native audio focus probe:

```powershell
./apps/android/scripts/verify-physical.ps1 -Device SELECTED_AUTHORIZED_SERIAL -NativeFocusProbe
```

1. Confirm the human is ready and the room/workload is recorded using aggregate
   descriptions only. Tap **Play public focus sample** in the isolated native probe.
   It uses installed offline en-US TTS and a public synthetic sentence.
2. Open **ADA focus fixture** (a separate UID with no network/microphone/storage
   permissions). Tap **Request full focus** while the sample is active. Verify its
   explicit **OS focus granted** state. A rejected request is inconclusive.
3. Return to the probe and record its callback state independently from what the
   listener heard. Unlike MainActivity, this debug-only probe deliberately omits
   pause-stop so a lifecycle cleanup cannot masquerade as a native focus callback.
   Stop it explicitly after every observation; the runner force-stops it in cleanup.
4. Repeat transient and duck focus separately, restarting only by explicit tap.
   Confirm stopping, no automatic resume and late-completion suppression. Test the
   production MainActivity's background stop independently. A passing public probe
   is not proof of real calls/headset routing or a resolved Samsung engine issue.
5. Record device API/model, adapter state, focus outcome, timing and audible yes/no
   observations. Do not retain speech/transcript/dumps of unrelated apps.

Real recognition requires a separate **human-ready Record tap**. Verify en-US is
installed/offline, OS grant is effective and no server event exists before explicit
review/Send. Use only agreed synthetic phrases; keep raw speech out of diagnostics.
Report phrase/word counts, total word errors, readiness/capture/final latency and
aggregate room/noise conditions. Availability is not accuracy. Verify denied,
permanently denied, settings-return, active revoke, navigation/account/background
and late callback behavior, keeping text entry available. Never combine a synthetic
adapter result with a native ASR result under one pass label.

For CPU/RAM/thermal checks, run a repeatable warmup and ten identical public sample
cycles after stable idle. Measure the validation app and selected recognition/TTS
service processes separately; report sampling interval, PSS/RSS, CPU tick frequency,
peak/median and thermal state. Do not export full dumps/private app lists. Compare
typed/text-only idle with the same interval and settings. These are diagnostic
measurements, not a performance budget until an approved budget is specified.

Battery requires a real unplugged run at a recorded charge range, brightness,
temperature, network route and screen/audio workload. USB reverse/charging and
simulated battery unplug cannot establish drain. Use independently authorized
private HTTPS fixtures for an unplugged test, record at least30minutes/ten cycles,
and compare the same text-only control. Wired/Bluetooth disconnect/call checks,
TalkBack traversal and API26–33 fallback remain separate when hardware is available.

The Samsung S24 FE observations in the existing Phase17-A plan remain historical.
New source/unit/emulator evidence cannot be recorded as a new physical-phone pass.
