# ADA Ambient Intelligence — Android presentation redesign

Implementation scope: [the requested redesign](../plans/ADA-Android-UI-Redesign.md).
Audit/design recorded2026-10-18 America/Phoenix before the screen rollout. Source
baseline HEAD844d560 includes the existing uncommitted proxy fix and redesign plan;
those are preserved. This work changes presentation, not server capabilities.

## Existing UI audit

The application is Kotlin/Jetpack Compose/Material3, not XML Views. MainActivity
is the sole production Activity, with no Fragment navigation. ChatApp switches
the existing ChatDestination enum; its four main destinations are Chat, Memory,
Documents and Settings. Feature views include new conversations/styles, sources,
retrieval diagnostics, explicit memory/review, aliases, documents, read-only tools,
episodes, expression/learning/security, research and curiosity. No independent
onboarding flow exists; connection/password sign-in is the entry screen.

ChatViewModel and injected controllers expose StateFlow; AdaApi/HttpAdaApi and
SessionStore/AndroidSessionStore own HTTP and encrypted persistence. Credentials,
UUID journals, request/source snapshots, review and permission boundaries remain
there. UI rendering must not submit requests on appearance/state transitions.
Voice already uses reviewed on-device input and independent offline playback.
It exposes recording/playback states, but no audio-amplitude stream.

The theme originally supplied three persisted palettes (Oxford Blue, Dark Red,
Olive Green), light/dark colors, stock typography and small/medium/large shapes.
Screens use Material controls, error/live-region semantics,48dp controls, escaped
source/message text and bounded scrollable request recovery/composer panels.
ChatApp already uses lifecycle-aware collection; research, curiosity and proposal
screens still used ordinary collectAsState. MainActivity owns safe insets and
secure-window policy; ChatApp adds IME padding and retains the focused composer
when the keyboard opens. Those ownership/interaction rules are retained.

Pinned tools: min26/target36/compile36, Java21 toolchain/Java17 bytecode,
AGP8.11.1/Kotlin2.2.21/Compose BOM2025.10.00. Existing Material3, lifecycle-compose,
Canvas and animation APIs suffice. No new dependency, permission, font or SDK bump.
Baseline Android unit/lint/debug/instrumentation builds passed (254units).
Backend contract baseline6passed/2PG-not-configured skips; no schema change.

## Design system

Fresh installs use ADA Ambient in dark mode. Existing saved palette/dark values
keep their keys and choices; all three earlier palettes remain selectable, as
does light mode. The latest selected plan makes violet the new default identity.

| Role | Dark Ambient |
|---|---|
| Canvas | #070816 |
| Surface | #101329 |
| Elevated glass | tonal/translucent surface with a quiet1dp edge |
| Primary light | #A48CFF, from violet #8A6CFF |
| Listening light | #68D8FF |
| Warm speaking light | #EFA5C8 |
| Primary text | #F6F7FF |
| Secondary text | #B8BDD3 |
| Outline | #7E849E |

Light mode uses a darker violet for readable text/controls. Native sans-serif
typography uses32sp display,26sp screen headings,18–20sp section headings,
15–16sp body,12–14sp labels with system scaling. Shapes:14–16dp small controls,
20dp cards,24dp large surfaces. Spacing:4/8/16/24/32dp,48dp minimum controls.
Shared layout tokens bound reading width and choose an expanded navigation rail.

The compact refinement uses labelled icon buttons for frequent actions, with
48dp touch targets. Feature names stay readable inside menus; long settings,
source provenance and review disclosures keep their text. A single composer
surface contains entry, document-import access, microphone and Send/Stop controls.
Secondary controls open on demand so the conversation keeps most of the viewport.

AdaPresence is vector-rendered lighting and an orbit, not a downloaded image,
blurred bitmap or amplitude visualization. State comes from existing recording,
confirmed running request, playback, tool and error state. Unknown delivery stays
unconfirmed. Text/accessibility labels accompany color. Ambient animation pauses
offscreen/backgrounded and with system animation disabled; tests can freeze it.
Idle breathing is subtle/multisecond; only confirmed processing/task state orbits.
There are no per-row infinite animations or fabricated analytics/status values.

## Screen rollout

1. Theme/tokens, reusable atmospheric background/glass/message/heading/presence
   components and contrast/state tests, then build/test.
2. Sign-in, conversation list, chat messages/composer and application chrome.
   Keep all navigation destinations, request actions, tags/labels and current
   auth/IME/recovery behavior. Compact navigation remains four destinations;
   expanded windows use the same destinations in a rail. Build/test and inspect.
3. Voice controls use real recording/playback states with the same explicit
   permission/transcript approval/Stop actions. Other feature screens adopt the
   same theme, heading hierarchy and lifecycle collection. Original trust labels,
   approval disclosures, source quotes and error/retry controls stay intact.
4. Verify compact/landscape/expanded/large-font, insets/keyboard, all palettes,
   semantics/reduced motion, real HTTP flow and recovery in a separate validation
   APK using disposable data. Record measured checks and target limits below.

## Files and boundaries

Modify Theme.kt, AppearanceSettings.kt, MainActivity.kt, ChatApp.kt, VoicePanel.kt
and presentation-only feature Screen/Settings files as needed. Add
AmbientComponents.kt for actual reused visuals, focused unit/instrumentation
tests and a guarded emulator verification runner. Update AndroidREADME and
STATUS/WORKLOG with actual outcomes. Backend/data/controllers/ViewModels,
API contracts, journal versions/keys, migrations, locks and wrappers are protected.
Normal app installation/deployment is outside this task.

