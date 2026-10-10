package dev.ada.assistant.data

import java.util.Base64
import java.util.UUID
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.SocketPolicy
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class DocumentHttpTest {
    private lateinit var server: MockWebServer
    @Before fun setup() { server = MockWebServer(); server.start() }
    @After fun cleanup() { server.shutdown() }
    private fun credential() = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-document-token", true)!!
    private fun pending() = PendingDocument(SessionIdentity(credential().server.toString(), UUID.randomUUID()), UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID(),
        "exact quote.md", "text/markdown", Base64.getEncoder().encodeToString("Synthetic 😀 e\u0301\r\n日本語  ".toByteArray(Charsets.UTF_8)))
    private fun receipt(p: PendingDocument) = DocumentUploadDto(p.uploadId, p.sourceId, p.scopeId, UUID.randomUUID(), 1,
        p.filename, p.mediaType, documentHash(p.rawBytes()), p.rawBytes().size, 1791504000000L, state = "ready", created_at = 1791504000000L, published_at = 1791504000001L, chunk_count = 1)

    @Test fun rawUploadHasExactUtf8AndEncodedMetadataAndNeverRepeatsImmediate503() = runTest {
        val p = pending(); val r = receipt(p); val api = HttpAdaApi()
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
        server.enqueue(MockResponse().setBody(adaJson.encodeToString(r)))
        assertEquals(ApiFailure.Busy(0), (api.uploadDocument(credential(), p) as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
        assertEquals(r, (api.uploadDocument(credential(), p) as ApiResult.Success).value)
        val first = server.takeRequest(); val second = server.takeRequest()
        assertEquals(first.path, second.path); assertEquals("POST", first.method)
        assertEquals("/v1/scopes/${p.scopeId}/documents/uploads/${p.uploadId}", first.requestUrl!!.encodedPath)
        assertEquals(p.sourceId.toString(), first.requestUrl!!.queryParameter("source_id"))
        assertEquals(p.filename, first.requestUrl!!.queryParameter("filename"))
        assertEquals("text/markdown", first.getHeader("Content-Type"))
        assertEquals("Bearer synthetic-document-token", first.getHeader("Authorization"))
        assertArrayEquals(p.rawBytes(), first.body.readByteArray()); assertArrayEquals(p.rawBytes(), second.body.readByteArray())
    }
    @Test fun ambiguousUploadTimeoutKeepsOutcomeUnknownAndMakesOnePost() = runTest {
        server.enqueue(MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE))
        assertEquals(ApiFailure.Timeout, (HttpAdaApi(150).uploadDocument(credential(), pending()) as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
    }
    @Test fun allDocumentReadsStayAuthenticatedAndUseOwnedIdsWithPaging() = runTest {
        val p = pending(); val r = receipt(p); val api = HttpAdaApi()
        server.enqueue(MockResponse().setBody(adaJson.encodeToString(r)))
        server.enqueue(MockResponse().setBody(adaJson.encodeToString(listOf(r))))
        server.enqueue(MockResponse().setBody(adaJson.encodeToString(listOf(r))))
        assertEquals(r, (api.documentUpload(credential(), p.uploadId) as ApiResult.Success).value)
        assertEquals(listOf(r), (api.documentUploads(credential(), p.scopeId, 50, 100) as ApiResult.Success).value)
        assertEquals(listOf(r), (api.documentVersions(credential(), p.sourceId, 50, 100) as ApiResult.Success).value)
        assertEquals("/v1/document-uploads/${p.uploadId}", server.takeRequest().path)
        val uploads = server.takeRequest(); assertEquals("100", uploads.requestUrl!!.queryParameter("offset"))
        assertEquals("/v1/scopes/${p.scopeId}/document-uploads", uploads.requestUrl!!.encodedPath)
        val versions = server.takeRequest(); assertEquals("/v1/documents/${p.sourceId}/versions", versions.requestUrl!!.encodedPath)
        assertEquals("Bearer synthetic-document-token", versions.getHeader("Authorization"))
    }
    @Test fun hostileLocalInputMakesNoHttpCallAndUntrustedErrorsRemainSanitized() = runTest {
        val p = pending(); val api = HttpAdaApi()
        assertEquals(ApiFailure.Validation, (api.uploadDocument(credential(), p.copy(filename = "../unsafe.md")) as ApiResult.Failure).reason)
        assertEquals(0, server.requestCount)
        server.enqueue(MockResponse().setResponseCode(422).setBody("""{"detail":"document_invalid_encoding","input":"private"}"""))
        assertEquals("document_invalid_encoding", (api.uploadDocument(credential(), p) as ApiResult.Failure).code)
        server.enqueue(MockResponse().setResponseCode(422).setBody("""{"detail":"private-source-secret"}"""))
        assertNull((api.uploadDocument(credential(), p) as ApiResult.Failure).code)
    }
    @Test fun documentOptInIsExplicitAndClaimOnlyChatRetainsItsOriginalWireShape() = runTest {
        val api = HttpAdaApi(); val conversation = UUID.randomUUID(); val body = ChatInputDto(UUID.randomUUID(), "Synthetic query")
        server.enqueue(MockResponse().setBody(fixture("request-current.json")))
        api.send(credential(), conversation, body)
        val legacy = server.takeRequest().body.readUtf8()
        assertFalse(legacy.contains("use_documents")); assertEquals(body, adaJson.decodeFromString<ChatInputDto>(legacy))
        server.enqueue(MockResponse().setBody(fixture("request-current.json")))
        api.send(credential(), conversation, body.copy(use_documents = true))
        assertTrue(server.takeRequest().body.readUtf8().contains("\"use_documents\":true"))
    }
}
