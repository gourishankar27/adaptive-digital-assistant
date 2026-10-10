package dev.ada.assistant

import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.*
import java.io.File
import java.time.Instant
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test

/** Authenticated HTTP against the disposable migrated server; all content is synthetic. */
class MemoryHttpIntegrationTest {
    private val api = HttpAdaApi()
    private fun credential(): ConnectionCredential {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val tokenFile = File(context.filesDir, "foundation-test-token")
        assumeTrue("Provision the disposable Android fixture server with verify-emulator.ps1", tokenFile.isFile)
        return checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", tokenFile.readText().trim(), true))
    }
    private fun <T> success(result: ApiResult<T>): T {
        check(result is ApiResult.Success) { "The synthetic authenticated memory HTTP prerequisite failed" }
        return result.value
    }
    private fun failure(result: ApiResult<*>, reason: ApiFailure, code: String? = null) {
        check(result is ApiResult.Failure) { "The synthetic memory boundary was not rejected" }
        assertEquals(reason, result.reason)
        if (code != null) assertEquals(code, result.code)
    }

    @Test fun unicodeEvidenceSameIdReplayAndConflictsStayOwnedAndExact() = runBlocking {
        val credential = credential()
        val scope = success(api.createScope(credential, ScopeInputDto("Unicode memory verification")))
        val quote = "Memory HTTP project uses Oxford Blue. 😀 e\u0301\r\n日本語 العربية 中文"
        val content = "🙋 $quote\r\nEnd of synthetic note.  "
        val note = NoteInputDto(UUID.randomUUID(), content)
        val source = success(api.createNote(credential, scope.id, note))
        assertEquals(note.source_id, source.source_id)
        assertTrue(source.content == content)
        assertEquals("user_explicit", source.trust_class)
        assertTrue(source.created_at > Int.MAX_VALUE)
        assertTrue(success(api.createNote(credential, scope.id, note)) == source)
        failure(api.createNote(credential, scope.id, note.copy(content = content + " ")),
            ApiFailure.Conflict, "source_id_reused")
        val selected = exactEvidenceSelection(source, scope.id, 3, 3 + quote.length)
        assertEquals(2, selected.span_start)
        assertTrue(selected.quote == quote)
        assertThrows(IllegalArgumentException::class.java) { exactEvidenceSelection(source, scope.id, 1, source.content.length) }
        val body = ClaimInputDto(UUID.randomUUID(), source.id, selected.span_start, selected.span_end,
            "Memory HTTP project", "color", "Oxford Blue", "decision", "2026-01-01T00:00:00.123Z")
        val claim = success(api.createClaim(credential, scope.id, body))
        assertEquals(body.claim_id, claim.id)
        assertTrue(claim.evidence == selected && verifyClaimEvidence(claim, source))
        assertEquals(Instant.parse(body.valid_from).toEpochMilli(), claim.valid_from)
        assertTrue(success(api.createClaim(credential, scope.id, body)) == claim)
        failure(api.createClaim(credential, scope.id, body.copy(value = "Dark Red")), ApiFailure.Conflict, "claim_id_reused")
        failure(api.createClaim(credential, scope.id, body.copy(claim_id = UUID.randomUUID())), ApiFailure.Conflict, "claim_duplicate")
        failure(api.createClaim(credential, scope.id, body.copy(claim_id = UUID.randomUUID(),
            valid_from = "2026-01-01T00:00:00.123001Z")), ApiFailure.Validation)
        assertEquals(1, success(api.sources(credential, scope.id)).size)
        assertEquals(listOf(claim.id), success(api.claims(credential, scope.id)).map { it.id })
        assertEquals(listOf(claim.id), success(api.claims(credential, scope.id, history = true)).map { it.id })
        val otherScope = success(api.createScope(credential, ScopeInputDto("Separate memory verification")))
        failure(api.createClaim(credential, otherScope.id, body.copy(claim_id = UUID.randomUUID())), ApiFailure.NotFound)
        failure(api.source(credential, UUID.randomUUID()), ApiFailure.NotFound)
        failure(api.claim(credential, UUID.randomUUID()), ApiFailure.NotFound)
        val unauthorized = checkNotNull(ConnectionCredential.parse("http://10.0.2.2:18764", "invalid-test-only", true))
        failure(api.source(unauthorized, source.id), ApiFailure.Unauthorized)
        failure(api.claim(unauthorized, claim.id), ApiFailure.Unauthorized)
    }

