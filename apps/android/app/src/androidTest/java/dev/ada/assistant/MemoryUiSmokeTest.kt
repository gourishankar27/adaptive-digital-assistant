package dev.ada.assistant

import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.assertIsFocused
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertIsSelected
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.performTextReplacement
import androidx.test.espresso.Espresso.closeSoftKeyboard
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import dev.ada.assistant.data.*
import dev.ada.assistant.ui.*
import java.security.MessageDigest
import java.time.Instant
import java.time.OffsetDateTime
import java.util.UUID
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/** Explicit synthetic API/storage fixture; exercises the production VM/controller/Compose path. */
class MemoryUiSmokeTest {
    @get:Rule val compose = createComposeRule()
    private val viewModels = ViewModelStore()
    private val store = UiMemoryStore()
    private val api = UiMemoryApi(store)
    private lateinit var vm: ChatViewModel

    @Before fun authenticatedFixture() {
        compose.runOnIdle {
            vm = ViewModelProvider(viewModels, object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T = ChatViewModel(api, store, false) as T
            })[ChatViewModel::class.java]
        }
        compose.setContent { AdaTheme(ThemePalette.OliveGreen, dark = true) { ChatApp(vm, openSettings = {}) } }
        compose.runOnIdle { vm.connect("https://memory-ui.invalid", "synthetic-only") }
        compose.waitUntil(10_000) { vm.state.value.account != null && !vm.state.value.profiles.loading && !vm.state.value.scopes.loading }
    }

    @After fun discardFixture() {
        if (::vm.isInitialized) compose.runOnIdle { vm.logout(); viewModels.clear() }
    }

    private fun openMemory() {
        compose.onNodeWithTag("nav-memory").performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.scopeId == api.ownedScope.id && !vm.memory.state.value.claims.loading }
    }

    private fun beginRemember() {
        compose.onNodeWithTag("memory-list").performScrollToNode(hasTestTag("memory-remember"))
        compose.onNodeWithTag("memory-remember").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.screen == MemoryScreen.Edit }
    }

    private fun fillAnnotation() {
        compose.onNodeWithTag("memory-subject").performScrollTo().performTextInput("Project")
        compose.onNodeWithTag("memory-predicate").performScrollTo().performTextInput("color")
        compose.onNodeWithTag("memory-value").performScrollTo().performTextInput("Blue")
    }

    @Test fun reviewedUnicodeNoteSecondStepFailureResumesSameIdsWithoutDuplicateNote() {
        openMemory(); beginRemember(); fillAnnotation()
        val exact = "Exact 😀 e\u0301\r\n日本語"
        compose.onNodeWithTag("memory-note").performScrollTo().performTextInput(exact)
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.screen == MemoryScreen.Preview }
        compose.onNodeWithTag("memory-preview-quote").assertTextContains(exact)
        assertTrue(api.notes.isEmpty()); assertTrue(api.claimWrites.isEmpty()); assertNull(store.memory)
        api.failNextClaim = true
        compose.onNodeWithTag("memory-save").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.saving && vm.memory.state.value.pending?.source != null }
        val saved = store.memory!!
        assertEquals(exact, saved.reservation.note?.content)
        assertEquals(1, api.notes.size); assertEquals(1, api.claimWrites.size)
        assertEquals(saved.reservation.note?.source_id, api.notes.single().source_id)
        assertEquals(saved.reservation.claimId, api.claimWrites.single().claim_id)
        compose.onNodeWithTag("memory-resume-pending").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.saving && vm.memory.state.value.pending == null && vm.memory.state.value.detail != null }
        assertEquals(1, api.notes.size)
        assertEquals(2, api.claimWrites.size)
        assertEquals(api.claimWrites.first(), api.claimWrites.last())
        assertEquals(saved.reservation.claimId, vm.memory.state.value.detail?.id)
        assertNull(store.memory)
        compose.onNodeWithTag("memory-detail-quote").performScrollTo().assertTextContains(exact)
        compose.onNodeWithTag("memory-detail-source").performScrollTo().assertTextContains(exact)
    }

    @Test fun exactReadOnlySourceSelectionRejectsModelAndEmptySpanThenKeepsEmojiBoundary() {
        openMemory(); beginRemember(); fillAnnotation()
        compose.onNodeWithTag("memory-choose-source").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.sourceChoices.loading && vm.memory.state.value.sourceChoices.items.size == 2 }
        compose.onNodeWithTag("memory-select-source-${api.modelSource.id}").performScrollTo().assertIsNotEnabled()
        compose.onNodeWithTag("memory-select-source-${api.userSource.id}").performScrollTo().performClick()
        val selected = compose.onNodeWithTag("memory-source-selection")
        selected.performScrollTo().assertTextContains(api.userSource.content)
        assertFalse(selected.fetchSemanticsNode().config.contains(SemanticsActions.SetText))
        selected.performSemanticsAction(SemanticsActions.SetSelection) { action -> assertTrue(action(0, 0, false)) }
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.validation != null }
        compose.onNodeWithTag("memory-error").assertIsFocused()
        assertTrue(api.notes.isEmpty()); assertTrue(api.claimWrites.isEmpty()); assertNull(store.memory)
        selected.performScrollTo().performSemanticsAction(SemanticsActions.SetSelection) { action -> assertTrue(action(0, 2, false)) }
        compose.runOnIdle {
            assertEquals(0, vm.memory.state.value.draft.startUtf16)
            assertEquals(2, vm.memory.state.value.draft.endUtf16)
        }
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.preview != null }
        val preview = vm.memory.state.value.preview!!
        assertNull(preview.reservation.note)
        assertEquals("😀", preview.reservation.evidence?.quote)
        assertEquals(0, preview.reservation.evidence?.span_start)
        assertEquals(1, preview.reservation.evidence?.span_end)
        compose.onNodeWithTag("memory-preview-quote").performScrollTo().assertTextContains("😀")
        compose.onNodeWithTag("memory-save").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.pending == null && vm.memory.state.value.detail != null }
        assertTrue(api.notes.isEmpty())
        assertEquals(1, api.claimWrites.size)
        assertEquals(api.userSource.content, vm.memory.state.value.detailSource?.content)
    }

    @Test fun futureCorrectionPreservesEarlierHistoryAndReplacementLink() {
        val old = api.seedEarlierClaim()
        openMemory()
        compose.onNodeWithTag("memory-list").performScrollToNode(hasTestTag("memory-claim-${old.id}"))
        compose.onNodeWithTag("memory-claim-${old.id}").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.evidenceVerified && !vm.memory.state.value.detailLoading }
        compose.onNodeWithTag("memory-correct").performScrollTo().performClick()
        compose.onNodeWithTag("memory-value").performScrollTo().performTextInput("Green")
        compose.onNodeWithTag("memory-valid-from").performScrollTo().performTextInput("2027-01-01T00:00:00.123Z")
        compose.onNodeWithTag("memory-note").performScrollTo().performTextInput("A future correction 😀")
        compose.onNodeWithTag("memory-preview").performScrollTo().performClick()
        compose.waitUntil(10_000) { vm.memory.state.value.preview != null }
        assertEquals(old.id, vm.memory.state.value.preview?.reservation?.corrects?.id)
        closeSoftKeyboard()
        compose.waitForIdle()
        compose.onNodeWithText("Previous value").performScrollTo()
        assertEquals(0, api.corrections.size)
        compose.onNodeWithTag("memory-save").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.saving && vm.memory.state.value.pending == null && vm.memory.state.value.detail?.value == "Green" }
        val replacement = vm.memory.state.value.detail!!
        assertEquals(Instant.parse("2027-01-01T00:00:00.123Z").toEpochMilli(), replacement.valid_from)
        assertEquals(replacement.id, api.rows[old.id]?.superseded_by)
        assertEquals(replacement.valid_from, api.rows[old.id]?.valid_to)
        compose.onNodeWithTag("memory-back").performScrollTo().performClick()
        compose.onNodeWithTag("memory-list").performScrollToNode(hasTestTag("memory-mode-history"))
        compose.onNodeWithTag("memory-mode-history").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.claims.loading && vm.memory.state.value.claims.items.size == 2 }
        compose.onNodeWithTag("memory-list").performScrollToNode(hasTestTag("memory-claim-${old.id}"))
        compose.onNodeWithTag("memory-claim-${old.id}").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.detailLoading && vm.memory.state.value.detail?.id == old.id }
        compose.onNodeWithTag("memory-detail-quote").performScrollTo().assertTextContains(old.evidence.quote)
        compose.onNodeWithTag("memory-replacement").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.memory.state.value.detailLoading && vm.memory.state.value.detail?.id == replacement.id }
        assertEquals("Green", vm.memory.state.value.detail?.value)
    }

    @Test fun staticEnumProfileCreationChangesOnlyNewConversationSelection() {
        api.fillFirstProfilePage()
        compose.runOnIdle { vm.openConversation(api.savedConversation.id) }
        compose.waitUntil(10_000) { vm.state.value.conversation?.id == api.savedConversation.id && !vm.state.value.events.loading }
        val before = vm.state.value.conversation!!
        compose.onNodeWithTag("nav-settings").performClick()
        compose.onNodeWithTag("settings-styles").performScrollTo().performClick()
        compose.onNodeWithTag("settings-new-profile").performScrollTo().performClick()
        compose.onNodeWithTag("settings-profile-name").performScrollTo().performTextReplacement("Phase7 Formal")
        compose.onNodeWithTag("settings-style-formal").performScrollTo().performClick()
        compose.onNodeWithTag("settings-warmth-reserved").performScrollTo().performClick()
        compose.onNodeWithTag("settings-detail-concise").performScrollTo().performClick()
        compose.onNodeWithTag("settings-create-profile").performScrollTo().performClick()
        compose.waitUntil(10_000) { !vm.state.value.creatingProfile && !vm.state.value.profiles.loading && api.profileWrites.size == 1 }
        assertEquals(PersonalityInputDto("Phase7 Formal", "formal", "reserved", "concise"), api.profileWrites.single())
        assertEquals(before, vm.state.value.conversation)
        val selected = vm.state.value.createProfileId
        assertTrue(vm.state.value.profiles.items.none { it.id == selected })
        assertEquals(50, vm.state.value.profiles.items.size)
        assertEquals(selected, vm.state.value.selectedProfile?.id)
        assertNotEquals(before.personality.name, vm.state.value.selectedProfile?.name)
        closeSoftKeyboard()
        compose.waitUntil(10_000) { compose.onAllNodes(hasTestTag("nav-chat")).fetchSemanticsNodes().size == 1 }
        compose.onNodeWithTag("nav-chat").performClick()
        compose.onNodeWithTag("conversation-list").performScrollToNode(hasTestTag("new-conversation"))
        compose.onNodeWithTag("new-conversation").performScrollTo().performClick()
        assertEquals(selected, vm.state.value.createProfileId)
        compose.onNodeWithTag("profile-$selected").performScrollTo().assertIsSelected()
        assertEquals(before.personality, api.savedConversation.personality)
        assertEquals(before.scope_id, api.savedConversation.scope_id)
        assertEquals(before.prompt_version, api.savedConversation.prompt_version)
    }
}

