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
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.consumeWindowInsets
import androidx.compose.material3.Scaffold
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.Box
import dev.ada.assistant.data.HttpAdaApi
import dev.ada.assistant.data.AndroidSessionStore
import dev.ada.assistant.ui.ChatViewModel
import dev.ada.assistant.ui.ChatApp
import dev.ada.assistant.ui.AdaTheme
import dev.ada.assistant.ui.AppearancePreferences
import dev.ada.assistant.ui.AppearanceSettingsDialog
import androidx.activity.SystemBarStyle
import androidx.compose.ui.platform.LocalFocusManager

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        enableEdgeToEdge()
        val viewModel = ViewModelProvider(this, object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                ChatViewModel(HttpAdaApi(), AndroidSessionStore(applicationContext), BuildConfig.DEBUG)
                    .also { it.restore() } as T
        })[ChatViewModel::class.java]
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
                Scaffold { insets ->
                    Box(Modifier.padding(insets).consumeWindowInsets(insets)) {
                        ChatApp(viewModel) {
                            focus.clearFocus()
                            settingsOpen = true
                        }
                    }
                }
                if (settingsOpen) AppearanceSettingsDialog(appearance, change = {
                    preferences.save(it)
                    appearance = it
                }, close = { settingsOpen = false })
            }
        }
    }
}
