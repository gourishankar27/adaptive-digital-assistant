package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID

@OptIn(ExperimentalLayoutApi::class)
@Composable fun ScheduleScreen(controller: ScheduleController, scopes: List<ScopeDto>, profiles: List<PersonalityDto>, continueConversation: (UUID) -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    var editing by remember(s.scopeId) { mutableStateOf<ScheduleDto?>(null) }
    var showForm by remember(s.scopeId) { mutableStateOf(false) }
    var deletion by remember { mutableStateOf<ScheduleDto?>(null) }
    var selectedProfile by remember(profiles) { mutableStateOf(profiles.firstOrNull()?.id) }
    deletion?.let { row -> AdaConfirmation("Delete this schedule?", "Further occurrences will be suppressed. Existing inbox items and receipts follow your saved-content retention policy.", "Delete schedule", { deletion = null }, { controller.action(row, "delete"); deletion = null }, "schedule-delete") }
    LazyColumn(Modifier.fillMaxSize().testTag("schedule-screen"), contentPadding = PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            AdaSectionHeading("Reminders & inbox")
            Text("Scope: ${scopes.firstOrNull { it.id == s.scopeId }?.name ?: "Choose an owned scope"}")
            Text("Private reminders and opted-in questions. In-app notices refresh while ADA is open. Background push and lock-screen messages are off; delivery can wait while the server or device is offline.")
            s.notice?.let { AdaNotice(it, Modifier.testTag("schedule-notice")) }
            if (s.busy) AdaLoading("Checking reminders")
            AdaOutlinedButton(controller::refresh, Modifier.testTag("schedule-refresh")) { Text("Refresh") }
            if (!s.supported) Text("This server does not support schedules.")
            s.policy?.let { policy ->
                AdaToggle(policy.enabled, "Allow scheduled reminders and questions", controller::setEnabled, Modifier.testTag("schedule-consent"), switch = true)
                if (!policy.globally_enabled) AdaNotice("The server dispatcher is stopped. You can review schedules; delivery resumes only after the operator enables it.")
                Text("Turning this off pauses all schedules. Turning it on requires reauthorizing each paused schedule. Curiosity topic consent is separate.")
            }
        }
        item {
            AdaSettingsGroup("Scope and conversation profile", "schedule-context") {
                scopes.forEach { row -> AdaChoice(s.scopeId == row.id, row.name, { editing = null; controller.activate(row.id) }) }
                Text("Profile for explicitly opened conversations")
                profiles.forEach { row -> AdaChoice(selectedProfile == row.id, row.name, { selectedProfile = row.id }) }
            }
            AdaButton({ editing = null; showForm = !showForm; controller.clearPreview() }, enabled = s.scopeId != null, modifier = Modifier.testTag("schedule-new")) { Text(if (showForm) "Close editor" else "New reminder or question") }
            if (s.scopeId == null) Text("Choose an owned scope to create or inspect a schedule.")
            if (showForm) ScheduleEditor(controller, editing, s.busy)
        }
        s.preview?.let { preview -> item {
            Surface(shape = MaterialTheme.shapes.medium, color = MaterialTheme.colorScheme.surfaceContainer) {
                Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    AdaSectionHeading("Review next occurrences")
                    Text(preview.definition?.text?.takeIf { it.isNotBlank() } ?: "Optional ${preview.definition?.topic} question")
                    preview.source?.let { source -> Text("Original user statement — evidence, not verified truth"); Text(source.quote) }
                    Text("Timezone: ${preview.definition?.timezone}. ${preview.timezone_data}. Allowed hours stay in this timezone when you travel; edits require a new preview.")
                    Text("Missed runs: only the latest eligible occurrence. No flood of old reminders. This creates an inbox item; it never sends a message as you.")
                    var all by remember(preview.operation_id) { mutableStateOf(false) }
                    val rows = preview.occurrences.orEmpty()
                    (if (all) rows else rows.take(5)).forEach { row -> Text("${row.local} · ${Instant.ofEpochMilli(row.at)} UTC") }
                    if (rows.size > 5) AdaTextButton({ all = !all }) { Text(if (all) "Show fewer" else "Show all ${rows.size} occurrences") }
                    AdaButton(controller::confirm, enabled = s.policy?.enabled == true && !s.busy, modifier = Modifier.testTag("schedule-confirm")) { Text("Confirm schedule") }
                }
            }
        } }
        if (s.pending.isNotEmpty()) item {
            AdaSettingsGroup("Unconfirmed changes (${s.pending.size})", "schedule-pending") {
                s.pending.forEach { op ->
                    Text("Saved ${if (op.kind == "preview") "preview" else "change"} awaiting confirmation")
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        if (op.kind == "preview") AdaTextButton({ controller.reviewPreview(op) }) { Text("Review saved preview") }
                        AdaTextButton({ controller.check(op) }) { Text("Check saved result") }
                        AdaTextButton({ controller.retry(op) }, enabled = !s.busy) { Text("Retry original change") }
                    }
                }
            }
        }
        item { AdaSectionHeading("Inbox · page ${s.inboxOffset / 100 + 1}"); if (s.inbox.isEmpty()) Text(if (s.inboxOffset == 0) "No deliveries yet. Refresh after an eligible run." else "No items on this page.") }
        items(s.inbox, key = { "inbox-${it.id}" }) { row ->
            Surface(shape = MaterialTheme.shapes.medium, color = MaterialTheme.colorScheme.surfaceContainerLow) {
                Column(Modifier.fillMaxWidth().padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text(if (row.kind == "curiosity_question") "Conversation starter" else "Reminder", style = MaterialTheme.typography.titleMedium)
                    Text(row.text ?: "Content is expired, snoozed or no longer available.")
                    Text(statusLabel(row.state))
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        if (row.text != null && row.state !in setOf("dismissed", "expired", "revoked")) {
                            AdaTextButton({ controller.inboxAction(row, "acknowledge") }, enabled = row.acknowledged_at == null && !s.busy) { Text("Acknowledge") }
                            AdaTextButton({ controller.inboxAction(row, "snooze") }, enabled = !s.busy) { Text("Snooze 1 hour") }
                            AdaTextButton({ controller.open(row, requireNotNull(selectedProfile)) }, enabled = selectedProfile != null && !s.busy, modifier = Modifier.testTag("schedule-open")) { Text("Open conversation") }
                        }
                        if (row.state != "dismissed") AdaTextButton({ controller.inboxAction(row, "dismiss") }, enabled = !s.busy) { Text("Dismiss") }
                        val opened = row.opened_conversation_id ?: s.receipts.values.lastOrNull { it.item_id == row.id && it.action == "open" }?.conversation_id
                        if (opened != null) AdaTextButton({ continueConversation(opened) }) { Text("Continue conversation") }
                    }
                }
            }
        }
        item {
            FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                AdaTextButton({ controller.inboxPage(false) }, enabled = s.inboxOffset > 0 && !s.busy) { Text("Newer inbox items") }
                AdaTextButton({ controller.inboxPage(true) }, enabled = s.inbox.size == 100 && s.inboxOffset < 900 && !s.busy) { Text("Older inbox items") }
            }
            AdaSectionHeading("Schedules"); if (s.schedules.isEmpty()) Text("No schedules in this scope.")
        }
        items(s.schedules, key = { "schedule-${it.id}" }) { row ->
            Surface(shape = MaterialTheme.shapes.medium, color = MaterialTheme.colorScheme.surfaceContainerLow) {
                Column(Modifier.fillMaxWidth().padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text(row.definition?.text?.takeIf { it.isNotBlank() } ?: row.definition?.topic?.let { "Optional $it question" } ?: "Deleted schedule")
                    Text("${statusLabel(row.state)} · ${row.delivered} delivered · ${row.missed} missed")
                    row.next_at?.let { Text("Next scheduled instant: ${Instant.ofEpochMilli(it)}") }
                    row.reason?.let { Text(statusLabel(it)) }
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        if (row.state != "deleted") {
                            AdaTextButton({ editing = row; showForm = true; controller.clearPreview() }) { Text("Edit") }
                            if (row.state == "active") AdaTextButton({ controller.action(row, "pause") }, enabled = !s.busy) { Text("Pause") }
                            if (row.state in setOf("paused", "quarantined")) AdaTextButton({ controller.action(row, "reauthorize") }, enabled = s.policy?.enabled == true && !s.busy) { Text("Reauthorize") }
                            if (row.state == "active") AdaTextButton({ controller.action(row, "snooze") }, enabled = !s.busy) { Text("Snooze 1 hour") }
                            AdaTextButton({ deletion = row }, enabled = !s.busy) { Text("Delete") }
                        }
                        AdaTextButton({ controller.inspect(row) }) { Text("Delivery receipts") }
                    }
                }
            }
        }
        if (s.occurrences.isNotEmpty()) item {
            AdaSettingsGroup("Delivery receipts", "schedule-receipts") {
                s.occurrences.forEach { row -> Text("${Instant.ofEpochMilli(row.scheduled_for)} · ${statusLabel(row.state)}${row.reason?.let { " · ${statusLabel(it)}" } ?: ""}") }
                FlowRow {
                    AdaTextButton({ controller.occurrencePage(false) }, enabled = s.occurrenceOffset > 0) { Text("Newer receipts") }
                    AdaTextButton({ controller.occurrencePage(true) }, enabled = s.occurrences.size == 100 && s.occurrenceOffset < 900) { Text("Older receipts") }
                }
                Text("Acknowledged means ADA recorded your acknowledgement. It is not proof of push delivery or that someone read a notification.")
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable private fun ScheduleEditor(controller: ScheduleController, editing: ScheduleDto?, busy: Boolean) {
    val key = editing?.id
    val original = editing?.definition
    var kind by remember(key) { mutableStateOf(original?.kind ?: "reminder") }
    var message by remember(key) { mutableStateOf(original?.text ?: "") }
    var topic by remember(key) { mutableStateOf(original?.topic ?: "interests") }
    var timezone by remember(key) { mutableStateOf(original?.timezone ?: ZoneId.systemDefault().id) }
    var local by remember(key) { mutableStateOf(original?.start_local ?: LocalDateTime.now().plusMinutes(5).format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm"))) }
    var frequency by remember(key) { mutableStateOf(original?.frequency ?: "once") }
    var count by remember(key) { mutableStateOf((original?.count ?: 1).toString()) }
    var fold by remember(key) { mutableStateOf(original?.fold ?: "reject") }
    var gap by remember(key) { mutableStateOf(original?.gap ?: "skip") }
    var start by remember(key) { mutableStateOf("%02d:%02d".format((original?.allowed_start ?: 480) / 60, (original?.allowed_start ?: 480) % 60)) }
    var end by remember(key) { mutableStateOf("%02d:%02d".format((original?.allowed_end ?: 1320) / 60, (original?.allowed_end ?: 1320) % 60)) }
    var expiry by remember(key) { mutableStateOf(original?.expires_at ?: Instant.ofEpochMilli(System.currentTimeMillis() + 30 * 86400000L).toString()) }
    var error by remember(key) { mutableStateOf<String?>(null) }
    fun changed() { controller.clearPreview(); error = null }
    fun minutes(value: String): Int { require(value.matches(Regex("\\d\\d:\\d\\d"))); val parts = value.split(":").map { it.toInt() }; require(parts[0] in 0..24 && parts[1] in 0..59 && (parts[0] < 24 || parts[1] == 0)); return parts[0] * 60 + parts[1] }
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text(if (editing == null) "New schedule" else "Edit schedule", style = MaterialTheme.typography.titleMedium)
        FlowRow { listOf("reminder" to "Reminder", "curiosity_question" to "Optional question").forEach { (value, label) -> AdaChoiceChip(kind == value, label, { kind = value; changed() }) } }
        if (kind == "reminder") OutlinedTextField(message, { message = it; changed() }, label = { Text("Reminder text") }, modifier = Modifier.fillMaxWidth().testTag("schedule-text"))
        else {
            Text("Existing curiosity topic/depth consent and daily limits still apply. Enable those separately in Questions & curiosity.")
            FlowRow { curiosityTopics.forEach { value -> AdaChoiceChip(topic == value, value.replaceFirstChar(Char::titlecase), { topic = value; changed() }) } }
        }
        OutlinedTextField(timezone, { timezone = it; changed() }, label = { Text("IANA timezone, e.g. America/Phoenix") }, modifier = Modifier.fillMaxWidth().testTag("schedule-timezone"))
        OutlinedTextField(local, { local = it; changed() }, label = { Text("Local start: YYYY-MM-DDTHH:mm") }, modifier = Modifier.fillMaxWidth().testTag("schedule-local"))
        FlowRow { listOf("once", "daily", "weekly").forEach { value -> AdaChoiceChip(frequency == value, value.replaceFirstChar(Char::titlecase), { frequency = value; changed() }) } }
        if (frequency != "once") OutlinedTextField(count, { count = it; changed() }, label = { Text("Occurrences, 1–100") }, modifier = Modifier.fillMaxWidth())
        AdaSettingsGroup("Allowed hours, expiry and DST", "schedule-calendar-options") {
            OutlinedTextField(start, { start = it; changed() }, label = { Text("Allowed from (HH:mm)") }, modifier = Modifier.fillMaxWidth().testTag("schedule-hours-start"))
            OutlinedTextField(end, { end = it; changed() }, label = { Text("Allowed until, exclusive (HH:mm)") }, modifier = Modifier.fillMaxWidth().testTag("schedule-hours-end"))
            OutlinedTextField(expiry, { expiry = it; changed() }, label = { Text("Expiry, ISO 8601 with timezone") }, modifier = Modifier.fillMaxWidth())
            Text("Repeated autumn time")
            listOf("reject" to "Ask me to choose", "first" to "First occurrence", "second" to "Second occurrence").forEach { (value, label) -> AdaChoice(fold == value, label, { fold = value; changed() }) }
            Text("Missing spring time")
            AdaChoice(gap == "skip", "Skip that recurring occurrence", { gap = "skip"; changed() })
            AdaChoice(gap == "reject", "Reject the schedule for review", { gap = "reject"; changed() })
            Text("A missing one-time local time is always rejected. Times stay in the chosen timezone; travel never silently changes them.")
        }
        error?.let { AdaNotice(it, error = true) }
        AdaButton({
            try {
                val number = if (frequency == "once") 1 else count.toInt()
                val a = minutes(start); val b = minutes(end)
                require(number in 1..100 && a < b && a < 1440 && b <= 1440)
                LocalDateTime.parse(local); ZoneId.of(timezone); require(java.time.OffsetDateTime.parse(expiry).nano % 1000000 == 0)
                require(kind != "reminder" || (message.isNotBlank() && message.codePointCount(0, message.length) <= 1000))
                controller.preview(ScheduleDefinitionDto(kind = kind, text = if (kind == "reminder") message else "", topic = if (kind == "curiosity_question") topic else null,
                    source = if (kind == "curiosity_question") original?.source else null, timezone = timezone, start_local = local,
                    frequency = frequency, count = number, fold = fold, gap = gap, allowed_start = a, allowed_end = b, expires_at = expiry), editing)
            } catch (_: Exception) { error = "Check the reminder text, local date/time, IANA timezone, allowed hours, occurrence count and expiry." }
        }, enabled = !busy, modifier = Modifier.testTag("schedule-preview")) { Text("Preview occurrences") }
    }
}
