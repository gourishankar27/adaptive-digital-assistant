@file:kotlinx.serialization.UseSerializers(UuidSerializer::class)

package dev.ada.assistant.data

import java.util.UUID
import java.time.Instant
import kotlinx.serialization.Serializable

/** The exact user-reviewed input and allocated IDs, bound to a verified account and scope. */
@Serializable
data class MemoryReservation(
    val identity: SessionIdentity,
    val scopeId: UUID,
    val claimId: UUID,
    val note: NoteInputDto? = null,
    val evidence: EvidenceDto? = null,
    val subject: String,
    val predicate: String,
    val value: String,
    val kind: String,
    val validFrom: String? = null,
    val validTo: String? = null,
    val corrects: ClaimDto? = null,
) {
    override fun toString() = "MemoryReservation(redacted)"
}

/** Only the source acknowledgement may advance; the reservation never changes during recovery. */
@Serializable
data class PendingMemory(val reservation: MemoryReservation, val source: SourceVersionDto? = null) {
    override fun toString() = "PendingMemory(redacted)"

    fun claimInput(): ClaimInputDto {
        val evidence = boundEvidence()
        return ClaimInputDto(reservation.claimId, evidence.source_version_id, evidence.span_start, evidence.span_end,
            reservation.subject, reservation.predicate, reservation.value, reservation.kind, reservation.validFrom, reservation.validTo)
    }

    fun correctionInput(): SupersedeInputDto {
        require(reservation.corrects != null) { "No correction reservation" }
        val evidence = boundEvidence()
        return SupersedeInputDto(reservation.claimId, evidence.source_version_id, evidence.span_start, evidence.span_end,
            reservation.value, reservation.validFrom, reservation.validTo)
    }

    private fun boundEvidence(): EvidenceDto {
        validateMemoryPending(this)
        val returned = requireNotNull(source) { "Source acknowledgement required" }
        return reservation.evidence ?: exactEvidenceSelection(returned, reservation.scopeId, 0, returned.content.length)
    }
}

/** Local payload bounds protect recovery storage; ownership is still checked by the server. */
internal fun validateMemoryPending(pending: PendingMemory) {
    try {
        val reservation = pending.reservation
        require((reservation.note == null) != (reservation.evidence == null))
        memoryText(reservation.subject, 160)
        memoryText(reservation.predicate, 160)
        memoryText(reservation.value, 1000)
        require(reservation.kind in setOf("fact", "preference", "decision"))
        reservation.note?.let { memoryText(it.content, 4000) }
        val explicitStart = memoryInstant(reservation.validFrom)
        val end = memoryInstant(reservation.validTo)
        if (explicitStart != null && end != null) require(end > explicitStart)
        val old = reservation.corrects
        if (old != null) {
            require(old.id != reservation.claimId && old.scope_id == reservation.scopeId)
            require(old.subject == reservation.subject && old.predicate == reservation.predicate && old.kind == reservation.kind)
            memoryText(old.value, 1000)
            memoryText(old.evidence.quote, 4000)
            require(old.status in setOf("active", "superseded") && old.origin == "user_asserted")
            require(validMemoryMillis(old.valid_from) && validMemoryMillis(old.created_at))
            old.valid_to?.let { require(validMemoryMillis(it) && it > old.valid_from) }
            explicitStart?.let { require(it > old.valid_from && (old.valid_to == null || it <= old.valid_to)) }
        }
        val source = pending.source
        if (source == null) {
            require(reservation.evidence == null) // Existing evidence always carries its exact returned version.
            return
        }
        require(source.scope_id == reservation.scopeId && source.version >= 1 && validMemoryMillis(source.created_at))
        memoryText(source.content, 4000)
        val selected = reservation.evidence
        if (selected == null) {
            val note = requireNotNull(reservation.note)
            require(source.source_id == note.source_id && source.content == note.content)
            exactEvidenceSelection(source, reservation.scopeId, 0, source.content.length)
        } else {
            memoryText(selected.quote, 4000)
            require(selected.source_version_id == source.id)
            val start = codePointToUtf16Offset(source.content, selected.span_start)
            val finish = codePointToUtf16Offset(source.content, selected.span_end)
            require(exactEvidenceSelection(source, reservation.scopeId, start, finish) == selected)
        }
        // An omitted start/effective_at is bound to the source acknowledgement, not wall-clock time.
        val start = explicitStart ?: source.created_at
        end?.let { require(it > start) }
        old?.let { require(start > it.valid_from && (it.valid_to == null || start <= it.valid_to)) }
    } catch (error: Exception) {
        if (error is kotlinx.coroutines.CancellationException) throw error
        throw SessionStorageException(SessionStoreFailure.InvalidPayload)
    }
}

private fun memoryText(text: String, maxCodePoints: Int) {
    require(text.isNotBlank() && text.codePointCount(0, text.length) in 1..maxCodePoints)
    var index = 0
    while (index < text.length) {
        val char = text[index]
        if (char.isHighSurrogate()) {
            require(index + 1 < text.length && text[index + 1].isLowSurrogate())
            index += 2
        } else {
            require(!char.isLowSurrogate() && char != '\u0000')
            index++
        }
    }
}

private fun memoryInstant(value: String?): Long? = value?.let {
    require(it.isNotBlank())
    Instant.parse(requireNotNull(normalizeUtcMillis(it))).toEpochMilli()
}

private fun validMemoryMillis(value: Long) = value in -62135596800000L..253402300799999L
