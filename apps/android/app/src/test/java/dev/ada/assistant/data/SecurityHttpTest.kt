package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class SecurityHttpTest {
    @Test fun changedEpochSuppressesPrivateBodyAndSecurityReplayUsesExactUuid() = runTest {
        MockWebServer().use { server ->
            val c = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-security", true)!!
            c.dataEpoch = 0
            server.enqueue(MockResponse().addHeader("X-ADA-Data-Epoch", "1").setBody("[]"))
            val api = HttpAdaApi()
            assertEquals(ApiFailure.Unauthorized, (api.scopes(c) as ApiResult.Failure).reason)
            server.takeRequest()
            val owner = UUID.randomUUID(); val job = UUID.randomUUID(); val preview = UUID.randomUUID()
            val journal = SecurityJournal(SessionIdentity(c.server.toString(), owner), "delete", job, preview = preview)
            server.enqueue(MockResponse().setResponseCode(503).setBody("{}"))
            api.deleteContent(c, journal)
            val request = server.takeRequest()
            assertEquals("/v1/security/deletions", request.path)
            val body = adaJson.decodeFromString<DeletionInputDto>(request.body.readUtf8())
            assertEquals(job, body.job_id); assertEquals(preview, body.preview_id); assertEquals("erase_saved_content", body.confirmation)
        }
    }
}
