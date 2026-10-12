package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class StreamingContractTest {
    private val reply = adaJson.decodeFromString<RequestDto>(fixture("request-current.json")).copy(status = "running", response = null)
    private fun checkpoint() = StreamStatusDto(reply.request_id, reply.conversation_id, reply.attempt, true, "running", 1, 0, "", reply)
    private fun event(sequence: Int, text: String) = StreamEventDto(reply.request_id, reply.attempt, sequence, "delta", JsonObject(mapOf("text" to JsonPrimitive(text))), 1)
    @Test fun duplicateAndReorderedChunksNeverDuplicateText() {
        val c = checkpoint(); c.validate(reply.request_id, reply.conversation_id)
        val accumulated = StreamAccumulator(c)
        accumulated.accept(event(2, "🫖 exact")); accumulated.accept(event(2, "🫖 exact"))
        assertEquals("🫖 exact", accumulated.text)
        assertThrows(StreamGap::class.java) { accumulated.accept(event(4, "gap")) }
        assertEquals(2, accumulated.sequence); assertEquals("🫖 exact", accumulated.text)
    }
    @Test fun foreignAttemptInvalidUnicodeAndInvalidStateFailClosed() {
        val c = checkpoint(); val accumulated = StreamAccumulator(c)
        assertThrows(IllegalArgumentException::class.java) { accumulated.accept(event(2, "foreign").copy(request_id = UUID.randomUUID())) }
        assertThrows(IllegalArgumentException::class.java) { accumulated.accept(event(2, "late").copy(attempt = reply.attempt + 1)) }
        assertThrows(IllegalArgumentException::class.java) { accumulated.accept(event(2, "\uD800")) }
        assertThrows(IllegalArgumentException::class.java) { c.copy(stream_state = "completed").validate(reply.request_id, reply.conversation_id) }
        assertEquals("", accumulated.text)
    }
    @Test fun nativeHttpSseUsesBearerHeaderAndFragmentedUtf8() = runTest {
        MockWebServer().use { server ->
            server.start()
            val id = reply.request_id; val attempt = reply.attempt
            val json = """{"request_id":"$id","attempt":$attempt,"sequence":2,"type":"delta","payload":{"text":"🫖 exact"},"created_at":1}"""
            server.enqueue(MockResponse().setHeader("Content-Type", "text/event-stream").setChunkedBody("id: $attempt:2\nevent: delta\ndata: $json\n\n", 2))
            val c = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-test-only", true)!!
            val result = HttpAdaApi().streamEvents(c, id, attempt, 1).toList()
            assertEquals("🫖 exact", ((result.single() as ApiResult.Success).value.payload["text"] as JsonPrimitive).content)
            val request = server.takeRequest()
            assertEquals("Bearer synthetic-test-only", request.getHeader("Authorization"))
            assertEquals("/v1/requests/$id/stream?attempt=$attempt&after=1", request.path)
            assertFalse(request.path!!.contains("synthetic-test-only"))
        }
    }
    @Test fun foreignStreamAndRevokedCredentialCannotProduceProvisionalText() = runTest {
        MockWebServer().use { server ->
            server.start(); val id = reply.request_id
            val c = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-test-only", true)!!
            server.enqueue(MockResponse().setHeader("Content-Type", "text/event-stream").setBody("event: access_lost\ndata: {\"detail\":\"invalid_token\"}\n\n"))
            assertEquals(ApiFailure.Unauthorized, (HttpAdaApi().streamEvents(c, id, reply.attempt, 0).toList().single() as ApiResult.Failure).reason)
            server.enqueue(MockResponse().setResponseCode(401).setBody("private-untrusted-body"))
            assertEquals(ApiFailure.Unauthorized, (HttpAdaApi().streamEvents(c, id, reply.attempt, 0).toList().single() as ApiResult.Failure).reason)
        }
    }
}
