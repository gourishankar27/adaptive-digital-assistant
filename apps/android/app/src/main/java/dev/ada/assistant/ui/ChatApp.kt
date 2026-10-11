package dev.ada.assistant.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.isImeVisible
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import dev.ada.assistant.data.ApiFailure
import dev.ada.assistant.data.EventDto
import dev.ada.assistant.data.hasAgentTools
import dev.ada.assistant.data.hasEpisodes
import kotlin.math.cos
import kotlin.math.sin

@Composable
@OptIn(ExperimentalLayoutApi::class)
fun ChatApp(vm: ChatViewModel, openSettings: () -> Unit) {
    val state by vm.state.collectAsStateWithLifecycle()
    val focus = LocalFocusManager.current
    val typing = WindowInsets.isImeVisible
    BackHandler(state.account != null && state.destination != ChatDestination.Conversations) { focus.clearFocus(); vm.back() }
    Scaffold(
        modifier = Modifier.fillMaxSize().imePadding(),
        contentWindowInsets = WindowInsets(0, 0, 0, 0), // MainActivity supplies system bar insets.
        topBar = {
            if (!typing) Surface(color = MaterialTheme.colorScheme.surface, tonalElevation = 2.dp) {
                Row(Modifier.fillMaxWidth().padding(horizontal = AdaSpacing.medium), verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f).padding(vertical = AdaSpacing.small)) {
                        Text("ADA", style = MaterialTheme.typography.titleLarge)
                        Text("A little space to think", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    TextButton(
                        onClick = { focus.clearFocus(); if (state.account == null) openSettings() else vm.navigate(ChatDestination.Settings) },
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("top-settings"),
                    ) { Text("Settings") }
                }
            }
        },
        bottomBar = {
            if (state.account != null && !typing) NavigationBar(windowInsets = WindowInsets(0, 0, 0, 0)) {
                val inChat = state.destination !in setOf(ChatDestination.Settings, ChatDestination.Connect, ChatDestination.Memory, ChatDestination.Documents, ChatDestination.Entities, ChatDestination.Proposals)
                NavigationBarItem(
                    selected = inChat,
                    onClick = { focus.clearFocus(); vm.navigate(ChatDestination.Conversations) },
                    icon = { NavigationGlyph(0) }, label = { Text("Chat") },
                    modifier = Modifier.testTag("nav-chat"),
                )
                NavigationBarItem(
                    selected = state.destination in setOf(ChatDestination.Memory, ChatDestination.Entities, ChatDestination.Proposals), enabled = state.capabilities?.structured_memory == true,
                    onClick = { focus.clearFocus(); vm.navigate(ChatDestination.Memory) }, icon = { NavigationGlyph(1) }, label = { Text("Memory") },
                    modifier = Modifier.testTag("nav-memory").semantics { stateDescription = if (state.capabilities?.structured_memory == true) "Owned statements and evidence" else "This server does not offer structured memory" },
                )
                NavigationBarItem(
                    selected = state.destination == ChatDestination.Documents,
                    enabled = state.capabilities?.let { it.document_uploads && it.document_ingestion == "text_markdown_v1" } == true,
                    onClick = { focus.clearFocus(); vm.navigate(ChatDestination.Documents) }, icon = { NavigationGlyph(1) }, label = { Text("Documents") },
                    modifier = Modifier.testTag("nav-documents"),
                )
                NavigationBarItem(
                    selected = state.destination == ChatDestination.Settings,
                    onClick = { focus.clearFocus(); vm.navigate(ChatDestination.Settings) },
                    icon = { NavigationGlyph(2) }, label = { Text("Settings") },
                    modifier = Modifier.testTag("nav-settings"),
                )
            }
        },
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding)) {
            when (state.destination) {
                ChatDestination.Connect -> ChatConnect(state, vm::connect, openSettings)
                ChatDestination.Conversations -> ConversationsScreen(state, vm)
                ChatDestination.NewConversation -> NewConversationScreen(state, vm)
                ChatDestination.Chat -> ConversationScreen(state, vm, typing)
                ChatDestination.Sources -> SourcesScreen(state, vm)
                ChatDestination.Retrieval -> RetrievalScreen(state, vm)
                ChatDestination.Memory -> {
                    if (state.capabilities?.let { it.memory_review && it.memory_proposals == "selected_sources_v1" } == true) TextButton({ vm.navigate(ChatDestination.Proposals) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("open-proposals")) { Text("Review memory suggestions") }
                    if (state.capabilities?.let { it.scoped_entities && it.entity_writes && it.entity_resolution == "explicit_aliases_v1" } == true) TextButton({ vm.navigate(ChatDestination.Entities) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("open-entities")) { Text("People, projects and aliases") }
                    MemoryScreens(vm.memory)
                }
                ChatDestination.Entities -> EntityScreens(vm.entities) { vm.navigate(ChatDestination.Memory) }
                ChatDestination.Proposals -> ProposalScreens(vm.proposals) { vm.navigate(ChatDestination.Memory) }
                ChatDestination.Tools -> AgentScreen(vm.agents, state.conversation, state.account)
                ChatDestination.Episodes -> EpisodeScreen(vm.episodes, state.conversation)
                ChatDestination.Documents -> DocumentScreens(vm.documents)
                ChatDestination.Settings -> AccountSettingsScreen(state, vm, openSettings)
            }
        }
    }
}

