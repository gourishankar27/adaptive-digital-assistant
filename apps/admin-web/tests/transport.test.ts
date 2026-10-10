import { beforeEach, describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import current from '../../../contracts/fixtures/request-current.json';
import legacy from '../../../contracts/fixtures/request-legacy.json';
import capabilities from '../../../contracts/fixtures/capabilities-current.json';
import { codePointOffset, ContractError, decodeCapabilities, decodeRequest, millis, parseWire, sourceForLabel } from '../src/api/decode';
import { observeRequestState } from '../src/api/types';
import { HttpAdaApi, normalizeServer, type FetchTransport } from '../src/api/http';
import { AdaError, httpFailure, retryAfter } from '../src/api/errors';
import { ownerA } from './mock-api';

const fixtureText = (name: string) => readFileSync(resolve(process.cwd(), '../../contracts/fixtures', `${name}.json`), 'utf8');
const json = (value: unknown, status = 200, headers: Record<string, string> = {}) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json', ...headers } });
const origin = 'http://localhost:3000';
beforeEach(() => { window.history.replaceState(null, '', '/'); });

describe('existing contract compatibility', () => {
  it('decodes captured current and missing-trace requests, preserving request-owned source mapping', () => {
    const present = decodeRequest(parseWire(fixtureText('request-current')));
    expect(present.request_id).toBe(current.request_id);
    expect(present.citations[0].valid_from).toBe(1735689600000n);
    expect(sourceForLabel(present, 'M1')?.evidence.quote).toBe(current.citations[0].evidence.quote);
    expect(sourceForLabel(present, 'M99')).toBeUndefined();
    const old = decodeRequest(parseWire(fixtureText('request-legacy')));
    expect(old.request_id).toBe(legacy.request_id);
    expect(old.citations).toEqual([]);
    expect(old.citation_warnings).toContain('unknown_label:M1');
  });
  it('ignores additive fields; absent legacy citation/tokens fields stay absent or empty', () => {
    const old = { ...legacy, response: undefined, citations: undefined, citation_warnings: undefined, input_tokens: undefined, output_tokens: undefined, future: { unexpected: true } };
    expect(decodeRequest(old)).toMatchObject({ response: null, citations: [], citation_warnings: [], input_tokens: null, output_tokens: null });
    expect(decodeCapabilities({ ...capabilities, future: true, memory_writes: 'future_mode' }).memory_writes).toBe('future_mode');
    const withFraction = JSON.stringify(capabilities).replace(/}$/, ',"future_metric":0.123456789012345678901}');
    expect(decodeCapabilities(parseWire(withFraction)).api_version).toBe('v1');
  });
  it('preserves unknown enums without converting a future request state to completed', () => {
    const request = decodeRequest({ ...current, status: 'queued_v2', citations: [{ ...current.citations[0], kind: 'future_kind', origin: 'future_origin' }] });
    expect(observeRequestState(request.status)).toEqual({ kind: 'unknown', value: 'queued_v2' });
    expect(request.citations[0].kind).toBe('future_kind');
    expect(() => decodeCapabilities({ ...capabilities, api_version: 'v2' })).toThrow(ContractError);
    expect(() => decodeCapabilities({ ...capabilities, authority: 'client' })).toThrow(ContractError);
  });
  it('preserves full int64 milliseconds and rejects out-of-range or already-rounded numbers', () => {
    expect(millis(parseWire('9223372036854775807'))).toBe(9223372036854775807n);
    expect(millis(parseWire('-9223372036854775808'))).toBe(-9223372036854775808n);
    expect(() => millis(parseWire('9223372036854775808'))).toThrow(ContractError);
    expect(() => millis(Number('9223372036854775807'))).toThrow(ContractError);
    expect(() => millis(1.2)).toThrow(ContractError);
  });
  it('converts UTF-16 selections and rejects boundaries inside a surrogate pair', () => {
    expect(codePointOffset('a🧭b', 3)).toBe(2);
    expect(() => codePointOffset('a🧭b', 2)).toThrow(ContractError);
    expect(() => decodeRequest({ ...current, citations: [{ ...current.citations[0], evidence: { ...current.citations[0].evidence, quote: '🧭', span_start: 0, span_end: 1 } }] })).not.toThrow();
  });
});

