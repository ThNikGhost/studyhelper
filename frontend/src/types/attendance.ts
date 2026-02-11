// Attendance types matching backend schemas

export interface AttendanceEntry {
  id: number
  lesson_date: string | null
  subject_name: string
  lesson_type: string
  start_time: string
  end_time: string
  teacher_name: string | null
  room: string | null
  subject_id: number | null
  is_absent: boolean
  absence_id: number | null
}

export interface AbsenceRecord {
  id: number
  user_id: number
  schedule_entry_id: number
  created_at: string
}

export interface SubjectAttendanceStats {
  subject_name: string
  subject_id: number | null
  planned_classes: number
  total_classes: number
  absences: number
  attended: number
  attendance_percent: number
}

export interface AttendanceStats {
  total_planned: number
  total_completed: number
  total_classes: number // backwards compat
  absences: number
  attended: number
  attendance_percent: number
  by_subject: SubjectAttendanceStats[]
}