@Composable
private fun ChatConnect(state: ChatState, connect: (String, String) -> Unit, openSettings: () -> Unit) {
    var server by remember { mutableStateOf("") }
    var token by remember { mutableStateOf("") } // Never saved in a Bundle or plaintext preferences.
    val focus = LocalFocusManager.current
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.large),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
    ) {
        ScreenHeading("Welcome back.", "Connect to your ADA server. Your account, conversations and sources stay together.")
        OutlinedTextField(
            server, { server = it }, label = { Text("ADA server URL") }, singleLine = true,
            enabled = !state.connecting, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri, imeAction = ImeAction.Next),
            supportingText = { Text("Use verified HTTPS. Debug builds also support listed local development hosts.") },
            modifier = Modifier.fillMaxWidth().testTag("connect-server"),
        )
        OutlinedTextField(
            token, { token = it }, label = { Text("Bearer token") }, singleLine = true,
            enabled = !state.connecting, visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
            keyboardActions = KeyboardActions(onDone = {
                if (!state.connecting && server.isNotBlank() && token.isNotBlank()) { focus.clearFocus(); connect(server, token); token = "" }
            }),
            modifier = Modifier.fillMaxWidth().testTag("connect-token"),
        )
        StateFeedback(state)
        Button(
            onClick = { focus.clearFocus(); connect(server, token); token = "" },
            enabled = !state.connecting && server.isNotBlank() && token.isNotBlank(),
            modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("connect-action"),
        ) { Text(if (state.connecting) "Connecting…" else "Connect") }
        if (state.connecting) BusyIndicator("Checking your account and API compatibility")
        Text("The credential and pending requests are encrypted on this device. Logging out clears private local state.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        TextButton(onClick = openSettings, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Choose your appearance") }
    }
}

