package dev.ada.assistant

import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.data.ConnectionCredential

/** Injected only by instrumentation; production connection rules remain unchanged. */
internal fun fixtureOrigin(fallbackPort: Int = 18765): String {
    val origin = InstrumentationRegistry.getArguments().getString("adaTestOrigin") ?: "http://10.0.2.2:$fallbackPort"
    val parsed = ConnectionCredential.parse(origin, "synthetic-validation", true)
    require(parsed != null && parsed.server.scheme == "http" && parsed.server.host in setOf("127.0.0.1", "10.0.2.2"))
    return parsed.server.toString()
}
