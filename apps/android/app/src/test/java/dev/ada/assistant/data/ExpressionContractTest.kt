package dev.ada.assistant.data

import org.junit.Assert.*
import org.junit.Test
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonObject

class ExpressionContractTest {
    private fun fixture(name: String) = checkNotNull(javaClass.classLoader!!.getResource(name)).readText()
    @Test fun actualHttpExpressionFixturesDecodeWithExactReceiptAndSourceBindings() {
        val expression = adaJson.decodeFromString<ExpressionDto>(fixture("expression-current.json"))
        validateExpression(expression); assertEquals("concise", expression.preferences.verbosity)
        val receipt = adaJson.decodeFromString<ExpressionReceiptDto>(fixture("expression-preference-receipt.json"))
        assertEquals(receipt.operation_id, receipt.preference!!.receipt_id)
        assertEquals(receipt.operation_id, expression.source_receipts["verbosity"])
        assertEquals("explicit_settings", receipt.reason)
        val signal = adaJson.decodeFromString<ExpressionReceiptDto>(fixture("expression-signal-receipt.json"))
        validateExpression(signal.expression!!); assertEquals("reviewed_model_signal", signal.reason)
        assertEquals(70, signal.expression.vector.warmth)
        assertEquals("none", signal.expression.preferences.humor)
        val reset = adaJson.decodeFromString<ExpressionReceiptDto>(fixture("expression-reset-receipt.json"))
        validateExpression(reset.expression!!); assertEquals(60, reset.expression.vector.warmth)
    }
    @Test fun unsupportedRangesAndPsychologicalFieldsFailClosed() {
        val expression = adaJson.decodeFromString<ExpressionDto>(fixture("expression-current.json"))
        try { validateExpression(expression.copy(vector = expression.vector.copy(warmth = 101))); fail("range accepted") } catch (_: IllegalArgumentException) { }
        try { validatePreferences(PreferenceValuesDto(initiative = "execute_shell")); fail("authority accepted") } catch (_: IllegalArgumentException) { }
        val raw = adaJson.parseToJsonElement(fixture("capabilities-current.json")).jsonObject
        val legacy = adaJson.decodeFromString<CapabilitiesDto>(JsonObject(raw.filterKeys { it !in setOf("interaction_preferences", "session_expression", "automatic_affect_inference") }).toString())
        assertEquals("unsupported", legacy.session_expression)
    }
}
