# ADA implementation verification and forward suggestions

**Proposals only** — this document records verification outcomes, documentation gaps, and forward-looking suggestions. Reading or adding this file does not authorize implementation, deployment, or operational changes. Keep the states of "planned," "implemented," "locally checked," and "target-verified" distinct. No commands or features listed here are implemented or verified unless explicitly marked as such.

## Verification outcome — Phases 02A–11 (2026-10-10)

A full working-tree verification confirmed that the working tree implements Phases 02A through 11, one phase beyond the previously claimed up to Phase 10. The implementation includes server, Android, admin web, and contract components as specified.

- **Server**: Migrations 0001–0008 form a linear additive chain. SCHEMA_HEAD = "0008" in `src/ada/schema.py`. Phase 02A includes a Windows path regression fix. Phase 05 adds six `/v1/admin/` GET routes with bounded windows, pagination, and cached Ollama health. Phase 08 implements seven document routes with strict quotas and parsing outside transactions. Phase 09 adds 13 entity routes with NFKC/casefold resolution and reversible merge/undo. Phase 10 includes `OllamaEmbeddingProvider` with digest checks and RRF60 lexical-first fusion. Phase 11 excludes pending proposals from factual retrieval and implements atomic review with same-key replay.
- **Android**: Version 0.11.0-review (versionCode 6) includes the proposal inbox and Keystore journal v5. All Phase 03–11 features are confirmed in code, including exact request journals, memory flows, and v1–v5 journal compatibility; Phase 11's final Android recovery stages remain to be recorded. The client uses only the ADA HTTP API.
- **Admin web**: Implements sign-in via `/v1/admin/me`, six admin GET routes, memory-only tokens, and bounded polling. Includes 52 unit and 6 Playwright e2e tests.
- **Contracts**: `contracts/openapi.json` covers 55 paths and generates types in `apps/admin-web/src/api/generated.ts` with drift check.

`/v1/capabilities` accurately advertises implemented features: `automatic_memory_extraction=false`, `semantic` disabled by default, `streaming/tools/edge_inference/shared_scopes=false`. No Phase 12–19 features are present.

## Gaps found

1. `plans/STATUS.md` states "final Android verification in progress" for Phase 11, but the detailed section records the 145-unit gate and 26-case emulator pass as completed; only the force-stop/cold-launch final outcome was pending.
2. The Android version bump to 0.11.0-review / versionCode 6 is in `apps/android/app/build.gradle.kts` but not recorded in `plans/STATUS.md` or `plans/WORKLOG.md` (last recorded: 0.9.0-entities / code 5).
3. Migrations 0007 and 0008 and the Phase 10/11 working tree are uncommitted.
4. The configured application database is at head 0005, but the current source requires 0008. Server readiness would return 503 against it.
5. `apps/android/app/src/main/java/dev/ada/assistant/ui/States.kt` still carries the Phase 03 `screenMap`/`Destination` list (Connect, Conversations, NewConversation, Chat, Sources, Memory, Settings), not extended for Documents/Entities/Proposals; live navigation uses `ChatState.kt` `ChatDestination`.
6. Admin web unit test count in source (52) matches the Phase 11 detail record but not the older Phase 06/08 table rows (45/51); point-in-time snapshots, no action required.
7. Physical Samsung S24 FE/Android 16, trusted release HTTPS, TalkBack/manual accessibility, and real-model quality/latency verification remain pending across Phases 03–11.
8. Phase 10 semantic retrieval remains disabled by default; the embedding model (`embeddinggemma:300m`) is not present locally.

## New suggestions

A. **Close the operational installation gap**: Back up the configured database, then run `alembic upgrade head` (0005 → 0008) as a separately authorized installation step. Verify `/v1/health` readiness and `/v1/capabilities` afterward. *Prerequisite: user authorization, verified backup.*

B. **Finish and record Phase 11**: Run/record the final Android force-stop recovery stages and strict cold launch, update the `STATUS` table row, record the 0.11.0-review / code 6 version, and commit the Phase 10/11 working tree. *Prerequisite: physical device access or emulator verification.*

C. **Real-model activation evaluation for Phase 10**: Pull `embeddinggemma:300m`, run hybrid evaluation on a representative authorized corpus, measure CPU/GPU memory and latency on the RTX 4090 Laptop / i9-14900HX / 32 GB machine, and only then flip `ADA_EMBEDDING_ENABLED` with digest pinned. Keep lexical fallback as the safety net. *Prerequisite: model download authorization, test corpus.*

D. **Physical target verification sweep**: One consolidated checklist pass on the S24 FE/Android 16 covering Phases 04/07/08/09/11 flows (connect, chat retry, memory write recovery, document upload, entity merge/undo, proposal accept/reject), plus real Ollama conversation with known evidence, TalkBack and API 26 behavior. *Prerequisite: physical device, trusted HTTPS setup.*

E. **Consider Phase 16 (streaming and cancellation)** as the next feature phase: It has the largest user-perceived-latency payoff, reuses durable request ID/retry machinery, and can follow after Phase 04. Phase 17 voice can follow.

F. **Consider Phase 18 (security and operations)** earlier: Documents, entities, and proposals have retained quotas but no deletion/retention/cleanup service. A bounded explicit user deletion/retention design (owner-scoped, audited) is a candidate proposal before heavy usage.

G. **Revisit exact-search scaling past 256 items only with measured load**: Phase 10 chose exact cosine over ANN/pgvector; keep that, but add a capacity note that item 257 triggers lexical fallback, and revisit ANN only if representative scope sizes exceed the bound.

H. **Minor cleanup candidates**: Extend the Phase 03 Android `screenMap` (or remove it) to current destinations; reconcile per-phase web unit counts in `STATUS` as historical snapshots.

I. **Documentation**: Add a short "Current implementation boundary" note to `README.md` or `plans/CURRENT-STATE.md` stating implementation now reaches Phase 11 (code + local checks) while the application database and target-device verification remain separate.

## Not authorized

Nothing in this document authorizes deployment, migration installation, model downloads, device actions, or implementation of later-phase features. Each suggestion requires a separate authorization and verification step before execution.