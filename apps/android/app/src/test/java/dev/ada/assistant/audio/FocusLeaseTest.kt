package dev.ada.assistant.audio

import org.junit.Assert.*
import org.junit.Test

class FocusLeaseTest {
    @Test fun abandonedCallbacksCannotInterruptAReplacement() {
        val lease = FocusLease()
        val old = lease.begin()
        lease.end()
        assertFalse(lease.accepts(old))
        val current = lease.begin()
        assertFalse(lease.accepts(old))
        assertTrue(lease.accepts(current))
        lease.end()
        assertFalse(lease.accepts(current))
    }
}
