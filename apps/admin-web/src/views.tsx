import { useState, type FormEvent, type ReactNode } from 'react';
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom';
import type { AdminSession } from './admin-session';
import type { Filters, Overview, RequestMetadata } from './api/admin';
import { Button, Field, Panel } from './components';
import { amount, QueryView, timestamp, useMonitor } from './monitor-query';

function Intro({ title, children }: { title: string; children: ReactNode }) { return <div className="page-intro"><p className="eyebrow">ADA / backend monitoring</p><h1>{title}</h1><p className="intro-copy">{children}</p></div>; }
function Facts({ rows }: { rows: [string, ReactNode][] }) { return <dl className="facts">{rows.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>; }
function State({ value }: { value: string }) { return <span className="state-chip">{['running', 'completed', 'failed'].includes(value) ? value : `Unknown: ${value}`}</span>; }
function ProviderHealth({ health }: { health: Overview['provider_health'] }) {
  return <Facts rows={[
    ['Provider reachability', health.reachability === 'unknown' ? 'Unknown / not measured' : health.reachability === 'unreachable' ? 'Unavailable' : health.error_code || health.model_available === false ? 'Degraded' : 'Reachable'],
    ['Configured model installed', health.model_available == null ? 'Unknown / not measured' : health.model_available ? 'Yes' : 'No'],
    ['Probe checked', health.checked_at == null ? 'Not measured' : timestamp(health.checked_at)], ['Sanitized probe code', health.error_code ?? 'None reported'], ['Probe cache', `${health.cache_seconds} seconds`],
  ]} />;
}
export function OverviewView({ session }: { session: AdminSession }) {
  const [params, setParams] = useSearchParams();
  const hours = [1, 24, 168].includes(Number(params.get('hours'))) ? Number(params.get('hours')) : 24;
  const query = useMonitor(session, 'overview', hours, (api, signal) => api.overview(hours, signal));
  return <><Intro title="The backend, at a glance.">Recent request counts and measured readiness from the ADA server.</Intro><div className="field inline-field"><label htmlFor="window">Recent window</label><select id="window" value={hours} onChange={event => setParams({ hours: event.target.value })}><option value="1">Last hour</option><option value="24">Last 24 hours</option><option value="168">Last 7 days</option></select></div><QueryView query={query}>{data => <>
    <p className="muted">Requests created from {timestamp(data.created_from)}. Server observed {timestamp(data.updated_at)}.</p><div className="stat-grid">{Object.entries(data.requests).map(([status, count]) => <Panel key={status}><h2>{status[0].toUpperCase() + status.slice(1)}</h2><p className="metric">{amount(count)}</p><p className="hint">Requests in the selected creation window</p></Panel>)}</div><Panel><h2>Memory suggestions</h2>{data.memory_proposal_counts ? <Facts rows={Object.entries(data.memory_proposal_counts).map(([status, count]) => [status, amount(count)])} /> : <p>Proposal counts are not reported by this server.</p>}<p className="hint">Current review states for suggestions created in this window. Counts contain no review text or source excerpts.</p></Panel><div className="preview-grid"><Panel><h2>Readiness & capacity</h2><Facts rows={[
      ['Authenticated API read', 'Responding'], ['Database', data.database_ready ? 'Ready' : 'Unavailable'], ['Schema revision', data.schema_version ?? 'Unknown'], ['Active generation slots', `${data.generation_admission.process_active_slots} / ${data.generation_admission.max_parallel}`], ['Available slots', amount(data.generation_admission.process_available_slots)], ['Server workers', amount(data.generation_admission.workers)],
    ]} /><p className="hint">Readiness describes this successful read. It does not guarantee the next chat will succeed.</p></Panel><Panel><h2>Provider measurement</h2><ProviderHealth health={data.provider_health} /><Link to="/providers">View provider configuration</Link></Panel></div><Panel><h2>Recorded token totals</h2><Facts rows={[
      ['Input tokens', amount(data.input_tokens, 'tokens')], ['Requests with known input tokens', amount(data.input_tokens_known_requests)], ['Output tokens', amount(data.output_tokens, 'tokens')], ['Requests with known output tokens', amount(data.output_tokens_known_requests)],
    ]} /><p className="hint">Totals include only recorded values, across requests in this window. Missing token counts are not zero. This API provides counts, not a time series.</p></Panel>
  </>}</QueryView></>;
}
export function ProvidersView({ session }: { session: AdminSession }) {
  const query = useMonitor(session, 'providers', null, (api, signal) => api.providers(signal));
  return <><Intro title="Know the configured capacity.">Provider and generation limits reported by the backend. Configuration is read-only.</Intro><QueryView query={query}>{data => <div className="preview-grid"><Panel><h2>Provider configuration</h2><Facts rows={[
    ['Provider', data.provider], ['Configured model', data.model], ['Context limit', amount(data.context_tokens, 'tokens')], ['Output limit', amount(data.output_tokens, 'tokens')], ['Completion timeout', amount(data.timeout_seconds, 'seconds')], ['Maximum parallel generation', amount(data.generation_admission.max_parallel)], ['Active process slots', amount(data.generation_admission.process_active_slots)], ['Available process slots', amount(data.generation_admission.process_available_slots)], ['Workers', amount(data.generation_admission.workers)],
  ]} /><p className="hint">Slots belong to this ADA process. They describe admission capacity, not a provider queue or GPU load.</p></Panel><Panel><h2>Measured availability</h2><ProviderHealth health={data.health} /><p className="notice">GPU utilization and tokens per second are not measured by this API.</p><p className="hint">Health reads inspect provider availability without generating text. An installed model is not a successful-generation guarantee.</p></Panel></div>}</QueryView></>;
}
const requestKeys = ['owner_id', 'request_id', 'status', 'provider', 'created_from', 'created_to', 'limit', 'offset'];
const auditKeys = ['actor_id', 'action', 'outcome', 'limit', 'offset'];
const allowedFilters = (params: URLSearchParams, keys: string[]) => Object.fromEntries([...params].filter(([key, value]) => keys.includes(key) && value.length <= 80));
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const auditActions = ['role.grant', 'role.revoke', 'monitor.me', 'monitor.overview', 'monitor.providers', 'monitor.requests', 'monitor.request', 'monitor.audit'];
function FilterForm({ filters, audit = false, apply }: { filters: Filters; audit?: boolean; apply: (value: Filters) => void }) {
  const [error, setError] = useState('');
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget), next: Filters = {};
    for (const [key, value] of form) if (typeof value === 'string' && value.trim()) next[key] = value.trim();
    for (const key of ['owner_id', 'request_id', 'actor_id']) if (next[key] && !uuidPattern.test(next[key])) { setError('Owner, request and actor IDs must be valid UUIDs.'); return; }
    if (next.request_id && !next.owner_id) { setError('Choose an owner ID when filtering by request ID.'); return; }
    if (next.provider && !/^[A-Za-z0-9_.-]{1,40}$/.test(next.provider)) { setError('Provider must be 1–40 letters, numbers, dots, underscores or hyphens.'); return; }
    for (const key of ['created_from', 'created_to']) if (next[key]) next[key] = String(Date.parse(`${next[key]}Z`));
    if (!audit && (next.created_from || next.created_to)) {
      const end = next.created_to ? Number(next.created_to) : Date.now();
      const start = next.created_from ? Number(next.created_from) : end - 86400000;
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || end < start || end - start > 604800000) { setError('Choose an ordered UTC date window of at most 7 days.'); return; }
      next.created_from = String(start); next.created_to = String(end);
    }
    setError(''); apply(next);
  }
  const dateInput = (key: string) => filters[key] && /^\d{1,16}$/.test(filters[key]) && Number(filters[key]) <= 8640000000000000 ? new Date(Number(filters[key])).toISOString().slice(0, 23) : '';
  return <form onSubmit={submit} className="filter-form"><h2>{audit ? 'Audit filters' : 'Request filters'}</h2><div className="filter-grid">
    {audit ? <><Field label="Actor ID" name="actor_id" defaultValue={filters.actor_id} /><div className="field"><label htmlFor="action">Action</label><select id="action" name="action" defaultValue={filters.action ?? ''}><option value="">All actions</option>{auditActions.map(action => <option key={action}>{action}</option>)}</select></div><div className="field"><label htmlFor="outcome">Outcome</label><select id="outcome" name="outcome" defaultValue={filters.outcome ?? ''}><option value="">All outcomes</option>{['allowed', 'denied', 'granted', 'revoked', 'not_found', 'invalid', 'failed', 'unchanged', 'rate_limited'].map(value => <option key={value}>{value}</option>)}</select></div></> : <><Field label="Owner ID" name="owner_id" defaultValue={filters.owner_id} /><Field label="Request ID" name="request_id" defaultValue={filters.request_id} /><div className="field"><label htmlFor="state">State</label><select id="state" name="status" defaultValue={filters.status ?? ''}><option value="">All states</option>{['running', 'completed', 'failed'].map(value => <option key={value}>{value}</option>)}</select></div><Field label="Provider" name="provider" defaultValue={filters.provider} /><Field label="Created from (UTC)" name="created_from" type="datetime-local" step="0.001" defaultValue={dateInput('created_from')} /><Field label="Created to (UTC)" name="created_to" type="datetime-local" step="0.001" defaultValue={dateInput('created_to')} /></>}
    <div className="field"><label htmlFor="page-size">Rows per page</label><select id="page-size" name="limit" defaultValue={filters.limit ?? '50'}>{[10, 25, 50, 100].map(value => <option key={value}>{value}</option>)}</select></div>
  </div>{error && <p className="error-message" role="alert">{error}</p>}<Button type="submit">Apply filters</Button><Button type="button" secondary onClick={() => { setError(''); apply({}); }}>Reset filters</Button></form>;
}
function Pagination({ page, change }: { page: { limit: number; offset: number; has_more: boolean }; change: (offset: number) => void }) { return <div className="pagination"><Button secondary disabled={!page.offset} onClick={() => change(Math.max(0, page.offset - page.limit))}>Previous page</Button><span>Page {Math.floor(page.offset / page.limit) + 1} · {page.limit} rows per page</span><Button secondary disabled={!page.has_more || page.offset + page.limit > 10000} onClick={() => change(page.offset + page.limit)}>Next page</Button></div>; }
export function Requests({ session }: { session: AdminSession }) {
  const [params, setParams] = useSearchParams(), filters = allowedFilters(params, requestKeys), back = `/requests${params.size ? `?${new URLSearchParams(filters)}` : ''}`;
  const query = useMonitor(session, 'requests', filters, (api, signal) => api.requests(filters, signal));
  return <><Intro title="Follow each request.">Server-filtered metadata. Sorted by creation time descending, then owner and request identity.</Intro><Panel><FilterForm key={params.toString()} filters={filters} apply={value => setParams(value)} /></Panel><QueryView query={query}>{page => <>
    <p className="muted">Creation window: {timestamp(page.created_from)} to {timestamp(page.created_to)}. Observed {timestamp(page.updated_at)}.</p>{!page.items.length ? <Panel><h2>No requests in this window</h2><p>Change or reset the filters to inspect another window.</p></Panel> : <div className="table-scroll" role="region" aria-label="Request metadata table" tabIndex={0}><table><caption>Request metadata</caption><thead><tr>{['State', 'Owner / request', 'Conversation', 'Attempt / provider', 'Created / started / finished (UTC)', 'Request elapsed'].map(label => <th key={label} scope="col">{label}</th>)}</tr></thead><tbody>{page.items.map(item => <tr key={`${item.owner_id}/${item.request_id}`}><td><State value={item.status} /></td><td><span className="identifier">Owner: {item.owner_id}</span><Link className="identifier" to={`/requests/${item.owner_id}/${item.request_id}`} state={{ back }}>Request: {item.request_id}</Link></td><td className="identifier">{item.conversation_id}</td><td>{item.attempt}<br />{item.provider}<br />{item.model}</td><td>{timestamp(item.created_at)}<br />{timestamp(item.started_at)}<br />{timestamp(item.finished_at)}</td><td>{amount(item.elapsed_ms, 'ms')}</td></tr>)}</tbody></table></div>}
    <Pagination page={page} change={offset => setParams({ ...filters, limit: String(page.limit), offset: String(offset), created_from: String(page.created_from), created_to: String(page.created_to) })} />
  </>}</QueryView></>;
}
function Identity({ item }: { item: RequestMetadata }) { return <Facts rows={[
  ['Owner ID', item.owner_id], ['Request ID', item.request_id], ['Conversation ID', item.conversation_id], ['Scope ID', item.scope_id], ['State', <State value={item.status} />], ['Attempt count', amount(item.attempt)], ['Provider', item.provider], ['Model', item.model], ['Sanitized error code', item.error_code ?? 'None reported'], ['Input tokens', amount(item.input_tokens, 'tokens')], ['Output tokens', amount(item.output_tokens, 'tokens')],
]} />; }
export function Detail({ session }: { session: AdminSession }) {
  const { owner = '', request = '' } = useParams(), location = useLocation();
  const stateBack = (location.state as { back?: unknown } | null)?.back;
  const back = typeof stateBack === 'string' && /^\/requests(?:\?|$)/.test(stateBack) ? `/requests?${new URLSearchParams(allowedFilters(new URLSearchParams(stateBack.split('?')[1]), requestKeys))}` : '/requests';
  const query = useMonitor(session, 'detail', { owner, request }, (api, signal) => api.detail(owner, request, signal));
  return <><Link to={back}>← Back to requests</Link><Intro title="The recorded request.">An owner and request ID identify this metadata. Private content is excluded.</Intro><QueryView query={query}>{item => <><div className="preview-grid"><Panel><h2>Identity & outcome</h2><Identity item={item} /></Panel><Panel><h2>Recorded timeline</h2><Facts rows={[
    ['Created', timestamp(item.created_at)], ['Current attempt started', timestamp(item.started_at)], ['Finished', timestamp(item.finished_at)], ['Server observed', timestamp(item.observed_at)], ['Request elapsed', amount(item.elapsed_ms, 'ms')],
  ]} /><p className="hint">Elapsed is the server-recorded request interval, including context and database work. Earlier attempt timestamps are not exposed.</p></Panel></div><Panel><h2>Retrieval summary</h2>{!item.retrieval.available ? <p className="notice">Not recorded — this legacy request has no available retrieval summary.</p> : <><Facts rows={[
    ['Trace availability', 'Recorded'], ['Candidates considered', amount(item.retrieval.candidate_count)], ['Memories selected', amount(item.retrieval.selected_count)], ['Retrieval time', amount(item.retrieval.retrieval_ms, 'ms')], ['Memory budget used', amount(item.retrieval.memory_used_bytes, 'bytes')], ['Memory budget limit', amount(item.retrieval.memory_limit_bytes, 'bytes')], ['Prompt budget used', amount(item.retrieval.prompt_used_bytes, 'bytes')], ['Prompt budget limit', amount(item.retrieval.prompt_limit_bytes, 'bytes')], ['History pairs omitted', amount(item.retrieval.history_pairs_omitted)], ['Candidate pool truncated', item.retrieval.candidate_pool_truncated == null ? 'Not recorded' : item.retrieval.candidate_pool_truncated ? 'Yes' : 'No'],
  ]} /><p className="hint">Selected memories are not cited memories. Citation counts are not exposed by this admin API. Retrieval time covers the recorded retrieval step.</p></>}</Panel></>}</QueryView></>;
}
export function Audit({ session }: { session: AdminSession }) {
  const [params, setParams] = useSearchParams(), filters = allowedFilters(params, auditKeys);
  const query = useMonitor(session, 'audit', filters, (api, signal) => api.audit(filters, signal));
  return <><Intro title="An accountable monitoring trail.">Metadata for explicit role changes and monitoring reads. Local-operator events use the server’s reserved actor identity.</Intro><Panel><FilterForm audit key={params.toString()} filters={filters} apply={value => setParams(value)} /></Panel><QueryView query={query}>{page => <><p className="muted">Retention: {page.retention_days} days, up to {page.max_rows.toLocaleString()} events. Observed {timestamp(page.updated_at)}.</p>{!page.items.length ? <Panel><h2>No audit events match</h2><p>Change or reset the filters.</p></Panel> : <div className="table-scroll" role="region" aria-label="Audit metadata table" tabIndex={0}><table><caption>Audit metadata</caption><thead><tr>{['Time (UTC) / event ID', 'Actor', 'Action', 'Target', 'Outcome'].map(label => <th key={label} scope="col">{label}</th>)}</tr></thead><tbody>{page.items.map(item => <tr key={String(item.id)}><td>{timestamp(item.created_at)}<br />{String(item.id)}</td><td className="identifier">{item.actor_kind}<br />{item.actor_id}</td><td>{item.action}</td><td>{item.target_owner_id && item.target_request_id ? <Link className="identifier" to={`/requests/${item.target_owner_id}/${item.target_request_id}`}>{item.target_owner_id}<br />{item.target_request_id}</Link> : item.target_owner_id ?? 'No request target'}</td><td>{item.outcome}</td></tr>)}</tbody></table></div>}<Pagination page={page} change={offset => setParams({ ...filters, limit: String(page.limit), offset: String(offset) })} /></>}</QueryView></>;
}