@Composable
private fun ConversationsScreen(state: ChatState, vm: ChatViewModel) {
    LazyColumn(
        Modifier.fillMaxSize().testTag("conversation-list"),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
    ) {
        item {
            ScreenHeading("Your conversations", state.account?.let { "Hello, ${it.name}. Pick up a conversation or start with a fresh page." } ?: "Connect to see your conversations.")
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                Button(onClick = vm::beginCreate, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("new-conversation")) { Text("New conversation") }
                TextButton(onClick = vm::refreshConversations, enabled = !state.conversations.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh") }
            }
        }
        item { StateFeedback(state) }
        if (state.pending != null) item {
            StatusCard("A message needs attention", "A reserved message is still pending. Return to its conversation to check the original request.") {
                TextButton(onClick = { vm.openConversation(state.pending.message.conversationId) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Return to pending message") }
            }
        }
        if (state.conversations.items.isEmpty() && !state.conversations.loading && state.fault == null) item {
            StatusCard("A fresh start", "Your conversations will appear here. Choose a style and a private scope when you create one.")
        }
        items(state.conversations.items, key = { it.id }) { conversation ->
            Card(
                onClick = { vm.openConversation(conversation.id) },
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("conversation-${conversation.id}"),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow),
            ) {
                Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text(conversation.title, style = MaterialTheme.typography.titleMedium)
                    val scope = state.scopes.items.firstOrNull { it.id == conversation.scope_id }
                    Text(scope?.name ?: scopeLabel(conversation.scope_kind), style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("${conversation.personality.name} · ${conversation.personality.style}", style = MaterialTheme.typography.labelLarge)
                }
            }
        }
        if (state.conversations.loading) item { BusyIndicator("Loading conversations") }
        if (state.conversations.hasMore && !state.conversations.loading) item {
            OutlinedButton(onClick = vm::loadMoreConversations, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Load more conversations") }
        }
    }
}

@Composable
private fun NewConversationScreen(state: ChatState, vm: ChatViewModel) {
    var addStyle by remember { mutableStateOf(false) }
    var profileName by remember { mutableStateOf("ADA") }
    val focus = LocalFocusManager.current
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.medium).testTag("new-conversation-form"),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
    ) {
        BackButton(vm::back)
        ScreenHeading("A fresh conversation", "Choose how ADA speaks and where this conversation belongs.")
        StateFeedback(state)
        OutlinedTextField(
            state.createTitle, vm::updateCreateTitle, label = { Text("Conversation title") },
            singleLine = true, enabled = !state.creating,
            modifier = Modifier.fillMaxWidth().testTag("new-title"),
        )
        Text("Chat style", style = MaterialTheme.typography.titleMedium)
        Text("Style shapes expression. It never changes ownership or permissions.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        val offPageProfile = state.selectedProfile?.takeIf { saved -> state.profiles.items.none { it.id == saved.id } }
        Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            offPageProfile?.let { profile ->
                ChoiceRow(state.createProfileId == profile.id, profile.name, "Selected for your next conversation · ${profile.style} · ${profile.warmth} · ${profile.detail}", !state.creating,
                    { vm.selectProfile(profile.id) }, Modifier.testTag("profile-${profile.id}"))
            }
            state.profiles.items.forEach { profile ->
                ChoiceRow(
                    selected = state.createProfileId == profile.id,
                    title = profile.name, detail = "${profile.style} · ${profile.warmth} · ${profile.detail}",
                    enabled = !state.creating,
                    select = { vm.selectProfile(profile.id) },
                    modifier = Modifier.testTag("profile-${profile.id}"),
                )
            }
        }
        if (state.profiles.loading) BusyIndicator("Loading your styles")
        if (state.profiles.hasMore && !state.profiles.loading) TextButton(onClick = vm::loadMoreProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more styles") }
        if ((state.profiles.items.isEmpty() && offPageProfile == null) || addStyle) {
            OutlinedTextField(profileName, { profileName = it }, label = { Text("New style name") }, singleLine = true,
                supportingText = { Text("Starts warm, conversational and balanced. Up to 40 characters.") },
                enabled = !state.creatingProfile, modifier = Modifier.fillMaxWidth().testTag("new-profile-name"))
            if (state.profileUncertain) StatusCard("Check whether the style was saved", "The connection ended before creation was confirmed. Refresh styles and inspect the list before creating another.") {
                TextButton(onClick = vm::refreshProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh styles") }
                TextButton(onClick = vm::acknowledgeProfileReview, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("I reviewed the list; allow a new style") }
            }
            Button(
                onClick = { focus.clearFocus(); vm.createProfile(profileName) },
                enabled = !state.creatingProfile && !state.profileUncertain && profileName.isNotBlank() && profileName.codePointCount(0, profileName.length) <= 40,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("create-profile"),
            ) { Text(if (state.creatingProfile) "Creating style…" else "Create chat style") }
        } else TextButton(onClick = { addStyle = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Add a chat style") }
        HorizontalDivider()
        Text("Knowledge scope", style = MaterialTheme.typography.titleMedium)
        Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            ChoiceRow(
                selected = state.createScopeId == null, title = "New personal scope",
                detail = "ADA will create a new private personal scope for this conversation.",
                enabled = !state.creating, select = { vm.selectScope(null) }, modifier = Modifier.testTag("scope-personal"),
            )
            state.scopes.items.forEach { scope ->
                ChoiceRow(
                    selected = state.createScopeId == scope.id, title = scope.name,
                    detail = scopeLabel(scope.kind), enabled = !state.creating, select = { vm.selectScope(scope.id) },
                    modifier = Modifier.testTag("scope-${scope.id}"),
                )
            }
        }
        if (state.scopes.loading) BusyIndicator("Loading your scopes")
        if (state.scopes.hasMore && !state.scopes.loading) TextButton(onClick = vm::loadMoreScopes, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more scopes") }
        if (state.creationUncertain) StatusCard("Creation outcome is uncertain", "The conversation may already exist. Refresh your list and inspect it before creating another.") {
            TextButton(onClick = vm::refreshConversations, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh conversation list") }
            TextButton(onClick = { vm.navigate(ChatDestination.Conversations) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Review conversations") }
            TextButton(onClick = vm::acknowledgeConversationReview, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("I reviewed the list; allow a new conversation") }
        }
        Button(
            onClick = { focus.clearFocus(); vm.createConversation() },
            enabled = !state.creating && !state.creationUncertain && state.createProfileId != null && state.createTitle.isNotBlank() && state.createTitle.codePointCount(0, state.createTitle.length) <= 120,
            modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("create-conversation"),
        ) { Text(if (state.creating) "Creating…" else "Create conversation") }
    }
}

@Composable
private fun ConversationScreen(state: ChatState, vm: ChatViewModel, typing: Boolean) {
    val conversation = state.conversation
    if (conversation == null) {
        Column(Modifier.padding(AdaSpacing.medium)) { StateFeedback(state); BackButton(vm::back); BusyIndicator("Opening your conversation") }
        return
    }
    val list = rememberLazyListState()
    BoxWithConstraints(Modifier.fillMaxSize()) {
      val totalMaxHeight = maxHeight
      val compact = totalMaxHeight < 360.dp
      val hasPending = state.pending?.message?.conversationId == conversation.id
      val headerHeight = (totalMaxHeight * 0.25f).coerceAtMost(200.dp)
      val pendingHeight = (totalMaxHeight * 0.25f).coerceAtMost(170.dp)
      val composerHeight = (totalMaxHeight * (if (compact) 0.45f else 0.40f)).coerceAtMost(280.dp)
      Column(Modifier.fillMaxSize()) {
       if (!typing && (state.capabilities?.hasAgentTools() == true || state.capabilities?.hasEpisodes() == true)) Row(Modifier.fillMaxWidth()) {
         if (state.capabilities?.hasAgentTools() == true) TextButton({ vm.navigate(ChatDestination.Tools) }, modifier = Modifier.weight(1f).heightIn(min = AdaSpacing.touch).testTag("open-tools")) { Text("Read-only tools") }
         if (state.capabilities?.hasEpisodes() == true) TextButton({ vm.navigate(ChatDestination.Episodes) }, modifier = Modifier.weight(1f).heightIn(min = AdaSpacing.touch).testTag("open-episodes")) { Text("History & episodes") }
       }
       if (!typing) {
        if (!compact) {
            ConversationContext(state, vm, headerHeight)
            HorizontalDivider()
        }
        LazyColumn(
            Modifier.weight(1f).fillMaxWidth().testTag("chat-history"), state = list,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium),
            verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
        ) {
            if (compact) item(key = "conversation-context") { ConversationContext(state, vm, 200.dp, scrollWithin = false) }
            if (compact && hasPending) item(key = "request-recovery") { PendingPanel(state, vm, 170.dp, scrollWithin = false) }
            if (state.events.items.isEmpty() && !state.events.loading) item {
                StatusCard("What’s on your mind?", "Your words belong here. ADA will use this conversation’s saved style and chosen scope.")
            }
            items(state.events.items, key = { it.id }) { event ->
                EventCard(event, state, vm)
            }
            if (state.events.loading) item { BusyIndicator("Loading recorded messages") }
            if (state.events.hasMore && !state.events.loading) item {
                OutlinedButton(onClick = vm::loadMoreEvents, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Load more history") }
            }
            state.submittedMessages.values.filter { it.conversationId == conversation.id }.forEach { submitted ->
                val requestId = submitted.body.request_id
                val response = state.sources[requestId]?.takeIf { it.request_id == requestId && it.conversation_id == conversation.id && it.status == "completed" }
                val userMissing = state.events.items.none { it.request_id == requestId && it.role == "user" }
                val replyMissing = state.events.items.none { it.request_id == requestId && it.role == "assistant" }
                if (response != null && (userMissing || replyMissing)) item(key = "submitted-$requestId") {
                    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                        if (userMissing) Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                            Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                                Text("You", style = MaterialTheme.typography.labelLarge)
                                SafeChatText(submitted.body.content)
                            }
                        }
                        if (replyMissing && response.response != null) Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)) {
                            Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                                Text("ADA", style = MaterialTheme.typography.labelLarge)
                                SafeChatText(response.response)
                                val labels = Regex("\\[(M[1-9][0-9]*)]").findAll(response.response).map { it.groupValues[1] }.distinct().toList()
                                labels.forEach { label ->
                                    TextButton(onClick = { vm.openSources(requestId, label) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("source-chip-$label")) { Text("Source [$label]") }
                                }
                                if (labels.isEmpty()) TextButton(onClick = { vm.openSources(requestId) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Sources for this reply") }
                            }
                        }
                    }
                }
            }
        }
        LaunchedEffect(conversation.id, state.events.items.lastOrNull()?.id, state.pending?.phase, compact) {
            val precedingItems = if (compact) 1 + if (hasPending) 1 else 0 else 0
            if (state.events.items.isNotEmpty() && (state.pending != null || state.events.items.size <= 2)) list.animateScrollToItem(state.events.items.lastIndex + precedingItems)
        }
        if (!compact && hasPending) PendingPanel(state, vm, pendingHeight)
       }
        // Keep the same composer/focus state while the IME opens; only its available height changes.
        // Dismissing the keyboard restores context, history and recovery controls.
        Composer(state, vm, if (typing) totalMaxHeight else composerHeight)
      }
    }
}

@Composable
private fun ConversationContext(state: ChatState, vm: ChatViewModel, maximumHeight: Dp, scrollWithin: Boolean = true) {
    val conversation = state.conversation ?: return
    val scope = state.scopes.items.firstOrNull { it.id == conversation.scope_id }
    var contextDetails by remember(conversation.id) { mutableStateOf(false) }
    var confirmUpgrade by remember(conversation.id) { mutableStateOf(false) }
    val scroll = rememberScrollState()
    val scrolling = if (scrollWithin) Modifier.heightIn(max = maximumHeight).verticalScroll(scroll) else Modifier
    Column(Modifier.fillMaxWidth().then(scrolling).padding(horizontal = AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = { vm.navigate(ChatDestination.Conversations) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Conversations") }
            Spacer(Modifier.weight(1f))
            TextButton(onClick = vm::refreshEvents, enabled = !state.events.loading, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh history") }
        }
        Text(conversation.title, style = MaterialTheme.typography.titleLarge, modifier = Modifier.semantics { heading() })
        Text("Scope: ${scope?.name ?: scopeLabel(conversation.scope_kind)}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Saved style: ${conversation.personality.name} · ${conversation.personality.style} · ${conversation.personality.warmth} · ${conversation.personality.detail}", style = MaterialTheme.typography.bodySmall)
        TextButton(onClick = { contextDetails = !contextDetails }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (contextDetails) "Hide conversation details" else "Conversation details") }
        if (contextDetails) SafeChatText("Saved prompt: ${conversation.prompt_version}\nRevision: ${conversation.revision}\nConversation: ${conversation.id}\nScope: ${conversation.scope_id}", links = false)
        if (conversation.prompt_version in setOf("ada-baseline-v1", "ada-baseline-v2", "ada-baseline-v3") &&
            state.capabilities?.chat_prompt_version in setOf("ada-baseline-v3", "ada-baseline-v4") &&
            conversation.prompt_version != state.capabilities?.chat_prompt_version) {
            Text("This conversation has an older saved prompt. Updating changes future replies; past answers stay as recorded.", style = MaterialTheme.typography.bodySmall)
            TextButton(onClick = { confirmUpgrade = true }, enabled = state.pending == null && !state.upgrading, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("prompt-upgrade")) { Text(if (state.upgrading) "Updating prompt…" else "Update saved prompt") }
        }
        StateFeedback(state, suppressFailure = state.pending?.failure != null && state.pending.failure == state.fault)
    }
    if (confirmUpgrade) AlertDialog(
        onDismissRequest = { confirmUpgrade = false }, title = { Text("Update the saved prompt?") },
        text = { Text("Future replies will use the current ADA prompt and retrieval behavior. Existing answers, source cards and the saved style remain unchanged. The server records this explicit upgrade.") },
        confirmButton = { TextButton(onClick = { confirmUpgrade = false; vm.upgradePrompt() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Update prompt") } },
        dismissButton = { TextButton(onClick = { confirmUpgrade = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep saved prompt") } },
    )
}

@Composable
private fun EventCard(event: EventDto, state: ChatState, vm: ChatViewModel) {
    val user = event.role == "user"
    Card(
        Modifier.fillMaxWidth().testTag("event-${event.id}"),
        colors = CardDefaults.cardColors(containerColor = if (user) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerLow),
    ) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text(if (user) "You" else if (event.role == "assistant") "ADA" else "Recorded message", style = MaterialTheme.typography.labelLarge)
            if (event.request_status != "completed") Text(
                when (event.request_status) { "running" -> "Request still running"; "failed" -> "Request did not complete"; else -> "Request status is not recognized" },
                style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            SafeChatText(event.content)
            if (event.role == "assistant") {
                val labels = remember(event.content) { Regex("\\[([MD][1-9][0-9]*)]").findAll(event.content).map { it.groupValues[1] }.distinct().toList() }
                labels.forEach { label ->
                    TextButton(
                        onClick = { vm.openSources(event.request_id, label) },
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("source-chip-$label").semantics { contentDescription = "Open Source [$label] for this reply" },
                    ) { Text("Source [$label]") }
                }
                if (labels.isEmpty()) TextButton(onClick = { vm.openSources(event.request_id) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Sources for this reply") }
                val known = state.sources[event.request_id]
                if (known?.request_id == event.request_id && labels.any { label -> known.citations.none { it.label == label } && known.document_citations.none { it.label == label } }) Text("Some source labels are unavailable for this saved reply.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun PendingPanel(state: ChatState, vm: ChatViewModel, maximumHeight: Dp, scrollWithin: Boolean = true) {
    val pending = state.pending ?: return
    var details by remember(pending.message.body.request_id) { mutableStateOf(false) }
    var confirmNew by remember(pending.message.body.request_id) { mutableStateOf(false) }
    val receivedWithCleanupFailure = pending.phase == PendingPhase.Blocked &&
        pending.response?.status == "completed" && pending.response.response != null &&
        pending.response.request_id == pending.message.body.request_id && pending.response.conversation_id == pending.message.conversationId
    val scroll = rememberScrollState()
    val scrolling = if (scrollWithin) Modifier.heightIn(max = maximumHeight).verticalScroll(scroll) else Modifier
    val title = when (pending.phase) {
        PendingPhase.Journaling -> "Saving your pending message"
        PendingPhase.Submitting -> "Sending your message"
        PendingPhase.Running -> "ADA is working on your reply"
        PendingPhase.Unknown -> "The reply’s outcome is not known yet"
        PendingPhase.Failed -> "This request did not complete"
        PendingPhase.Missing -> "The request was not found"
        PendingPhase.Conflict -> "The saved request needs review"
        PendingPhase.Blocked -> if (receivedWithCleanupFailure) "Reply received; recovery storage needs attention" else "Reconnect before continuing"
    }
    Surface(color = MaterialTheme.colorScheme.surfaceContainerHighest) {
        Column(Modifier.fillMaxWidth().then(scrolling).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text(title, style = MaterialTheme.typography.titleSmall, modifier = Modifier.testTag("pending-status"))
            if (pending.phase in setOf(PendingPhase.Journaling, PendingPhase.Submitting, PendingPhase.Running, PendingPhase.Unknown)) {
                LinearProgressIndicator(Modifier.fillMaxWidth().testTag("pending-progress").semantics {
                    contentDescription = if (pending.phase == PendingPhase.Unknown) "Request outcome unresolved; check the original request" else title
                })
            }
            if (state.events.items.none { it.request_id == pending.message.body.request_id && it.role == "user" }) SafeChatText(pending.message.body.content, links = false)
            Text(
                when (pending.phase) {
                    PendingPhase.Unknown -> "A lost connection or timed-out wait does not mean generation failed. Check the original request ID."
                    PendingPhase.Running, PendingPhase.Submitting -> "You can leave this screen. The server may continue working; another Send will not duplicate this request."
                    PendingPhase.Missing -> "After verifying the same account, you can submit the original ID and exact saved message."
                    PendingPhase.Failed -> "Retry keeps the original message, options and request ID. Editing a draft creates a separate new message."
                    PendingPhase.Conflict -> "Refresh history and check the reserved request before deciding what to do next."
                    PendingPhase.Blocked -> if (receivedWithCleanupFailure) "The reply completed, but encrypted recovery storage could not be cleared. After resolving device storage, Check request safely checks this same ID and tries clearing its journal again." else "This request will not be submitted under another account or server."
                    PendingPhase.Journaling -> "The exact request is saved securely before it is sent."
                },
                style = MaterialTheme.typography.bodySmall,
            )
            pending.failure?.let { FailureNotice(it) }
            when (pending.phase) {
                PendingPhase.Unknown, PendingPhase.Running, PendingPhase.Conflict -> TextButton(onClick = vm::reconcile, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("check-request")) { Text("Check request") }
                PendingPhase.Failed -> Button(onClick = vm::retry, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("retry-request")) { Text("Retry original request") }
                PendingPhase.Missing -> Button(onClick = vm::resubmitSamePayload, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("resubmit-request")) { Text("Submit original request") }
                PendingPhase.Blocked -> if (receivedWithCleanupFailure) TextButton(onClick = vm::reconcile, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("check-request")) { Text("Check request") }
                else -> Unit
            }
            if (pending.phase == PendingPhase.Conflict) TextButton(onClick = vm::refreshEvents, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh history") }
            if (pending.phase in setOf(PendingPhase.Failed, PendingPhase.Missing, PendingPhase.Conflict)) TextButton(onClick = { confirmNew = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("new-message")) { Text("Start a new message") }
            TextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide request details" else "Request details") }
            if (details) SafeChatText("Request: ${pending.message.body.request_id}\nMemory: ${if (pending.message.body.use_memory) "enabled" else "disabled"}\nHistorical instant: ${pending.message.body.as_of ?: "current"}", links = false)
        }
    }
    if (confirmNew) AlertDialog(
        onDismissRequest = { confirmNew = false }, title = { Text("Start a separate message?") },
        text = { Text("The original server request is kept. Your next Send will use a new request ID and the current draft. It will not retry or cancel the original request.") },
        confirmButton = { TextButton(onClick = { confirmNew = false; vm.discardPending() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Use a new request") } },
        dismissButton = { TextButton(onClick = { confirmNew = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep original request") } },
    )
}

@Composable
private fun Composer(state: ChatState, vm: ChatViewModel, maximumHeight: Dp) {
    var advanced by remember { mutableStateOf(false) }
    val focus = LocalFocusManager.current
    val count = state.draft.codePointCount(0, state.draft.length)
    val reserved = state.pending != null
    val canSend = !reserved && state.draft.isNotBlank() && count <= 4000 && state.capabilities?.chat == true
    Surface(color = MaterialTheme.colorScheme.surface, shadowElevation = 2.dp) {
        Column(Modifier.fillMaxWidth().heightIn(max = maximumHeight).verticalScroll(rememberScrollState()).padding(horizontal = AdaSpacing.medium, vertical = AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            if (advanced) {
                if (state.capabilities?.memory_in_chat == true) Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(state.useMemory, vm::updateMemory, enabled = !reserved, modifier = Modifier.semantics { contentDescription = "Use saved memory in this message" })
                    Text("Use saved memory", style = MaterialTheme.typography.bodyMedium)
                }
                if (state.capabilities?.let { it.document_retrieval && it.document_citations } == true) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(state.useDocuments, vm::updateDocuments, enabled = !reserved && state.useMemory && state.conversation?.prompt_version == "ada-baseline-v4",
                            modifier = Modifier.testTag("use-documents").semantics { contentDescription = "Use imported documents in this message" })
                        Text("Use imported documents", style = MaterialTheme.typography.bodyMedium)
                    }
                    if (state.conversation?.prompt_version != "ada-baseline-v4") Text("Explicitly update this conversation’s saved prompt to use imported documents.", style = MaterialTheme.typography.bodySmall)
                    else if (!state.useMemory) Text("Turn on saved memory to use scoped evidence, including imported documents.", style = MaterialTheme.typography.bodySmall)
                }
                if (state.capabilities?.historical_memory_queries == true) OutlinedTextField(
                    state.asOf, vm::updateAsOf, label = { Text("Historical instant (optional)") },
                    supportingText = { Text("ISO 8601 with a timezone, for example 2026-10-08T12:00:00.000Z. Blank uses current memory.") },
                    enabled = !reserved, singleLine = true, modifier = Modifier.fillMaxWidth().testTag("historical-instant"),
                )
                if (reserved) Text("The pending request keeps its original options.", style = MaterialTheme.typography.bodySmall)
            }
            OutlinedTextField(
                state.draft, vm::updateDraft, label = { Text("Message ADA") },
                placeholder = { Text("What’s on your mind?") }, minLines = 1, maxLines = 4,
                isError = count > 4000,
                supportingText = { Text(if (count > 4000) "Shorten this draft to 4,000 Unicode characters. Emoji count once." else "$count / 4,000 characters") },
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Default),
                modifier = Modifier.fillMaxWidth().testTag("composer"),
            )
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                TextButton(onClick = { advanced = !advanced }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("message-options")) { Text(if (advanced) "Hide options" else "Message options") }
                Spacer(Modifier.weight(1f))
                Button(onClick = { focus.clearFocus(); vm.send() }, enabled = canSend, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("send")) { Text("Send") }
            }
        }
    }
}

@Composable
private fun SourcesScreen(state: ChatState, vm: ChatViewModel) {
    val id = state.sourceRequestId
    val request = id?.let { state.sources[it] }?.takeIf { it.request_id == id }
    val cards = request?.citations.orEmpty().filter { state.sourceLabel == null || it.label == state.sourceLabel }
    val documents = request?.document_citations.orEmpty().filter { state.sourceLabel == null || it.label == state.sourceLabel }
    LazyColumn(Modifier.fillMaxSize().testTag("sources-list"), contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item { BackButton(vm::back); ScreenHeading("Sources", "These cards belong to this saved reply, with the original quotes and source versions."); StateFeedback(state) }
        if (state.sourceLoading) item { BusyIndicator("Loading sources for this reply") }
        if (!state.sourceLoading && request != null && cards.isEmpty() && documents.isEmpty()) item {
            StatusCard("Source unavailable", if (state.sourceLabel != null) "This label has no source card for the saved reply. It may refer to an older request without a recorded trace or an unknown label." else "No source cards are attached to this saved reply. Older requests may have no retrieval trace.")
        }
        items(cards, key = { "${it.label}:${it.claim_id}" }) { card -> ChatSourceCard(card, checkNotNull(id)) }
        items(documents, key = { "${it.label}:${it.chunk_id}" }) { card -> DocumentSourceCard(card, checkNotNull(id)) }
        if (!state.sourceLoading && request == null && id != null) item {
            TextButton(onClick = { vm.openSources(id, state.sourceLabel) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Try loading sources again") }
        }
        if (id != null) item {
            OutlinedButton(onClick = vm::loadTrace, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("retrieval-details")) { Text("Retrieval details") }
            Text("Selected context, including uncited material, is shown separately from reply sources.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun RetrievalScreen(state: ChatState, vm: ChatViewModel) {
    val trace = state.trace?.takeIf { it.request_id == state.sourceRequestId }
    LazyColumn(Modifier.fillMaxSize().testTag("retrieval-list"), contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item { BackButton(vm::back); ScreenHeading("Retrieval details", "This is context selected for this request, separate from the source cards attached to the reply."); StateFeedback(state) }
        if (state.traceLoading) item { BusyIndicator("Loading the recorded retrieval details") }
        if (state.traceMissing) item { StatusCard("No recorded retrieval details", "This older request has no retrieval trace. Its saved reply remains the original reply; no context is reconstructed.") }
        if (trace != null) {
            item {
                StatusCard("Recorded context", "Selected claims: ${trace.selected.size}\nSelected document excerpts: ${trace.document_selected.size}\nCandidates considered: ${trace.candidates.size + trace.document_candidates.size}\nRetrieval time: ${trace.retrieval_ms} ms\nEvidence budget: ${trace.budget.memory_used_bytes} / ${trace.budget.memory_limit_bytes} bytes\nPrompt budget: ${trace.budget.prompt_used_bytes ?: "unknown"} / ${trace.budget.prompt_limit_bytes ?: "unknown"} bytes")
            }
            if (trace.selected.isEmpty() && trace.document_selected.isEmpty()) item { Text("No evidence was selected for this request.") }
            items(trace.plan.entity_resolution.filter { it.state == "ambiguous" }, key = { "ambiguity:${it.name}" }) { resolution ->
                Card(Modifier.fillMaxWidth().testTag("retrieval-entity-ambiguity")) {
                    Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                        Text("Ambiguous identity: ${resolution.name ?: "self"}", style = MaterialTheme.typography.titleMedium)
                        Text("This request kept these identities separate. Clarify the intended person or project before using its linked assertions.")
                        resolution.candidates.forEach { candidate -> SafeChatText("${candidate.label} · ${candidate.kind}\n${candidate.id}", links = false) }
                        if (resolution.truncated) Text("More matches existed; linked assertions were withheld.")
                    }
                }
            }
            if (trace.plan.entity_resolution_truncated) item { Text("The recorded identity summary is bounded; additional ambiguous linked assertions were withheld.") }
            items(trace.selected, key = { "${it.label}:${it.claim_id}" }) { card -> ChatSourceCard(card, trace.request_id) }
            items(trace.document_selected, key = { "${it.label}:${it.chunk_id}" }) { card -> DocumentSourceCard(card, trace.request_id) }
        }
        if (!state.traceLoading && !state.traceMissing && trace == null) item { TextButton(onClick = vm::loadTrace, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Try loading retrieval details again") } }
    }
}

@Composable
private fun AccountSettingsScreen(state: ChatState, vm: ChatViewModel, openSettings: () -> Unit) {
    var replacement by remember(state.account?.owner, state.account?.server) { mutableStateOf("") }
    val focus = LocalFocusManager.current
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.large), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        ScreenHeading("Settings", "Your connection and the way ADA looks on this device.")
        StateFeedback(state)
        state.account?.let { account ->
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                    Text("Connected account", style = MaterialTheme.typography.titleMedium)
                    SafeChatText(account.name, links = false)
                    SafeChatText(account.server, links = false)
                }
            }
        }
        OutlinedButton(onClick = openSettings, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("appearance")) { Text("Appearance") }
        Text("Choose Oxford Blue, Dark Red or Olive Green in light or dark mode. Text follows the system font size.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        HorizontalDivider()
        SettingsProfiles(state, vm)
        state.account?.let { account ->
            HorizontalDivider()
            Text("Replace this account’s token", style = MaterialTheme.typography.titleMedium)
            Text("Use a newly issued token for the same account. ADA verifies the owner again before restoring saved recovery state.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            OutlinedTextField(
                replacement, { replacement = it }, label = { Text("Replacement bearer token") },
                singleLine = true, visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
                modifier = Modifier.fillMaxWidth().testTag("replacement-token"),
            )
            OutlinedButton(
                onClick = { val entered = replacement; replacement = ""; focus.clearFocus(); vm.rotateCredential(account.server, entered) },
                enabled = !state.connecting && replacement.isNotBlank(),
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("replace-token"),
            ) { Text("Replace token for this account") }
        }
        Text("Account and server changes clear local conversations, sources, drafts and pending requests. A request already submitted may continue on the server.", style = MaterialTheme.typography.bodyMedium)
        Button(onClick = vm::logout, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("logout")) { Text("Log out / change server") }
        Text("Voice, tools and automatic memory extraction are not available in this version.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun SettingsProfiles(state: ChatState, vm: ChatViewModel) {
    var creating by remember(state.account?.owner, state.account?.server) { mutableStateOf(false) }
    var choosing by remember(state.account?.owner, state.account?.server) { mutableStateOf(false) }
    val profileDraft = state.profileDraft
    val focus = LocalFocusManager.current
    val selected = state.profiles.items.firstOrNull { it.id == state.createProfileId }
        ?: state.selectedProfile?.takeIf { it.id == state.createProfileId }
    Text("Chat styles", style = MaterialTheme.typography.titleMedium)
    Text("Choose an expression style for a new conversation. Existing conversations keep their saved style, prompt and knowledge scope.", style = MaterialTheme.typography.bodyMedium)
    state.conversation?.let { conversation ->
        Text("Saved in ${conversation.title}: ${conversation.personality.name} · ${conversation.personality.style} · ${conversation.personality.warmth} · ${conversation.personality.detail}", style = MaterialTheme.typography.bodySmall)
    }
    Text(selected?.let { "For a new conversation: ${it.name} · ${it.style} · ${it.warmth} · ${it.detail}" } ?: "Choose a style when starting a new conversation.", style = MaterialTheme.typography.bodySmall)
    OutlinedButton(onClick = { choosing = !choosing; if (choosing) vm.refreshProfiles() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-choose-profile")) { Text(if (choosing) "Close style list" else "Choose for a new conversation") }
    if (choosing) {
        Column(Modifier.selectableGroup(), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            state.selectedProfile?.takeIf { saved -> state.profiles.items.none { it.id == saved.id } }?.let { profile ->
                ChoiceRow(state.createProfileId == profile.id, profile.name, "Selected for your next conversation · ${profile.style} · ${profile.warmth} · ${profile.detail}", !state.creatingProfile,
                    { vm.selectProfile(profile.id); choosing = false }, Modifier.testTag("settings-profile-${profile.id}"))
            }
            state.profiles.items.forEach { profile ->
                ChoiceRow(state.createProfileId == profile.id, profile.name, "${profile.style} · ${profile.warmth} · ${profile.detail}", enabled = !state.creatingProfile,
                    select = { vm.selectProfile(profile.id); choosing = false }, modifier = Modifier.testTag("settings-profile-${profile.id}"))
            }
        }
        if (state.profiles.loading) BusyIndicator("Loading owned styles")
        if (state.profiles.hasMore && !state.profiles.loading) TextButton(onClick = vm::loadMoreProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more styles") }
    }
    OutlinedButton(onClick = { creating = !creating }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-new-profile")) { Text(if (creating) "Close new style" else "Create a chat style") }
    if (creating) {
        OutlinedTextField(profileDraft.name, { vm.updateProfileDraft(profileDraft.copy(name = it)) }, label = { Text("Profile name") }, singleLine = true,
            supportingText = { Text("Up to 40 letters, numbers, spaces, underscores, dots or hyphens.") },
            enabled = !state.creatingProfile, modifier = Modifier.fillMaxWidth().testTag("settings-profile-name"))
        Text("Style", style = MaterialTheme.typography.titleSmall)
        Column(Modifier.selectableGroup()) {
            listOf("direct", "conversational", "formal").forEach { choice ->
                ChoiceRow(profileDraft.style == choice, choice.replaceFirstChar(Char::uppercase), "Expression style", !state.creatingProfile,
                    { vm.updateProfileDraft(profileDraft.copy(style = choice)) }, Modifier.testTag("settings-style-$choice"))
            }
        }
        Text("Warmth", style = MaterialTheme.typography.titleSmall)
        Column(Modifier.selectableGroup()) {
            listOf("reserved", "warm").forEach { choice ->
                ChoiceRow(profileDraft.warmth == choice, choice.replaceFirstChar(Char::uppercase), "Expression only; no permissions or learning", !state.creatingProfile,
                    { vm.updateProfileDraft(profileDraft.copy(warmth = choice)) }, Modifier.testTag("settings-warmth-$choice"))
            }
        }
        Text("Detail", style = MaterialTheme.typography.titleSmall)
        Column(Modifier.selectableGroup()) {
            listOf("concise", "balanced", "detailed").forEach { choice ->
                ChoiceRow(profileDraft.detail == choice, choice.replaceFirstChar(Char::uppercase), "Preferred amount of explanation", !state.creatingProfile,
                    { vm.updateProfileDraft(profileDraft.copy(detail = choice)) }, Modifier.testTag("settings-detail-$choice"))
            }
        }
        if (state.profileUncertain) {
            Text("The profile creation outcome is unknown. Refresh and review the owned list before consciously allowing a new creation.", style = MaterialTheme.typography.bodySmall)
            TextButton(onClick = { choosing = true; vm.refreshProfiles() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh and review styles") }
            TextButton(onClick = vm::acknowledgeProfileReview, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-review-profile")) { Text("I reviewed the list; allow a new style") }
        }
        Button(onClick = { focus.clearFocus(); vm.createProfile(profileDraft.name, profileDraft.style, profileDraft.warmth, profileDraft.detail) },
            enabled = !state.creatingProfile && !state.profileUncertain && profileDraft.name.isNotBlank(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-create-profile")) {
            Text(if (state.creatingProfile) "Creating style…" else "Create for new conversations")
        }
    }
}

@Composable
private fun StateFeedback(state: ChatState, suppressFailure: Boolean = false) {
    if (!suppressFailure) state.fault?.let { FailureNotice(it) }
    state.notice?.let { notice ->
        Surface(color = MaterialTheme.colorScheme.secondaryContainer, shape = MaterialTheme.shapes.medium) {
            Text(notice, modifier = Modifier.fillMaxWidth().padding(AdaSpacing.medium).semantics { liveRegion = LiveRegionMode.Polite }, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
private fun FailureNotice(failure: ApiFailure) {
    val focus = remember { FocusRequester() }
    LaunchedEffect(failure) { focus.requestFocus() }
    Surface(color = MaterialTheme.colorScheme.errorContainer, contentColor = MaterialTheme.colorScheme.onErrorContainer, shape = MaterialTheme.shapes.medium) {
        Column(Modifier.fillMaxWidth().padding(AdaSpacing.medium).testTag("failure-notice").focusRequester(focus).focusable().semantics { liveRegion = LiveRegionMode.Polite }, verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text(if (failure is ApiFailure.Busy) "ADA is busy. Wait before trying this action again." else failure.message(), style = MaterialTheme.typography.bodyMedium)
            if (failure is ApiFailure.Busy && failure.retryAfterSeconds != null) Text("Wait at least ${failure.retryAfterSeconds} seconds before retrying.", style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
private fun ScreenHeading(title: String, explanation: String) {
    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text(title, style = MaterialTheme.typography.headlineMedium, modifier = Modifier.semantics { heading() })
        Text(explanation, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun StatusCard(title: String, explanation: String, actions: @Composable () -> Unit = {}) {
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainerLow)) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            Text(explanation, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            actions()
        }
    }
}

@Composable
private fun ChoiceRow(selected: Boolean, title: String, detail: String, enabled: Boolean, select: () -> Unit, modifier: Modifier = Modifier) {
    Surface(color = if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainerLow, shape = MaterialTheme.shapes.medium) {
        Row(modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).selectable(selected, enabled = enabled, role = Role.RadioButton, onClick = select).padding(AdaSpacing.small), verticalAlignment = Alignment.CenterVertically) {
            RadioButton(selected, onClick = null, enabled = enabled)
            Column(Modifier.weight(1f).padding(AdaSpacing.small), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(title, style = MaterialTheme.typography.bodyLarge)
                Text(detail, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
    }
}

@Composable
private fun BackButton(back: () -> Unit) { TextButton(onClick = back, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("screen-back")) { Text("Back") } }

@Composable
private fun BusyIndicator(label: String) {
    Row(Modifier.fillMaxWidth().padding(AdaSpacing.small), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        CircularProgressIndicator(Modifier.size(24.dp).semantics { contentDescription = label }, strokeWidth = 2.dp)
        Text(label, style = MaterialTheme.typography.bodyMedium)
    }
}

private fun scopeLabel(kind: String): String = when (kind) { "personal" -> "Private personal scope"; "project" -> "Private project scope"; else -> "Private scope" }

@Composable
private fun NavigationGlyph(kind: Int) {
    val color = LocalContentColor.current
    Canvas(Modifier.size(24.dp)) {
        val stroke = Stroke(1.7.dp.toPx())
        if (kind == 0) {
            drawRoundRect(color, Offset(3.dp.toPx(), 3.dp.toPx()), Size(18.dp.toPx(), 15.dp.toPx()), CornerRadius(4.dp.toPx()), style = stroke)
            drawLine(color, Offset(8.dp.toPx(), 18.dp.toPx()), Offset(6.dp.toPx(), 22.dp.toPx()), strokeWidth = stroke.width)
            drawLine(color, Offset(6.dp.toPx(), 22.dp.toPx()), Offset(13.dp.toPx(), 18.dp.toPx()), strokeWidth = stroke.width)
        } else if (kind == 1) {
            val path = Path().apply { moveTo(6.dp.toPx(), 3.dp.toPx()); lineTo(18.dp.toPx(), 3.dp.toPx()); lineTo(18.dp.toPx(), 21.dp.toPx()); lineTo(12.dp.toPx(), 17.dp.toPx()); lineTo(6.dp.toPx(), 21.dp.toPx()); close() }
            drawPath(path, color, style = stroke)
        } else {
            drawCircle(color, 6.dp.toPx(), style = stroke)
            drawCircle(color, 2.dp.toPx(), style = stroke)
            repeat(8) { index ->
                val angle = index * Math.PI / 4
                drawLine(color, center + Offset((cos(angle) * 8.dp.toPx()).toFloat(), (sin(angle) * 8.dp.toPx()).toFloat()), center + Offset((cos(angle) * 11.dp.toPx()).toFloat(), (sin(angle) * 11.dp.toPx()).toFloat()), strokeWidth = stroke.width)
            }
        }
    }
}
