export type FailureKind = 'authentication' | 'forbidden' | 'not-found' | 'conflict' | 'too-large' | 'validation' | 'busy' | 'provider' | 'unreachable' | 'timeout' | 'cancelled' | 'incompatible' | 'server';
export type ApiFailure = { kind: FailureKind; message: string; status?: number; retryAfterMs?: number; outcome: 'unknown' | 'rejected' | 'unavailable' };
export class AdaError extends Error {
  constructor(readonly failure: ApiFailure) { super(failure.message); }
}

export function retryAfter(value: string | null, now = Date.now()): number | undefined {
  if (!value) return undefined;
  if (/^\d+$/.test(value)) {
    const milliseconds = Number(value) * 1000;
    return Number.isSafeInteger(milliseconds) ? Math.min(milliseconds, 86400000) : undefined;
  }
  const at = Date.parse(value);
  return Number.isFinite(at) ? Math.min(Math.max(at - now, 0), 86400000) : undefined;
}

// Deliberately ignore error bodies: validator messages/proxy HTML may contain private input.
export function httpFailure(status: number, after?: number): ApiFailure {
  const map: Record<number, [FailureKind, string]> = {
    401: ['authentication', 'The credential is invalid or expired. Reconnect with a current token.'],
    403: ['forbidden', 'This account cannot access this resource.'],
    404: ['not-found', 'The resource is unavailable to this account.'],
    409: ['conflict', 'The saved request differs or the conversation changed. Keep the original request data.'],
    413: ['too-large', 'The input is too large. Shorten it before making a new submission.'],
    422: ['validation', 'The server rejected the input. Check the fields before making a new submission.'],
    429: ['busy', 'The server is busy. Wait before retrying.'],
    503: ['busy', 'The server is unavailable or busy. Wait before retrying.'],
    502: ['provider', 'The model provider could not finish the request. Check its saved status.'],
  };
  const [kind, message] = map[status] ?? ['server', 'The server could not complete this operation.'];
  return { kind, message, status, retryAfterMs: after, outcome: status >= 500 ? 'unknown' : 'rejected' };
}

export function safeFailure(error: unknown): ApiFailure {
  return error instanceof AdaError ? error.failure : { kind: 'server', message: 'The connection could not be verified. Try again.', outcome: 'unavailable' };
}
