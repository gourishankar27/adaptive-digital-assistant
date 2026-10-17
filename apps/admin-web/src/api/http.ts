import { ContractError, decodeCapabilities, decodeRequest, decodeUser, parseWire, uuid } from './decode';
import { AdaError, httpFailure, retryAfter } from './errors';
import type { AdaApi } from './types';

export type FetchTransport = (input: string, init: RequestInit) => Promise<Response>;

async function unavailableCode(response: Response): Promise<'database_not_ready' | 'monitoring_unavailable' | undefined> {
  if (response.status !== 503 || response.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase() !== 'application/json' || !response.body) return;
  // Inspect at most 1 KiB for two fixed codes; proxy/validator/private text is discarded.
  const reader = response.body.getReader(), decoder = new TextDecoder('utf-8', { fatal: true });
  let size = 0, body = '';
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > 1024) return;
      body += decoder.decode(value, { stream: true });
    }
    body += decoder.decode();
    const payload: unknown = JSON.parse(body);
    if (typeof payload !== 'object' || payload === null || !('detail' in payload)) return;
    if (payload.detail === 'database_not_ready' || payload.detail === 'monitoring_unavailable') return payload.detail;
  } catch { /* Unknown or malformed failures retain generic status wording. */ }
  finally { await reader.cancel().catch(() => undefined); }
}

export function normalizeServer(value: string): string {
  if (!/^https?:\/\/[^/?#\\\s]+\/?$/i.test(value.trim())) throw new ContractError();
  const url = new URL(value);
  if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || (url.pathname !== '/' && url.pathname !== '')) throw new ContractError();
  if (url.protocol !== 'https:' && !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname)) throw new ContractError();
  if (url.origin !== window.location.origin) throw new ContractError();
  return url.origin;
}

export class HttpAdaApi implements AdaApi {
  private token: string;
  private active = new Set<AbortController>();
  private privacyEpoch?: string;
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
  async checkConnection(signal?: AbortSignal) { return this.checkServer(signal); }
  async capabilities(signal?: AbortSignal) { return this.get('/v1/capabilities', decodeCapabilities, signal); }
  async requestStatus(requestId: string, signal?: AbortSignal) {
    const expected = uuid(requestId).toLowerCase();
    return this.get(`/v1/requests/${expected}`, value => {
      const request = decodeRequest(value);
      if (request.request_id.toLowerCase() !== expected) throw new ContractError();
      return request;
    }, signal);
  }

  protected async checkServer(signal?: AbortSignal): Promise<void> {
    await this.get('/health/ready', value => {
      if (typeof value !== 'object' || value === null || !('status' in value) || value.status !== 'ready' || !('schema' in value) || typeof value.schema !== 'string' || !/^[0-9]{4}$/.test(value.schema)) throw new ContractError();
    }, signal, false);
  }

  protected async get<T>(path: string, decode: (value: unknown) => T, signal?: AbortSignal, authenticated = true): Promise<T> {
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
        method: 'GET', headers: authenticated ? { Accept: 'application/json', Authorization: `Bearer ${this.token}` } : { Accept: 'application/json' },
        signal: controller.signal, credentials: 'omit', redirect: 'error', cache: 'no-store', referrerPolicy: 'no-referrer',
      });
      // Even a custom injected transport cannot silently forward a redirect.
      if (response.redirected) throw new AdaError({ kind: 'unreachable', message: 'The API redirected the connection. Check the configured server.', outcome: 'unknown' });
      if (!response.ok) {
        if (response.status === 401) this.disconnect();
        const code = await unavailableCode(response);
        if (controller.signal.aborted && response.status !== 401) throw new DOMException('Cancelled', 'AbortError');
        throw new AdaError(httpFailure(response.status, retryAfter(response.headers.get('Retry-After')), code));
      }
      const privacyEpoch = response.headers.get('X-ADA-Privacy-Epoch');
      if (privacyEpoch !== null) {
        if (!/^[0-9]{1,20}$/.test(privacyEpoch)) throw new ContractError();
        if (this.privacyEpoch !== undefined && this.privacyEpoch !== privacyEpoch) {
          this.disconnect();
          throw new AdaError({ kind: 'authentication', message: 'Saved content changed. Sign in again to clear monitoring caches and refresh.', outcome: 'unavailable' });
        }
        this.privacyEpoch = privacyEpoch;
      }
      if (response.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase() !== 'application/json') throw new ContractError();
      let body: string;
      if (!authenticated) {
        const reader = response.body?.getReader();
        if (!reader) throw new ContractError();
        const decoder = new TextDecoder('utf-8', { fatal: true }); let size = 0; body = '';
        try {
          for (;;) {
            const { value, done } = await reader.read(); if (done) break;
            size += value.byteLength; if (size > 1024) throw new ContractError();
            body += decoder.decode(value, { stream: true });
          }
          body += decoder.decode();
        } finally { await reader.cancel().catch(() => undefined); }
      } else body = await response.text();
      const result = decode(parseWire(body));
      if (controller.signal.aborted || !this.token) throw new DOMException('Cancelled', 'AbortError');
      return result;
    } catch (error) {
      if (error instanceof AdaError) throw error;
      if (error instanceof ContractError) throw new AdaError({ kind: 'incompatible', message: error.message, outcome: 'unavailable' });
      if (controller.signal.aborted) {
        throw new AdaError({ kind: timedOut ? 'timeout' : 'cancelled', message: timedOut ? 'The wait timed out. A submitted request may still be running; recover its original request ID.' : 'Stopped waiting. Any submitted server request may continue.', outcome: 'unknown' });
      }
      throw new AdaError({ kind: 'unreachable', message: 'The server could not be reached. Check DNS, Wi-Fi or VPN, proxy availability and the browser certificate warning. Browsers do not identify the exact network or TLS cause here. Restore the connection before retrying.', outcome: 'unknown' });
    } finally {
      clearTimeout(timer);
      signal?.removeEventListener('abort', cancel);
      this.active.delete(controller);
    }
  }
}
