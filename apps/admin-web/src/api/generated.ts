export interface paths {
    "/v1/admin/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Me */
        get: operations["me_v1_admin_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/admin/requests": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Requests */
        get: operations["requests_v1_admin_requests_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/admin/requests/{owner_id}/{request_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Request Detail */
        get: operations["request_detail_v1_admin_requests__owner_id___request_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/admin/providers": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Providers */
        get: operations["providers_v1_admin_providers_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/admin/overview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Overview */
        get: operations["overview_v1_admin_overview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/admin/audit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Audits */
        get: operations["audits_v1_admin_audit_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/documents/uploads/{upload_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Upload */
        post: operations["upload_v1_scopes__scope_id__documents_uploads__upload_id__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/document-uploads": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Uploads */
        get: operations["uploads_v1_scopes__scope_id__document_uploads_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/document-uploads/{upload_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Upload Status */
        get: operations["upload_status_v1_document_uploads__upload_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/documents/{source_id}/versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Versions */
        get: operations["versions_v1_documents__source_id__versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/document-versions/{source_version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Version */
        get: operations["version_v1_document_versions__source_version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/document-versions/{source_version_id}/chunks": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Chunks */
        get: operations["chunks_v1_document_versions__source_version_id__chunks_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/document-versions/{source_version_id}/raw": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Raw */
        get: operations["raw_v1_document_versions__source_version_id__raw_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/entities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Entities */
        get: operations["entities_v1_scopes__scope_id__entities_get"];
        put?: never;
        /** Create */
        post: operations["create_v1_scopes__scope_id__entities_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/entities/resolve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Resolve */
        post: operations["resolve_v1_scopes__scope_id__entities_resolve_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/entities/self": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Self Link */
        post: operations["self_link_v1_scopes__scope_id__entities_self_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/entity-audit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Audit */
        get: operations["audit_v1_scopes__scope_id__entity_audit_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entity-operations/{operation_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Operation */
        get: operations["operation_v1_entity_operations__operation_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Entity */
        get: operations["entity_v1_entities__entity_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}/aliases": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Aliases */
        get: operations["aliases_v1_entities__entity_id__aliases_get"];
        put?: never;
        /** Add Alias */
        post: operations["add_alias_v1_entities__entity_id__aliases_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entity-aliases/{alias_id}/retire": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Retire Alias */
        post: operations["retire_alias_v1_entity_aliases__alias_id__retire_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}/rename": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Rename */
        post: operations["rename_v1_entities__entity_id__rename_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}/merge-preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preview */
        get: operations["preview_v1_entities__entity_id__merge_preview_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}/merge": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Merge */
        post: operations["merge_v1_entities__entity_id__merge_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/entities/{entity_id}/undo-merge": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Undo */
        post: operations["undo_v1_entities__entity_id__undo_merge_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/claims/{claim_id}/entity": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Link */
        post: operations["link_v1_claims__claim_id__entity_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/memory-extractions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Extract */
        post: operations["extract_v1_scopes__scope_id__memory_extractions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/memory-extractions/{extraction_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Extraction */
        get: operations["extraction_v1_memory_extractions__extraction_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/memory-proposals": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Inbox */
        get: operations["inbox_v1_scopes__scope_id__memory_proposals_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/memory-proposals/{proposal_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Detail */
        get: operations["detail_v1_memory_proposals__proposal_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/memory-proposals/{proposal_id}/edit": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Edit */
        post: operations["edit_v1_memory_proposals__proposal_id__edit_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/memory-proposals/{proposal_id}/review": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Review */
        post: operations["review_v1_memory_proposals__proposal_id__review_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/memory-reviews/{review_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Receipt */
        get: operations["receipt_v1_memory_reviews__review_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tools": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Tools */
        get: operations["tools_v1_tools_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/agent-protocols": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Protocols */
        get: operations["protocols_v1_agent_protocols_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/agent-runs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Runs */
        get: operations["runs_v1_conversations__conversation_id__agent_runs_get"];
        put?: never;
        /** Create */
        post: operations["create_v1_conversations__conversation_id__agent_runs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/agent-runs/{run_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Detail */
        get: operations["detail_v1_agent_runs__run_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/agent-runs/{run_id}/steps/{step_id}/approve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Approve */
        post: operations["approve_v1_agent_runs__run_id__steps__step_id__approve_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/agent-runs/{run_id}/steps/{step_id}/revoke": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Revoke */
        post: operations["revoke_v1_agent_runs__run_id__steps__step_id__revoke_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/agent-runs/{run_id}/recover": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Recover */
        post: operations["recover_v1_agent_runs__run_id__recover_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/tool-receipts/{receipt_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Receipt */
        get: operations["receipt_v1_tool_receipts__receipt_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/consolidation-jobs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Jobs */
        get: operations["jobs_v1_scopes__scope_id__consolidation_jobs_get"];
        put?: never;
        /** Enqueue */
        post: operations["enqueue_v1_scopes__scope_id__consolidation_jobs_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/consolidation-jobs/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Job */
        get: operations["job_v1_consolidation_jobs__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/episodes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Episodes */
        get: operations["episodes_v1_scopes__scope_id__episodes_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/episodes/{episode_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Episode */
        get: operations["episode_v1_episodes__episode_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/episode-contexts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Context */
        post: operations["context_v1_scopes__scope_id__episode_contexts_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/episode-contexts/{request_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Frozen Context */
        get: operations["frozen_context_v1_episode_contexts__request_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/preferences/{kind}/{target_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Preference */
        get: operations["preference_v1_preferences__kind___target_id__get"];
        put?: never;
        /** Write */
        post: operations["write_v1_preferences__kind___target_id__post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/expression": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Inspect */
        get: operations["inspect_v1_conversations__conversation_id__expression_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/expression/signals": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Signal */
        post: operations["signal_v1_conversations__conversation_id__expression_signals_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/expression/reset": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reset */
        post: operations["reset_v1_conversations__conversation_id__expression_reset_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/expression-receipts/{operation_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Receipt */
        get: operations["receipt_v1_expression_receipts__operation_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/expression": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Snapshot */
        get: operations["snapshot_v1_requests__request_id__expression_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/learning": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** State */
        get: operations["state_v1_scopes__scope_id__learning_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/learning/config": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Configure */
        post: operations["configure_v1_scopes__scope_id__learning_config_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/learning/observations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Observe */
        post: operations["observe_v1_scopes__scope_id__learning_observations_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/learning/reviews": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Review */
        post: operations["review_v1_scopes__scope_id__learning_reviews_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/learning/reset": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Reset */
        post: operations["reset_v1_scopes__scope_id__learning_reset_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/learning-receipts/{operation_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Receipt */
        get: operations["receipt_v1_learning_receipts__operation_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/learning": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Snapshot */
        get: operations["snapshot_v1_requests__request_id__learning_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/stream-requests": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit */
        post: operations["submit_v1_conversations__conversation_id__stream_requests_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/stream-status": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Status */
        get: operations["status_v1_requests__request_id__stream_status_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/cancel": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Cancel */
        post: operations["cancel_v1_requests__request_id__cancel_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/stream": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Stream */
        get: operations["stream_v1_requests__request_id__stream_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/voice-requests": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Submit */
        post: operations["submit_v1_conversations__conversation_id__voice_requests_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/voice-input": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get */
        get: operations["get_v1_requests__request_id__voice_input_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/voice-inputs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Inputs */
        get: operations["list_inputs_v1_conversations__conversation_id__voice_inputs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health/live": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Live */
        get: operations["live_health_live_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health/ready": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Ready */
        get: operations["ready_health_ready_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Me */
        get: operations["me_v1_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/capabilities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Capabilities */
        get: operations["capabilities_v1_capabilities_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/personalities": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Personalities */
        get: operations["personalities_v1_personalities_get"];
        put?: never;
        /** Create Personality */
        post: operations["create_personality_v1_personalities_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Conversations */
        get: operations["conversations_v1_conversations_get"];
        put?: never;
        /** Create Conversation */
        post: operations["create_conversation_v1_conversations_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Conversation */
        get: operations["conversation_v1_conversations__conversation_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/prompt-upgrade": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Upgrade Prompt */
        post: operations["upgrade_prompt_v1_conversations__conversation_id__prompt_upgrade_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/events": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Events */
        get: operations["events_v1_conversations__conversation_id__events_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/conversations/{conversation_id}/messages": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Chat */
        post: operations["chat_v1_conversations__conversation_id__messages_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Request Status */
        get: operations["request_status_v1_requests__request_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/requests/{request_id}/retrieval": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Request Retrieval */
        get: operations["request_retrieval_v1_requests__request_id__retrieval_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scopes */
        get: operations["scopes_v1_scopes_get"];
        put?: never;
        /** Create Scope */
        post: operations["create_scope_v1_scopes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Scope */
        get: operations["scope_v1_scopes__scope_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/retrieve": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Retrieve Memory */
        post: operations["retrieve_memory_v1_scopes__scope_id__retrieve_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/semantic-index/rebuild": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Rebuild Semantic Index */
        post: operations["rebuild_semantic_index_v1_scopes__scope_id__semantic_index_rebuild_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/notes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Note */
        post: operations["create_note_v1_scopes__scope_id__notes_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/source-versions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Source Versions */
        get: operations["source_versions_v1_scopes__scope_id__source_versions_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/source-versions/{source_version_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Source Version */
        get: operations["source_version_v1_source_versions__source_version_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/scopes/{scope_id}/claims": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Claims */
        get: operations["claims_v1_scopes__scope_id__claims_get"];
        put?: never;
        /** Create Claim */
        post: operations["create_claim_v1_scopes__scope_id__claims_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/claims/{claim_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Claim */
        get: operations["claim_v1_claims__claim_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/v1/claims/{claim_id}/supersede": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Supersede Claim */
        post: operations["supersede_claim_v1_claims__claim_id__supersede_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AdminAuditOutput */
        AdminAuditOutput: {
            /**
             * Id
             * Format: int64
             */
            id: bigint;
            /**
             * Actor Id
             * Format: uuid
             */
            actor_id: string;
            /**
             * Actor Kind
             * @enum {string}
             */
            actor_kind: "user" | "local_operator";
            /**
             * Action
             * @enum {string}
             */
            action: "role.grant" | "role.revoke" | "monitor.me" | "monitor.overview" | "monitor.requests" | "monitor.request" | "monitor.providers" | "monitor.audit";
            /** Target Owner Id */
            target_owner_id: string | null;
            /** Target Request Id */
            target_request_id: string | null;
            /**
             * Outcome
             * @enum {string}
             */
            outcome: "allowed" | "denied" | "not_found" | "invalid" | "failed" | "granted" | "revoked" | "unchanged" | "rate_limited";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** AdminAuditsOutput */
        AdminAuditsOutput: {
            /** Items */
            items: components["schemas"]["AdminAuditOutput"][];
            /** Limit */
            limit: number;
            /** Offset */
            offset: number;
            /** Has More */
            has_more: boolean;
            /**
             * Retention Days
             * @default 30
             * @constant
             */
            retention_days: 30;
            /**
             * Max Rows
             * @default 10000
             * @constant
             */
            max_rows: 10000;
            /**
             * Updated At
             * Format: int64
             */
            updated_at: bigint;
        };
        /** AdminJobMetadata */
        AdminJobMetadata: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "episode" | "proposals" | "lexical_rebuild";
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "running" | "completed" | "failed" | "stale";
            /** Checkpoint */
            checkpoint: string;
            /** Version */
            version: string;
            /** Attempt */
            attempt: number;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Started At */
            started_at: bigint | null;
            /** Finished At */
            finished_at: bigint | null;
            /** Elapsed Ms */
            elapsed_ms: number | null;
        };
        /** AdminMeOutput */
        AdminMeOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Permissions */
            permissions: "monitoring:read"[];
        };
        /** AdminOverviewOutput */
        AdminOverviewOutput: {
            /** Consolidation Job Counts */
            consolidation_job_counts?: {
                [key: string]: number;
            } | null;
            /** Consolidation Jobs */
            consolidation_jobs?: components["schemas"]["AdminJobMetadata"][] | null;
            agent_run_counts?: components["schemas"]["AgentCounts"] | null;
            /** Memory Proposal Counts */
            memory_proposal_counts?: {
                [key: string]: number;
            } | null;
            /** Interaction Learning Counts */
            interaction_learning_counts?: {
                [key: string]: number;
            } | null;
            /** Window Hours */
            window_hours: number;
            /**
             * Created From
             * Format: int64
             */
            created_from: bigint;
            /**
             * Updated At
             * Format: int64
             */
            updated_at: bigint;
            requests: components["schemas"]["RequestCounts"];
            /** Input Tokens */
            input_tokens: number | null;
            /** Output Tokens */
            output_tokens: number | null;
            /** Input Tokens Known Requests */
            input_tokens_known_requests: number;
            /** Output Tokens Known Requests */
            output_tokens_known_requests: number;
            /** Database Ready */
            database_ready: boolean;
            /** Schema Version */
            schema_version: string | null;
            provider_health: components["schemas"]["ProviderHealth"];
            generation_admission: components["schemas"]["AdmissionOutput"];
            /** Gpu Utilization */
            gpu_utilization?: number | null;
            /** Tokens Per Second */
            tokens_per_second?: number | null;
        };
        /** AdminProvidersOutput */
        AdminProvidersOutput: {
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            health: components["schemas"]["ProviderHealth"];
            generation_admission: components["schemas"]["AdmissionOutput"];
            /** Context Tokens */
            context_tokens: number;
            /** Output Tokens */
            output_tokens: number;
            /** Timeout Seconds */
            timeout_seconds: number;
            /** Gpu Utilization */
            gpu_utilization?: number | null;
            /** Tokens Per Second */
            tokens_per_second?: number | null;
        };
        /** AdminRequestDetailOutput */
        AdminRequestDetailOutput: {
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "running" | "completed" | "failed";
            /** Attempt */
            attempt: number;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Started At
             * Format: int64
             */
            started_at: bigint;
            /** Finished At */
            finished_at: bigint | null;
            /**
             * Observed At
             * Format: int64
             */
            observed_at: bigint;
            /**
             * Elapsed Ms
             * @description Finished/observed minus current attempt start, including context and DB overhead; not provider latency.
             */
            elapsed_ms: bigint | null;
            /** Error Code */
            error_code: string | null;
            /** Input Tokens */
            input_tokens: number | null;
            /** Output Tokens */
            output_tokens: number | null;
            retrieval: components["schemas"]["RetrievalSummary"];
            stream?: components["schemas"]["StreamMetadata"] | null;
        };
        /** AdminRequestOutput */
        AdminRequestOutput: {
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "running" | "completed" | "failed";
            /** Attempt */
            attempt: number;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Started At
             * Format: int64
             */
            started_at: bigint;
            /** Finished At */
            finished_at: bigint | null;
            /**
             * Observed At
             * Format: int64
             */
            observed_at: bigint;
            /**
             * Elapsed Ms
             * @description Finished/observed minus current attempt start, including context and DB overhead; not provider latency.
             */
            elapsed_ms: bigint | null;
            /** Error Code */
            error_code: string | null;
            /** Input Tokens */
            input_tokens: number | null;
            /** Output Tokens */
            output_tokens: number | null;
        };
        /** AdminRequestsOutput */
        AdminRequestsOutput: {
            /** Items */
            items: components["schemas"]["AdminRequestOutput"][];
            /** Limit */
            limit: number;
            /** Offset */
            offset: number;
            /** Has More */
            has_more: boolean;
            /**
             * Created From
             * Format: int64
             */
            created_from: bigint;
            /**
             * Created To
             * Format: int64
             */
            created_to: bigint;
            /**
             * Updated At
             * Format: int64
             */
            updated_at: bigint;
        };
        /** AdmissionOutput */
        AdmissionOutput: {
            /** Max Parallel */
            max_parallel: number;
            /** Process Available Slots */
            process_available_slots: number;
            /** Process Active Slots */
            process_active_slots: number;
            /**
             * Workers
             * @default 1
             * @constant
             */
            workers: 1;
        };
        /** AgentCounts */
        AgentCounts: {
            /** Running */
            running: number;
            /** Pending Approval */
            pending_approval: number;
            /** Completed */
            completed: number;
            /** Failed */
            failed: number;
            /** Unknown */
            unknown: number;
        };
        /** AgentInput */
        AgentInput: {
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /** Task */
            task: string;
            /**
             * Protocol Version
             * @constant
             */
            protocol_version: "ada-agent-v1";
            /** Allowed Tools */
            allowed_tools: ("calculator" | "memory_lookup" | "source_lookup")[];
            /** As Of */
            as_of?: string | null;
        };
        /** AgentRunOutput */
        AgentRunOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /** Protocol Version */
            protocol_version: string;
            /**
             * Status
             * @enum {string}
             */
            status: "running" | "pending_approval" | "completed" | "failed" | "unknown";
            /** Response */
            response: string | null;
            /** Error Code */
            error_code: string | null;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            /** Generation */
            generation: number;
            /** Lease Until */
            lease_until: bigint | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Finished At */
            finished_at: bigint | null;
            /**
             * As Of
             * Format: int64
             */
            as_of: bigint;
            /** Steps */
            steps: components["schemas"]["AgentStepOutput"][];
        };
        /** AgentStepOutput */
        AgentStepOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Number */
            number: number;
            /** Attempt */
            attempt: number;
            /**
             * Status
             * @enum {string}
             */
            status: "model" | "pending_approval" | "executing" | "completed" | "failed" | "unknown" | "revoked";
            /** Tool */
            tool: ("calculator" | "memory_lookup" | "source_lookup") | null;
            /** Tool Version */
            tool_version: string | null;
            /** Arguments */
            arguments: {
                [key: string]: unknown;
            } | null;
            /** Argument Hash */
            argument_hash: string | null;
            /** Preview Hash */
            preview_hash: string | null;
            /** Expires At */
            expires_at: bigint | null;
            receipt: components["schemas"]["ToolReceiptOutput"] | null;
        };
        /** AliasInput */
        AliasInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Alias Id
             * Format: uuid
             */
            alias_id: string;
            /** Label */
            label: string;
        };
        /** AliasOutput */
        AliasOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Entity Id
             * Format: uuid
             */
            entity_id: string;
            /** Label */
            label: string;
            /** Normalized Key */
            normalized_key: string;
            /** Canonical */
            canonical: boolean;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Valid To */
            valid_to: bigint | null;
            /**
             * Origin
             * @default user_confirmed
             * @constant
             */
            origin: "user_confirmed";
        };
        /** ApprovalInput */
        ApprovalInput: {
            /**
             * Approval Id
             * Format: uuid
             */
            approval_id: string;
            /** Preview Hash */
            preview_hash: string;
            /** Argument Hash */
            argument_hash: string;
            /** Tool Version */
            tool_version: string;
        };
        /** CancelInput */
        CancelInput: {
            /** Attempt */
            attempt: number;
        };
        /** CancelReceipt */
        CancelReceipt: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /** Attempt */
            attempt: number;
            /**
             * Outcome
             * @enum {string}
             */
            outcome: "requested" | "already_terminal";
            /**
             * Observed State
             * @enum {string}
             */
            observed_state: "running" | "cancel_requested" | "completed" | "failed" | "cancelled" | "interrupted";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** Candidate */
        Candidate: {
            /** Subject */
            subject: string;
            /** Predicate */
            predicate: string;
            /** Value */
            value: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "fact" | "preference" | "decision";
            /** Valid From */
            valid_from?: string | null;
            /** Valid To */
            valid_to?: string | null;
            /** Subject Entity Id */
            subject_entity_id?: string | null;
            /** Support */
            support: components["schemas"]["SourcePin"][];
            /** Confidence */
            confidence?: number | null;
        };
        /** CapabilitiesOutput */
        CapabilitiesOutput: {
            /**
             * Voice Input
             * @default unsupported
             */
            voice_input: string;
            /**
             * Voice Audio Uploads
             * @default false
             */
            voice_audio_uploads: boolean;
            /**
             * Stream Protocol
             * @default unsupported
             */
            stream_protocol: string;
            /**
             * Generation Cancellation
             * @default false
             */
            generation_cancellation: boolean;
            /**
             * Interaction Learning
             * @default unsupported
             */
            interaction_learning: string;
            /**
             * Interaction Preferences
             * @default unsupported
             */
            interaction_preferences: string;
            /**
             * Session Expression
             * @default unsupported
             */
            session_expression: string;
            /**
             * Automatic Affect Inference
             * @default false
             */
            automatic_affect_inference: boolean;
            /**
             * Episodes
             * @default unsupported
             */
            episodes: string;
            /**
             * Consolidation Jobs
             * @default unsupported
             */
            consolidation_jobs: string;
            /**
             * Consolidation Generation
             * @default false
             */
            consolidation_generation: boolean;
            /**
             * Consolidation Worker
             * @default false
             */
            consolidation_worker: boolean;
            /**
             * Agent Tools
             * @default unsupported
             */
            agent_tools: string;
            /**
             * Agent Protocol
             * @default unsupported
             */
            agent_protocol: string;
            /** Agent Registry */
            agent_registry?: string[];
            /**
             * Memory Proposals
             * @default unsupported
             */
            memory_proposals: string;
            /**
             * Memory Review
             * @default false
             */
            memory_review: boolean;
            /**
             * Memory Provenance
             * @default legacy
             */
            memory_provenance: string;
            /**
             * Semantic Retrieval
             * @default false
             */
            semantic_retrieval: boolean;
            /**
             * Semantic State
             * @default disabled
             */
            semantic_state: string;
            /**
             * Scoped Entities
             * @default false
             */
            scoped_entities: boolean;
            /**
             * Entity Resolution
             * @default unsupported
             */
            entity_resolution: string;
            /**
             * Entity Writes
             * @default false
             */
            entity_writes: boolean;
            /**
             * Admin Monitoring
             * @default false
             */
            admin_monitoring: boolean;
            /**
             * Document Ingestion
             * @default unsupported
             */
            document_ingestion: string;
            /**
             * Document Uploads
             * @default false
             */
            document_uploads: boolean;
            /**
             * Document Retrieval
             * @default false
             */
            document_retrieval: boolean;
            /**
             * Document Citations
             * @default false
             */
            document_citations: boolean;
            /**
             * Document Max Bytes
             * @default 0
             */
            document_max_bytes: number;
            /** Api Version */
            api_version: string;
            /** Chat */
            chat: boolean;
            /** Streaming */
            streaming: boolean;
            /** Tools */
            tools: boolean;
            /** Structured Memory */
            structured_memory: boolean;
            /** Memory Writes */
            memory_writes: string;
            /** Memory In Chat */
            memory_in_chat: boolean;
            /** Memory Retrieval */
            memory_retrieval: string;
            /** Memory Citations */
            memory_citations: boolean;
            /** Retrieval Traces */
            retrieval_traces: boolean;
            /** Chat Prompt Version */
            chat_prompt_version: string;
            /** Automatic Memory Extraction */
            automatic_memory_extraction: boolean;
            /** Historical Memory Queries */
            historical_memory_queries: boolean;
            /** Private Project Scopes */
            private_project_scopes: boolean;
            /** Shared Scopes */
            shared_scopes: boolean;
            /** Edge Inference */
            edge_inference: boolean;
            /** Personality Isolation */
            personality_isolation: boolean;
            /** Authority */
            authority: string;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
        };
        /** ChatInput */
        ChatInput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /** Content */
            content: string;
            /** As Of */
            as_of?: string | null;
            /**
             * Use Memory
             * @default true
             */
            use_memory: boolean;
            /**
             * Use Documents
             * @default false
             */
            use_documents: boolean;
        };
        /** CitationOutput */
        CitationOutput: {
            provenance?: components["schemas"]["ReviewProvenance"] | null;
            /** Label */
            label: string;
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Subject */
            subject: string;
            /** Predicate */
            predicate: string;
            /** Value */
            value: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "fact" | "preference" | "decision";
            /**
             * Valid From
             * Format: int64
             */
            valid_from: bigint;
            /** Valid To */
            valid_to: bigint | null;
            /**
             * Origin
             * @constant
             */
            origin: "user_asserted";
            evidence: components["schemas"]["EvidenceOutput"];
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Source Version */
            source_version: number;
            /** Conflict */
            conflict: boolean;
            /** Subject Entity Id */
            subject_entity_id?: string | null;
            entity?: components["schemas"]["EntityChoice"] | null;
        };
        /** ClaimInput */
        ClaimInput: {
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Span Start */
            span_start: number;
            /** Span End */
            span_end: number;
            /** Valid To */
            valid_to?: string | null;
            /** Subject Entity Id */
            subject_entity_id?: string | null;
            /** Subject */
            subject: string;
            /** Predicate */
            predicate: string;
            /** Value */
            value: string;
            /**
             * Kind
             * @default fact
             * @enum {string}
             */
            kind: "fact" | "preference" | "decision";
            /** Valid From */
            valid_from?: string | null;
        };
        /** ClaimOutput */
        ClaimOutput: {
            provenance?: components["schemas"]["ReviewProvenance"] | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Subject */
            subject: string;
            /** Subject Entity Id */
            subject_entity_id?: string | null;
            /** Predicate */
            predicate: string;
            /** Value */
            value: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "fact" | "preference" | "decision";
            /**
             * Status
             * @enum {string}
             */
            status: "active" | "superseded";
            /**
             * Valid From
             * Format: int64
             */
            valid_from: bigint;
            /** Valid To */
            valid_to: bigint | null;
            /** Superseded By */
            superseded_by: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Origin
             * @constant
             */
            origin: "user_asserted";
            evidence: components["schemas"]["EvidenceOutput"];
        };
        /** ConflictOutput */
        ConflictOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Value */
            value: string;
            /**
             * Valid From
             * Format: int64
             */
            valid_from: bigint;
            /** Valid To */
            valid_to: bigint | null;
            /** Status */
            status: string;
            /** Write Hash */
            write_hash: string;
            /** Subject Entity Id */
            subject_entity_id: string | null;
        };
        /** ConsolidationInput */
        ConsolidationInput: {
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "episode" | "proposals" | "lexical_rebuild";
            /** Sources */
            sources?: components["schemas"]["SourcePin"][];
        };
        /** ConsolidationOutput */
        ConsolidationOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "episode" | "proposals" | "lexical_rebuild";
            /** Version */
            version: string;
            /**
             * Status
             * @enum {string}
             */
            status: "queued" | "running" | "completed" | "failed" | "stale";
            /**
             * Checkpoint
             * @enum {string}
             */
            checkpoint: "reserved" | "claimed" | "published" | "terminal";
            /** Attempt */
            attempt: number;
            /** Model */
            model: string;
            /** Lease Until */
            lease_until: bigint | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Started At */
            started_at: bigint | null;
            /** Finished At */
            finished_at: bigint | null;
            /** Elapsed Ms */
            elapsed_ms: number | null;
            /** Error Code */
            error_code: string | null;
            receipt: components["schemas"]["ConsolidationReceipt"] | null;
        };
        /** ConsolidationReceipt */
        ConsolidationReceipt: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /**
             * Outcome
             * @enum {string}
             */
            outcome: "completed" | "failed" | "stale";
            /** Attempt */
            attempt: number;
            /** Episode Id */
            episode_id: string | null;
            /** Extraction Id */
            extraction_id: string | null;
            /** Proposal Ids */
            proposal_ids: string[];
            /** Indexed Claims */
            indexed_claims: number | null;
            /** Indexed Chunks */
            indexed_chunks: number | null;
            /** Error Code */
            error_code: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** ContinuityCard */
        ContinuityCard: {
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Source Version */
            source_version: number;
            /**
             * Source Origin
             * @enum {string}
             */
            source_origin: "chat_event" | "user_note" | "imported_document";
            /**
             * Trust Class
             * @enum {string}
             */
            trust_class: "user_explicit" | "model_generated" | "imported_untrusted";
            evidence: components["schemas"]["EvidenceOutput"];
            /** Label */
            label: string;
            /**
             * Episode Id
             * Format: uuid
             */
            episode_id: string;
            /**
             * Summary Trust
             * @constant
             */
            summary_trust: "model_generated";
            /**
             * Uncertainty
             * @constant
             */
            uncertainty: "source_reference_not_verified_recollection";
            /**
             * Omitted Source Count
             * @default 0
             */
            omitted_source_count: number;
        };
        /** ConversationInput */
        ConversationInput: {
            /**
             * Personality Id
             * Format: uuid
             */
            personality_id: string;
            /**
             * Title
             * @default New conversation
             */
            title: string;
            /** Scope Id */
            scope_id?: string | null;
        };
        /** ConversationOutput */
        ConversationOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Title */
            title: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Scope Kind
             * @enum {string}
             */
            scope_kind: "personal" | "project";
            personality: components["schemas"]["PersonalitySnapshotOutput"];
            /** Prompt Version */
            prompt_version: string;
            /** Revision */
            revision: number;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** DocumentCandidateOutput */
        DocumentCandidateOutput: {
            /**
             * Chunk Id
             * Format: uuid
             */
            chunk_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Channels */
            channels: string[];
            /** Decision */
            decision: string;
            /** Score */
            score?: number;
            /** Term Coverage */
            term_coverage?: number;
            /** Semantic Similarity */
            semantic_similarity?: number;
        } & {
            [key: string]: unknown;
        };
        /** DocumentChunkOutput */
        DocumentChunkOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Upload Id
             * Format: uuid
             */
            upload_id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Ordinal */
            ordinal: number;
            /** Span Start */
            span_start: number;
            /** Span End */
            span_end: number;
            /** Quote */
            quote: string;
            /** Content Hash */
            content_hash: string;
            /** Quote Hash */
            quote_hash: string;
            /** Line Start */
            line_start: number;
            /** Line End */
            line_end: number;
        };
        /** DocumentCitationOutput */
        DocumentCitationOutput: {
            /** Label */
            label: string;
            /**
             * Origin
             * @constant
             */
            origin: "imported_document";
            /**
             * Trust Class
             * @constant
             */
            trust_class: "imported_untrusted";
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Source Version */
            source_version: number;
            /**
             * Upload Id
             * Format: uuid
             */
            upload_id: string;
            /**
             * Chunk Id
             * Format: uuid
             */
            chunk_id: string;
            /** Filename */
            filename: string;
            /**
             * Media Type
             * @enum {string}
             */
            media_type: "text/plain" | "text/markdown";
            /** Raw Hash */
            raw_hash: string;
            /**
             * Available From
             * Format: int64
             */
            available_from: bigint;
            /** Available To */
            available_to: bigint | null;
            /**
             * Published At
             * Format: int64
             */
            published_at: bigint;
            /** Line Start */
            line_start: number;
            /** Line End */
            line_end: number;
            evidence: components["schemas"]["EvidenceOutput"];
        };
        /** DocumentUploadOutput */
        DocumentUploadOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Version */
            version: number;
            /** Filename */
            filename: string;
            /**
             * Media Type
             * @enum {string}
             */
            media_type: "text/plain" | "text/markdown";
            /** Input Hash */
            input_hash: string;
            /** Raw Hash */
            raw_hash: string;
            /** Raw Size */
            raw_size: number;
            /**
             * Available From
             * Format: int64
             */
            available_from: bigint;
            /** Available To */
            available_to: bigint | null;
            /**
             * State
             * @enum {string}
             */
            state: "processing" | "ready" | "failed";
            /** Error Code */
            error_code: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Published At */
            published_at: bigint | null;
            /** Chunk Count */
            chunk_count: number;
            /**
             * Origin
             * @constant
             */
            origin: "imported_document";
            /**
             * Trust Class
             * @constant
             */
            trust_class: "imported_untrusted";
        };
        /** DocumentVersionOutput */
        DocumentVersionOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Version */
            version: number;
            /** Content */
            content: string;
            /** Content Hash */
            content_hash: string;
            /**
             * Trust Class
             * @constant
             */
            trust_class: "imported_untrusted";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            upload: components["schemas"]["DocumentUploadOutput"];
        };
        /** EditInput */
        EditInput: {
            /** Revision */
            revision: number;
            /** Review Hash */
            review_hash: string;
            candidate: components["schemas"]["Candidate"];
        };
        /** EffectivePreferences */
        EffectivePreferences: {
            /**
             * Verbosity
             * @enum {string}
             */
            verbosity: "concise" | "balanced" | "detailed";
            /**
             * Initiative
             * @enum {string}
             */
            initiative: "respond" | "suggest";
            /**
             * Formality
             * @enum {string}
             */
            formality: "casual" | "neutral" | "formal";
            /**
             * Humor
             * @enum {string}
             */
            humor: "none" | "light";
            /**
             * Cadence
             * @enum {string}
             */
            cadence: "direct" | "stepwise";
        };
        /** EntityChoice */
        EntityChoice: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Label */
            label: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "person" | "project" | "object" | "other";
        };
        /** EntityInput */
        EntityInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Entity Id
             * Format: uuid
             */
            entity_id: string;
            /** Label */
            label: string;
            /**
             * Kind
             * @default other
             * @enum {string}
             */
            kind: "person" | "project" | "object" | "other";
        };
        /** EntityOperationOutput */
        EntityOperationOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Action
             * @enum {string}
             */
            action: "create" | "alias" | "retire_alias" | "rename" | "self" | "link" | "merge" | "undo_merge";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            entity?: components["schemas"]["EntityOutput"] | null;
            alias?: components["schemas"]["AliasOutput"] | null;
            link?: components["schemas"]["LinkOutput"] | null;
        };
        /** EntityOutput */
        EntityOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Label */
            label: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "person" | "project" | "object" | "other";
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Normalized Key */
            normalized_key: string;
            /** Revision */
            revision: number;
            /** Redirect Id */
            redirect_id: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Is Self */
            is_self: boolean;
            /**
             * Origin
             * @default user_confirmed
             * @constant
             */
            origin: "user_confirmed";
        };
        /** EntityResolutionOutput */
        EntityResolutionOutput: {
            /**
             * State
             * @enum {string}
             */
            state: "resolved" | "ambiguous" | "absent";
            /** Name */
            name: string | null;
            /** Entity Id */
            entity_id: string | null;
            /** Candidates */
            candidates: components["schemas"]["EntityChoice"][];
            /** Alias Ids */
            alias_ids: string[];
            /**
             * Explicitly Selected
             * @default false
             */
            explicitly_selected: boolean;
            /**
             * Truncated
             * @default false
             */
            truncated: boolean;
            /**
             * Policy
             * @default nfkc_casefold_whitespace_v1
             * @constant
             */
            policy: "nfkc_casefold_whitespace_v1";
        };
        /** EpisodeContextInput */
        EpisodeContextInput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /** Episode Ids */
            episode_ids: string[];
        };
        /** EpisodeContextOutput */
        EpisodeContextOutput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * As Of
             * Format: int64
             */
            as_of: bigint;
            /**
             * Purpose
             * @constant
             */
            purpose: "navigation_only";
            /** Episodes */
            episodes: components["schemas"]["EpisodeOutput"][];
        };
        /** EpisodeOutput */
        EpisodeOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Job Id
             * Format: uuid
             */
            job_id: string;
            /** Summary Version */
            summary_version: string;
            /** Model */
            model: string;
            /**
             * Trust Class
             * @constant
             */
            trust_class: "model_generated";
            /** Sections */
            sections: components["schemas"]["SummarySection"][];
            /** Tags */
            tags: string[];
            /** Omissions */
            omissions: string[];
            /** Sources */
            sources: components["schemas"]["EpisodeSource"][];
            /**
             * Range Start
             * Format: int64
             */
            range_start: bigint;
            /**
             * Range End
             * Format: int64
             */
            range_end: bigint;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** EpisodeSource */
        EpisodeSource: {
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Source Version */
            source_version: number;
            /**
             * Source Origin
             * @enum {string}
             */
            source_origin: "chat_event" | "user_note" | "imported_document";
            /**
             * Trust Class
             * @enum {string}
             */
            trust_class: "user_explicit" | "model_generated" | "imported_untrusted";
            evidence: components["schemas"]["EvidenceOutput"];
            /** Conversation Id */
            conversation_id: string | null;
            /** Event Id */
            event_id: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Source Created At
             * Format: int64
             */
            source_created_at: bigint;
            /** Available From */
            available_from?: bigint | null;
            /** Available To */
            available_to?: bigint | null;
            /** Published At */
            published_at?: bigint | null;
        };
        /** ErrorOutput */
        ErrorOutput: {
            /** Detail */
            detail: string;
        };
        /** EventOutput */
        EventOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Role
             * @enum {string}
             */
            role: "user" | "assistant";
            /** Content */
            content: string;
            /**
             * Trust Class
             * @enum {string}
             */
            trust_class: "user_explicit" | "model_generated";
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Request Status
             * @enum {string}
             */
            request_status: "running" | "completed" | "failed";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
        };
        /** EvidenceOutput */
        EvidenceOutput: {
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Span Start */
            span_start: number;
            /** Span End */
            span_end: number;
            /** Quote */
            quote: string;
            /** Content Hash */
            content_hash: string;
        };
        /** ExpressionOutput */
        ExpressionOutput: {
            /**
             * Policy Version
             * @default ada-expression-v1
             * @constant
             */
            policy_version: "ada-expression-v1";
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Profile Id
             * Format: uuid
             */
            profile_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Active */
            active: boolean;
            /** Binding Revision */
            binding_revision: number;
            preferences: components["schemas"]["EffectivePreferences"];
            /** Origins */
            origins: {
                [key: string]: "personality" | "account" | "scope" | "profile" | "conversation";
            };
            /** Source Receipts */
            source_receipts: {
                [key: string]: string | null;
            };
            /** Dynamic Enabled */
            dynamic_enabled: boolean;
            /** Session Id */
            session_id: string | null;
            /** Turn */
            turn: number;
            vector: components["schemas"]["ExpressionVector"];
            defaults: components["schemas"]["ExpressionVector"];
            /** Expires At */
            expires_at: bigint | null;
            /** Expired */
            expired: boolean;
            /** Last Request Id */
            last_request_id: string | null;
        };
        /** ExpressionReceiptOutput */
        ExpressionReceiptOutput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Action
             * @enum {string}
             */
            action: "preferences" | "signal" | "reset";
            /**
             * Target Kind
             * @enum {string}
             */
            target_kind: "account" | "scope" | "profile" | "conversation";
            /**
             * Target Id
             * Format: uuid
             */
            target_id: string;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Reason
             * @enum {string}
             */
            reason: "explicit_settings" | "user_reset" | "user_selected" | "reviewed_model_signal";
            /** Source Request Id */
            source_request_id?: string | null;
            preference?: components["schemas"]["PreferenceOutput"] | null;
            expression?: components["schemas"]["ExpressionOutput"] | null;
        };
        /** ExpressionVector */
        ExpressionVector: {
            /** Warmth */
            warmth: number;
            /** Focus */
            focus: number;
            /** Energy */
            energy: number;
            /** Playfulness */
            playfulness: number;
            /** Concern */
            concern: number;
        };
        /** ExtractionInput */
        ExtractionInput: {
            /**
             * Extraction Id
             * Format: uuid
             */
            extraction_id: string;
            /** Sources */
            sources: components["schemas"]["SourcePin"][];
        };
        /** ExtractionOutput */
        ExtractionOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * State
             * @enum {string}
             */
            state: "processing" | "completed" | "failed";
            /** Model */
            model: string;
            /** Extractor Version */
            extractor_version: string;
            /** Validation */
            validation: {
                [key: string]: unknown;
            };
            /** Error Code */
            error_code: string | null;
            /** Proposal Ids */
            proposal_ids: string[];
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** InteractionObservationOutput */
        InteractionObservationOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Source Request Id
             * Format: uuid
             */
            source_request_id: string;
            source: components["schemas"]["SourcePin"];
            evidence: components["schemas"]["SupportingEvidence"];
            values: components["schemas"]["PreferenceValues"];
            /**
             * Confidence Class
             * @enum {string}
             */
            confidence_class: "explicit_statement" | "repeated_observation" | "weak_inference";
            /**
             * Interpretation Trust
             * @constant
             */
            interpretation_trust: "unreviewed_interpretation";
            /** Extraction Version */
            extraction_version: string;
            /**
             * Purpose
             * @constant
             */
            purpose: "interaction_preference";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /**
             * Expires At
             * Format: int64
             */
            expires_at: bigint;
        };
        /** InteractionProposalOutput */
        InteractionProposalOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Revision */
            revision: number;
            values: components["schemas"]["PreferenceValues"];
            /**
             * Status
             * @enum {string}
             */
            status: "pending" | "approved" | "rejected";
            /** Independent Count */
            independent_count: number;
            /** Eligible */
            eligible: boolean;
            /** Observations */
            observations: string[];
            /**
             * Expires At
             * Format: int64
             */
            expires_at: bigint;
            /**
             * Trust Class
             * @constant
             */
            trust_class: "unreviewed_interpretation";
        };
        /** LearnedPreferenceOutput */
        LearnedPreferenceOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            values: components["schemas"]["PreferenceValues"];
            /** Account Wide */
            account_wide: boolean;
            /**
             * Receipt Id
             * Format: uuid
             */
            receipt_id: string;
            /**
             * Proposal Id
             * Format: uuid
             */
            proposal_id: string;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Observation Ids */
            observation_ids?: string[];
            /** Reviewed Revision */
            reviewed_revision?: number | null;
        };
        /** LearningConfigOutput */
        LearningConfigOutput: {
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Revision */
            revision: number;
            /** Epoch */
            epoch: number;
            /**
             * Status
             * @enum {string}
             */
            status: "off" | "enrolled" | "paused";
            /** Continuity Enabled */
            continuity_enabled: boolean;
            /** Policy Version */
            policy_version: string;
            /** Threshold */
            threshold: number;
        };
        /** LearningConfigWrite */
        LearningConfigWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Expected Revision */
            expected_revision: number;
            /**
             * Status
             * @enum {string}
             */
            status: "off" | "enrolled" | "paused";
            /**
             * Continuity Enabled
             * @default false
             */
            continuity_enabled: boolean;
        };
        /** LearningReceiptOutput */
        LearningReceiptOutput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Action
             * @enum {string}
             */
            action: "config" | "observe" | "review" | "reset";
            /** Revision */
            revision: number;
            /** Epoch */
            epoch: number;
            /** Observation Id */
            observation_id?: string | null;
            /** Proposal Id */
            proposal_id?: string | null;
            /** Decision */
            decision?: ("approve" | "reject") | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Observation Ids */
            observation_ids?: string[];
            /** Proposal Revision */
            proposal_revision?: number | null;
        };
        /** LearningResetWrite */
        LearningResetWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Expected Revision */
            expected_revision: number;
        };
        /** LearningReviewWrite */
        LearningReviewWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Proposal Id
             * Format: uuid
             */
            proposal_id: string;
            /** Expected Revision */
            expected_revision: number;
            /**
             * Decision
             * @enum {string}
             */
            decision: "approve" | "reject";
            /**
             * Account Wide
             * @default false
             */
            account_wide: boolean;
            /**
             * Reviewed
             * @constant
             */
            reviewed: true;
            values?: components["schemas"]["PreferenceValues"] | null;
        };
        /** LearningSnapshot */
        LearningSnapshot: {
            /** Policy Version */
            policy_version: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Epoch */
            epoch: number;
            /** Revision */
            revision: number;
            preferences: components["schemas"]["PreferenceValues"];
            /** Receipts */
            receipts: {
                [key: string]: string;
            };
            /** Continuity */
            continuity: components["schemas"]["ContinuityCard"][];
            /** Continuity Reason */
            continuity_reason: string;
        };
        /** LearningStateOutput */
        LearningStateOutput: {
            config: components["schemas"]["LearningConfigOutput"];
            /** Observations */
            observations: components["schemas"]["InteractionObservationOutput"][];
            /** Proposals */
            proposals: components["schemas"]["InteractionProposalOutput"][];
            /** Learned */
            learned: components["schemas"]["LearnedPreferenceOutput"][];
        };
        /** LinkInput */
        LinkInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Entity Id */
            entity_id: string | null;
            /** Expected Entity Id */
            expected_entity_id: string | null;
        };
        /** LinkOutput */
        LinkOutput: {
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /** Entity Id */
            entity_id: string | null;
            /** Original Subject */
            original_subject: string;
        };
        /** LiveOutput */
        LiveOutput: {
            /**
             * Status
             * @constant
             */
            status: "ok";
        };
        /** MergeInput */
        MergeInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Target Id
             * Format: uuid
             */
            target_id: string;
            /** Preview Token */
            preview_token: string;
        };
        /** MergePreviewOutput */
        MergePreviewOutput: {
            source: components["schemas"]["EntityOutput"];
            target: components["schemas"]["EntityOutput"];
            /** Alias Count */
            alias_count: number;
            /** Claim Link Count */
            claim_link_count: number;
            /** Self Binding Affected */
            self_binding_affected: boolean;
            /** Preview Token */
            preview_token: string;
        };
        /** NoteInput */
        NoteInput: {
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Content */
            content: string;
        };
        /** ObservationWrite */
        ObservationWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            source: components["schemas"]["SourcePin"];
            values: components["schemas"]["PreferenceValues"];
            /**
             * Confidence Class
             * @enum {string}
             */
            confidence_class: "explicit_statement" | "repeated_observation" | "weak_inference";
        };
        /** OperationInput */
        OperationInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
        };
        /** PersonalityInput */
        PersonalityInput: {
            /**
             * Name
             * @default ADA
             */
            name: string;
            /**
             * Style
             * @default conversational
             * @enum {string}
             */
            style: "direct" | "conversational" | "formal";
            /**
             * Warmth
             * @default warm
             * @enum {string}
             */
            warmth: "reserved" | "warm";
            /**
             * Detail
             * @default balanced
             * @enum {string}
             */
            detail: "concise" | "balanced" | "detailed";
        };
        /** PersonalityOutput */
        PersonalityOutput: {
            /** Name */
            name: string;
            /** Style */
            style: string;
            /** Warmth */
            warmth: string;
            /** Detail */
            detail: string;
            /**
             * Id
             * Format: uuid
             */
            id: string;
        } & {
            [key: string]: unknown;
        };
        /** PersonalitySnapshotOutput */
        PersonalitySnapshotOutput: {
            /** Name */
            name: string;
            /** Style */
            style: string;
            /** Warmth */
            warmth: string;
            /** Detail */
            detail: string;
        } & {
            [key: string]: unknown;
        };
        /** PreferenceOutput */
        PreferenceOutput: {
            /**
             * Target Kind
             * @enum {string}
             */
            target_kind: "account" | "scope" | "profile" | "conversation";
            /**
             * Target Id
             * Format: uuid
             */
            target_id: string;
            /** Revision */
            revision: number;
            values: components["schemas"]["PreferenceValues"];
            /** Receipt Id */
            receipt_id: string | null;
        };
        /** PreferenceValues */
        PreferenceValues: {
            /** Verbosity */
            verbosity?: ("concise" | "balanced" | "detailed") | null;
            /** Initiative */
            initiative?: ("respond" | "suggest") | null;
            /** Formality */
            formality?: ("casual" | "neutral" | "formal") | null;
            /** Humor */
            humor?: ("none" | "light") | null;
            /** Cadence */
            cadence?: ("direct" | "stepwise") | null;
        };
        /** PreferenceWrite */
        PreferenceWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Expected Revision */
            expected_revision: number;
            values: components["schemas"]["PreferenceValues"];
            /** Dynamic Enabled */
            dynamic_enabled?: boolean | null;
        };
        /** PromptUpgradeOutput */
        PromptUpgradeOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Prompt Version */
            prompt_version: string;
            /** Revision */
            revision: number;
        };
        /** ProposalOutput */
        ProposalOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Extraction Id
             * Format: uuid
             */
            extraction_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "pending" | "accepted" | "rejected";
            /** Revision */
            revision: number;
            candidate: components["schemas"]["Candidate"];
            original_candidate: components["schemas"]["Candidate"];
            /** Model */
            model: string;
            /** Extractor Version */
            extractor_version: string;
            /** Validation */
            validation: {
                [key: string]: unknown;
            };
            /** Support */
            support: components["schemas"]["SupportingEvidence"][];
            /** Conflicts */
            conflicts: components["schemas"]["ConflictOutput"][];
            /** Review Hash */
            review_hash: string;
            /** Rejection Reason */
            rejection_reason: string | null;
            /** Review Id */
            review_id: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** ProtocolOutput */
        ProtocolOutput: {
            /**
             * Version
             * @constant
             */
            version: "ada-agent-v1";
            /** Compatible Chat Prompts */
            compatible_chat_prompts: string[];
            /** Max Steps */
            max_steps: number;
            /** Context Bytes */
            context_bytes: number;
            /** Elapsed Seconds */
            elapsed_seconds: number;
            /** Approval Seconds */
            approval_seconds: number;
            /** Lease Seconds */
            lease_seconds: number;
            /**
             * External Writes
             * @constant
             */
            external_writes: false;
        };
        /** ProviderHealth */
        ProviderHealth: {
            /**
             * Reachability
             * @enum {string}
             */
            reachability: "reachable" | "unreachable" | "unknown";
            /** Model Available */
            model_available: boolean | null;
            /** Checked At */
            checked_at: bigint | null;
            /** Error Code */
            error_code: ("provider_unavailable" | "invalid_health_response") | null;
            /**
             * Cache Seconds
             * @default 30
             * @constant
             */
            cache_seconds: 30;
        };
        /** ReadyOutput */
        ReadyOutput: {
            /**
             * Status
             * @constant
             */
            status: "ready";
            /** Schema */
            schema: string;
        };
        /** RebuildOutput */
        RebuildOutput: {
            /** Namespace */
            namespace: string;
            /** Indexed */
            indexed: number;
            /** Reused */
            reused: number;
            /**
             * Corpus Limit
             * @default 256
             */
            corpus_limit: number;
            /** Elapsed Ms */
            elapsed_ms: number;
        };
        /** RecoverInput */
        RecoverInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Generation */
            generation: number;
        };
        /** RenameInput */
        RenameInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /** Label */
            label: string;
            /** Expected Revision */
            expected_revision: number;
        };
        /** RequestCounts */
        RequestCounts: {
            /**
             * Running
             * @default 0
             */
            running: number;
            /**
             * Completed
             * @default 0
             */
            completed: number;
            /**
             * Failed
             * @default 0
             */
            failed: number;
        };
        /** RequestExpressionOutput */
        RequestExpressionOutput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            expression: components["schemas"]["ExpressionOutput"] | null;
        };
        /** RequestLearningOutput */
        RequestLearningOutput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            learning: components["schemas"]["LearningSnapshot"] | null;
        };
        /** RequestOutput */
        RequestOutput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "running" | "completed" | "failed";
            /** Response */
            response: string | null;
            /** Error Code */
            error_code: string | null;
            /** Attempt */
            attempt: number;
            /** Provider */
            provider: string;
            /** Model */
            model: string;
            /** Input Tokens */
            input_tokens: number | null;
            /** Output Tokens */
            output_tokens: number | null;
            /** Citations */
            citations: components["schemas"]["CitationOutput"][];
            /** Document Citations */
            document_citations?: components["schemas"]["DocumentCitationOutput"][];
            /** Citation Warnings */
            citation_warnings: string[];
            /** Continuity Citations */
            continuity_citations?: components["schemas"]["ContinuityCard"][];
        };
        /** ResolveInput */
        ResolveInput: {
            /** Name */
            name?: string | null;
            /**
             * Self Reference
             * @default false
             */
            self_reference: boolean;
            /** Selected Id */
            selected_id?: string | null;
            /** As Of */
            as_of?: string | null;
        };
        /** RetrievalBudgetOutput */
        RetrievalBudgetOutput: {
            /** Memory Limit Bytes */
            memory_limit_bytes: number;
            /** Memory Used Bytes */
            memory_used_bytes: number;
            /** Selected Limit */
            selected_limit: number;
            /** Candidate Limit Per Channel */
            candidate_limit_per_channel: number;
            /** Candidate Pool Truncated */
            candidate_pool_truncated: boolean;
            /** Prompt Limit Bytes */
            prompt_limit_bytes?: number;
            /** Prompt Used Bytes */
            prompt_used_bytes?: number;
            /** History Pairs */
            history_pairs?: number;
            /** History Pairs Omitted */
            history_pairs_omitted?: number;
        } & {
            [key: string]: unknown;
        };
        /** RetrievalCandidateOutput */
        RetrievalCandidateOutput: {
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /** Channels */
            channels: string[];
            /** Decision */
            decision: string;
            /** Score */
            score?: number;
            /** Term Coverage */
            term_coverage?: number;
            /** Semantic Similarity */
            semantic_similarity?: number;
        } & {
            [key: string]: unknown;
        };
        /** RetrievalOutput */
        RetrievalOutput: {
            /** Version */
            version: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            plan: components["schemas"]["RetrievalPlanOutput"];
            /** Candidates */
            candidates: components["schemas"]["RetrievalCandidateOutput"][];
            /** Selected */
            selected: components["schemas"]["CitationOutput"][];
            /** Document Candidates */
            document_candidates?: components["schemas"]["DocumentCandidateOutput"][];
            /** Document Selected */
            document_selected?: components["schemas"]["DocumentCitationOutput"][];
            budget: components["schemas"]["RetrievalBudgetOutput"];
            /** Retrieval Ms */
            retrieval_ms: number;
        };
        /** RetrievalPlanOutput */
        RetrievalPlanOutput: {
            semantic?: components["schemas"]["SemanticDiagnostic"] | null;
            /** Entity Keys */
            entity_keys?: string[];
            /** Entity Resolution */
            entity_resolution?: components["schemas"]["EntityResolutionOutput"][];
            /**
             * Entity Ambiguity In Context
             * @default false
             */
            entity_ambiguity_in_context: boolean;
            /**
             * Entity Resolution Truncated
             * @default false
             */
            entity_resolution_truncated: boolean;
            /** Enabled */
            enabled: boolean;
            /**
             * Reason
             * @enum {string}
             */
            reason: "ready" | "date_required" | "disabled" | "prompt_upgrade_required";
            /**
             * Time Mode
             * @enum {string}
             */
            time_mode: "current" | "as_of" | "needs_date";
            /** As Of */
            as_of: bigint | null;
            /** Query Terms */
            query_terms: string[];
            /** Expanded Terms */
            expanded_terms: string[];
            /** Subject Keys */
            subject_keys: string[];
            /** Overview */
            overview: boolean;
            /** Prompt Version */
            prompt_version?: string | null;
            /**
             * Documents Enabled
             * @default false
             */
            documents_enabled: boolean;
            /**
             * Document Reason
             * @default disabled
             * @enum {string}
             */
            document_reason: "ready" | "date_required" | "disabled" | "prompt_upgrade_required";
        };
        /** RetrievalSummary */
        RetrievalSummary: {
            /** Available */
            available: boolean;
            /** Candidate Count */
            candidate_count?: number | null;
            /** Selected Count */
            selected_count?: number | null;
            /** Retrieval Ms */
            retrieval_ms?: number | null;
            /** Memory Limit Bytes */
            memory_limit_bytes?: number | null;
            /** Memory Used Bytes */
            memory_used_bytes?: number | null;
            /** Prompt Limit Bytes */
            prompt_limit_bytes?: number | null;
            /** Prompt Used Bytes */
            prompt_used_bytes?: number | null;
            /** History Pairs Omitted */
            history_pairs_omitted?: number | null;
            /** Candidate Pool Truncated */
            candidate_pool_truncated?: boolean | null;
        };
        /** RetrieveInput */
        RetrieveInput: {
            /** Query */
            query: string;
            /** As Of */
            as_of?: string | null;
            /**
             * Limit
             * @default 8
             */
            limit: number;
            /**
             * Budget Bytes
             * @default 2200
             */
            budget_bytes: number;
            /**
             * Use Documents
             * @default false
             */
            use_documents: boolean;
        };
        /** ReviewInput */
        ReviewInput: {
            /** Revision */
            revision: number;
            /** Review Hash */
            review_hash: string;
            candidate: components["schemas"]["Candidate"];
            /**
             * Review Id
             * Format: uuid
             */
            review_id: string;
            /**
             * Decision
             * @enum {string}
             */
            decision: "accept" | "reject";
            /** Annotation */
            annotation: string;
            /** Replace Claim Id */
            replace_claim_id?: string | null;
        };
        /** ReviewOutput */
        ReviewOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Proposal Id
             * Format: uuid
             */
            proposal_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Principal Id
             * Format: uuid
             */
            principal_id: string;
            /**
             * Decision
             * @enum {string}
             */
            decision: "accept" | "reject";
            /** Revision */
            revision: number;
            /** Review Hash */
            review_hash: string;
            /** Claim Id */
            claim_id: string | null;
            /** Endorsement Source Version Id */
            endorsement_source_version_id: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** ReviewProvenance */
        ReviewProvenance: {
            /**
             * Version
             * @default review-v1
             * @constant
             */
            version: "review-v1";
            /**
             * Origin
             * @constant
             */
            origin: "user_reviewed";
            /**
             * Proposal Id
             * Format: uuid
             */
            proposal_id: string;
            /**
             * Review Id
             * Format: uuid
             */
            review_id: string;
            /** Model */
            model: string;
            /** Extractor Version */
            extractor_version: string;
            /** Support */
            support: components["schemas"]["SupportingEvidence"][];
        };
        /** ReviewedVoiceInput */
        ReviewedVoiceInput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /** Content */
            content: string;
            /** As Of */
            as_of?: string | null;
            /**
             * Use Memory
             * @default true
             */
            use_memory: boolean;
            /**
             * Use Documents
             * @default false
             */
            use_documents: boolean;
            transcript: components["schemas"]["TranscriptInput"];
            /**
             * Review
             * @constant
             */
            review: "approve";
        };
        /** ScopeInput */
        ScopeInput: {
            /** Name */
            name: string;
            /**
             * Kind
             * @default project
             * @enum {string}
             */
            kind: "personal" | "project";
        };
        /** ScopeOutput */
        ScopeOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
            /**
             * Kind
             * @enum {string}
             */
            kind: "personal" | "project";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** SelfInput */
        SelfInput: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Entity Id
             * Format: uuid
             */
            entity_id: string;
        };
        /** SemanticDiagnostic */
        SemanticDiagnostic: {
            /**
             * State
             * @default disabled
             */
            state: string;
            /**
             * Reason
             * @default provider_disabled
             */
            reason: string;
            /** Namespace */
            namespace?: string | null;
            /** Model */
            model?: string | null;
            /** Model Digest */
            model_digest?: string | null;
            /** Dimensions */
            dimensions?: number | null;
            /**
             * Index Version
             * @default embeddinggemma-search-v1
             */
            index_version: string;
            /**
             * Ranking Version
             * @default lexical-first-rrf60-v1
             */
            ranking_version: string;
            /**
             * Eligible
             * @default 0
             */
            eligible: number;
            /**
             * Indexed
             * @default 0
             */
            indexed: number;
            /**
             * Query Ms
             * @default 0
             */
            query_ms: number;
            /**
             * Ranking Ms
             * @default 0
             */
            ranking_ms: number;
            /** Index Built At */
            index_built_at?: bigint | null;
            /** Min Similarity */
            min_similarity?: number | null;
        };
        /** SessionReset */
        SessionReset: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Session Id
             * Format: uuid
             */
            session_id: string;
        };
        /** SignalVector */
        SignalVector: {
            /** Warmth */
            warmth?: number | null;
            /** Focus */
            focus?: number | null;
            /** Energy */
            energy?: number | null;
            /** Playfulness */
            playfulness?: number | null;
            /** Concern */
            concern?: number | null;
        };
        /** SignalWrite */
        SignalWrite: {
            /**
             * Operation Id
             * Format: uuid
             */
            operation_id: string;
            /**
             * Session Id
             * Format: uuid
             */
            session_id: string;
            /**
             * Source Request Id
             * Format: uuid
             */
            source_request_id: string;
            /**
             * Reviewed
             * @constant
             */
            reviewed: true;
            /**
             * Reason
             * @enum {string}
             */
            reason: "user_selected" | "reviewed_model_signal";
            vector: components["schemas"]["SignalVector"];
        };
        /** SourcePin */
        SourcePin: {
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Version */
            version: number;
            /** Content Hash */
            content_hash: string;
            /** Span Start */
            span_start: number;
            /** Span End */
            span_end: number;
        };
        /** SourceVersionOutput */
        SourceVersionOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /** Version */
            version: number;
            /** Content */
            content: string;
            /** Content Hash */
            content_hash: string;
            /**
             * Trust Class
             * @enum {string}
             */
            trust_class: "user_explicit" | "model_generated";
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** StreamMetadata */
        StreamMetadata: {
            /**
             * State
             * @enum {string}
             */
            state: "running" | "cancel_requested" | "completed" | "failed" | "cancelled" | "interrupted";
            /** Sequence */
            sequence: number;
            /** Replay After */
            replay_after: number;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
            /** Finished At */
            finished_at: bigint | null;
        };
        /** StreamStatus */
        StreamStatus: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /** Attempt */
            attempt: number;
            /** Available */
            available: boolean;
            /**
             * Stream State
             * @enum {string}
             */
            stream_state: "running" | "cancel_requested" | "completed" | "failed" | "cancelled" | "interrupted";
            /** Sequence */
            sequence: number;
            /** Replay After */
            replay_after: number;
            /** Provisional */
            provisional: string;
            result: components["schemas"]["RequestOutput"];
        };
        /** SummarySection */
        SummarySection: {
            /** Text */
            text: string;
            /** Support */
            support: components["schemas"]["SourcePin"][];
        };
        /** SupersedeInput */
        SupersedeInput: {
            /**
             * Claim Id
             * Format: uuid
             */
            claim_id: string;
            /**
             * Source Version Id
             * Format: uuid
             */
            source_version_id: string;
            /** Span Start */
            span_start: number;
            /** Span End */
            span_end: number;
            /** Valid To */
            valid_to?: string | null;
            /** Subject Entity Id */
            subject_entity_id?: string | null;
            /** Value */
            value: string;
            /** Effective At */
            effective_at?: string | null;
        };
        /** SupportingEvidence */
        SupportingEvidence: {
            /**
             * Source Id
             * Format: uuid
             */
            source_id: string;
            /** Source Version */
            source_version: number;
            /**
             * Source Origin
             * @enum {string}
             */
            source_origin: "chat_event" | "user_note" | "imported_document";
            /**
             * Trust Class
             * @enum {string}
             */
            trust_class: "user_explicit" | "model_generated" | "imported_untrusted";
            evidence: components["schemas"]["EvidenceOutput"];
        };
        /** ToolReceiptOutput */
        ToolReceiptOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Approval Id
             * Format: uuid
             */
            approval_id: string;
            /**
             * Owner Id
             * Format: uuid
             */
            owner_id: string;
            /**
             * Run Id
             * Format: uuid
             */
            run_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Step Id
             * Format: uuid
             */
            step_id: string;
            /** Tool */
            tool: ("calculator" | "memory_lookup" | "source_lookup") | null;
            /** Tool Version */
            tool_version: string | null;
            /** Argument Hash */
            argument_hash: string | null;
            /** Preview Hash */
            preview_hash: string | null;
            /**
             * Outcome
             * @enum {string}
             */
            outcome: "completed" | "failed" | "unknown" | "revoked";
            /**
             * Origin
             * @constant
             */
            origin: "tool_result";
            /**
             * Trust Class
             * @constant
             */
            trust_class: "untrusted_tool_output";
            /** Result */
            result: {
                [key: string]: unknown;
            } | null;
            /** Error Code */
            error_code: string | null;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** ToolSpecOutput */
        ToolSpecOutput: {
            /**
             * Name
             * @enum {string}
             */
            name: "calculator" | "memory_lookup" | "source_lookup";
            /** Version */
            version: string;
            /** Description */
            description: string;
            /**
             * Classification
             * @constant
             */
            classification: "read_only";
            /**
             * Permission
             * @constant
             */
            permission: "authenticated_owner_scope";
            /** Allowed Targets */
            allowed_targets: "run_scope"[];
            /** Argument Schema */
            argument_schema: {
                [key: string]: unknown;
            };
            /** Result Schema */
            result_schema: {
                [key: string]: unknown;
            };
            /** Output Bytes */
            output_bytes: number;
            /** Max Calls */
            max_calls: number;
            /** Timeout Seconds */
            timeout_seconds: number;
            /**
             * Approval Required
             * @constant
             */
            approval_required: true;
        };
        /** TraceOutput */
        TraceOutput: {
            /** Version */
            version: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            plan: components["schemas"]["RetrievalPlanOutput"];
            /** Candidates */
            candidates: components["schemas"]["RetrievalCandidateOutput"][];
            /** Selected */
            selected: components["schemas"]["CitationOutput"][];
            /** Document Candidates */
            document_candidates?: components["schemas"]["DocumentCandidateOutput"][];
            /** Document Selected */
            document_selected?: components["schemas"]["DocumentCitationOutput"][];
            budget: components["schemas"]["RetrievalBudgetOutput"];
            /** Retrieval Ms */
            retrieval_ms: number;
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Created At
             * Format: int64
             */
            created_at: bigint;
        };
        /** TranscriptInput */
        TranscriptInput: {
            /**
             * Transcript Id
             * Format: uuid
             */
            transcript_id: string;
            /**
             * Engine Id
             * @constant
             */
            engine_id: "android_on_device";
            /** Engine Version */
            engine_version: string;
            /** Language */
            language: string;
            /** Duration Ms */
            duration_ms: number;
            /** Original Text */
            original_text: string;
        };
        /** UserOutput */
        UserOutput: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Name */
            name: string;
        };
        /** ValidationErrorOutput */
        ValidationErrorOutput: {
            /** Detail */
            detail: string | components["schemas"]["ValidationIssueOutput"][];
        };
        /** ValidationIssueOutput */
        ValidationIssueOutput: {
            /** Type */
            type: string;
            /** Loc */
            loc: (string | number)[];
            /** Msg */
            msg: string;
        };
        /** VoiceLineageOutput */
        VoiceLineageOutput: {
            /**
             * Request Id
             * Format: uuid
             */
            request_id: string;
            /**
             * Conversation Id
             * Format: uuid
             */
            conversation_id: string;
            /**
             * Scope Id
             * Format: uuid
             */
            scope_id: string;
            /**
             * Transcript Id
             * Format: uuid
             */
            transcript_id: string;
            /** Engine Id */
            engine_id: string;
            /** Engine Version */
            engine_version: string;
            /**
             * Engine Metadata
             * @default client_reported
             * @constant
             */
            engine_metadata: "client_reported";
            /** Language */
            language: string;
            /** Duration Ms */
            duration_ms: number;
            /** Original Text */
            original_text: string;
            /** Original Hash */
            original_hash: string;
            /**
             * Original Origin
             * @default asr_generated
             * @constant
             */
            original_origin: "asr_generated";
            /**
             * Original Trust
             * @default generated_interpretation
             * @constant
             */
            original_trust: "generated_interpretation";
            /** Reviewed Text */
            reviewed_text: string;
            /** Reviewed Hash */
            reviewed_hash: string;
            /**
             * Reviewed Origin
             * @default user_reviewed
             * @constant
             */
            reviewed_origin: "user_reviewed";
            /**
             * Endorsement Source Version Id
             * Format: uuid
             */
            endorsement_source_version_id: string;
            /**
             * Approved At
             * Format: int64
             */
            approved_at: bigint;
            /**
             * Audio Storage
             * @default not_received_by_server
             * @constant
             */
            audio_storage: "not_received_by_server";
            /** Audio Sha256 */
            audio_sha256?: null;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    me_v1_admin_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminMeOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    requests_v1_admin_requests_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
                owner_id?: string | null;
                request_id?: string | null;
                status?: ("running" | "completed" | "failed") | null;
                provider?: string | null;
                created_from?: bigint | null;
                created_to?: bigint | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminRequestsOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    request_detail_v1_admin_requests__owner_id___request_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                owner_id: string;
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminRequestDetailOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    providers_v1_admin_providers_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminProvidersOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    overview_v1_admin_overview_get: {
        parameters: {
            query?: {
                window_hours?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminOverviewOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    audits_v1_admin_audit_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
                actor_id?: string | null;
                action?: ("role.grant" | "role.revoke" | "monitor.me" | "monitor.overview" | "monitor.requests" | "monitor.request" | "monitor.providers" | "monitor.audit") | null;
                outcome?: ("allowed" | "denied" | "not_found" | "invalid" | "failed" | "granted" | "revoked" | "unchanged" | "rate_limited") | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AdminAuditsOutput"];
                };
            };
            /** @description Unauthorized */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Forbidden */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Too Many Requests */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    upload_v1_scopes__scope_id__documents_uploads__upload_id__post: {
        parameters: {
            query: {
                source_id: string;
                filename: string;
                available_from?: string | null;
                available_to?: string | null;
            };
            header?: never;
            path: {
                scope_id: string;
                upload_id: string;
            };
            cookie?: never;
        };
        /** @description Exact UTF-8 file bytes. No multipart, archives, PDF or remote URLs. */
        requestBody: {
            content: {
                "text/plain": string;
                "text/markdown": string;
            };
        };
        responses: {
            /** @description Same-ID receipt replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentUploadOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentUploadOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            408: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            415: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    uploads_v1_scopes__scope_id__document_uploads_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentUploadOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    upload_status_v1_document_uploads__upload_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                upload_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentUploadOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    versions_v1_documents__source_id__versions_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                source_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentUploadOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    version_v1_document_versions__source_version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                source_version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentVersionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    chunks_v1_document_versions__source_version_id__chunks_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                source_version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DocumentChunkOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    raw_v1_document_versions__source_version_id__raw_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                source_version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/octet-stream": string;
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    entities_v1_scopes__scope_id__entities_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    create_v1_scopes__scope_id__entities_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EntityInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    resolve_v1_scopes__scope_id__entities_resolve_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ResolveInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityResolutionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    self_link_v1_scopes__scope_id__entities_self_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SelfInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    audit_v1_scopes__scope_id__entity_audit_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    operation_v1_entity_operations__operation_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    entity_v1_entities__entity_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    aliases_v1_entities__entity_id__aliases_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AliasOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    add_alias_v1_entities__entity_id__aliases_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AliasInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    retire_alias_v1_entity_aliases__alias_id__retire_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                alias_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperationInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    rename_v1_entities__entity_id__rename_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RenameInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    preview_v1_entities__entity_id__merge_preview_get: {
        parameters: {
            query: {
                target_id: string;
            };
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MergePreviewOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    merge_v1_entities__entity_id__merge_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MergeInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    undo_v1_entities__entity_id__undo_merge_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                entity_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperationInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    link_v1_claims__claim_id__entity_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                claim_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LinkInput"];
            };
        };
        responses: {
            /** @description Identical operation replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EntityOperationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    extract_v1_scopes__scope_id__memory_extractions_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExtractionInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExtractionOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExtractionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    extraction_v1_memory_extractions__extraction_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                extraction_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExtractionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    inbox_v1_scopes__scope_id__memory_proposals_get: {
        parameters: {
            query?: {
                status?: ("pending" | "accepted" | "rejected") | null;
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProposalOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    detail_v1_memory_proposals__proposal_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                proposal_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProposalOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    edit_v1_memory_proposals__proposal_id__edit_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                proposal_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EditInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProposalOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    review_v1_memory_proposals__proposal_id__review_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                proposal_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ReviewInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReviewOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReviewOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    receipt_v1_memory_reviews__review_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                review_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReviewOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    tools_v1_tools_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolSpecOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    protocols_v1_agent_protocols_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProtocolOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    runs_v1_conversations__conversation_id__agent_runs_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AgentRunOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    create_v1_conversations__conversation_id__agent_runs_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AgentInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AgentRunOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AgentRunOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    detail_v1_agent_runs__run_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AgentRunOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    approve_v1_agent_runs__run_id__steps__step_id__approve_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                step_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApprovalInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    revoke_v1_agent_runs__run_id__steps__step_id__revoke_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
                step_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ApprovalInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    recover_v1_agent_runs__run_id__recover_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                run_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RecoverInput"];
            };
        };
        responses: {
            /** @description OK */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    receipt_v1_tool_receipts__receipt_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                receipt_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ToolReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    jobs_v1_scopes__scope_id__consolidation_jobs_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsolidationOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    enqueue_v1_scopes__scope_id__consolidation_jobs_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConsolidationInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsolidationOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsolidationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    job_v1_consolidation_jobs__job_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsolidationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    episodes_v1_scopes__scope_id__episodes_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EpisodeOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    episode_v1_episodes__episode_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                episode_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EpisodeOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    context_v1_scopes__scope_id__episode_contexts_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["EpisodeContextInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EpisodeContextOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EpisodeContextOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    frozen_context_v1_episode_contexts__request_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EpisodeContextOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    preference_v1_preferences__kind___target_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                kind: "account" | "scope" | "profile" | "conversation";
                target_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreferenceOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    write_v1_preferences__kind___target_id__post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                kind: "account" | "scope" | "profile" | "conversation";
                target_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PreferenceWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    inspect_v1_conversations__conversation_id__expression_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    signal_v1_conversations__conversation_id__expression_signals_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SignalWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    reset_v1_conversations__conversation_id__expression_reset_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SessionReset"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    receipt_v1_expression_receipts__operation_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ExpressionReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    snapshot_v1_requests__request_id__expression_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestExpressionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    state_v1_scopes__scope_id__learning_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningStateOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    configure_v1_scopes__scope_id__learning_config_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LearningConfigWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    observe_v1_scopes__scope_id__learning_observations_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ObservationWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    review_v1_scopes__scope_id__learning_reviews_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LearningReviewWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    reset_v1_scopes__scope_id__learning_reset_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LearningResetWrite"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Created */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    receipt_v1_learning_receipts__operation_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LearningReceiptOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    snapshot_v1_requests__request_id__learning_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestLearningOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    submit_v1_conversations__conversation_id__stream_requests_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChatInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StreamStatus"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    status_v1_requests__request_id__stream_status_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StreamStatus"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    cancel_v1_requests__request_id__cancel_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CancelInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CancelReceipt"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    stream_v1_requests__request_id__stream_get: {
        parameters: {
            query: {
                attempt: number;
                after?: number;
            };
            header?: {
                "last-event-id"?: string | null;
            };
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "text/event-stream": string;
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    submit_v1_conversations__conversation_id__voice_requests_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ReviewedVoiceInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StreamStatus"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    get_v1_requests__request_id__voice_input_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VoiceLineageOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    list_inputs_v1_conversations__conversation_id__voice_inputs_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["VoiceLineageOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    live_health_live_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LiveOutput"];
                };
            };
        };
    };
    ready_health_ready_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReadyOutput"];
                };
            };
            /** @description Service Unavailable */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    me_v1_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UserOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    capabilities_v1_capabilities_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CapabilitiesOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    personalities_v1_personalities_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PersonalityOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    create_personality_v1_personalities_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PersonalityInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PersonalityOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    conversations_v1_conversations_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    create_conversation_v1_conversations_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConversationInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    conversation_v1_conversations__conversation_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConversationOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    upgrade_prompt_v1_conversations__conversation_id__prompt_upgrade_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PromptUpgradeOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    events_v1_conversations__conversation_id__events_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["EventOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    chat_v1_conversations__conversation_id__messages_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                conversation_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChatInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            502: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    request_status_v1_requests__request_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RequestOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    request_retrieval_v1_requests__request_id__retrieval_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                request_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TraceOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    scopes_v1_scopes_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScopeOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    create_scope_v1_scopes_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ScopeInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScopeOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    scope_v1_scopes__scope_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ScopeOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    retrieve_memory_v1_scopes__scope_id__retrieve_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RetrieveInput"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RetrievalOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    rebuild_semantic_index_v1_scopes__scope_id__semantic_index_rebuild_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RebuildOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
        };
    };
    create_note_v1_scopes__scope_id__notes_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["NoteInput"];
            };
        };
        responses: {
            /** @description Same-ID replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    source_versions_v1_scopes__scope_id__source_versions_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    source_version_v1_source_versions__source_version_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                source_version_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SourceVersionOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    claims_v1_scopes__scope_id__claims_get: {
        parameters: {
            query?: {
                as_of?: string | null;
                history?: boolean;
                subject?: string | null;
                predicate?: string | null;
                limit?: number;
                offset?: number;
            };
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"][];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    create_claim_v1_scopes__scope_id__claims_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                scope_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ClaimInput"];
            };
        };
        responses: {
            /** @description Same-ID replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    claim_v1_claims__claim_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                claim_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
    supersede_claim_v1_claims__claim_id__supersede_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                claim_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SupersedeInput"];
            };
        };
        responses: {
            /** @description Same-ID replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ClaimOutput"];
                };
            };
            /** @description Sanitized error code */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized error code */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorOutput"];
                };
            };
            /** @description Sanitized validation issues or error code; input is omitted */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValidationErrorOutput"];
                };
            };
        };
    };
}
