import { useEffect, useState, useSyncExternalStore, type ReactNode } from 'react';
import { useQuery, type UseQueryResult } from '@tanstack/react-query';
import type { AdminApi } from './api/admin';
import { safeFailure } from './api/errors';
import { Button } from './components';
import type { AdminSession } from './admin-session';

const visible = () => document.visibilityState !== 'hidden';
const subscribeVisibility = (listener: () => void) => { document.addEventListener('visibilitychange', listener); return () => document.removeEventListener('visibilitychange', listener); };
export function useMonitor<T>(session: AdminSession, resource: string, args: unknown, read: (api: AdminApi, signal: AbortSignal) => Promise<T>) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  const isVisible = useSyncExternalStore(subscribeVisibility, visible);
  return useQuery({ queryKey: session.key(resource, args), queryFn: ({ signal }) => session.read(api => read(api, signal)),
    enabled: state.kind === 'connected' && isVisible, retry: false, retryOnMount: false, gcTime: 0, staleTime: 30000,
    refetchOnWindowFocus: false, refetchOnReconnect: false, refetchIntervalInBackground: false,
    refetchInterval: query => !isVisible || state.kind !== 'connected' || query.state.error && ['not-found', 'validation', 'incompatible'].includes(safeFailure(query.state.error).kind) ? false : Math.max(30000, query.state.error ? safeFailure(query.state.error).retryAfterMs ?? 0 : 0),
  });
}
export function timestamp(value: bigint | null | undefined): string {
  if (value == null) return 'Not recorded';
  // Date supports a smaller range than int64. Preserve the exact instant if outside it.
  if (value < -8640000000000000n || value > 8640000000000000n) return `${value} ms since epoch (outside display range)`;
  return new Date(Number(value)).toISOString().replace('T', ' ').replace('Z', ' UTC');
}
export function amount(value: number | bigint | null | undefined, unit = '') { return value == null ? 'Not recorded' : `${value.toLocaleString()}${unit ? ` ${unit}` : ''}`; }
export function QueryView<T>({ query, children }: { query: UseQueryResult<T>; children: (data: T) => ReactNode }) {
  const failure = query.error ? safeFailure(query.error) : undefined;
  const retryAt = failure?.retryAfterMs ? query.errorUpdatedAt + failure.retryAfterMs : 0;
  const [now, setNow] = useState(Date.now);
  useEffect(() => { if (!failure?.retryAfterMs) return; const timer = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(timer); }, [failure?.retryAfterMs]);
  const isVisible = useSyncExternalStore(subscribeVisibility, visible);
  const unavailable = failure && ['not-found', 'authentication', 'forbidden'].includes(failure.kind);
  return <>
    <div className="refresh-row"><Button secondary disabled={!isVisible || query.isFetching || retryAt > Math.max(now, query.errorUpdatedAt)} onClick={() => void query.refetch()}>{query.isFetching ? 'Refreshing…' : 'Refresh'}</Button><span>{query.dataUpdatedAt ? `Last successful refresh: ${timestamp(BigInt(query.dataUpdatedAt))}` : 'No successful update yet'}</span></div>
    {failure && <p className="error-message" role={query.data ? undefined : 'alert'}>{query.data && !unavailable ? 'Stale data — refresh failed. ' : ''}{failure.message}{retryAt > Math.max(now, query.errorUpdatedAt) ? ` Retry available in ${Math.ceil((retryAt - Math.max(now, query.errorUpdatedAt)) / 1000)} seconds.` : ''}</p>}
    {query.isPending && <p role="status">Loading monitoring metadata…</p>}
    {query.data && !unavailable ? children(query.data) : null}
    <p className="hint">Refreshes every 30 seconds while visible. Polling pauses in hidden tabs.</p>
  </>;
}
