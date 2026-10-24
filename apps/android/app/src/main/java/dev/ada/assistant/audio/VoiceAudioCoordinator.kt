package dev.ada.assistant.audio

/** One process-wide lease. Wake never competes with capture or speech playback. */
object VoiceAudioCoordinator {
    enum class Use { Capture, Playback, Wake }
    private var owner: Any? = null
    private var revoke: (() -> Unit)? = null
    @Synchronized fun acquire(token: Any, next: Use, interrupted: () -> Unit): Boolean {
        if (owner === token) return true
        if (owner != null && next == Use.Wake) return false
        val previous = revoke
        owner = token; revoke = interrupted
        previous?.invoke()
        return owner === token
    }
    @Synchronized fun release(token: Any) { if (owner === token) { owner = null; revoke = null } }
    @Synchronized fun busy() = owner != null
}
