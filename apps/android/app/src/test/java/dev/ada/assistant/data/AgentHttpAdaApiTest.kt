package dev.ada.assistant.data

import java.util.UUID
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.encodeToString
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.Assert.*
import org.junit.Test

class AgentHttpAdaApiTest {
    @Test fun exactAgentRoutesAreAuthenticatedOneShotAndLocallyValidated() = runTest {
        val server = MockWebServer(); server.start()
        try {
            val c = ConnectionCredential.parse(server.url("/").newBuilder().host("127.0.0.1").build().toString(), "synthetic-only", true)!!
            val run = UUID.randomUUID(); val p = AgentJournal(SessionIdentity(c.server.toString(), UUID.randomUUID()), UUID.randomUUID(), UUID.randomUUID(), run, adaJson.encodeToString(AgentInputDto(run, "Calculate 2+3", allowed_tools = listOf("calculator"))))
            val api = HttpAdaApi()
            server.enqueue(MockResponse().setResponseCode(503).setHeader("Retry-After", "0"))
            assertTrue(api.createAgentRun(c, p) is ApiResult.Failure)
            val sent = server.takeRequest(); assertEquals("/v1/conversations/${p.conversationId}/agent-runs", sent.path); assertEquals(p.body, sent.body.readUtf8()); assertEquals("Bearer synthetic-only", sent.getHeader("Authorization")); assertEquals(1, server.requestCount)
            for (kind in listOf("approve", "revoke")) {
                val key = UUID.randomUUID(); val step = UUID.randomUUID(); val op = AgentOperation(kind, key, step, adaJson.encodeToString(AgentApprovalDto(key, "a".repeat(64), "b".repeat(64), "calculator-v1")))
                server.enqueue(MockResponse().setResponseCode(409))
                assertTrue(api.agentOperation(c, p.copy(operation = op)) is ApiResult.Failure)
                val request = server.takeRequest(); assertEquals("/v1/agent-runs/$run/steps/$step/$kind", request.path); assertEquals(op.body, request.body.readUtf8())
            }
            val key = UUID.randomUUID(); val recover = AgentOperation("recover", key, body = adaJson.encodeToString(AgentRecoverDto(key, 2)))
            server.enqueue(MockResponse().setResponseCode(409)); api.agentOperation(c, p.copy(operation = recover)); assertEquals("/v1/agent-runs/$run/recover", server.takeRequest().path)
            val count = server.requestCount
            assertEquals(ApiFailure.Validation, (api.createAgentRun(c, p.copy(body = p.body.replace("calculator", "shell"))) as ApiResult.Failure).reason)
            assertEquals(count, server.requestCount)
        } finally { server.shutdown() }
    }
    @Test fun futureCapabilitiesCannotEnableAnUnimplementedRegistry() {
        val legacy = adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json")); assertFalse(legacy.hasAgentTools())
        assertFalse(legacy.copy(agent_tools = "approval_read_only_v1", agent_protocol = "ada-agent-v1", agent_registry = selectedAgentTools.toList() + "shell").hasAgentTools())
    }
}
