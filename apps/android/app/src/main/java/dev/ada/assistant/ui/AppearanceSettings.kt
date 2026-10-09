package dev.ada.assistant.ui

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.core.content.edit

data class AppearanceSettings(val palette: ThemePalette = ThemePalette.OxfordBlue, val dark: Boolean = false)

/** Device-local, non-private appearance only. Never use this store for credentials or ADA data. */
class AppearancePreferences(context: Context) {
    private val preferences = context.applicationContext.getSharedPreferences("appearance", Context.MODE_PRIVATE)

    fun load() = AppearanceSettings(
        palette = ThemePalette.fromPreference(preferences.getString("palette", null)),
        dark = preferences.getBoolean("dark", false),
    )

    fun save(settings: AppearanceSettings) {
        preferences.edit {
            putString("palette", settings.palette.preferenceKey)
            putBoolean("dark", settings.dark)
        }
    }
}

@Composable fun AppearanceSettingsDialog(
    settings: AppearanceSettings,
    change: (AppearanceSettings) -> Unit,
    close: () -> Unit,
) {
    Dialog(onDismissRequest = close) {
        Surface(
            modifier = Modifier.widthIn(max = 560.dp).fillMaxWidth().fillMaxHeight(0.9f),
            shape = MaterialTheme.shapes.large,
            color = MaterialTheme.colorScheme.surface,
        ) {
            Column(
                modifier = Modifier.verticalScroll(rememberScrollState()).padding(AdaSpacing.large),
                verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
            ) {
                Text("Settings", style = MaterialTheme.typography.headlineMedium)
                Text("Appearance", style = MaterialTheme.typography.titleLarge)
                Text("Choose the colors that feel right for you.")
                Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    ThemePalette.entries.forEach { palette ->
                        val selected = settings.palette == palette
                        Surface(
                            color = if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
                            contentColor = if (selected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface,
                            shape = MaterialTheme.shapes.medium,
                        ) {
                            Row(
                                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)
                                    .selectable(selected, role = Role.RadioButton, onClick = { change(settings.copy(palette = palette)) })
                                    .padding(AdaSpacing.medium),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small),
                            ) {
                                RadioButton(selected = selected, onClick = null)
                                Box(Modifier.size(24.dp).background(palette.seed, CircleShape).border(1.dp, MaterialTheme.colorScheme.outline, CircleShape))
                                Column(Modifier.weight(1f)) {
                                    Text(palette.label, style = MaterialTheme.typography.bodyLarge)
                                    if (palette == ThemePalette.OxfordBlue) Text("Default", style = MaterialTheme.typography.bodySmall)
                                }
                            }
                        }
                    }
                }
                Row(
                    modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Text("Dark mode", modifier = Modifier.weight(1f))
                    Switch(settings.dark, { change(settings.copy(dark = it)) }, modifier = Modifier.semantics { contentDescription = "Dark mode" })
                }
                Text("Your choice is saved on this device.", style = MaterialTheme.typography.bodySmall)
                TextButton(onClick = close, modifier = Modifier.align(Alignment.End).heightIn(min = AdaSpacing.touch)) { Text("Done") }
            }
        }
    }
}
