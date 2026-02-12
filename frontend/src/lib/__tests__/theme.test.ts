import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getSavedTheme, resolveTheme, applyTheme } from '../theme'

const STORAGE_KEY = 'studyhelper-local-settings'

describe('getSavedTheme', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns "system" when no saved settings', () => {
    expect(getSavedTheme()).toBe('system')
  })

  it('returns saved "dark" theme from JSON settings', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'dark' }))
    expect(getSavedTheme()).toBe('dark')
  })

  it('returns saved "light" theme from JSON settings', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'light' }))
    expect(getSavedTheme()).toBe('light')
  })

  it('returns "system" for invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'invalid json')
    expect(getSavedTheme()).toBe('system')
  })

  it('returns "system" for invalid themeMode value', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeMode: 'invalid' }))
    expect(getSavedTheme()).toBe('system')
  })

  it('returns "system" when themeMode is missing', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ subgroup: 1 }))
    expect(getSavedTheme()).toBe('system')
  })
})

describe('resolveTheme', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns "light" for light mode', () => {
    expect(resolveTheme('light')).toBe('light')
  })

  it('returns "dark" for dark mode', () => {
    expect(resolveTheme('dark')).toBe('dark')
  })

  it('returns "dark" for system when OS prefers dark', () => {
    vi.spyOn(window, 'matchMedia').mockReturnValue({
      matches: true,
    } as MediaQueryList)
    expect(resolveTheme('system')).toBe('dark')
  })

  it('returns "light" for system when OS prefers light', () => {
    vi.spyOn(window, 'matchMedia').mockReturnValue({
      matches: false,
    } as MediaQueryList)
    expect(resolveTheme('system')).toBe('light')
  })
})

describe('applyTheme', () => {
  afterEach(() => {
    document.documentElement.classList.remove('dark')
    vi.restoreAllMocks()
  })

  it('adds .dark class for dark mode', () => {
    applyTheme('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('removes .dark class for light mode', () => {
    document.documentElement.classList.add('dark')
    applyTheme('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('updates theme-color meta tag for dark', () => {
    const meta = document.createElement('meta')
    meta.name = 'theme-color'
    meta.content = '#3B82F6'
    document.head.appendChild(meta)

    applyTheme('dark')
    expect(meta.content).toBe('#0a0f1f')

    document.head.removeChild(meta)
  })

  it('updates theme-color meta tag for light', () => {
    const meta = document.createElement('meta')
    meta.name = 'theme-color'
    meta.content = '#0a0f1f'
    document.head.appendChild(meta)

    applyTheme('light')
    expect(meta.content).toBe('#3B82F6')

    document.head.removeChild(meta)
  })
})
