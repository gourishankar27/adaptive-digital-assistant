# ADA Android UI Redesign

You are redesigning the existing Android application **ADA — Adaptive Digital Assistant**.

This is an existing working application, not a greenfield demo.

Your task is to modernize ADA's Android presentation layer into a polished, dark-first, atmospheric AI assistant interface while preserving the application's architecture, behavior, navigation, API contracts, authentication, data flow, and existing functionality.

Do not begin by rewriting screens.

Begin by understanding the existing project.

---

# Product Identity

ADA is a personal adaptive digital assistant.

ADA should feel:

intelligent
calm
private
capable
human-aware
warm
slightly futuristic

ADA should NOT feel:

like a generic chatbot template
like a gaming interface
like a crypto dashboard
like a neon cyberpunk application
like an iOS clone
like a Material Design demo
like a collection of glass cards
like a purple-gradient AI landing page

The interface should communicate that ADA is an intelligent presence rather than simply a chat application.

The emotional character should be subtle.

Warmth should come from motion, copy, pacing, spacing, responsiveness, and occasional warm light.

Do not use hearts, cartoon expressions, excessive pink, mascots, or childish visual cues.

---

# First Step: Audit the Existing Android Project

Before changing code, inspect the repository.

Determine:

- whether the UI uses Jetpack Compose, XML Views, or a hybrid
- existing Material version and theme implementation
- navigation architecture
- Activity and Fragment structure
- ViewModels and UI state models
- repositories and data sources
- existing screens
- reusable components
- authentication flow
- chat/conversation flow
- voice functionality if present
- settings/profile/personality screens if present
- loading/error/empty states
- existing accessibility support
- existing tests
- current minSdk, targetSdk, and compileSdk
- current handling of system bars and WindowInsets

Do not assume the project uses Jetpack Compose.

If the application already uses Compose, continue using Compose.

If it primarily uses Views/XML, do not migrate the entire application to Compose merely for this redesign unless explicitly requested.

Do not modify backend behavior simply to achieve a visual effect.

Do not move networking, persistence, authentication, memory, or business logic into UI classes.

Report your audit findings before beginning broad UI changes.

---

# Architecture Rules

Treat this primarily as a UI-layer redesign.

Preserve the existing architectural boundaries unless there is a clear defect directly blocking the redesign.

For Compose projects, follow Android's recommended unidirectional data-flow model:

UI renders immutable state.

User actions generate events.

Screen-level ViewModels process those events and expose state.

Use StateFlow/Flow where the existing architecture supports it.

Collect state using lifecycle-aware APIs.

Composable functions must not directly perform network requests or access databases.

Reusable visual components should not own screen-level ViewModels.

Repositories remain the boundary between application logic and external/local data sources.

Do not introduce a second architecture alongside the existing architecture.

Do not rename API models, routes, navigation destinations, request fields, or persisted keys merely for visual cleanliness.

---

# Core Visual Direction

The design language is called:

## ADA Ambient Intelligence

Use a dark, near-black environment with softly illuminated depth.

The visual reference is a combination of:

- cinematic AI assistant interfaces
- dark spatial interfaces
- restrained glass surfaces
- subtle aurora lighting
- luminous 3D intelligence objects
- premium voice-assistant interfaces

Do not directly reproduce another application's branding or screens.

Extract the visual principles and reinterpret them for ADA.

---

# Background System

The primary app canvas should be a very dark navy-black rather than pure black.

Suggested starting point:

Canvas Deep:        #070816
Canvas:             #0A0C1C
Surface:            #101329
Surface Elevated:   #171A34

The background may contain extremely soft atmospheric illumination.

Preferred light families:

ADA Violet:         #8A6CFF
ADA Cyan:           #68D8FF
ADA Warm Rose:      #EFA5C8

These colors are illumination sources, not general-purpose fill colors.

Use them through low-opacity radial light, edge glow, assistant visualization, focused controls, and selected states.

Do not cover screens with obvious rainbow mesh gradients.

Most of the screen should still read as dark navy.

---

# Primary Accent

ADA Violet is the primary brand accent.

Use it deliberately.

Recommended:

Primary:            #8A6CFF
Primary Bright:     #A48CFF
Primary Deep:       #6249D8

Cyan is a secondary light source.

Rose is an emotional warmth accent.

Do not give violet, cyan, and rose equal visual weight.

Violet remains dominant.

