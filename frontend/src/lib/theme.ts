/**
 * Theme management utilities (framework-agnostic).
 *
 * Handles system preference detection and DOM updates
 * for light/dark theme switching.
 *
 * Note: Theme persistence is now handled by useUserSettings hook
 * (server sync) and useLocalSettingsStore (local fallback).
 */

import type { ThemeMode } from '@/types/auth'

// Re-export for backwards compatibility
export type { ThemeMode }

const STORAGE_KEY = 'studyhelper-local-settings'
const DARK_THEME_COLOR = '#0a0f1f'
const LIGHT_THEME_COLOR = '#3B82F6'

/**
 * Read saved theme from localStorage (for FOUC prevention).
 *
 * @returns Saved ThemeMode or 'system' as default.
 */
export function getSavedTheme(): ThemeMode {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored) as { themeMode?: string }
      if (
        parsed.themeMode === 'light' ||
        parsed.themeMode === 'dark' ||
        parsed.themeMode === 'system'
      ) {
        return parsed.themeMode
      }
    }
  } catch {
    // localStorage unavailable (SSR, private browsing, etc.)
  }
  return 'system'
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
