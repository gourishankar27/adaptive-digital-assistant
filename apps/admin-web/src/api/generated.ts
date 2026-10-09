export interface paths {
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
        /** CapabilitiesOutput */
        CapabilitiesOutput: {
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
