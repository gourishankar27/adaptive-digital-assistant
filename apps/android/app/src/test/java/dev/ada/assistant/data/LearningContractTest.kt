package dev.ada.assistant.data

import java.util.UUID
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonObject
import org.junit.Assert.*
import org.junit.Test

class LearningContractTest {
    private val owner = SessionIdentity("https://ada.example/", UUID.randomUUID())
    @Test fun actualHttpLearningFixturesKeepSourceTrustAndReviewIdentity() {
        val state = adaJson.decodeFromString<LearningStateDto>(fixture("learning-state.json"))
        val identity = SessionIdentity(owner.server, state.observations.first().owner_id)
        validateLearningState(state, identity, state.config.scope_id)
        assertEquals(3, state.proposals.single().independent_count); assertTrue(state.proposals.single().eligible)
        val receipt = adaJson.decodeFromString<LearningReceiptDto>(fixture("learning-review-receipt.json"))
        assertEquals(state.proposals.single().id, receipt.proposal_id); assertEquals("approve", receipt.decision)
        val approved = adaJson.decodeFromString<LearningStateDto>(fixture("learning-state-approved.json"))
        validateLearningState(approved, identity, state.config.scope_id)
        assertEquals(receipt.observation_ids, approved.learned.single().observation_ids)
        assertEquals(receipt.proposal_revision, approved.learned.single().reviewed_revision)
        try { validateLearningState(state.copy(observations = state.observations.map { it.copy(owner_id = UUID.randomUUID()) }), identity, state.config.scope_id); fail("Foreign evidence accepted") } catch(_: IllegalArgumentException) {}
    }
    @Test fun unknownAuthorityAndImplicitReviewAreRejected() {
        val key = UUID.randomUUID(); val sid = UUID.randomUUID()
        for(body in listOf("""{"operation_id":"$key","expected_revision":0,"status":"enrolled","owner_id":"${owner.owner}"}""",
            """{"operation_id":"$key","proposal_id":"$sid","expected_revision":1,"decision":"approve"}""")) {
            try { validateLearningJournal(LearningJournal(owner, sid, key, if(body.contains("proposal_id")) "review" else "config", body)); fail("Invalid journal accepted") } catch(_: IllegalArgumentException) {}
        }
    }
    @Test fun exactConfigAndReviewedEnumStayBounded() {
        val key = UUID.randomUUID(); val sid = UUID.randomUUID()
        validateLearningJournal(LearningJournal(owner, sid, key, "config", adaJson.encodeToString(LearningConfigWriteDto(key, 0, "enrolled"))))
        for(field in preferenceChoices.keys) for(value in preferenceChoices.getValue(field)) assertEquals(mapOf(field to value), preferenceMap(singlePreference(field, value)))
    }
    @Test fun legacyRequestAndCapabilitiesDoNotInventLearningOrContinuity() {
        val legacy = JsonObject(adaJson.parseToJsonElement(fixture("capabilities-current.json")).jsonObject - "interaction_learning")
        val caps = adaJson.decodeFromString<CapabilitiesDto>(legacy.toString())
        assertEquals("unsupported", caps.interaction_learning)
        val request = adaJson.decodeFromString<RequestDto>(fixture("request-legacy.json"))
        assertTrue(request.continuity_citations.isEmpty())
    }
}
