package dev.ada.assistant

import android.os.Bundle
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.DocumentController
import dev.ada.assistant.ui.DocumentDraft
import java.io.File
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

internal val DOCUMENT_RECOVERY_TEXT = "The synthetic Document Falcon recovery project uses Oxford Blue. 😀 e\u0301\r\n日本語 العربية 中文.\r\n" +
    "Exact imported text survives process interruption. ".repeat(12)

/** Real upload commits; only its HTTP delivery is explicitly simulated as lost. */
class DocumentRecoveryPrepareTest {
    @Test fun prepareCommittedUploadWithoutDelivery() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue("Run the explicit document force-stop stages", InstrumentationRegistry.getArguments().getString("adaDocumentRecovery") == "true")
        val context = instrumentation.targetContext; val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable HTTP fixture server", tokenFile.isFile)
        val store = AndroidSessionStore(context); store.clear()
        val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
        var controller: DocumentController? = null; var prepared = false
        try {
            val token = tokenFile.readText().trim(); val conn = ConnectionCredential.parse("http://10.0.2.2:18764", token, true)!!
            val actual = HttpAdaApi(); val me = success(actual.me(conn)); val features = success(actual.capabilities(conn))
            val identity = SessionIdentity(conn.server.toString(), me.id)
            val ownedScope = success(actual.createScope(conn, ScopeInputDto("Document process recovery verification")))
            store.saveCredential(StoredCredential(identity, token))
            val lost = LostDocumentDelivery(actual); val documents = DocumentController(lost, store, scope, { error("Synthetic credential unexpectedly revoked") })
            controller = documents
            withContext(Dispatchers.Main) { documents.setVerifiedSession(conn, identity, features); documents.activate() }
            await { !documents.state.value.scopes.loading && documents.state.value.scopes.items.any { it.id == ownedScope.id } }
            withContext(Dispatchers.Main) {
                documents.selectScope(ownedScope.id); documents.beginUpload()
                documents.updateDraft(DocumentDraft(filename = "recovery.md", mediaType = "text/markdown", text = DOCUMENT_RECOVERY_TEXT)); documents.preview(); documents.savePreview()
            }
            await { !documents.state.value.saving && documents.state.value.pending != null && documents.state.value.fault == ApiFailure.Timeout }
            val pending = checkNotNull(store.documentPending(identity)); assertEquals(1, lost.posts)
            assertEquals(DOCUMENT_RECOVERY_TEXT, documentText(pending.rawBytes()))
            val receipt = success(actual.documentUpload(conn, pending.uploadId)); assertEquals("ready", receipt.state)
            assertEquals(1, success(actual.documentVersions(conn, pending.sourceId)).size)
            assertTrue(success(actual.claims(conn, ownedScope.id)).isEmpty())
            prepared = true
            instrumentation.sendStatus(0, Bundle().apply {
                putString("recoveryDocumentUpload", pending.uploadId.toString()); putString("recoveryDocumentSource", pending.sourceId.toString())
            })
        } finally {
            withContext(Dispatchers.Main) { controller?.reset() }; scope.cancel(); if (!prepared) store.clear()
        }
    }
    private suspend fun await(condition: () -> Boolean) = withTimeout(20_000) { while (!condition()) delay(50) }
    private fun <T> success(result: ApiResult<T>): T { check(result is ApiResult.Success) { "Synthetic authenticated document prerequisite failed" }; return result.value }
    private class LostDocumentDelivery(private val actual: AdaApi) : AdaApi by actual {
        var posts = 0
        override suspend fun uploadDocument(connection: ConnectionCredential, pending: PendingDocument): ApiResult<DocumentUploadDto> {
            posts++; check(actual.uploadDocument(connection, pending) is ApiResult.Success) { "Synthetic document failed to commit" }
            return ApiResult.Failure(ApiFailure.Timeout)
        }
    }
}
