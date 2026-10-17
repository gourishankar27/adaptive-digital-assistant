import { describe, expect, it, vi } from 'vitest';
import { HttpAdminApi } from '../src/api/admin';
import { normalizeServer, type FetchTransport } from '../src/api/http';
import { owner } from './mock-admin';

describe('private origin login preflight', () => {
  it('checks readiness without a credential before sending admin authentication', async () => {
    const transport = vi.fn<FetchTransport>(async path => path === '/health/ready'
      ? new Response('{"status":"ready","schema":"0015"}', { headers: { 'Content-Type': 'application/json' } })
      : new Response(JSON.stringify({ id: owner, permissions: ['monitoring:read'] }), { headers: { 'Content-Type': 'application/json' } }));
    await new HttpAdminApi(window.location.origin, 'synthetic-only', transport).adminMe();
    expect(transport.mock.calls[0][0]).toBe('/health/ready');
    expect(transport.mock.calls[0][1].headers).not.toHaveProperty('Authorization');
    expect(transport.mock.calls[1][1].headers).toHaveProperty('Authorization', 'Bearer synthetic-only');
  });
  it.each([302, 503])('never authenticates after a failed %s preflight', async status => {
    const transport = vi.fn<FetchTransport>(async () => new Response('{}', { status, headers: { 'Content-Type': 'application/json', Location: 'https://elsewhere.example' } }));
    await expect(new HttpAdminApi(window.location.origin, 'synthetic-only', transport).adminMe()).rejects.toBeDefined();
    expect(transport).toHaveBeenCalledTimes(1);
    expect(transport.mock.calls[0][1].headers).not.toHaveProperty('Authorization');
    expect(transport.mock.calls[0][1].redirect).toBe('error');
  });
  it('rejects paths that URL normalization would silently erase', () => {
    for (const suffix of ['/../', '/%2e%2e/', '/?', '/#']) expect(() => normalizeServer(window.location.origin + suffix)).toThrow();
  });
  it.each(['<html>ready</html>', '{"status":"ready","schema":"internal"}', ' '.repeat(2048)])('does not authenticate to malformed readiness data', async body => {
    const transport = vi.fn<FetchTransport>(async () => new Response(body, { headers: { 'Content-Type': 'application/json' } }));
    await expect(new HttpAdminApi(window.location.origin, 'synthetic-only', transport).adminMe()).rejects.toMatchObject({ failure: { kind: 'incompatible' } });
    expect(transport).toHaveBeenCalledTimes(1);
    expect(transport.mock.calls[0][1].headers).not.toHaveProperty('Authorization');
  });
  it('fences a disconnected preflight before its late response can send credentials', async () => {
    let release!: (value: Response) => void;
    const transport = vi.fn<FetchTransport>(async () => new Promise(resolve => { release = resolve; }));
    const api = new HttpAdminApi(window.location.origin, 'synthetic-only', transport);
    const login = api.adminMe(); api.disconnect();
    release(new Response('{"status":"ready","schema":"0015"}', { headers: { 'Content-Type': 'application/json' } }));
    await expect(login).rejects.toMatchObject({ failure: { kind: 'cancelled' } });
    expect(transport).toHaveBeenCalledTimes(1);
  });
});
