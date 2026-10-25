package dev.ada.assistant.ui

import dev.ada.assistant.data.WORK_PROTOCOL
import dev.ada.assistant.data.EDGE_PROTOCOL
import dev.ada.assistant.data.LONG_VOICE_TEXT
import dev.ada.assistant.data.isLong

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.fillMaxHeight
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
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
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
import androidx.compose.runtime.snapshotFlow
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.error
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
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
    val voice by vm.voice.state.collectAsStateWithLifecycle()
    val tools by vm.agents.state.collectAsStateWithLifecycle()
    val presence = adaPresenceState(state, voice, state.destination == ChatDestination.Tools && tools.run?.status == "running")
    val focus = LocalFocusManager.current
    val typing = WindowInsets.isImeVisible
    val keyboard = LocalSoftwareKeyboardController.current
    BackHandler(state.account != null && state.destination != ChatDestination.Conversations) {
        focus.clearFocus()
        if (typing) keyboard?.hide() else vm.back()
    }
    BoxWithConstraints(Modifier.fillMaxSize().imePadding()) {
    val rail = maxWidth >= AdaLayout.railAt && state.account != null && !typing
    Scaffold(
        modifier = Modifier.fillMaxSize(), containerColor = Color.Transparent, contentColor = MaterialTheme.colorScheme.onBackground,
        contentWindowInsets = WindowInsets(0, 0, 0, 0), // MainActivity supplies system bar insets.
        topBar = {
            if (!typing && state.destination == ChatDestination.Chat && state.conversation != null) ConversationToolbar(state, vm)
            else if (!typing) Surface(color = MaterialTheme.colorScheme.background.copy(alpha = .82f)) {
                Row(Modifier.fillMaxWidth().padding(horizontal = AdaSpacing.medium), verticalAlignment = Alignment.CenterVertically) {
                    AdaPresence(presence, Modifier.size(AdaSpacing.touch), motion = presence in setOf(AdaPresenceState.Thinking, AdaPresenceState.Acting), describe = presence != AdaPresenceState.Idle)
                    Column(Modifier.weight(1f).padding(vertical = AdaSpacing.small)) {
                        Text("ADA", style = MaterialTheme.typography.titleLarge)
                        Text(if (state.account == null) "A private space to think" else "Your private workspace", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    AdaIconButton(AdaIcon.Settings, "Settings",
                        onClick = { focus.clearFocus(); if (state.account == null) openSettings() else vm.navigate(ChatDestination.Settings) },
                        modifier = Modifier.testTag("top-settings"))
                }
            }
        },
        bottomBar = {
            if (state.account != null && !typing && !rail) Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                AdaGlassSurface(Modifier.widthIn(max = AdaLayout.reading).padding(horizontal = AdaSpacing.small, vertical = AdaSpacing.small)) {
                    AppNavigation(state, rail = false) { focus.clearFocus(); vm.navigate(it) }
                }
            }
        },
    ) { padding ->
        Row(Modifier.fillMaxSize().padding(padding)) {
            if (rail) AppNavigation(state, rail = true) { focus.clearFocus(); vm.navigate(it) }
            Box(Modifier.weight(1f).fillMaxHeight(), contentAlignment = Alignment.TopCenter) {
            Column(Modifier.widthIn(max = AdaLayout.content).fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally) {
            when (state.destination) {
                ChatDestination.Connect -> ChatConnect(state, vm::connect, vm::disconnect, openSettings, vm::passwordLogin)
                ChatDestination.Conversations -> ConversationsScreen(state, vm)
                ChatDestination.NewConversation -> NewConversationScreen(state, vm)
                ChatDestination.Chat -> ConversationScreen(state, vm, typing)
                ChatDestination.Sources -> SourcesScreen(state, vm)
                ChatDestination.Retrieval -> RetrievalScreen(state, vm)
                ChatDestination.Memory -> {
                    if (state.capabilities?.let { it.memory_review && it.memory_proposals == "selected_sources_v1" } == true) AdaTextButton({ vm.navigate(ChatDestination.Proposals) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("open-proposals")) { Text("Review memory suggestions") }
                    if (state.capabilities?.let { it.scoped_entities && it.entity_writes && it.entity_resolution == "explicit_aliases_v1" } == true) AdaTextButton({ vm.navigate(ChatDestination.Entities) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("open-entities")) { Text("People, projects and aliases") }
                    MemoryScreens(vm.memory)
                }
                ChatDestination.Entities -> EntityScreens(vm.entities) { vm.navigate(ChatDestination.Memory) }
                ChatDestination.Proposals -> ProposalScreens(vm.proposals) { vm.navigate(ChatDestination.Memory) }
                ChatDestination.Research -> ResearchScreen(vm.research, state.conversation)
                ChatDestination.Curiosity -> CuriosityScreen(vm.curiosity, state.conversation, state.profiles.items, vm::openConversation)
                ChatDestination.Work -> WorkScreen(vm.work, vm::openConversation, { vm.navigate(ChatDestination.Schedules) }, { vm.navigate(ChatDestination.Curiosity) })
                ChatDestination.Edge -> EdgeScreen(vm.edge)
                ChatDestination.Reflection -> ReflectionScreen(vm.reflection, state.scopes.items, state.profiles.items, vm::openConversation)
                ChatDestination.Schedules -> ScheduleScreen(vm.scheduling, state.scopes.items, state.profiles.items, vm::openConversation)
                ChatDestination.Tools -> AgentScreen(vm.agents, state.conversation, state.account, state.scopes.items.firstOrNull { it.id == state.conversation?.scope_id }?.name)
                ChatDestination.Episodes -> EpisodeScreen(vm.episodes, state.conversation, state.scopes.items.firstOrNull { it.id == state.conversation?.scope_id }?.name)
                ChatDestination.Documents -> DocumentScreens(vm.documents)
                ChatDestination.Settings -> AccountSettingsScreen(state, vm, openSettings)
            }
            }
            }
        }
    }
    }
}

@Composable
private fun AppNavigation(state: ChatState, rail: Boolean, navigate: (ChatDestination) -> Unit) {
    data class Item(val target: ChatDestination, val label: String, val glyph: Int, val selected: Boolean, val enabled: Boolean, val tag: String)
    val inChat = state.destination !in setOf(ChatDestination.Settings, ChatDestination.Connect, ChatDestination.Memory, ChatDestination.Documents, ChatDestination.Entities, ChatDestination.Proposals)
    val items = listOf(
        Item(ChatDestination.Conversations, "Chat", 0, inChat, true, "nav-chat"),
        Item(ChatDestination.Memory, "Memory", 1, state.destination in setOf(ChatDestination.Memory, ChatDestination.Entities, ChatDestination.Proposals), state.capabilities?.structured_memory == true, "nav-memory"),
        Item(ChatDestination.Documents, "Documents", 3, state.destination == ChatDestination.Documents, state.capabilities?.let { it.document_uploads && it.document_ingestion == "text_markdown_v1" } == true, "nav-documents"),
        Item(ChatDestination.Settings, "Settings", 2, state.destination == ChatDestination.Settings, true, "nav-settings"),
    )
    fun itemModifier(item: Item): Modifier = Modifier.testTag(item.tag).semantics { contentDescription = item.label }.then(if (item.target == ChatDestination.Memory) Modifier.semantics {
        stateDescription = if (item.enabled) "Owned statements and evidence" else "This server does not offer structured memory"
    } else Modifier)
    if (rail) NavigationRail(Modifier.fillMaxHeight().verticalScroll(rememberScrollState()).testTag("expanded-navigation"), containerColor = Color.Transparent) {
        items.forEach { item -> NavigationRailItem(item.selected, { navigate(item.target) }, icon = { NavigationGlyph(item.glyph) }, label = { Text(item.label, maxLines = 1, overflow = TextOverflow.Ellipsis) }, enabled = item.enabled, modifier = itemModifier(item)) }
    } else NavigationBar(containerColor = Color.Transparent, tonalElevation = 0.dp, windowInsets = WindowInsets(0, 0, 0, 0), modifier = Modifier.testTag("compact-navigation")) {
        items.forEach { item -> NavigationBarItem(item.selected, { navigate(item.target) }, icon = { NavigationGlyph(item.glyph) }, label = { Text(if (item.target == ChatDestination.Documents) "Docs" else item.label, maxLines = 1, overflow = TextOverflow.Ellipsis) }, enabled = item.enabled, modifier = itemModifier(item)) }
    }
}

@Composable
private fun ChatConnect(state: ChatState, connect: (String, String) -> Unit, clear: () -> Unit, openSettings: () -> Unit, passwordLogin: (String, String, String) -> Unit) {
    var server by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var legacy by remember { mutableStateOf(false) }
    var token by remember { mutableStateOf("") } // Never saved in a Bundle or plaintext preferences.
    val focus = LocalFocusManager.current
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
    Column(
        Modifier.widthIn(max = AdaLayout.form).fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.large),
        verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
    ) {
        AdaPresenceHeading("Welcome back.", "Your private space for a clearer conversation.", if (state.connecting) AdaPresenceState.Unconfirmed else AdaPresenceState.Idle)
        OutlinedTextField(
            server, { clear(); server = it; token = ""; password = ""; username = "" }, label = { Text("ADA server URL") }, singleLine = true,
            enabled = !state.connecting, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri, imeAction = ImeAction.Next),
            supportingText = { Text("Use verified HTTPS. Debug builds also support listed local development hosts.") },
            modifier = Modifier.fillMaxWidth().testTag("connect-server"),
        )
        ServerAddressPanel(server, change = { clear(); server = it; token = ""; password = ""; username = "" }, enabled = !state.connecting)
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(legacy, { legacy = it; token = ""; password = "" }, modifier = Modifier.testTag("connect-legacy"))
            Text("Advanced: legacy bearer token")
        }
        if (legacy) {
        OutlinedTextField(
            token, { token = it }, label = { Text("Bearer token") }, singleLine = true,
            enabled = !state.connecting, visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
            keyboardActions = KeyboardActions(onDone = {
                if (!state.connecting && server.isNotBlank() && token.isNotBlank()) { focus.clearFocus(); connect(server, token); token = "" }
            }),
            modifier = Modifier.fillMaxWidth().testTag("connect-token"),
        )
        } else {
            OutlinedTextField(username, { username = it }, label = { Text("Username") }, singleLine = true,
                enabled = !state.connecting, modifier = Modifier.fillMaxWidth().testTag("connect-username"))
            OutlinedTextField(password, { password = it }, label = { Text("Password") }, singleLine = true,
                enabled = !state.connecting, visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                modifier = Modifier.fillMaxWidth().testTag("connect-password"))
        }
        StateFeedback(state)
        AdaButton(
            onClick = { focus.clearFocus(); if (legacy) connect(server, token) else passwordLogin(server, username, password); token = ""; password = "" },
            enabled = !state.connecting && server.isNotBlank() && (if (legacy) token.isNotBlank() else username.isNotBlank() && password.isNotEmpty()),
            modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("connect-action"),
        ) { Text(if (state.connecting) "Connecting…" else "Connect") }
        if (state.connecting) BusyIndicator("Checking your account and API compatibility")
        Text("The credential and pending requests are encrypted on this device. Logging out clears private local state.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        AdaTextButton(onClick = openSettings, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Choose your appearance") }
    }
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
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                AdaPresence(adaPresenceState(state), Modifier.size(AdaLayout.presence), motion = false)
                Column(Modifier.weight(1f)) {
                    Text("Your conversations", style = MaterialTheme.typography.headlineSmall, modifier = Modifier.semantics { heading() })
                    Text(state.account?.let { "Hello, ${it.name}." } ?: "Connect to begin.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                AdaIconButton(AdaIcon.Refresh, "Refresh conversations", vm::refreshConversations, enabled = !state.conversations.loading)
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                AdaButton(onClick = vm::beginCreate, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("new-conversation")) {
                    AdaIconGlyph(AdaIcon.Add)
                    Text("New conversation", Modifier.padding(start = AdaSpacing.small))
                }
            }
        }
        item { StateFeedback(state) }
        if (state.pending != null) item {
            StatusCard("A message needs attention", "A reserved message is still pending. Return to its conversation to check the original request.") {
                AdaTextButton(onClick = { vm.openConversation(state.pending.message.conversationId) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Return to pending message") }
            }
        }
        if (state.conversations.items.isEmpty() && !state.conversations.loading && state.fault == null) item {
            StatusCard("A fresh start", "Your conversations will appear here. Choose a style and a private scope when you create one.")
        }
        items(state.conversations.items, key = { it.id }) { conversation ->
            Card(
                onClick = { vm.openConversation(conversation.id) },
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("conversation-${conversation.id}").semantics { role = Role.Button },
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
            AdaOutlinedButton(onClick = vm::loadMoreConversations, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Load more conversations") }
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
        Text("Style shapes expression. It never changes ownership or permissions.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
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
        if (state.profiles.hasMore && !state.profiles.loading) AdaTextButton(onClick = vm::loadMoreProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more styles") }
        if ((state.profiles.items.isEmpty() && offPageProfile == null) || addStyle) {
            OutlinedTextField(profileName, { profileName = it }, label = { Text("New style name") }, singleLine = true,
                supportingText = { Text("Starts warm, conversational and balanced. Up to 40 characters.") },
                enabled = !state.creatingProfile, modifier = Modifier.fillMaxWidth().testTag("new-profile-name"))
            if (state.profileUncertain) StatusCard("Check whether the style was saved", "The connection ended before creation was confirmed. Refresh styles and inspect the list before creating another.") {
                AdaTextButton(onClick = vm::refreshProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh styles") }
                AdaTextButton(onClick = vm::acknowledgeProfileReview, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("I reviewed the list; allow a new style") }
            }
            AdaButton(
                onClick = { focus.clearFocus(); vm.createProfile(profileName) },
                enabled = !state.creatingProfile && !state.profileUncertain && profileName.isNotBlank() && profileName.codePointCount(0, profileName.length) <= 40,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("create-profile"),
            ) { Text(if (state.creatingProfile) "Creating style…" else "Create chat style") }
        } else AdaTextButton(onClick = { addStyle = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Add a chat style") }
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
        if (state.scopes.hasMore && !state.scopes.loading) AdaTextButton(onClick = vm::loadMoreScopes, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more scopes") }
        if (state.creationUncertain) StatusCard("Creation outcome is uncertain", "The conversation may already exist. Refresh your list and inspect it before creating another.") {
            AdaTextButton(onClick = vm::refreshConversations, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh conversation list") }
            AdaTextButton(onClick = { vm.navigate(ChatDestination.Conversations) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Review conversations") }
            AdaTextButton(onClick = vm::acknowledgeConversationReview, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("I reviewed the list; allow a new conversation") }
        }
        AdaButton(
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
    val scope = rememberCoroutineScope()
    var followLatest by remember(conversation.id) { mutableStateOf(true) }
    var autoScrolling by remember(conversation.id) { mutableStateOf(false) }
    LaunchedEffect(conversation.id) {
        snapshotFlow { Triple(list.firstVisibleItemIndex, list.firstVisibleItemScrollOffset, list.isScrollInProgress) }.collect {
            if (list.isScrollInProgress && !autoScrolling) followLatest = !list.canScrollForward
        }
    }
    BoxWithConstraints(Modifier.widthIn(max = AdaLayout.reading).fillMaxSize()) {
      val totalMaxHeight = maxHeight
      val hasPending = state.pending?.message?.conversationId == conversation.id
      Column(Modifier.fillMaxSize()) {
        LazyColumn(
            Modifier.weight(1f).fillMaxWidth().testTag("chat-history"), state = list,
            contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium),
            verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium),
        ) {
            item(key = "conversation-feedback") { StateFeedback(state, suppressFailure = state.pending?.failure != null && state.pending.failure == state.fault) }
            if (state.events.items.isEmpty() && !state.events.loading) item {
                AdaPresenceHeading("What’s on your mind?", "This conversation uses your saved style and chosen scope.", compact = true)
            }
            items(state.events.items, key = { it.id }) { event ->
                EventCard(event, state, vm)
                if (event.role == "assistant") CuriosityChatCard(vm.curiosity, request = event.request_id)
            }
            item { CuriosityChatCard(vm.curiosity, conversation = conversation.id) }
            if (state.events.loading) item { BusyIndicator("Loading recorded messages") }
            if (state.events.hasMore && !state.events.loading) item {
                AdaOutlinedButton(onClick = vm::loadMoreEvents, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Load more history") }
            }
            state.submittedMessages.values.filter { it.conversationId == conversation.id }.forEach { submitted ->
                val requestId = submitted.body.request_id
                val response = state.sources[requestId]?.takeIf { it.request_id == requestId && it.conversation_id == conversation.id && it.status == "completed" }
                val userMissing = state.events.items.none { it.request_id == requestId && it.role == "user" }
                val replyMissing = state.events.items.none { it.request_id == requestId && it.role == "assistant" }
                if (response != null && (userMissing || replyMissing)) item(key = "submitted-$requestId") {
                    Column(verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
                        if (userMissing) AdaMessageSurface(true) {
                            Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                                Text("You", style = MaterialTheme.typography.labelLarge)
                                SafeChatText(submitted.body.content)
                            }
                        }
                        if (replyMissing && response.response != null) AdaMessageSurface(false) {
                            Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
                                Text("ADA", style = MaterialTheme.typography.labelLarge)
                                SafeChatText(response.response)
                                ReadReplyButton(vm, requestId)
                                val labels = Regex("\\[([MDC][1-9][0-9]*)]").findAll(response.response).map { it.groupValues[1] }.distinct().toList()
                                labels.forEach { label ->
                                    AdaTextButton(onClick = { vm.openSources(requestId, label) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("source-chip-$label")) { Text("Source [$label]") }
                                }
                                if (labels.isEmpty()) AdaTextButton(onClick = { vm.openSources(requestId) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Sources for this reply") }
                            }
                        }
                    }
                }
            }
            if (hasPending) item(key = "request-recovery") { PendingPanel(state, vm, AdaLayout.pendingMax, scrollWithin = false) }
        }
        LaunchedEffect(conversation.id, state.events.items.lastOrNull()?.id, state.pending?.phase) {
            // Follow new messages/status transitions, not every streamed token or a reader's scroll.
            if (followLatest && (state.events.items.isNotEmpty() || hasPending)) {
                autoScrolling = true
                try { list.animateScrollToItem((list.layoutInfo.totalItemsCount - 1).coerceAtLeast(0)) }
                finally { autoScrolling = false }
            }
        }
        if (!followLatest) AdaTextButton({
            followLatest = true
            scope.launch {
                autoScrolling = true
                try { list.animateScrollToItem((list.layoutInfo.totalItemsCount - 1).coerceAtLeast(0)) }
                finally { autoScrolling = false }
            }
        }, Modifier.align(Alignment.End).heightIn(min = AdaSpacing.touch).testTag("jump-latest")) { Text("Latest message") }
        // Same composer stays composed while IME opens; thread uses the remaining window.
        Composer(state, vm, if (typing) totalMaxHeight else (totalMaxHeight * AdaLayout.composerFraction).coerceAtMost(AdaLayout.composerMax))
      }
    }
}

@Composable
private fun ConversationToolbar(state: ChatState, vm: ChatViewModel) {
    val conversation = state.conversation ?: return
    var menu by remember(conversation.id) { mutableStateOf(false) }
    var details by remember(conversation.id) { mutableStateOf(false) }
    Surface(color = MaterialTheme.colorScheme.background.copy(alpha = .82f)) {
        Row(Modifier.fillMaxWidth().padding(horizontal = AdaSpacing.small), verticalAlignment = Alignment.CenterVertically) {
            AdaIconButton(AdaIcon.Back, "Conversations", { vm.navigate(ChatDestination.Conversations) })
            Column(Modifier.weight(1f).padding(horizontal = AdaSpacing.small, vertical = AdaSpacing.small)) {
                Text(conversation.title, style = MaterialTheme.typography.titleMedium, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.semantics { heading() })
                Text("${conversation.personality.name} · ${conversation.personality.style}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
            Box {
                AdaIconButton(AdaIcon.More, "Conversation menu", { menu = true }, Modifier.testTag("chat-menu").semantics { stateDescription = if (menu) "Expanded" else "Collapsed" })
                DropdownMenu(menu, { menu = false }) {
                    DropdownMenuItem(text = { Text("Conversation details") }, leadingIcon = { AdaIconGlyph(AdaIcon.Sources) },
                        onClick = { menu = false; details = true }, modifier = Modifier.testTag("conversation-details"))
                    DropdownMenuItem(text = { Text("Refresh history") }, leadingIcon = { AdaIconGlyph(AdaIcon.Refresh) },
                        enabled = !state.events.loading, onClick = { menu = false; vm.refreshEvents() })
                    if (state.capabilities?.web_research == "ada-web-research-v1") DropdownMenuItem(text = { Text("Public research") }, onClick = { menu = false; vm.navigate(ChatDestination.Research) }, modifier = Modifier.testTag("open-research"))
                    if (state.capabilities?.curiosity_protocol == "ada-curiosity-v1") DropdownMenuItem(text = { Text("Questions & curiosity") }, onClick = { menu = false; vm.navigate(ChatDestination.Curiosity) }, modifier = Modifier.testTag("open-curiosity"))
                    if (state.capabilities?.work_protocol == WORK_PROTOCOL) DropdownMenuItem(text = { Text("Projects & next actions") }, onClick = { menu = false; vm.navigate(ChatDestination.Work) }, modifier = Modifier.testTag("open-work"))
                    if (state.capabilities?.reflection_protocol == "ada-reflection-v1") DropdownMenuItem(text = { Text("While you were away") }, onClick = { menu = false; vm.navigate(ChatDestination.Reflection) }, modifier = Modifier.testTag("open-reflection"))
                    if (state.capabilities?.scheduling_protocol == "ada-scheduling-v1") DropdownMenuItem(text = { Text("Reminders & inbox") }, onClick = { menu = false; vm.navigate(ChatDestination.Schedules) }, modifier = Modifier.testTag("open-schedules"))
                    if (state.capabilities?.hasAgentTools() == true) DropdownMenuItem(text = { Text("Read-only tools") }, onClick = { menu = false; vm.navigate(ChatDestination.Tools) }, modifier = Modifier.testTag("open-tools"))
                    if (state.capabilities?.hasEpisodes() == true) DropdownMenuItem(text = { Text("History & episodes") }, onClick = { menu = false; vm.navigate(ChatDestination.Episodes) }, modifier = Modifier.testTag("open-episodes"))
                    DropdownMenuItem(text = { Text("Settings") }, leadingIcon = { AdaIconGlyph(AdaIcon.Settings) }, onClick = { menu = false; vm.navigate(ChatDestination.Settings) })
                }
            }
        }
    }
    if (details) CompactChatDialog("Conversation details", "conversation-details-dialog", "conversation-details-done", { details = false }) {
        ConversationContext(state, vm, AdaLayout.dialogMax, scrollWithin = false)
    }
}

@Composable
private fun CompactChatDialog(title: String, tag: String, doneTag: String, close: () -> Unit, content: @Composable () -> Unit) {
    Dialog(onDismissRequest = close, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        BoxWithConstraints(Modifier.fillMaxWidth().imePadding()) {
        AdaGlassSurface(Modifier.padding(AdaSpacing.medium).widthIn(max = AdaLayout.form).fillMaxWidth().testTag(tag)) {
            Column(Modifier.heightIn(max = (maxHeight - AdaSpacing.section).coerceAtLeast(AdaSpacing.touch).coerceAtMost(AdaLayout.dialogMax))) {
                Row(Modifier.fillMaxWidth().padding(start = AdaSpacing.medium, end = AdaSpacing.tiny), verticalAlignment = Alignment.CenterVertically) {
                    Text(title, style = MaterialTheme.typography.titleMedium, modifier = Modifier.weight(1f).semantics { heading() })
                    AdaIconButton(AdaIcon.Close, "Done", close, Modifier.testTag(doneTag))
                }
                Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) { content() }
            }
        }
    }
    }
}

@Composable
private fun ConversationContext(state: ChatState, vm: ChatViewModel, maximumHeight: Dp, scrollWithin: Boolean = true) {
    val conversation = state.conversation ?: return
    val scope = state.scopes.items.firstOrNull { it.id == conversation.scope_id }
    var contextDetails by remember(conversation.id) { mutableStateOf(false) }
    var confirmUpgrade by remember(conversation.id) { mutableStateOf(false) }
    var confirmQuality by remember(conversation.id) { mutableStateOf(false) }
    val scroll = rememberScrollState()
    val scrolling = if (scrollWithin) Modifier.heightIn(max = maximumHeight).verticalScroll(scroll) else Modifier
    Column(Modifier.fillMaxWidth().then(scrolling).padding(horizontal = AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
        Text(conversation.title, style = MaterialTheme.typography.titleLarge, modifier = Modifier.semantics { heading() })
        Text("Scope: ${scope?.name ?: scopeLabel(conversation.scope_kind)}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Saved style: ${conversation.personality.name} · ${conversation.personality.style} · ${conversation.personality.warmth} · ${conversation.personality.detail}", style = MaterialTheme.typography.bodySmall)
        AdaTextButton(onClick = { contextDetails = !contextDetails }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (contextDetails) "Hide conversation details" else "Conversation details") }
        if (contextDetails) SafeChatText("Saved prompt: ${conversation.prompt_version}\nRevision: ${conversation.revision}\nConversation: ${conversation.id}\nScope: ${conversation.scope_id}", links = false)
        if (conversation.prompt_version in setOf("ada-baseline-v1", "ada-baseline-v2", "ada-baseline-v3") &&
            state.capabilities?.chat_prompt_version in setOf("ada-baseline-v3", "ada-baseline-v4") &&
            conversation.prompt_version != state.capabilities?.chat_prompt_version) {
            Text("This conversation has an older saved prompt. Updating changes future replies; past answers stay as recorded.", style = MaterialTheme.typography.bodyMedium)
            AdaTextButton(onClick = { confirmUpgrade = true }, enabled = state.pending == null && !state.upgrading, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("prompt-upgrade")) { Text(if (state.upgrading) "Updating prompt…" else "Update saved prompt") }
        }
        StateFeedback(state, suppressFailure = state.pending?.failure != null && state.pending.failure == state.fault)
        if (state.capabilities?.quality_prompt_version == "ada-baseline-v5" && conversation.prompt_version in setOf("ada-baseline-v1", "ada-baseline-v2", "ada-baseline-v3", "ada-baseline-v4")) {
            AdaTextButton({ confirmQuality = true }, enabled = state.pending == null && !state.upgrading,
                modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("quality-prompt-upgrade")) { Text("Review context upgrade") }
        }
    }
    if (confirmQuality) AlertDialog(
        onDismissRequest = { confirmQuality = false }, title = { Text("Use the v5 context policy?") },
        text = { Text("This explicitly changes future replies: relevant original excerpts and complete chat pairs are ranked within bounded searches. Missing context stays uncertain. Nothing is automatically saved to memory. Past answers and source snapshots stay as recorded; the server audits this change.") },
        confirmButton = { AdaTextButton({ confirmQuality = false; vm.upgradePrompt(quality = true) }) { Text("Enable for future replies") } },
        dismissButton = { AdaTextButton({ confirmQuality = false }) { Text("Keep saved prompt") } },
    )
    if (confirmUpgrade) AlertDialog(
        onDismissRequest = { confirmUpgrade = false }, title = { Text("Update the saved prompt?") },
        text = { Text("Future replies will use the current ADA prompt and retrieval behavior. Existing answers, source cards and the saved style remain unchanged. The server records this explicit upgrade.") },
        confirmButton = { AdaTextButton(onClick = { confirmUpgrade = false; vm.upgradePrompt() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Update prompt") } },
        dismissButton = { AdaTextButton(onClick = { confirmUpgrade = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep saved prompt") } },
    )
}

@Composable
private fun EventCard(event: EventDto, state: ChatState, vm: ChatViewModel) {
    val user = event.role == "user"
    AdaMessageSurface(user, Modifier.testTag("event-${event.id}")) {
        Column(Modifier.padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(if (user) "You" else if (event.role == "assistant") "ADA" else "Recorded message", style = MaterialTheme.typography.labelLarge, modifier = Modifier.weight(1f))
                if (user) AdaIconButton(AdaIcon.Sources, "Input and reply sources", { vm.openSources(event.request_id) })
            }
            if (event.request_status != "completed") Text(
                when (event.request_status) { "running" -> "Request still running"; "failed" -> "Request did not complete"; else -> "Request status is not recognized" },
                style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            SafeChatText(event.content)
            if (event.role == "assistant" && event.request_status == "completed" && state.capabilities?.work_protocol == WORK_PROTOCOL) AdaTextButton({ vm.saveNextAction(event) }, modifier = Modifier.testTag("save-next-action-${event.request_id}")) { Text("Save next action") }
            if (event.role == "assistant" && event.request_status == "completed") ReadReplyButton(vm, event.request_id)
            if (event.role == "assistant") {
                val labels = remember(event.content) { Regex("\\[([MDC][1-9][0-9]*)]").findAll(event.content).map { it.groupValues[1] }.distinct().toList() }
                labels.forEach { label ->
                    AdaTextButton(
                        onClick = { vm.openSources(event.request_id, label) },
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("source-chip-$label").semantics { contentDescription = "Open Source [$label] for this reply" },
                    ) { Text("Source [$label]") }
                }
                if (labels.isEmpty()) AdaTextButton(onClick = { vm.openSources(event.request_id) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Sources for this reply") }
                val known = state.sources[event.request_id]
                if (known?.request_id == event.request_id && labels.any { label -> known.citations.none { it.label == label } && known.document_citations.none { it.label == label } && known.continuity_citations.none { it.label == label } }) Text("Some source labels are unavailable for this saved reply.", style = MaterialTheme.typography.bodyMedium)
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
    AdaGlassSurface(Modifier.padding(horizontal = AdaSpacing.small, vertical = AdaSpacing.tiny)) {
        Column(Modifier.fillMaxWidth().then(scrolling).padding(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.small)) {
            if (pending.message.voiceTranscript != null) Text("Reviewed voice input · original transcript retained separately")
            Text(title, style = MaterialTheme.typography.titleSmall, modifier = Modifier.testTag("pending-status"))
            state.stream?.takeIf { it.request_id == pending.message.body.request_id }?.let { progress ->
                if (progress.provisional.isNotEmpty()) {
                    Text(if (progress.stream_state in setOf("cancelled", "failed", "interrupted")) "Incomplete reply" else "Provisional reply", style = MaterialTheme.typography.labelLarge)
                    SafeChatText(progress.provisional, links = false)
                }
                if (progress.stream_state in setOf("running", "cancel_requested") && progress.available) {
                    Text(if (state.stopping || progress.stream_state == "cancel_requested") "Stop requested; waiting for shutdown" else if (state.streamConnected) "Receiving reply" else "Observer detached; Check request to reconnect")
                    AdaButton(onClick = vm::stopGeneration, enabled = progress.stream_state == "running" && !state.stopping,
                        modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("thread-stop-generation")) { Text("Stop") }
                }
            }
            if (pending.phase in setOf(PendingPhase.Journaling, PendingPhase.Submitting, PendingPhase.Running, PendingPhase.Unknown)) {
                LinearProgressIndicator(Modifier.fillMaxWidth().testTag("pending-progress").semantics {
                    contentDescription = if (pending.phase == PendingPhase.Unknown) "Request outcome unresolved; check the original request" else title
                })
            }
            if (state.events.items.none { it.request_id == pending.message.body.request_id && it.role == "user" }) SafeChatText(pending.message.body.content, links = false)
            if (details || pending.phase !in setOf(PendingPhase.Journaling, PendingPhase.Submitting, PendingPhase.Running)) Text(
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
                PendingPhase.Unknown, PendingPhase.Running, PendingPhase.Conflict -> AdaTextButton(onClick = vm::reconcile, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("check-request")) { Text("Check request") }
                PendingPhase.Failed -> AdaButton(onClick = vm::retry, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("retry-request")) { Text("Retry original request") }
                PendingPhase.Missing -> AdaButton(onClick = vm::resubmitSamePayload, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("resubmit-request")) { Text("Submit original request") }
                PendingPhase.Blocked -> if (receivedWithCleanupFailure) AdaTextButton(onClick = vm::reconcile, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("check-request")) { Text("Check request") }
                else -> Unit
            }
            if (pending.phase == PendingPhase.Conflict) AdaTextButton(onClick = vm::refreshEvents, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh history") }
            if (pending.phase in setOf(PendingPhase.Failed, PendingPhase.Missing, PendingPhase.Conflict)) AdaTextButton(onClick = { confirmNew = true }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("new-message")) { Text("Start a new message") }
            AdaTextButton(onClick = { details = !details }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text(if (details) "Hide request details" else "Request details") }
            if (details) SafeChatText("Request: ${pending.message.body.request_id}\nMemory: ${if (pending.message.body.use_memory) "enabled" else "disabled"}\nHistorical instant: ${pending.message.body.as_of ?: "current"}", links = false)
        }
    }
    if (confirmNew) AlertDialog(
        onDismissRequest = { confirmNew = false }, title = { Text("Start a separate message?") },
        text = { Text("The original server request is kept. Your next Send will use a new request ID and the current draft. It will not retry or cancel the original request.") },
        confirmButton = { AdaTextButton(onClick = { confirmNew = false; vm.discardPending() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Use a new request") } },
        dismissButton = { AdaTextButton(onClick = { confirmNew = false }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Keep original request") } },
    )
}

@Composable
private fun Composer(state: ChatState, vm: ChatViewModel, maximumHeight: Dp) {
    // In a short landscape IME window, scroll inside a one-line editor rather
    // than scrolling the entire icon row out of view with a multiline draft.
    val shortWindow = maximumHeight < AdaLayout.shortComposer
    var advanced by remember { mutableStateOf(false) }
    var addMenu by remember { mutableStateOf(false) }
    val focus = LocalFocusManager.current
    val reserved = state.pending != null
    val voiceState by vm.voice.state.collectAsStateWithLifecycle()
    val composerText = voiceState.draft?.reviewedText ?: voiceState.partialText ?: state.draft
    val count = composerText.codePointCount(0, composerText.length)
    val canSend = !state.connecting && !vm.voice.captureActive && !voiceState.draftLoading && !reserved && composerText.isNotBlank() && (count <= 4000 || voiceState.draft?.transcript?.isLong()==true) && state.capabilities?.chat == true &&
        (voiceState.draft == null || vm.voice.composerDraftForSend() != null)
    val progress = state.stream?.takeIf { it.request_id == state.pending?.message?.body?.request_id }
    val canStop = progress?.stream_state in setOf("running", "cancel_requested") && progress?.available == true
    AdaGlassSurface(Modifier.padding(horizontal = AdaSpacing.small, vertical = AdaSpacing.tiny).testTag("chat-composer-surface"), boundary = true) {
        Column(Modifier.fillMaxWidth().heightIn(max = maximumHeight).verticalScroll(rememberScrollState()).padding(AdaSpacing.tiny)) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.Bottom) {
                Box {
                    AdaIconButton(AdaIcon.Attach, "Add or message options", { addMenu = true }, Modifier.testTag("composer-menu").semantics { stateDescription = if (addMenu) "Expanded" else "Collapsed" })
                    DropdownMenu(addMenu, { addMenu = false }) {
                        if (state.capabilities?.let { it.document_uploads && it.document_ingestion == "text_markdown_v1" } == true) DropdownMenuItem(
                            text = { Text("Open document imports") }, leadingIcon = { AdaIconGlyph(AdaIcon.Attach) },
                            onClick = { addMenu = false; focus.clearFocus(); vm.navigate(ChatDestination.Documents) }, modifier = Modifier.testTag("attach-document"))
                        DropdownMenuItem(text = { Text("Message options") }, leadingIcon = { AdaIconGlyph(AdaIcon.Options) },
                            onClick = { addMenu = false; focus.clearFocus(); advanced = true }, modifier = Modifier.testTag("message-options"))
                    }
                }
                BasicTextField(
                    composerText, vm::updateComposerDraft, minLines = 1, maxLines = if (shortWindow) 1 else 4,
                    enabled = voiceState.draft == null || !reserved,
                    textStyle = MaterialTheme.typography.bodyLarge.copy(color = MaterialTheme.colorScheme.onSurface),
                    cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Default),
                    modifier = Modifier.weight(1f).heightIn(min = AdaSpacing.touch).testTag("composer").semantics {
                        contentDescription = "Message ADA"
                        if (vm.voice.captureActive) stateDescription = "Transcript in progress; editing is available after recording"
                        if (count > (if(voiceState.draft?.transcript?.isLong()==true) LONG_VOICE_TEXT else 4000)) error("This draft exceeds the recording mode text limit.")
                    },
                    decorationBox = { field -> Box(Modifier.padding(vertical = if (shortWindow) AdaSpacing.small else AdaLayout.fieldInset, horizontal = AdaSpacing.tiny)) {
                        if (composerText.isEmpty()) Text("Message ADA", style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        field()
                    } },
                )
                VoicePanel(vm)
                if (canStop) AdaIconButton(AdaIcon.Stop, if (state.stopping || progress?.stream_state == "cancel_requested") "Stop requested" else "Stop reply",
                    vm::stopGeneration, Modifier.testTag("stop-generation"), enabled = !state.stopping && progress?.stream_state == "running")
                else AdaIconButton(AdaIcon.Send, "Send message", { focus.clearFocus(); vm.send() }, Modifier.testTag("send"), enabled = canSend)
            }
            if (voiceState.enabled || vm.voice.captureActive || voiceState.draft != null) {
                Text(when {
                    voiceState.fault != null -> "Voice draft needs attention · tap mic for details or retry"
                    voiceState.draftLoading -> "Checking encrypted voice draft…"
                    voiceState.phase == VoicePhase.Recording -> "Recording · ${voiceState.durationMs / 1000}s / ${if(voiceState.longFormEnabled) "2h" else "60s"} · release or tap mic to finish"
                    voiceState.draft != null -> if (voiceState.saving) "Saving encrypted voice draft…" else "Voice draft · edit above; Send approves · tap mic for options"
                    vm.voice.captureActive || voiceState.phase in setOf(VoicePhase.Denied, VoicePhase.Interrupted, VoicePhase.Error, VoicePhase.Unavailable) -> voiceState.notice ?: voicePhaseLabel(voiceState.phase)
                    else -> "Tap mic for controls · hold to talk"
                }, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 1, overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis,
                    modifier = Modifier.padding(horizontal = AdaSpacing.small).testTag("voice-composer-status"))
            }
            if (count >= 3600 && !vm.voice.captureActive) Text(if(voiceState.draft?.transcript?.isLong()==true) "$count / 32,768 · select reply context in voice controls" else if (count > 4000) "Shorten this draft to 4,000 Unicode characters. Emoji count once." else "$count / 4,000 characters",
                modifier = Modifier.padding(horizontal = AdaSpacing.medium).testTag("composer-count"),
                color = if (count > 4000) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodySmall)
        }
    }
    if (advanced) CompactChatDialog("Message options", "message-options-dialog", "message-options-done", { advanced = false }) {
                if (state.capabilities?.memory_in_chat == true) Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(state.useMemory, vm::updateMemory, enabled = !reserved, modifier = Modifier.semantics { contentDescription = "Use saved memory in this message" })
                    Text("Use saved memory", style = MaterialTheme.typography.bodyMedium)
                }
                if (state.capabilities?.let { it.document_retrieval && it.document_citations } == true) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Checkbox(state.useDocuments, vm::updateDocuments, enabled = !reserved && state.useMemory && state.conversation?.prompt_version in setOf("ada-baseline-v4", "ada-baseline-v5"),
                            modifier = Modifier.testTag("use-documents").semantics { contentDescription = "Use imported documents in this message" })
                        Text("Use imported documents", style = MaterialTheme.typography.bodyMedium)
                    }
                    if (state.conversation?.prompt_version !in setOf("ada-baseline-v4", "ada-baseline-v5")) Text("Explicitly update this conversation’s saved prompt to use imported documents.", style = MaterialTheme.typography.bodyMedium)
                    else if (!state.useMemory) Text("Turn on saved memory to use scoped evidence, including imported documents.", style = MaterialTheme.typography.bodyMedium)
                }
                if (state.capabilities?.historical_memory_queries == true) OutlinedTextField(
                    state.asOf, vm::updateAsOf, label = { Text("Historical instant (optional)") },
                    supportingText = { Text("ISO 8601 with a timezone, for example 2026-10-08T12:00:00.000Z. Blank uses current memory.") },
                    enabled = !reserved, singleLine = true, modifier = Modifier.fillMaxWidth().testTag("historical-instant"),
                )
                if (reserved) Text("The pending request keeps its original options.", style = MaterialTheme.typography.bodyMedium)

    }
}

@Composable
private fun SourcesScreen(state: ChatState, vm: ChatViewModel) {
    val id = state.sourceRequestId
    val voice by vm.voice.state.collectAsStateWithLifecycle()
    androidx.compose.runtime.LaunchedEffect(id) { id?.let(vm.voice::inspectLineage) }
    val request = id?.let { state.sources[it] }?.takeIf { it.request_id == id }
    val cards = request?.citations.orEmpty().filter { state.sourceLabel == null || it.label == state.sourceLabel }
    val documents = request?.document_citations.orEmpty().filter { state.sourceLabel == null || it.label == state.sourceLabel }
    val continuity = request?.continuity_citations.orEmpty().filter { state.sourceLabel == null || it.label == state.sourceLabel }
    LazyColumn(Modifier.fillMaxSize().testTag("sources-list"), contentPadding = androidx.compose.foundation.layout.PaddingValues(AdaSpacing.medium), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        item { BackButton(vm::back); ScreenHeading("Sources", "These cards belong to this saved reply, with the original quotes and source versions."); StateFeedback(state) }
        voice.lineage?.takeIf { it.request_id == id }?.let { row -> item { VoiceLineageCard(row) } }
        voice.longLineage?.takeIf { it.request_id == id }?.let { row -> item { LongVoiceLineageCard(row) } }
        if (state.sourceLoading) item { BusyIndicator("Loading sources for this reply") }
        if (!state.sourceLoading && request != null && cards.isEmpty() && documents.isEmpty() && continuity.isEmpty()) item {
            StatusCard("Source unavailable", if (state.sourceLabel != null) "This label has no source card for the saved reply. It may refer to an older request without a recorded trace or an unknown label." else "No source cards are attached to this saved reply. Older requests may have no retrieval trace.")
        }
        items(cards, key = { "${it.label}:${it.claim_id}" }) { card -> ChatSourceCard(card, checkNotNull(id)) }
        items(documents, key = { "${it.label}:${it.chunk_id}" }) { card -> DocumentSourceCard(card, checkNotNull(id)) }
        items(continuity, key = { "${it.label}:${it.episode_id}" }) { card ->
            Card(Modifier.fillMaxWidth()) { Column(Modifier.padding(AdaSpacing.medium)) {
                Text("[${card.label}] Continuity source · ${card.trust_class}", style = MaterialTheme.typography.titleMedium)
                Text("Exact original excerpt selected through a generated episode. A reference is not verified recollection or proof; summaries remain generated navigation.")
                if (card.omitted_source_count > 0) Text("Some original episode sources were omitted from this bounded selection.")
                SafeChatText(card.evidence.quote, links = false)
            } }
        }
        if (!state.sourceLoading && request == null && id != null) item {
            AdaTextButton(onClick = { vm.openSources(id, state.sourceLabel) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Try loading sources again") }
        }
        if (id != null) item {
            AdaOutlinedButton(onClick = vm::loadTrace, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("retrieval-details")) { Text("Retrieval details") }
            Text("Selected context, including uncited material, is shown separately from reply sources.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
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
        if (!state.traceLoading && !state.traceMissing && trace == null) item { AdaTextButton(onClick = vm::loadTrace, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Try loading retrieval details again") } }
    }
}

@Composable
private fun AccountSettingsScreen(state: ChatState, vm: ChatViewModel, openSettings: () -> Unit) {
    var confirmLogout by remember { mutableStateOf<Boolean?>(null) }
    var replacement by remember(state.account?.owner, state.account?.server) { mutableStateOf("") }
    val focus = LocalFocusManager.current
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(AdaSpacing.large), verticalArrangement = Arrangement.spacedBy(AdaSpacing.medium)) {
        ScreenHeading("Settings", "Your connection, appearance and interaction preferences.")
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
        AdaOutlinedButton(onClick = openSettings, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("appearance")) { Text("Appearance") }
        Text("ADA Ambient, Oxford Blue, Dark Red or Olive Green. Light and dark modes keep your system text size.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        HorizontalDivider()
        AdaSettingsGroup("Chat styles", "settings-styles") { SettingsProfiles(state, vm) }
        HorizontalDivider()
        AdaSettingsGroup("Interaction preferences", "settings-preferences") { ExpressionSettings(vm.expression, state.conversation?.id) }
        HorizontalDivider()
        AdaSettingsGroup("Learning and continuity", "settings-learning") { LearningSettings(vm.learning, state) }
        if (state.capabilities?.curiosity_protocol == "ada-curiosity-v1") AdaTextButton({ vm.navigate(ChatDestination.Curiosity) }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Questions & curiosity settings") }
        if (state.capabilities?.work_protocol == WORK_PROTOCOL) AdaTextButton({ vm.navigate(ChatDestination.Work) }, modifier = Modifier.testTag("settings-work")) { Text("Projects & next actions") }
        if (state.capabilities?.device_draft_sync == EDGE_PROTOCOL) AdaTextButton({ vm.navigate(ChatDestination.Edge) }, modifier = Modifier.testTag("settings-edge")) { Text("Device drafts · study") }
        if (state.capabilities?.reflection_protocol == "ada-reflection-v1") AdaTextButton({ vm.navigate(ChatDestination.Reflection) }, modifier = Modifier.testTag("settings-reflection")) { Text("While you were away") }
        if (state.capabilities?.scheduling_protocol == "ada-scheduling-v1") AdaTextButton({ vm.navigate(ChatDestination.Schedules) }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-schedules")) { Text("Reminders & inbox") }
        HorizontalDivider()
        AdaSettingsGroup("Devices and saved content", "settings-security") { SecuritySettings(vm.security) }
        AdaSettingsGroup("Advanced token access", "settings-token") {
        state.account?.let { account ->
            HorizontalDivider()
            Text("Replace this account’s token", style = MaterialTheme.typography.titleMedium)
            Text("Use a newly issued token for the same account. ADA verifies the owner again before restoring saved recovery state.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            OutlinedTextField(
                replacement, { replacement = it }, label = { Text("Replacement bearer token") },
                singleLine = true, visualTransformation = PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
                modifier = Modifier.fillMaxWidth().testTag("replacement-token"),
            )
            AdaOutlinedButton(
                onClick = { val entered = replacement; replacement = ""; focus.clearFocus(); vm.rotateCredential(account.server, entered) },
                enabled = !state.connecting && replacement.isNotBlank(),
                modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("replace-token"),
            ) { Text("Replace token for this account") }
        }
        }
        Text("Account and server changes clear local conversations, sources, drafts and pending requests. A request already submitted may continue on the server.", style = MaterialTheme.typography.bodyMedium)
        AdaSettingsGroup("Password sessions", "settings-password") { PasswordSessionPanel(vm) }
        AdaOutlinedButton(onClick = { confirmLogout = true }, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch)) { Text("Sign out all password sessions") }
        AdaButton(onClick = { confirmLogout = false }, modifier = Modifier.fillMaxWidth().heightIn(min = AdaSpacing.touch).testTag("logout")) { Text("Log out / change server") }
        Text("Voice uses installed on-device services. Memory extraction requires explicit review.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
    confirmLogout?.let { all -> AdaConfirmation(
        if (all) "Sign out all password sessions?" else "Log out of this device?",
        if (all) "This signs out password sessions on every device. Local private views and recovery are cleared. Saved server content and separate device tokens remain."
        else "This clears local conversations, drafts and recovery. Submitted server requests may continue; saved server content remains.",
        if (all) "Sign out all sessions" else "Log out", { confirmLogout = null }, { confirmLogout = null; vm.logout(all = all) }, "logout") }

}

@Composable
private fun SettingsProfiles(state: ChatState, vm: ChatViewModel) {
    var creating by remember(state.account?.owner, state.account?.server) { mutableStateOf(false) }
    var choosing by remember(state.account?.owner, state.account?.server) { mutableStateOf(false) }
    val profileDraft = state.profileDraft
    val focus = LocalFocusManager.current
    val selected = state.profiles.items.firstOrNull { it.id == state.createProfileId }
        ?: state.selectedProfile?.takeIf { it.id == state.createProfileId }
    Text("Choose an expression style for a new conversation. Existing conversations keep their saved style, prompt and knowledge scope.", style = MaterialTheme.typography.bodyMedium)
    state.conversation?.let { conversation ->
        Text("Saved in ${conversation.title}: ${conversation.personality.name} · ${conversation.personality.style} · ${conversation.personality.warmth} · ${conversation.personality.detail}", style = MaterialTheme.typography.bodySmall)
    }
    Text(selected?.let { "For a new conversation: ${it.name} · ${it.style} · ${it.warmth} · ${it.detail}" } ?: "Choose a style when starting a new conversation.", style = MaterialTheme.typography.bodySmall)
    AdaOutlinedButton(onClick = { choosing = !choosing; if (choosing) vm.refreshProfiles() }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-choose-profile")) { Text(if (choosing) "Close style list" else "Choose for a new conversation") }
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
        if (state.profiles.hasMore && !state.profiles.loading) AdaTextButton(onClick = vm::loadMoreProfiles, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Load more styles") }
    }
    AdaOutlinedButton(onClick = { creating = !creating }, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-new-profile")) { Text(if (creating) "Close new style" else "Create a chat style") }
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
            Text("The profile creation outcome is unknown. Refresh and review the owned list before consciously allowing a new creation.", style = MaterialTheme.typography.bodyMedium)
            AdaTextButton(onClick = { choosing = true; vm.refreshProfiles() }, modifier = Modifier.heightIn(min = AdaSpacing.touch)) { Text("Refresh and review styles") }
            AdaTextButton(onClick = vm::acknowledgeProfileReview, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-review-profile")) { Text("I reviewed the list; allow a new style") }
        }
        AdaButton(onClick = { focus.clearFocus(); vm.createProfile(profileDraft.name, profileDraft.style, profileDraft.warmth, profileDraft.detail) },
            enabled = !state.creatingProfile && !state.profileUncertain && profileDraft.name.isNotBlank(), modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("settings-create-profile")) {
            Text(if (state.creatingProfile) "Creating style…" else "Create for new conversations")
        }
    }
}

@Composable
private fun StateFeedback(state: ChatState, suppressFailure: Boolean = false) {
    if (!suppressFailure) state.fault?.let { FailureNotice(it) }
    state.notice?.let { AdaNotice(it) }
}

@Composable
private fun FailureNotice(failure: ApiFailure) {
    AdaFailureNotice(failure, Modifier.testTag("failure-notice"))
}

@Composable
private fun ScreenHeading(title: String, explanation: String) {
    AdaSectionHeading(title, explanation)
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
private fun BackButton(back: () -> Unit) { AdaTextButton(onClick = back, modifier = Modifier.heightIn(min = AdaSpacing.touch).testTag("screen-back")) { Text("Back") } }

@Composable
private fun BusyIndicator(label: String) {
    AdaLoading(label)
}

private fun scopeLabel(kind: String): String = when (kind) { "personal" -> "Private personal scope"; "project" -> "Private project scope"; else -> "Private scope" }

@Composable
private fun NavigationGlyph(kind: Int) {
    AdaIconGlyph(when (kind) { 0 -> AdaIcon.Chat; 1 -> AdaIcon.Memory; 3 -> AdaIcon.Sources; else -> AdaIcon.Settings })
}
