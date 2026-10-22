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

/** Candidate quality failed: no model activation, automatic downloads or chat insertion. */
@Composable fun EdgeScreen(controller: EdgeController) {
    val s by controller.state.collectAsStateWithLifecycle()
    var confirm by remember { mutableStateOf<Pair<String, () -> Unit>?>(null) }
    confirm?.let { (message, action) -> AdaConfirmation("Review device operation",message,"Confirm",{ confirm=null },{ confirm=null;action() },"edge-confirm") }
    LazyColumn(Modifier.fillMaxSize().testTag("edge-screen"),contentPadding=PaddingValues(AdaSpacing.medium),verticalArrangement=Arrangement.spacedBy(AdaSpacing.medium)) {
        item {
            AdaSectionHeading("Device drafts")
            Text("Local drafting is disabled. Both measured models missed required reply constraints. Network chat remains available; no model is downloaded automatically.")
            Text("A device draft is generated text, never a server reply, factual memory or permission to act. Device registration authorizes only reviewed draft synchronization.")
            s.notice?.let { AdaNotice(it) }
            if(s.busy) AdaLoading("Checking device draft")
            AdaOutlinedButton(controller::refresh,enabled=!s.busy) { Text("Refresh") }
            if(s.supported) AdaButton({ confirm="Register this installation's signing key for your account? This does not approve model output or enable local generation." to controller::enroll },enabled=!s.busy && !controller.isRegistered(),modifier=Modifier.testTag("edge-enroll")) { Text(if(controller.isRegistered()) "Device registered" else "Register device") }
        }
        items(s.devices,key={ it.id }) { row -> AdaSettingsGroup(row.label,"edge-device-${row.id}") {
            Text(if(row.revoked_at==null) "Registered · sequence ${row.last_sequence}" else "Revoked")
            if(row.revoked_at==null) AdaOutlinedButton({ confirm="Revoke this device? Unsynchronized and saved drafts from it become stale. This does not delete other devices or promote any output." to { controller.revoke(row) } },enabled=!s.busy) { Text("Revoke") }
        } }
        s.draft?.let { draft -> item { AdaSettingsGroup("Recovered local generated draft","edge-local") {
            Text(draft.output);Text("${draft.modelId} · ${if(draft.truncated) "length limit reached" else "generated draft"}")
            s.scopes.forEach { row -> AdaChoice(s.scope==row.id,row.name,{ controller.selectScope(row.id) }) }
            AdaButton({ confirm="Save this exact generated text and its input to the selected scope as an untrusted device draft? This will not send a chat message or create factual memory." to controller::sync },enabled=s.scope==draft.scopeId && !s.busy && s.pending.none{it.kind=="sync"}) { Text("Review and save draft") }
        } } }
        s.receipt?.let { row -> item { AdaSettingsGroup("Saved device draft","edge-receipt") { Text(row.output);Text("Generated on device · untrusted draft · ${row.model_id}") } } }
        items(s.pending,key={it.operationId}) { op -> AdaSettingsGroup("Unconfirmed ${op.kind}","edge-pending-${op.operationId}") {
            Text("Restart checks the original result only. Retry sends the identical saved operation. Discard removes only this local recovery record.")
            AdaOutlinedButton({controller.check(op)},enabled=!s.busy) { Text("Check result") }
            AdaOutlinedButton({confirm="Retry the exact saved ${op.kind} operation?" to {controller.retry(op)}},enabled=!s.busy) { Text("Retry original") }
            AdaTextButton({confirm="Discard only this local recovery record? The device or draft may still exist on the server." to {controller.discard(op)}}) { Text("Discard local record") }
        } }
    }
}
