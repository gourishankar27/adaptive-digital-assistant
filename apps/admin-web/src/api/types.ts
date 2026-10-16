import type { components } from './generated';

// Generated schemas cover every actual route, including currently deferred UI writes.
export type { components, paths, operations } from './generated';
export type Dto<Name extends keyof components['schemas']> = components['schemas'][Name];
export type User = Pick<Dto<'UserOutput'>, 'id' | 'name'> & { data_epoch?: number };
export type Capabilities = Pick<Dto<'CapabilitiesOutput'>, 'api_version' | 'authority' | 'provider' | 'model' | 'chat' | 'streaming' | 'tools'> &
  Partial<Omit<Dto<'CapabilitiesOutput'>, 'api_version' | 'authority' | 'provider' | 'model' | 'chat' | 'streaming' | 'tools' | 'memory_writes' | 'memory_retrieval'>> & {
    memory_writes?: string; memory_retrieval?: string;
  };
export type Citation = Omit<Dto<'CitationOutput'>, 'kind' | 'origin'> & { kind: string; origin: string };
export type RequestRecord = Omit<Dto<'RequestOutput'>, 'status' | 'citations'> & { status: string; citations: Citation[] };
export type ObservedRequestState =
  | { kind: 'running' | 'completed' | 'failed' }
  | { kind: 'unknown'; value: string };

export function observeRequestState(status: string): ObservedRequestState {
  return status === 'running' || status === 'completed' || status === 'failed'
    ? { kind: status } : { kind: 'unknown', value: status };
}

export type ConnectionInfo = { server: string; user: User; capabilities: Capabilities };
export interface AdaApi {
  me(signal?: AbortSignal): Promise<User>;
  capabilities(signal?: AbortSignal): Promise<Capabilities>;
  requestStatus(requestId: string, signal?: AbortSignal): Promise<RequestRecord>;
  disconnect(): void;
}
