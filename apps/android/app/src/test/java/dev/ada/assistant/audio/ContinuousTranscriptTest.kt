package dev.ada.assistant.audio

import dev.ada.assistant.data.*
import java.util.UUID
import org.junit.Assert.*
import org.junit.Test

class ContinuousTranscriptTest {
    @Test fun silenceNeverCreatesOrClosesATurnAndRepeatedWordsArePreserved() {
        val session=ContinuousTranscript()
        assertFalse(session.commit("",30000))
        assertTrue(session.commit("yes",31000))
        assertFalse(session.commit("   ",70000))
        assertTrue(session.commit("yes 🫖",100000))
        assertEquals("yes yes 🫖",session.text())
        assertEquals(listOf(0,1),session.segments().map { it.sequence })
        val old=session.segments()
        session.commit("after a long pause",150000)
        assertEquals(old,session.segments().take(2))
        assertTrue(session.segments().all { voiceHash(it.text)==it.sha256 })
    }
    @Test fun capacityFailsBeforeMutatingSavedWords() {
        val session=ContinuousTranscript(); session.commit("a".repeat(LONG_VOICE_TEXT),1000)
        try { session.commit("overflow",2000); fail() } catch (_: IllegalArgumentException) { }
        assertEquals(LONG_VOICE_TEXT,session.text().length)
        assertEquals(1,session.segments().size)
    }
    @Test fun staleAudioReleaseCannotReleaseTheNewCaptureAndWakeCannotPreempt() {
        val old=Any(); val fresh=Any(); var interrupted=false
        assertTrue(VoiceAudioCoordinator.acquire(old,VoiceAudioCoordinator.Use.Wake) { interrupted=true })
        assertTrue(VoiceAudioCoordinator.acquire(fresh,VoiceAudioCoordinator.Use.Capture) {})
        assertTrue(interrupted)
        VoiceAudioCoordinator.release(old)
        assertFalse(VoiceAudioCoordinator.acquire(old,VoiceAudioCoordinator.Use.Wake) {})
        VoiceAudioCoordinator.release(fresh)
        assertTrue(VoiceAudioCoordinator.acquire(old,VoiceAudioCoordinator.Use.Wake) {})
        VoiceAudioCoordinator.release(old)
    }
    @Test fun wakeGrantExpiresAndRevocationNeverCreatesAnotherGrant() {
        WakeAuthority.stopped=null
        val identity=SessionIdentity("https://ada.test/",UUID.randomUUID())
        WakeAuthority.arm(WakeAuthority.Grant(identity,UUID.randomUUID(),UUID.randomUUID(),0,1000),now=100)
        assertNotNull(WakeAuthority.current(999)); assertNull(WakeAuthority.current(1000))
        WakeAuthority.revoke(); assertNull(WakeAuthority.current(100))
    }
}
