import type { AdminSession } from './admin-session';
import { Panel } from './components';
import { ContractError } from './api/decode';
import { QueryView, timestamp, useMonitor } from './monitor-query';

export function ReflectionView({ session }: { session: AdminSession }) {
  const query = useMonitor(session, 'reflection', {}, (api, signal) => {
    if (!api.reflection) return Promise.reject(new ContractError());
    return api.reflection(signal);
  });
  return <><div className="page-intro"><p className="eyebrow">ADA / backend monitoring</p><h1>Idle reflection</h1><p>Counts, states and hard budgets. Private drafts, source text, topics and owner selections stay in the owner review area.</p></div>
    <QueryView query={query}>{data => <>
      <Panel><h2>Safety and capacity</h2><p>{data.globally_enabled ? 'Idle work globally enabled' : 'Idle work globally stopped'}</p><p>{data.summary_generation ? 'Validated model summary class enabled' : 'Model summaries disabled'}</p>{data.suspended_model_class && <p role="status">The model class is suspended. A new cancellation and usefulness verification is required.</p>}<p>Opted-in policies: {data.policies_enabled}. Minimum ADA inactivity: {data.minimum_idle_seconds} seconds. Hard daily cap: {data.maximum_jobs} jobs and {data.maximum_nightly_seconds} reserved seconds.</p><p>Observed {timestamp(data.updated_at)}.</p></Panel>
      <div className="preview-grid">{(['runs', 'artifacts'] as const).map(group => <Panel key={group}><h2>{group === 'runs' ? 'Jobs' : 'Review artifacts'}</h2><dl className="facts">{Object.entries(data[group]).map(([state, total]) => <div key={state}><dt>{state.replaceAll('_', ' ')}</dt><dd>{total.toLocaleString()}</dd></div>)}</dl></Panel>)}</div>
    </>}</QueryView></>;
}
