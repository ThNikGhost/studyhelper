/**
 * Local settings store with localStorage persistence.
 *
 * Used as fallback when user is not authenticated.
 * When authenticated, settings sync to server via useUserSettings hook.
 *
 * Also used for theme FOUC prevention (theme needs to be applied
 * before React hydration, so we read from localStorage directly).
 */

import { create } from 'zustand'
import type { ThemeMode } from '@/types/auth'

const STORAGE_KEY = 'studyhelper-local-settings'

interface LocalSettingsState {
  /** User's subgroup (1, 2, ...) or null to show all. */
  subgroup: number | null

  /** Preferred PE teacher name or null to show all. */
  peTeacher: string | null

  /** Theme mode for FOUC prevention. */
  themeMode: ThemeMode

  /** Set user's subgroup preference. */
  setSubgroup: (value: number | null) => void

  /** Set preferred PE teacher. */
  setPeTeacher: (value: string | null) => void

  /** Set theme mode. */
  setThemeMode: (value: ThemeMode) => void
}

interface StoredSettings {
  subgroup: number | null
  peTeacher: string | null
  themeMode: ThemeMode
}

/** Read settings from localStorage. */
function readFromStorage(): StoredSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) {
      return { subgroup: null, peTeacher: null, themeMode: 'system' }
    }
    const parsed = JSON.parse(stored) as Partial<StoredSettings>
    return {
      subgroup: parsed.subgroup ?? null,
      peTeacher: parsed.peTeacher ?? null,
      themeMode: parsed.themeMode ?? 'system',
    }
  } catch {
    return { subgroup: null, peTeacher: null, themeMode: 'system' }
  }
}

/** Save settings to localStorage. */
function saveToStorage(settings: StoredSettings): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {
    // localStorage may be unavailable
  }
}

export const useLocalSettingsStore = create<LocalSettingsState>((set, get) => {
  const initial = readFromStorage()

  return {
    subgroup: initial.subgroup,
    peTeacher: initial.peTeacher,
    themeMode: initial.themeMode,

    setSubgroup: (value) => {
      set({ subgroup: value })
      saveToStorage({ ...get(), subgroup: value })
    },

    setPeTeacher: (value) => {
      set({ peTeacher: value })
      saveToStorage({ ...get(), peTeacher: value })
    },

    setThemeMode: (value) => {
      set({ themeMode: value })
      saveToStorage({ ...get(), themeMode: value })
    },
  }
})

/**
 * @deprecated Use useUserSettings() hook instead for server-synced settings.
 * This alias is kept for backwards compatibility during migration.
 */
export const useSettingsStore = useLocalSettingsStore
