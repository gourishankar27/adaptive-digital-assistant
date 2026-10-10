import { describe, expect, it, vi } from 'vitest';
import { decodeDetail, decodeMetadata, decodeOverview, HttpAdminApi } from '../src/api/admin';
import { ContractError, parseWire } from '../src/api/decode';
import { amount, timestamp } from '../src/monitor-query';
import { detail, otherOwner, overview, owner, requestId } from './mock-admin';
const wire = (value: unknown) => JSON.stringify(value, (_, v) => typeof v === 'bigint' ? Number(v) : v);
describe('monitoring allowlist and lossless adapter', () => {
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
