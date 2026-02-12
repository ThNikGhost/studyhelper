import { renderHook, act, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { useTheme } from '../useTheme'
import { useAuthStore } from '@/stores/authStore'
import { useLocalSettingsStore } from '@/stores/settingsStore'

const STORAGE_KEY = 'studyhelper-local-settings'

// Helper to create wrapper with QueryClientProvider
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    // Reset auth store to unauthenticated state
    useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false })
    // Reset local settings store
    useLocalSettingsStore.setState({ subgroup: null, peTeacher: null, themeMode: 'system' })
  })

  afterEach(() => {
    document.documentElement.classList.remove('dark')
    vi.restoreAllMocks()
  })

  it('initializes with system mode by default', () => {
    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    expect(result.current.mode).toBe('system')
  })

  it('initializes with saved mode from localStorage when not authenticated', () => {
    // Set localStorage and update store to match
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'dark' }))
    useLocalSettingsStore.setState({ themeMode: 'dark' })
    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    expect(result.current.mode).toBe('dark')
  })

  it('applies dark class when mode is dark', async () => {
    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    act(() => result.current.setTheme('dark'))
    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })

  it('removes dark class when mode is light', async () => {
    document.documentElement.classList.add('dark')
    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    act(() => result.current.setTheme('light'))
    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(false)
    })
  })

  it('returns resolvedTheme matching current mode', async () => {
    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    act(() => result.current.setTheme('dark'))
    await waitFor(() => {
      expect(result.current.resolvedTheme).toBe('dark')
    })

    act(() => result.current.setTheme('light'))
    await waitFor(() => {
      expect(result.current.resolvedTheme).toBe('light')
    })
  })

  it('uses theme from user settings when authenticated', () => {
    useAuthStore.setState({
      user: {
        id: 1,
        email: 'test@example.com',
        name: 'Test',
        avatar_url: null,
        preferred_subgroup: null,
        preferred_pe_teacher: null,
        theme_mode: 'dark',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      isAuthenticated: true,
      isLoading: false,
    })

    const { result } = renderHook(() => useTheme(), { wrapper: createWrapper() })
    expect(result.current.mode).toBe('dark')
  })
})
