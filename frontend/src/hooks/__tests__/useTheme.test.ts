import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { useTheme } from '../useTheme'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => {
    document.documentElement.classList.remove('dark')
    vi.restoreAllMocks()
  })

  it('initializes with system mode by default', () => {
    const { result } = renderHook(() => useTheme())
    expect(result.current.mode).toBe('system')
  })

  it('initializes with saved mode from localStorage', () => {
    localStorage.setItem('studyhelper-theme', 'dark')
    const { result } = renderHook(() => useTheme())
    expect(result.current.mode).toBe('dark')
  })

  it('applies dark class when mode is dark', () => {
    const { result } = renderHook(() => useTheme())
    act(() => result.current.setTheme('dark'))
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('removes dark class when mode is light', () => {
    document.documentElement.classList.add('dark')
    const { result } = renderHook(() => useTheme())
    act(() => result.current.setTheme('light'))
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('persists theme to localStorage on change', () => {
    const { result } = renderHook(() => useTheme())
    act(() => result.current.setTheme('dark'))
    expect(localStorage.getItem('studyhelper-theme')).toBe('dark')
  })

  it('returns resolvedTheme matching current mode', () => {
    const { result } = renderHook(() => useTheme())
    act(() => result.current.setTheme('dark'))
    expect(result.current.resolvedTheme).toBe('dark')

    act(() => result.current.setTheme('light'))
    expect(result.current.resolvedTheme).toBe('light')
  })
})
