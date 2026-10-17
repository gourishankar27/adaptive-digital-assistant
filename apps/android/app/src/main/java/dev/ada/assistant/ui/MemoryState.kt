package dev.ada.assistant.ui

import dev.ada.assistant.data.*
import java.util.UUID

enum class MemoryMode { Current, AsOf, History }
enum class MemoryScreen { Browse, Detail, Edit, Preview }
data class MemoryDraft(
    val note: String = "", val subject: String = "", val predicate: String = "",
    val value: String = "", val kind: String = "fact", val validFrom: String = "",
    val validTo: String = "", val selectedSource: SourceVersionDto? = null,
    val startUtf16: Int = 0, val endUtf16: Int = 0, val corrects: ClaimDto? = null,
) {
    override fun toString() = "MemoryDraft(redacted)"
}
data class MemoryState(
    val windowsEnabled: Boolean = false, val windowLoading: Boolean = false,
    val window: WindowRetrievalDto? = null,
    val enabled: Boolean = false, val writesEnabled: Boolean = false, val historicalEnabled: Boolean = false,
    val screen: MemoryScreen = MemoryScreen.Browse,
    val scopes: ChatPage<ScopeDto> = ChatPage(), val scopeId: UUID? = null,
    val mode: MemoryMode = MemoryMode.Current, val asOf: String = "",
    val claims: ChatPage<ClaimDto> = ChatPage(),
    val detail: ClaimDto? = null, val detailSource: SourceVersionDto? = null,
    val detailLoading: Boolean = false, val evidenceVerified: Boolean = false,
    val sourceChoices: ChatPage<SourceVersionDto> = ChatPage(),
    val draft: MemoryDraft = MemoryDraft(), val preview: PendingMemory? = null,
    val pending: PendingMemory? = null, val saving: Boolean = false,
    val fault: ApiFailure? = null, val notice: String? = null, val validation: String? = null,
) {
    override fun toString() = "MemoryState(redacted)"
}

/** A warning about loaded overlapping assertions, never an authority ranking. */
fun competingAssertions(claims: List<ClaimDto>): Set<UUID> = claims
    .groupBy { Triple(it.scope_id, it.subject, it.predicate) }.values.flatMap { slot ->
        if (slot.map { it.value }.distinct().size < 2) emptyList() else slot.filter { a ->
            slot.any { b -> a.id != b.id && a.value != b.value &&
                (a.valid_to == null || b.valid_from < a.valid_to) &&
                (b.valid_to == null || a.valid_from < b.valid_to) }
        }.map { it.id }
    }.toSet()