---

# Text System

Primary text:

#F6F7FF

Secondary text:

#B8BDD3

Muted text:

#7E849E

Disabled text:

use an appropriate lower-emphasis accessible value derived from the theme.

Avoid pure #FFFFFF for every text element.

Create clear hierarchy through luminance, size, weight, and spacing.

Do not rely only on opacity if it causes poor contrast.

---

# Typography

Use Android-native or properly licensed fonts already available to the project.

Do not introduce proprietary fonts copied from reference products.

If no custom ADA font exists, prefer a clean Android/system sans-serif.

The typography should feel soft and precise rather than heavy.

Recommended approximate hierarchy for compact phone layouts:

Display: 30–34sp, medium/semi-bold
Screen title: 24–28sp, medium
Section title: 18–20sp, medium
Body: 15–16sp, regular
UI label: 13–14sp, medium
Caption: 12–13sp, regular

Respect user font scaling.

Avoid tiny decorative labels.

Avoid excessive uppercase.

Avoid excessive bold text.

---

# Shape Language

Use a consistent rounded geometry.

Primary cards and major surfaces:

20–24dp radius

Compact controls:

14–18dp radius

Buttons:

18–24dp radius or pill when visually justified

Small chips:

pill geometry

Do not randomly alternate between sharp rectangles, 12dp cards, 32dp cards, and pills.

The design should look like one system.

---

# Glass Surface System

Do not make every component glass.

Glass is reserved for elevated or interactive surfaces.

Examples:

chat composer
floating navigation
modal surfaces
assistant controls
voice controls
selected cards
important overlays

A glass surface should combine:

dark translucent fill
subtle 1dp light border
soft tonal separation
minimal shadow
optional background blur where performant

Suggested conceptual values:

Glass fill:
rgba(20, 23, 45, 0.55–0.75)

Glass border:
rgba(255, 255, 255, 0.10–0.16)

Highlight edge:
rgba(255, 255, 255, 0.20)

Avoid thick glowing borders.

Avoid applying blur behind every scrolling row.

If true background blur creates performance or compatibility problems, simulate the depth using translucent surfaces, tonal gradients, borders, and shadows instead.

---

# ADA Orb / Intelligence Core

Create a reusable visual component representing ADA.

Suggested component name:

AdaOrb
AdaCore
AdaPresence

Choose the name that best matches existing project terminology.

The assistant visualization should become a recognizable part of the application.

It may consist of:

a luminous central sphere
soft internal gradients
one or more subtle orbital forms
depth lighting
low-opacity glow
gentle motion

Do not make it look like a planet logo copied from another product.

Develop a distinct ADA interpretation.

The component must visually represent application state.

## Idle

Very subtle breathing animation.

Slow movement.

Low glow.

## Listening

Slight expansion.

Audio-reactive or pulse behavior if voice amplitude is actually available.

Cyan becomes somewhat more visible.

## Thinking

Controlled internal motion.

Slow orbital movement or rotating gradient.

Violet becomes stronger.

Avoid generic loading spinners whenever the ADA visual can communicate the state.

## Speaking

Gentle rhythmic response connected to speech state.

Do not fake audio responsiveness if no amplitude data exists.

## Acting

A focused, slightly brighter state that communicates tool or task execution.

## Error / Offline

Reduce saturation and movement.

Use the semantic error system without turning the entire orb bright red.

The state must also be communicated through text or semantics.

Never rely on color alone.

---

# Motion Language

Motion should make ADA feel alive without making the interface busy.

Most UI transitions:

approximately 180–280ms

Prefer spring or eased movement instead of abrupt linear animation.

Large navigation transitions may be slightly slower.

Ambient ADA Orb breathing may use a multi-second cycle with very small amplitude.

Avoid:

constant floating cards
large parallax effects
continuous screen-wide particles
random shimmer
every component animating on entry
excessive bounce

Motion should communicate:

state
focus
continuity
response

not decoration.

Respect system animation settings and reduced-motion expectations.

Pause unnecessary infinite animations when components are not visible.

---

# Home / Primary ADA Screen

The primary screen should feel like entering ADA's environment rather than opening a dashboard.

Keep the hierarchy simple.

The screen may contain:

a restrained top application area
ADA identity/status
the ADA Orb or presence visualization
contextual greeting or current state
a primary interaction composer
voice entry
relevant recent actions or conversations when appropriate

