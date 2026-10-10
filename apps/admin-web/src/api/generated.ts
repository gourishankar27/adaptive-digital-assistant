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
        /** CapabilitiesOutput */
        CapabilitiesOutput: {
            /**
             * Admin Monitoring
             * @default false
             */
            admin_monitoring: boolean;
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
        };
        /** CitationOutput */
        CitationOutput: {
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
        /** LiveOutput */
        LiveOutput: {
            /**
             * Status
             * @constant
             */
            status: "ok";
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
            /** Citation Warnings */
            citation_warnings: string[];
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
            budget: components["schemas"]["RetrievalBudgetOutput"];
            /** Retrieval Ms */
            retrieval_ms: number;
        };
        /** RetrievalPlanOutput */
        RetrievalPlanOutput: {
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
            /** Value */
            value: string;
            /** Effective At */
            effective_at?: string | null;
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
