# Phase 25 — conversational curiosity and personal follow-up

Status: **Proposed; planning only.** Inputs: 20 scorecard, 14/15 owner settings/
continuity, 11 review, G-26/G-37.23 is preferred for relevance. Follow
[shared rules](FUTURE-ROADMAP.md). The user wants all three channels: questions
during chat, a later inbox, and occasional initiated conversations/notifications.
This phase implements chat/inbox; 27 provides durable timed delivery.

## Outcome

ADA sometimes carries the conversation by asking a thoughtful question, can pick
up a prior thread, and can get to know a new owner without demanding a form.
Personal topics are permitted. Owner controls decide topic depth, cadence and
channels. This does not authorize inferred sensitive dossiers or automatic memory.

## Checkpoints

- **A — topic and cadence controls.** Provide opt-in curiosity with topic choices
  such as interests, work, routines, relationships and deeper personal reflection;
  per-topic pause/block, a global off switch and configurable question frequency.
  Start with at most one question per reply and two unsolicited draft questions
  per owner/day as proposed bounds, not per-scope quotas that multiply silently.
  User-requested interview mode can explicitly change cadence. Skip, not now and
  do not ask again work without justification. Avoid repetitive questions.
- **B — active-chat questions.** First address the actual request; ask a follow-up
  when it is useful and permitted. A generic getting-to-know-you question needs no
  prior evidence. A personalized premise must link to accessible exact original
  evidence or be clearly framed as an uncertain question. Do not infer an emotional
  state, diagnosis, attraction, intimate fact or permission from a gap in memory.
  Support an owner-explicit conversation/interview intent, not only extraction.
- **C — later inbox.** Generate bounded question drafts/open threads with optional
  source pins, topic, reason category, expiry and deduplication key. Display only
  to the owner; provide answer/skip/dismiss/pause-topic controls. An inbox draft
  is not a sent assistant chat event. Starting a conversation from a draft uses
  an explicit durable operation ID and cannot invent a user-authored message.
  Source-less generic questions are labeled accordingly; stale premises expire.
- **D — memory and consent.** An answer is an ordinary owner statement with the
  existing source trust. Creating a durable assertion or interaction preference
  uses the current review/explicit setting path. Do not convert all answers into
  an automatically learned relationship or psychological profile. Respect
  corrections, erasure, scope changes and do-not-ask suppression. Retain only
  minimal topic/dedup metadata when a draft is dismissed, with disclosed lifetime.
- **E — channel handoff.** Expose a versioned question/draft contract that Phase 27 can
  schedule under fresh consent. No timers or push infrastructure here. Future
  notifications must be generic on lock screens, within owner-selected hours,
  rate-limited and revocable. The choice to plan all channels does not enable
  live notifications or decide exact hours/topics for the owner.

## Proposed data/interfaces

Owner/topic/channel policy, question draft and optional source lineage, delivery/
answer/dismiss receipt and bounded duplicate suppression. Freeze the relevant
policy/version and source pins for inspectable personalized questions. Include
private drafts/answers and topic preferences in erasure/backup/epoch inventory.
Server permission and factual retrieval remain independent of persona/warmth.
Admin gets operational metadata only. New in-chat wording uses a versioned opt-in
policy, preserving historical prompts, original snapshots and replay.

## Failures, evaluation and exit

Test a new owner with no memory, deep-personal topics enabled/disabled, stale or
deleted sources, wrong-owner pins, repeated dismissal, policy changes during
generation, duplicate opening/answering and late callbacks after logout. Include
prompt-injected sources asking to probe unrelated secrets. Check that concise/
task-focused mode can suppress follow-ups and that questions never block text chat.
Measure relevance, premise accuracy, repetition, accepted/skipped questions and
owner-rated helpfulness. Optimize usefulness, not conversation length or emotional
dependence. Do not manufacture concern, guilt, exclusivity or a claim that ADA
was privately thinking/feeling something that was never generated.

Exit with complete chat and inbox flows, inspectable personalization and reliable
topic/off controls. No scheduler, hidden profile, automatic endorsement or unsolicited
external message is implemented by this phase. Physical notification checks stay
deferred until a later selected validation window.
