package dev.ada.assistant

import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.ChatDestination
import dev.ada.assistant.ui.ChatViewModel
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test

/** Production activity/Keystore/UI after a real adb force-stop; user resumes the original bytes. */
class DocumentRecoveryResumeTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    private lateinit var vm: ChatViewModel
    @Test fun resumesOriginalUploadAndCitesItsImportedVersionAfterProcessStop() {
        val arguments = InstrumentationRegistry.getArguments()
        assumeTrue("Run the explicit document force-stop stages", arguments.getString("adaDocumentRecovery") == "true")
        val expectedUpload = UUID.fromString(arguments.getString("expectedDocumentUpload"))
        val expectedSource = UUID.fromString(arguments.getString("expectedDocumentSource"))
        vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.waitUntil(20_000) { vm.state.value.account != null && !vm.state.value.connecting && vm.documents.state.value.pending?.uploadId == expectedUpload }
        val store = AndroidSessionStore(compose.activity.applicationContext)
        val saved = checkNotNull(runBlocking { store.readCredential() }); assertEquals(saved.identity.owner, vm.state.value.account?.owner)
        val pending = checkNotNull(runBlocking { store.documentPending(saved.identity) })
        assertEquals(expectedUpload, pending.uploadId); assertEquals(expectedSource, pending.sourceId)
        assertEquals(DOCUMENT_RECOVERY_TEXT, documentText(pending.rawBytes()))
        val conn = ConnectionCredential.parse(saved.identity.server, saved.token, true)!!; val api = HttpAdaApi()
        val original = runBlocking { success(api.documentUpload(conn, expectedUpload)) }
        assertEquals("ready", original.state); assertEquals(1, runBlocking { success(api.documentVersions(conn, expectedSource)) }.size)
        // Verification/restoration has made no POST and does not delete the unresolved journal.
        assertNotNull(runBlocking { store.documentPending(saved.identity) })
        compose.runOnIdle { vm.navigate(ChatDestination.Documents) }
        compose.onNodeWithTag("documents-list").performScrollToNode(hasTestTag("document-resume"))
        compose.onNodeWithTag("document-resume").performScrollTo().performClick()
        compose.waitUntil(20_000) { vm.documents.state.value.pending == null && !vm.documents.state.value.saving && vm.documents.state.value.version != null }
        assertEquals(original, vm.documents.state.value.detail); assertEquals(DOCUMENT_RECOVERY_TEXT, vm.documents.state.value.version!!.content)
        assertNull(runBlocking { store.documentPending(saved.identity) }); assertTrue(vm.documents.state.value.chunks.items.all { verifyDocumentChunk(it, vm.documents.state.value.version!!) })
        assertEquals(listOf(original.id), runBlocking { success(api.documentVersions(conn, expectedSource)) }.map { it.id })
        compose.onNodeWithTag("documents-list").performScrollToNode(hasTestTag("document-version-text"))
        compose.onNodeWithTag("document-version-text").performScrollTo().assertTextContains(DOCUMENT_RECOVERY_TEXT)
        val profile = runBlocking { success(api.personalities(conn)) }.single { it.name == "ADA Test" }
        val conversation = runBlocking { success(api.createConversation(conn, ConversationInputDto(profile.id, "Document recovery source cards", pending.scopeId))) }
        compose.runOnIdle { vm.openConversation(conversation.id) }
        compose.waitUntil(20_000) { vm.state.value.conversation?.id == conversation.id && !vm.state.value.events.loading }
        compose.runOnIdle { vm.updateDraft("Which color does the Document Falcon recovery project use?"); vm.updateDocuments(true); vm.send() }
        compose.waitUntil(20_000) { vm.state.value.pending == null && vm.state.value.events.items.any { it.role == "assistant" } }
        val event = vm.state.value.events.items.single { it.role == "assistant" }
        val reply = runBlocking { success(api.request(conn, event.request_id)) }
        val card = reply.document_citations.single(); assertEquals(original.source_version_id, card.source_version_id)
        compose.onNodeWithTag("source-chip-D1").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.state.value.sourceLoading && vm.state.value.destination == ChatDestination.Sources }
        compose.onNodeWithTag("sources-list").performScrollToNode(hasTestTag("source-quote-D1"))
        compose.onNodeWithTag("source-quote-D1").performScrollTo().assertTextContains(DOCUMENT_RECOVERY_TEXT)
        assertTrue(reply.citations.isEmpty()); assertEquals("imported_untrusted", card.trust_class)
    }
    @After fun cleanup() {
        if (::vm.isInitialized) compose.runOnIdle { vm.logout() }
        runBlocking { AndroidSessionStore(compose.activity.applicationContext).clear() }
    }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success) { "Synthetic authenticated document verification failed" }; return result.value }
}