Do not fill the home screen with six dashboard cards.

Do not show fake analytics or decorative data.

Only surface information that exists in the application.

The strongest visual relationship should be:

User
↓
ADA presence
↓
Current context
↓
Interaction

---

# Chat Experience

The chat screen must prioritize readability over visual effects.

The background remains atmospheric but quieter than onboarding or voice mode.

Assistant messages should not all appear inside large glowing cards.

Prefer restrained assistant message treatment.

User messages may use a subtle tinted or glass surface.

Keep long AI responses comfortable to read.

Code blocks, citations, attachments, source cards, tables, and other structured content must remain legible.

The composer should feel elevated and persistent.

The composer may use:

glass surface
rounded geometry
text input
attachment/add control
voice control
send/action control

The input area must correctly handle:

IME
multiline text
system navigation gestures
landscape
small screens
font scaling

Do not sacrifice typing usability for appearance.

---

# Voice Mode

Voice mode may be the most visually expressive ADA screen.

Use the ADA Orb as the primary visual object.

Layout hierarchy:

top navigation/status
large ADA presence region
small state label
optional transcript or response
primary microphone control
secondary text-mode/exit controls

The microphone should be visually obvious but not oversized to the point of feeling like a call-screen clone.

Listening, thinking, and speaking must look meaningfully different.

Use animation and light carefully.

---

# Onboarding

If onboarding already exists, redesign it rather than inventing an unrelated new flow.

The visual approach may use a full-screen ADA environment with one strong visual object per page.

Each onboarding page should communicate one real capability.

Do not claim features ADA does not currently provide.

Keep copy short.

Use one primary action.

Use Skip only where appropriate.

Do not create five or six onboarding pages just to show visual effects.

A three-screen structure is preferred when supported by the real feature set.

---

# Navigation

Preserve the application's existing information architecture unless a navigation problem is discovered during the audit.

Do not rename routes purely because another label sounds more stylish.

For compact phones, use the simplest appropriate navigation pattern.

For larger Android windows, consider adaptive navigation only where it improves the existing workflow.

Potential expanded layouts may use:

navigation rail
two-pane conversation/history layout
supporting pane

Only introduce these when corresponding features already exist.

---

# Adaptive Android Layout

The UI must be designed for Android windows, not only a single 6.7-inch portrait screenshot.

Support:

compact phone portrait
phone landscape
foldable/window resizing
medium-width layouts
expanded/tablet layouts where practical

Use window size classes or the project's equivalent architecture.

Do not hardcode layout around one device resolution.

---

# Edge-to-Edge

The application should intentionally support edge-to-edge presentation.

Background and atmospheric visuals may extend underneath system bars.

Interactive elements must respect safe insets.

Status bar icons must remain readable.

Gesture navigation areas must not contain conflicting touch targets.

The chat composer must remain correctly positioned above:

gesture navigation
three-button navigation
IME/keyboard

Treat Android system UI as part of the composition.

Do not imitate an iPhone status bar or Dynamic Island.

---

# Accessibility

Visual polish must not reduce usability.

Interactive controls require appropriate Android touch targets, normally at least 48dp.

Provide semantic descriptions where needed.

Support TalkBack.

Do not encode state through color alone.

Maintain readable contrast.

Respect font scaling.

Avoid extremely thin text.

Avoid motion that is essential for understanding an action.

Custom visual controls such as AdaOrb must expose meaningful accessibility semantics when interactive or state-bearing.

---

# Performance

This interface must run like a production Android application.

Avoid stacking multiple expensive blur passes over scrolling content.

Avoid huge continuously animated bitmap backgrounds.

Avoid unnecessary recomposition.

Do not create one infinite animation per list item.

Cache expensive visual calculations when appropriate.

If blur or advanced effects require newer platform APIs, provide a reasonable fallback.

Prefer a convincing lightweight effect over an expensive technically perfect glass simulation.

Visual complexity must degrade gracefully.

---

# Material 3

Use Material 3 as an Android interaction/accessibility foundation when appropriate.

Do not make the final interface look like untouched stock Material components.

Create ADA-specific theme tokens and reusable components around Material primitives.

Preserve expected Android behavior:

touch feedback
focus
accessibility semantics
keyboard behavior
window insets
navigation
state restoration

The goal is:

native Android behavior
+
custom ADA visual identity

---

# Design Tokens

