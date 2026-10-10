package dev.ada.assistant.data

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

/** Synthetic evidence only: transport tests never log or persist private API content. */
class MemoryHttpAdaApiTest {
    private lateinit var server: MockWebServer
    private val api = HttpAdaApi()
    private val scope = UUID.fromString("00000000-0000-0000-0000-000000000003")
    private val source = adaJson.decodeFromString<SourceVersionDto>(fixture("source-current.json"))
    private val claim = adaJson.decodeFromString<ClaimDto>(fixture("claim-current.json"))
    @Before fun setup() { server = MockWebServer(); server.start() }
    @After fun cleanup() { server.shutdown() }
    private fun credential() = checkNotNull(ConnectionCredential.parse(
        server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-test-only", true))

    @Test fun ownedMemoryQueriesUseExactScopePaginationAndTimeMode() = runTest {
        server.enqueue(MockResponse().setBody("[]"))
        assertTrue((api.claims(credential(), scope, 25, 50, asOf = "2026-10-09T08:00:00.123+02:00") as ApiResult.Success).value.isEmpty())
        val dated = server.takeRequest()
        assertEquals("/v1/scopes/$scope/claims", dated.requestUrl?.encodedPath)
        assertEquals("25", dated.requestUrl?.queryParameter("limit"))
        assertEquals("50", dated.requestUrl?.queryParameter("offset"))
        assertEquals("false", dated.requestUrl?.queryParameter("history"))
        assertEquals("2026-10-09T08:00:00.123+02:00", dated.requestUrl?.queryParameter("as_of"))
        assertEquals("Bearer synthetic-test-only", dated.getHeader("Authorization"))
        assertFalse(dated.requestUrl.toString().contains("synthetic-test-only"))
        server.enqueue(MockResponse().setBody(fixture("claims-history.json")))
        assertTrue((api.claims(credential(), scope, history = true) as ApiResult.Success).value.isNotEmpty())
        val history = server.takeRequest()
        assertEquals("true", history.requestUrl?.queryParameter("history"))
        assertNull(history.requestUrl?.queryParameter("as_of"))
        server.enqueue(MockResponse().setBody(fixture("sources-current.json")))
        api.sources(credential(), scope, 20, 40)
        val sources = server.takeRequest()
        assertEquals("/v1/scopes/$scope/source-versions", sources.requestUrl?.encodedPath)
        assertEquals("20", sources.requestUrl?.queryParameter("limit"))
        assertEquals("40", sources.requestUrl?.queryParameter("offset"))
    }

    @Test fun memoryWriteReplayRetainsOriginalIdsAndExactPayloadWithoutAuthorityFields() = runTest {
        val note = NoteInputDto(source.source_id, "😀 e\u0301\r\nनमस्ते 中文  ")
        val assertion = ClaimInputDto(claim.id, source.id, 0, 1, "ADA", "language", "Python", "decision",
            "2025-01-01T00:00:00.123Z", "2027-01-01T00:00:00.124Z")
        val replacement = SupersedeInputDto(UUID.fromString("00000000-0000-0000-0000-00000000000d"),
            UUID.fromString("00000000-0000-0000-0000-00000000000c"), 0, 15, "Java", "2025-06-01T00:00:00.123Z")
        val operations: List<Triple<String, String, suspend () -> ApiResult<*>>> = listOf(
            Triple("scopes/$scope/notes", adaJson.encodeToString(note)) { api.createNote(credential(), scope, note) },
            Triple("scopes/$scope/claims", adaJson.encodeToString(assertion)) { api.createClaim(credential(), scope, assertion) },
            Triple("claims/${claim.id}/supersede", adaJson.encodeToString(replacement)) { api.supersede(credential(), claim.id, replacement) },
        )
        for ((index, operation) in operations.withIndex()) {
            val response = fixture(listOf("source-current.json", "claim-current.json", "claim-correction.json")[index])
            for (status in listOf(201, 200)) {
                server.enqueue(MockResponse().setResponseCode(status).setBody(response))
                assertTrue(operation.third() is ApiResult.Success)
                val sent = server.takeRequest()
                assertEquals("POST", sent.method)
                assertEquals("/v1/${operation.first}", sent.path)
                assertEquals("Bearer synthetic-test-only", sent.getHeader("Authorization"))
                val payload = sent.body.readUtf8()
                assertEquals(operation.second, payload)
                val fields = adaJson.parseToJsonElement(payload).toString()
                for (authority in listOf("\"owner_id\"", "\"trust_class\"", "\"confidence\"", "\"quote\"", "\"content_hash\"")) {
                    assertFalse(fields.contains(authority))
                }
            }
        }
    }

    @Test fun allMemoryWritesRemainOneShotAtBusyAndUnknownOutcome() = runTest {
        val note = NoteInputDto(source.source_id, source.content)
        val assertion = ClaimInputDto(claim.id, source.id, 2, 19, "ADA", "language", "Python", "decision")
        val replacement = SupersedeInputDto(UUID.randomUUID(), source.id, 2, 19, "Java")
        val operations: List<suspend () -> ApiResult<*>> = listOf(
            { api.createNote(credential(), scope, note) },
            { api.createClaim(credential(), scope, assertion) },
            { api.supersede(credential(), claim.id, replacement) },
        )
        for ((index, send) in operations.withIndex()) {
            server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
            assertEquals(ApiFailure.Busy(0), (send() as ApiResult.Failure).reason)
            assertEquals(index + 1, server.requestCount)
            server.takeRequest()
        }
        server.enqueue(MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE))
        assertEquals(ApiFailure.Timeout, (HttpAdaApi(callTimeoutMillis = 150)
            .createNote(credential(), scope, note) as ApiResult.Failure).reason)
        assertEquals(4, server.requestCount)
    }

    @Test fun fixedMemoryConflictsAndValidationCodesSupportRecoveryWithoutRawBodies() = runTest {
        val cases = mapOf(
            "source_id_reused" to 409, "source_conflict" to 409, "claim_id_reused" to 409,
            "claim_duplicate" to 409, "claim_conflict" to 409, "claim_already_superseded" to 409,
            "evidence_content_changed" to 409, "source_not_user_evidence" to 422,
            "invalid_evidence_span" to 422, "empty_evidence_span" to 422,
            "invalid_validity_interval" to 422, "correction_outside_validity_interval" to 422,
            "history_and_as_of_conflict" to 422, "invalid_query_value" to 422,
        )
        for ((code, status) in cases) {
            server.enqueue(MockResponse().setResponseCode(status).setBody("""{"detail":"$code","input":"private-quote-and-token"}"""))
            val result = api.createClaim(credential(), scope,
                ClaimInputDto(claim.id, source.id, 2, 19, "ADA", "language", "Python")) as ApiResult.Failure
            assertEquals(if (status == 409) ApiFailure.Conflict else ApiFailure.Validation, result.reason)
            assertEquals(code, result.code)
            assertFalse(result.toString().contains("private"))
        }
        server.enqueue(MockResponse().setResponseCode(422).setBody("""{"detail":"private-source-quote"}"""))
        val unknown = api.createNote(credential(), scope, NoteInputDto(source.source_id, "Synthetic")) as ApiResult.Failure
        assertNull(unknown.code)
        assertFalse(unknown.toString().contains("private"))
    }

    @Test fun unauthorizedAndGuessedMemoryIdsStayFailuresWithoutCachedFallback() = runTest {
        server.enqueue(MockResponse().setResponseCode(401).setBody("""{"detail":"claim_duplicate"}"""))
        val unauthorized = api.createNote(credential(), scope, NoteInputDto(source.source_id, source.content)) as ApiResult.Failure
        assertEquals(ApiFailure.Unauthorized, unauthorized.reason)
        assertNull(unauthorized.code)
        server.enqueue(MockResponse().setResponseCode(404).setBody(fixture("source-current.json")))
        assertEquals(ApiFailure.NotFound, (api.source(credential(), UUID.randomUUID()) as ApiResult.Failure).reason)
        server.enqueue(MockResponse().setResponseCode(404).setBody(fixture("claim-current.json")))
        assertEquals(ApiFailure.NotFound, (api.claim(credential(), UUID.randomUUID()) as ApiResult.Failure).reason)
        assertEquals(3, server.requestCount)
    }
}
