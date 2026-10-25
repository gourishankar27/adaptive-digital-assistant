# ADA 1.0 private personal release

The owner selected a release for their own laptop/S24 FE, not public distribution.
Version1.0.0/code 28 is prepared as a **candidate personal baseline**. Installation
and remaining physical acceptance are distinct from a successful host build.
Use [HOW-TO-USE-ADA](HOW-TO-USE-ADA.md) for the complete setup and daily commands.

## Release identity and scope

`release.json` records version, candidate status, distribution and protocol/schema
identities. Python/API, web package/lock and Android use1.0.0; tests check agreement.
API v1, schema 0022, journal 19 and backup-v8 remain separate versions. No migration,
permission model, prompt snapshot or completed replay is changed by the label.

| Artifact | Purpose | Signing/app identity |
|---|---|---|
| PersonalVoice | Own-phone continuous ASR, Bella and experimental wake | Debug-signed; `dev.ada.assistant.debug` |
| CoreDebug | Own-phone standard platform speech | Debug-signed; same debug app ID |
| CoreRelease | Standard build for deliberate release signing | Unsigned; `dev.ada.assistant` |

PersonalVoice does not remove the native Release gate. Device/resource acceptance
and combined-runtime/phonemizer/voice redistribution review remain open. Do not
publish the personal debug APK or claim those gates passed. A broader release is
a separate decision. Failed on-device text generation remains disabled; OCR is off.

## Build a concrete candidate

From root, with the pinned toolchain:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_private_voice.py --download
.\scripts\build-android.ps1 -Profile PersonalVoice
```

The second command runs tests/lint/build, verifies actual APK app ID/version and
native catalogue presence/hash, and writes APK plus receipt under `dist/android`.
The receipt records SHA256, source commit and dirty-working-tree status, not secrets.
No installation occurs. Common Gradle output paths can be overwritten by another
profile; use the distinctly staged artifact and its matching receipt.

For the standard release artifact instead:

```powershell
.\scripts\build-android.ps1 -Profile CoreRelease
```

This stages `ada-1.0.0-corerelease.apk`, **unsigned** and excluding native speech.
The personal voice artifact is separately named and retained.

## Install the personal build

Use section7 of the setup guide: select the explicit ADB serial, verify the
receipt/hash, then `adb -s SERIAL install -r APK`. Matching package/signature is
required for a data-preserving update. Keep the existing debug key, normally
`%USERPROFILE%/.android/debug.keystore`. Never commit or share private keys.

Do not uninstall as a signature-conflict shortcut. First identify the app ID and
original signing key. Switching from debug to production ID creates a separate
app and requires separate sign-in; local Keystore journals cannot simply be copied.

## Sign a standard release APK, if you choose that profile

PersonalVoice is already debug-signed. This section is only for **CoreRelease**;
it does not bypass the native gate. Keep your signing key outside the repository
and back it up privately for all future updates. Use a real interactive terminal.
Create a key only if you do not already have the correct one:

```powershell
$adaSigningDir = Join-Path $env:LOCALAPPDATA 'ADA/signing'
New-Item -ItemType Directory -Path $adaSigningDir -Force | Out-Null
$adaKey = Join-Path $adaSigningDir 'ada-release.p12'
if (-not (Test-Path -LiteralPath $adaKey)) {
    keytool -genkeypair -keystore $adaKey -storetype PKCS12 -alias ada-personal-release -keyalg RSA -keysize 3072 -validity 10000
}
```

Enter passwords in the local hidden prompts; never use password command arguments
or post them. Existing production installations need their original key, not a new
one. Then align, sign and verify the standard APK:

```powershell
$adaTools = Join-Path $env:LOCALAPPDATA 'Android/Sdk/build-tools/35.0.0'
$adaUnsigned = (Resolve-Path 'dist/android/ada-1.0.0-corerelease.apk').Path
$adaAligned = Join-Path (Split-Path $adaUnsigned) 'ada-1.0.0-core-aligned.apk'
$adaSigned = Join-Path (Split-Path $adaUnsigned) 'ada-1.0.0-core-signed.apk'
& "$adaTools/zipalign.exe" -P 16 -f 4 $adaUnsigned $adaAligned
if ($LASTEXITCODE -ne 0) { throw 'Alignment failed.' }
& "$adaTools/apksigner.bat" sign --ks $adaKey --ks-key-alias ada-personal-release --out $adaSigned $adaAligned
if ($LASTEXITCODE -ne 0) { throw 'Signing failed.' }
& "$adaTools/apksigner.bat" verify --verbose --print-certs $adaSigned
if ($LASTEXITCODE -ne 0) { throw 'Signature verification failed.' }
Get-FileHash -LiteralPath $adaSigned -Algorithm SHA256
```

Adjust the SDK path if necessary. Sign only after alignment and do not modify the
APK afterwards. The unsigned build receipt does not describe the newly signed APK;
retain its new hash and certificate fingerprint with your private release record.
These signing/key-creation instructions have not been executed for your key.
Official references: [app signing](https://developer.android.com/studio/publish/app-signing),
[apksigner](https://developer.android.com/tools/apksigner).

## Laptop update and acceptance

The read-only installation check found schema 0022/PostgreSQL 17, healthy API8000
and proxy18764, and tailnet-only Serve. Refresh the editable Python package and
rebuild web assets with the API/proxy deliberately stopped, then restart as the
setup guide describes. Existing0022 needs no schema change for1.0. Verify readiness,
HTTPS/password sign-in and an owned chat. No database reset is part of this release.

Host builds/tests are recorded in STATUS/WORKLOG. Remaining owner checks:

- Install/update the intended app without losing local drafts; sign in over Tailscale.
- Verify actual Continuous local recording, editable review and explicit Send.
- Complete deferred long microphone, post-fix human locked-wake, permissions/calls/
  routes, accessibility and extended unplugged resource acceptance.

The private baseline can be reviewed with those limitations; it is not evidence of
a public-ready voice product. Do not silently close Phase32's physical exit gates.

## Record the source baseline after review

The current tree includes uncommitted implementation/release changes. Review them
before creating a release commit/tag; no automatic Git tag/public upload is made:

```powershell
git status --short
git diff --check
git diff
# Review/stage tracked changes interactively:
git add -p
# Add the new release files only after reviewing them:
git add -- .gitattributes CHANGELOG.md release.json src/ada/version.py scripts/build-android.ps1 tests/test_release_identity.py docs/README.md docs/archive
git diff --cached --stat
git diff --cached
git commit -m "Prepare ADA 1.0.0 private personal baseline"
git tag -a v1.0.0 -m "ADA 1.0.0 private personal baseline"
```

In `git add -p`, select the intended1.0 hunks and exclude unrelated work. Confirm
the cached diff includes the version changes and Phase32 fixes. After commit,
rebuild the selected profile from a clean tree so its receipt records that commit
with `working_tree_dirty=false`. Archive receipts and acceptance results with the
tag. Future development starts after that baseline;
do not relabel an unreviewed dirty checkout as a tagged release.

## Historical recovery references

[Phase20/legacy0005 readiness](archive/RELEASE-READINESS-PHASE20.md),
[current database administration](DATABASE-ADMINISTRATION-WINDOWS.md),
[security/recovery](SECURITY-AND-OPERATIONS.md),
[actual verification](../plans/STATUS.md), [work log](../plans/WORKLOG.md).
