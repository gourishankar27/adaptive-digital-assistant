import { HttpAdminApi } from './admin';
import { AdaError, httpFailure, retryAfter } from './errors';
import { HttpAdaApi, normalizeServer, type FetchTransport } from './http';

// Host-only HttpOnly cookies are handled exclusively by the browser. No token API.
let queue: Promise<unknown> = Promise.resolve();
export function browserAuth(server: string, operation: 'login' | 'refresh' | 'logout' | 'logout-all' | 'password', body: object = {}, transport: FetchTransport = (path, init) => globalThis.fetch(path, init), isCurrent: () => boolean = () => true): Promise<number | undefined> {
  normalizeServer(server);
  if (!server.startsWith('https://')) return Promise.reject(new AdaError({ kind: 'authentication', message: 'Password sign-in requires the HTTPS admin origin. Use the private-network guide to configure it.', outcome: 'unavailable' }));
  const execute = async () => {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 10000);
    try {
      if (operation === 'login') {
        const probe = new HttpAdaApi(server, 'public-readiness', (path, init) => transport(path, init));
        try { await probe.checkConnection(controller.signal); } finally { probe.disconnect(); }
      }
      const path = operation === 'login' || operation === 'refresh' ? `/v1/auth/browser/${operation}` : `/v1/auth/${operation}`;
      const response = await transport(path, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-ADA-CSRF': '1' }, body: JSON.stringify(body), credentials: 'same-origin', redirect: 'error', cache: 'no-store', referrerPolicy: 'no-referrer', signal: controller.signal });
      if (response.redirected || !response.ok) throw new AdaError(httpFailure(response.status, retryAfter(response.headers.get('Retry-After'))));
      if ((operation === 'login' || operation === 'refresh') && !isCurrent()) {
        // Revoke the cancelled result while still holding the auth queue/lock,
        // before a later login can install a different account's cookies.
        await transport('/v1/auth/logout', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-ADA-CSRF': '1' }, body: '{}', credentials: 'same-origin', redirect: 'error', cache: 'no-store', signal: controller.signal });
        throw new AdaError({ kind: 'cancelled', message: 'The account or connection changed.', outcome: 'unavailable' });
      }
      const expiry = response.headers.get('X-ADA-Access-Expires-At');
      return expiry && /^[0-9]{1,16}$/.test(expiry) && Number.isSafeInteger(Number(expiry)) ? Number(expiry) : undefined;
    } finally { clearTimeout(timer); }
  };
  const result = queue.catch(() => undefined).then(async () => { if (navigator.locks) return await navigator.locks.request('ada-password-session', execute); return await execute(); });
  queue = result;
  return result;
}

export class CookieAdminApi extends HttpAdminApi {
  constructor(server: string, transport: FetchTransport = (path, init) => globalThis.fetch(path, init)) {
    let expectedOwner: string | undefined;
    super(server, 'cookie-session', async (path, init) => {
      const headers = new Headers(init.headers); headers.delete('Authorization');
      const response = await transport(path, { ...init, headers, credentials: path.startsWith('/health/') ? 'omit' : 'same-origin' });
      if (path.startsWith('/v1/') && response.ok) {
        const owner = response.headers.get('X-ADA-Owner');
        if (!owner || expectedOwner && owner !== expectedOwner) throw new AdaError({ kind: 'authentication', message: 'The signed-in account changed in another tab. Sign in again to clear private monitoring state.', outcome: 'unavailable' });
        if (path === '/v1/admin/me') expectedOwner = owner;
      }
      return response;
    });
  }
}
