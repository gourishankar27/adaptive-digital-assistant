import { useEffect, useRef, useState, useSyncExternalStore, type FormEvent, type ReactNode } from 'react';
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import type { AdminSession } from './admin-session';
import { Button, Field, Panel } from './components';
import { normalizeServer } from './api/http';
import { loadAppearance, saveAppearance, type Appearance } from './appearance';
import { Audit, Detail, OverviewView, ProvidersView, Requests } from './views';

function SignIn({ session }: { session: AdminSession }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  const [server, setServer] = useState(window.location.origin), [token, setToken] = useState(''), [validation, setValidation] = useState('');
  const feedback = useRef<HTMLDivElement>(null);
  const [now, setNow] = useState(Date.now);
  useEffect(() => { if (session.retryDeadline() <= Date.now()) return; const timer = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(timer); }, [session, state]);
  useEffect(() => { if (state.kind === 'error' || validation) feedback.current?.focus(); }, [state.kind, validation]);
  function submit(event: FormEvent) {
    event.preventDefault();
    let origin: string;
    try { origin = normalizeServer(server); }
    catch { setValidation('Use the current browser origin. Configure a different API server in the development proxy.'); return; }
    if (!token.trim() || token.trim().length > 200 || /[\r\n]/.test(token)) { setValidation('Enter a current bearer token (up to 200 characters).'); return; }
    const credential = token.trim(); setToken(''); setValidation('');
    void session.connect(origin, credential);
  }
  return <><Intro title="A clear view of ADA.">Sign in with a server-authorized operator token to inspect backend monitoring metadata.</Intro><div className="preview-grid"><Panel><h2>Operator sign-in</h2><form onSubmit={submit} noValidate>
    <Field label="Browser server origin" type="url" value={server} autoComplete="off" spellCheck={false} onChange={event => { session.disconnect(); setToken(''); setValidation(''); setServer(event.target.value); }} hint="Same-origin access. A fixed development proxy selects the backend." />
    <Field label="Bearer token" type="password" value={token} autoComplete="off" spellCheck={false} onChange={event => { session.disconnect(); setValidation(''); setToken(event.target.value); }} hint="Kept in this tab’s memory. Refreshing the page requires signing in again." />
    <div ref={feedback} tabIndex={-1} role={validation || state.kind === 'error' ? 'alert' : 'status'} className="feedback">
      {validation || (state.kind === 'error' ? state.failure.kind === 'forbidden' ? 'Access denied. A local operator must explicitly grant the monitoring role.' : state.failure.message : state.kind === 'validating' ? 'Verifying the server and operator permission…' : 'Ready to verify your operator account.')}
      {state.kind === 'error' && state.failure.retryAfterMs !== undefined && <p>Wait at least {Math.ceil(state.failure.retryAfterMs / 1000)} seconds before signing in again.</p>}
    </div><Button type="submit" disabled={state.kind === 'validating' || session.retryDeadline() > now}>Sign in</Button>{state.kind === 'validating' && <Button type="button" secondary onClick={session.disconnect}>Stop waiting</Button>}
  </form></Panel><Panel><p className="eyebrow">Read-only monitoring</p><h2>Actual state. Clear boundaries.</h2><p>Inspect request status, provider readiness and audit metadata. Missing measurements stay unknown.</p><p className="notice">The server checks the monitoring role on every read. Account names and personalities do not grant access.</p><p className="muted">Private conversations, source quotes and prompt content are excluded from these views.</p></Panel></div></>;
}
export function Intro({ title, children }: { title: string; children: ReactNode }) { return <div className="page-intro"><p className="eyebrow">ADA / backend monitoring</p><h1>{title}</h1><p className="intro-copy">{children}</p></div>; }
function Guard({ session, children }: { session: AdminSession; children: ReactNode }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  return state.kind === 'connected' ? children : <SignIn session={session} />;
}
function Settings({ session, appearance, change }: { session: AdminSession; appearance: Appearance; change: (value: Appearance) => void }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  return <><Intro title="Make room to read.">Choose the palette, brightness and text size that suit your screen.</Intro><div className="preview-grid"><Panel><h2>Appearance</h2><div className="field"><label htmlFor="palette">Color palette</label><select id="palette" value={appearance.palette} onChange={event => change({ ...appearance, palette: event.target.value as Appearance['palette'] })}><option value="blue">Oxford Blue · #002147 (default)</option><option value="red">Dark Red · #350616</option><option value="olive">Olive Green · #3c4c24</option></select></div><div className="field"><label htmlFor="mode">Brightness</label><select id="mode" value={appearance.mode} onChange={event => change({ ...appearance, mode: event.target.value as Appearance['mode'] })}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></div><div className="field"><label htmlFor="text-size">Text size</label><select id="text-size" value={appearance.text} onChange={event => change({ ...appearance, text: event.target.value as Appearance['text'] })}><option value="standard">Standard</option><option value="large">Large</option></select></div><p className="hint">Only these appearance preferences are saved on this device.</p></Panel><Panel><h2>Current connection</h2>{state.kind === 'connected' ? <><p className="server-label">Server: {state.server}</p><p className="identifier">Operator: {state.operator.id}</p><p>Permission verified: monitoring:read</p><Button secondary onClick={session.disconnect}>Sign out / change account</Button><p className="hint">Signing out clears all monitoring data and the credential from this session.</p></> : <p>Sign in from a monitoring screen to verify your operator account.</p>}<p className="notice">Provider and capacity settings are read-only on the Providers screen.</p></Panel></div></>;
}
const darkSnapshot = () => window.matchMedia('(prefers-color-scheme: dark)').matches;
const subscribeDark = (listener: () => void) => { const media = window.matchMedia('(prefers-color-scheme: dark)'); media.addEventListener('change', listener); return () => media.removeEventListener('change', listener); };
export function App({ session }: { session: AdminSession }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  const [appearance, setAppearance] = useState(loadAppearance);
  const dark = useSyncExternalStore(subscribeDark, darkSnapshot);
  const location = useLocation(), main = useRef<HTMLElement>(null), previousPath = useRef(location.pathname);
  useEffect(() => { if (previousPath.current !== location.pathname) main.current?.focus(); previousPath.current = location.pathname; }, [location.pathname]);
  const guard = (view: ReactNode) => <Guard session={session}>{view}</Guard>;
  return <div className="app" data-theme={appearance.mode === 'system' ? dark ? 'dark' : 'light' : appearance.mode} data-palette={appearance.palette} data-text-size={appearance.text}>
    <a className="skip-link" href="#main-content">Skip to content</a><header><NavLink className="brand" to="/overview" aria-label="ADA monitoring home"><span className="brand-mark" aria-hidden="true">A</span><span>ADA<span className="brand-caption">Backend monitoring</span></span></NavLink><div className="account">{state.kind === 'connected' ? <><span className="identifier">Operator {state.operator.id}</span><Button secondary onClick={session.disconnect}>Sign out</Button></> : <span className="dev-badge">Authorization required</span>}</div></header>
    <div className="toolbar"><nav aria-label="Monitoring navigation">{['overview', 'requests', 'providers', 'audit', 'settings'].map(path => <NavLink key={path} to={`/${path}`}>{path[0].toUpperCase() + path.slice(1)}</NavLink>)}</nav></div>
    <main id="main-content" tabIndex={-1} ref={main}><Routes><Route path="/" element={<Navigate to="/overview" replace />} /><Route path="/sign-in" element={state.kind === 'connected' ? <Navigate to="/overview" replace /> : <SignIn session={session} />} /><Route path="/overview" element={guard(<OverviewView session={session} />)} /><Route path="/requests" element={guard(<Requests session={session} />)} /><Route path="/requests/:owner/:request" element={guard(<Detail session={session} />)} /><Route path="/providers" element={guard(<ProvidersView session={session} />)} /><Route path="/audit" element={guard(<Audit session={session} />)} /><Route path="/settings" element={<Settings session={session} appearance={appearance} change={value => { setAppearance(value); saveAppearance(value); }} />} /><Route path="*" element={<Panel><h1>Page unavailable</h1><p>Choose a monitoring screen from the navigation.</p></Panel>} /></Routes></main>
    <footer><span>ADA / read-only monitoring</span><span>Times shown in UTC</span></footer>
  </div>;
}
