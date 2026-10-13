package dev.ada.assistant

import android.os.Bundle
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.audio.AndroidSpeechCapture
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.VoicePhase
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test

class VoicePlatformAvailabilityTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()
    @Test fun platformAvailabilityIsReportedWithoutStartingTheMicrophone() {
        val native = AndroidSpeechCapture(compose.activity)
        val vm = ViewModelProvider(compose.activity)[ChatViewModel::class.java]
        compose.runOnIdle { assertEquals(VoicePhase.Idle, vm.voice.state.value.phase) }
        InstrumentationRegistry.getInstrumentation().sendStatus(2, Bundle().apply {
            putString("voiceNativeAvailability", native.availability.name)
            putString("voicePlatformVersion", native.version)
        })
        compose.runOnIdle { native.close() }
    }
}
