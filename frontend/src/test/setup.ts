import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import { server } from './mocks/server'
import { pwaRegisterMock } from './pwa-mock'

// Mock virtual:pwa-register/react using shared mock state
vi.mock('virtual:pwa-register/react', () => ({
  useRegisterSW: () => ({
    needRefresh: [pwaRegisterMock.needRefresh, pwaRegisterMock.setNeedRefresh],
    offlineReady: [pwaRegisterMock.offlineReady, pwaRegisterMock.setOfflineReady],
    updateServiceWorker: pwaRegisterMock.updateServiceWorker,
  }),
}))

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
    get length() {
      return Object.keys(store).length
    },
    key: (index: number) => Object.keys(store)[index] ?? null,
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
})

// MSW server lifecycle
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => {
  server.resetHandlers()
  cleanup()
  localStorage.clear()
  // Reset PWA mock to defaults
  pwaRegisterMock.needRefresh = false
  pwaRegisterMock.offlineReady = false
  pwaRegisterMock.setNeedRefresh.mockClear()
  pwaRegisterMock.setOfflineReady.mockClear()
  pwaRegisterMock.updateServiceWorker.mockClear()
})
afterAll(() => server.close())
