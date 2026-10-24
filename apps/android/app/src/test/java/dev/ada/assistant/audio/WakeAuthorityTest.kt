package dev.ada.assistant.audio

import dev.ada.assistant.data.SessionIdentity
import java.util.UUID
import org.junit.Assert.*
import org.junit.After
import org.junit.Test

class WakeAuthorityTest {
    private fun grant()=WakeAuthority.Grant(SessionIdentity("https://ada.test/",UUID.randomUUID()),UUID.randomUUID(),UUID.randomUUID(),0,2000,true,UUID.randomUUID())
    @After fun clear() { WakeAuthority.stopped=null; WakeAuthority.revoke() }
    @Test fun extensionPreservesLeaseOwnerScopeEpochAndSessionFamily() {
        val original=grant(); WakeAuthority.arm(original,1000)
        for(changed in listOf(original.copy(leaseId=UUID.randomUUID()),original.copy(conversation=UUID.randomUUID()),original.copy(scope=UUID.randomUUID()),original.copy(dataEpoch=1),original.copy(sessionId=UUID.randomUUID()),original.copy(persistent=false))) {
            assertFalse(WakeAuthority.extend(original,changed.copy(expiresAt=5000),1000))
        }
        assertTrue(WakeAuthority.extend(original,original.copy(expiresAt=5000),1000))
        assertEquals(original.leaseId,WakeAuthority.current(2500)!!.leaseId)
    }
    @Test fun revokedExpiredOrReplacedLeaseCannotBeResurrectedByLateHttp() {
        val original=grant(); WakeAuthority.arm(original,1000); WakeAuthority.revoke()
        assertFalse(WakeAuthority.extend(original,original.copy(expiresAt=5000),1000))
        WakeAuthority.arm(original,1000)
        assertFalse(WakeAuthority.extend(original,original.copy(expiresAt=5000),2001))
        val replacement=grant(); WakeAuthority.arm(replacement,1000)
        assertFalse(WakeAuthority.extend(original,original.copy(expiresAt=5000),1000))
        assertEquals(replacement.leaseId,WakeAuthority.current(1000)!!.leaseId)
    }
}
