import { QueryClient } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import { AdminSession } from '../src/admin-session';
import { AdaError, httpFailure } from '../src/api/errors';
import { mockAdmin, otherOwner, owner } from './mock-admin';
function deferred<T>() { let resolve!: (value: T) => void; const promise = new Promise<T>(r => { resolve = r; }); return { promise, resolve }; }
describe('admin identity boundaries', () => {
  it('honors admin-me Retry-After across reconnect attempts', async () => {
    vi.useFakeTimers();
    try {
      const api = mockAdmin(), session = new AdminSession(new QueryClient(), () => api);
      vi.mocked(api.adminMe).mockRejectedValueOnce(new AdaError(httpFailure(429, 60000)));
      await session.connect('server', 'credential'); await session.connect('server', 'replacement'); expect(api.adminMe).toHaveBeenCalledTimes(1);
      await vi.advanceTimersByTimeAsync(60000); await session.connect('server', 'replacement'); expect(session.getSnapshot().kind).toBe('connected'); session.disconnect();
    } finally { vi.useRealTimers(); }
  });
  it.each([401, 403])('clears all metadata and blocks reads after %s', async status => {
    const api = mockAdmin(), queries = new QueryClient(), session = new AdminSession(queries, () => api); await session.connect('server', 'credential');
    queries.setQueryData(session.key('detail', { owner, request: 'request' }), { privateMetadata: true });
    await expect(session.read(async () => { throw new AdaError(httpFailure(status)); })).rejects.toBeInstanceOf(AdaError);
    expect(queries.getQueryCache().getAll()).toHaveLength(0); expect(session.getSnapshot().kind).toBe('error');
    await expect(session.read(api => api.overview(24))).rejects.toBeInstanceOf(AdaError); expect(api.overview).not.toHaveBeenCalled();
  });
  it('fences late sign-in, reads and old-account denial on switch', async () => {
    const old = mockAdmin(), next = mockAdmin(otherOwner), waiting = deferred<Awaited<ReturnType<typeof old.adminMe>>>();
    vi.mocked(old.adminMe).mockReturnValueOnce(waiting.promise);
    const queries = new QueryClient(), session = new AdminSession(queries, vi.fn().mockReturnValueOnce(old).mockReturnValue(next));
    const oldConnect = session.connect('old', 'old-credential'); await session.connect('next', 'new-credential'); waiting.resolve({ id: owner, permissions: ['monitoring:read'] }); await oldConnect;
    expect(session.getSnapshot()).toMatchObject({ kind: 'connected', operator: { id: otherOwner }, server: 'next' });
    const late = deferred<number>(); const read = session.read(() => late.promise); await session.connect('changed', 'credential'); late.resolve(1); await expect(read).rejects.toBeInstanceOf(AdaError);
    queries.setQueryData(session.key('overview', 24), 1); const denied = deferred<number>(); const staleRead = session.read(() => denied.promise.then(() => { throw new AdaError(httpFailure(403)); }));
    await session.connect('new', 'credential'); queries.setQueryData(session.key('overview', 24), 2); denied.resolve(0); await expect(staleRead).rejects.toBeInstanceOf(AdaError); expect(session.getSnapshot().kind).toBe('connected'); expect(queries.getQueryCache().getAll()).toHaveLength(1);
  });
  it('includes server, principal, epoch, filters and composite identity without credentials', async () => {
    const session = new AdminSession(new QueryClient(), () => mockAdmin()); await session.connect('server', 'secret');
    const key = session.key('detail', { owner: otherOwner, request: 'request' }); expect(key).toEqual(['ada-admin', 'server', owner, expect.any(Number), 'detail', { owner: otherOwner, request: 'request' }]); expect(JSON.stringify(key)).not.toContain('secret'); session.disconnect();
  });
});
