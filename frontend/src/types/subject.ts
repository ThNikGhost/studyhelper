// Subject and Semester types matching backend schemas

export interface Semester {
  id: number
  number: number
  year_start: number
  year_end: number
  name: string
  is_current: boolean
  start_date: string | null
  end_date: string | null
  created_at: string
  updated_at: string
}

export interface SemesterCreate {
  number: number
  year_start: number
  year_end: number
  name: string
  start_date?: string | null
  end_date?: string | null
}

export interface SemesterUpdate {
  number?: number
  year_start?: number
  year_end?: number
  name?: string
  start_date?: string | null
  end_date?: string | null
}

export interface Subject {
  id: number
  name: string
  short_name: string | null
  description: string | null
  semester_id: number
  planned_classes: number | null
  total_hours: number | null
  created_at: string
  updated_at: string
}

export interface SubjectCreate {
  name: string
  short_name?: string | null
  description?: string | null
  semester_id: number
  planned_classes?: number | null
  total_hours?: number | null
}

export interface SubjectUpdate {
  name?: string
  short_name?: string | null
  description?: string | null
  semester_id?: number
  planned_classes?: number | null
  total_hours?: number | null
}
