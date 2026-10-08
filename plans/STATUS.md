# Phase status

Recorded 2026-10-08. Update this file after implementation and verification.
“Planned” means a specification exists, not that code or a working UI exists.

| Phase | Status | Evidence / next gate |
|---|---|---|
| 00–02 | Implemented baseline | Packaged Linux run: 60 passed/50 skipped. User's Windows PostgreSQL run: 105 passed/3 fixture failures/2 skipped. Real chat reported by user. |
| 02A | Local checks passed; target closure pending | Linux: 61 passed/50 skipped; four installer tests passed; Ruff lint/format passed. Windows PostgreSQL rerun still needed. |
| 03 | Planned | Close 02A, type existing client responses, choose compatible tools and create scaffolds. |
| 04 | Planned | Phase 03 contract/scaffolds; emulator and physical-phone verification. |
| 05 | Planned | Phase 03; explicit server admin authorization. |
| 06 | Planned | Phase 05 metadata API; real browser/backend integration. |
| 07 | Planned | Phase 04; exact evidence and correction flows. |
| 08 | Planned | Phase 03/current Phase 2; safe versioned upload and provenance contract. |
| 09 | Planned | Phase 03/current Phase 2; scoped entity/alias migration. |
| 10 | Planned | Phase 08; scoped semantic quality measurements; Phase 09 for entity-aware work. |
| 11 | Planned | Phases 07/08; review-based promotion; Phase 09 for canonical links. |
| 12 | Planned | Phase 03 and relevant client; permission and receipt contracts. |
| 13 | Planned | Phases 08/11; durable consolidation jobs. |
| 14 | Planned | Phase 07; explicit preference and bounded session-state contract. |
| 15 | Planned | Phases 11/13/14; consent and provenance for learning. |
| 16 | Planned | Phase 04; stream/reconnect/cancel contract; Phase 06 for monitoring. |
| 17 | Planned | Phases 04/16; explicit audio/transcript boundaries. |
| 18 | Planned | Phases 05/06 and installed feature inventory; recovery/deletion/device credentials. |
| 19 | Conditional plan | Phases 12/18 plus measured device or selected integration requirements. |

Next selected implementation should be Phase 03 after the Windows fixture fix is
verified. Do not mark later phases started simply because their documents exist.
If work is incomplete, record the checkpoint and exact blocking condition; keep
the usable earlier feature active. Missing device/database checks stay visible.
