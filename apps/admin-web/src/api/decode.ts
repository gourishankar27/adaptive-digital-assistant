import { parse, isInteger, isSafeNumber, LosslessNumber } from 'lossless-json';
import type { Capabilities, Citation, RequestRecord, User } from './types';

export class ContractError extends Error {
  constructor() { super('The server response is incompatible with this client.'); }
}

export function parseWire(text: string): unknown {
  try {
    return parse(text, undefined, value => isSafeNumber(value) ? Number(value) : isInteger(value) ? BigInt(value) : new LosslessNumber(value));
  } catch { throw new ContractError(); }
}

export function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new ContractError();
  return value as Record<string, unknown>;
}
function text(value: unknown): string {
  if (typeof value !== 'string') throw new ContractError();
  return value;
}
export function uuid(value: unknown): string {
  const result = text(value);
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(result)) throw new ContractError();
  return result;
}
function bool(value: unknown): boolean {
  if (typeof value !== 'boolean') throw new ContractError();
  return value;
}
function integer(value: unknown, minimum = 0): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < minimum) throw new ContractError();
  return value;
}
export function millis(value: unknown): bigint {
  if (typeof value === 'number' && !Number.isSafeInteger(value)) throw new ContractError();
  if (typeof value !== 'number' && typeof value !== 'bigint') throw new ContractError();
  const result = BigInt(value);
  if (result < -(2n ** 63n) || result > 2n ** 63n - 1n) throw new ContractError();
  return result;
}
function optionalText(value: unknown): string | null { return value == null ? null : text(value); }
function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) throw new ContractError();
  return value.map(text);
}

export function decodeUser(value: unknown): User {
  const row = record(value);
  return { id: uuid(row.id), name: text(row.name) };
}

export function decodeCapabilities(value: unknown): Capabilities {
  const row = record(value);
  if (row.api_version !== 'v1' || row.authority !== 'server') throw new ContractError();
  const result: Capabilities = {
    api_version: 'v1', authority: 'server', provider: text(row.provider), model: text(row.model),
    chat: bool(row.chat), streaming: bool(row.streaming), tools: bool(row.tools),
  };
  for (const key of ['structured_memory', 'memory_in_chat', 'memory_citations', 'retrieval_traces', 'automatic_memory_extraction', 'historical_memory_queries', 'private_project_scopes', 'shared_scopes', 'edge_inference', 'personality_isolation'] as const) {
    if (row[key] !== undefined) result[key] = bool(row[key]);
  }
  for (const key of ['memory_writes', 'memory_retrieval', 'chat_prompt_version'] as const) {
    if (row[key] !== undefined) result[key] = text(row[key]);
  }
  return result;
}

export function decodeCitation(value: unknown): Citation {
  const row = record(value), evidence = record(row.evidence);
  const spanStart = integer(evidence.span_start), spanEnd = integer(evidence.span_end, 1);
  if (spanEnd <= spanStart) throw new ContractError();
  const quote = text(evidence.quote);
  if (Array.from(quote).length !== spanEnd - spanStart) throw new ContractError();
  const hash = text(evidence.content_hash);
  if (!/^[a-f0-9]{64}$/.test(hash)) throw new ContractError();
  return {
    label: text(row.label), claim_id: uuid(row.claim_id), scope_id: uuid(row.scope_id),
    subject: text(row.subject), predicate: text(row.predicate), value: text(row.value),
    kind: text(row.kind), origin: text(row.origin), valid_from: millis(row.valid_from),
    valid_to: row.valid_to == null ? null : millis(row.valid_to),
    evidence: { source_version_id: uuid(evidence.source_version_id), span_start: spanStart, span_end: spanEnd, quote, content_hash: hash },
    source_id: uuid(row.source_id), source_version: integer(row.source_version, 1), conflict: bool(row.conflict),
  };
}

export function decodeRequest(value: unknown): RequestRecord {
  const row = record(value);
  if (row.citations !== undefined && !Array.isArray(row.citations)) throw new ContractError();
  return {
    request_id: uuid(row.request_id), conversation_id: uuid(row.conversation_id), status: text(row.status),
    response: optionalText(row.response), error_code: optionalText(row.error_code), attempt: integer(row.attempt, 1),
    provider: text(row.provider), model: text(row.model),
    input_tokens: row.input_tokens == null ? null : integer(row.input_tokens),
    output_tokens: row.output_tokens == null ? null : integer(row.output_tokens),
    citations: (row.citations as unknown[] | undefined)?.map(decodeCitation) ?? [],
    citation_warnings: row.citation_warnings === undefined ? [] : stringList(row.citation_warnings),
  };
}

// Selection boundaries in a browser are UTF-16. The API expects Unicode code points.
export function codePointOffset(content: string, utf16Offset: number): number {
  if (!Number.isInteger(utf16Offset) || utf16Offset < 0 || utf16Offset > content.length) throw new ContractError();
  if (utf16Offset > 0 && utf16Offset < content.length && /[\uD800-\uDBFF]/.test(content[utf16Offset - 1]) && /[\uDC00-\uDFFF]/.test(content[utf16Offset])) throw new ContractError();
  return Array.from(content.slice(0, utf16Offset)).length;
}

export function sourceForLabel(request: RequestRecord, label: string): Citation | undefined {
  return request.citations.find(citation => citation.label === label);
}
