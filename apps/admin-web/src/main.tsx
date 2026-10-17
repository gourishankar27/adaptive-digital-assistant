import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './App';
import { HttpAdminApi } from './api/admin';
import { AdminSession } from './admin-session';
import './styles.css';

const queries = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } });
const session = new AdminSession(queries, (server, token) => new HttpAdminApi(server, token));
window.addEventListener('pagehide', session.disconnect);
void session.reopen(window.location.origin);
createRoot(document.getElementById('root')!).render(<StrictMode><QueryClientProvider client={queries}><BrowserRouter basename="/admin"><App session={session} /></BrowserRouter></QueryClientProvider></StrictMode>);
