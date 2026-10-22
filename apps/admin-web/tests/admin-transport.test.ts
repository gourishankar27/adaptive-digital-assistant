import { describe, expect, it, vi } from 'vitest';
import { decodeReflection, decodeDetail, decodeMetadata, decodeOverview, decodeScheduling, HttpAdminApi } from '../src/api/admin';
import { ContractError, parseWire } from '../src/api/decode';
import { amount, timestamp } from '../src/monitor-query';
import { detail, otherOwner, overview, owner, requestId } from './mock-admin';
const wire = (value: unknown) => JSON.stringify(value, (_, v) => typeof v === 'bigint' ? Number(v) : v);
describe('monitoring allowlist and lossless adapter', () => {
  it('projects reflection safety budgets without private artifacts or forged counts', () => {
    const safe = decodeReflection({ globally_enabled: false, summary_generation: false, suspended_model_class: true,
      policies_enabled: 2, runs: { completed: 3, private_text: 'private' }, artifacts: { kept: 1, question: 'private' },
      maximum_nightly_seconds: 600, maximum_jobs: 3, minimum_idle_seconds: 900, updated_at: 9223372036854775807n,
      source_quotes: ['private'], owner_id: owner });
    expect(safe.runs.completed).toBe(3); expect(safe.updated_at).toBe(9223372036854775807n);
    expect(safe).not.toHaveProperty('owner_id'); expect(safe.runs).not.toHaveProperty('private_text'); expect(safe.artifacts).not.toHaveProperty('question');
    expect(() => decodeReflection({ ...safe, maximum_jobs: 4 })).toThrow(ContractError);
    expect(() => decodeReflection({ ...safe, artifacts: { kept: -1 } })).toThrow(ContractError);
  });
  it('projects scheduling counts and drops text, devices and forged state keys', () => {
    const safe = decodeScheduling({ globally_enabled: false, schedules: { active: 2, text: 'private' }, occurrences: { failed: 1, payload: 'private' }, inbox: { unread: 3, topic: 'private' }, updated_at: 9223372036854775807n, registrations: ['private'] });
    expect(safe.schedules.active).toBe(2); expect(safe.occurrences.failed).toBe(1); expect(safe.inbox.unread).toBe(3);
    expect(safe.updated_at).toBe(9223372036854775807n); expect(safe).not.toHaveProperty('registrations');
    expect(safe.schedules).not.toHaveProperty('text'); expect(safe.occurrences).not.toHaveProperty('payload'); expect(safe.inbox).not.toHaveProperty('topic');
    expect(() => decodeScheduling({ ...safe, schedules: { active: -1 } })).toThrow(ContractError);
  });
  it('projects measured stream state without private deltas or receipts', () => {
    const safe = decodeDetail({ ...detail, stream: { state: 'cancel_requested', sequence: 18, replay_after: 0, created_at: 9223372036854775807n, finished_at: null, provisional: 'private', messages: ['private'], cancel_receipt: 'private' } });
    expect(safe.stream?.state).toBe('cancel_requested'); expect(safe.stream?.sequence).toBe(18);
    expect(safe.stream?.created_at).toBe(9223372036854775807n);
    expect(JSON.stringify(safe.stream, (_, value) => typeof value === 'bigint' ? value.toString() : value)).not.toContain('private');
    expect(decodeDetail(detail).stream).toBeNull();
  });
  it('projects maintenance metadata, preserves times and excludes generated/private input', () => {
    const job = { id: requestId, owner_id: owner, scope_id: requestId, kind: 'episode', status: 'queued', checkpoint: 'reserved', version: 'consolidation-v1', attempt: 0, created_at: 9223372036854775807n, started_at: null, finished_at: null, elapsed_ms: null, input: 'private', snapshot: 'private', summary: 'private' };
    const safe = decodeOverview({ ...overview, consolidation_job_counts: { queued: 1, running: 0, completed: 0, failed: 0, stale: 0, quotes: ['private'] }, consolidation_jobs: [job] });
    expect(safe.consolidation_jobs?.[0].created_at).toBe(9223372036854775807n);
    expect(safe.consolidation_jobs?.[0].started_at).toBeNull(); expect(safe.consolidation_jobs?.[0]).not.toHaveProperty('input');
    expect(safe.consolidation_jobs?.[0]).not.toHaveProperty('summary'); expect(safe.consolidation_job_counts).not.toHaveProperty('quotes');
    expect(decodeOverview(overview).consolidation_jobs).toBeNull(); expect(decodeOverview(overview).consolidation_job_counts).toBeNull();
  });
  it('keeps tool monitoring to state counts and supports older servers', () => {
    const safe = decodeOverview({ ...overview, agent_run_counts: { running: 1, pending_approval: 2, completed: 3, failed: 0, unknown: 0, arguments: 'private', results: ['private'] } });
    expect(safe.agent_run_counts).toEqual({ running: 1, pending_approval: 2, completed: 3, failed: 0, unknown: 0 });
    expect(decodeOverview(overview).agent_run_counts).toBeNull();
    expect(() => decodeOverview({ ...overview, agent_run_counts: { running: -1 } })).toThrow(ContractError);
  });
  it('projects proposal counts without retaining private reviews or excerpts', () => {
    const result = decodeOverview({ ...overview, memory_proposal_counts: { pending: 2, accepted: 1, rejected: 0, review_text: 'private', quotes: ['private'] } });
    expect(result.memory_proposal_counts).toEqual({ pending: 2, accepted: 1, rejected: 0 });
    expect(decodeOverview(overview).memory_proposal_counts).toBeNull();
    expect(() => decodeOverview({ ...overview, memory_proposal_counts: { pending: -1, accepted: 0, rejected: 0 } })).toThrow(ContractError);
  });
  it('describes read-only filter failures without exposing bodies or implying submission', async () => {
    const api = new HttpAdminApi(window.location.origin, 'credential', async () => new Response('{"detail":"private input"}', { status: 422, headers: { 'Content-Type': 'application/json' } }));
    await expect(api.requests({})).rejects.toMatchObject({ failure: { kind: 'validation', message: 'The server rejected the monitoring filters. Check the IDs, page and date window.' } });
  });
  it('drops private additive fields recursively and distinguishes null/zero/unknown', () => {
    const safe = decodeDetail({ ...detail, user_text: 'private', prompt: 'private', retrieval: { available: false, quotes: ['private'] } });
    expect(safe).not.toHaveProperty('user_text'); expect(safe.retrieval).not.toHaveProperty('quotes'); expect(safe.input_tokens).toBeNull(); expect(safe.output_tokens).toBe(0);
    expect(decodeMetadata({ ...detail, status: 'queued_v2' }).status).toBe('queued_v2'); expect(amount(null)).toBe('Not recorded'); expect(amount(0)).toBe('0');
  });
  it('preserves full int64 times and rejects invalid types/admission', () => {
    const decoded = decodeDetail(parseWire(wire(detail).replace('"created_at":0', '"created_at":9223372036854775807')));
    expect(decoded.created_at).toBe(9223372036854775807n); expect(timestamp(decoded.created_at)).toContain('9223372036854775807');
    expect(() => decodeMetadata({ ...detail, attempt: -1 })).toThrow(ContractError); expect(() => decodeOverview({ ...overview, generation_admission: { ...overview.generation_admission, workers: 2 } })).toThrow(ContractError);
    expect(() => decodeOverview({ ...overview, provider_health: { ...overview.provider_health, reachability: ['reachable'] } })).toThrow(ContractError);
  });
  it('uses real admin routes, safe filters and rejects an owner-mismatched detail', async () => {
    const transport = vi.fn(async () => new Response(wire(detail), { headers: { 'Content-Type': 'application/json' } })), api = new HttpAdminApi(window.location.origin, 'credential', transport);
    await api.detail(owner, requestId); expect(transport).toHaveBeenCalledWith(`/v1/admin/requests/${owner}/${requestId}`, expect.objectContaining({ cache: 'no-store', redirect: 'error', credentials: 'omit' }));
    await expect(api.detail(otherOwner, requestId)).rejects.toMatchObject({ failure: { kind: 'incompatible' } });
    expect(() => api.requests({ token: 'secret' })).toThrow(ContractError); expect(() => api.overview(169)).toThrow(ContractError);
  });
});
