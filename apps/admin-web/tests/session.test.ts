import { QueryClient } from '@tanstack/react-query';
import { describe, expect, it, vi } from 'vitest';
import current from '../../../contracts/fixtures/request-current.json';
import { decodeRequest } from '../src/api/decode';
import { AdaError } from '../src/api/errors';
import { ConnectionSession, privateQueryKey } from '../src/state';
import { mockApi, ownerA } from './mock-api';

describe('private connection state', () => {
  it('binds cache keys to server, identity, scope and request', () => {
    expect(privateQueryKey('server-a', 'owner-a', 'trace', 'scope-a', 'request-a')).not.toEqual(privateQueryKey('server-a', 'owner-b', 'trace', 'scope-a', 'request-a'));
    expect(privateQueryKey('server-a', 'owner-a', 'trace')).not.toEqual(privateQueryKey('server-b', 'owner-a', 'trace'));
  });
  it('clears all private queries and aborts the adapter on disconnect/account switch', async () => {
    const queries = new QueryClient(), first = mockApi(), second = mockApi('00000000-0000-0000-0000-000000000002');
    const factory = vi.fn().mockReturnValueOnce(first).mockReturnValueOnce(second);
    const session = new ConnectionSession(queries, factory);
    await session.connect('server-a', 'synthetic-a');
    queries.setQueryData(privateQueryKey('server-a', ownerA, 'source'), { text: 'synthetic-private' });
    await session.connect('server-b', 'synthetic-b');
    expect(first.disconnect).toHaveBeenCalled();
    expect(queries.getQueryData(privateQueryKey('server-a', ownerA, 'source'))).toBeUndefined();
    session.disconnect();
    expect(queries.getQueryCache().getAll()).toHaveLength(0);
    expect(session.getSnapshot().kind).toBe('disconnected');
  });
  it('a late old connection cannot restore account data after a switch', async () => {
    let complete!: (value: { id: string; name: string }) => void;
    const first = mockApi(); first.me = () => new Promise(resolve => { complete = resolve; });
    const second = mockApi('00000000-0000-0000-0000-000000000002');
    const session = new ConnectionSession(new QueryClient(), vi.fn().mockReturnValueOnce(first).mockReturnValueOnce(second));
    const oldAttempt = session.connect('server-a', 'synthetic-a');
    await session.connect('server-b', 'synthetic-b');
    complete({ id: ownerA, name: 'Old private name' });
    await oldAttempt;
    expect(session.getSnapshot()).toMatchObject({ kind: 'connected', connection: { server: 'server-b', user: { id: '00000000-0000-0000-0000-000000000002' } } });
    expect(first.capabilities).not.toHaveBeenCalled();
  });
  it('401 during a private read removes account data and stops automatic retries', async () => {
    const queries = new QueryClient(), api = mockApi();
    api.requestStatus = vi.fn(async () => { throw new AdaError({ kind: 'authentication', message: 'Reconnect.', status: 401, outcome: 'rejected' }); });
    const session = new ConnectionSession(queries, () => api);
    await session.connect('server-a', 'synthetic-a');
    await expect(session.requestStatus(current.request_id)).rejects.toBeInstanceOf(AdaError);
    expect(session.getSnapshot()).toMatchObject({ kind: 'error', failure: { kind: 'authentication' } });
    expect(queries.getQueryCache().getAll()).toHaveLength(0);
    expect(api.requestStatus).toHaveBeenCalledTimes(1);
  });
  it('a pending private read cannot deliver its result after logout', async () => {
    let complete!: (value: ReturnType<typeof decodeRequest>) => void;
    const api = mockApi(); api.requestStatus = () => new Promise(resolve => { complete = resolve; });
    const queries = new QueryClient(), session = new ConnectionSession(queries, () => api);
    await session.connect('server-a', 'synthetic-a');
    const pending = session.requestStatus(current.request_id);
    const expectation = expect(pending).rejects.toBeDefined();
    session.disconnect(); complete(decodeRequest(current));
    await expectation;
    expect(session.getSnapshot().kind).toBe('disconnected');
    expect(queries.getQueryCache().getAll()).toHaveLength(0);
  });
});
