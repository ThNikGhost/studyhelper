/**
 * User settings store with localStorage persistence.
 *
 * Manages user preferences like subgroup and PE teacher selection.
 * Settings are device-specific (stored in localStorage, not synced to server).
 */

import { create } from 'zustand'

const SUBGROUP_STORAGE_KEY = 'user_subgroup'
const PE_TEACHER_STORAGE_KEY = 'pe_preferred_teacher'

interface SettingsState {
  /** User's subgroup (1, 2, ...) or null to show all. */
  subgroup: number | null

  /** Preferred PE teacher name or null to show all. */
  peTeacher: string | null

  /** Set user's subgroup preference. */
  setSubgroup: (value: number | null) => void

  /** Set preferred PE teacher. */
  setPeTeacher: (value: string | null) => void
}

/** Read number from localStorage, return null if not found or invalid. */
function readSubgroupFromStorage(): number | null {
  try {
    const stored = localStorage.getItem(SUBGROUP_STORAGE_KEY)
    if (!stored) return null
    const parsed = parseInt(stored, 10)
    return Number.isNaN(parsed) ? null : parsed
  } catch {
    return null
  }
}

/** Read string from localStorage, return null if not found. */
function readPeTeacherFromStorage(): string | null {
  try {
    return localStorage.getItem(PE_TEACHER_STORAGE_KEY)
  } catch {
    return null
  }
}

/** Save subgroup to localStorage. */
function saveSubgroupToStorage(value: number | null): void {
  try {
    if (value !== null) {
      localStorage.setItem(SUBGROUP_STORAGE_KEY, String(value))
    } else {
      localStorage.removeItem(SUBGROUP_STORAGE_KEY)
    }
  } catch {
    // localStorage may be unavailable
  }
}

/** Save PE teacher to localStorage. */
function savePeTeacherToStorage(value: string | null): void {
  try {
    if (value) {
      localStorage.setItem(PE_TEACHER_STORAGE_KEY, value)
    } else {
      localStorage.removeItem(PE_TEACHER_STORAGE_KEY)
    }
  } catch {
    // localStorage may be unavailable
  }
}

export const useSettingsStore = create<SettingsState>((set) => ({
  subgroup: readSubgroupFromStorage(),
  peTeacher: readPeTeacherFromStorage(),

  setSubgroup: (value) => {
    saveSubgroupToStorage(value)
    set({ subgroup: value })
  },

  setPeTeacher: (value) => {
    savePeTeacherToStorage(value)
    set({ peTeacher: value })
  },
}))
