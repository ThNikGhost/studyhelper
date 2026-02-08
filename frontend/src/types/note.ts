// Lesson note types matching backend schemas

export interface LessonNote {
  id: number
  user_id: number
  schedule_entry_id: number | null
  subject_name: string
  lesson_date: string | null
  content: string
  created_at: string
  updated_at: string
}

export interface LessonNoteCreate {
  schedule_entry_id?: number | null
  subject_name: string
  lesson_date?: string | null
  content: string
}

export interface LessonNoteUpdate {
  content: string
}
