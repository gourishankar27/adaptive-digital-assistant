import { useEffect, useRef, useState, useSyncExternalStore, type FormEvent } from 'react';
import { NavLink, Route, Routes, useLocation } from 'react-router-dom';
import type { ConnectionSession } from './state';
import { screenMap } from './state';
import { Button, Field, Panel, TextContent } from './components';
import { normalizeServer } from './api/http';

function Connect({ session }: { session: ConnectionSession }) {
  const state = useSyncExternalStore(session.subscribe, session.getSnapshot);
  const [server, setServer] = useState(window.location.origin);
  const [token, setToken] = useState('');
  const [validation, setValidation] = useState('');
  const feedback = useRef<HTMLDivElement>(null);
  useEffect(() => { if (state.kind === 'error' || validation) feedback.current?.focus(); }, [state.kind, validation]);
  function change() { session.disconnect(); setValidation(''); }
  function submit(event: FormEvent) {
    event.preventDefault();
    let normalized: string;
    try { normalized = normalizeServer(server); }
    catch { setValidation('Use the current browser origin. Configure a different API server in the development proxy.'); return; }
    if (!token.trim() || token.trim().length > 200 || /[\r\n]/.test(token)) { setValidation('Enter a current bearer token (up to 200 characters).'); return; }
    const credential = token;
    setToken(''); setValidation('');
    void session.connect(normalized, credential);
  }
  return <>
    <div className="page-intro"><p className="eyebrow">Connection / phase 03</p><h1>A clear connection.<br />A grounded starting point.</h1><p className="intro-copy">Connect to your ADA backend and check the current account. This development foundation prepares the interface for authorized monitoring.</p></div>
    <div className="connection-grid">
      <Panel className="connect-panel">
        <div className="panel-heading"><span className="number">01</span><div><h2>Connect to ADA</h2><p className="muted">Your credential stays in this browser tab’s memory.</p></div></div>
        {state.kind === 'connected' ? <div className="connected-content">
          <div className="status-line"><span className="status-dot" aria-hidden="true" />Account verified</div>
          <h3>{state.connection.user.name}</h3><p className="server-label">{state.connection.server}</p>
          <p className="notice">Admin monitoring requires server authorization in Phase 05. This account check grants no admin role.</p>
          <dl className="facts"><div><dt>Chat API</dt><dd>{state.connection.capabilities.chat ? 'Reported available' : 'Unavailable'}</dd></div><div><dt>Streaming</dt><dd>{state.connection.capabilities.streaming ? 'Reported available' : 'Unavailable'}</dd></div><div><dt>Tools</dt><dd>{state.connection.capabilities.tools ? 'Reported available' : 'Unavailable'}</dd></div></dl>
          <details><summary>Connection details</summary><dl className="facts"><div><dt>Account ID</dt><dd>{state.connection.user.id}</dd></div><div><dt>Provider</dt><dd>{state.connection.capabilities.provider}</dd></div><div><dt>Model</dt><dd>{state.connection.capabilities.model}</dd></div></dl></details>
          <Button secondary onClick={() => { setToken(''); session.disconnect(); }}>Disconnect</Button>
        </div> : <form onSubmit={submit} noValidate>
          <Field label="Browser server origin" type="url" value={server} spellCheck={false} autoComplete="off" onChange={event => { change(); setToken(''); setServer(event.target.value); }} hint="Same-origin API access. The local development proxy points to ADA on your laptop." />
          <Field label="Bearer token" type="password" value={token} autoComplete="off" spellCheck={false} onChange={event => { change(); setToken(event.target.value); }} hint="Use a token issued by the ADA server. Refreshing the page requires connecting again." />
          <div ref={feedback} tabIndex={-1} role={validation || state.kind === 'error' ? 'alert' : 'status'} className={validation || state.kind === 'error' ? 'feedback error' : 'feedback'}>
            {validation || (state.kind === 'error' ? state.failure.message : state.kind === 'validating' ? 'Checking your account and the API contract…' : 'Ready when you are.')}
            {state.kind === 'error' && state.failure.retryAfterMs !== undefined && <p>Wait at least {Math.ceil(state.failure.retryAfterMs / 1000)} seconds before reconnecting.</p>}
          </div>
          <Button type="submit" disabled={state.kind === 'validating'}>{state.kind === 'validating' ? 'Connecting…' : 'Connect'}</Button>
          {state.kind === 'validating' && <Button type="button" secondary onClick={session.disconnect}>Stop waiting</Button>}
        </form>}
      </Panel>
      <aside className="connection-aside"><p className="eyebrow">A foundation, ready to build on</p><h2>One backend.<br />Clear boundaries.</h2><p>The interface uses the existing authenticated HTTP contract. The server owns permissions and private data.</p><div className="aside-rule" /><ul><li><span>01</span>Real account and capability checks</li><li><span>02</span>Account-bound private state</li><li><span>03</span>Readable, accessible controls</li></ul><p className="aside-note">Chat and dashboard screens are scheduled for their own phases. No production metrics or conversations are simulated here.</p></aside>
    </div>
  </>;
}

