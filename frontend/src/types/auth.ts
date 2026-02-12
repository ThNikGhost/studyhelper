export type ThemeMode = 'light' | 'dark' | 'system'

export interface User {
  id: number
  email: string
  name: string
  avatar_url: string | null
  preferred_subgroup: number | null
  preferred_pe_teacher: string | null
  theme_mode: ThemeMode | null
  created_at: string
  updated_at: string
}

export interface UserSettingsUpdate {
  preferred_subgroup?: number | null
  preferred_pe_teacher?: string | null
  theme_mode?: ThemeMode | null
}

export interface RegisterRequest {
  email: string
  name: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  fetchUser: () => Promise<void>
  setUser: (user: User | null) => void
}
