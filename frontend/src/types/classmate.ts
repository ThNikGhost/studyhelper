// Classmate types matching backend schemas

export interface ClassmateDetail {
  id: number
  classmate_id: number
  user_id: number
  short_name: string | null
  email: string | null
  phone: string | null
  telegram: string | null
  vk: string | null
  photo_url: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ClassmateBase {
  id: number
  full_name: string
  group_name: string | null
  subgroup: number | null
  created_at: string
  updated_at: string
}

export interface Classmate extends ClassmateBase {
  details: ClassmateDetail | null
}

export interface ClassmateCreate {
  full_name: string
  group_name?: string | null
  subgroup?: number | null
}

export interface ClassmateUpdate {
  full_name?: string
  group_name?: string | null
  subgroup?: number | null
}

export interface ClassmateDetailUpsert {
  short_name?: string | null
  email?: string | null
  phone?: string | null
  telegram?: string | null
  vk?: string | null
  photo_url?: string | null
  notes?: string | null
}
