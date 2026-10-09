package dev.ada.assistant.data

import java.util.UUID
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import okhttp3.mockwebserver.SocketPolicy
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

class HttpAdaApiTest {
    private lateinit var server: MockWebServer
    private val api = HttpAdaApi()
    @Before fun setup() { server = MockWebServer(); server.start() }
    @After fun cleanup() { server.shutdown() }
    private fun credential() = checkNotNull(ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-test-only", true))

    @Test fun realHttpAdapterAuthenticatesAndDecodesFutureFields() = runTest {
        server.enqueue(MockResponse().setBody("""{"id":"00000000-0000-4000-8000-000000000001","name":"Test","future":12}"""))
        assertEquals("Test", (api.me(credential()) as ApiResult.Success).value.name)
        val request = server.takeRequest()
        assertEquals("/v1/me", request.path)
        assertEquals("Bearer synthetic-test-only", request.getHeader("Authorization"))
    }

    @Test fun statusMappingDiscardsUntrustedSecretBearingBodies() = runTest {
        val cases = listOf(401 to ApiFailure.Unauthorized, 403 to ApiFailure.Forbidden, 404 to ApiFailure.NotFound,
            409 to ApiFailure.Conflict, 413 to ApiFailure.TooLarge, 422 to ApiFailure.Validation, 502 to ApiFailure.Provider)
        for ((status, expected) in cases) {
            server.enqueue(MockResponse().setResponseCode(status).setBody("""{"detail":"private-data-and-token","input":"private"}"""))
            val result = api.me(credential()) as ApiResult.Failure
            assertEquals(expected, result.reason)
            assertFalse(result.toString().contains("private"))
        }
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "3"))
        assertEquals(ApiFailure.Busy(3), (api.me(credential()) as ApiResult.Failure).reason)
    }

    @Test fun errorsAndInvalidContractDoNotActivateFixtures() = runTest {
        server.enqueue(MockResponse().setBody("{}"))
        assertEquals(ApiFailure.IncompatibleContract, (api.me(credential()) as ApiResult.Failure).reason)
        server.enqueue(MockResponse().setResponseCode(500).setBody(fixture("capabilities-current.json")))
        assertEquals(ApiFailure.Http(500), (api.capabilities(credential()) as ApiResult.Failure).reason)
    }

    @Test fun redirectsNeverForwardTheBearerCredential() = runTest {
        MockWebServer().use { other ->
            other.start()
            server.enqueue(MockResponse().setResponseCode(302).setHeader("Location", other.url("/capture")))
            assertEquals(ApiFailure.Http(302), (api.me(credential()) as ApiResult.Failure).reason)
            assertEquals(0, other.requestCount)
        }
    }

    @Test fun transportTimeoutRemainsUnknownAndDoesNotRetryPost() = runTest {
        server.enqueue(MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE))
        val body = ChatInputDto(UUID.randomUUID(), "Synthetic timeout input")
        val result = HttpAdaApi(callTimeoutMillis = 150).send(credential(), UUID.randomUUID(), body)
        assertEquals(ApiFailure.Timeout, (result as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
    }

    @Test fun creationPostNeverFollows503WithImmediateRetryAfter() = runTest {
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
        // A replay would consume this successful creation response and create a duplicate.
        server.enqueue(MockResponse().setBody(fixture("conversation-current.json")))
        val body = ConversationInputDto(UUID.fromString("00000000-0000-0000-0000-000000000002"), "Synthetic creation")
        val result = api.createConversation(credential(), body)
        assertEquals(ApiFailure.Busy(0), (result as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
        val request = server.takeRequest()
        assertEquals("POST", request.method)
        assertEquals("/v1/conversations", request.path)
        assertEquals(body, adaJson.decodeFromString<ConversationInputDto>(request.body.readUtf8()))
    }

    @Test fun explicitRetryUsesFreshBodyWithIdenticalUuidContentAndOptions() = runTest {
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
        server.enqueue(MockResponse().setBody(fixture("request-current.json")))
        val conversation = UUID.fromString("00000000-0000-0000-0000-000000000004")
        val body = ChatInputDto(UUID.fromString("00000000-0000-0000-0000-000000000009"),
            "Exact 😀 text\r\n e\u0301  ", "2026-10-08T00:00:00.000Z", false)
        assertEquals(ApiFailure.Busy(0), (api.send(credential(), conversation, body) as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
        // Only this second, explicit API call may send the reserved payload again.
        val retried = (api.send(credential(), conversation, body) as ApiResult.Success).value
        assertEquals(body.request_id, retried.request_id)
        assertEquals(ObservedRequestState.Completed, retried.observedState)
        assertEquals(2, server.requestCount)
        val original = server.takeRequest()
        val retry = server.takeRequest()
        assertEquals(original.path, retry.path)
        assertEquals(original.body.clone().readUtf8(), retry.body.clone().readUtf8())
        for (request in listOf(original, retry)) {
            assertEquals("POST", request.method)
            assertEquals("Bearer synthetic-test-only", request.getHeader("Authorization"))
            assertEquals(body, adaJson.decodeFromString<ChatInputDto>(request.body.readUtf8()))
        }
    }

    @Test fun postAuthenticationFailuresAndRedirectsNeverReplayOrForwardCredentials() = runTest {
        val body = ChatInputDto(UUID.randomUUID(), "Synthetic rejected request")
        server.enqueue(MockResponse().setResponseCode(401).setHeader("WWW-Authenticate", "Bearer"))
        assertEquals(ApiFailure.Unauthorized, (api.send(credential(), UUID.randomUUID(), body) as ApiResult.Failure).reason)
        assertEquals(1, server.requestCount)
        MockWebServer().use { other ->
            other.start()
            server.enqueue(MockResponse().setResponseCode(307).setHeader("Location", other.url("/capture")))
            assertEquals(ApiFailure.Http(307), (api.send(credential(), UUID.randomUUID(), body) as ApiResult.Failure).reason)
            assertEquals(2, server.requestCount)
            assertEquals(0, other.requestCount)
        }
    }

    @Test fun sendKeepsReservedUuidContentAndOptionsAndDoesNotRetryConflict() = runTest {
        server.enqueue(MockResponse().setResponseCode(409))
        val body = ChatInputDto(UUID.fromString("00000000-0000-4000-8000-000000000001"), "Exact 😀 text\n", "2026-10-08T00:00:00.000Z", false)
        assertEquals(ApiFailure.Conflict, (api.send(credential(), UUID.fromString("00000000-0000-4000-8000-000000000002"), body) as ApiResult.Failure).reason)
        val request = server.takeRequest()
        assertEquals(body, adaJson.decodeFromString<ChatInputDto>(request.body.readUtf8()))
        assertEquals(1, server.requestCount)
    }

    @Test fun releaseAndDebugUrlPoliciesRejectCredentialsPathsAndBroadHttp() {
        assertNull(ConnectionCredential.parse("http://localhost:8000", "test", false))
        assertNull(ConnectionCredential.parse("http://192.168.1.5:8000", "test", true))
        assertNull(ConnectionCredential.parse("https://user:password@example.com", "test", false))
        assertNull(ConnectionCredential.parse("https://example.com/path?token=test", "test", false))
        assertNull(ConnectionCredential.parse("https://example.com", "test\nheader", false))
        assertNotNull(ConnectionCredential.parse("HTTPS://EXAMPLE.COM:443/", "test", false))
        assertNotNull(ConnectionCredential.parse("http://10.0.2.2:8000", "test", true))
        assertFalse(credential().toString().contains("synthetic-test-only"))
    }

    @Test fun onlyKnownErrorCodesSurviveSanitization() = runTest {
        server.enqueue(MockResponse().setResponseCode(409).setBody("""{"detail":"retry_history_changed"}"""))
        val conflict = api.send(credential(), UUID.randomUUID(), ChatInputDto(UUID.randomUUID(), "Synthetic")) as ApiResult.Failure
        assertEquals(ApiFailure.Conflict, conflict.reason)
        assertEquals("retry_history_changed", conflict.code)
        server.enqueue(MockResponse().setResponseCode(409).setBody("""{"detail":"private-source-quote-or-token"}"""))
        val unknown = api.me(credential()) as ApiResult.Failure
        assertNull(unknown.code)
        assertFalse(unknown.toString().contains("private"))
        server.enqueue(MockResponse().setResponseCode(401).setBody("""{"detail":"retry_history_changed"}"""))
        val unauthorized = api.me(credential()) as ApiResult.Failure
        assertEquals(ApiFailure.Unauthorized, unauthorized.reason)
        assertNull(unauthorized.code)
    }

    @Test fun busyPreservesNumericAndHttpDateRetryAfter() = runTest {
        server.enqueue(MockResponse().setResponseCode(429).setHeader("Retry-After", "600"))
        assertEquals(ApiFailure.Busy(600), (api.me(credential()) as ApiResult.Failure).reason)
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", ZonedDateTime.now(java.time.ZoneOffset.UTC).plusSeconds(30).format(DateTimeFormatter.RFC_1123_DATE_TIME)))
        val date = (api.me(credential()) as ApiResult.Failure).reason as ApiFailure.Busy
        assertTrue(checkNotNull(date.retryAfterSeconds) in 28..30)
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "-10"))
        assertEquals(ApiFailure.Busy(null), (api.me(credential()) as ApiResult.Failure).reason)
    }
}
