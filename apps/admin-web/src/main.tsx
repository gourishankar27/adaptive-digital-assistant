import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './App';
import { HttpAdaApi } from './api/http';
import { ConnectionSession } from './state';
import './styles.css';

const queries = new QueryClient({ defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } } });
const session = new ConnectionSession(queries, (server, token) => new HttpAdaApi(server, token));
window.addEventListener('pagehide', session.disconnect);
createRoot(document.getElementById('root')!).render(<StrictMode><QueryClientProvider client={queries}><BrowserRouter><App session={session} /></BrowserRouter></QueryClientProvider></StrictMode>);
