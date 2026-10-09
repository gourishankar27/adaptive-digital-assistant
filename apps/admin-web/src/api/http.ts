import { ContractError, decodeCapabilities, decodeRequest, decodeUser, parseWire, uuid } from './decode';
import { AdaError, httpFailure, retryAfter } from './errors';
import type { AdaApi } from './types';

export type FetchTransport = (input: string, init: RequestInit) => Promise<Response>;

export function normalizeServer(value: string): string {
  const url = new URL(value);
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || (url.pathname !== '/' && url.pathname !== '')) throw new ContractError();
  if (url.origin !== window.location.origin) throw new ContractError();
  return url.origin;
}

export class HttpAdaApi implements AdaApi {
  private token: string;
  private active = new Set<AbortController>();
  constructor(readonly server: string, token: string, private transport: FetchTransport = (input, init) => globalThis.fetch(input, init), private timeoutMs = 10000) {
    normalizeServer(server);
    if (!token.trim() || token.trim().length > 200 || /[\r\n]/.test(token)) throw new ContractError();
    this.token = token.trim();
  }
  disconnect() {
    this.token = '';
    for (const controller of this.active) controller.abort();
    this.active.clear();
  }
  async me(signal?: AbortSignal) { return this.get('/v1/me', decodeUser, signal); }
  async capabilities(signal?: AbortSignal) { return this.get('/v1/capabilities', decodeCapabilities, signal); }
  async requestStatus(requestId: string, signal?: AbortSignal) {
    const expected = uuid(requestId).toLowerCase();
    return this.get(`/v1/requests/${expected}`, value => {
      const request = decodeRequest(value);
      if (request.request_id.toLowerCase() !== expected) throw new ContractError();
      return request;
    }, signal);
  }

  private async get<T>(path: string, decode: (value: unknown) => T, signal?: AbortSignal): Promise<T> {
    if (!this.token) throw new AdaError({ kind: 'authentication', message: 'Reconnect with a current token.', outcome: 'unavailable' });
    const controller = new AbortController();
    this.active.add(controller);
    let timedOut = false;
    const cancel = () => controller.abort();
    signal?.addEventListener('abort', cancel, { once: true });
    if (signal?.aborted) controller.abort();
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, this.timeoutMs);
    try {
      const response = await this.transport(path, {
        method: 'GET', headers: { Accept: 'application/json', Authorization: `Bearer ${this.token}` },
        signal: controller.signal, credentials: 'omit', redirect: 'error', cache: 'no-store', referrerPolicy: 'no-referrer',
      });
      // Even a custom injected transport cannot silently forward a redirect.
      if (response.redirected) throw new AdaError({ kind: 'unreachable', message: 'The API redirected the connection. Check the configured server.', outcome: 'unknown' });
      if (!response.ok) {
        if (response.status === 401) this.disconnect();
        throw new AdaError(httpFailure(response.status, retryAfter(response.headers.get('Retry-After'))));
      }
      if (!response.headers.get('Content-Type')?.toLowerCase().includes('application/json')) throw new ContractError();
      const result = decode(parseWire(await response.text()));
      if (controller.signal.aborted || !this.token) throw new DOMException('Cancelled', 'AbortError');
      return result;
    } catch (error) {
      if (error instanceof AdaError) throw error;
      if (error instanceof ContractError) throw new AdaError({ kind: 'incompatible', message: error.message, outcome: 'unavailable' });
      if (controller.signal.aborted) {
        throw new AdaError({ kind: timedOut ? 'timeout' : 'cancelled', message: timedOut ? 'The wait timed out. A submitted request may still be running; recover its original request ID.' : 'Stopped waiting. Any submitted server request may continue.', outcome: 'unknown' });
      }
      throw new AdaError({ kind: 'unreachable', message: 'The server could not be reached. Check the connection and try again.', outcome: 'unknown' });
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener('abort', cancel);
      this.active.delete(controller);
    }
  }
}
