package dev.ada.assistant.data

import java.time.Instant
import java.util.UUID
import org.junit.Assert.*
import org.junit.Test

class MemoryEvidenceContractTest {
    private val source = adaJson.decodeFromString<SourceVersionDto>(fixture("source-current.json"))
    private val claim = adaJson.decodeFromString<ClaimDto>(fixture("claim-current.json"))

    @Test fun codePointSelectionUsesExactReturnedContentAndHash() {
        val quote = "e\u0301\r\nनमस्ते 中文"
        val text = "😀 $quote 🦋"
        // Fixed SHA-256 computed independently over the synthetic UTF-8 text.
        val version = source.copy(content = text,
            content_hash = "01ee6a4e8ea6892e3b3fa489759bbe8cffa3e8b054163626bf359cd46c72c339")
        val evidence = exactEvidenceSelection(version, version.scope_id, 3, 3 + quote.length)
        assertEquals(quote, evidence.quote)
        assertEquals(2, evidence.span_start)
        assertEquals(2 + quote.codePointCount(0, quote.length), evidence.span_end)
        assertEquals(version.id, evidence.source_version_id)
        assertEquals(version.content_hash, evidence.content_hash)
        assertEquals(3, codePointToUtf16Offset(text, evidence.span_start))
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(version, version.scope_id, 1, text.length) }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(version, version.scope_id, 0, text.length - 1) }
    }

    @Test fun writeSelectionRejectsForeignScopeModelTrustAndChangedOrInvalidSourceBytes() {
        val badVersions = listOf(source.copy(trust_class = "model_generated"), source.copy(trust_class = "future_trust"),
            source.copy(content = source.content + " "), source.copy(content_hash = "0".repeat(64)),
            source.copy(content = "unpaired \uD83D"), source.copy(content = "\u0000"))
        for (version in badVersions) assertThrows(IllegalArgumentException::class.java) {
            exactEvidenceSelection(version, source.scope_id, 0, version.content.length)
        }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, UUID.randomUUID(), 0, source.content.length) }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, source.scope_id, 3, 3) }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, source.scope_id, 2, 3) }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, source.scope_id, -1, 3) }
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, source.scope_id, 0, source.content.length + 1) }
    }

    @Test fun readOnlyEvidenceVerificationChecksVersionScopeHashAndExactQuote() {
        assertTrue(verifyClaimEvidence(claim, source))
        assertTrue(verifyClaimEvidence(claim, source.copy(trust_class = "model_generated")))
        assertFalse(verifyClaimEvidence(claim, source.copy(id = UUID.randomUUID())))
        assertFalse(verifyClaimEvidence(claim, source.copy(scope_id = UUID.randomUUID())))
        assertFalse(verifyClaimEvidence(claim, source.copy(content = source.content.replace("Python", "Rust"))))
        assertFalse(verifyClaimEvidence(claim.copy(evidence = claim.evidence.copy(quote = claim.evidence.quote + " ")), source))
        assertFalse(verifyClaimEvidence(claim.copy(evidence = claim.evidence.copy(content_hash = "0".repeat(64))), source))
        assertFalse(verifyClaimEvidence(claim.copy(evidence = claim.evidence.copy(span_start = -1)), source))
        assertFalse(verifyClaimEvidence(claim.copy(evidence = claim.evidence.copy(span_end = 1_000)), source))
    }

    @Test fun timezoneNormalizationPreservesExactMillisecondsWithoutFloatingPoint() {
        assertNull(normalizeUtcMillis("  "))
        assertEquals("2026-10-09T06:00:00.123Z", normalizeUtcMillis("2026-10-09T08:00:00.123+02:00"))
        assertEquals("1969-12-31T23:59:59.999Z", normalizeUtcMillis("1969-12-31T23:59:59.999Z"))
        assertEquals(-1L, Instant.parse(normalizeUtcMillis("1969-12-31T23:59:59.999Z")).toEpochMilli())
        assertEquals("9999-12-31T23:59:59.999Z", normalizeUtcMillis("9999-12-31T23:59:59.999Z"))
        assertEquals(253402300799999L, Instant.parse(normalizeUtcMillis("9999-12-31T23:59:59.999Z")).toEpochMilli())
        for (invalid in listOf("2026-10-09T08:00:00", "2026-10-09T08:00:00.123001Z",
            "0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00", "2026-10-09", "not a time")) {
            assertThrows(Exception::class.java) { normalizeUtcMillis(invalid) }
        }
    }

    @Test fun sourceAndClaimDtoTimesKeepFullSignedInt64Precision() {
        val high = fixture("source-current.json").replace("1791417600000", Long.MAX_VALUE.toString())
        val low = fixture("claim-current.json").replace("1735689600000", Long.MIN_VALUE.toString())
        assertEquals(Long.MAX_VALUE, adaJson.decodeFromString<SourceVersionDto>(high).created_at)
        assertEquals(Long.MIN_VALUE, adaJson.decodeFromString<ClaimDto>(low).valid_from)
        val history = adaJson.decodeFromString<List<ClaimDto>>(fixture("claims-history.json"))
        assertEquals("superseded", history.first().status)
        assertEquals(1748736000000L, history.first().valid_to)
        assertEquals(UUID.fromString("00000000-0000-0000-0000-00000000000d"), history.first().superseded_by)
        assertEquals(history.first().evidence, claim.evidence)
    }
}
