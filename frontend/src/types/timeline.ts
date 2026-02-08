import type { Semester } from '@/types/subject'

export interface TimelineDeadline {
  work_id: number
  title: string
  work_type: string
  deadline: string
  subject_name: string
  subject_id: number
  status: string | null
}

export interface TimelineExam {
  schedule_entry_id: number
  subject_name: string
  lesson_date: string
  start_time: string
  end_time: string
  room: string | null
  teacher_name: string | null
}

export interface TimelineData {
  semester: Semester
  deadlines: TimelineDeadline[]
  exams: TimelineExam[]
}
