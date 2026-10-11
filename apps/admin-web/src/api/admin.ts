import type { Dto } from './types';
import { ContractError, millis, record, uuid } from './decode';
import { HttpAdaApi } from './http';
import { AdaError, type FailureKind } from './errors';

export type AdminMe = Dto<'AdminMeOutput'>;
export type Overview = Dto<'AdminOverviewOutput'>;
export type Providers = Dto<'AdminProvidersOutput'>;
export type RequestMetadata = Omit<Dto<'AdminRequestOutput'>, 'status'> & { status: string };
export type RequestDetail = RequestMetadata & { retrieval: Dto<'RetrievalSummary'> };
export type RequestPage = Omit<Dto<'AdminRequestsOutput'>, 'items'> & { items: RequestMetadata[] };
export type AuditPage = Dto<'AdminAuditsOutput'>;
export type Filters = Record<string, string>;
export interface AdminApi {
  adminMe(signal?: AbortSignal): Promise<AdminMe>;
  overview(hours: number, signal?: AbortSignal): Promise<Overview>;
  providers(signal?: AbortSignal): Promise<Providers>;
  requests(filters: Filters, signal?: AbortSignal): Promise<RequestPage>;
  detail(owner: string, request: string, signal?: AbortSignal): Promise<RequestDetail>;
  audit(filters: Filters, signal?: AbortSignal): Promise<AuditPage>;
  disconnect(): void;
}

type Decoder = (v: unknown) => unknown;
const text = (v: unknown): string => { if (typeof v !== 'string' || v.length > 200 || [...v].some(char => char.charCodeAt(0) < 32)) throw new ContractError(); return v; };
const bool: Decoder = v => { if (typeof v !== 'boolean') throw new ContractError(); return v; };
const count: Decoder = v => { if (typeof v !== 'number' || !Number.isSafeInteger(v) || v < 0) throw new ContractError(); return v; };
const nullable = (decode: Decoder): Decoder => v => v == null ? null : decode(v);
const list = (decode: Decoder): Decoder => v => { if (!Array.isArray(v) || v.length > 100) throw new ContractError(); return v.map(decode); };
const shape = <T,>(value: unknown, fields: Record<string, Decoder>): T => {
  const input = record(value), output: Record<string, unknown> = {};
  // Project only permitted fields: unknown/private extensions never enter caches.
  for (const [key, decode] of Object.entries(fields)) output[key] = decode(input[key]);
  return output as T;
};
const health: Decoder = v => shape(v, { reachability: value => { const state = text(value); return ['reachable', 'unreachable', 'unknown'].includes(state) ? state : 'unknown'; }, model_available: nullable(bool), checked_at: nullable(millis), error_code: nullable(text), cache_seconds: count });
const admission: Decoder = v => {
  const result = shape<Dto<'AdmissionOutput'>>(v, { max_parallel: count, process_available_slots: count, process_active_slots: count, workers: count });
  if (result.workers !== 1 || result.max_parallel < 1 || result.process_available_slots + result.process_active_slots !== result.max_parallel) throw new ContractError();
  return result;
};
const requestFields = { owner_id: uuid, request_id: uuid, conversation_id: uuid, scope_id: uuid, status: text, attempt: count, provider: text, model: text, created_at: millis, started_at: millis, finished_at: nullable(millis), observed_at: millis, elapsed_ms: nullable(millis), error_code: nullable(text), input_tokens: nullable(count), output_tokens: nullable(count) };
export const decodeMetadata = (v: unknown) => shape<RequestMetadata>(v, requestFields);
export const decodeAdminMe = (v: unknown) => {
  const result = shape<AdminMe>(v, { id: uuid, permissions: list(text) });
  if (!result.permissions.includes('monitoring:read')) throw new ContractError();
  return result;
};
export const decodeOverview = (v: unknown) => shape<Overview>(v, { consolidation_job_counts: nullable(value => shape(value, { queued: count, running: count, completed: count, failed: count, stale: count })), consolidation_jobs: nullable(list(value => shape(value, { id: uuid, owner_id: uuid, scope_id: uuid, kind: text, status: text, checkpoint: text, version: text, attempt: count, created_at: millis, started_at: nullable(millis), finished_at: nullable(millis), elapsed_ms: nullable(count) }))), window_hours: count, created_from: millis, updated_at: millis, requests: value => shape(value, { running: count, completed: count, failed: count }), agent_run_counts: nullable(value => shape(value, { running: count, pending_approval: count, completed: count, failed: count, unknown: count })), memory_proposal_counts: nullable(value => shape(value, { pending: count, accepted: count, rejected: count })), input_tokens: nullable(count), output_tokens: nullable(count), input_tokens_known_requests: count, output_tokens_known_requests: count, database_ready: bool, schema_version: nullable(text), provider_health: health, generation_admission: admission });
export const decodeProviders = (v: unknown) => shape<Providers>(v, { provider: text, model: text, health, generation_admission: admission, context_tokens: count, output_tokens: count, timeout_seconds: count });
export const decodeRequestPage = (v: unknown) => shape<RequestPage>(v, { items: list(decodeMetadata), limit: count, offset: count, has_more: bool, created_from: millis, created_to: millis, updated_at: millis });
export const decodeDetail = (v: unknown) => shape<RequestDetail>(v, { ...requestFields, retrieval: value => shape(value, { available: bool, candidate_count: nullable(count), selected_count: nullable(count), retrieval_ms: nullable(count), memory_limit_bytes: nullable(count), memory_used_bytes: nullable(count), prompt_limit_bytes: nullable(count), prompt_used_bytes: nullable(count), history_pairs_omitted: nullable(count), candidate_pool_truncated: nullable(bool) }) });
export const decodeAuditPage = (v: unknown) => shape<AuditPage>(v, { items: list(value => shape(value, { id: millis, actor_id: uuid, actor_kind: text, action: text, target_owner_id: nullable(uuid), target_request_id: nullable(uuid), outcome: text, created_at: millis })), limit: count, offset: count, has_more: bool, retention_days: count, max_rows: count, updated_at: millis });

