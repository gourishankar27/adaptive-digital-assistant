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
fun AgentScreen(controller: AgentController, conversation: ConversationDto?, account: AccountSummary?, scopeName: String? = null) {
    val s by controller.state.collectAsStateWithLifecycle()
    var approval by remember { mutableStateOf<AgentStepDto?>(null) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        AdaSectionHeading("Read-only tools")
        if (s.run?.status == "running") Row { AdaPresence(AdaPresenceState.Acting, Modifier.size(AdaLayout.presence)); Text(AdaPresenceState.Acting.label) }
        Text("Calculator, memory lookup and exact source lookup. Each tool request needs your approval. Results are evidence; they do not save memory.")
        if (!s.enabled) Text("This server does not support the selected tool protocol.")
        s.fault?.let { AdaFailureNotice(it) }
        s.notice?.let { AdaNotice(it) }
        if (s.busy) { AdaLoading("Checking the tool session"); Text("Checking the tool session…") }
        val p = s.journal
        if (p == null) {
            OutlinedTextField(s.task, controller::task, Modifier.fillMaxWidth().testTag("agent-task"), label = { Text("Task") }, enabled = s.enabled && !s.busy)
            OutlinedTextField(s.asOf, controller::asOf, Modifier.fillMaxWidth(), label = { Text("As of (optional ISO time)") }, enabled = s.enabled && !s.busy)
            selectedAgentTools.forEach { name -> AdaToggle(name in s.tools, toolLabel(name), { controller.toggleTool(name) }, enabled = s.enabled && !s.busy) }
            Text(conversation?.let { "Scope: ${scopeName ?: "Saved conversation scope"}" } ?: "Open a conversation first")
            AdaButton({ conversation?.let(controller::start) }, enabled = s.enabled && !s.busy && conversation?.prompt_version in setOf("ada-baseline-v3", "ada-baseline-v4"), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-start")) { Text("Request tool session") }
            if (conversation != null && conversation.prompt_version !in setOf("ada-baseline-v3", "ada-baseline-v4")) Text("Explicitly upgrade this conversation's prompt before using tools.")
        } else {
            Text("Account: ${account?.name ?: "Verified account"}")
            Text("Server: ${p.identity.server}")
            Text("Scope: ${scopeName ?: "Saved session scope"}")
            AdaTechnicalDetails("Owner: ${p.identity.owner}\nScope: ${p.scopeId}\nRun: ${p.runId}\nState: ${s.run?.status}\nFailure code: ${s.run?.error_code ?: "none"}")
            val run = s.run
            run?.let { Text("As of: ${displayInstant(it.as_of)}") }
            Text("State: ${statusLabel(run?.status)}", Modifier.testTag("agent-state"))
            if (run?.status == "completed") { Text("Model answer (untrusted)"); Text(run.response ?: "No answer recorded") }
            run?.steps?.forEach { step ->
                Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text("Step ${step.number}: ${statusLabel(step.status)}")
                    step.tool?.let { Text("Tool: ${toolLabel(it)}") }
                    step.arguments?.let { Text("Exact arguments"); Text(it.toString(), Modifier.testTag("agent-arguments")) }
                    step.expires_at?.let { Text("Approval expires: ${displayInstant(it)}") }
                    if (step.status == "pending_approval") {
                        Text("Effect: read or calculate within this run's scope. No external write.")
                        AdaButton({ approval = step }, enabled = s.enabled && !s.busy && p.operation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-preview")) { Text("Review approval") }
                        AdaOutlinedButton({ controller.decide(step, false) }, enabled = s.enabled && !s.busy && p.operation == null, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-deny")) { Text("Deny request") }
                    }
                    step.receipt?.let { r -> Text("Outcome: ${statusLabel(r.outcome)}", Modifier.testTag("agent-receipt")); Text(trustLabel(r.trust_class)); r.result?.let { Text(it.toString()) }; AdaTechnicalDetails("Receipt: ${r.id}\nOrigin: ${r.origin}\nTrust: ${r.trust_class}\nOutcome: ${r.outcome}\nFailure code: ${r.error_code ?: "none"}") }
                } }
            }
            AdaOutlinedButton(controller::check, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-check")) { Text("Check saved run") }
            if (p.operation != null || run == null) AdaOutlinedButton(controller::retry, enabled = s.enabled && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-retry")) { Text("Retry exact saved operation") }
            if (run?.status == "running" && p.operation == null) AdaOutlinedButton(controller::recover, enabled = s.enabled && !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Mark interrupted after lease expires") }
            if (run?.status in setOf("completed", "failed", "unknown") && p.operation == null) AdaButton(controller::closeCompleted, enabled = !s.busy, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Close session") }
        }
    }
    approval?.let { step -> AlertDialog(onDismissRequest = { approval = null }, title = { Text("Approve this exact read-only request?") }, text = {
        Column(Modifier.verticalScroll(rememberScrollState())) { Text("Account: ${account?.name}\nServer: ${s.journal?.identity?.server}\nScope: ${s.journal?.scopeId}\nAs of UTC milliseconds: ${s.run?.as_of}\nTool: ${step.tool}\nVersion: ${step.tool_version}"); Text(step.arguments.toString()); Text("Effect: scoped read or calculation. Approval binds this preview and expires. It cannot authorize an external write.") }
    }, confirmButton = { AdaTextButton({ approval = null; controller.decide(step, true) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("agent-approve")) { Text("Approve exact request") } }, dismissButton = { AdaTextButton({ approval = null }) { Text("Back") } }) }
}