private class UiMemoryStore : SessionStore {
    var credential: StoredCredential? = null
    var chat: PendingMessage? = null
    var memory: PendingMemory? = null
    override suspend fun readCredential() = credential
    override suspend fun saveCredential(credential: StoredCredential) { this.credential = credential }
    override suspend fun clear() { credential = null; chat = null; memory = null }
    override suspend fun pending(identity: SessionIdentity) = chat?.takeIf { it.identity == identity }
    override suspend fun savePending(message: PendingMessage) { chat = message }
    override suspend fun removePending(identity: SessionIdentity, requestId: UUID) { if (chat?.identity == identity && chat?.body?.request_id == requestId) chat = null }
    override suspend fun memoryPending(identity: SessionIdentity) = memory?.takeIf { it.reservation.identity == identity }
    override suspend fun saveMemoryPending(pending: PendingMemory) { check(memory == null || memory!!.reservation == pending.reservation); memory = pending }
    override suspend fun removeMemoryPending(identity: SessionIdentity, claimId: UUID) { if (memory?.reservation?.identity == identity && memory?.reservation?.claimId == claimId) memory = null }
}

private fun unusedUiMemoryApi(): AdaApi = java.lang.reflect.Proxy.newProxyInstance(AdaApi::class.java.classLoader, arrayOf(AdaApi::class.java)) { _, method, _ ->
    error("Unexpected synthetic UI call: ${method.name}")
} as AdaApi

