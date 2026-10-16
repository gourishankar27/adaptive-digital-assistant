# Gaps and future plans

**Review supplement, 2026-10-16:** the original audit/proposals below are retained
as 2026-10-15 evidence. Read [FUTURE-ROADMAP](FUTURE-ROADMAP.md) and the appended
review/corrections before selecting work. New plans start at Phase 20; they do not
blindly adopt F-0's installation/device prerequisites. Physical-device/iOS gaps
are excluded from this planning pass. G-30–G-40 add missing prerequisites and
design risks; none is closed merely by writing a plan.

**Authorized local-operation follow-up, 2026-10-16:** fresh inspection found the
configured Docker database already at0015, without schema drift. The current
loopback API, built admin preview and real Ollama chat/monitoring/replay checks
passed. G-01's local schema-installation gap is now closed; the original audit
and Phase20-only records below remain dated evidence. No0005→0015 live upgrade
is claimed from this observation. G-06/G-09/G-41 and physical/reliability gates
remain open; no new live backup or remote deployment was performed. See the
installation follow-up in STATUS/WORKLOG and
[Windows database administration](../docs/DATABASE-ADMINISTRATION-WINDOWS.md).

Recorded 2026-10-15 UTC. This document is the outcome of a read-only gap audit of
all `plans/` phase files against the current source, tests, contracts, migrations
and clients. It is **documentation only**: nothing in this file authorizes
implementation, installation, deployment or external messages. Reading this
document does not build anything (root `AGENTS.md`: "Adding planning documents
does not authorize building the planned applications").

Method: the audit read every plans/ document (phase-02a through phase-19,
README, CURRENT-STATE, STANDARDS, CODEX-WORKFLOW, STATUS, WORKLOG, DECISIONS,
SOURCES, UI-SPEC), the root README, `docs/ARCHITECTURE.md` and other docs, and
verified citations by direct read-only inspection of `migrations/versions/`,
`src/ada/`, the exported OpenAPI record, `scripts/start.ps1`,
`apps/android/app/build.gradle.kts` and `apps/admin-web/`. No test suite was
rerun, no live database was queried and no code, test, migration, contract,
lockfile, script or product document was changed. See the 2026-10-15 entry in
[WORKLOG.md](WORKLOG.md) for the exact checks.

Parts: Section A — operational/installation gaps (G-01…G-10); Section B —
deferred-by-design boundaries (G-11…G-22); Section C — user-requested
capabilities (G-23…G-29); Section D — future-plan proposals (F-0…F-12) with a
recommended sequencing; then the log-maintenance conventions.

## Status legend

States stay distinct (plans/AGENTS.md). "Planned" means a specification exists,
not that code or a working UI exists.

| State | Meaning |
|---|---|
| Planned | A plan or design exists; no code is claimed. |
| Implemented in source | Code exists in the current tree; no verification is claimed by this label alone. |
| Locally checked | Tests/baselines passed on local Windows, emulators, disposable SQLite/PostgreSQL and (where recorded) fixture or small real-model probes. |
| Target-verified | Physical Samsung S24 FE/Android 16, real servers, release HTTPS, real-model or real-data checks passed for the feature. |
| Installed | The user's configured application database and running instance actually carry the migration head and code the phase requires. |

At the original audit, most Phases 03–18 sat between "Locally checked" and
"Target-verified", with installation not freshly checked. Historical observation
was0005; the authorized follow-up above now verifies local head0015. Installation
does not itself verify every feature on physical hardware or remote HTTPS.

## Phase-coverage summary

| Phase | Status (2026-10-15) | Key open gap(s) |
|---|---|---|
| 00–02 | Implemented in source; Locally checked; baseline Target-verified | G-01 |
| 02A | Target-verified | — |
| 03–16 | Implemented in source; Locally checked; target gates open (physical-phone, release HTTPS, manual accessibility, real-model, installation) | G-01, G-05, G-06, G-07, G-08, G-12, G-13, G-14, G-16, G-17, G-18, G-23 |
| 17 | Implemented in source; Locally checked; partial S24 FE Target-verified (quiet/offline ASR, TTS rates/Stop, recovery); permission/focus issues require 17-A | G-05, G-06, G-22, G-27 |
| 17-A | Implemented in source; testing paused by user 2026-10-14 (S24 FE disconnected); target gates open | G-02, G-07, G-27 |
| 18 (18A–18D) | Implemented in source; Locally checked (full PG18/SQLite 747 passed/23 skipped, Android 224 units, web 56 units + 6 Chromium); final audits and target gates open per pause | G-01, G-03, G-06, G-08, G-09, G-17, G-21 |
| 19 | Planned (conditional); unimplemented (edge_inference: false) | G-11, G-24, G-25, G-27 (remaining Phase 19 scope is covered by G-11) |

## Section A — Operational / installation gaps

Code exists in source; the gap is installation, target verification or a paused
gate. Every item below is Open and dated 2026-10-15 unless noted.

### G-01 — Configured application database far behind source head — HIGH

- Date logged: 2026-10-15. Status: **Closed for local schema/current-server
  installation on2026-10-16**; original audit evidence below is retained.
- Closure: fresh PostgreSQL17.11 query returned0015/54tables; no-op upgrade,
  no-drift check, ready API/current built admin, ordinary-user403 then explicit
  grant200, real qwen3.8:27b chat and identical replay passed. No database reset
  or existing credential/grant change. Physical/release HTTPS and G-41 are separate.
- Evidence/source: fresh read-only checks during Phases 16 (2026-10-12) and 17
  (2026-10-12) recorded configured application head **0005**; Phases 14/15 could
  not reach the configured server; Phases 17-A/18 (2026-10-13/14) did not
  re-query it. Current source requires head **0015** (Phase 18). Migration files
  0001–0015 all exist in `migrations/versions/`.
- User impact: the running ADA instance does not actually serve Phase 08–18
  features (documents, entities, embeddings, proposals, tools, episodes,
  preferences, learning, streaming, voice, security).
- Linked plan: F-0.
- Next action: an authorized installation window — verified encrypted backup
  first, then upgrade the configured database from observed 0005 to head 0015.
  This is a separate, still-unperformed, user-authorized step; no test session
  performs it.

### G-02 — Phase 17-A voice validation paused, open native gates — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: STATUS/WORKLOG 2026-10-14 checkpoint "testing paused by
  user" (S24 FE disconnected). Open gates: audible full/transient/duck
  audio-focus interruption confirmation (the latest staged probe recorded the
  interruption callback, but the user reported speech possibly continuing in the
  fixture — **not a pass**); settings-return and active native microphone
  revocation matrix; real calls/headsets/noisy routes; representative speech
  samples (noise/accent) and native duration/deadline paths; app +
  speech-service CPU/RAM/temperature and real unplugged battery; API 26–33
  fallback paths; manual TalkBack/IME traversal.
- User impact: on-device voice may misbehave under interruptions (media, calls,
  Bluetooth) or on older devices before it can be called target-ready.
- Linked plan: F-0 (resume the paused gates), F-3 (voice quality tracks).
- Next action: resume the separate native focus trials and remaining target
  matrix when the phone is reconnected.

### G-03 — Phase 18 verification paused, final gates open — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: STATUS/WORKLOG 2026-10-14. Implementation is complete in
  source with local verification complete: full PG18/SQLite suite
  747 passed/23 skipped; Android 224 unit tests; web 56 units + 6 Chromium
  cases; dependency audits clean (0 known Python vulnerabilities/41 deps;
  0 findings/295 npm). Open: final source/contract/protected-history/documentation
  audits; Caddy private-HTTPS template syntax and actual trusted-HTTPS
  validation; real-data sizing/capacity; live operations.
- User impact: security/operations features (device credentials, erasure,
  encrypted backup/restore) are not yet cleared for operational use.
- Linked plan: F-0, F-8.
- Next action: finish the final audits and Caddy/private-HTTPS validation;
  then real-data sizing and live operations in a separate scope.

### G-04 — Phase 11 strict cold-launch gate failed once; no successful retry — LOW

- Date logged: 2026-10-15 (historical open item from 2026-10-10/11). Status: Open.
- Evidence/source: STATUS Phase 11 close-out: the strict cold-launch check
  failed, the complete emulator script exited 1, and the task emulator became
  unavailable, so no successful retry is claimed.
- User impact: cold-launch reliability on the emulator remains unproven for that
  checkpoint; the Phase 12 app's new launch passed, which mitigates but does not
  close the historical item.
- Linked plan: F-0 (re-exercise during the next device/emulator window).
- Next action: rerun the strict cold-launch gate during the next authorized
  device verification window.

### G-05 — Physical S24 FE verification partial; device runs an older debug build — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: S24 FE evidence so far is voice audit + isolated
  validation-app checks only (STATUS 17-A audit; 2026-10-14 API36 retry). The
  full feature matrix — chat, memory, documents, entities, proposals inbox,
  tools, episodes, preferences, learning, streaming, security settings — has not
  been physically verified. The phone still has the debug app
  versionCode 12 / 0.17.0-voice; source is at versionCode 13 / 0.18.0-security
  (`apps/android/app/build.gradle.kts`). Release signing/distribution not
  performed.
- User impact: everyday use on the real phone is unverified for most features;
  the phone app lags source.
- Linked plan: F-0.
- Next action: physical full-feature matrix on the S24 FE plus a release
  0.18.0-security build installed on device.

### G-06 — No verified trusted-HTTPS path for remote clients — HIGH

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: `scripts/start.ps1` binds loopback only
  (`ValidateSet('127.0.0.1','::1')`); Android release requires verified TLS
  (none exists yet); admin-web HTTPS static hosting requires a separately
  selected setup; Phase 18B added a private-VPN + supplied trusted certificate
  Caddy example/runbook (`ops/Caddyfile.private.example`,
  `docs/SECURITY-AND-OPERATIONS.md`), but Caddy syntax and actual private
  HTTPS remain unverified (G-03).
- User impact: the phone/admin client cannot connect off-loopback today; any
  remote use would be cleartext or impossible.
- Linked plan: F-0 (part — Caddy validation), F-1 (first-class connectivity).
- Next action: validate the Caddyfile syntax and an actual trusted-HTTPS path,
  then build the LAN/Tailscale connection flow in F-1.

### G-07 — Manual accessibility verification pending for both clients — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: STATUS entries across Phases 03–18 repeatedly state that
  automated semantics/contrast/zoom checks passed and are explicitly **not** a
  substitute for manual review. Pending: TalkBack/screen-reader, hardware
  keyboard, visual/IME review, other browsers for admin-web.
- User impact: assistive-technology users are not covered by any claimed
  verification on either client.
- Linked plan: F-0.
- Next action: manual TalkBack/IME pass on the S24 FE and browser/manual pass
  for admin-web.

### G-08 — No sustained load, production latency, or GPU/throughput measurements — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: STATUS entries record fixture and small-probe timings only,
  explicitly labeled non-production. Admin monitoring reports GPU/throughput as
  unknown. Root `AGENTS.md`: one Uvicorn worker remains until admission control
  is shared across processes (`scripts/start.ps1` runs exactly one worker).
- User impact: behavior under sustained use or concurrent load is unknown;
  scale-out is blocked by process-local admission.
- Linked plan: F-8.
- Next action: sustained load testing protocol and safe metadata-only
  GPU/throughput probes (F-8).

### G-09 — No live/scheduled backups — MED

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: Phase 18C provides on-demand encrypted
  (AES-256-GCM/scrypt) PostgreSQL backup/restore with a validated drill on a
  small fixture (backup 0.516 s / restore 1.25 s), explicitly "not a
  production RTO/RPO guarantee". Data-loss boundary is the last committed
  snapshot plus the supplied deletion ledger; "no live backup was taken"
  (STATUS 2026-10-14).
- User impact: data created after the last manually taken backup can be lost;
  there is no automated recovery safety net.
- Linked plan: F-8.
- Next action: scheduled automatic encrypted backups with retention (F-8).

### G-10 — Housekeeping: retained synthetic fixtures; legacy smoke never run — LOW

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: STATUS Phases 11–13/16: several synthetic fixture
  directories remain in Windows Temp and `.pytest_cache` (removal was blocked by
  policy; synthetic data only). The standalone legacy `smoke_upgrade.py` was
  never run (requires an old Phase 1 checkout); migrated-fixture replay covers
  compatibility instead.
- User impact: none functional; repository hygiene only.
- Linked plan: F-0 (housekeeping item).
- Next action: clean the retained synthetic fixture directories when policy
  allows.

## Section B — Deferred / absent by design

Documented deferrals, not defects. Each remains Open as a known boundary of the
current system until the linked plan (if any) is selected. All dated 2026-10-15.

| ID | Deferred boundary | Evidence/source | Linked plan |
|---|---|---|---|
| G-11 | Phase 19 (optional on-device model assistance, one selected external integration, durable schedule for proactive/scheduled actions, optional iOS) is fully planned and entirely unimplemented | `src/ada/api.py` capabilities: `edge_inference: false`; plans/phase-19 file | F-4, F-6, F-10, F-11, F-12 |
| G-12 | Semantic/embedding retrieval (Phase 10) is implemented but disabled by default; the selected embeddinggemma:300m model was never downloaded; only synthetic fixture vectors were measured | `api.py`: `semantic_retrieval` config-dependent (disabled by default); STATUS Phase 10 | F-7 |
| G-13 | Automatic claim extraction is OFF by design; only explicit selected-source suggestions with human review exist | `api.py`: `automatic_memory_extraction: false`, `memory_proposals: "selected_sources_v1"` | F-7 |
| G-14 | Document ingestion is text/Markdown only; PDF/OCR/archives explicitly deferred from Phase 08 | `api.py`: `document_ingestion: "text_markdown_v1"`; STATUS Phase 08 | F-7 |
| G-15 | Shared scopes / cross-user membership grants not implemented; scopes are strictly private | `api.py`: `shared_scopes: false` | F-9 |
| G-16 | PostgreSQL row-level security is a future defense-in-depth decision; isolation is application-enforced + DB integrity constraints | STATUS Phase 03–07; plans/STANDARDS.md | — (decision only) |
| G-17 | Retention policy is retain-until-explicit-owner-deletion (Phase 18D); no age-based expiry; historical request snapshots/checkpoints persist (24-hour stream cursor expiry is access, not deletion) | STATUS Phase 18 (18D); Phase 16 retention note | F-8 |
| G-18 | Natural date parsing supports only the exact phrase "as of YYYY-MM-DD" (UTC midnight); relative dates ("last week") require user clarification or the `--at` option | README.md (date-parsing contract); docs/PHASE2-RETRIEVAL.md | F-7 |
| G-19 | No automatic affect/mood inference; only opt-in bounded session tone with explicit reviewed signals (Phase 14) | `api.py`: `automatic_affect_inference: false` | — (by design) |
| G-20 | No iOS client (a Swift client "could later use the same HTTP contract") | docs/ARCHITECTURE.md; no iOS directory in repo | F-11 |
| G-21 | No remote admin enrollment: admin web signs in with an already-issued token; admin grants are local CLI (`grant-admin`/`revoke-admin` with account UUIDs) only | README.md (Local administration); STATUS Phase 05 | F-2 (must not weaken) |
| G-22 | Voice is on-device-only by design: no audio upload, no server ASR; STT = system on-device SpeechRecognizer (API31+, en-US default); TTS = installed offline voices only; quality is whatever the platform models provide | `api.py`: `voice_audio_uploads: false`; docs/VOICE-INTERFACE.md; STATUS Phase 17 | F-3 |

## Section C — User-requested capabilities with no plan entry yet

From the user's 2026-10-15 request. All dated 2026-10-15, all Open, all mapped
to a future-plan proposal in Section D. Unlike Section A (which uses
HIGH/MED/LOW), Section C entries carry no severity label until a plan is
selected.

### G-23 — "Make ADA more useful and smart" has no quality/evaluation program — user item 1

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: no cross-feature real-model quality/evaluation program
  exists. Retrieval recall was measured on synthetic corpora (claim corpus
  recall 0.8667; document corpus synthetic 1.0); extraction/summary/preference
  quality was evaluated on synthetic or tiny real probes; representative
  quality evaluations remain pending for several phases (STATUS Phases 10–15).
  No roadmap item exists for continuous quality improvement.
- User impact: "smart" is aspirational, not measurable; the user cannot see or
  steer improvement.
- Linked plan: F-7.
- Next action: select F-7 (quality & smartness program) or a subset.

### G-24 — Secure internet access: no web fetch or external read tool — user item 2

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: there is no web fetch or external read tool of any kind and
  no egress policy; the architecture is local-only (clients → ADA HTTP → local
  Ollama/PostgreSQL; no native client ever contacts Ollama/PostgreSQL directly).
  Phase 19B plans "one selected external integration" (e.g. read-only calendar)
  but not general safe web access.
- User impact: ADA cannot look anything up on the internet for the user.
- Linked plan: F-4 (becomes the first "selected external integration" of
  Phase 19B).
- Next action: select F-4 with a pilot domain allowlist.

### G-25 — Always-on + "dreaming mode": no scheduler, no background thinking — user item 3

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: no durable scheduler exists anywhere in `src/ada` (grep for
  scheduler/idle/dream finds only `IDLE_MS` in `expression.py`, a session-tone
  expiry constant). Phase 19B explicitly states scheduled/proactive actions
  "require a separately implemented durable schedule, timezone, consent,
  expiry/revocation and job receipt"
  (plans/phase-19-edge-and-external-integrations.md). There is no idle
  detection, no background thinking jobs, and the server is a manually
  started loopback Uvicorn process (`scripts/start.ps1` — no Windows
  service/watchdog/auto-restart).
- User impact: ADA only works while the user has started it and is talking to
  it; nothing happens while the user is away.
- Linked plan: F-6 (always-on + dreaming; implements the Phase 19B durable-
  schedule prerequisite).
- Next action: select F-6 with a v1 job subset.

### G-26 — ADA proactively curious / asks the user personal questions — user item 4

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: no ADA-initiated conversation or question feature exists or
  is planned. Existing passive building blocks: Phase 13 source-linked
  episodes/continuity, Phase 15 opt-in learning, Phase 11 review inbox. This is
  a private single-user platform and the user has said deeper personal
  questions are acceptable — but plans/AGENTS.md and the Phase 14/15
  constraints still forbid automatic mood classification, learned
  relationship profiles or psychological scoring, so the design must stay
  evidence-grounded and user-controlled.
- User impact: the user must carry the entire conversation; ADA never
  initiates.
- Linked plan: F-5.
- Next action: select F-5 (opt-in curiosity, review-inbox delivery).

### G-27 — Small on-device LLM for more natural TTS/STT — user item 5

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: current voice uses only the platform on-device recognizer
  and installed offline TTS voices (G-22); there is no small on-device LLM in
  the voice path. Phase 19A (on-device model assistance) targets
  intent suggestions/drafts, not voice naturalness. The user perceives current
  voice as robotic.
- User impact: voice interaction sounds machine-like and STT quality is
  platform-dependent.
- Linked plan: F-3 (measured platform-model track first; optional small-LLM
  track after S24 FE benchmarks).
- Next action: select F-3.

### G-28 — Username/password instead of tokens — user item 6

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: only CLI-issued random bearer tokens exist
  (`ada create-user` / `ada rotate-token`; README). No username+password
  login and no signup flow anywhere (grep "password" in `src/ada` matches
  only the backup-encryption helpers in `operations.py`). The user wants
  simple username/password "for now" (single local operator, private network).
- User impact: normal logins depend on manually handed over bearer tokens.
- Linked plan: F-2.
- Next action: select F-2 (passwords alongside tokens, not replacing them).

### G-29 — Device connectivity on same Wi-Fi / Tailscale VPN — user item 7

- Date logged: 2026-10-15. Status: Open.
- Evidence/source: the API binds loopback only (`scripts/start.ps1`); Android
  debug allows only loopback/emulator hosts and release requires verified TLS
  (which does not exist yet — G-06). Phase 18B's private-VPN + trusted-cert
  Caddy runbook is the closest existing artifact but is unverified and has no
  first-class LAN/Tailscale connection flow, configuration UX, or discovery.
- User impact: the phone cannot reach the server from the couch/another room
  today.
- Linked plan: F-1.
- Next action: select F-1 (Tailscale recommended; same-Wi-Fi TLS as alternative).

## Section D — Future plan proposals

Nothing below is authorized. Each item is a proposal with goal, high-level
scope, hard invariants, prerequisites, a phasing/checkpoint outline, open
questions for the user and dependency notes. Example commands are **PROPOSED**
and must be labeled and verified when their implementation is created
(plans/AGENTS.md). Migration proposals are additive after the current head
0015 with populated-upgrade tests (plans/STANDARDS.md).

### Recommended sequencing

1. **F-0 first** — close known gaps: verification + one authorized
   installation, no new feature code.
2. **Track A — daily usability**: F-1 connectivity, F-2 login, F-3 voice.
3. **Track B — smartness**: F-4 internet, F-5 curiosity, F-6 dreaming/
   always-on, F-7 quality program.
4. **Track C — operational maturity**: F-8 backups/retention/capacity,
   interleaved with Tracks A/B.
5. **Optional, only on explicit selection**: F-9 shared scopes, F-10 further
   external integrations, F-11 iOS, F-12 non-voice on-device drafts.

### F-0 — Close the known gaps (P0; verification + authorized install; no new feature code)

- Goal: bring the running system to what source already implements and close
  the paused verification gates.
- Scope outline:
  1. Authorized installation: verified encrypted backup (Phase 18C on-demand
     backup), then upgrade the configured application database from observed
     head 0005 to head 0015. The PROPOSED upgrade command (run against the
     configured DB only after the backup is verified):
     `.\.venv\Scripts\python.exe -m alembic upgrade head`
     Then restart, `/v1/capabilities` + readiness check, old-conversation
     replay smoke.
  2. Resume and finish the paused Phase 17-A gates (G-02) and Phase 18 gates
     (G-03), including the audible full-focus interruption trial and
     Caddy/private-HTTPS validation (also closes G-06 in part).
  3. Physical S24 FE full-feature matrix + release app build 0.18.0-security
     on device (G-05), manual TalkBack/IME (G-07), strict cold-launch rerun
     (G-04).
  4. Housekeeping: clean retained synthetic fixture directories (G-10).
- Hard invariants: backup before migration; the configured upgrade is
  installation scope, not a test-session action (STANDARDS "Existing backend
  commands"); no later phase or deployment; one Uvicorn worker retained.
- Prerequisites: user authorizes the live-database upgrade window (open
  question); S24 FE reconnected; no code changes expected.
- Phasing: (a) backup + upgrade + replay smoke; (b) 17-A/18 gate completion;
  (c) physical matrix + release install; (d) housekeeping.
- Open questions: confirm the user authorizes the live-database upgrade window
  (it is an installation and requires explicit approval per repo rules).
- Dependency notes: F-0 closes G-01…G-10 (partially G-06/G-09) and is the
  prerequisite for any Track A/B work that needs a current target system.

### F-1 — Private-network device connectivity (user item 7; closes G-29; builds on G-06 / Phase 18B runbook)

- Goal: the phone connects to the ADA server when on the same Wi-Fi or over a
  Tailscale VPN, always over trusted TLS, never cleartext.
- Scope outline: server side — optional non-loopback bind behind an explicit
  config gate + verified Caddy (or Tailscale Serve) TLS termination per the
  Phase 18B runbook; client side — Android private-network server URL + trust
  path (release TLS verification, no cleartext exceptions), connection settings
  UX, capability-gated LAN/Tailscale hints; documentation with exact
  Windows/Tailscale steps; physical verification on the S24 FE over both
  same-Wi-Fi (TLS) and Tailscale.
- Hard invariants: no CORS enablement; PostgreSQL/Ollama ports never exposed to
  the network (STANDARDS client rules: clients never contact database/Ollama
  ports); no provider/database client in the app; loopback remains the default;
  admin web uses the same origin; tokens remain bearer (F-2 may add a session
  credential but never weakens authorization); no remote admin enrollment
  (G-21 stays).
- Prerequisites: F-0 item 2 (Caddy syntax + actual private HTTPS validated);
  a chosen transport (open question).
- Phasing: (a) server TLS termination verified on the laptop; (b) Android
  connection settings + release TLS path; (c) same-Wi-Fi physical test;
  (d) Tailscale physical test + docs.
- Open questions: Tailscale (recommended — encrypted by default, stable
  identity) vs plain Wi-Fi TLS; do you want same-Wi-Fi at all given the
  laptop's firewall, or Tailscale-only?
- Dependency notes: independent of F-2/F-3; pairs with F-2 so a new login
  credential works over the same transport.

### F-2 — Username/password sign-in (user item 6; closes G-28)

- Goal: simple username + password login for the user's accounts on the private
  network, replacing manual token hand-off for normal use.
- Scope outline: new additive migration after 0015 (PROPOSED — not implemented)
  storing argon2id/scrypt password hashes (never plaintext, consistent with the
  existing hashed-credential posture); a POST sign-in endpoint issuing
  short-lived session credentials (or reusing Phase 18 device-credential
  enrollment for Android); explicit no-public-signup default (accounts still
  created by the local operator CLI; private-network self-enrollment default-
  off); rate limiting and lockout via the existing Phase 18 owner/global rate
  bounds; token compatibility — existing bearer tokens keep working (CLI, admin
  web, legacy).
- Hard invariants: server-enforced authorization unchanged; owner IDs come from
  the authenticated principal, never from input JSON (STANDARDS authority
  rules); an admin role is enforced by the server and is NEVER granted by
  login, username or personality (root AGENTS.md); no passwords in logs,
  errors, contracts or fixtures (root AGENTS.md; STANDARDS sanitization);
  Android Keystore storage of the session credential (STANDARDS client
  behavior); 401 fences stop client retries (STANDARDS).
- Prerequisites: F-0 (installed system to verify against) recommended;
  F-1 for the private-network transport (or loopback first).
- Phasing: (a) migration + password hashing + sign-in endpoint with failure
  tests; (b) Android sign-in flow + Keystore storage; (c) admin web unchanged-
  token compatibility check; (d) physical verification.
- Open questions: add password alongside tokens (recommended) or replace for
  normal users; where should accounts be created (CLI only vs opt-in
  private-network self-enrollment); session lifetime.
- Dependency notes: must not alter Phase 18 device-credential semantics;
  pairs with F-1.

### F-3 — More natural on-device voice (user item 5; closes G-27; extends Phase 17/17-A, touches the Phase 19A boundary)

- Goal: STT and TTS that sound and behave less robotic, still 100% on-device,
  still review-before-send.
- Scope outline (two measured tracks; decide after S24 FE benchmarks):
  (a) Platform track — download/update higher-quality offline ASR and TTS
  language models on-device (the API31+ on-device factory already supports
  installed models), voice/rate tuning UI, better endpointing;
  (b) Optional small-LLM track — a small on-device model (license/quantization
  verified per Phase 19A rules) used ONLY for voice-facing text adaptation:
  rephrasing the completed server reply into concise spoken form, or polishing
  ASR transcripts before the review screen. The server reply remains the
  authoritative event; on-device LLM output is a labeled generated draft and
  never silently becomes user evidence or a server response (Phase 19A
  proposal/lineage contract).
- Hard invariants: no audio upload (`voice_audio_uploads` stays false); no
  network fallback for ASR; reviewed-endorsement lineage preserved (Phase 17
  fingerprint domain); TTS playback controls remain independent of server
  generation cancellation (Phase 17 rules); text chat always available without
  mic/ASR/TTS (capability gating, STANDARDS).
- Prerequisites: F-0 (finished 17-A gates, current release build on device);
  F-2/F-1 if voice is exercised over the network transport.
- Phasing: (a) S24 FE baseline benchmarks (STT word errors, TTS
  perceptibility, battery/thermal); (b) platform model updates + tuning UI;
  (c) re-benchmark; (d) decide on the small-LLM track with a separate
  checkpoint and proposal review.
- Open questions: which track first (recommended: platform model updates +
  tuning, measure on S24 FE, then decide on small-LLM); which languages;
  battery/thermal budget.
- Dependency notes: the small-LLM track is the only piece shared with F-12;
  keep the Phase 19A boundary explicit if it is selected.

### F-4 — Secure internet access (user item 2; closes G-24; becomes the first "selected external integration" of Phase 19B)

- Goal: ADA can read the internet for the user while the user's private data
  never leaves the machine uncontrolled and the web can never grant ADA
  authority.
- Scope outline: server-managed read-only web-fetch tool registered under the
  existing Phase 12 approval protocol (exact preview, explicit per-request
  approval, durable receipts); domain allowlist/denylist policy (start small,
  e.g. documentation sites); a request builder that strips private content —
  no memory/claims/scope text/conversation content in outgoing queries;
  bounded response size/time/depth; fetched content is imported untrusted
  evidence (document-style D cards, hash + version snapshot, no claim
  promotion); full egress audit trace (URL, tool, approval, size, time) visible
  to the owner; explicit user intent required for any future write integration
  (Phase 19B rules); no admin-role reuse for external actions.
- Hard invariants: "Model output is not factual authority or authorization"
  (root AGENTS.md); retrieved web text is untrusted display/evidence data
  (STANDARDS provenance); no network calls inside open DB transactions (root
  AGENTS.md; STANDARDS); shared process admission — one worker (STANDARDS);
  no credentials/keys sent to third parties; no external messages authorized
  by this plan (root AGENTS.md).
- Prerequisites: F-0; a pilot domain list (open question).
- Phasing: (a) egress policy + request-builder invariants with failure tests;
  (b) fetch tool under Phase 12 approval/receipts; (c) untrusted-import D-card
  path + egress audit; (d) 2–3 pilot domains, physical verification.
- Open questions: which first domain(s)/services (recommended: 2–3 read-only
  documentation/API services as the pilot); per-request approval (recommended)
  vs per-session allowlist; cache policy.
- Dependency notes: this is the template for F-10; any write integration stays
  out of scope here.

### F-5 — Proactive curiosity: ADA asks about you (user item 4; closes G-26; depends on F-6 scheduler or at least the explicit review inbox)

- Goal: ADA carries the conversation by raising grounded questions about the
  user — opt-in, bounded and fully private.
- Scope outline: a curiosity generator that produces question DRAFTS strictly
  grounded in the user's own exact saved evidence (e.g. an entity with missing
  attributes, a pending Phase 11 proposal, a superseded/stale claim, an
  unanswered open thread from an episode); questions are delivered as explicit
  notifications/drafts in a review inbox (Android + admin-visible metadata
  only) and only become chat turns when the user accepts/opens them — never
  auto-sent; scope-level opt-in/opt-out, daily cap (proposed: 1–2 per scope per
  day), pause/reset consistent with Phase 15 semantics; question lineage
  records the exact source links (C-card style) so every question is
  inspectable.
- Hard invariants: NO mood classifier, NO learned relationship
  profile, NO psychological scoring (Phase 14/15 boundaries; plans/AGENTS.md
  privacy rules); questions may only reference evidence the owner can see;
  model imagination is not a source — if no evidence, no question (root
  AGENTS.md model-trust rule); personality changes expression only, never the
  curiosity authority or scope (root AGENTS.md); erasure (Phase 18) covers
  generated question records; admin sees counts only (STANDARDS admin rules).
- Prerequisites: F-0; F-6 scheduler for timed delivery (or review-inbox-only
  delivery without a scheduler).
- Phasing: (a) evidence-scanner invariants (missing attribute, pending
  proposal, stale claim, open thread); (b) draft generation + lineage +
  review-inbox delivery; (c) opt-in/cap/pause/reset controls; (d) physical
  verification + erasure coverage check.
- Open questions: allowed question topics (work projects vs personal life vs
  both); delivery channel (notification vs inbox only); default on or off
  (recommended: off until the user enables it).
- Dependency notes: builds on Phase 11/13/15 artifacts read-only; its dream-
  job variant is one of F-6's rotation jobs.

### F-6 — Always-on operation + "dreaming mode" (user item 3; closes G-25; implements the Phase 19B "durable schedule" prerequisite)

- Goal: ADA keeps running on the Windows laptop (always-on) and — when the
  user is idle — runs bounded background "dream" consolidation (dreaming).
- Scope outline: (a) always-on — a Windows service wrapper (e.g. NSSM or a
  scheduled task — PROPOSED, verify docs at implementation time) managing the
  existing one-worker Uvicorn + doctor health probe + automatic restart,
  startup at logon, graceful shutdown, with watchdog metrics exposed to admin
  monitoring; (b) dreaming — when the user is idle (no in-flight requests, no
  active conversation for a configurable window, machine not in
  battery-critical/thermal state), a bounded background "dream" worker runs a
  rotation of explicit consolidation jobs: (1) episode summaries (Phase 13),
  (2) pending memory-proposal extraction from recent approved sources
  (Phase 11), (3) lexical/embedding index rebuilds (Phases 2/10),
  (4) contradiction/staleness scan over valid-time claims (report-only),
  (5) curiosity question drafts (F-5), (6) backup freshness check (F-8).
- Hard invariants: one durable schedule with timezone, consent, expiry/
  revocation and job receipts (Phase 19B requirement, quoted in G-25); shares
  the existing process admission — NO extra inference process while the one-
  worker rule stands (root AGENTS.md; STANDARDS); no model calls inside
  transactions (root AGENTS.md); all dream outputs are proposals/drafts/
  reports only — nothing is auto-published, auto-approved or auto-deleted;
  exact source lineage and request-frozen semantics preserved; dream runs are
  idempotent, leased and fenced like Phase 13 jobs; user-visible "what ADA
  thought about while you were away" review screen; global kill switch;
  respects device-credential revocation and privacy epochs (Phase 18).
- Prerequisites: F-0; F-5 for the question-draft job (or that job deferred);
  F-8 for the backup-freshness job (or that job deferred).
- Phasing: (a) always-on service wrapper + watchdog metrics; (b) durable
  schedule primitive (timezone/consent/expiry/receipts) with invariants;
  (c) dream worker with v1 job subset; (d) review screen + kill switch;
  (e) long-run verification.
- Open questions: which job subset for v1 (recommended: episodes +
  contradiction scan + question drafts); idle definition; max nightly
  runtime/GPU budget.
- Dependency notes: the Phase 19B durable-schedule primitive also unblocks
  F-10's scheduled/proactive actions.

### F-7 — Quality & smartness program (user item 1; closes G-23; overlaps G-12/G-14/G-18)

- Goal: make "smart" measurable and improvable, not aspirational.
- Scope outline: (1) real-model evaluation harness — representative private
  corpora (user-authorized) for retrieval recall/MRR, extraction precision,
  summary faithfulness, preference accuracy (closes the "representative
  evaluation" gates pending since Phases 10–15); (2) embedding activation
  decision — download the embedding model, run the real quality/resource
  measurements Phase 10 explicitly deferred, then enable or document-disabled
  with evidence; (3) automatic extraction behind review — extend Phase 11 from
  selected-source to auto-suggested-on-completed-turns, still with the
  mandatory human review gate (the `automatic_memory_extraction` capability
  flag flips only with evidence); (4) relative date parsing beyond "as of
  YYYY-MM-DD" (G-18); (5) contradiction handling beyond conservative grouping;
  (6) PDF/OCR document ingestion (the deferred Phase 08 checkpoint, G-14) so
  ADA can actually digest the user's files.
- Hard invariants: model output never becomes factual authority (root
  AGENTS.md); review gates stay human (Phase 11); evaluation must distinguish
  fixture vs real-model runs (STANDARDS phase-completion rule); new migrations
  only after 0015 with populated-upgrade tests (STANDARDS).
- Prerequisites: F-0 (installed, current system to evaluate); user-authorized
  evaluation corpus (open question).
- Phasing: (a) evaluation harness + baseline measurements; (b) embedding
  model download + real measurements + activation decision; (c) auto-
  extraction behind review with invariants/failure tests first; (d) date
  parsing + contradiction improvements; (e) PDF/OCR ingestion checkpoint.
- Open questions: which evaluation corpus to start with; is the user OK with
  periodic real-model benchmark runs consuming GPU time.
- Dependency notes: (2) and (3) each flip a capability reported by
  `/v1/capabilities`; (6) is a separate, larger checkpoint that may warrant its
  own phase file.

### F-8 — Operational maturity (closes G-08/G-09 and part of G-17)

- Goal: make the installed system operationally safe to leave running.
- Scope outline: (1) scheduled automatic encrypted backups — extend Phase 18C
  with a leased, receipted, retention-bounded schedule (e.g. daily, keep N) so
  the data-loss boundary is no longer "last committed snapshot"; (2)
  retention/age policy decision (currently retain-until-deletion, G-17) —
  document a chosen policy for snapshots/checkpoints; (3) real-data sizing/
  capacity measurements (the 0.516 s/1.25 s drill was a small fixture);
  (4) multi-worker shared admission design (prerequisite for scale-out; one
  worker remains until then); (5) GPU/throughput metrics for admin monitoring
  (safe, metadata-only probes); (6) sustained load testing protocol.
- Hard invariants: backups encrypted (AES-256-GCM/scrypt) to the selected
  local directory; schedules are leased/fenced/receipted like Phase 13/18
  jobs; admin monitoring stays metadata-only (STANDARDS); no live secrets in
  metrics/logs (STANDARDS sanitization); retention changes require an explicit,
  audited policy decision, not silent deletion.
- Prerequisites: F-0 (installed system); F-6's durable schedule for (1) if it
  lands first, otherwise a minimal scheduled task (PROPOSED).
- Phasing: (a) backup scheduling + retention + drill at real data size;
  (b) retention policy decision recorded in DECISIONS + docs; (c) sizing/
  load protocol + GPU/throughput probes; (d) multi-worker admission design
  (design-only checkpoint).
- Open questions: backup cadence/retention N; which metrics are acceptable in
  admin monitoring.
- Dependency notes: F-6's backup-freshness job plugs into (1).

### F-9 — Shared scopes & membership grants (closes G-15) — optional

- Goal: let the user share a project scope's knowledge with another person.
- Scope outline: only if the user ever wants shared project knowledge with
  another person; requires its own authorization design (deferred in
  docs/ARCHITECTURE.md): explicit membership grants, server-enforced scope
  checks, separate credentials, audit, and erasure interplay.
- Hard invariants: grants are server-enforced and explicit; personality never
  grants access (root AGENTS.md); all existing owner/scope/time filters remain
  (STANDARDS); additive migration after 0015 with populated-upgrade tests.
- Prerequisites: F-0; an explicit user request (single-user today).
- Phasing: design checkpoint first (authorization model + invariants), then
  implementation only if selected.
- Open questions: who is the second person; what may be read vs written in a
  shared scope.
- Dependency notes: none of Tracks A–B require this.

### F-10 — External integrations beyond web + durable-schedule products (Phase 19B continuation) — optional

- Goal: one selected integration at a time, plus scheduled/proactive actions.
- Scope outline: e.g. a read-only calendar lookup, each with provider
  receipt/idempotency under the Phase 12 approval protocol; scheduled/proactive
  actions with consent/expiry per Phase 19B rules on F-6's durable schedule.
- Hard invariants: F-4's invariants carry over (untrusted external data,
  approval protocol, no credentials to third parties, no external messages
  without explicit request); one integration at a time; additive migrations
  only after 0015.
- Prerequisites: F-4 (web template) and F-6 (durable schedule) as applicable.
- Phasing: per-integration checkpoints, each starting with an invariants/
  failure-test checkpoint.
- Open questions: which integration next after the web pilot.
- Dependency notes: this is where F-4's template gets reused.

### F-11 — iOS client (optional; closes G-20)

- Goal: an iOS client for the same authenticated HTTP contract.
- Scope outline: reuse the same authenticated HTTP contracts; separate effort,
  lower priority; same client invariants as Android (Keychain storage, no
  provider/database bypass, capability gating, review-before-send).
- Hard invariants: STANDARDS client rules apply unchanged; no new server
  authentication scheme is introduced for it (a frontend client may need a
  typed contract from prior phases but does not authorize a new auth scheme —
  CODEX-WORKFLOW).
- Prerequisites: F-1 (trusted transport) and F-2 (password sign-in) strongly
  recommended first.
- Phasing: scaffold + connection/auth checkpoint before any feature screen.
- Open questions: is iOS worth the effort before other items.
- Dependency notes: independent of Tracks B/C.

### F-12 — On-device model assistance for non-voice drafts (Phase 19A continuation) — optional

- Goal: on-device model assistance for intent suggestions/drafts outside the
  voice path.
- Scope outline: only if the S24 FE measurements from F-3 justify it; same
  Phase 19A proposal/lineage contract — on-device output is a labeled
  generated draft, never a server response or user evidence.
- Hard invariants: license/quantization verified per Phase 19A rules; no
  audio involved; capability-gated; no extra inference process beyond shared
  admission accounting.
- Prerequisites: F-3 measurement results.
- Phasing: design + license checkpoint, then one bounded feature.
- Open questions: which draft feature (intent suggestion vs query completion).
- Dependency notes: shares hardware budget with F-3 on-device models.

## Keeping this log up to date

- New gaps are appended with the next free G-xx ID (next free after this
  document: **G-42**), date, status (Open/Closed), source evidence, user
  impact, linked F-xx and next action.
- When a gap is closed, do not delete it — flip status to Closed with the date
  and an evidence pointer (preserve history, per repo rules).
- Distinct states always: Planned / Implemented in source / Locally checked /
  Target-verified / Installed.
- No credentials, tokens, raw private conversations, source quotes or hidden
  model reasoning in this file (root and plans AGENTS.md).
- Proposed commands and CLI names are labeled PROPOSED until implemented, and
  are verified when their implementation is created (plans/AGENTS.md).
- Every future-plan proposal gets concrete inputs, checkpoints, data/
  interfaces, failures, tests and exit criteria before work starts
  (plans/AGENTS.md); compilation alone does not prove a product flow works.
- Record implemented behavior, checks actually run, skips and unresolved
  limits in STATUS.md and WORKLOG.md; preserve prior validation evidence
  instead of rewriting it as a new run (root AGENTS.md).

## 2026-10-16 review — corrections and Phase 20 onward

Planning review against `fa2cbba`, actual 96-path/132-schema OpenAPI, 15 migrations
and selected relevant source/tests. No live DB, phone, iOS, inference or test suite
was run. This is an evidence-backed roadmap review, not an exhaustive code/security
audit. Existing successful tests are historical evidence only.

### Corrections to the original assessment

- G-01: 0005 is a historical observation, not freshly checked current state. A 0005
  installation already includes Phase 08 documents. Do not claim all 08–18 features
  absent; compare source/install versions when installation is actually selected.
- G-06/G-29/F-1: Android already accepts valid HTTPS origins (`ConnectionCredential`
  in `AdaApi.kt`). The missing piece is a demonstrated trusted/private endpoint
  and usable setup/diagnostics, not permission for arbitrary LAN HTTP. Keep API
  loopback behind a proxy; a public/non-loopback API bind is unnecessary.
- G-23/F-7: five evaluation programs already exist in `scripts/evaluate_*.py`.
  Missing is a representative combined regression/usefulness program and measured
  configuration decisions, not all evaluation. Split PDF expansion from ranking.
- G-25: `ConsolidationService` already has a background worker for explicit jobs.
  Missing are unattended supervision, durable scheduling, consented automatic
  selection and foreground priority. These are separate phases, not one new daemon.
- G-28: current authentication includes Phase 18 digest-only device credentials as
  well as CLI tokens. Password login is a new front door, with sessions still
  required internally. It must work in admin web as well as Android.
- G-16/G-17/G-19/G-21 are decisions/boundaries, not necessarily defects: RLS is an
  optional defense-in-depth decision, chosen retention stays until explicit owner
  deletion, automatic mood inference remains absent, and local admin grants stay
  separate from login. No reopened retention decision or remote grant UI is required.
- F-0's 0015-only encrypted backup cannot protect an old 0005 database unchanged
  (G-30). Physical 17-A validation/live installation need not block independent
  current-schema development. New Phase 20 replaces that blanket prerequisite.
- F-4 cannot promise zero disclosure: approved query/URL and network metadata leave
  the server. Store detailed owner research receipts privately; do not log full
  URLs/queries as ordinary telemetry. Allowlist plus a prompt filter is insufficient.
- F-5 needlessly restricts new-owner conversation: a generic personal question
  needs no saved evidence. Personalized assertions/premises do. Owner chose all
  three channels, with staged implementation and per-channel consent/settings.
- F-3's optional text LLM may adapt wording; speech-specific ASR/TTS models are
  the primary quality route. Device licensing/resource/quality evidence is still
  required before activation, deliberately outside this review.

### Mapping the original gaps

| Existing gaps | Disposition in this review | New phase(s) |
|---|---|---|
| G-01/G-03 | Non-device audit/recovery and separately selected live installation | 20; 21/26 operational routes |
| G-02/G-05 | Physical validation excluded; preserve current open status | Existing 17-A, no new blocking dependency |
| G-04/G-10 | Current emulator regression/hygiene; do not rewrite historical failures | 20 |
| G-06/G-29 | Trusted private transport and setup UX | 21 |
| G-07 | Browser/manual desktop part relevant; phone TalkBack deferred | 20 and affected client phases |
| G-08/G-09 | Host measurements, supervision, unattended encrypted recovery | 26; 27 trigger integration |
| G-11 | Conditional 19 is not a missing required release; split selected ideas | 24/27/29; others parked |
| G-12/G-18/G-23 | Measured relevance, dates, context and useful workflows | 20/23; optional 30 |
| G-13 | Selected-source review exists; automatic source selection is opt-in future work | 28, preserving 11 review |
| G-14 | Format expansion separate from answer ranking | Optional 31 |
| G-15/G-16/G-19 | Sharing/RLS/automatic affect not required for this roadmap | Parked/by design |
| G-17 | Preserve selected content retention; backup pruning is a separate choice | 26/28 storage limits |
| G-20 | iOS excluded | No new iOS phase |
| G-21/G-28 | Password login on both clients; admin grants remain local/server-enforced | 22 |
| G-22/G-27 | Speech architecture/model study now; physical activation later | 29 |
| G-24 | Approved public research with hard egress/privacy controls | 24 |
| G-25 | Separate uptime, schedules and idle reflection | 26/27/28 |
| G-26 | Natural questions, later inbox and scheduled initiated conversations | 25/27/28 |

### Additional gaps and prerequisite risks

All logged 2026-10-16; status **Open**. Items concerning future capabilities are
design risks to resolve before enabling them, not evidence of an existing exploit.

| ID | Finding and direct source evidence | Impact / next action | Plan |
|---|---|---|---|
| G-30 | `operations.backup` and `unpack` reject heads other than 0015; F-0 proposes using them before upgrading historical 0005 | Rehearse encrypted legacy export/restore or a separately tested native-dump path; do not upgrade first merely to enable backup | 20 |
| G-31 | Recovery manifest head checks and credential quarantine are 0015-specific; `inventory.content_tables` rejects unknown owner tables | Extend versioned backup/restore, authority quarantine, erasure inventory and client epoch handling with every new schema/session/job | 20 plus each later data phase |
| G-32 | `SecurityMiddleware` requires bearer authentication on every `/v1/` request before owner rate admission; `auth.py` has no password verifier | Add exact pre-auth routing, bounded body/hash/IP/account attempts, collision-safe identity migration and browser/native session recovery | 22 |
| G-33 | Closed calculator/memory/source registry has no network broker/egress approval or web evidence type | Control DNS/redirect SSRF, private query disclosure, response parsing/injection and exact owner-only saved web citations | 24 |
| G-34 | `operations.main` uses interactive `getpass`; no startup supervisor or unattended backup secret provider exists | Protected noninteractive secret retrieval, explicit destination identity, key recovery and DB/provider readiness are required before unattended backup/uptime claims | 26 |
| G-35 | Consolidation/proposals share a nonblocking process-local semaphore; no durable foreground priority or host idle/resource policy exists | Idle work could occupy the only slot while chat gets busy; require bounded cancellation/fairness, power/thermal checks and interference measurements | 26/28 |
| G-36 | Normal chat does not automatically select completed turns for proposals; generated summaries remain navigation | Automatic source selection needs separate opt-in, exact lineage/dedup and human review; reflection cannot become an implicit factual writer | 23/28 |
| G-37 | No topic/cadence/channel curiosity policy or question/dismissal lineage exists | Implement generic versus evidence-grounded questions, personal-topic controls and reliable skip/block; active chat needs no scheduler | 25 |
| G-38 | No durable occurrence/timezone/consent receipt or notification channel exists | Define DST/missed-run/duplicate/revocation behavior, durable inbox and honest delivery; an LLM reminder sentence is not a scheduled action | 27 |
| G-39 | `consolidation.py`: 100 jobs/100 contexts/500 index items; `proposals.py`: 100 extractions/400 proposals; backup 256 MiB cap | Recurring work can exhaust retained quotas: forecast growth, dedup and stop visibly; any archive/compaction/deletion policy preserves selected retention and receipts | 20/26/28 |
| G-40 | Current summaries retain obsolete blanket claims (architecture's early device-enrollment absence) beside later 18 sections; 17-A has unchecked implementation boxes after hardening | Reconcile current navigation/status with source while preserving dated history and remaining target evidence | 20 |

Confirmed choices: first host is the existing laptop kept on AC and awake;
curiosity should support active chat, an inbox and occasional initiated notices.
The everyday job shortlist is still provisional. No password was requested or
stored, no device inspected, no provider purchased or network service enrolled.
See [FUTURE-ROADMAP](FUTURE-ROADMAP.md) for dependencies, defaults and phase files.

## Phase 20 readiness disposition — 2026-10-16

This entry supersedes only the current disposition, preserving the original audit.
See [RELEASE-READINESS](../docs/RELEASE-READINESS.md) and STATUS/WORKLOG for checks.

| Gap | Current result / next gate |
|---|---|
| G-01 | Open installation gate: no live schema query or upgrade; concrete backup-first checklist now exists. Historical 0005 is not a fresh observation. |
| G-03/G-06 | Source/contract/history audit and real Caddy template/lab TLS checks complete; actual private-network/system-trusted deployment and real-data sizing remain separate. |
| G-04 | Current-build gate checked: three strict emulator COLD/Status-ok launches. Historical Phase 11 failure remains its own failed run. |
| G-07 | Real Chromium keyboard/contrast/zoom checks passed; manual assistive-technology review remains unrun. Physical TalkBack excluded. |
| G-08/G-09 | Fixture timings/limits recorded; sustained live capacity, supervised hosting and scheduled backups remain Phase 26 scope. |
| G-10 | Historical synthetic evidence retained deliberately; current owned fixture cleanup is recorded. No blanket Temp/cache removal. |
| G-30 | Implemented separate 0005 encrypted backup/isolated restoration and upgrade/replay drill. No available 0005 server checkout: exact old-server HTTP is still an explicit compatibility limit. |
| G-31 | Current 0005/0015 recovery policy and fail-closed inventory/version tests implemented. Every future head must explicitly extend quarantine/erasure/backup compatibility. |
| G-39 | Existing quotas/256 MiB limit retained and documented; no silent quota increase or age deletion. Recurring-work growth controls remain a future prerequisite. |
| G-40 | Current architecture/navigation and implementation versus target checklists reconciled. Dated older evidence remains historical. |

### G-41 — Emulator streaming/recovery verification intermittency — Open

Logged 2026-10-16 during Phase 20. Two isolated API37 streaming runs timed out;
added safe diagnostics identified `pending=Missing`, `fault=NotFound` before any
provisional text. An instrumented retry passed the eight-check suite and both OS
permission cases. Its subsequent combined force-stop stage failed without useful
stage output; a new focused `-RecoveryOnly` run with emitted stage diagnostics
passed both prepare/actual-force-stop/resume pairs and SecurityUI. No production
Android behavior was changed or root cause established. Passing reruns are not
proof of a fix; earlier failures remain in the log.

Next gate: before operational release, repeat under controlled host load and
capture fixed submission failure codes/state transitions plus fixture admission
metadata. Distinguish a rejected/unknown submission from observer timing and a
harness synchronization failure. Preserve exact UUID recovery; never auto-resubmit
as a test workaround. Safe diagnostic capture and a bounded recovery-only runner
are implemented; physical testing is not required for this emulator investigation.

Next free gap ID: **G-42**. No later feature phase was implemented.
