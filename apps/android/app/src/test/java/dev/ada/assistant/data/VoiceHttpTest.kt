package dev.ada.assistant.data

import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class VoiceHttpTest {
    @Test fun actualServerVoiceFixturesUseAuthenticatedTypedSubmissionAndHonestProvenance() = runTest {
        val lineage = adaJson.decodeFromString<VoiceLineageDto>(fixture("voice-lineage.json"))
        lineage.validate(lineage.conversation_id, lineage.scope_id)
        assertNotEquals(lineage.original_text, lineage.reviewed_text)
        assertEquals("generated_interpretation", lineage.original_trust); assertNull(lineage.audio_sha256)
        val server = MockWebServer(); server.start()
        try {
            val c = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-voice-http", true)!!
            val api = HttpAdaApi()
            server.enqueue(MockResponse().setResponseCode(202).setBody(fixture("voice-started.json")))
            val transcript = TranscriptInputDto(lineage.transcript_id, lineage.engine_id, lineage.engine_version, lineage.language, lineage.duration_ms, lineage.original_text)
            val body = ReviewedVoiceInputDto(lineage.request_id, lineage.reviewed_text, transcript)
            assertTrue(api.submitVoice(c, lineage.conversation_id, body) is ApiResult.Success)
            val request = server.takeRequest()
            assertEquals("/v1/conversations/${lineage.conversation_id}/voice-requests", request.path)
            assertEquals("Bearer synthetic-voice-http", request.getHeader("Authorization"))
            assertEquals(body, adaJson.decodeFromString<ReviewedVoiceInputDto>(request.body.readUtf8()))
            server.enqueue(MockResponse().setBody(fixture("voice-lineage.json")))
            assertEquals(lineage, (api.voiceInput(c, lineage.request_id) as ApiResult.Success).value)
            assertEquals("/v1/requests/${lineage.request_id}/voice-input", server.takeRequest().path)
            server.enqueue(MockResponse().setBody(fixture("voice-inputs.json")))
            assertEquals(listOf(lineage), (api.voiceInputs(c, lineage.conversation_id) as ApiResult.Success).value)
            assertEquals("/v1/conversations/${lineage.conversation_id}/voice-inputs", server.takeRequest().path)
        } finally { server.shutdown() }
    }
    @Test fun forgedTrustHashesAndScopeAreRejected() {
        val row = adaJson.decodeFromString<VoiceLineageDto>(fixture("voice-lineage.json"))
        for (bad in listOf(row.copy(original_trust = "user_explicit"), row.copy(audio_sha256 = "0".repeat(64)), row.copy(reviewed_hash = "0".repeat(64)), row.copy(original_text = "Forged"))) {
            try { bad.validate(row.conversation_id, row.scope_id); fail("Forged lineage accepted") } catch (_: IllegalArgumentException) { }
        }
    }
}