    @Test fun futureCorrectionPreservesHalfOpenHistoryAndOriginalRequestSources() = runBlocking {
        val credential = credential()
        val scope = success(api.createScope(credential, ScopeInputDto("Future correction verification")))
        val note = success(api.createNote(credential, scope.id,
            NoteInputDto(UUID.randomUUID(), "Memory HTTP project uses Oxford Blue. 😀 e\u0301\r\n日本語")))
        val evidence = exactEvidenceSelection(note, scope.id, 0, note.content.length)
        val originalInput = ClaimInputDto(UUID.randomUUID(), note.id, evidence.span_start, evidence.span_end,
            "Memory HTTP project", "color", "Oxford Blue", "decision",
            "2026-01-01T00:00:00.123Z", "2091-01-01T00:00:00.111Z")
        val originalClaim = success(api.createClaim(credential, scope.id, originalInput))
        val profile = success(api.personalities(credential)).single { it.name == "ADA Test" }
        val conversation = success(api.createConversation(credential,
            ConversationInputDto(profile.id, "Synthetic original citation verification", scope.id)))
        val message = ChatInputDto(UUID.randomUUID(), "Which color does the Memory HTTP project use?")
        val original = success(api.send(credential, conversation.id, message))
        assertEquals("completed", original.status)
        assertTrue(original.response?.startsWith("[FAKE provider]") == true)
        assertEquals(originalClaim.id, original.citations.single().claim_id)
        val replacementNote = success(api.createNote(credential, scope.id,
            NoteInputDto(UUID.randomUUID(), "Memory HTTP project uses Olive Green from the future correction. 😀")))
        val replacementEvidence = exactEvidenceSelection(replacementNote, scope.id, 0, replacementNote.content.length)
        val correction = SupersedeInputDto(UUID.randomUUID(), replacementNote.id,
            replacementEvidence.span_start, replacementEvidence.span_end, "Olive Green", "2090-01-01T00:00:00.321Z")
        for (invalid in listOf(
            correction.copy(claim_id = UUID.randomUUID(), effective_at = originalInput.valid_from),
            correction.copy(claim_id = UUID.randomUUID(), effective_at = "2025-12-31T23:59:59.999Z"),
            correction.copy(claim_id = UUID.randomUUID(), effective_at = "2091-01-01T00:00:00.112Z"),
        )) failure(api.supersede(credential, originalClaim.id, invalid), ApiFailure.Validation, "correction_outside_validity_interval")
        failure(api.supersede(credential, originalClaim.id,
            correction.copy(claim_id = UUID.randomUUID(), valid_to = correction.effective_at)),
            ApiFailure.Validation, "invalid_validity_interval")
        val replacement = success(api.supersede(credential, originalClaim.id, correction))
        assertTrue(success(api.supersede(credential, originalClaim.id, correction)) == replacement)
        failure(api.supersede(credential, originalClaim.id, correction.copy(claim_id = UUID.randomUUID(), value = "Dark Red")),
            ApiFailure.Conflict, "claim_already_superseded")
        val old = success(api.claim(credential, originalClaim.id))
        assertEquals("superseded", old.status)
        assertEquals(replacement.id, old.superseded_by)
        assertEquals(replacement.valid_from, old.valid_to)
        assertEquals(Instant.parse(correction.effective_at).toEpochMilli(), replacement.valid_from)
        assertEquals(listOf(old.id), success(api.claims(credential, scope.id)).map { it.id })
        assertEquals(listOf(old.id), success(api.claims(credential, scope.id, asOf = "2089-12-31T23:59:59.999Z")).map { it.id })
        assertEquals(listOf(replacement.id), success(api.claims(credential, scope.id, asOf = correction.effective_at)).map { it.id })
        assertEquals(setOf(old.id, replacement.id), success(api.claims(credential, scope.id, history = true)).map { it.id }.toSet())
        failure(api.claims(credential, scope.id, history = true, asOf = correction.effective_at),
            ApiFailure.Validation, "history_and_as_of_conflict")
        // The request preserves the original validity bounds, exact quote and evidence mapping.
        val saved = success(api.request(credential, original.request_id))
        assertTrue(saved == original)
        assertTrue(saved.citations.single().valid_to == originalClaim.valid_to)
        assertTrue(saved.citations.single().valid_to != old.valid_to)
        assertTrue(success(api.send(credential, conversation.id, message)) == original)
        assertEquals(2, success(api.events(credential, conversation.id)).size)
        val modelEvent = success(api.events(credential, conversation.id)).single { it.role == "assistant" }
        val modelSource = success(api.source(credential, modelEvent.source_version_id))
        assertEquals("model_generated", modelSource.trust_class)
        failure(api.createClaim(credential, scope.id, ClaimInputDto(UUID.randomUUID(), modelSource.id, 0,
            modelSource.content.codePointCount(0, modelSource.content.length), "Memory HTTP project", "color", "Olive Green")),
            ApiFailure.Validation, "source_not_user_evidence")
    }

