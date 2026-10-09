import { QueryClient } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { App } from '../src/App';
import { safeHref, TextContent } from '../src/components';
import { ConnectionSession } from '../src/state';
import { mockApi } from './mock-api';

describe('foundation screens', () => {
  it('validates with deliberate focus and authenticates without implying admin', async () => {
    const api = mockApi(), user = userEvent.setup();
    render(<MemoryRouter><App session={new ConnectionSession(new QueryClient(), () => api)} /></MemoryRouter>);
    await user.click(screen.getByRole('button', { name: 'Connect' }));
    expect(screen.getByRole('alert')).toHaveFocus();
    await user.type(screen.getByLabelText('Bearer token'), 'synthetic-test-credential');
    await user.click(screen.getByRole('button', { name: 'Connect' }));
    await screen.findByText('Account verified');
    expect(screen.getByText(/grants no admin role/)).toBeInTheDocument();
    expect(screen.queryByLabelText('Bearer token')).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Disconnect' }));
    expect(screen.getByLabelText('Bearer token')).toHaveValue('');
  });
  it('has accessible appearance controls and planned screen map', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><App session={new ConnectionSession(new QueryClient(), () => mockApi())} /></MemoryRouter>);
    await user.selectOptions(screen.getByLabelText('Theme'), 'dark');
    await user.selectOptions(screen.getByLabelText('Text'), 'large');
    expect(document.querySelector('.app')).toHaveAttribute('data-theme', 'dark');
    await user.click(screen.getByRole('link', { name: 'Screen map' }));
    await waitFor(() => expect(screen.getByRole('main')).toHaveFocus());
    expect(screen.getAllByText('Phase 6 · planned')).toHaveLength(5);
    expect(screen.queryByRole('button', { name: 'Send' })).not.toBeInTheDocument();
  });
  it('renders untrusted HTML as text and refuses executable or credentialed links', () => {
    const value = '<img src=x onerror=alert(1)><script>private</script>';
    const { container } = render(<TextContent text={value} />);
    expect(container.querySelector('img,script')).toBeNull();
    expect(screen.getByText(value)).toBeInTheDocument();
    expect(safeHref('javascript:alert(1)')).toBeUndefined();
    expect(safeHref('https://user:password@example.com')).toBeUndefined();
    expect(safeHref('https://example.com/source')).toBe('https://example.com/source');
  });
});
