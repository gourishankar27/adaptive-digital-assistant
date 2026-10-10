import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { App } from '../src/App';
import { safeHref, TextContent } from '../src/components';
import { AdminSession } from '../src/admin-session';
import { AdaError, httpFailure } from '../src/api/errors';
import { mockAdmin, otherOwner, owner, requestId } from './mock-admin';

function mount(path = '/overview', api = mockAdmin()) {
  const queries = new QueryClient({ defaultOptions: { queries: { retry: false } } }), session = new AdminSession(queries, () => api);
  const rendered = render(<QueryClientProvider client={queries}><MemoryRouter initialEntries={[path]}><App session={session} /></MemoryRouter></QueryClientProvider>);
  return { api, queries, session, ...rendered };
}
async function signIn(user: ReturnType<typeof userEvent.setup>) { await user.type(screen.getByLabelText('Bearer token'), 'synthetic-test-credential'); await user.click(screen.getByRole('button', { name: 'Sign in' })); }
describe('admin views', () => {
  it('verifies admin permission and clears the input, cache and credential on logout', async () => {
    const { queries, api } = mount(), user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: 'Sign in' })); expect(screen.getByRole('alert')).toHaveFocus();
    await signIn(user); await screen.findByRole('heading', { name: 'The backend, at a glance.' });
    expect(screen.getAllByText('Unknown / not measured')).toHaveLength(2);
    expect(JSON.stringify(queries.getQueryCache().getAll().map(q => q.queryKey))).not.toContain('synthetic-test-credential');
    expect(localStorage.length).toBe(0); expect(sessionStorage.length).toBe(0);
    await user.click(screen.getByRole('button', { name: 'Sign out' })); expect(queries.getQueryCache().getAll()).toHaveLength(0); expect(api.disconnect).toHaveBeenCalled(); expect(screen.getByLabelText('Bearer token')).toHaveValue('');
  });
  it('denies an ordinary token and immediately removes a revoked detail', async () => {
    const { api, queries } = mount(`/requests/${owner}/${requestId}`), user = userEvent.setup();
    vi.mocked(api.adminMe).mockRejectedValueOnce(new AdaError(httpFailure(403)));
    await signIn(user); expect(await screen.findByRole('alert')).toHaveTextContent('Access denied'); expect(api.detail).not.toHaveBeenCalled();
    await signIn(user); await screen.findByText('Not recorded — this legacy request has no available retrieval summary.');
    expect(screen.getByText('<script>model</script>')).toBeInTheDocument(); expect(document.querySelector('script')).toBeNull();
    vi.mocked(api.detail).mockRejectedValueOnce(new AdaError(httpFailure(403)));
    await user.click(screen.getByRole('button', { name: 'Refresh' })); await screen.findByRole('alert'); expect(screen.queryByText('Identity & outcome')).not.toBeInTheDocument(); expect(queries.getQueryCache().getAll()).toHaveLength(0);
  });
  it('keeps last successful values stale on transient failure, with stable focus', async () => {
    const { api } = mount(), user = userEvent.setup(); await signIn(user); await screen.findByText('Responding');
    vi.mocked(api.overview).mockRejectedValueOnce(new AdaError(httpFailure(503)));
    const refresh = screen.getByRole('button', { name: 'Refresh' }); await user.click(refresh);
    await screen.findByText(/Stale data — refresh failed/); expect(screen.getByText('Responding')).toBeInTheDocument(); expect(refresh).toHaveFocus();
  });
  it('uses both IDs in detail links and restores server filters without client filtering', async () => {
    const { api } = mount('/requests?status=completed&limit=10'), user = userEvent.setup(); await signIn(user);
    const links = await screen.findAllByRole('link', { name: `Request: ${requestId}` });
    expect(links.map(link => link.getAttribute('href'))).toEqual([`/requests/${owner}/${requestId}`, `/requests/${otherOwner}/${requestId}`]);
    await user.click(links[1]); await screen.findByText('Identity & outcome'); expect(api.detail).toHaveBeenCalledWith(otherOwner, requestId, expect.any(AbortSignal));
    await user.click(screen.getByRole('link', { name: /Back to requests/ })); await screen.findByRole('table'); expect(screen.getByLabelText('State')).toHaveValue('completed'); expect(screen.getByRole('main')).toHaveFocus();
  });
  it('validates owner/time filters, resets them and handles empty results', async () => {
    const { api } = mount('/requests'), user = userEvent.setup(); await signIn(user); await screen.findByRole('table');
    await user.type(screen.getByLabelText('Request ID'), requestId); await user.click(screen.getByRole('button', { name: 'Apply filters' })); expect(screen.getByRole('alert')).toHaveTextContent('Choose an owner');
    vi.mocked(api.requests).mockResolvedValueOnce({ items: [], limit: 50, offset: 0, has_more: false, created_from: 0n, created_to: 1000n, updated_at: 1000n });
    await user.type(screen.getByLabelText('Owner ID'), owner); await user.click(screen.getByRole('button', { name: 'Apply filters' })); await screen.findByText('No requests in this window');
    await user.click(screen.getByRole('button', { name: 'Reset filters' })); await waitFor(() => expect(screen.getByLabelText('Request ID')).toHaveValue(''));
  });
  it('persists only appearance, honors palettes and text size before authentication', async () => {
    mount('/settings'); const user = userEvent.setup(); expect(document.querySelector('.app')).toHaveAttribute('data-palette', 'blue');
    await user.selectOptions(screen.getByLabelText('Color palette'), 'red'); await user.selectOptions(screen.getByLabelText('Brightness'), 'dark'); await user.selectOptions(screen.getByLabelText('Text size'), 'large');
    expect(document.querySelector('.app')).toHaveAttribute('data-theme', 'dark'); expect(localStorage.getItem('ada.appearance.v1')).toBe('{"palette":"red","mode":"dark","text":"large"}');
  });
  it('preserves exact millisecond bounds when reapplying a paginated date filter', async () => {
    const { api } = mount('/requests?created_from=1001&created_to=2100&limit=10'), user = userEvent.setup(); await signIn(user); await screen.findByRole('table');
    await user.click(screen.getByRole('button', { name: 'Apply filters' }));
    await waitFor(() => expect(api.requests).toHaveBeenLastCalledWith({ created_from: '1001', created_to: '2100', limit: '10' }, expect.any(AbortSignal)));
  });
  it('renders untrusted text literally and refuses executable or credentialed links', () => {
    const value = '<img src=x onerror=alert(1)><script>private</script>', { container } = render(<TextContent text={value} />);
    expect(container.querySelector('img,script')).toBeNull(); expect(screen.getByText(value)).toBeInTheDocument(); expect(safeHref('javascript:alert(1)')).toBeUndefined(); expect(safeHref('https://user:password@example.com')).toBeUndefined();
  });
});
