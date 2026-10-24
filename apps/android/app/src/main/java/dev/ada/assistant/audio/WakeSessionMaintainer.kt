package dev.ada.assistant.audio

import dev.ada.assistant.data.*

/** Reads only owned authentication/conversation metadata. Never reads a journal or sends a turn. */
class WakeSessionMaintainer(private val api:AdaApi,private val store:SessionStore,private val debug:Boolean) {
    private val rotations=PasswordRefreshCoordinator.forStore(store)
    suspend fun verify(grant:WakeAuthority.Grant):WakeAuthority.Grant? {
        val saved=try { store.readCredential() } catch (_:Exception) { null } ?: return null
        if(saved.identity!=grant.identity || saved.dataEpoch!=grant.dataEpoch || (grant.sessionId!=null && saved.loginSessionId!=grant.sessionId)) return null
        val token:String; val expires:Long; var sessionId=saved.loginSessionId
        if(saved.passwordSession) {
            val refreshed=rotations.refresh(api,store,saved,debug,background=true)
            if(refreshed is ApiResult.Failure && refreshed.reason is ApiFailure.Busy) return grant.takeIf { it.expiresAt>System.currentTimeMillis() }
            if(refreshed !is ApiResult.Success) return null
            token=refreshed.value.access_token; expires=minOf(refreshed.value.access_expires_at,refreshed.value.expires_at); sessionId=refreshed.value.session_id
        } else { token=saved.token; expires=System.currentTimeMillis()+120000 }
        val access=ConnectionCredential.parse(grant.identity.server,token,debug) ?: return null
        access.dataEpoch=grant.dataEpoch
        val me=api.me(access)
        if(me !is ApiResult.Success || me.value.id!=grant.identity.owner || me.value.data_epoch!=grant.dataEpoch) return null
        val conversation=api.conversation(access,grant.conversation)
        if(conversation !is ApiResult.Success || conversation.value.id!=grant.conversation || conversation.value.scope_id!=grant.scope) return null
        return grant.copy(expiresAt=expires,sessionId=sessionId)
    }
}
