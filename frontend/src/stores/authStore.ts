import * as Sentry from '@sentry/react'
import { create } from 'zustand'
import api from '@/lib/api'
import type { AuthState, RegisterRequest, TokenResponse, User } from '@/types/auth'

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true })
    try {
      const formData = new URLSearchParams()
      formData.append('username', username)
      formData.append('password', password)

      const response = await api.post<TokenResponse>('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      // Fetch user after login
      const userResponse = await api.get<User>('/auth/me')
      Sentry.setUser({ id: String(userResponse.data.id) })
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true })
    try {
      // Register returns UserResponse, not tokens
      await api.post('/auth/register', data)

      // Login after successful registration
      const formData = new URLSearchParams()
      formData.append('username', data.email)
      formData.append('password', data.password)

      const loginResponse = await api.post<TokenResponse>('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      localStorage.setItem('access_token', loginResponse.data.access_token)
      localStorage.setItem('refresh_token', loginResponse.data.refresh_token)

      // Fetch user after login
      const userResponse = await api.get<User>('/auth/me')
      Sentry.setUser({ id: String(userResponse.data.id) })
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({ isLoading: false })
      throw error
    }
  },

  logout: async () => {
    try {
      await api.post('/auth/logout')
    } catch {
      // Ignore errors on logout
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      Sentry.setUser(null)
      set({ user: null, isAuthenticated: false })
    }
  },

  fetchUser: async () => {
    if (!localStorage.getItem('access_token')) {
      set({ user: null, isAuthenticated: false })
      return
    }

    set({ isLoading: true })
    try {
      const response = await api.get<User>('/auth/me')
      Sentry.setUser({ id: String(response.data.id) })
      set({ user: response.data, isAuthenticated: true, isLoading: false })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  setUser: (user: User | null) => set({ user, isAuthenticated: !!user }),
}))
