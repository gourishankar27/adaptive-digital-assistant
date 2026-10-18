package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import dev.ada.assistant.data.*
import java.util.UUID
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable fun CuriosityScreen(controller: CuriosityController, conversation: ConversationDto?, profiles: List<PersonalityDto>, continueConversation: (UUID) -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    var topic by remember { mutableStateOf("interests") }
    var selected by remember { mutableStateOf<SourceVersionDto?>(null) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        AdaSectionHeading("Questions & curiosity")
        Text("Optional conversation starters. Answering does not save a fact or build a hidden profile. Timed delivery and notifications are unavailable.")
        s.notice?.let { Text(it, Modifier.testTag("curiosity-notice")) }
        if (s.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
        OutlinedButton(controller::refresh, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Check questions and settings") }
        s.policy?.let { policy ->
            var settings by remember(policy.revision) { mutableStateOf(policy.settings) }
            Row { Switch(settings.enabled, { settings = settings.copy(enabled = it) }, Modifier.testTag("curiosity-enabled")); Text("Allow curiosity") }
            Row { Checkbox(settings.chat_enabled, { settings = settings.copy(chat_enabled = it) }); Text("Questions after replies") }
            Row { Checkbox(settings.inbox_enabled, { settings = settings.copy(inbox_enabled = it) }); Text("Later inbox drafts") }
            Text("Question frequency")
            listOf("occasional" to "Every third reply", "rare" to "Every fifth reply", "every_reply" to "Each eligible reply").forEach { (key, label) ->
                Row { RadioButton(settings.frequency == key, { settings = settings.copy(frequency = key) }); Text(label) }
            }
            Row { Checkbox(settings.depth == "personal", { settings = settings.copy(depth = if (it) "personal" else "light") }); Text("Allow deeper personal questions in enabled topics") }
            curiosityTopics.forEach { name ->
                Text(name.replaceFirstChar(Char::titlecase))
                Row { listOf("enabled", "paused", "blocked").forEach { value ->
                    TextButton({ settings = settings.copy(topics = settings.topics + (name to value)) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (settings.topics[name] == value) "$value ✓" else value) }
                } }
            }
            Button({ controller.save(settings) }, enabled = !s.busy, modifier = Modifier.testTag("curiosity-save")) { Text("Save curiosity settings") }
            OutlinedButton(controller::off, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("curiosity-off")) { Text("Turn all curiosity off") }
            Text("At most one optional question per reply. Inbox: two drafts per owner/day across all scopes, UTC. Explicit interview requests: up to ten/day. Concise or explicit task-focused preferences suppress follow-ups.")
            Text("Turning off or changing the policy discards unanswered drafts. Skipped/dismissed text and source pins are removed. Duplicate metadata lasts 30 days; Do not ask again lasts until owner erasure. Historical answers and minimal receipts follow normal owner retention.")
            if (policy.settings.enabled && conversation != null) {
                Text("Later inbox — ${conversation.title}")
                curiosityTopics.forEach { name -> TextButton({ topic = name }, enabled = policy.settings.topics[name] == "enabled") { Text(if (topic == name) "$name ✓" else name) } }
                OutlinedButton({ controller.originals(conversation.scope_id) }) { Text("Choose an original statement (optional)") }
                s.originals.forEach { original -> TextButton({ selected = original }) { Text(original.content.take(120)) } }
                selected?.let { Text("Selected original statement; its exact saved span will be shown. This does not establish a current fact."); TextButton({ selected = null }) { Text("Use a generic question instead") } }
                Button({ controller.create(conversation.scope_id, topic, original = selected) }, enabled = !s.busy, modifier = Modifier.testTag("curiosity-create")) { Text("Prepare an inbox question") }
                OutlinedButton({ controller.create(conversation.scope_id, topic, interview = true, original = selected) }, enabled = !s.busy) { Text("Interview me: ask a question now") }
            }
        }
        s.pending.forEach { op -> Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
            Text("Saved ${op.kind} delivery: ${s.receipts[op.operationId]?.state ?: "unconfirmed"}")
            TextButton({ controller.check(op) }) { Text("Check original delivery") }
            TextButton({ controller.retry(op) }, enabled = !s.busy) { Text("Retry exact delivery explicitly") }
        } } }
        s.questions.forEach { q -> CuriosityQuestionCard(controller, q, profiles, continueConversation) }
        s.inspected?.let { Text("Verified original source"); SafeChatText(it.content, links = false) }
        s.answer?.let { Text("Saved ordinary reply"); SafeChatText(it.response ?: "The request has no completed response yet.", links = false) }
    }
}

