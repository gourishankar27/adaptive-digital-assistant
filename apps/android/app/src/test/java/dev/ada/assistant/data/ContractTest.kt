package dev.ada.assistant.data

import java.util.UUID
import org.junit.Assert.*
import org.junit.Test

internal fun fixture(name: String): String = checkNotNull(ContractTest::class.java.classLoader?.getResource(name)).readText()

class ContractTest {
    @Test fun currentAndLegacyActualServerFixturesDecode() {
        val current = adaJson.decodeFromString<RequestDto>(fixture("request-current.json"))
        val legacy = adaJson.decodeFromString<RequestDto>(fixture("request-legacy.json"))
        assertEquals(ObservedRequestState.Completed, current.observedState)
        assertEquals(ObservedRequestState.Completed, legacy.observedState)
        assertTrue(legacy.citations.isEmpty())
        assertTrue(current.citations.isNotEmpty())
        assertTrue(current.citations.first().valid_from > Int.MAX_VALUE)
        adaJson.decodeFromString<ConversationDto>(fixture("conversation-current.json"))
        adaJson.decodeFromString<ConversationDto>(fixture("conversation-legacy.json"))
        adaJson.decodeFromString<RetrievalDto>(fixture("retrieval-current.json"))
        adaJson.decodeFromString<TraceDto>(fixture("retrieval-additive.json"))
        adaJson.decodeFromString<CapabilitiesDto>(fixture("capabilities-current.json"))
        adaJson.decodeFromString<ErrorEnvelopeDto>(fixture("error-validation.json"))
        adaJson.decodeFromString<ErrorEnvelopeDto>(fixture("error-auth.json"))
    }

    @Test fun futureStatesAndOptionalFieldsNeverBecomeCompleted() {
        val json = fixture("request-legacy.json").replace("\"completed\"", "\"future_state\"")
            .trimEnd().removeSuffix("}") + ",\"future_optional\":true}"
        val value = adaJson.decodeFromString<RequestDto>(json)
        assertEquals("future_state", value.status)
        assertEquals(ObservedRequestState.Unknown, value.observedState)
    }

    @Test fun legacyOmittedCitationFieldsAndLongMillisArePreserved() {
        val json = """{"request_id":"00000000-0000-4000-8000-000000000001","conversation_id":"00000000-0000-4000-8000-000000000002","status":"completed","response":"saved","attempt":1,"provider":"fake","model":"fake"}"""
        assertTrue(adaJson.decodeFromString<RequestDto>(json).citations.isEmpty())
        val scope = adaJson.decodeFromString<ScopeDto>("""{"id":"00000000-0000-4000-8000-000000000003","name":"test","kind":"future_kind","created_at":253402300799000}""")
        assertEquals(253402300799000L, scope.created_at)
        assertEquals("future_kind", scope.kind)
        val upgrade = adaJson.decodeFromString<PromptUpgradeDto>("""{"id":"00000000-0000-4000-8000-000000000002","prompt_version":"ada-baseline-v3","revision":2}""")
        assertEquals(UUID.fromString("00000000-0000-4000-8000-000000000002"), upgrade.id)
    }

    @Test fun exactUnicodeSelectionsConvertWithoutNormalization() {
        val text = "A😀 e\u0301\r\nZ"
        assertEquals(2, utf16ToCodePointOffset(text, 3))
        assertEquals(3, codePointToUtf16Offset(text, 2))
        for (offset in 0..text.codePointCount(0, text.length)) {
            assertEquals(offset, utf16ToCodePointOffset(text, codePointToUtf16Offset(text, offset)))
        }
        assertThrows(IllegalArgumentException::class.java) { utf16ToCodePointOffset(text, 2) }
        assertEquals("😀 e\u0301", text.substring(codePointToUtf16Offset(text, 1), codePointToUtf16Offset(text, 5)))
    }
}
