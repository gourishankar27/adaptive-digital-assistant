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
    @Test fun calendarWindowUsesAuthenticatedVersionedBodyAndPreservesInterval() = runTest {
        server.enqueue(MockResponse().setBody("""{"version":"ada-window-retrieval-v1","resolution":{"version":"ada-time-window-v1","state":"resolved","reason":"explicit_calendar_window","semantics":"valid_time_overlap_current_recorded_state","start":1772956800000,"end":1773039600000},"guidance":"Compare the whole interval."}"""))
        val scope = UUID.randomUUID()
        val result = api.retrieveWindow(credential(), scope, WindowRetrieveInputDto("Mira beverage", TimeSelectionDto("yesterday", "America/New_York", "2026-03-09T12:00:00-04:00"))) as ApiResult.Success
        assertEquals(23 * 3600000L, result.value.resolution.end!! - result.value.resolution.start!!)
        val request = server.takeRequest()
        assertEquals("/v1/scopes/$scope/retrieve-window", request.path)
        assertEquals("Bearer synthetic-test-only", request.getHeader("Authorization"))
        assertTrue(request.body.readUtf8().contains("ada-time-window-v1"))
    }
    private lateinit var server: MockWebServer
    private val api = HttpAdaApi()
    @Before fun setup() { server = MockWebServer(); server.start() }
    @After fun cleanup() { server.shutdown() }
    private fun credential() = checkNotNull(ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-test-only", true))

    @Test fun passwordLoginRotationAndLogoutUseSinglePublicPostsAndMemoryAccess() = runTest {
        val origin = credential().server.toString()
        val id = "00000000-0000-4000-8000-000000000011"
        fun tokens(access: String, refresh: String) = """{"access_token":"$access","refresh_token":"$refresh","session_id":"$id","access_expires_at":2000000000000,"expires_at":2000000900000}"""
        server.enqueue(MockResponse().setHeader("Content-Type", "application/json").setBody("""{"status":"ready","schema":"0016"}"""))
        server.enqueue(MockResponse().setBody(tokens("synthetic-access-one", "synthetic-refresh-one")))
        val first = (api.passwordLogin(origin, "synthetic-user", "Public synthetic passphrase", true) as ApiResult.Success).value
        assertNull(server.takeRequest().getHeader("Authorization"))
        val login = server.takeRequest(); assertEquals("/v1/auth/login", login.path); assertNull(login.getHeader("Authorization"))
        assertTrue(login.body.readUtf8().contains("Public synthetic passphrase"))
        server.enqueue(MockResponse().setHeader("Content-Type", "application/json").setBody("""{"status":"ready","schema":"0016"}"""))
        server.enqueue(MockResponse().setBody(tokens("synthetic-access-two", "synthetic-refresh-two")))
        val second = (api.refreshLogin(origin, first.refresh_token, true) as ApiResult.Success).value
        server.takeRequest(); val refresh = server.takeRequest(); assertEquals("/v1/auth/refresh", refresh.path); assertNull(refresh.getHeader("Authorization"))
        server.enqueue(MockResponse().setBody("""{"status":"signed_out"}"""))
        assertTrue(api.logoutSession(ConnectionCredential.parse(origin, second.access_token, true)!!) is ApiResult.Success)
        assertEquals("Bearer synthetic-access-two", server.takeRequest().getHeader("Authorization"))
        assertFalse(first.toString().contains(first.refresh_token))
        assertEquals(5, server.requestCount)
    }

    @Test fun realHttpAdapterAuthenticatesAndDecodesFutureFields() = runTest {
        server.enqueue(MockResponse().setHeader("Content-Type", "application/json").setBody("""{"status":"ready","schema":"0015"}"""))
        server.enqueue(MockResponse().setBody("""{"id":"00000000-0000-4000-8000-000000000001","name":"Test","future":12}"""))
        assertEquals("Test", (api.me(credential()) as ApiResult.Success).value.name)
        assertNull(server.takeRequest().getHeader("Authorization"))
        val request = server.takeRequest()
        assertEquals("/v1/me", request.path)
        assertEquals("Bearer synthetic-test-only", request.getHeader("Authorization"))
    }

    @Test fun statusMappingDiscardsUntrustedSecretBearingBodies() = runTest {
        val cases = listOf(401 to ApiFailure.Unauthorized, 403 to ApiFailure.Forbidden, 404 to ApiFailure.NotFound,
            409 to ApiFailure.Conflict, 413 to ApiFailure.TooLarge, 422 to ApiFailure.Validation, 502 to ApiFailure.Provider)
        for ((status, expected) in cases) {
            server.enqueue(MockResponse().setResponseCode(status).setBody("""{"detail":"private-data-and-token","input":"private"}"""))
            val result = api.capabilities(credential()) as ApiResult.Failure
            assertEquals(expected, result.reason)
            assertFalse(result.toString().contains("private"))
        }
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "3"))
        assertEquals(ApiFailure.Busy(3), (api.capabilities(credential()) as ApiResult.Failure).reason)
    }

    @Test fun errorsAndInvalidContractDoNotActivateFixtures() = runTest {
        server.enqueue(MockResponse().setBody("{}"))
        assertEquals(ApiFailure.IncompatibleContract, (api.capabilities(credential()) as ApiResult.Failure).reason)
        server.enqueue(MockResponse().setResponseCode(500).setBody(fixture("capabilities-current.json")))
        assertEquals(ApiFailure.Http(500), (api.capabilities(credential()) as ApiResult.Failure).reason)
    }

    @Test fun redirectsNeverForwardTheBearerCredential() = runTest {
        MockWebServer().use { other ->
            other.start()
            server.enqueue(MockResponse().setResponseCode(302).setHeader("Location", other.url("/capture")))
            assertEquals(ApiFailure.Http(302), (api.capabilities(credential()) as ApiResult.Failure).reason)
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
        val unknown = api.capabilities(credential()) as ApiResult.Failure
        assertNull(unknown.code)
        assertFalse(unknown.toString().contains("private"))
        server.enqueue(MockResponse().setResponseCode(401).setBody("""{"detail":"retry_history_changed"}"""))
        val unauthorized = api.capabilities(credential()) as ApiResult.Failure
        assertEquals(ApiFailure.Unauthorized, unauthorized.reason)
        assertNull(unauthorized.code)
    }

    @Test fun busyPreservesNumericAndHttpDateRetryAfter() = runTest {
        server.enqueue(MockResponse().setResponseCode(429).setHeader("Retry-After", "600"))
        assertEquals(ApiFailure.Busy(600), (api.capabilities(credential()) as ApiResult.Failure).reason)
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", ZonedDateTime.now(java.time.ZoneOffset.UTC).plusSeconds(30).format(DateTimeFormatter.RFC_1123_DATE_TIME)))
        val date = (api.capabilities(credential()) as ApiResult.Failure).reason as ApiFailure.Busy
        assertTrue(checkNotNull(date.retryAfterSeconds) in 28..30)
        server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "-10"))
        assertEquals(ApiFailure.Busy(null), (api.capabilities(credential()) as ApiResult.Failure).reason)
    }
}