@Composable private fun CuriosityQuestionCard(controller: CuriosityController, q: CuriosityQuestionDto, profiles: List<PersonalityDto>, continueConversation: ((UUID) -> Unit)? = null) {
    val state by controller.state.collectAsStateWithLifecycle()
    val answerPending = state.pending.any { it.kind == "answer" && it.questionId == q.id }
    val answerCompleted = q.answer_request_id != null || state.receipts.values.any { it.action == "answer" && it.question_id == q.id && it.state == "completed" }
    if (q.text == null) {
        if (q.state in setOf("expired", "stale", "revoked", "deferred")) Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small)) {
            Text("${q.topic}: ${q.state}. The question premise is not displayed.")
            TextButton({ controller.action(q, "dismiss") }) { Text("Dismiss this draft") }
        } }
        return
    }
    if (q.state !in setOf("pending", "offered", "opened", "answering", "answered")) return
    var answer by remember(q.id) { mutableStateOf("") }
    Card(Modifier.fillMaxWidth().testTag("curiosity-question")) { Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Optional question · ${q.topic}")
        SafeChatText(q.text, links = false)
        Text(if (q.source == null) "Generic conversation starter; no personal premise." else "Based on an owner-selected original statement; it may no longer be current.")
        Text("${q.state} · expires ${displayInstant(q.expires_at)}")
        (q.opened_conversation_id ?: q.conversation_id)?.let { cid -> if (continueConversation != null) TextButton({ continueConversation(cid) }) { Text("Continue in chat") } }
        q.source?.let { SafeChatText(it.quote, links = false); TextButton({ controller.inspect(q) }) { Text("Inspect exact original") } }
        if (q.state in setOf("pending", "offered", "opened")) {
            if (q.opened_conversation_id == null && q.conversation_id == null) {
                Text("Choose a style to start a conversation. Opening creates no user message.")
                profiles.forEach { p -> OutlinedButton({ controller.open(q, p.id) }, modifier = Modifier.testTag("curiosity-open")) { Text("Open with ${p.name}") } }
            } else if (!answerPending && !answerCompleted) {
                OutlinedTextField(answer, { answer = it }, label = { Text("Your answer (ordinary chat, no automatic memory)") }, modifier = Modifier.fillMaxWidth().testTag("curiosity-answer-text"))
                Button({ controller.answer(q, answer) }, enabled = answer.isNotBlank(), modifier = Modifier.testTag("curiosity-answer")) { Text("Send my answer") }
            }
            Row { TextButton({ controller.action(q, "skip") }) { Text("Skip") }; TextButton({ controller.action(q, "not_now") }) { Text("Not now (one hour)") } }
            TextButton({ controller.action(q, "dismiss") }) { Text("Dismiss") }
            TextButton({ controller.action(q, "dont_ask_again") }) { Text("Do not ask this again") }
            TextButton({ controller.action(q, "pause_topic") }) { Text("Pause this topic") }
        }
        if (answerPending || q.state == "answering") {
            Text("An answer delivery is saved. Check or retry its original delivery above. Dismissing this question does not cancel an admitted chat request.")
            TextButton({ controller.action(q, "dismiss") }) { Text("Dismiss this question") }
        }
        Row { TextButton({ controller.action(q, "helpful") }) { Text("Helpful") }; TextButton({ controller.action(q, "unhelpful") }) { Text("Not helpful") } }
    } }
}

@Composable fun CuriosityChatCard(controller: CuriosityController, request: UUID? = null, conversation: UUID? = null) {
    val s by controller.state.collectAsStateWithLifecycle()
    s.questions.filter { (request != null && it.request_id == request) || (conversation != null && it.opened_conversation_id == conversation) }.forEach { CuriosityQuestionCard(controller, it, emptyList()) }
}
