import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getSavedTheme, saveTheme, resolveTheme, applyTheme } from '../theme'

describe('getSavedTheme', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns "system" when no saved theme', () => {
    expect(getSavedTheme()).toBe('system')
  })

  it('returns saved "dark" theme', () => {
    localStorage.setItem('studyhelper-theme', 'dark')
    expect(getSavedTheme()).toBe('dark')
  })

  it('returns saved "light" theme', () => {
    localStorage.setItem('studyhelper-theme', 'light')
    expect(getSavedTheme()).toBe('light')
  })

  it('returns "system" for invalid stored value', () => {
    localStorage.setItem('studyhelper-theme', 'invalid')
    expect(getSavedTheme()).toBe('system')
  })
})

describe('saveTheme', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('persists theme to localStorage', () => {
    saveTheme('dark')
    expect(localStorage.getItem('studyhelper-theme')).toBe('dark')
  })

  it('overwrites previous value', () => {
    saveTheme('dark')
    saveTheme('light')
    expect(localStorage.getItem('studyhelper-theme')).toBe('light')
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
