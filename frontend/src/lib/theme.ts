/**
 * Theme management utilities (framework-agnostic).
 *
 * Handles localStorage persistence, system preference detection,
 * and DOM updates for light/dark theme switching.
 */

export type ThemeMode = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'studyhelper-theme'
const DARK_THEME_COLOR = '#0a0f1f'
const LIGHT_THEME_COLOR = '#3B82F6'

/**
 * Read saved theme from localStorage.
 *
 * @returns Saved ThemeMode or 'system' as default.
 */
export function getSavedTheme(): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored
    }
  } catch {
    // localStorage unavailable (SSR, private browsing, etc.)
  }
  return 'system'
}

/**
 * Persist theme choice to localStorage.
 */
export function saveTheme(mode: ThemeMode): void {
  try {
    localStorage.setItem(STORAGE_KEY, mode)
  } catch {
    // localStorage unavailable
  }
}

/**
 * Resolve 'system' to actual 'light' or 'dark' based on OS preference.
 */
export function resolveTheme(mode: ThemeMode): 'light' | 'dark' {
  if (mode === 'light' || mode === 'dark') return mode
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/**
 * Apply theme to the DOM: toggle .dark class on <html> and update theme-color meta.
 */
export function applyTheme(mode: ThemeMode): void {
  const resolved = resolveTheme(mode)
  const root = document.documentElement

  if (resolved === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }

  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]')
  if (meta) {
    meta.content = resolved === 'dark' ? DARK_THEME_COLOR : LIGHT_THEME_COLOR
  }
}
