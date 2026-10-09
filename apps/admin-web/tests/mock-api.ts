import { vi } from 'vitest';
import { decodeCapabilities } from '../src/api/decode';
import type { AdaApi } from '../src/api/types';
import capabilities from '../../../contracts/fixtures/capabilities-current.json';

// Test-only adapter. Production modules never import tests or canonical fixtures.
export const ownerA = '00000000-0000-0000-0000-000000000001';
export function mockApi(owner = ownerA): AdaApi {
  return {
    me: vi.fn(async () => ({ id: owner, name: 'Synthetic account' })),
    capabilities: vi.fn(async () => decodeCapabilities(capabilities)),
    requestStatus: vi.fn(),
    disconnect: vi.fn(),
  };
}