function Preview() {
  return <><div className="page-intro"><p className="eyebrow">Design / phase 03</p><h1>Room to read.<br />Easy to navigate.</h1><p className="intro-copy">Explore the shared color, typography and control foundations. These examples contain static interface copy.</p></div><div className="preview-grid"><Panel><p className="eyebrow">Reading preview</p><h2>Clear words, calm presentation</h2><TextContent text="ADA keeps expression separate from authority. A source shows where an assertion came from; the server checks who can access it." /><p className="muted">Long text wraps naturally as you enlarge the interface or narrow the window.</p><p className="notice">Example status: connection details need your attention.</p></Panel><Panel><p className="eyebrow">Control preview</p><h2>Visible focus and useful labels</h2><Field label="Example field" placeholder="Try navigating with Tab" hint="Preview only; this field sends no data." /><Button type="button" disabled>Unavailable in this phase</Button><p className="hint">Use the appearance controls above for light, dark and larger text.</p></Panel></div></>;
}

function Screens() {
  return <><div className="page-intro"><p className="eyebrow">Screen map / development</p><h1>A deliberate next step.</h1><p className="intro-copy">The planned admin screens share a state model for loading, empty, offline, forbidden, error, stale and uncertain outcomes.</p></div><Panel><div className="panel-heading"><span className="number">02</span><div><h2>Admin interface map</h2><p className="muted">The backend admin policy arrives in Phase 05; monitoring UI follows in Phase 06.</p></div></div><ol className="screen-list">{screenMap.map((screen, index) => <li key={screen.name}><span className="screen-index">{String(index + 1).padStart(2, '0')}</span><div><h3>{screen.name}</h3><p>{screen.description}</p></div><span className="phase-chip">{screen.phase === 3 ? 'Foundation' : `Phase ${screen.phase} · planned`}</span></li>)}</ol></Panel></>;
}

export function App({ session }: { session: ConnectionSession }) {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [textSize, setTextSize] = useState('standard');
  const location = useLocation();
  const main = useRef<HTMLElement>(null);
  const previousPath = useRef(location.pathname);
  useEffect(() => {
    if (previousPath.current !== location.pathname) main.current?.focus();
    previousPath.current = location.pathname;
  }, [location.pathname]);
  return <div className="app" data-theme={theme} data-text-size={textSize}>
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header><NavLink className="brand" to="/" aria-label="ADA foundation home"><span className="brand-mark" aria-hidden="true">A</span><span>ADA<span className="brand-caption">Adaptive Digital Assistant</span></span></NavLink><span className="dev-badge"><span aria-hidden="true" />Development foundation</span></header>
    <div className="toolbar"><nav aria-label="Foundation navigation"><NavLink to="/" end>Connection</NavLink><NavLink to="/design">Design preview</NavLink><NavLink to="/screens">Screen map</NavLink></nav><div className="appearance"><div className="setting-control"><label htmlFor="theme-selector">Theme</label><select id="theme-selector" value={theme} onChange={event => setTheme(event.target.value as typeof theme)}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></div><div className="setting-control"><label htmlFor="text-selector">Text</label><select id="text-selector" value={textSize} onChange={event => setTextSize(event.target.value)}><option value="standard">Standard</option><option value="large">Large</option></select></div></div></div>
    <main id="main-content" tabIndex={-1} ref={main}><Routes><Route path="/" element={<Connect session={session} />} /><Route path="/design" element={<Preview />} /><Route path="/screens" element={<Screens />} /><Route path="*" element={<Panel><h1>Page unavailable</h1><p>Choose a foundation screen from the navigation.</p></Panel>} /></Routes></main>
    <footer><span>ADA / UI foundations</span><span>Phase 03 · local development</span></footer>
  </div>;
}