function query(filters: Filters, allowed: string[]): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (!allowed.includes(key) || value.length > 80) throw new ContractError();
    if (value) params.set(key, value);
  }
  return params.toString() ? `?${params}` : '';
}
export class HttpAdminApi extends HttpAdaApi implements AdminApi {
  protected override async get<T>(path: string, decode: (value: unknown) => T, signal?: AbortSignal): Promise<T> {
    try { return await super.get(path, decode, signal); }
    catch (error) {
      const messages: Partial<Record<FailureKind, string>> = {
        authentication: 'The credential is invalid or expired. Sign in with a current token.',
        forbidden: 'Access denied. This account no longer has the monitoring permission.',
        'not-found': 'The monitoring record is unavailable to this operator.',
        validation: 'The server rejected the monitoring filters. Check the IDs, page and date window.',
        timeout: 'The monitoring read timed out. Refresh when the server is reachable.',
        cancelled: 'Stopped waiting for monitoring data.',
        provider: 'The monitoring upstream is unavailable. Refresh when the server is reachable.',
      };
      if (error instanceof AdaError && messages[error.failure.kind]) throw new AdaError({ ...error.failure, message: messages[error.failure.kind]! });
      throw error;
    }
  }
  adminMe(signal?: AbortSignal) { return this.get('/v1/admin/me', decodeAdminMe, signal); }
  overview(hours: number, signal?: AbortSignal) {
    if (!Number.isInteger(hours) || hours < 1 || hours > 168) throw new ContractError();
    return this.get(`/v1/admin/overview?window_hours=${hours}`, decodeOverview, signal);
  }
  providers(signal?: AbortSignal) { return this.get('/v1/admin/providers', decodeProviders, signal); }
  requests(filters: Filters, signal?: AbortSignal) { return this.get('/v1/admin/requests' + query(filters, ['owner_id', 'request_id', 'status', 'provider', 'created_from', 'created_to', 'limit', 'offset']), decodeRequestPage, signal); }
  detail(owner: string, request: string, signal?: AbortSignal) {
    const expectedOwner = uuid(owner).toLowerCase(), expectedRequest = uuid(request).toLowerCase();
    return this.get(`/v1/admin/requests/${expectedOwner}/${expectedRequest}`, value => {
      const item = decodeDetail(value);
      if (item.owner_id.toLowerCase() !== expectedOwner || item.request_id.toLowerCase() !== expectedRequest) throw new ContractError();
      return item;
    }, signal);
  }
  audit(filters: Filters, signal?: AbortSignal) { return this.get('/v1/admin/audit' + query(filters, ['actor_id', 'action', 'outcome', 'limit', 'offset']), decodeAuditPage, signal); }
}
