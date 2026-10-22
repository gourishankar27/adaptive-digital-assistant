package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import dev.ada.assistant.data.*
import java.util.UUID
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@OptIn(ExperimentalLayoutApi::class)
@Composable fun CuriosityScreen(controller: CuriosityController, conversation: ConversationDto?, profiles: List<PersonalityDto>, continueConversation: (UUID) -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    var topic by remember { mutableStateOf("interests") }
    var selected by remember { mutableStateOf<SourceVersionDto?>(null) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        AdaSectionHeading("Questions & curiosity")
        Text("Optional conversation starters. Answering does not save a fact or build a hidden profile. Supported servers offer timed delivery separately under Reminders & inbox. Background push is off.")
        s.notice?.let { AdaNotice(it, Modifier.testTag("curiosity-notice")) }
        if (s.busy) AdaLoading("Checking questions and settings")
        AdaOutlinedButton(controller::refresh, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Check questions and settings") }
        if (!s.busy && s.policy == null) Text(if (!s.supported) "This server does not offer Questions & curiosity." else "Questions and settings are not loaded. Use Check questions and settings to try again.")
        s.policy?.let { policy ->
            var settings by remember(policy.revision) { mutableStateOf(policy.settings) }
            AdaToggle(settings.enabled, "Allow curiosity", { settings = settings.copy(enabled = it) }, Modifier.testTag("curiosity-enabled"), switch = true)
            AdaToggle(settings.chat_enabled, "Questions after replies", { settings = settings.copy(chat_enabled = it) })
            AdaToggle(settings.inbox_enabled, "Later inbox drafts", { settings = settings.copy(inbox_enabled = it) })
            Text("Question frequency")
            listOf("occasional" to "Every third reply", "rare" to "Every fifth reply", "every_reply" to "Each eligible reply").forEach { (key, label) ->
                AdaChoice(settings.frequency == key, label, { settings = settings.copy(frequency = key) })
            }
            AdaToggle(settings.depth == "personal", "Allow deeper personal questions in enabled topics", { settings = settings.copy(depth = if (it) "personal" else "light") })
            curiosityTopics.forEach { name ->
                Text(name.replaceFirstChar(Char::titlecase))
                FlowRow(Modifier.selectableGroup(), horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { listOf("enabled", "paused", "blocked").forEach { value ->
                    AdaChoiceChip(settings.topics[name] == value, statusLabel(value), { settings = settings.copy(topics = settings.topics + (name to value)) })
                } }
            }
            AdaButton({ controller.save(settings) }, enabled = !s.busy, modifier = Modifier.testTag("curiosity-save")) { Text("Save curiosity settings") }
            AdaOutlinedButton(controller::off, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("curiosity-off")) { Text("Turn all curiosity off") }
            Text("At most one optional question per reply. Inbox: two drafts per owner/day across all scopes, UTC. Explicit interview requests: up to ten/day. Concise or explicit task-focused preferences suppress follow-ups.")
            Text("Turning off or changing the policy discards unanswered drafts. Skipped/dismissed text and source pins are removed. Duplicate metadata lasts 30 days; Do not ask again lasts until owner erasure. Historical answers and minimal receipts follow normal owner retention.")
            if (policy.settings.enabled && conversation != null) {
                Text("Later inbox — ${conversation.title}")
                FlowRow(Modifier.selectableGroup(), horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { curiosityTopics.forEach { name -> AdaChoiceChip(topic == name, name.replaceFirstChar(Char::titlecase), { topic = name }, enabled = policy.settings.topics[name] == "enabled") } }
                AdaOutlinedButton({ controller.originals(conversation.scope_id) }) { Text("Choose an original statement (optional)") }
                s.originals.forEach { original -> AdaChoice(selected?.id == original.id, original.content.take(120), { selected = original }) }
                selected?.let { Text("Selected original statement; its exact saved span will be shown. This does not establish a current fact."); AdaTextButton({ selected = null }) { Text("Use a generic question instead") } }
                AdaButton({ controller.create(conversation.scope_id, topic, original = selected) }, enabled = !s.busy, modifier = Modifier.testTag("curiosity-create")) { Text("Prepare an inbox question") }
                AdaOutlinedButton({ controller.create(conversation.scope_id, topic, interview = true, original = selected) }, enabled = !s.busy) { Text("Interview me: ask a question now") }
            }
        }
        s.pending.forEach { op -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
            Text("Saved ${op.kind} delivery: ${statusLabel(s.receipts[op.operationId]?.state)}")
            AdaTextButton({ controller.check(op) }) { Text("Check original delivery") }
            AdaTextButton({ controller.retry(op) }, enabled = !s.busy) { Text("Retry exact delivery explicitly") }
        } } }
        s.questions.forEach { q -> CuriosityQuestionCard(controller, q, profiles, continueConversation) }
        s.inspected?.let { Text("Verified original source"); SafeChatText(it.content, links = false) }
        s.answer?.let { Text("Saved ordinary reply"); SafeChatText(it.response ?: "The request has no completed response yet.", links = false) }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable private fun CuriosityQuestionCard(controller: CuriosityController, q: CuriosityQuestionDto, profiles: List<PersonalityDto>, continueConversation: ((UUID) -> Unit)? = null) {
    val state by controller.state.collectAsStateWithLifecycle()
    val answerPending = state.pending.any { it.kind == "answer" && it.questionId == q.id }
    val answerCompleted = q.answer_request_id != null || state.receipts.values.any { it.action == "answer" && it.question_id == q.id && it.state == "completed" }
    if (q.text == null) {
        if (q.state in setOf("expired", "stale", "revoked", "deferred")) Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
            Text("${q.topic}: ${statusLabel(q.state)}. The question premise is not displayed.")
            AdaTextButton({ controller.action(q, "dismiss") }) { Text("Dismiss this draft") }
        } }
        return
    }
    if (q.state !in setOf("pending", "offered", "opened", "answering", "answered")) return
    var answer by remember(q.id) { mutableStateOf("") }
    Card(Modifier.fillMaxWidth().testTag("curiosity-question")) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Optional question · ${q.topic}")
        SafeChatText(q.text, links = false)
        Text(if (q.source == null) "Generic conversation starter; no personal premise." else "Based on an owner-selected original statement; it may no longer be current.")
        Text("${statusLabel(q.state)} · expires ${displayInstant(q.expires_at)}")
        (q.opened_conversation_id ?: q.conversation_id)?.let { cid -> if (continueConversation != null) AdaTextButton({ continueConversation(cid) }) { Text("Continue in chat") } }
        q.source?.let { SafeChatText(it.quote, links = false); AdaTextButton({ controller.inspect(q) }) { Text("Inspect exact original") } }
        if (q.state in setOf("pending", "offered", "opened")) {
            if (q.opened_conversation_id == null && q.conversation_id == null) {
                Text("Choose a style to start a conversation. Opening creates no user message.")
                profiles.forEach { p -> AdaOutlinedButton({ controller.open(q, p.id) }, modifier = Modifier.testTag("curiosity-open")) { Text("Open with ${p.name}") } }
            } else if (!answerPending && !answerCompleted) {
                OutlinedTextField(answer, { answer = it }, label = { Text("Your answer (ordinary chat, no automatic memory)") }, modifier = Modifier.fillMaxWidth().testTag("curiosity-answer-text"))
                AdaButton({ controller.answer(q, answer) }, enabled = answer.isNotBlank(), modifier = Modifier.testTag("curiosity-answer")) { Text("Send my answer") }
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { AdaTextButton({ controller.action(q, "skip") }) { Text("Skip") }; AdaTextButton({ controller.action(q, "not_now") }) { Text("Not now (one hour)") } }
            AdaTextButton({ controller.action(q, "dismiss") }) { Text("Dismiss") }
            AdaTextButton({ controller.action(q, "dont_ask_again") }) { Text("Do not ask this again") }
            AdaTextButton({ controller.action(q, "pause_topic") }) { Text("Pause this topic") }
        }
        if (answerPending || q.state == "answering") {
            Text("An answer delivery is saved. Check or retry its original delivery above. Dismissing this question does not cancel an admitted chat request.")
            AdaTextButton({ controller.action(q, "dismiss") }) { Text("Dismiss this question") }
        }
        FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { AdaTextButton({ controller.action(q, "helpful") }) { Text("Helpful") }; AdaTextButton({ controller.action(q, "unhelpful") }) { Text("Not helpful") } }
    } }
}

@Composable fun CuriosityChatCard(controller: CuriosityController, request: UUID? = null, conversation: UUID? = null) {
    val s by controller.state.collectAsStateWithLifecycle()
    s.questions.filter { (request != null && it.request_id == request) || (conversation != null && it.opened_conversation_id == conversation) }.forEach { CuriosityQuestionCard(controller, it, emptyList()) }
}
