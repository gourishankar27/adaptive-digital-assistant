package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class ProposalHttpTest {
    @Test fun exactExtractionPostIsOneShotAndUsesOwnedAdaRoute() = runTest {
        val server = MockWebServer(); server.start()
        try {
            val conn = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-token", true)!!
            val identity = SessionIdentity(conn.server.toString(), UUID.randomUUID()); val key = UUID.randomUUID(); val scope = UUID.randomUUID()
            val body = adaJson.encodeToString(ExtractionInputDto(key, listOf(SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 3))))
            val p = PendingProposal(identity, scope, key, kind = "extract", body = body)
            server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
            assertTrue(HttpAdaApi().extractProposals(conn, p) is ApiResult.Failure); assertEquals(1, server.requestCount)
            val request = server.takeRequest(); assertEquals("/v1/scopes/$scope/memory-extractions", request.path); assertEquals(body, request.body.readUtf8())
            assertTrue(HttpAdaApi().extractProposals(conn, p.copy(identity = identity.copy(server = "https://foreign.test/"))) is ApiResult.Failure); assertEquals(1, server.requestCount)
        } finally { server.shutdown() }
    }
}
