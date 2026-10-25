# ADA 1.0 — private personal baseline

ADA runs on your Windows laptop with an Android client. Chat and owned memory
use authenticated ADA APIs; optional speech recognition and playback run locally
on the phone. This is your private v1.0.0 release candidate, not a public release.

**Start here: [laptop setup, Android build/install and everyday use](docs/HOW-TO-USE-ADA.md).**

- [Documentation index](docs/README.md)
- [v1.0 release scope and signing](docs/RELEASE-READINESS.md)
- [Release notes](CHANGELOG.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Actual checks, skips and remaining acceptance](plans/STATUS.md)

## Current versions

| Item | Current value |
|---|---|
| Personal release |1.0.0 candidate |
| Android version code |28 |
| API protocol |v1 — unchanged |
| Database migration |0022 —77 tables |
| Encrypted Android journal |19; older readers retained |
| Encrypted backup |v8; older supported formats retained |

Application version1.0 does not rename the API, migrations or journal versions.
Existing accounts, source trust, request IDs, snapshots and completed replay remain.

## Choose the right Android build

```powershell
# From the repository root; one-time public model preparation.
.\.venv\Scripts\python.exe scripts/prepare_private_voice.py --download

# Includes local continuous capture and Bella; stages a verified personal APK.
.\scripts\build-android.ps1 -Profile PersonalVoice
```

The staged APK is `dist/android/ada-1.0.0-personalvoice.apk`, debug-signed under
`dev.ada.assistant.debug`. Installation commands and signature-conflict handling
are in the [setup guide](docs/HOW-TO-USE-ADA.md#7-build-and-connect-the-android-app).
No build command automatically installs an APK.

`CoreDebug` excludes native speech. `CoreRelease` produces an **unsigned** standard
APK that must be signed before installation. Native Release remains blocked while
redistribution/device gates are open. Private voice is experimental: enable
**Long-form local recording** explicitly and inspect the recording-mode label.
The ordinary Android recognizer can stop on pauses and retains its60s limit.

## Laptop daily start

With Docker/PostgreSQL and Ollama running, use two PowerShell windows from the
repository root:

```powershell
# Window A — leave open.
.\scripts\start.ps1
```

```powershell
# Window B — leave open.
.\scripts\start-private-proxy.ps1
```

Tailscale Serve forwards private HTTPS to the loopback proxy. On this installation,
Android uses `https://windows-asus.tail110867.ts.net`; the dashboard is at
`https://windows-asus.tail110867.ts.net/admin/`. Use username/password sign-in.
The [guide](docs/HOW-TO-USE-ADA.md) explains checks and first-time configuration.

## Release boundary

Host checks pass; remaining S24 FE long-microphone, post-fix locked-wake, lifecycle,
accessibility and extended resource checks were deferred by the owner. Native
speech distribution review also remains open. Optional research/PDF/automation
features retain their separate configuration and consent gates. Text-generation
on the phone remains disabled after quality trials; OCR is off.

Historical phase summaries and old setup commands moved to
[the archive](docs/archive/README.md). Historical validation evidence is preserved
in plans/STATUS.md and plans/WORKLOG.md. No public publication is implied by this
version label. Future development starts after the private installation review.
