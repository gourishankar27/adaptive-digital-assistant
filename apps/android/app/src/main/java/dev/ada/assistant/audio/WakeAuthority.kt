package dev.ada.assistant.audio

import dev.ada.assistant.data.SessionIdentity
import java.util.UUID

/** Process-local mic authority, separate from shared credential renewal. No private words. */
object WakeAuthority {
    data class Grant(val identity: SessionIdentity, val conversation: UUID, val scope: UUID, val dataEpoch: Long, val expiresAt: Long,
        val persistent:Boolean=false, val sessionId:UUID?=null, val leaseId:UUID=UUID.randomUUID())
    @Volatile private var grant: Grant?=null
    @Volatile var stopped: (() -> Unit)?=null
    @Synchronized fun arm(value: Grant, now: Long=System.currentTimeMillis()) {
        require(value.dataEpoch>=0 && value.expiresAt>now && (value.persistent || value.expiresAt-now<=900_000))
        revoke(); grant=value
    }
    @Synchronized fun current(now: Long=System.currentTimeMillis()): Grant? = grant?.takeIf { it.expiresAt>now }
    @Synchronized fun extend(expected:Grant,replacement:Grant,now:Long=System.currentTimeMillis()):Boolean {
        val live=current(now) ?: return false
        if(live.leaseId!=expected.leaseId || live.leaseId!=replacement.leaseId || live.persistent!=replacement.persistent || live.identity!=replacement.identity || live.dataEpoch!=replacement.dataEpoch || live.conversation!=replacement.conversation || live.scope!=replacement.scope ||
            (live.sessionId!=null && live.sessionId!=replacement.sessionId) || replacement.expiresAt<=now) return false
        grant=replacement; return true
    }
    fun sameLease(expected:Grant)=current()?.let { it.leaseId==expected.leaseId && it.identity==expected.identity && it.dataEpoch==expected.dataEpoch }==true
    @Synchronized fun revoke() { grant=null; stopped?.invoke() }
}