private class UiMemoryApi(private val store: UiMemoryStore) : AdaApi by unusedUiMemoryApi() {
    val owner = UUID.randomUUID()
    val ownedScope = ScopeDto(UUID.randomUUID(), "Synthetic memory scope", "project", 1000)
    val userSource = source(UUID.randomUUID(), "😀 e\u0301\r\n日本語", "user_explicit")
    val modelSource = source(UUID.randomUUID(), "Synthetic model output", "model_generated")
    val sourceRows = linkedMapOf(userSource.id to userSource, modelSource.id to modelSource)
    val rows = linkedMapOf<UUID, ClaimDto>()
    val notes = mutableListOf<NoteInputDto>()
    val claimWrites = mutableListOf<ClaimInputDto>()
    val corrections = mutableListOf<SupersedeInputDto>()
    val profileWrites = mutableListOf<PersonalityInputDto>()
    var failNextClaim = false
    private val profile = PersonalityDto(UUID.randomUUID(), "Saved ADA", "conversational", "warm", "balanced")
    private val profiles = mutableListOf(profile)
    val savedConversation = ConversationDto(UUID.randomUUID(), "Frozen style", ownedScope.id, "project", PersonalitySnapshotDto(profile.name, profile.style, profile.warmth, profile.detail), "ada-baseline-v3", 1, 1000)
    private val features = CapabilitiesDto("v1", true, false, false, true, "explicit_user_assertions", true, "full_text_and_subject", true, true,
        "ada-baseline-v3", false, true, true, false, false, true, "server", "synthetic", "ui-test")
    override suspend fun me(connection: ConnectionCredential) = ApiResult.Success(MeDto(owner, "Memory UI Test"))
    override suspend fun capabilities(connection: ConnectionCredential) = ApiResult.Success(features)
    override suspend fun personalities(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(profiles.drop(offset).take(limit))
    override suspend fun conversations(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(savedConversation).drop(offset).take(limit))
    override suspend fun conversation(connection: ConnectionCredential, id: UUID): ApiResult<ConversationDto> = if (id == savedConversation.id) ApiResult.Success(savedConversation) else ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun events(connection: ConnectionCredential, id: UUID, limit: Int, offset: Int) = ApiResult.Success(emptyList<EventDto>())
    override suspend fun scopes(connection: ConnectionCredential, limit: Int, offset: Int) = ApiResult.Success(listOf(ownedScope).drop(offset).take(limit))
    override suspend fun scope(connection: ConnectionCredential, id: UUID): ApiResult<ScopeDto> = if (id == ownedScope.id) ApiResult.Success(ownedScope) else ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun sources(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int) = ApiResult.Success(sourceRows.values.filter { it.scope_id == scope }.drop(offset).take(limit))
    override suspend fun source(connection: ConnectionCredential, id: UUID): ApiResult<SourceVersionDto> = sourceRows[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun claims(connection: ConnectionCredential, scope: UUID, limit: Int, offset: Int, history: Boolean, asOf: String?): ApiResult<List<ClaimDto>> {
        check(!(history && asOf != null))
        val at = asOf?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: System.currentTimeMillis()
        return ApiResult.Success(rows.values.filter { it.scope_id == scope && (history || it.valid_from <= at && (it.valid_to == null || at < it.valid_to)) }.drop(offset).take(limit))
    }
    override suspend fun claim(connection: ConnectionCredential, id: UUID): ApiResult<ClaimDto> = rows[id]?.let { ApiResult.Success(it) } ?: ApiResult.Failure(ApiFailure.NotFound)
    override suspend fun createNote(connection: ConnectionCredential, scope: UUID, body: NoteInputDto): ApiResult<SourceVersionDto> {
        check(store.memory?.reservation?.note == body)
        notes += body
        val source = sourceRows.values.firstOrNull { it.source_id == body.source_id } ?: source(body.source_id, body.content, "user_explicit")
        sourceRows[source.id] = source
        return ApiResult.Success(source)
    }
    override suspend fun createClaim(connection: ConnectionCredential, scope: UUID, body: ClaimInputDto): ApiResult<ClaimDto> {
        check(store.memory?.claimInput() == body)
        claimWrites += body
        if (failNextClaim) { failNextClaim = false; return ApiResult.Failure(ApiFailure.Timeout) }
        val pending = store.memory!!
        val claim = fromPending(pending)
        rows[claim.id] = claim
        return ApiResult.Success(claim)
    }
    override suspend fun supersede(connection: ConnectionCredential, id: UUID, body: SupersedeInputDto): ApiResult<ClaimDto> {
        check(store.memory?.correctionInput() == body)
        corrections += body
        val claim = fromPending(store.memory!!)
        val old = rows.getValue(id)
        rows[id] = old.copy(status = "superseded", valid_to = claim.valid_from, superseded_by = claim.id)
        rows[claim.id] = claim
        return ApiResult.Success(claim)
    }
    override suspend fun createPersonality(connection: ConnectionCredential, body: PersonalityInputDto): ApiResult<PersonalityDto> {
        profileWrites += body
        val created = PersonalityDto(UUID.randomUUID(), body.name, body.style, body.warmth, body.detail)
        profiles += created
        return ApiResult.Success(created)
    }
    fun fillFirstProfilePage() {
        repeat(49) { index -> profiles += PersonalityDto(UUID.randomUUID(), "Earlier style $index", "direct", "reserved", "concise") }
    }
    fun seedEarlierClaim(): ClaimDto {
        val oldSource = source(UUID.randomUUID(), "Earlier decision", "user_explicit").copy(created_at = 1000)
        sourceRows[oldSource.id] = oldSource
        val old = ClaimDto(UUID.randomUUID(), ownedScope.id, "Project", "color", "Blue", "decision", "active", 1000, null, null, 1000,
            "user_asserted", exactEvidenceSelection(oldSource, ownedScope.id, 0, oldSource.content.length))
        rows[old.id] = old
        return old
    }
    private fun fromPending(pending: PendingMemory): ClaimDto {
        val r = pending.reservation; val source = pending.source!!
        val evidence = r.evidence ?: exactEvidenceSelection(source, r.scopeId, 0, source.content.length)
        return ClaimDto(r.claimId, r.scopeId, r.subject, r.predicate, r.value, r.kind, "active",
            r.validFrom?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() } ?: source.created_at,
            r.validTo?.let { OffsetDateTime.parse(it).toInstant().toEpochMilli() }, null, source.created_at, "user_asserted", evidence)
    }
    private fun source(sourceId: UUID, content: String, trust: String) = SourceVersionDto(UUID.randomUUID(), sourceId, ownedScope.id, 1, content,
        MessageDigest.getInstance("SHA-256").digest(content.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it.toInt() and 255) }, trust, 1791500000123L)
}
