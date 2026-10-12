# Android foundation rules

Root AGENTS.md and plans/STANDARDS.md remain authoritative. Phase 04 adds
authenticated chat and encrypted recovery to the Phase 03 foundations. Phase 07
adds explicit memory/evidence/correction and new static personality profiles.
Phase 08 adds bounded text/Markdown uploads and imported document evidence.
Phase 09 adds explicit scoped entities/aliases and reviewed identity mappings.
Phase 11 adds selected-source proposals and explicit review with new endorsement evidence.
Phase 12 adds separately capability-gated read-only tools with exact approval and receipts.
Phase 13 adds explicitly queued generated episodes, pending suggestions and scoped
lexical rebuild jobs, with source inspection and GET-only encrypted job recovery.
Phase 14 adds explicitly scoped interaction preferences and opt-in bounded session
expression, with encrypted v8 exact-key receipt recovery. Restore only reads;
expression never changes permissions, evidence, factual retrieval or tool approval.
Phase 15 adds scoped opt-in learning, explicit evidence/review/pause/reset and
encrypted v9 exact recovery (v1–v8 readable). Learned defaults never authorize
facts/tools/admin; C source cards retain original trust and request snapshots.
Phase 16 adds authenticated incremental replies, owned explicit Stop and GET-only
stream recovery. Detaching/backgrounding never implicitly cancels generation.
Partial text is provisional and cannot construct citation cards or assistant history.
Voice, external writes and automatic extraction remain later phases.

- Production repositories inject AdaApi and use authenticated ADA HTTP only.
  Mock transports and fixture data belong under test/androidTest, never main.
- Credentials and exact pending chat/memory/document/entity/proposal journals use Keystore-backed authenticated
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
- Episode summaries are generated navigation, never endorsed factual evidence.
  Save the exact job before POST; restore only reads the original key. A local
  discard does not cancel/delete server work. Pending suggestions still need
  the separate Phase 11 review. Keep scope/source hashes and code-point spans exact.
- Escape display content, allow only safe link schemes, and never execute content.
- Keep system text scaling, labels, keyboard focus and minimum 48dp touch targets.
- Debug HTTP is limited to the hosts in src/debug; release requires verified TLS.
- Use pinned catalog, wrapper checksum, .java-version and Gradle dependency locks.
  Update compatible versions deliberately; no unrelated framework upgrade.
- Run gradlew.bat testDebugUnitTest lintDebug assembleDebug. Run
  connectedDebugAndroidTest and launch on an emulator when available. Record
  physical-phone, TalkBack, font-size and network checks honestly.

- Proposal drafts and exact extraction/edit/review keys are encrypted and bound
  to verified identity. Model confidence does not approve a claim; display exact
  support trust and require a fresh revision preview after editing. Acceptance
  creates a separate explicit endorsement, never relabels imported/model sources.

- Agent journal v6 saves exact scoped creation/decision/recovery input before POST.
  Restore performs GET only; receipts preserve tool trust and original nonce. Unknown
  states never imply execution. Native model requests cannot approve themselves.
