// Schedule types matching backend schemas

export enum LessonType {
  LECTURE = 'lecture',
  PRACTICE = 'practice',
  LAB = 'lab',
  SEMINAR = 'seminar',
  EXAM = 'exam',
  CONSULTATION = 'consultation',
  OTHER = 'other',
}

export enum DayOfWeek {
  MONDAY = 1,
  TUESDAY = 2,
  WEDNESDAY = 3,
  THURSDAY = 4,
  FRIDAY = 5,
  SATURDAY = 6,
  SUNDAY = 7,
}

export enum WeekType {
  ODD = 'odd',
  EVEN = 'even',
}

export interface ScheduleEntry {
  id: number
  day_of_week: DayOfWeek
  start_time: string // HH:MM:SS format
  end_time: string
  week_type: WeekType | null
  subject_name: string
  lesson_type: LessonType
  teacher_name: string | null
  room: string | null
  building: string | null
  group_name: string | null
  subgroup: number | null
  notes: string | null
  subject_id: number | null
  teacher_id: number | null
  created_at: string
  updated_at: string
}

export interface DaySchedule {
  date: string // YYYY-MM-DD
  day_of_week: DayOfWeek
  day_name: string
  entries: ScheduleEntry[]
}

export interface WeekSchedule {
  week_start: string
  week_end: string
  week_number: number
  is_odd_week: boolean
  days: DaySchedule[]
}

export interface CurrentLesson {
  current: ScheduleEntry | null
  next: ScheduleEntry | null
  time_until_next: number | null
}

// Helper to get lesson type label in Russian
export const lessonTypeLabels: Record<LessonType, string> = {
  [LessonType.LECTURE]: 'Лекция',
  [LessonType.PRACTICE]: 'Практика',
  [LessonType.LAB]: 'Лаб. работа',
  [LessonType.SEMINAR]: 'Семинар',
  [LessonType.EXAM]: 'Экзамен',
  [LessonType.CONSULTATION]: 'Консультация',
  [LessonType.OTHER]: 'Другое',
}

// Helper to get day name in Russian
export const dayNames: Record<DayOfWeek, string> = {
  [DayOfWeek.MONDAY]: 'Понедельник',
  [DayOfWeek.TUESDAY]: 'Вторник',
  [DayOfWeek.WEDNESDAY]: 'Среда',
  [DayOfWeek.THURSDAY]: 'Четверг',
  [DayOfWeek.FRIDAY]: 'Пятница',
  [DayOfWeek.SATURDAY]: 'Суббота',
  [DayOfWeek.SUNDAY]: 'Воскресенье',
}

// Helper to get short day name
export const dayNamesShort: Record<DayOfWeek, string> = {
  [DayOfWeek.MONDAY]: 'Пн',
  [DayOfWeek.TUESDAY]: 'Вт',
  [DayOfWeek.WEDNESDAY]: 'Ср',
  [DayOfWeek.THURSDAY]: 'Чт',
  [DayOfWeek.FRIDAY]: 'Пт',
  [DayOfWeek.SATURDAY]: 'Сб',
  [DayOfWeek.SUNDAY]: 'Вс',
}
