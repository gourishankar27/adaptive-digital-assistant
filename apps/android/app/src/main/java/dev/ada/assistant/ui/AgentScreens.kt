package dev.ada.assistant.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.*

@Composable
fun AgentScreen(controller: AgentController, conversation: ConversationDto?, account: AccountSummary?) {
    val s by controller.state.collectAsStateWithLifecycle()
    var approval by remember { mutableStateOf<AgentStepDto?>(null) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text("Read-only tools", style = MaterialTheme.typography.headlineSmall)
        Text("Calculator, memory lookup and exact source lookup. Each tool request needs your approval. Results are evidence; they do not save memory.")
        if (!s.enabled) Text("This server does not support the selected tool protocol.")
        s.notice?.let { Text(it) }
        if (s.busy) { LinearProgressIndicator(Modifier.fillMaxWidth()); Text("Checking the tool session…") }
        val p = s.journal
        if (p == null) {
            OutlinedTextField(s.task, controller::task, Modifier.fillMaxWidth().testTag("agent-task"), label = { Text("Task") }, enabled = s.enabled && !s.busy)
            OutlinedTextField(s.asOf, controller::asOf, Modifier.fillMaxWidth(), label = { Text("As of (optional ISO time)") }, enabled = s.enabled && !s.busy)
            selectedAgentTools.forEach { name -> Row(Modifier.fillMaxWidth()) { Checkbox(name in s.tools, { controller.toggleTool(name) }, enabled = s.enabled && !s.busy); Text(name, Modifier.padding(top = 12.dp)) } }
            Text("Scope: ${conversation?.scope_id ?: "Open a conversation first"}")
            Button({ conversation?.let(controller::start) }, enabled = s.enabled && !s.busy && conversation?.prompt_version in setOf("ada-baseline-v3", "ada-baseline-v4"), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-start")) { Text("Request tool session") }
            if (conversation != null && conversation.prompt_version !in setOf("ada-baseline-v3", "ada-baseline-v4")) Text("Explicitly upgrade this conversation's prompt before using tools.")
        } else {
            Text("Account: ${account?.name ?: p.identity.owner}")
            Text("Server: ${p.identity.server}")
            Text("Scope: ${p.scopeId}")
            Text("Run: ${p.runId}")
            val run = s.run
            run?.let { Text("As of UTC milliseconds: ${it.as_of}") }
            Text("State: ${run?.status ?: "unconfirmed"}", Modifier.testTag("agent-state"))
            run?.error_code?.let { Text("Failure code: $it") }
            if (run?.status == "completed") { Text("Model answer (untrusted)"); Text(run.response ?: "No answer recorded") }
            run?.steps?.forEach { step ->
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text("Step ${step.number}: ${step.status}")
                    step.tool?.let { Text("Tool: $it · ${step.tool_version}") }
                    step.arguments?.let { Text("Exact arguments"); Text(it.toString(), Modifier.testTag("agent-arguments")) }
                    step.expires_at?.let { Text("Approval expires at UTC milliseconds: $it") }
                    if (step.status == "pending_approval") {
                        Text("Effect: read or calculate within this run's scope. No external write.")
                        Button({ approval = step }, enabled = s.enabled && !s.busy && p.operation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-preview")) { Text("Review approval") }
                        OutlinedButton({ controller.decide(step, false) }, enabled = s.enabled && !s.busy && p.operation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-deny")) { Text("Deny request") }
                    }
                    step.receipt?.let { r -> Text("Receipt ${r.id}"); Text("Outcome: ${r.outcome}", Modifier.testTag("agent-receipt")); Text("${r.origin} · ${r.trust_class}"); r.result?.let { Text(it.toString()) }; r.error_code?.let { Text("Failure code: $it") } }
                } }
            }
            OutlinedButton(controller::check, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-check")) { Text("Check saved run") }
            if (p.operation != null || run == null) OutlinedButton(controller::retry, enabled = s.enabled && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-retry")) { Text("Retry exact saved operation") }
            if (run?.status == "running" && p.operation == null) OutlinedButton(controller::recover, enabled = s.enabled && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Mark interrupted after lease expires") }
            if (run?.status in setOf("completed", "failed", "unknown") && p.operation == null) Button(controller::closeCompleted, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Close session") }
        }
    }
    approval?.let { step -> AlertDialog(onDismissRequest = { approval = null }, title = { Text("Approve this exact read-only request?") }, text = {
        Column(Modifier.verticalScroll(rememberScrollState())) { Text("Account: ${account?.name}\nServer: ${s.journal?.identity?.server}\nScope: ${s.journal?.scopeId}\nAs of UTC milliseconds: ${s.run?.as_of}\nTool: ${step.tool}\nVersion: ${step.tool_version}"); Text(step.arguments.toString()); Text("Effect: scoped read or calculation. Approval binds this preview and expires. It cannot authorize an external write.") }
    }, confirmButton = { TextButton({ approval = null; controller.decide(step, true) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-approve")) { Text("Approve exact request") } }, dismissButton = { TextButton({ approval = null }) { Text("Back") } }) }
}
