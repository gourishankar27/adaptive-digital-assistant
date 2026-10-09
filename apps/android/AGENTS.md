# Android foundation rules

Root AGENTS.md and plans/STANDARDS.md remain authoritative. Phase 04 adds
authenticated chat and encrypted recovery to the Phase 03 foundations. Memory
editing, streaming, cancellation, voice and tools remain later selected phases.

- Production repositories inject AdaApi and use authenticated ADA HTTP only.
  Mock transports and fixture data belong under test/androidTest, never main.
- Credentials and the exact pending journal use Keystore-backed authenticated
  encryption under noBackupFilesDir. Never use appearance preferences for secrets.
  Verify server/owner before recovery; key loss requires reconnect, not plaintext fallback.
- Do not log private DTOs, error bodies, bearer tokens or credential URLs.
- Bind future caches/journals to normalized server, authenticated identity and
  scope/request. Clear private state on disconnect or account/server change.
- Preserve UUIDs, Long UTC milliseconds, exact source quotes and code-point spans.
  Unknown server states do not mean completed; unsupported write controls stay off.
- Escape display content, allow only safe link schemes, and never execute content.
- Keep system text scaling, labels, keyboard focus and minimum 48dp touch targets.
- Debug HTTP is limited to the hosts in src/debug; release requires verified TLS.
- Use pinned catalog, wrapper checksum, .java-version and Gradle dependency locks.
  Update compatible versions deliberately; no unrelated framework upgrade.
- Run gradlew.bat testDebugUnitTest lintDebug assembleDebug. Run
  connectedDebugAndroidTest and launch on an emulator when available. Record
  physical-phone, TalkBack, font-size and network checks honestly.
