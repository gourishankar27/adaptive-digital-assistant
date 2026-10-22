# ADA Android App — Design Gap Report

> Verification update, 2026-10-18 (America/Phoenix): the original static audit below is retained as historical input. Some claims were corrected after source and native-device verification. See [section 8](#8-verified-follow-up-2026-10-18) for the implemented changes, qualified findings and remaining checks. The original REJECTED verdict is not a new device-test result.


- **Date:** 2026-10-18
- **Scope:** code-level audit of `apps/android` (Compose UI under `app/src/main/java/dev/ada/assistant/ui`, resources under `app/src/main/res`), compared against `docs/ANDROID-UI-REDESIGN.md` and `apps/android/README.md`
- **Method:** two independent audits (visual design critic + accessibility critic), each finding verified against source; WCAG contrast ratios independently computed (WCAG relative-luminance formula). No device/emulator run, no TalkBack session, no screenshots — those are listed in "Needed for the next pass".
- **App:** single Activity, minSdk 26, 15 destinations, 4 palettes × light/dark, theme centralized in `ui/Theme.kt`
- **Verdict:** REJECTED on both axes — gaps below. Severity: P1 = fix before next release; P2 = fix in follow-up.

## 1. Executive summary

Both auditors returned REJECTED. The app has a solid foundation (centralized tokens, complete 4-palette light/dark theme, good error focus-stealing and live regions in Chat/Memory, tappable-only voice controls, 48dp icon buttons, 265 test tags) but the design system was only partially rolled out: five coexisting card treatments, five selection-indicator patterns, four loading affordances, fragmented error states (one feature screen swallows faults silently, one leaks an exception class name), three destructive account actions with no confirmation, ~14 unlabeled progress indicators, ~60 sub-48dp buttons (concentrated on the most destructive screen), no dialog focus management, raw internal identifiers announced verbatim to screen readers, off-scale spacing literals in 7+ files, an off-palette teal app icon with no adaptive icon, and stale appearance documentation in both READMEs. Contrast: all text pairs pass WCAG AA (measured minimum 5.73:1); the one measured failure is the glass-edge outline at ~1.5:1 (below the 3:1 UI-component threshold).

## 2. Contrast verification (measured)

An initial hand-computed table flagged a P1 "Red palette light muted fails on tonal surfaces", but independent recomputation RETRACTS it. Final measured results (WCAG formula, verified):

- All muted/onSurfaceVariant text pairs pass 4.5:1 in every palette × mode. Measured minimums: Ambient light muted on surfaceContainerHigh 5.73:1; Red light muted on background 7.75:1, on surfaceVariant 6.42:1, on surfaceContainerHigh 6.23:1 (the retracted claim); Oxford light 7.45:1; Olive light 7.05:1; dark-mode minimums 7.2–7.9:1.
- Light error `#B3261E`: 6.13–6.20:1 on light backgrounds (passes). onErrorContainer pairs: 12.77:1 light, 7.24:1 dark (pass).
- Primary buttons: white-on-primary minimum Ambient 6.06:1 (Oxford 16.05, Red 17.66, Olive 9.33); dark ink-on-accent Ambient 6.53:1. All pass.
- Raw outline colors pass the 3:1 UI threshold everywhere (measured min: Olive light 4.12:1).
- Inverse pair: 5.69:1 (passes).
- **NEW measured failure:** glass-edge border (outline color at 32% alpha, `Theme.kt:131`) blends to 1.47–1.53:1 over the backgrounds of all four palettes in both modes — below the 3:1 UI-component threshold (WCAG 1.4.11 for borders that identify components). Tonal surface difference carries most of the separation; the 1dp "quiet edge" is not a reliable boundary. Fix: raise edge alpha to ~0.45–0.5 or rely on tonal step only (and document the choice).
- Note: disabled Send glyph (onSurface @ 38% alpha, `ChatIcons.kt:42`) measures roughly 1.5–2:1; disabled UI is WCAG-exempt, but consider ≥3:1 disabled ink for low-vision discoverability.

> **Caveat:** an automated PowerShell verification script produced garbage output (buggy luminance math) and was discarded; the table above is from a verified independent computation. After any palette tweak, re-measure the Red light and Ambient light muted pairs (closest historical calls).

## 3. P1 findings (fix before next release)

### 3.1 Destructive actions without confirmation

- "Log out / change server" and "Sign out all password sessions" fire on a single tap (`ChatApp.kt:836-837`). Sign-out-all is server-side, multi-device, near-irreversible; the only guard is adjacent prose (`ChatApp.kt:834`).
- Per-session "Revoke" in `PasswordSessionPanel.kt:22` calls revoke directly, no dialog.
- Every other destructive flow in the app uses an AlertDialog (`EpisodeScreen.kt:91`, `EntityScreens.kt:120`, `ProposalScreens.kt:94`, `DocumentScreens.kt:222`, `MemoryScreens.kt:316`, `LearningSettings.kt:50`, `SecuritySettings.kt:60`).

**Fix:** AlertDialog confirmation for sign-out-all and per-session revoke (strongly recommended for logout too), consistent with the app's existing pattern.

### 3.2 Fragmented, sometimes silent error states (design + a11y combined finding)

- Chat has the rich pattern: FailureNotice card with error container color, focus steal, `LiveRegionMode.Polite` (`ChatApp.kt:914-929`); Memory has the same (`MemoryScreens.kt:330-334`).
- `CuriosityScreen.kt` renders NO fault at all — `state.fault` is never referenced; a failed curiosity refresh/save is silent to every user.
- `ProposalScreens.kt:27` shows the raw exception class name: "The operation needs attention: ${it::class.simpleName}".
- `EntityScreens.kt:31` and `EpisodeScreen.kt:36` render bare red Text — no card, no focus, no live region.
- `LearningSettings.kt:24` and `ExpressionSettings.kt:36` replace `failure.message()` with generic fixed text ("The operation could not be confirmed…"), discarding the actual reason.
- ~10 more screens render fault/notice as plain Text without live regions (`EntityScreens.kt:31-32`, `DocumentScreens.kt:90-92`, `EpisodeScreen.kt:36-37`, `CuriosityScreen.kt:21`, `ResearchScreen.kt:27`, `AgentScreens.kt:23`, `SecuritySettings.kt:21`, `VoicePanel.kt:112` and `:131-132`, `ChatApp.kt:597` pending-phase title) — screen-reader users can fail an operation and never hear why.

**Fix:** one shared humanized fault/notice component (the FailureNotice pattern) with live region + focus steal, used by every controller; map every failure to user-readable copy; remove the class-name leak.

### 3.3 Raw internal state as primary user-facing text

- `ResearchScreen.kt:45` "State: ${run.state}", `:55` "Receipt: ${receipt.state}"; `AgentScreens.kt:40-54` raw status/failure-code/trust-class lines; `EpisodeScreen.kt:87` dialog title "Queue ${s.previewKind}" with raw enum (incl. `lexical_rebuild`); `LearningSettings.kt:92-96` and `ExpressionSettings.kt:47-62` dropdown options are raw enum values with only underscore replacement.
- Raw ISO-8601 timestamps announced verbatim: `Instant.ofEpochMilli(...).toString()` at `EpisodeScreen.kt:43-44`, `:66`, `:82`; `SecuritySettings.kt:34`; `LearningSettings.kt:80` — screen readers read "2 0 2 6 dash 1 0 dash…". The codebase already has a localized `displayInstant()` (used in `ChatSourceCard.kt:84-87`); these are the outliers. Raw UUIDs also surface: `AgentScreens.kt:36-39`; `ChatSourceCard.kt:70-79` (opt-in technical details — acceptable, keep opt-in only).

**Fix:** human labels for all states/enums (raw value in a "technical details" expander, the `DocumentScreens.kt:195` pattern — the one screen that does it), `displayInstant()` everywhere.

### 3.4 Fixed 600dp dialog height cap overflows short landscape windows

- CompactChatDialog caps content at `heightIn(max = 600.dp)` (`ChatApp.kt:491`). On short landscape windows (content ≈ 400–570dp) the conversation-details and message-options dialogs are taller than the screen; the dialog frame is clipped.
- Sibling dialogs do it correctly: `VoicePanel.kt:61-62` (`(maxHeight − 24dp).coerceAtLeast(96dp)` via `BoxWithConstraints`), `AppearanceSettings.kt:63` (`fillMaxHeight(0.9f)`).

**Fix:** constrain by actual available height (VoicePanel pattern).

### 3.5 Selection state is text-only (a11y)

- Five different selection patterns coexist, and the non-RadioButton ones have no machine-readable selected state: "✓" suffix (`CuriosityScreen.kt:37,46`; `VoicePanel.kt:146`), "(selected)"/"selected" suffix (`EntityScreens.kt:55`, `DocumentScreens.kt:102,126-127`, `ResearchScreen.kt:34-35`, `MemoryWindowPanel.kt:25`), "Selected:"/"Replacement selected" prefix (`EntityScreens.kt:89`, `ProposalScreens.kt:58,75`), plus two radio-row variants (`ChatApp.kt:948`, `MemoryScreens.kt:344-348`). TalkBack never announces "selected"; "✓" reads as "check mark". A screen-reader user can save the wrong curiosity topic, entity kind, or media type.

**Fix:** `Modifier.selectable(selected, role = Role.RadioButton)` / `stateDescription` everywhere; one selection pattern app-wide.

### 3.6 Unlabeled progress indicators + oversized-below-minimum touch targets (a11y)

- ~14 bare progress indicators with no label/contentDescription: `EntityScreens.kt:33`; `DocumentScreens.kt:110,164,182,214`; `EpisodeScreen.kt:35`; `CuriosityScreen.kt:22`; `ResearchScreen.kt:28`; `AgentScreens.kt:24`; `LearningSettings.kt:23`; `ExpressionSettings.kt:34`; `ProposalScreens.kt:26`; `MemoryWindowPanel.kt:33`. The labeled pattern already exists (`FoundationScreen.kt:82`, `MemoryScreens.kt:382`, `ChatApp.kt:610`).
- ~60 inline TextButtons lack the 48dp minimum (`Modifier.heightIn(min = AdaSpacing.touch)` is the established repo pattern and is missing on): `SecuritySettings.kt:22,24,28,37,38,43,49,54,55,59,62,63` (the whole revoke/rotate/delete-confirm flow); `CuriosityScreen.kt:40,46,48-51,56,57,72,83,84,88,91,93-96,100,102`; `EntityScreens.kt:50,74,90,117-118`; `DocumentScreens.kt:105,112,179,184,222-225`; `EpisodeScreen.kt:47,90`; `ResearchScreen.kt:22-23,34-35,43,56,59,63,71,73,74,78`; `AgentScreens.kt:65`; `ProposalScreens.kt:57,62,76,83,93-94`; `LearningSettings.kt:53`; `MemoryWindowPanel.kt:52`.

**Fix:** one shared labeled loading component; apply the 48dp minimum everywhere, starting with SecuritySettings and the Curiosity question-card action row (adjacent targets need spacing so they don't crowd).

### 3.7 Token discipline not applied (violates `docs/ANDROID-UI-REDESIGN.md:61-62`)

- `Theme.kt:20-22` defines `AdaSpacing` (4/8/16/24/32dp, touch 48dp) and `AdaLayout`, but off-scale 12dp/14dp literals appear in 7+ files: `EpisodeScreen.kt:31,53,64,69`; `VoicePanel.kt:163`; `ProposalScreens.kt:41`; `ChatApp.kt:685,952`; `AgentScreens.kt:29`; `LearningSettings.kt:39,43,84`; `ExpressionSettings.kt:30,67`.
- ~15 raw `48.dp` occurrences in `VoicePanel.kt` (`:98,99,109,113,114,119,124,126,132-134,141,146,148,151`) instead of `AdaSpacing.touch`; magic numbers 120/170/200dp and 600dp in `ChatApp.kt:653,439,449,491`.

**Fix:** use tokens; add a lint/test rule banning raw `N.dp` literals in `ui/` (or a ktlint custom rule).

### 3.8 Stale appearance documentation contradicts shipped code

- `apps/android/README.md:85-95` lists only three palettes, says Oxford Blue is the default, "new installations start with Oxford Blue in light mode", fallback = Oxford Blue. Root `README.md:313` says "Oxford Blue is the default palette."
- Shipped code: AmbientViolet is the default palette, dark is the fresh-install default, fallback is AmbientViolet (`Theme.kt:25,31`; `AppearanceSettings.kt:37,45`). The same Android README's intro (lines 5-12) was updated — the file is internally inconsistent.

**Fix:** rewrite the Appearance section of `apps/android/README.md` and root `README.md` line 313.

## 4. P2 findings

### 4.1 Visual consistency (design system not fully rolled out)

- **Five card/panel treatments** for the same content kinds: `AdaGlassSurface` (`AmbientComponents.kt:80-84`), `Card`/surfaceContainerLow (`ChatApp.kt:279-282`, `937-944`), bare default Card (`EpisodeScreen.kt:53,64,69`; `EntityScreens.kt:36,66`; `CuriosityScreen.kt:54,70,78`), borderless Surface/ChoiceRow (`ChatApp.kt:949`; `AppearanceSettings.kt:77-81`), and MemoryQuote Surface/surfaceContainerHighest (`MemoryScreens.kt:367-372`) — fix: one AdaCard composable with variants; reserve glass for composer/pending/dialog chrome.
- **Four loading affordances:** `BusyIndicator` (`ChatApp.kt:964-969`), bare LinearProgressIndicator, bare unlabeled CircularProgressIndicator, `MemoryProgress` (`MemoryScreens.kt:379-385`) — fix: one labeled component (pairs with 3.6).
- **Heading size drift:** 24sp conversation list (`ChatApp.kt:255`) vs 26sp `AdaSectionHeading` vs 20sp toolbar (`ChatApp.kt:463`) and `ExpressionSettings.kt:21` vs 18sp sibling settings sections (`LearningSettings.kt:18`, `SecuritySettings.kt:19`, `PasswordSessionPanel.kt:16`) — fix: pin screen=26 / section=18 / field-group=16 in one composable.
- **Two hand-drawn Canvas icon families:** `AdaIconGlyph` 1.8dp round cap (`ChatIcons.kt:64,66`) vs `NavigationGlyph` 1.7dp butt cap (`ChatApp.kt:977`) — fix: unify on one grid/stroke spec.
- **Body copy at 13sp** (bodySmall) for long-form paragraphs (`ChatApp.kt:238,520,625,712-713,808,838`; `NewConversationScreen.kt:317`) vs the doc's 15–16sp body floor (`ANDROID-UI-REDESIGN.md:59`).
- **AccountSettingsScreen** (`ChatApp.kt:792-839`) is one unbroken wall of 6+ sections with no sub-navigation or grouped cards.
- **Glass-edge contrast ~1.5:1** (see §2) — identity rests entirely on tonal difference.
- **Brand:** "ADA" wordmark is a plain titleLarge Text (`ChatApp.kt:119`), no lockup; app icon is a flat teal `#245B52` square outside all four palettes (`res/drawable/ada_icon.xml`), the only drawable in `res/` — no adaptive icon, no splash, no light/dark variants.
- **Launch flash:** base XML theme is `Theme.Material.Light.NoActionBar` (`res/values/styles.xml:2`) while fresh-install default is dark — window paints light before Compose; bar icon style only fixed in a SideEffect after first composition (`MainActivity.kt:51-55`).

### 4.2 Layout & responsive

- **840dp rail breakpoint** (`Theme.kt:21`, `ChatApp.kt:109`) is 240dp above Material's 600dp medium class: 600–840dp portrait tablets get the bottom bar plus a glass pill wrapper (`ChatApp.kt:129-133`) — if 840 is deliberate, document why; otherwise move to 600dp.
- **IME open removes ALL chrome:** topBar, rail, and bottom bar are gated on `!typing` (`ChatApp.kt:109,114,116-129,128-137`) — while typing on a landscape phone the user sees no title/back/menu; system Back first only clears focus (`ChatApp.kt:107`) — fix: slim toolbar under the IME.
- **Composer magic numbers:** shortWindow < 120.dp (`ChatApp.kt:653`), 14dp field padding (`:685`), 45%/200dp budget (`:449`).
- **Voice draft discards have no confirmation** (`VoicePanel.kt:99,114,134`) while analogous discards elsewhere confirm — the transcript is a user-authored artifact.
- **No transient success feedback anywhere** (no Snackbar/Toast/haptics in the codebase); successes are silent or persist as inline text. No pull-to-refresh on any list screen (Conversations, Entities, Episodes, Proposals, Curiosity, Sources — all explicit Refresh buttons only).
- **Curiosity capability empty state missing:** policy == null renders heading + refresh and nothing else (`CuriosityScreen.kt:24` gate), unlike Proposals' explicit unavailable notice (`ProposalScreens.kt:25`).
- **ServerAddressPanel:** "Remove {label}" deletes a saved server in one tap with no confirmation (`:47`); success and error feedback render in identical neutral style (`:88`).
- **Full-content deletion** uses checkbox-acknowledgement instead of the app's dialog pattern (`SecuritySettings.kt:43-49`) — copy is explicit and it is checkbox-gated, but it's the odd one out; standard confirm dialog (checkbox copy inside) recommended.
- **SecuritySettings shows no loading indicator** while busy — buttons merely disable (`SecuritySettings.kt:11-58`).
- **One-time token "copy" affordance** is long-press selection of masked text only (`SecuritySettings.kt:27`) — add an explicit Copy button.

### 4.3 Motion

- **No destination transitions at all:** the `when(destination)` switch (`ChatApp.kt:140-160`) swaps screens with zero animation; the 240ms token is used only for presence color (`AmbientComponents.kt:131`).
- **Perpetual idle orb breathing** (3.6s infinite, `AmbientComponents.kt:116-117`) on the connect screen, empty-conversation state, and inside the voice dialog — guards are good (lifecycle, offscreen, system animator scale) but idle surfaces shouldn't animate; reserve motion for Listening/Thinking/Acting/Speaking.
- **No in-app reduced-motion toggle:** `LocalAdaMotionEnabled` (`Theme.kt:118`) is never set from UI (only androidTest `AmbientUiHttpTest.kt:59`); WCAG 2.3.3 is met via system animator scale, but add a "Reduce ambient motion" switch to AppearanceSettings.
- **Auto-scroll on every new event/pending-phase change** yanks users who scrolled up to reread (`ChatApp.kt:441-447`) — no "within N items of the end" check; with TalkBack the anchor can jump mid-utterance.

### 4.4 Appearance system

- **Dark mode is user-switch only** — no "Follow system" option at all (`AppearanceSettings.kt:43-53`); no app-level text-size setting (system scaling only).
- **Palette swatches show only the dark seed color** (`AppearanceSettings.kt:90`) — Oxford Blue `#002147` and Dark Red `#350616` are near-identical near-black circles; no light tint, no accent preview, no live-preview pane.

### 4.5 Accessibility structure & semantics

- **Missing `heading()` roles:** settings subsections (`SecuritySettings.kt:19`, `LearningSettings.kt:18`, `ExpressionSettings.kt:21`, `ChatApp.kt:850`), `AppearanceSettings.kt:71-72`, `FoundationScreen.kt:56` — landmark navigation is broken inside Settings.
- **No list semantics on any LazyColumn** (conversations `ChatApp.kt:278-291`, claims `MemoryScreens.kt:137-148`, receipts `DocumentScreens.kt:111`, episodes `EpisodeScreen.kt:64`, questions `CuriosityScreen.kt:59`) — no "item 3 of 12".
- **Clickable Cards without `Role.Button`:** conversation cards (`ChatApp.kt:279-290`), memory claim cards (`MemoryScreens.kt:138-148`) — second swipe to activate, whole paragraph read as the name.
- **Radio/switch/checkbox rows without merged semantics** (label is a separate TalkBack stop): `CuriosityScreen.kt:26-33`; `AgentScreens.kt:29`; `SecuritySettings.kt:48`; `VoicePanel.kt:128-130` (LearningSettings did it correctly — inconsistent).
- **Duplicate controls:** RadioButton + sibling TextButton doing the same action, radio outside any group (`EntityScreens.kt:46-48`; `DocumentScreens.kt:100-103`; `ProposalScreens.kt:54`); `selectableGroup()` containers lack the group role (`ChatApp.kt:319,352,858,877-896`; `MemoryScreens.kt:115,215`; `ExpressionSettings.kt:24`).
- **Episode message checkboxes are indistinguishable:** "Select user message" repeated with no identifier (`EpisodeScreen.kt:54-55`) — add index/excerpt.
- **No dialog focus management** on any of the ~13 AlertDialogs/Dialogs — focus is not moved into the modal or restored on close, so dpad/switch users can confirm irreversible actions on the obscured background.
- **SafeChatText: links render as "Open link to host" buttons** trailing the paragraph (`SafeChatText.kt:26-43`) — SR users can't tell WHERE in the reply a link sits; use AnnotatedString link spans. Positive: http(s)-only, embedded-credential rejection, 48dp, good descriptions.
- **SafeChatText monospace bug:** any message STARTING with ` ``` ` renders the ENTIRE message monospace (`SafeChatText.kt:31`) — intended only for fenced code; split per-span.
- **VoicePanel:** playback-voice DropdownMenu has no selected-item indicator and items lack 48dp minimum (`VoicePanel.kt:142-144`); recording status line includes raw `VoicePhase.name` (`:112`).
- **Nested scroll surfaces:** chat LazyColumn + vertically scrolling composer in the same window (`ChatApp.kt:393,664`) — dpad traversal from list end can drop into a 1-line-tall composer; test.
- **FLAG_SECURE** (`MainActivity.kt:36`) is intentional; note it also blocks screenshot-based a11y tooling on secure screens.

## 5. What's working well (keep)

- Centralized theme tokens (`Theme.kt`) with complete 4-palette light/dark tables; all measured text contrast passes AA (min 5.73:1).
- Error focus-steal + `LiveRegionMode.Polite` on the Chat and Memory FailureNotice pattern — the right model to extend everywhere.
- System "reduce motion" genuinely respected (animator scale + ContentObserver, `AmbientComponents.kt:87-102`).
- All `AdaIconButton`s carry `contentDescription` and enforce 48dp (`ChatIcons.kt:56`); 265 test tags for instrumentation.
- `VoicePanel`: every action is a tappable button (no gesture-only path); recording dismissal lock is explained in text; permanent-permission-denial has an "Open microphone settings" fallback (`VoicePanel.kt:117-119`).
- Single safe-inset owner (`AmbientComponents.kt:71-77`) with correct IME handling; system back clears focus before navigating (`ChatApp.kt:107`).
- Meaningful presence `stateDescription` ("ADA presence, Processing/Listening…"); capability gating hides nav items so there are no dead buttons.
- Localized `displayInstant()` exists (`ChatSourceCard.kt:84-87`); external links are explicit http(s)-only buttons.
- Confirmation dialogs exist on most destructive flows (15 AlertDialogs).

## 6. Recommended fix order

1. Shared humanized fault/notice component with live region + focus steal, used by every controller; kill the Curiosity silent-fault and the Proposal class-name leak (§3.2). — Biggest combined UX + screen-reader gap.
2. Confirmations for sign-out-all, per-session revoke, logout (§3.1); voice draft discard.
3. Short-window dialog constraint via available-height pattern (§3.4).
4. Human-readable state/enum copy + `displayInstant()` in Research, Agents, Episodes, Learning/Expression pickers (§3.3).
5. One labeled loading component; label all ~14 indicators; 48dp minimums on the ~60 buttons, starting with SecuritySettings and Curiosity rows (§3.6).
6. Selection semantics: one selectable/RadioButton pattern everywhere with `stateDescription` (§3.5).
7. Token discipline pass: `AdaSpacing`/`AdaLayout` only, one AdaCard, one heading scale, unified icon family (§3.7, §4.1); lint rule against raw `N.dp`.
8. Dialog focus management for all ~13 dialogs (§4.5).
9. Brand & first impression: adaptive icon on-palette, dark launch theme, wordmark lockup, glass-edge alpha fix (§2, §4.1).
10. Docs: rewrite stale appearance sections in both READMEs (§3.8).

## 7. Needed for the next pass (visual + device verification)

Code-level findings above are complete, but these items cannot be closed without a device/emulator:

1. Screenshots (or screen recordings) of each primary screen — Connect, Conversations, Conversation + composer, Settings, Memory, Documents, Episodes, Research, Curiosity, Voice panel open — in Ambient palette light and dark, at phone width AND tablet width (≥840dp), plus one short-landscape capture (≤500dp window height) to visually confirm the 600dp dialog clipping bug (§3.4).
2. An emulator or device with the debug APK installed and TalkBack enabled, for a guided pass over: composer → send → stop → pending/recovery panel; memory write (remember → select quote → preview → save); entity merge review; proposal accept/reject with conflicts; document upload review; settings subsections.
3. Foldable live-resize and physical large-tablet checks (already open items at `docs/ANDROID-UI-REDESIGN.md:206-208`).
4. After any palette tweak: re-measure the Red light and Ambient light muted pairs (closest historical calls, §2).

---

*Generated from a two-critic code audit + independent WCAG contrast computation; every file:line reference was verified against source on 2026-10-18.*


## 8. Verified follow-up, 2026-10-18

Scope: Android design hardening against the report, starting from `b2a383e`.
App20 / `0.25.2-ui`. The repository and native behavior were checked before
accepting the proposed remedies. Server contracts, ownership checks, saved
request bodies, source trust, journals, migrations and audio controllers remain
unchanged. No later phase or deployment is part of this work.

### Findings and disposition

| Original finding | Verified result and change |
| --- | --- |
| 2, 4.1: glass boundary contrast | Mixed. Low-contrast decorative panel edges are not all functional controls. The composer needs an identifiable input boundary: it now uses the opaque theme outline. Eight-scheme tests check that boundary at 3:1 and muted/inline-link text at 4.5:1 on relevant surfaces. Raising every edge to 50% alpha would not guarantee 3:1. |
| 3.1: session/logout actions | Confirmed. Added reviewed dialogs for logout/change server, all password sessions and individual session revocation; the safe Cancel button receives initial keyboard focus. Existing callbacks run only after confirmation. |
| 3.2: feedback | Partly confirmed. Proposals exposed a class name; Tools omitted its fault. Both fixed. Curiosity has no `fault` field: its controller already reports errors through `notice`, so it was not silently swallowing an unrendered fault. Shared human-readable notice/failure surfaces now provide polite live regions, and failures request focus once. Learning/Expression retain the actual mapped failure reason. |
| 3.3: protocol copy | Confirmed in the identified feature screens. State, job, preference and recording labels are readable; exact diagnostics stay available in technical details. Unknown states never mean success. Dates use the existing localized formatter; original IDs/UTC values remain inspectable. |
| 3.4: compact dialogs | Confirmed in source. Conversation details/options now constrain their total height to the available window, with a fixed reachable close control and scrolling body. Keyboard insets are included. |
| 3.5: choices | Confirmed for the text-suffix patterns. Shared radio rows/chips expose selected state; toggles merge their label and checked state. Voice speed/voice selection also expose state. Display changes preserve selected protocol values. |
| 3.6: loading and target sizes | Confirmed for missing progress labels. Shared labelled loading is used by the affected screens, including security. Material already expands touch hit regions, so the original report overstated missing hit targets; the phone measured only 40dp of native TextButton layout/semantics space. Shared buttons now explicitly reserve at least48dp to prevent adjacent crowding. |
| 3.7: tokens | Repeated spacing/touch/composer/dialog values moved to shared roles. Arbitrary dp values are not inherently defects: icon geometry, line widths and intentional shapes retain dimensions. No custom lint dependency or blanket ban was introduced. |
| 3.8: docs | Confirmed and corrected in both READMEs: four palettes, Ambient/dark fresh defaults, preserved explicit legacy choices. |
| 4.1: cards/type/icons/settings | Shared feedback, loading, settings headings and collapsed groups reduce inconsistent interaction patterns. Long-form explanatory copy uses bodyMedium; captions/provenance retain bodySmall. Navigation now uses the same icon family. Distinct evidence/quote/pending surfaces and title hierarchy remain intentional; one generic card and a new wordmark are not prerequisites. |
| 4.1: launch/brand | Confirmed teal icon/light flash mismatch. Added Ambient adaptive icon, monochrome mask and Android12+ splash resources. Saved appearance is applied before Compose starts; system bars follow the effective mode. Secure-window protection remains. |
| 4.2: responsive navigation | Rail starts at600dp, so medium landscape/tablet windows can use it. While typing, chrome is deliberately hidden to reserve conversation space. Back hides the keyboard before leaving the conversation; explicit tests preserve the typed multiline/emoji draft. A persistent toolbar was not added to already short IME windows. |
| 4.2: destructive/empty/security details | Draft and saved-draft discard require confirmation; active recording discard stays immediate to stop the microphone. Saved-server removal and token rotation require review; full erasure retains its preview/checkbox and adds a final dialog. Curiosity has explicit unavailable/loading content. Added an explicit sensitive-clipboard Copy action for one-time credentials; it is never invoked automatically. |
| 4.2: refresh/success | Explicit Refresh and durable inline feedback remain. Missing pull-to-refresh, Toast, Snackbar or haptics alone is not a verified failure and does not justify adding another interaction model. |
| 4.3: motion/reading | Confirmed automatic scroll could interrupt reading. It now follows only while at the latest content; scrolling up exposes Latest message. Added saved Reduce ambient motion, combined with existing lifecycle/system animation gating. Idle breathing remains part of the approved design. Destination animations are optional; immediate private-state switches remain. |
| 4.4: appearance | Added opt-in Follow system appearance and dual light/accent swatches. Existing explicit dark/light choices are preserved until the user opts in. System font scaling remains the text-size control. |
| 4.5: structure | Added settings headings, clickable-card Button roles, uniquely indexed episode-message choices and merged labelled controls. Native LazyColumn already supplies collection semantics; selectableGroup supplies native grouping without an invented extra group role. Those blanket missing-semantics claims are retracted. |
| 4.5: dialogs | Native Compose dialogs already create a modal window and contain focus; obscured background activation was not established. New destructive dialogs explicitly focus Cancel. A physical keyboard-action test found and fixed the initial focus timing relative to dialog-window creation. Spoken TalkBack focus and return order still need manual verification. |
| 4.5: text/links | Fenced-code styling is applied per display span, not to the whole reply. HTTP(S) links are inline annotated links with explicit activation; unsafe schemes and embedded credentials remain rejected. Text is never parsed as executable HTML/commands, and original quote text/code-point offsets are preserved. |
| 4.5: nested scrolling/security | The compact editor remains internally scrollable so full multiline input survives short windows. Geometry/IME checks are automated; full switch/D-pad traversal remains a manual target. FLAG_SECURE remains enabled on the real activity. Public screenshots come only from a separate synthetic test host. |

### Evidence and remaining verification

The dated Android-design entry in [STATUS](../plans/STATUS.md) and
[WORKLOG](../plans/WORKLOG.md) records exact invocations, corrected failures,
configuration checks and cleanup. Existing evidence elsewhere in this document
is historical, not a substitute for those runs.

The connected S24 FE is SM-S721U1, Android16/API36. Validation uses the separate
`dev.ada.validation.designgaps.debug` app, actual authenticated local HTTP,
Keystore and a disposable PostgreSQL schema. All content/accounts are synthetic;
provider, research and voice drivers are explicit fixtures. Audio-controller tests
do not establish microphone accuracy, natural speech or speaker-focus behavior.
No normal ADA app/data reset is needed.

Manual TalkBack announcements/reading order/modal restoration, hardware
keyboard/switch traversal, alternative IMEs, physical tablet/foldable live resize,
performance/battery/long-scroll and inherited microphone/speaker/focus release
gates remain pending. The user requested automated checks only. A full backend,
web or connected-test-suite pass is not claimed.

### Repeating the isolated checks

Use the pinned JDK/wrapper and a dedicated `ADA_TEST_DATABASE_URL`, never the
application database. Build the distinct validation ID first:

```powershell
./apps/android/gradlew.bat -p apps/android `
  -PadaValidationApplicationId=dev.ada.validation.designgaps `
  testDebugUnitTest lintDebug assembleDebug assembleDebugAndroidTest
./.venv/Scripts/python.exe scripts/verify_android_design_gaps.py `
  --device <adb-serial> --physical-model SM-S721U1 --suite design
```

The helper verifies the selected model, package metadata and copied APK contents
before installing. It creates/cleans its own fixture schema, loopback server,
ADB reverse and validation packages. The serial is explicit; no normal app is
installed. Additional suites and `--stage` select specific flows. `--variant`
asserts the actual font/window configuration; landscape/expanded additionally
request landscape in the public test activity. It does not set system font or
density automatically.
Save and restore system font/rotation settings around configuration tests.
Return to the normal application ID for the final build artifact.


Automated configuration results for this follow-up:

| Target | Checked configuration | Result |
| --- | --- | --- |
| S24 FE / API36 | Portrait1080x2340, density450, font1.0 | Native semantics/links/confirmation focus, primary light/dark screens and reviewed HTTP feature flows passed. |
| S24 FE / API36 | Font1.6 | Primary light/dark screens, frozen source evidence, dialog bounds and multiline/emoji keyboard Back passed; corrected compact Docs label rechecked visually. |
| S24 FE / API36 | Actual landscape2340x1080, font1.3 | Rail, primary screens, fixed dialog close controls and keyboard Back/draft passed. |
| API37 emulator | Expanded2560x1800, density320, font1.6 | Native semantics/link activation9.534s, dark32.088s/light32.806s walkthroughs, bounded dialogs16.425s and keyboard Back14.112s passed. |

Representative public app-layer captures were visually reviewed at these sizes. Dialog captures
are tagged dialog surfaces, not full-screen dimensions. Manual spoken
accessibility, physical tablet/foldable behavior and performance remain pending.
The original phone settings and ordinary app are preserved. Fixture apps/reverses
are removed, disposable database schemas cleaned and owned emulator/PG stopped.
Final build/check/audit details are recorded in STATUS/WORKLOG.