Actual results, corrected failures and remaining physical/quality checks are
recorded in [STATUS](../plans/STATUS.md) and [WORKLOG](../plans/WORKLOG.md).

## Compact layout refinement — 2026-10-18

The follow-up prioritizes reading space after the first redesign. The home list
uses a smaller presence/header and concise conversation rows. Each row keeps its
title and useful scope/style context without repeating the same title as a second
line. New-conversation and refresh actions remain accessible.

An open chat uses a compact Back/title/overflow header. The overflow menu exposes
the existing capability-gated research, curiosity, read-only tools and history/
episodes destinations, plus conversation context and history actions. Saved scope,
style, prompt details and explicit upgrade confirmations remain available on demand.
These controls no longer form a permanent multi-line toolbar above the messages.

Message entry, the Add/paperclip menu, microphone and Send are integrated in the
composer row. The Add menu opens document imports or a Message options dialog.
Memory, imported-document use and historical-instant settings retain their current
capability/prompt gates; a pending request keeps its original frozen options.
The character warning remains available when needed without a permanent empty
counter row. While an owned stream can be stopped, the action becomes Stop rather
than reserving another fixed panel below the conversation.

The pending reply and provisional text appear at the end of the scrollable
conversation. Status and recovery actions still distinguish running, unknown,
failed, missing and conflicting requests. Details expand when needed; check/retry
actions keep the original request ID and payload. Partial text stays provisional
and cannot supply completed source cards.

Dated compact-refinement checks, corrected failures and remaining target work are
recorded separately in STATUS and WORKLOG. Earlier checks below describe the first
redesign and keep their original provenance.

## Using the redesigned app

The normal build is app19/0.25.1-ambient. Existing installs keep their saved
appearance; choose **Settings → Appearance → ADA Ambient** to use the new violet
palette. Dark mode is the fresh-install default, not an override of a saved choice.
Oxford Blue, Dark Red and Olive Green remain available in both modes.

1. Open a conversation. Use Back to return to the list, or the overflow icon to
   open feature and conversation actions. Feature entries appear only when the
   connected server supports them. Open conversation context to inspect the saved
   scope, style and prompt, or review an explicit prompt upgrade.
2. Type in the compact message field and tap Send. The input remains multiline
   and respects the keyboard and system insets. Very short keyboard windows show
   one internally scrolling input line; the draft retains its line breaks.
   Compact windows keep the four
   bottom destinations; wider windows use the same destinations in a scrollable
   rail. Source/citation text and original provenance remain unchanged.
3. Open Add/paperclip → **Message options** to choose available saved-memory,
   imported-document or historical-instant options, then close the dialog to
   continue typing. Existing pending requests keep their reserved options.
4. Open Add/paperclip → **Open document imports** for the existing reviewed upload
   workflow. Select the intended owned scope there, then import/review UTF-8 text
   or Markdown. This is a separate document library, not a file attached to the
   current chat message. It does not accept arbitrary files or PDFs. Uploading
   creates imported, untrusted evidence, not an endorsed user assertion. Using
   those documents in chat requires the existing scoped retrieval options and
   supported saved prompt.
5. Tap the microphone to open Voice controls. Tap Record explicitly, review the
   generated transcript, approve the wording and use **Send reviewed voice**.
   Opening the dialog alone does not activate the microphone. Stop or discard an
   active recording before closing; a reviewed draft is not implicitly approved
   or sent by dismissal. Playback and Stop retain the existing offline voice flow.
6. During a reply, read the inline provisional output and use Stop when available.
   Expand recovery details if the outcome is uncertain; Check request and original
   retry actions preserve the reserved request. Leaving the screen does not
   automatically cancel generation.

The presence visualization reflects existing state. It adds no voice service,
waveform, model, private inference or permission. There is no automatic message
submission, memory write or notification. Device speech/focus limitations from
earlier phases remain separate.

Actual changed Android files: MainActivity.kt; ui/Theme.kt,
AppearanceSettings.kt, AmbientComponents.kt, ChatApp.kt, ChatIcons.kt, VoicePanel.kt,
MemoryScreens.kt, DocumentScreens.kt, EntityScreens.kt, ProposalScreens.kt,
AgentScreens.kt, EpisodeScreen.kt, ResearchScreen.kt and CuriosityScreen.kt;
version metadata plus focused unit/instrumentation tests. Controllers, ViewModels,
data/audio implementations, journals, manifests, backend/OpenAPI, migrations and
dependency locks remain unchanged.

## Verification boundaries

Automated evidence uses the installed API37 emulator and a separate validation
application ID. HTTP/password/Keystore/stream/source/recovery flows use disposable
PostgreSQL and an explicitly selected FakeProvider, never an application account.
Native MainActivity tests verify saved palette/mode restoration, system-bar icon
flags and FLAG_SECURE. Public synthetic screenshots use a separate test-only host
that renders the same UI; production screenshot protection remains intact. The first-redesign
images capture the app surface. The compact follow-up additionally captures the
whole emulator window, including the OS keyboard, only from the public test host
to verify rotated layout; real/private screenshots remain protected.

Relevant local checks include all Android units/lint/builds, native-PG contract
checks, rendered text contrast, orb semantics, gesture/three-button navigation,
multiline input/IME anchoring, compact portrait, rotated landscape and expanded
windows with increased text scale. See STATUS for each actual invocation rather
than adding historical counts together.

Still required: physical S24FE/Android16, manual TalkBack, physical keyboard/IME
variations, foldable live-resize, graphics/battery/long-scroll performance and the
inherited voice/focus/G-41 release gates. Emulator semantics and configuration
checks do not establish those results. No normal app installation or deployment.
