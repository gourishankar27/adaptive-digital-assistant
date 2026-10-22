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
import java.time.LocalDate
import java.time.Instant
import java.util.UUID

@OptIn(ExperimentalLayoutApi::class)
@Composable fun WorkScreen(controller: WorkController, openConversation: (UUID) -> Unit, openReminders: () -> Unit, openCuriosity: () -> Unit) {
    val s by controller.state.collectAsStateWithLifecycle()
    var project by remember { mutableStateOf("") }
    var day by remember { mutableStateOf(LocalDate.now().toString()) }
    var timezone by remember { mutableStateOf("America/Phoenix") }
    var followup by remember { mutableStateOf<WorkItemDto?>(null) }
    var followupTopic by remember { mutableStateOf("work") }
    var reminder by remember { mutableStateOf<WorkItemDto?>(null) }
    var afterSaveReminder by remember { mutableStateOf<UUID?>(null) }
    var reminderTime by remember { mutableStateOf("") }
    var reminderExpiry by remember { mutableStateOf("") }
    var reminderFold by remember { mutableStateOf("reject") }
    var forget by remember { mutableStateOf<WorkPending?>(null) }
    var historyOffset by remember(s.historyItem) { mutableIntStateOf(0) }
    LaunchedEffect(s.items,s.busy) { afterSaveReminder?.let { id -> s.items.firstOrNull { it.id==id }?.let { reminder=it; reminderTime=it.fields.due_local.orEmpty(); afterSaveReminder=null } } }
    followup?.let { row -> AdaConfirmation("Ask about this task?", "How would you like to follow up on: ${row.fields.description}? Topic: $followupTopic. Creates an optional Questions inbox draft under your current consent, without a user turn or factual memory.", "Prepare question", { followup=null }, { controller.followup(row,followupTopic); followup=null }, "work-followup") }
    forget?.let { op -> AdaConfirmation("Discard this recovery record?", "This removes only the local record. A saved task, question or reminder may still exist on the server. Check its result first.", "Discard local record", { forget=null }, { controller.forget(op); forget=null }, "work-forget") }
    LazyColumn(Modifier.fillMaxSize().testTag("work-screen"), contentPadding = PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            AdaSectionHeading("Projects & next actions")
            Text("Your explicit goals and tasks. Due dates never imply completion or a scheduled reminder. Briefs show current work; saved chat answers remain unchanged.")
            s.notice?.let { AdaNotice(it,Modifier.testTag("work-notice")) }
            if (s.busy) AdaLoading("Checking work")
            AdaOutlinedButton(controller::refresh, enabled=!s.busy) { Text("Refresh") }
            AdaSettingsGroup("Choose a personal or project scope", "work-scopes") {
                s.scopes.forEach { row -> AdaChoice(s.scope==row.id,"${row.name} · ${row.kind}",{ controller.selectScope(row.id) },Modifier.testTag("work-scope-${row.id}")) }
                Text("Up to 100 owned scopes are shown.")
                OutlinedTextField(project,{ project=it },label={ Text("New project name") },modifier=Modifier.fillMaxWidth().testTag("work-project-name"))
                AdaButton({ controller.project(project); project="" },enabled=project.isNotBlank() && project.length<=120 && !s.busy,modifier=Modifier.testTag("work-project-create")) { Text("Create project") }
            }
            if (s.scope!=null) FlowRow {
                AdaButton({ controller.begin("task") },enabled=!s.busy,modifier=Modifier.testTag("work-new-task")) { Text("New task") }
                AdaOutlinedButton({ controller.begin("goal") },enabled=!s.busy) { Text("New goal") }
            }
        }
        if (s.pending.isNotEmpty()) item { AdaSettingsGroup("Unconfirmed changes and reminder previews", "work-pending") { s.pending.forEach { op ->
            Text("Saved ${op.kind.replace('_',' ')} operation. Reopening has not resubmitted it.")
            op.scopeId?.let { id -> AdaTextButton({ controller.selectScope(id) }) { Text("Open original scope") } }
            AdaTextButton({ controller.check(op) },Modifier.testTag("work-check")) { Text("Check saved result") }
            AdaTextButton({ controller.retry(op) },enabled=!s.busy,modifier=Modifier.testTag("work-retry")) { Text("Retry original change") }
            AdaTextButton({ forget=op }) { Text("Discard local recovery record") }
        } } }
        s.draft?.let { draft -> item {
            Column(verticalArrangement=Arrangement.spacedBy(AdaSpacing.small)) {
                val f=draft.body.fields
                AdaSectionHeading(if (draft.body.expected_revision==0) "Review new ${f.kind}" else "Revise ${f.kind}")
                Text("Scope: ${s.scopes.firstOrNull { it.id==draft.scope }?.name ?: "Selected chat scope"}. Revision: ${draft.body.expected_revision}. Nothing is saved by editing.")
                OutlinedTextField(f.description,{ controller.fields(f.copy(description=it)) },label={ Text("Next action or goal") },modifier=Modifier.fillMaxWidth().testTag("work-description"))
                FlowRow { listOf("planned","done","deferred","unknown","dismissed").forEach { value -> AdaChoiceChip(f.status==value,value,{ controller.fields(f.copy(status=value)) }) } }
                if (f.kind=="task") {
                    Text("Optional parent goal (goals on this page)")
                    AdaChoice(f.goal_id==null,"No parent goal",{ controller.fields(f.copy(goal_id=null)) })
                    s.items.filter { it.fields.kind=="goal" && it.fields.status!="dismissed" }.forEach { g -> AdaChoice(f.goal_id==g.id,g.fields.description,{ controller.fields(f.copy(goal_id=g.id)) }) }
                }
                OutlinedTextField(f.due_local.orEmpty(),{ controller.fields(f.copy(due_local=it.ifBlank { null })) },label={ Text("Optional due time: YYYY-MM-DDTHH:mm") },modifier=Modifier.fillMaxWidth().testTag("work-due"))
                OutlinedTextField(f.timezone.orEmpty(),{ controller.fields(f.copy(timezone=it.ifBlank { null })) },label={ Text("Due timezone (IANA), or leave both blank") },modifier=Modifier.fillMaxWidth().testTag("work-timezone"))
                FlowRow { listOf("reject","first","second").forEach { value -> AdaChoiceChip(f.fold==value,"Repeated time: $value",{ controller.fields(f.copy(fold=value)) }) } }
                if (f.pins.isNotEmpty()) Text("${f.pins.size} exact original source link(s). Generated/imported material does not establish a fact or agreed commitment.")
                AdaToggle(draft.body.reminder_choice=="review_after_save","Review a reminder after Save (separate confirmation)",{ controller.reminderChoice(if(it) "review_after_save" else "none") })
                AdaButton(controller::prepare,enabled=!s.busy && f.description.isNotBlank(),modifier=Modifier.testTag("work-preview")) { Text("Review exact Save") }
                s.preview?.let { p ->
                    Text("Save ${f.kind}: ${f.description}\nStatus: ${f.status}\nDue: ${p.due_at?.let { Instant.ofEpochMilli(it) } ?: "None"}\nReminder: not scheduled · ${draft.body.reminder_choice.replace('_',' ')}\nOrigin: ${p.provenance.replace('_',' ')}",modifier=Modifier.testTag("work-exact-preview"))
                    p.sources.forEach { source -> Text("Original ${source.trust_class.replace('_',' ')} excerpt"); SafeChatText(source.evidence.quote,links=false) }
                    AdaButton({ if(draft.body.reminder_choice=="review_after_save") afterSaveReminder=draft.item; controller.save() },enabled=!s.busy,modifier=Modifier.testTag("work-save")) { Text("Confirm Save") }
                }
                AdaTextButton(controller::closeDraft) { Text("Close unsaved editor") }
            }
        } }
        if (s.scope!=null && s.items.isEmpty()) item { Text("No work on this page. Create a goal or a specific next action.") }
        items(s.items,key={ it.id }) { row ->
            Card(Modifier.fillMaxWidth().testTag("work-item-${row.id}")) { Column(Modifier.padding(AdaSpacing.medium),verticalArrangement=Arrangement.spacedBy(AdaSpacing.small)) {
                Text(row.fields.description,style=MaterialTheme.typography.titleMedium)
                Text("${row.fields.kind} · ${row.fields.status} · revision ${row.revision}${if (row.overdue) " · overdue" else ""}")
                Text("${row.provenance.replace('_',' ')}. Status records your choice, not independent verification.")
                row.due_at?.let { Text("Due ${Instant.ofEpochMilli(it)} · ${row.fields.timezone}") }
                AdaToggle(row.id in s.selected,"Include in project/day brief",{ controller.selectForBrief(row,it) },Modifier.testTag("work-select-${row.id}"))
                AdaOutlinedButton({ controller.edit(row) },enabled=!s.busy,modifier=Modifier.testTag("work-edit-${row.id}")) { Text("Edit status or action") }
                AdaTextButton({ controller.history(row); historyOffset=0 }) { Text("Revision history") }
                row.origin_conversation_id?.let { id -> AdaTextButton({ openConversation(id) }) { Text("Resume original conversation") } }
                AdaSettingsGroup("Original sources", "work-sources-${row.id}") { row.source_unavailable?.let { AdaNotice("Original source is unavailable. This task remains your explicitly saved work.") }; row.sources.forEach { Text("${it.source_origin} · ${it.trust_class}"); SafeChatText(it.evidence.quote,links=false) } }
                if (row.fields.status in setOf("planned","unknown")) {
                    FlowRow { listOf("work","routines").forEach { topic -> AdaChoiceChip(followupTopic==topic,topic,{ followupTopic=topic }) } }
                    AdaTextButton({ followup=row },enabled=!s.busy && s.questionPolicy?.settings?.enabled==true && s.questionPolicy?.settings?.topics?.get(followupTopic)=="enabled") { Text("Prepare optional follow-up") }
                }
                if (row.fields.status=="planned") AdaTextButton({ reminder=row; reminderTime=row.fields.due_local.orEmpty() },enabled=!s.busy) { Text("Review a reminder") }
                if (row.schedule_id!=null) Text("A linked reminder exists. Editing this work pauses it; rescheduling needs another preview and consent.")
            } }
        }
        if (s.scope!=null) item { Row { AdaTextButton({ controller.page(false) },enabled=s.offset>0 && !s.busy) { Text("Previous work") }; AdaTextButton({ controller.page(true) },enabled=s.items.size==50 && s.offset<150 && !s.busy) { Text("Next work") } } }
        if (s.historyItem!=null) item { AdaSettingsGroup("Original revision history", "work-history") {
            s.history.forEach { Text("Revision ${it.revision} · ${it.fields.status} · ${Instant.ofEpochMilli(it.created_at)}"); SafeChatText(it.fields.description,links=false) }
            AdaTextButton({ historyOffset=(historyOffset-100).coerceAtLeast(0); s.items.firstOrNull { it.id==s.historyItem }?.let { controller.history(it,historyOffset) } },enabled=historyOffset>0) { Text("Earlier history") }
            AdaTextButton({ historyOffset+=100; s.items.firstOrNull { it.id==s.historyItem }?.let { controller.history(it,historyOffset) } },enabled=s.history.size==100 && historyOffset<1900) { Text("Later history") }
        } }
        reminder?.let { row -> item { AdaSettingsGroup("Reminder preview for selected task", "work-reminder-editor") {
            Text(row.fields.description)
            Text("Uses separate Reminders consent. Only explicit confirmation schedules foreground-inbox delivery; no push/email/calendar action.")
            OutlinedTextField(timezone,{ timezone=it },label={ Text("Reminder IANA timezone") },modifier=Modifier.fillMaxWidth())
            OutlinedTextField(reminderTime,{ reminderTime=it },label={ Text("Start YYYY-MM-DDTHH:mm") },modifier=Modifier.fillMaxWidth())
            OutlinedTextField(reminderExpiry,{ reminderExpiry=it },label={ Text("Expiry ISO instant with offset") },modifier=Modifier.fillMaxWidth())
            FlowRow { listOf("reject","first","second").forEach { value -> AdaChoiceChip(reminderFold==value,"Repeated time: $value",{ reminderFold=value }) } }
            AdaButton({ controller.reminder(row,ScheduleDefinitionDto(text=row.fields.description,timezone=timezone,start_local=reminderTime,expires_at=reminderExpiry,fold=reminderFold,allowed_start=0,allowed_end=1440)) },enabled=!s.busy) { Text("Preview reminder time") }
            AdaTextButton({ reminder=null }) { Text("Close reminder editor") }
        } } }
        s.reminder?.schedule_preview?.let { preview -> item { AdaSettingsGroup("Exact reminder review", "work-reminder-preview") {
            Text(preview.definition?.text.orEmpty()); Text("Timezone: ${preview.definition?.timezone}")
            preview.occurrences.orEmpty().forEach { Text("${it.local} · ${Instant.ofEpochMilli(it.at)}") }
            Text("Preview expires: ${preview.preview_expires_at?.let { Instant.ofEpochMilli(it) }}. No reminder exists until confirmation.")
            AdaButton(controller::confirmReminder,enabled=!s.busy && s.schedulePolicy?.enabled==true,modifier=Modifier.testTag("work-reminder-confirm")) { Text("Confirm reminder") }
            AdaTextButton(openReminders) { Text("Open Reminders consent & inbox") }
        } } }
        item { AdaSettingsGroup("Balanced project/day brief", "work-brief-editor") {
            Text("${s.selected.size} selected items across ${s.selected.values.toSet().size} scopes; maximum 30 items/4 scopes. Select items across personal and project scopes above.")
            OutlinedTextField(day,{ day=it },label={ Text("Day YYYY-MM-DD") },modifier=Modifier.fillMaxWidth())
            OutlinedTextField(timezone,{ timezone=it },label={ Text("Day timezone (IANA)") },modifier=Modifier.fillMaxWidth())
            AdaButton({ controller.brief(day,timezone) },enabled=!s.busy && s.selected.isNotEmpty(),modifier=Modifier.testTag("work-create-brief")) { Text("Generate selected-work brief") }
            AdaTextButton(openReminders) { Text("Reminders & inbox") }; AdaTextButton(openCuriosity) { Text("Questions consent & inbox") }
        } }
        s.brief?.let { brief -> item { AdaSettingsGroup("Selected-work brief · ${brief.day}", "work-brief") {
            Text("Snapshot at ${Instant.ofEpochMilli(brief.created_at)}. Day groups due dates; status and overdue reflect snapshot time. ${brief.needs_decision} items need a decision. Task navigation, not factual evidence; original chat answers are unchanged.")
            brief.items.forEach { value ->
                Text("[${value.label}] ${value.task.fields.description}")
                Text("Scope: ${s.scopes.firstOrNull { it.id==value.task.scope_id }?.name ?: "Original selected scope"}")
                Text("${value.task.fields.status}${if (value.overdue) " · overdue" else ""}${if (value.due_on_day) " · due this day" else ""} · changed: ${value.changes.joinToString()}")
                value.task.source_unavailable?.let { Text("Original source unavailable; verify before relying on it.") }
                value.task.sources.forEach { Text("Original ${it.trust_class} source"); SafeChatText(it.evidence.quote,links=false) }
                value.task.origin_conversation_id?.let { id -> AdaTextButton({ openConversation(id) }) { Text("Resume original conversation") } }
            }
        } } }
    }
}
