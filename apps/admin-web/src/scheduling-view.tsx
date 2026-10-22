import type { AdminSession } from './admin-session';
import { Panel } from './components';
import { ContractError } from './api/decode';
import { QueryView, timestamp, useMonitor } from './monitor-query';

export function SchedulingView({ session }: { session: AdminSession }) {
  const query = useMonitor(session, 'scheduling', {}, (api, signal) => {
    if (!api.scheduling) return Promise.reject(new ContractError());
    return api.scheduling(signal);
  });
  return <><div className="page-intro"><p className="eyebrow">ADA / backend monitoring</p><h1>Scheduling</h1><p>Aggregate queue and delivery states. Reminder text, personal topics, sources and device registrations are excluded.</p></div>
    <QueryView query={query}>{data => <>
      <Panel><h2>Dispatcher</h2><p>{data.globally_enabled ? 'Enabled by global configuration' : 'Stopped by global configuration'}</p><p>{data.worker_running ? 'Dispatch loop running' : 'Dispatch loop not running'}</p><p>Process iteration errors: {data.process_error_count}. Last code: {data.last_error_code ?? 'None reported'}. These process counters reset on restart.</p><p>Observed {timestamp(data.updated_at)}.</p><p className="hint">Inbox delivery is durable. Foreground in-app polling is available; timely background push is not enabled. Counts do not prove that a person read a reminder.</p></Panel>
      <div className="preview-grid">{(['schedules', 'occurrences', 'inbox'] as const).map(group => <Panel key={group}><h2>{group[0].toUpperCase() + group.slice(1)}</h2><dl className="facts">{Object.entries(data[group]).map(([state, total]) => <div key={state}><dt>{state.replaceAll('_', ' ')}</dt><dd>{total.toLocaleString()}</dd></div>)}</dl></Panel>)}</div>
    </>}</QueryView></>;
}
