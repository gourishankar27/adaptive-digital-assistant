package dev.ada.assistant.ui

import dev.ada.assistant.data.ProposalDto

/** Only exact loaded annotations/support/time match. This does not approve or hide a review. */
fun proposalReviewGroups(items: List<ProposalDto>): List<List<ProposalDto>> = items.groupBy { proposal ->
    Triple(proposal.scope_id, proposal.status, proposal.candidate.copy(confidence = null,
        support = proposal.candidate.support.sortedWith(compareBy({ it.source_version_id.toString() }, { it.version }, { it.content_hash }, { it.span_start }, { it.span_end }))))
}.values.toList()
