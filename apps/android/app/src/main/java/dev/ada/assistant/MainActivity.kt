package dev.ada.assistant

import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.SideEffect
import dev.ada.assistant.data.HttpAdaApi
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.ChatApp
import dev.ada.assistant.ui.AdaTheme
import dev.ada.assistant.ui.AdaAppFrame
import dev.ada.assistant.ui.AppearancePreferences
import dev.ada.assistant.ui.AppearanceSettingsDialog
import androidx.activity.SystemBarStyle
import androidx.compose.ui.platform.LocalFocusManager

class MainActivity : ComponentActivity() {
    private var chatModel: ChatViewModel? = null
    override fun onResume() { super.onResume(); chatModel?.voice?.observeForeground(true) }
    override fun onPause() { chatModel?.voice?.observeForeground(false); super.onPause() }
    override fun onDestroy() { chatModel?.voice?.detachAudio(); super.onDestroy() }
    override fun onStart() { super.onStart(); chatModel?.observeForeground(true) }
    override fun onStop() { chatModel?.voice?.permissionHostStopped(); chatModel?.observeForeground(false); super.onStop() }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        enableEdgeToEdge()
        val viewModel = ViewModelProvider(this, object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                ChatViewModel(HttpAdaApi(), AndroidSessionStore(applicationContext), BuildConfig.DEBUG, voiceClock = android.os.SystemClock::elapsedRealtime)
                    .also { it.restore() } as T
        })[ChatViewModel::class.java]
        chatModel = viewModel
        viewModel.voice.attachAudio(dev.ada.assistant.audio.AndroidSpeechCapture(this), dev.ada.assistant.audio.AndroidSpeechPlayback(this))
        setContent {
            val preferences = remember { AppearancePreferences(applicationContext) }
            var appearance by remember { mutableStateOf(preferences.load()) }
            var settingsOpen by rememberSaveable { mutableStateOf(false) }
            val focus = LocalFocusManager.current
            SideEffect {
                val barStyle = if (appearance.dark) SystemBarStyle.dark(android.graphics.Color.TRANSPARENT)
                    else SystemBarStyle.light(android.graphics.Color.TRANSPARENT, android.graphics.Color.TRANSPARENT)
                enableEdgeToEdge(statusBarStyle = barStyle, navigationBarStyle = barStyle)
            }
            AdaTheme(palette = appearance.palette, dark = appearance.dark) {
                AdaAppFrame {
                        ChatApp(viewModel) {
                            focus.clearFocus()
                            viewModel.voice.observeForeground(false)
                            settingsOpen = true
                        }
                }
                if (settingsOpen) AppearanceSettingsDialog(appearance, change = {
                    preferences.save(it)
                    appearance = it
                }, close = { settingsOpen = false; viewModel.voice.observeForeground(true) })
            }
        }
    }
}
