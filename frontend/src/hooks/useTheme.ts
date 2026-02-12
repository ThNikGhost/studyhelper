import { useEffect, useCallback } from 'react'
import { applyTheme, resolveTheme } from '@/lib/theme'
import { useUserSettings } from '@/hooks/useUserSettings'
import type { ThemeMode } from '@/types/auth'

interface UseThemeReturn {
  mode: ThemeMode
  resolvedTheme: 'light' | 'dark'
  setTheme: (mode: ThemeMode) => void
}

/**
 * React hook for theme management with server sync.
 *
 * When authenticated, syncs theme to server.
 * Applies .dark class and listens for system preference changes.
 */
export function useTheme(): UseThemeReturn {
  const { settings, updateSettings } = useUserSettings()
  const mode = settings.themeMode

  const setTheme = useCallback(
    (newMode: ThemeMode) => {
      updateSettings({ theme_mode: newMode })
    },
    [updateSettings]
  )

  // Apply theme on mode change
  useEffect(() => {
    applyTheme(mode)
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