    @Test fun aNewAllowedProfileOnlyChangesANewConversationSnapshot() = runBlocking {
        val credential = credential()
        val scope = success(api.createScope(credential, ScopeInputDto("Personality snapshot verification")))
        val baseline = success(api.personalities(credential)).single { it.name == "ADA Test" }
        val existing = success(api.createConversation(credential,
            ConversationInputDto(baseline.id, "Original static style verification", scope.id)))
        val input = PersonalityInputDto("Memory Formal", "formal", "reserved", "detailed")
        val created = success(api.createPersonality(credential, input))
        assertEquals(input.name, created.name)
        assertEquals(input.style, created.style)
        assertEquals(input.warmth, created.warmth)
        assertEquals(input.detail, created.detail)
        val newConversation = success(api.createConversation(credential,
            ConversationInputDto(created.id, "New static style verification", scope.id)))
        assertEquals(PersonalitySnapshotDto(input.name, input.style, input.warmth, input.detail), newConversation.personality)
        val frozen = success(api.conversation(credential, existing.id))
        assertEquals(existing.personality, frozen.personality)
        assertEquals(existing.prompt_version, frozen.prompt_version)
        assertEquals(existing.revision, frozen.revision)
        assertEquals(existing.scope_id, newConversation.scope_id)
        assertTrue(frozen.personality != newConversation.personality)
    }

    @Test fun aCorrectionCanStartExactlyAtTheExistingExclusiveEnd() = runBlocking {
        val credential = credential()
        val scope = success(api.createScope(credential, ScopeInputDto("Correction end boundary verification")))
        val source = success(api.createNote(credential, scope.id, NoteInputDto(UUID.randomUUID(), "Boundary value is Blue.")))
        val original = success(api.createClaim(credential, scope.id, ClaimInputDto(UUID.randomUUID(), source.id, 0,
            source.content.codePointCount(0, source.content.length), "Boundary", "color", "Blue", "fact",
            "2026-01-01T00:00:00.123Z", "2030-01-01T00:00:00.321Z")))
        val evidence = success(api.createNote(credential, scope.id, NoteInputDto(UUID.randomUUID(), "Boundary value becomes Green.")))
        val replacement = success(api.supersede(credential, original.id, SupersedeInputDto(UUID.randomUUID(), evidence.id,
            0, evidence.content.codePointCount(0, evidence.content.length), "Green", "2030-01-01T00:00:00.321Z")))
        assertEquals(original.valid_to, replacement.valid_from)
        assertEquals(replacement.id, success(api.claim(credential, original.id)).superseded_by)
    }
}
