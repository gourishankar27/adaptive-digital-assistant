package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.data.ApiResult
import dev.ada.assistant.data.ChatInputDto
import dev.ada.assistant.data.ConnectionCredential
import dev.ada.assistant.data.ConversationInputDto
import dev.ada.assistant.data.HttpAdaApi
import dev.ada.assistant.data.PendingMessage
import dev.ada.assistant.data.SessionIdentity
import dev.ada.assistant.data.StoredCredential
import java.io.File
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test

/** Stage one: no Activity starts, so only the test deliberately retains the exact journal. */
class ProcessRecoveryPrepareTest {
    @Test fun prepareCommittedReplyWithoutDelivery() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue("Run the explicit force-stop recovery stages", InstrumentationRegistry.getArguments().getString("adaProcessRecovery") == "true")
        val context = instrumentation.targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android chat fixture server", tokenFile.isFile)
        val store = AndroidSessionStore(context)
        store.clear()
        var prepared = false
        try {
            val token = tokenFile.readText().trim()
            val credential = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", token, true))
            val api = HttpAdaApi()
            val me = success(api.me(credential))
            val capabilities = success(api.capabilities(credential))
            assertEquals("Foundation Test", me.name)
            assertEquals("v1", capabilities.api_version)
            assertEquals("server", capabilities.authority)
            assertTrue(capabilities.chat && capabilities.memory_citations)
            val profile = success(api.personalities(credential)).single { it.name == "ADA Test" }
            val scope = success(api.scopes(credential)).single { it.name == "Android verification" }
            val conversation = success(api.createConversation(credential, ConversationInputDto(profile.id, "Process recovery verification", scope.id)))
            val identity = SessionIdentity(credential.server.toString(), me.id)
            val body = ChatInputDto(UUID.randomUUID(), "Which color does the Android verification project use?", as_of = null, use_memory = true)
            store.saveCredential(StoredCredential(identity, token))
            // This commit happens before the actual POST, matching the production write ordering.
            store.savePending(PendingMessage(identity, conversation.id, body))
            val committed = success(api.send(credential, conversation.id, body))
            assertEquals(body.request_id, committed.request_id)
            assertEquals("completed", committed.status)
            assertTrue(committed.citations.any { it.label == "M1" })
            val events = success(api.events(credential, conversation.id))
            assertEquals(2, events.size)
            assertEquals(1, events.count { it.role == "user" && it.request_id == body.request_id })
            assertEquals(1, events.count { it.role == "assistant" && it.request_id == body.request_id })
            assertEquals(body, store.pending(identity)?.body)
            prepared = true
            // Only IDs are emitted. The bearer, message, source quote and response are never output.
            instrumentation.sendStatus(0, Bundle().apply {
                putString("recoveryRequest", body.request_id.toString())
                putString("recoveryConversation", conversation.id.toString())
            })
        } finally {
            if (!prepared) store.clear()
        }
        // Root orchestration now force-stops the target process before the second class launches it.
    }

    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated HTTP prerequisite failed" }
        return result.value
    }
}
