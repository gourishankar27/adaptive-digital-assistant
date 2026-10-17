import { describe, expect, it, vi } from 'vitest';
import { browserAuth, CookieAdminApi } from '../src/api/password';
import { owner, otherOwner } from './mock-admin';

describe('password browser boundary', () => {
  it('rejects private responses when another tab changes the cookie owner', async () => {
    const transport = vi.fn(async (path: string) => new Response(path === '/health/ready' ? '{"status":"ready","schema":"0016"}' : path === '/v1/admin/me' ? JSON.stringify({ id: owner, permissions: ['monitoring:read'] }) : '{}', { headers: { 'Content-Type': 'application/json', 'X-ADA-Owner': path === '/v1/admin/me' ? owner : otherOwner } }));
    const api = new CookieAdminApi(window.location.origin, transport);
    expect((await api.adminMe()).id).toBe(owner);
    await expect(api.overview(24)).rejects.toMatchObject({ failure: { kind: 'authentication' } });
  });
  it('refuses password transmission over development HTTP', async () => {
    const transport = vi.fn();
    await expect(browserAuth(window.location.origin, 'login', { username: 'synthetic', password: 'public fixture passphrase' }, transport)).rejects.toThrow();
    expect(transport).not.toHaveBeenCalled();
  });
  it('keeps the separate cookie adapter free of Authorization and uses same-origin cookies', async () => {
    const transport = vi.fn(async () => new Response('{"status":"ready","schema":"0016"}', { headers: { 'Content-Type': 'application/json' } }));
    const api = new CookieAdminApi(window.location.origin, transport);
    await expect(api.adminMe()).rejects.toThrow();
    for (const [path, init] of transport.mock.calls as unknown as [string, RequestInit][]) {
      expect(new Headers(init.headers).has('Authorization')).toBe(false);
      expect(init.credentials).toBe(path.startsWith('/health/') ? 'omit' : 'same-origin');
      expect(init.redirect).toBe('error');
    }
    api.disconnect();
    await expect(api.adminMe()).rejects.toThrow();
  });
});
