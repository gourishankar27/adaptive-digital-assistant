import type { QueryClient } from '@tanstack/react-query';
import { AdaError, safeFailure, type ApiFailure } from './api/errors';
import type { AdminApi, AdminMe } from './api/admin';

export type AdminState = { kind: 'disconnected' } | { kind: 'validating' } | { kind: 'connected'; server: string; operator: AdminMe; epoch: number } | { kind: 'error'; failure: ApiFailure };
export class AdminSession {
  private state: AdminState = { kind: 'disconnected' };
  private epoch = 0;
  private api?: AdminApi;
  private cooldown?: { until: number; failure: ApiFailure };
  private listeners = new Set<() => void>();
  constructor(readonly queries: QueryClient, private factory: (server: string, token: string) => AdminApi) {}
  getSnapshot = () => this.state;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private emit(state: AdminState) { this.state = state; for (const listener of this.listeners) listener(); }
  private clear() {
    this.epoch++;
    this.api?.disconnect(); this.api = undefined;
    void this.queries.cancelQueries(); this.queries.clear();
  }
  disconnect = () => { this.clear(); this.emit({ kind: 'disconnected' }); };
  retryDeadline = () => this.cooldown?.until ?? 0;
  async connect(server: string, token: string) {
    this.clear(); const epoch = this.epoch;
    if (this.cooldown && this.cooldown.until > Date.now()) { this.emit({ kind: 'error', failure: { ...this.cooldown.failure, retryAfterMs: this.cooldown.until - Date.now() } }); return; }
    this.emit({ kind: 'validating' });
    try {
      const api = this.factory(server, token); this.api = api;
      const operator = await api.adminMe();
      if (epoch === this.epoch) this.emit({ kind: 'connected', server, operator, epoch });
    } catch (error) {
      if (epoch === this.epoch) {
        const failure = safeFailure(error);
        if (failure.retryAfterMs) this.cooldown = { until: Date.now() + failure.retryAfterMs, failure };
        this.clear(); this.emit({ kind: 'error', failure });
      }
    }
  }
  key(resource: string, args: unknown) {
    const state = this.state;
    return state.kind === 'connected' ? ['ada-admin', state.server, state.operator.id, state.epoch, resource, args] : ['ada-admin', 'disconnected', this.epoch, resource];
  }
  async read<T>(operation: (api: AdminApi) => Promise<T>): Promise<T> {
    const api = this.api, epoch = this.epoch;
    if (!api || this.state.kind !== 'connected') throw new AdaError({ kind: 'authentication', message: 'Sign in to monitor ADA.', outcome: 'unavailable' });
    if (this.cooldown && this.cooldown.until > Date.now()) throw new AdaError({ ...this.cooldown.failure, retryAfterMs: this.cooldown.until - Date.now() });
    try {
      const result = await operation(api);
      if (epoch !== this.epoch) throw new AdaError({ kind: 'cancelled', message: 'The account or server changed.', outcome: 'unavailable' });
      return result;
    } catch (error) {
      const failure = safeFailure(error);
      if (epoch === this.epoch && failure.retryAfterMs) this.cooldown = { until: Date.now() + failure.retryAfterMs, failure };
      if (epoch === this.epoch && ['authentication', 'forbidden'].includes(failure.kind)) { this.clear(); this.emit({ kind: 'error', failure }); }
      throw error;
    }
  }
}
