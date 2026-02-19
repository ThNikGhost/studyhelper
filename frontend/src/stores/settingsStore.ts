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

/** Hidden subjects config: subject ID → hidden lesson types (null = all). */
type HiddenSubjects = Record<string, string[] | null>

interface LocalSettingsState {
  /** User's subgroup (1, 2, ...) or null to show all. */
  subgroup: number | null

  /** Preferred PE teacher name or null to show all. */
  peTeacher: string | null

  /** Theme mode for FOUC prevention. */
  themeMode: ThemeMode

  /** Hidden subject IDs with per-type config. */
  hiddenSubjects: HiddenSubjects

  /** Set user's subgroup preference. */
  setSubgroup: (value: number | null) => void

  /** Set preferred PE teacher. */
  setPeTeacher: (value: string | null) => void

  /** Set theme mode. */
  setThemeMode: (value: ThemeMode) => void

  /** Set hidden subjects. */
  setHiddenSubjects: (value: HiddenSubjects) => void
}

interface StoredSettings {
  subgroup: number | null
  peTeacher: string | null
  themeMode: ThemeMode
  hiddenSubjects: HiddenSubjects
}

/** Read settings from localStorage with migration from old format. */
function readFromStorage(): StoredSettings {
  const defaults: StoredSettings = {
    subgroup: null,
    peTeacher: null,
    themeMode: 'system',
    hiddenSubjects: {},
  }
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return defaults
    const parsed = JSON.parse(stored) as Record<string, unknown>

    // Migrate old array format [1, 5] → {"1": null, "5": null}
    let hiddenSubjects: HiddenSubjects = {}
    if (Array.isArray(parsed.hiddenSubjects)) {
      for (const id of parsed.hiddenSubjects) {
        if (typeof id === 'number' && id > 0) {
          hiddenSubjects[String(id)] = null
        }
      }
    } else if (
      parsed.hiddenSubjects &&
      typeof parsed.hiddenSubjects === 'object' &&
      !Array.isArray(parsed.hiddenSubjects)
    ) {
      hiddenSubjects = parsed.hiddenSubjects as HiddenSubjects
    }

    return {
      subgroup: (parsed.subgroup as number | null) ?? null,
      peTeacher: (parsed.peTeacher as string | null) ?? null,
      themeMode: (parsed.themeMode as ThemeMode) ?? 'system',
      hiddenSubjects,
    }
  } catch {
    return defaults
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
    hiddenSubjects: initial.hiddenSubjects,

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

    setHiddenSubjects: (value) => {
      set({ hiddenSubjects: value })
      saveToStorage({ ...get(), hiddenSubjects: value })
    },
  }
})

/**
 * @deprecated Use useUserSettings() hook instead for server-synced settings.
 * This alias is kept for backwards compatibility during migration.
 */
export const useSettingsStore = useLocalSettingsStore
