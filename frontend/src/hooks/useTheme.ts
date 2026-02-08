import { useState, useEffect, useCallback } from 'react'
import {
  type ThemeMode,
  getSavedTheme,
  saveTheme,
  applyTheme,
  resolveTheme,
} from '@/lib/theme'

interface UseThemeReturn {
  mode: ThemeMode
  resolvedTheme: 'light' | 'dark'
  setTheme: (mode: ThemeMode) => void
}

/**
 * React hook for theme management.
 *
 * Persists choice to localStorage, applies .dark class,
 * and listens for system preference changes when mode is 'system'.
 */
export function useTheme(): UseThemeReturn {
  const [mode, setMode] = useState<ThemeMode>(getSavedTheme)

  const setTheme = useCallback((newMode: ThemeMode) => {
    setMode(newMode)
  }, [])

  // Apply theme and persist on mode change
  useEffect(() => {
    applyTheme(mode)
    saveTheme(mode)
  }, [mode])

  // Listen for OS preference changes when mode is 'system'
  useEffect(() => {
    if (mode !== 'system') return

    const mql = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => applyTheme('system')

    mql.addEventListener('change', handler)
    return () => mql.removeEventListener('change', handler)
  }, [mode])

  return { mode, resolvedTheme: resolveTheme(mode), setTheme }
}