describe('real HTTP adapter', () => {
  it('sends credentials only to relative same-origin ADA paths, with redirects blocked', async () => {
    const transport = vi.fn<FetchTransport>(async () => json({ id: ownerA, name: 'Synthetic account' }));
    const api = new HttpAdaApi(origin, 'synthetic-test-credential', transport);
    expect(await api.me()).toEqual({ id: ownerA, name: 'Synthetic account' });
    expect(transport).toHaveBeenCalledWith('/v1/me', expect.objectContaining({ method: 'GET', redirect: 'error', credentials: 'omit', cache: 'no-store' }));
    expect(() => normalizeServer('http://another-host:8000')).toThrow(ContractError);
    expect(() => normalizeServer(`${origin}/?token=secret`)).toThrow(ContractError);
    expect(() => normalizeServer('http://user:pass@localhost:3000')).toThrow(ContractError);
    expect(() => new HttpAdaApi(origin, 'bad\ncredential', transport)).toThrow(ContractError);
  });
  it('401 destroys the credential and prevents further requests without retries', async () => {
    const transport = vi.fn<FetchTransport>(async () => json({ detail: 'private credential should never appear' }, 401));
    const api = new HttpAdaApi(origin, 'synthetic-test-credential', transport);
    await expect(api.me()).rejects.toMatchObject({ failure: { kind: 'authentication', status: 401 } });
    await expect(api.me()).rejects.toMatchObject({ failure: { kind: 'authentication' } });
    expect(transport).toHaveBeenCalledTimes(1);
  });
  it.each([403, 404, 409, 413, 422, 429, 503, 502, 500])('maps %s without displaying private response bodies', async status => {
    const transport: FetchTransport = async () => json({ detail: [{ msg: 'private input/token/quote', input: 'private' }] }, status, { 'Retry-After': '3' });
    const api = new HttpAdaApi(origin, 'synthetic-test-credential', transport);
    try { await api.me(); throw new Error('expected failure'); }
    catch (error) {
      expect(error).toBeInstanceOf(AdaError);
      expect((error as AdaError).message).not.toContain('private');
      expect((error as AdaError).failure.retryAfterMs).toBe(3000);
    }
  });
  it.each(['database_not_ready', 'monitoring_unavailable'])('explains a known %s failure without exposing its body', async detail => {
    const transport: FetchTransport = async () => json({ detail, private_input: 'SYNTHETIC_PRIVATE_VALUE' }, 503, { 'Retry-After': '3' });
    try { await new HttpAdaApi(origin, 'synthetic-test-credential', transport).me(); throw new Error('expected failure'); }
    catch (error) {
      expect(error).toBeInstanceOf(AdaError);
      expect((error as AdaError).failure).toMatchObject({ kind: 'server', status: 503, outcome: 'unavailable', retryAfterMs: 3000 });
      expect((error as AdaError).message).toContain('migrations');
      expect((error as AdaError).message).not.toContain('SYNTHETIC_PRIVATE_VALUE');
    }
  });
  it.each([
    { body: '{"detail":"SYNTHETIC_PRIVATE_VALUE"}', type: 'application/json' },
    { body: '{"detail":"database_not_ready"}', type: 'text/html' },
    { body: '{"detail":"database_not_ready","extra":"' + 'x'.repeat(2048) + '"}', type: 'application/json' },
    { body: '{"detail":', type: 'application/json' },
  ])('keeps an unknown, malformed, non-JSON or oversized 503 generic', async ({ body, type }) => {
    const transport: FetchTransport = async () => new Response(body, { status: 503, headers: { 'Content-Type': type } });
    await expect(new HttpAdaApi(origin, 'synthetic-test-credential', transport).me()).rejects.toMatchObject({ failure: { kind: 'busy', status: 503, message: 'The server is unavailable or busy. Wait before retrying.' } });
  });
  it('parses Retry-After seconds/date and keeps uncertain outcomes explicit', () => {
    expect(retryAfter('3')).toBe(3000);
    expect(retryAfter('Thu, 08 Oct 2026 12:00:03 GMT', Date.parse('2026-10-08T12:00:00Z'))).toBe(3000);
    expect(retryAfter('garbage')).toBeUndefined();
    expect(httpFailure(503).outcome).toBe('unknown');
  });
  it('timeouts, network errors and non-JSON responses never become fixture success', async () => {
    const waiting: FetchTransport = async (_, init) => new Promise((_, reject) => init.signal?.addEventListener('abort', () => reject(new DOMException('cancelled', 'AbortError'))));
    await expect(new HttpAdaApi(origin, 'synthetic', waiting, 5).me()).rejects.toMatchObject({ failure: { kind: 'timeout', outcome: 'unknown' } });
    await expect(new HttpAdaApi(origin, 'synthetic', async () => { throw new Error('private server detail'); }).me()).rejects.toMatchObject({ failure: { kind: 'unreachable' } });
    await expect(new HttpAdaApi(origin, 'synthetic', async () => new Response('<html>private</html>')).me()).rejects.toMatchObject({ failure: { kind: 'incompatible' } });
  });
  it('decodes canonical request JSON through HTTP and keeps matching original IDs', async () => {
    const transport = vi.fn<FetchTransport>(async () => json(current));
    const request = await new HttpAdaApi(origin, 'synthetic', transport).requestStatus(current.request_id);
    expect(request.request_id).toBe(current.request_id);
    expect(request.citations).toHaveLength(1);
    expect(transport.mock.calls[0][0]).toBe(`/v1/requests/${current.request_id}`);
  });
  it('refuses mismatched persisted request IDs rather than reconciling another response', async () => {
    const transport: FetchTransport = async () => json({ ...current, request_id: legacy.request_id });
    await expect(new HttpAdaApi(origin, 'synthetic', transport).requestStatus(current.request_id)).rejects.toMatchObject({ failure: { kind: 'incompatible' } });
  });
});
