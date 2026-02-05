// Classmate types matching backend schemas

export interface Classmate {
  id: number
  full_name: string
  short_name: string | null
  email: string | null
  phone: string | null
  telegram: string | null
  vk: string | null
  photo_url: string | null
  group_name: string | null
  subgroup: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ClassmateCreate {
  full_name: string
  short_name?: string | null
  email?: string | null
  phone?: string | null
  telegram?: string | null
  vk?: string | null
  photo_url?: string | null
  group_name?: string | null
  subgroup?: number | null
  notes?: string | null
}

export interface ClassmateUpdate {
  full_name?: string
  short_name?: string | null
  email?: string | null
  phone?: string | null
  telegram?: string | null
  vk?: string | null
  photo_url?: string | null
  group_name?: string | null
  subgroup?: number | null
  notes?: string | null
}
