import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AdminSession } from '../src/admin-session';
import { AdaError, httpFailure } from '../src/api/errors';
import { QueryView, useMonitor } from '../src/monitor-query';
import { mockAdmin } from './mock-admin';
function Monitor({ session }: { session: AdminSession }) { const q = useMonitor(session, 'overview', 24, (api, signal) => api.overview(24, signal)); return <QueryView query={q}>{data => <p>Completed: {data.requests.completed}</p>}</QueryView>; }
async function tick(ms: number) { await act(async () => { await vi.advanceTimersByTimeAsync(ms); }); }
afterEach(() => { vi.useRealTimers(); Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' }); });
describe('bounded monitoring polling', () => {
  it('polls at 30 seconds, pauses hidden tabs, keeps focus and stops on auth loss', async () => {
    vi.useFakeTimers(); const api = mockAdmin(), queries = new QueryClient(), session = new AdminSession(queries, () => api); await session.connect('server', 'credential');
    const view = render(<QueryClientProvider client={queries}><Monitor session={session} /></QueryClientProvider>); await tick(1);
    expect(api.overview).toHaveBeenCalledTimes(1); const refresh = screen.getByRole('button', { name: 'Refresh' }); refresh.focus();
    await tick(29999); expect(api.overview).toHaveBeenCalledTimes(2); expect(refresh).toHaveFocus();
    await act(async () => { Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'hidden' }); document.dispatchEvent(new Event('visibilitychange')); });
    await tick(90000); expect(api.overview).toHaveBeenCalledTimes(2); expect(refresh).toBeDisabled();
    vi.mocked(api.overview).mockRejectedValueOnce(new AdaError(httpFailure(401)));
    await act(async () => { Object.defineProperty(document, 'visibilityState', { configurable: true, value: 'visible' }); document.dispatchEvent(new Event('visibilitychange')); }); await tick(1);
    expect(session.getSnapshot().kind).toBe('error'); await tick(90000); expect(api.overview).toHaveBeenCalledTimes(3); view.unmount();
  });
  it('honors Retry-After across manual refresh, polling and navigation', async () => {
    vi.useFakeTimers(); const api = mockAdmin(), queries = new QueryClient(), session = new AdminSession(queries, () => api); await session.connect('server', 'credential');
    const view = render(<QueryClientProvider client={queries}><Monitor session={session} /></QueryClientProvider>); await tick(1);
    vi.mocked(api.overview).mockRejectedValueOnce(new AdaError(httpFailure(429, 60000))); await tick(30000);
    expect(screen.getByRole('button', { name: 'Refresh' })).toBeDisabled(); expect(screen.getByText(/Stale data/)).toBeInTheDocument();
    await expect(session.read(api => api.providers())).rejects.toMatchObject({ failure: { kind: 'busy' } }); expect(api.providers).not.toHaveBeenCalled();
    await tick(59000); expect(api.overview).toHaveBeenCalledTimes(2); await tick(1000); expect(api.overview).toHaveBeenCalledTimes(3); view.unmount();
  });
  it('allows recovery after a transient error without Retry-After', async () => {
    vi.useFakeTimers(); const api = mockAdmin(), queries = new QueryClient(), session = new AdminSession(queries, () => api); await session.connect('server', 'credential');
    const view = render(<QueryClientProvider client={queries}><Monitor session={session} /></QueryClientProvider>); await tick(1);
    vi.mocked(api.overview).mockRejectedValueOnce(new AdaError(httpFailure(503))); await tick(30000);
    expect(screen.getByRole('button', { name: 'Refresh' })).toBeEnabled(); view.unmount();
  });
});
