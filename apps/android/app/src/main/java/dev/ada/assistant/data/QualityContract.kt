@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import kotlinx.serialization.Serializable

@Serializable data class TimeSelectionDto(
    val expression: String, val timezone: String? = null, val reference: String? = null,
    val version: String = "ada-time-window-v1",
)
@Serializable data class TimeResolutionDto(
    val version: String, val state: String, val reason: String, val semantics: String,
    val timezone: String? = null, val reference: Long? = null, val start: Long? = null,
    val end: Long? = null, val local_start: String? = null, val local_end: String? = null,
)
@Serializable data class WindowRetrieveInputDto(val query: String, val selection: TimeSelectionDto, val limit: Int = 8, val budget_bytes: Int = 2200)
@Serializable data class WindowRetrievalDto(
    val version: String, val resolution: TimeResolutionDto, val selected: List<CitationDto> = emptyList(),
    val candidate_pool_truncated: Boolean = false, val candidate_limit: Int = 64,
    val used_bytes: Int = 0, val omitted_groups: Int = 0, val invalid_groups: Int = 0, val guidance: String,
)
