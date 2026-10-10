# Android foundation rules

Root AGENTS.md and plans/STANDARDS.md remain authoritative. Phase 04 adds
authenticated chat and encrypted recovery to the Phase 03 foundations. Phase 07
adds explicit memory/evidence/correction and new static personality profiles.
Phase 08 adds bounded text/Markdown uploads and imported document evidence.
Phase 09 adds explicit scoped entities/aliases and reviewed identity mappings.
Streaming, cancellation, voice, tools and automatic extraction remain later phases.

- Production repositories inject AdaApi and use authenticated ADA HTTP only.
  Mock transports and fixture data belong under test/androidTest, never main.
- Credentials and exact pending chat/memory/document/entity journals use Keystore-backed authenticated
  encryption under noBackupFilesDir. Never use appearance preferences for secrets.
  Verify server/owner before recovery; key loss requires reconnect, not plaintext fallback.
- Do not log private DTOs, error bodies, bearer tokens or credential URLs.
- Bind future caches/journals to normalized server, authenticated identity and
  scope/request. Clear private state on disconnect or account/server change.
- Preserve UUIDs, Long UTC milliseconds, exact source quotes and code-point spans.
  Unknown server states do not mean completed; unsupported write controls stay off.
- Reserve exact source/claim IDs before memory POST; note acknowledgement is a
  durable stage, not claim success. Recovery reuses identical input and never
  replaces saved chat citation snapshots with refreshed memory.
- Document uploads preserve bounded exact UTF-8 bytes, upload/source IDs, scope,
  filename/type and availability in encrypted recovery before HTTP. Restore never
  automatically POSTs. Imported evidence cannot support an explicit user claim.
- Document cards use request-frozen D labels and distinct imported/untrusted provenance.
  Old M cards and prior journals remain compatible; document use needs real
  capabilities and the explicitly upgraded v4 prompt.
- Identity changes require explicit review, including self and merge preview.
  Save the original scoped operation/body before POST; restore never auto-writes.
  Ambiguity stays visible, and source cards retain the request's canonical snapshot.
- Escape display content, allow only safe link schemes, and never execute content.
- Keep system text scaling, labels, keyboard focus and minimum 48dp touch targets.
- Debug HTTP is limited to the hosts in src/debug; release requires verified TLS.
- Use pinned catalog, wrapper checksum, .java-version and Gradle dependency locks.
  Update compatible versions deliberately; no unrelated framework upgrade.
- Run gradlew.bat testDebugUnitTest lintDebug assembleDebug. Run
  connectedDebugAndroidTest and launch on an emulator when available. Record
  physical-phone, TalkBack, font-size and network checks honestly.
