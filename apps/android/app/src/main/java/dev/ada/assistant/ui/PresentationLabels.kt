package dev.ada.assistant.ui

/** Display only; raw protocol values remain intact in contracts and technical details. */
internal fun statusLabel(value: String?): String = when (value) {
    "pending_approval" -> "Waiting for your approval"
    "cancel_requested" -> "Stop requested"
    "not_now", "deferred" -> "Deferred"
    "unconfirmed", "unknown", null -> "Outcome unconfirmed"
    "pending", "queued" -> "Waiting"
    "running", "answering" -> "In progress"
    "completed", "answered", "success", "succeeded", "ok" -> "Completed"
    "failed" -> "Did not complete"
    "interrupted" -> "Interrupted"
    "cancelled" -> "Cancelled"
    "blocked" -> "Blocked"
    "partial" -> "Partially available"
    "ready" -> "Ready"
    "offered" -> "Offered"
    "opened" -> "Opened"
    "expired" -> "Expired"
    "stale" -> "Original context changed"
    "revoked" -> "Revoked"
    "active", "enrolled", "enabled" -> "Enabled"
    "paused" -> "Paused"
    "disabled", "off" -> "Off"
    "accepted", "approved" -> "Approved"
    "rejected", "denied" -> "Declined"
    "superseded" -> "Replaced"
    else -> "Unrecognized status; inspect technical details"
}

internal fun jobLabel(value: String?) = when (value) {
    "episode" -> "conversation summary"
    "proposals" -> "memory suggestions"
    "lexical_rebuild" -> "search index rebuild"
    else -> "job"
}

internal fun preferenceLabel(value: String?) = when (value) {
    null -> "Use inherited value"
    "verbosity" -> "Detail"
    "initiative" -> "Initiative"
    "formality" -> "Formality"
    "humor" -> "Humor"
    "cadence" -> "Pacing"
    "concise" -> "Concise"
    "balanced" -> "Balanced"
    "detailed" -> "Detailed"
    "respond" -> "Respond to my request"
    "suggest" -> "Offer relevant suggestions"
    "casual" -> "Casual"
    "neutral" -> "Neutral"
    "formal" -> "Formal"
    "none" -> "None"
    "light" -> "Light"
    "direct" -> "Direct"
    "stepwise" -> "Step by step"
    "explicit_statement" -> "Explicit statement"
    "repeated_observation" -> "Repeated observations"
    "weak_inference" -> "Tentative interpretation"
    else -> "Unrecognized preference"
}

internal fun toolLabel(value: String) = when (value) {
    "calculator" -> "Calculator"
    "memory_lookup" -> "Saved memory lookup"
    "source_lookup" -> "Original source lookup"
    else -> "Unrecognized tool"
}

internal fun trustLabel(value: String) = when (value) {
    "user_explicit" -> "Explicit user evidence"
    "model_generated", "generated_interpretation" -> "Generated interpretation"
    "tool_output", "tool_result" -> "Tool output; untrusted"
    "untrusted_web" -> "Public web; untrusted"
    "imported_untrusted", "imported" -> "Imported evidence; untrusted"
    else -> "Unrecognized trust; inspect the original source"
}

internal fun voicePhaseLabel(value: VoicePhase): String = when (value) {
    VoicePhase.Permission -> "Waiting for microphone permission"
    VoicePhase.Checking -> "Checking on-device recognition"
    VoicePhase.Recording -> "Recording"
    VoicePhase.Transcribing -> "Preparing transcript"
    else -> "Voice input ready for review"
}
