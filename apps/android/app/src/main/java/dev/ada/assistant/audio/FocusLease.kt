package dev.ada.assistant.audio

/** Main-thread generation fence; a callback from an abandoned focus request has no authority. */
internal class FocusLease {
    private var generation = 0L
    private var active = false
    fun begin(): Long { generation++; active = true; return generation }
    fun accepts(key: Long): Boolean = active && generation == key
    fun end() { active = false; generation++ }
}
