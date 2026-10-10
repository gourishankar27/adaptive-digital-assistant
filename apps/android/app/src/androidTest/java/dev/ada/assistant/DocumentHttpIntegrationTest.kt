package dev.ada.assistant

import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.time.Instant
import java.util.Base64
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

/** Real authenticated ADA HTTP and disposable migrated SQLite; every document/reply is synthetic. */
class DocumentHttpIntegrationTest {
    private val api = HttpAdaApi()
    private fun credential(): ConnectionCredential {
        val file = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android HTTP fixture server", file.isFile)
        return ConnectionCredential.parse("http://10.0.2.2:18764", file.readText().trim(), true)!!
    }
    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "Synthetic authenticated document HTTP failed" }; return result.value
    }
    private fun failed(result: ApiResult<*>, reason: ApiFailure, code: String? = null) {
        check(result is ApiResult.Failure) { "Synthetic document boundary was not rejected" }
        assertEquals(reason, result.reason); if (code != null) assertEquals(code, result.code)
    }
    private fun pending(conn: ConnectionCredential, scope: UUID, text: String, source: UUID = UUID.randomUUID()) = PendingDocument(
        SessionIdentity(conn.server.toString(), successMe(conn)), scope, UUID.randomUUID(), source, "synthetic.md", "text/markdown",
        Base64.getEncoder().encodeToString(text.toByteArray(Charsets.UTF_8)))
    private fun successMe(conn: ConnectionCredential) = runBlocking { success(api.me(conn)).id }

    @Test fun exactUtf8ChunksReplayAndTrustBoundariesUseRealServer() = runBlocking {
        val conn = credential(); val features = success(api.capabilities(conn))
        assertTrue(features.document_uploads && features.document_retrieval && features.document_citations)
        assertEquals("text_markdown_v1", features.document_ingestion)
        val scope = success(api.createScope(conn, ScopeInputDto("Document exact span verification")))
        val text = "\uFEFF# Synthetic imported document\r\nDocument Falcon project uses Oxford Blue. 😀 e\u0301 தமிழ் 日本語 العربية  \r\n" + "Long exact source line. ".repeat(85)
        val p = pending(conn, scope.id, text); val receipt = success(api.uploadDocument(conn, p))
        assertEquals("ready", receipt.state); assertTrue(verifyDocumentReceipt(p, receipt))
        assertTrue(success(api.uploadDocument(conn, p)) == receipt)
        failed(api.uploadDocument(conn, p.copy(rawBase64 = Base64.getEncoder().encodeToString((text + " ").toByteArray()))), ApiFailure.Conflict, "document_upload_id_reused")
        val version = success(api.documentVersion(conn, receipt.source_version_id)); assertTrue(version.content == text)
        assertTrue(verifyDocumentVersion(version, receipt)); assertEquals(receipt.raw_hash, version.content_hash)
        val chunks = success(api.documentChunks(conn, version.id, 100)); assertTrue(chunks.size >= 2)
        assertTrue(chunks.all { verifyDocumentChunk(it, version) }); assertEquals(text, chunks.joinToString("") { it.quote })
        assertEquals(0, chunks.first().span_start); assertEquals(text.codePointCount(0, text.length), chunks.last().span_end)
        assertEquals(listOf(receipt.id), success(api.documentUploads(conn, scope.id)).map { it.id })
        assertTrue(success(api.sources(conn, scope.id)).isEmpty()); failed(api.source(conn, version.id), ApiFailure.NotFound)
        failed(api.createClaim(conn, scope.id, ClaimInputDto(UUID.randomUUID(), version.id, 0, 10, "Project", "color", "Blue")), ApiFailure.Validation, "source_not_user_evidence")
        val otherScope = success(api.createScope(conn, ScopeInputDto("Separate document exact scope")))
        assertTrue(success(api.documentUploads(conn, otherScope.id)).isEmpty())
        failed(api.uploadDocument(conn, p.copy(scopeId = otherScope.id, uploadId = UUID.randomUUID())), ApiFailure.Conflict, "document_source_id_reused")
        val invalid = ConnectionCredential.parse(conn.server.toString(), "invalid-test-only", true)!!
        failed(api.documentUpload(invalid, receipt.id), ApiFailure.Unauthorized)
        failed(api.documentVersion(invalid, version.id), ApiFailure.Unauthorized)
        failed(api.documentUpload(conn, UUID.randomUUID()), ApiFailure.NotFound)
    }

    @Test fun realDocumentChatFreezesImportedCardsAfterReuploadAndHistoricalQueries() = runBlocking {
        val conn = credential(); val scope = success(api.createScope(conn, ScopeInputDto("Document citation snapshot verification")))
        val text = "The synthetic Document Falcon project uses Oxford Blue. 😀 e\u0301\r\n日本語"
        val p = pending(conn, scope.id, text); val first = success(api.uploadDocument(conn, p))
        val profile = success(api.personalities(conn)).single { it.name == "ADA Test" }
        val chat = success(api.createConversation(conn, ConversationInputDto(profile.id, "Document immutable citation verification", scope.id)))
        assertEquals("ada-baseline-v4", chat.prompt_version)
        val input = ChatInputDto(UUID.randomUUID(), "Which color does the Document Falcon project use?", use_documents = true)
        val reply = success(api.send(conn, chat.id, input)); assertEquals("completed", reply.status)
        assertTrue(reply.response?.startsWith("[FAKE provider]") == true); assertTrue(reply.citations.isEmpty())
        val card = reply.document_citations.single(); assertEquals("D1", card.label)
        assertEquals(first.source_version_id, card.source_version_id); assertEquals("imported_document", card.origin)
        assertEquals("imported_untrusted", card.trust_class); assertEquals(text, card.evidence.quote)
        // Server publication time, rather than the emulator's slightly different wall clock.
        val beforeReplacement = Instant.ofEpochMilli(checkNotNull(first.published_at)).toString()
        val newer = p.copy(uploadId = UUID.randomUUID(), rawBase64 = Base64.getEncoder().encodeToString("The synthetic Document Falcon project uses Olive Green. 😀".toByteArray()))
        val second = success(api.uploadDocument(conn, newer)); assertEquals(first.source_id, second.source_id); assertEquals(2, second.version)
        assertEquals(reply, success(api.request(conn, reply.request_id))); assertEquals(reply, success(api.send(conn, chat.id, input)))
        val trace = success(api.trace(conn, reply.request_id)); assertEquals(listOf(card), trace.document_selected)
        assertEquals(listOf(2, 1), success(api.documentVersions(conn, p.sourceId)).map { it.version })
        val historical = success(api.send(conn, chat.id, input.copy(request_id = UUID.randomUUID(), as_of = beforeReplacement)))
        assertEquals(first.source_version_id, historical.document_citations.single().source_version_id)
        val latest = success(api.send(conn, chat.id, input.copy(request_id = UUID.randomUUID())))
        assertEquals(second.source_version_id, latest.document_citations.single().source_version_id)
        val disabled = success(api.send(conn, chat.id, input.copy(request_id = UUID.randomUUID(), use_memory = false)))
        assertTrue(disabled.document_citations.isEmpty())
    }
}
