import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { ThemeToggle } from '../ThemeToggle'
import { useAuthStore } from '@/stores/authStore'
import { useLocalSettingsStore } from '@/stores/settingsStore'

const STORAGE_KEY = 'studyhelper-local-settings'

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false })
    useLocalSettingsStore.setState({ subgroup: null, peTeacher: null, themeMode: 'system' })
  })

  it('renders a button', () => {
    render(<ThemeToggle />, { wrapper: createWrapper() })
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('shows system theme aria-label by default', () => {
    render(<ThemeToggle />, { wrapper: createWrapper() })
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Системная тема')
  })

  it('cycles from system to light on click', async () => {
    render(<ThemeToggle />, { wrapper: createWrapper() })
    fireEvent.click(screen.getByRole('button'))
    await waitFor(() => {
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Светлая тема')
    })
  })

  it('cycles from light to dark on click', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'light' }))
    useLocalSettingsStore.setState({ themeMode: 'light' })
    render(<ThemeToggle />, { wrapper: createWrapper() })
    fireEvent.click(screen.getByRole('button'))
    await waitFor(() => {
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Тёмная тема')
    })
  })

  it('cycles from dark to system on click', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'dark' }))
    useLocalSettingsStore.setState({ themeMode: 'dark' })
    render(<ThemeToggle />, { wrapper: createWrapper() })
    fireEvent.click(screen.getByRole('button'))
    await waitFor(() => {
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Системная тема')
    })
  })

  it('applies dark class when cycling to dark', async () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'light' }))
    useLocalSettingsStore.setState({ themeMode: 'light' })
    render(<ThemeToggle />, { wrapper: createWrapper() })
    fireEvent.click(screen.getByRole('button'))
    await waitFor(() => {
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })
})
