# ADA release notes

## 1.0.0 — private personal candidate — 2026-10-24

Prepared as the owner's laptop/S24 FE baseline, not a public distribution.

- Authenticated chat/streaming, explicit cancellation and immutable request/source replay.
- Scoped memory, reviewed corrections/proposals, entities and source-linked history.
- Android chat, documents, projects/tasks and explicit preference/consent controls.
- Password sessions, private Tailscale HTTPS, read-only admin monitoring and encrypted recovery.
- Optional personal voice build: app-owned continuous capture, editable reviewed
  stories, Bella/Kokoro playback and experimental cue-only Hello Ada.
- Same-owner renewal preserves active continuous recording/hold/Stop and the
  selected mode; loss of support requires explicit short-mode fallback.
- New build profiles stage distinctly named APKs with identity/content/hash receipts.
- Current setup/documentation index replaces duplicate historical startup instructions.

Application versions are1.0.0, Android code 28. API v1, schema 0022, journal 19 and
backup-v8 stay unchanged. No new migration or automatic installation is introduced.
Existing IDs, ownership, trust, prompt snapshots and completed replay are retained.

Known limits: native Release/redistribution review and remaining physical speech/
wake/accessibility/resource acceptance are open. Optional services retain their
configuration/consent gates. On-device text generation failed quality and remains
disabled; OCR is off. The normal speech profile can finish on pauses and has the
legacy60s limit. The personal native build must be selected/installed/enabled explicitly.

See [setup](docs/HOW-TO-USE-ADA.md), [release scope](docs/RELEASE-READINESS.md),
[actual checks](plans/STATUS.md) and [implementation history](docs/archive/README.md).
