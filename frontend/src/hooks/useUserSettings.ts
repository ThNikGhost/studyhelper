/**
 * Hook for managing user settings with server sync.
 *
 * Uses TanStack Query for:
 * - Optimistic updates (instant UI feedback)
 * - Automatic rollback on error
 * - Refetch on reconnect/window focus
 *
 * Falls back to local-only mode when not authenticated.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { useLocalSettingsStore } from '@/stores/settingsStore'
import type { User, UserSettingsUpdate, ThemeMode } from '@/types/auth'

interface UserSettings {
  subgroup: number | null
  peTeacher: string | null
  themeMode: ThemeMode
}

interface UseUserSettingsReturn {
  settings: UserSettings
  updateSettings: (settings: UserSettingsUpdate) => void
  isUpdating: boolean
}

/**
 * Hook for user settings with server sync.
 *
 * When authenticated, settings sync to server.
 * When not authenticated, uses localStorage fallback.
 */
export function useUserSettings(): UseUserSettingsReturn {
  const queryClient = useQueryClient()
  const { user, isAuthenticated, setUser } = useAuthStore()
  const localSettings = useLocalSettingsStore()

  const mutation = useMutation({
    mutationFn: async (settings: UserSettingsUpdate) => {
      const response = await api.patch<User>('/auth/me/settings', settings)
      return response.data
    },

    // Optimistic update for instant UI
    onMutate: async (newSettings) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['user'] })

      // Snapshot current user
      const previousUser = user

      // Optimistically update authStore
      if (user) {
        const optimisticUser: User = {
          ...user,
          ...(newSettings.preferred_subgroup !== undefined && {
            preferred_subgroup: newSettings.preferred_subgroup ?? null,
          }),
          ...(newSettings.preferred_pe_teacher !== undefined && {
            preferred_pe_teacher: newSettings.preferred_pe_teacher ?? null,
          }),
          ...(newSettings.theme_mode !== undefined && {
            theme_mode: newSettings.theme_mode ?? null,
          }),
        }
        setUser(optimisticUser)
      }

      return { previousUser }
    },

    // Rollback on error
    onError: (_err, _vars, context) => {
      if (context?.previousUser) {
        setUser(context.previousUser)
      }
    },

    // Update with server response on success
    onSuccess: (updatedUser) => {
      setUser(updatedUser)

      // Also update local settings for FOUC prevention
      if (updatedUser.theme_mode) {
        localSettings.setThemeMode(updatedUser.theme_mode)
      }
    },
  })

  // Compute current settings
  const settings: UserSettings = isAuthenticated && user
    ? {
        subgroup: user.preferred_subgroup,
        peTeacher: user.preferred_pe_teacher,
        themeMode: user.theme_mode ?? 'system',
      }
    : {
        subgroup: localSettings.subgroup,
        peTeacher: localSettings.peTeacher,
        themeMode: localSettings.themeMode,
      }

  // Update function that handles both authenticated and local modes
  const updateSettings = (newSettings: UserSettingsUpdate) => {
    if (isAuthenticated) {
      mutation.mutate(newSettings)
    } else {
      // Local-only update
      if (newSettings.preferred_subgroup !== undefined) {
        localSettings.setSubgroup(newSettings.preferred_subgroup)
      }
      if (newSettings.preferred_pe_teacher !== undefined) {
        localSettings.setPeTeacher(newSettings.preferred_pe_teacher)
      }
      if (newSettings.theme_mode !== undefined) {
        localSettings.setThemeMode(newSettings.theme_mode ?? 'system')
      }
    }
  }

  return {
    settings,
    updateSettings,
    isUpdating: mutation.isPending,
  }
}
