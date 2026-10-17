package dev.ada.assistant.data

import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class ServerProfilesTest {
    @Test fun proxyFailureAndUnknown503DoNotFalselyDiagnoseDatabaseOrSendCredentials() = runTest {
        MockWebServer().use { server ->
            server.start()
            val credential = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-only", true)!!
            for ((status, body, expected) in listOf(
                Triple(502, "{}", ApiFailure.Unreachable),
                Triple(503, "{}", ApiFailure.Http(503)),
                Triple(503, """{"detail":"database_not_ready"}""", ApiFailure.ServerNotReady),
            )) {
                server.enqueue(MockResponse().setResponseCode(status).setHeader("Content-Type", "application/json").setBody(body))
                assertEquals(expected, (HttpAdaApi().me(credential) as ApiResult.Failure).reason)
                assertNull(server.takeRequest().getHeader("Authorization"))
            }
        }
    }
    @Test fun networkDiagnosticsDoNotMislabelGenericFailuresAsVpnRevocation() {
        assertEquals(ApiFailure.Tls, connectionFailure(javax.net.ssl.SSLHandshakeException("synthetic private diagnostic")))
        assertEquals(ApiFailure.Dns, connectionFailure(java.net.UnknownHostException("synthetic private diagnostic")))
        assertEquals(ApiFailure.Timeout, connectionFailure(java.net.SocketTimeoutException()))
        assertEquals(ApiFailure.Unreachable, connectionFailure(java.net.ConnectException()))
    }
    @Test fun profilesCanonicalizeOriginsAndRejectCredentialOrPathSmuggling() {
        assertEquals("https://ada.example/", ServerProfile.parse("Laptop", "https://ADA.example:443")?.origin)
        assertNotNull(ServerProfile.parse("IPv6", "https://[fd00::1]:8443"))
        for (origin in listOf("http://192.168.1.2", "https://user:secret@ada.example", "https://ada.example/a", "https://ada.example/?token=x", "https://ada.example/#x", "https://ada.example\\@evil.example", "https://ada.example/../")) {
            assertNull(origin, ServerProfile.parse("Laptop", origin))
        }
        assertNull(ServerProfile.parse("\nBad label", "https://ada.example"))
    }

    @Test fun importsAreStrictVersionedMetadataAndNeverActivateAnything() {
        val profile = ServerProfile.parse("Home laptop", "https://ada.example")!!
        assertEquals(profile, ServerProfiles.decodeImport(ServerProfiles.encodeImport(profile)))
        for (payload in listOf("{}", """{"version":2,"label":"Home","origin":"https://ada.example"}""", """{"version":1,"label":"Home","origin":"https://ada.example","token":"secret"}""", """{"version":1,"label":"Home","origin":"http://192.168.1.2"}""", "<script>bad</script>")) {
            assertNull(ServerProfiles.decodeImport(payload))
        }
        assertNull(ServerProfiles.decodeImport("x".repeat(2049)))
    }

    @Test fun corruptOrOversizedProfileStoresFailClosed() {
        assertTrue(ServerProfiles.decodeSaved("not json").isEmpty())
        val p = ServerProfile.parse("Home", "https://ada.example")!!
        assertEquals(listOf(p), ServerProfiles.decodeSaved(ServerProfiles.encodeSaved(listOf(p))))
        assertTrue(ServerProfiles.decodeSaved("[{}]").isEmpty())
        assertNull(ServerProfile.parse("Home", "https://" + "a.".repeat(300) + "example"))
        assertTrue(ServerProfiles.decodeSaved(" ".repeat(24577)).isEmpty())
        val tooMany = (0..12).map { ServerProfile.parse("Server $it", "https://s$it.example")!! }
        assertTrue(ServerProfiles.decodeSaved(kotlinx.serialization.json.Json.encodeToString(kotlinx.serialization.builtins.ListSerializer(ServerProfile.serializer()), tooMany)).isEmpty())
    }

    @Test fun failedReadinessNeverSendsTheTokenAndDoesNotFollowRedirects() = runTest {
        MockWebServer().use { server ->
            server.start()
            val credential = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-only", true)!!
            server.enqueue(MockResponse().setResponseCode(302).setHeader("Location", "https://other.example"))
            assertTrue(HttpAdaApi().me(credential) is ApiResult.Failure)
            val request = server.takeRequest()
            assertEquals("/health/ready", request.path)
            assertNull(request.getHeader("Authorization"))
            assertEquals(1, server.requestCount)
        }
    }

    @Test fun readyProbePrecedesAuthenticatedMeAndRejectsSpoofedOrHugeBodies() = runTest {
        MockWebServer().use { server ->
            server.start()
            val credential = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-only", true)!!
            server.enqueue(MockResponse().setHeader("Content-Type", "application/json").setBody("""{"status":"ready","schema":"0015"}"""))
            server.enqueue(MockResponse().setBody("""{"id":"00000000-0000-4000-8000-000000000001","name":"Synthetic"}"""))
            assertTrue(HttpAdaApi().me(credential) is ApiResult.Success)
            assertNull(server.takeRequest().getHeader("Authorization"))
            assertEquals("Bearer synthetic-only", server.takeRequest().getHeader("Authorization"))
            for (body in listOf("<html>ready</html>", """{"status":"ready","schema":"internal-details"}""", " ".repeat(2048))) {
                server.enqueue(MockResponse().setHeader("Content-Type", "application/json").setBody(body))
                assertTrue(HttpAdaApi().me(credential) is ApiResult.Failure)
                assertNull(server.takeRequest().getHeader("Authorization"))
            }
        }
    }
}
