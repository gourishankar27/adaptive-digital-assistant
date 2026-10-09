import type { QueryClient } from '@tanstack/react-query';
import { AdaError, safeFailure, type ApiFailure } from './api/errors';
import type { AdaApi, ConnectionInfo } from './api/types';

export type ConnectionState =
  | { kind: 'disconnected' }
  | { kind: 'validating' }
  | { kind: 'connected'; connection: ConnectionInfo }
  | { kind: 'error'; failure: ApiFailure };

// Definitions for subsequent phases. No simulated data or enabled write controls.
export type ScreenState<T> =
  | { kind: 'empty' }
  | { kind: 'loading' }
  | { kind: 'loaded'; data: T; lastUpdatedAt: number; stale: boolean }
  | { kind: 'offline'; action: 'reconnect' }
  | { kind: 'forbidden'; action: 'reconnect' }
  | { kind: 'error'; failure: ApiFailure; action: 'retry' }
  | { kind: 'unknown-outcome'; requestId?: string; action: 'reconcile' }
  | { kind: 'deferred'; phase: number };

export const screenMap = [
  { name: 'Sign in', phase: 3, description: 'Connection foundation; a server admin check is required before monitoring.' },
  { name: 'Overview', phase: 6, description: 'Readiness, actual counts and capacity, with unknown and stale states.' },
  { name: 'Requests', phase: 6, description: 'Authorized, server-filtered request metadata and pagination.' },
  { name: 'Request detail', phase: 6, description: 'Saved state, safe errors, timing and retrieval summaries.' },
  { name: 'Providers', phase: 6, description: 'Reported provider settings and limits, without credentials.' },
  { name: 'Audit', phase: 6, description: 'Authorized monitoring and role-change metadata.' },
] as const;

export function privateQueryKey(server: string, owner: string, resource: string, scope?: string, request?: string) {
  return ['ada', server, owner, resource, scope ?? '', request ?? ''] as const;
}

export class ConnectionSession {
  private current: ConnectionState = { kind: 'disconnected' };
  private listeners = new Set<() => void>();
  private generation = 0;
  private api?: AdaApi;
  constructor(private queries: QueryClient, private createApi: (server: string, token: string) => AdaApi) {}
  getSnapshot = () => this.current;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit(state: ConnectionState) { this.current = state; for (const listener of this.listeners) listener(); }
  private clear() {
    this.generation++;
    this.api?.disconnect();
    this.api = undefined;
    void this.queries.cancelQueries();
    this.queries.clear();
  }
  disconnect = () => { this.clear(); this.emit({ kind: 'disconnected' }); };
  async connect(server: string, token: string) {
    this.clear();
    const generation = this.generation;
    this.emit({ kind: 'validating' });
    try {
      const api = this.createApi(server, token);
      this.api = api;
      const user = await api.me();
      if (generation !== this.generation) return;
      const capabilities = await this.queries.fetchQuery({
        queryKey: privateQueryKey(server, user.id, 'capabilities'),
        queryFn: ({ signal }) => api.capabilities(signal), retry: false, gcTime: 0,
      });
      if (generation !== this.generation) return;
      this.emit({ kind: 'connected', connection: { server, user, capabilities } });
    } catch (error) {
      if (generation !== this.generation) return;
      this.clear();
      this.emit({ kind: 'error', failure: safeFailure(error) });
    }
  }

  // Subsequent read screens use this boundary so a revoked credential clears all private state.
  async requestStatus(requestId: string) {
    const current = this.current, api = this.api, generation = this.generation;
    if (current.kind !== 'connected' || !api) throw new AdaError({ kind: 'authentication', message: 'Connect before reading a request.', outcome: 'unavailable' });
    try {
      const result = await this.queries.fetchQuery({
        queryKey: privateQueryKey(current.connection.server, current.connection.user.id, 'request', undefined, requestId),
        queryFn: ({ signal }) => api.requestStatus(requestId, signal), retry: false, gcTime: 0,
      });
      if (generation !== this.generation) throw new AdaError({ kind: 'cancelled', message: 'The account or server changed. Reconnect before reading private data.', outcome: 'unknown' });
      return result;
    } catch (error) {
      if (generation === this.generation && safeFailure(error).kind === 'authentication') {
        this.clear(); this.emit({ kind: 'error', failure: safeFailure(error) });
      }
      throw error;
    }
  }
}
