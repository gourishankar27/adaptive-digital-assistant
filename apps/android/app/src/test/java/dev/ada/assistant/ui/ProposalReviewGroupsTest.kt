package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID
import kotlinx.serialization.json.JsonObject
import org.junit.Assert.*
import org.junit.Test

class ProposalReviewGroupsTest {
    private val scope = UUID.randomUUID()
    private val source = SourcePinDto(UUID.randomUUID(), 1, "a".repeat(64), 0, 8)
    private fun proposal(candidate: ProposalCandidateDto) = ProposalDto(UUID.randomUUID(), scope,
        UUID.randomUUID(), "pending", 1, candidate, candidate, "fixture", "v1", JsonObject(emptyMap()), emptyList(), emptyList(), "a".repeat(64), created_at = 0)
    @Test fun sameAnnotationStillRetainsEveryReviewAndSeparatesScopeTimeAndSupport() {
        val candidate = ProposalCandidateDto("Mira", "beverage", "tea", "preference", support = listOf(source))
        val a = proposal(candidate)
        val b = proposal(candidate.copy(confidence = 0.9))
        val groups = proposalReviewGroups(listOf(a, b, proposal(candidate.copy(valid_from = "2025-01-01T00:00:00Z")),
            proposal(candidate.copy(support = listOf(source.copy(span_end = 7)))), a.copy(id = UUID.randomUUID(), scope_id = UUID.randomUUID())))
        assertEquals(4, groups.size)
        assertEquals(listOf(a.id, b.id), groups.first().map { it.id })
        assertEquals(5, groups.sumOf { it.size })
        assertEquals(2, proposalReviewGroups(listOf(a, a.copy(id = UUID.randomUUID(), status = "accepted"))).size)
    }
}