Centralize design values.

Do not scatter literal colors, corner radii, elevations, and spacing throughout screen code.

Create or update an ADA theme/design system containing:

color roles
surface roles
typography
spacing
shape
elevation
glow roles
motion durations
component defaults

Names should describe purpose rather than appearance.

Prefer:

adaPrimary
surfaceGlass
surfaceElevated
textSecondary
glowListening

instead of:

purple500
darkCard2
blueGlow

where practical.

---

# Reusable Components

Extract repeated visual primitives instead of restyling every screen independently.

Potential reusable components include:

AdaBackground
AdaOrb / AdaPresence
AdaGlassSurface
AdaPrimaryButton
AdaIconButton
AdaTopBar
AdaChatComposer
AdaUserMessage
AdaAssistantMessage
AdaVoiceControl
AdaStatusIndicator
AdaDialog
AdaNavigationSurface

Only create components that are actually reused.

Do not create a huge abstract component framework before implementing real screens.

---

# Redesign Workflow

Do not redesign the entire application in one unreviewed pass.

Start with an audit.

Then define the ADA theme and reusable visual primitives.

Then redesign one representative high-value screen, preferably the primary chat/home experience.

Ensure the visual system works there.

Then propagate the system into the remaining screens.

After each stage, build and test the project.

Do not leave partially implemented placeholder components.

Do not replace working functionality with static mock data.

---

# Preserve Existing Behavior

Unless explicitly authorized, do not change:

backend API contracts
authentication semantics
database behavior
memory behavior
conversation persistence
networking semantics
tool execution behavior
personality logic
domain models
business rules

The visual redesign must sit on top of the working product.

If a UI change requires architectural work, explain exactly why before making the change.

---

# Visual Quality Guardrails

Before considering a screen complete, verify:

The page has one clear visual hierarchy.

ADA Violet is used consistently.

Cyan and Rose remain supporting illumination colors.

Corner radii belong to one coherent shape system.

Glass is used selectively.

Text remains readable over atmospheric backgrounds.

There are no unnecessary gradient blobs.

There are no generic three-card feature layouts.

There are no fake status indicators.

There are no decorative UI elements pretending to contain data.

There is no excessive glow.

There is no unnecessary animation.

The UI remains recognizably Android.

The design looks like ADA rather than a copied reference application.

---

# Deliverables

Before implementation, provide:

## 1. Existing UI Audit

Explain the current Android UI stack, navigation, theme architecture, reusable components, and major screens.

## 2. Proposed ADA Design System

Define final colors, typography, shape system, surfaces, spacing, motion, and assistant visualization.

## 3. Screen Redesign Plan

Describe what will change on each existing screen without changing its underlying behavior.

## 4. Files to Modify

Identify the exact Android source files that need modification or creation.

## 5. Implementation

Implement the redesign incrementally.

Do not provide pseudocode where working project code is expected.

## 6. Verification

Build the Android project.

Run relevant tests.

Resolve compilation errors.

Check representative compact and expanded layouts.

Verify light/status/navigation icon visibility.

Verify keyboard behavior.

Verify accessibility semantics for custom controls.

Report remaining limitations explicitly.

---

# Final Design Principle

ADA should feel like an intelligent presence living inside the device.

The interface should be visually distinctive when ADA is active and almost disappear when the user is reading, typing, or working.

Use atmosphere for identity.

Use typography for clarity.

Use motion for state.

Use glass for hierarchy.

Use color for attention.

Do not use visual effects simply because they are available.

---

## Implementation record — 2026-10-18 America/Phoenix

The presentation redesign is implemented as app19/0.25.1-ambient. Audit, design
tokens, screen/file map and usage are in [ANDROID-UI-REDESIGN](../docs/ANDROID-UI-REDESIGN.md).
Actual staged builds, unit/native-HTTP/emulator checks, corrected failures and
remaining physical/accessibility/performance gates are recorded in
[STATUS](STATUS.md) and [WORKLOG](WORKLOG.md). Existing backend/contracts,
controllers, journals, migrations and saved palette choices remain unchanged.
No normal app installation, deployment, later backend phase or new speech model.


The screenshot-driven compact follow-up moves chat features/options into menus and
dialogs, integrates the composer controls, and puts provisional replies in the
thread with reachable Stop. See the dated compact-refinement STATUS/WORKLOG and
updated guide for actual checks and remaining device verification.
