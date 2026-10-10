package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class EntityHttpTest {
    @Test fun exactLinkNullsAndFixedPathAreSentOnceOnBusy() = runTest {
        val server = MockWebServer(); server.start()
        try {
            val conn = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-entity-token", true)!!
            val identity = SessionIdentity(conn.server.toString(), UUID.randomUUID()); val scope = UUID.randomUUID(); val op = UUID.randomUUID(); val claim = UUID.randomUUID()
            val body = """{"operation_id":"$op","entity_id":null,"expected_entity_id":null}"""
            val pending = PendingEntity(identity, scope, op, "link", "claims/$claim/entity", body)
            server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "3"))
            server.enqueue(MockResponse().setBody(adaJson.encodeToString(EntityOperationDto(op, scope, "link", 1, link = EntityLinkDto(claim, original_subject = "Unchanged synthetic subject")))))
            val api = HttpAdaApi(); assertEquals(ApiFailure.Busy(3), (api.writeEntity(conn, pending) as ApiResult.Failure).reason)
            assertEquals(1, server.requestCount); val request = server.takeRequest(); assertEquals("/v1/claims/$claim/entity", request.path); assertEquals(body, request.body.readUtf8())
            val receipt = (api.writeEntity(conn, pending) as ApiResult.Success).value; assertTrue(verifyEntityOperation(pending, receipt)); assertEquals(2, server.requestCount)
            assertEquals(body, server.takeRequest().body.readUtf8())
        } finally { server.shutdown() }
    }
    @Test fun foreignServerJournalIsRejectedBeforeNetwork() = runTest {
        val server = MockWebServer(); server.start()
        try {
            val conn = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-token", true)!!
            val scope = UUID.randomUUID(); val op = UUID.randomUUID()
            val p = PendingEntity(SessionIdentity("https://different.test/", UUID.randomUUID()), scope, op, "create", "scopes/$scope/entities", """{"operation_id":"$op"}""")
            assertTrue(HttpAdaApi().writeEntity(conn, p) is ApiResult.Failure); assertEquals(0, server.requestCount)
        } finally { server.shutdown() }
    }
}
