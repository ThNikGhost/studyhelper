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
  /** Captured onRegisteredSW callback from last useRegisterSW call. */
  onRegisteredSW: null as ((swUrl: string, registration: unknown) => void) | null,
}
