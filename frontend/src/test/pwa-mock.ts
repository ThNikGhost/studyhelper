import { vi } from 'vitest'

/**
 * Shared PWA register mock state.
 * Override `needRefresh` / `offlineReady` in individual tests,
 * reset happens automatically in setup.ts afterEach.
 */
export const pwaRegisterMock = {
  needRefresh: false,
  offlineReady: false,
  setNeedRefresh: vi.fn(),
  setOfflineReady: vi.fn(),
  updateServiceWorker: vi.fn(),
}
