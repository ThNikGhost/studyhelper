// Work types matching backend schemas

export const WorkType = {
  HOMEWORK: 'homework',
  LAB: 'lab',
  PRACTICE: 'practice',
  COURSE_WORK: 'course_work',
  REPORT: 'report',
  TEST: 'test',
  EXAM: 'exam',
  OTHER: 'other',
} as const

export type WorkType = (typeof WorkType)[keyof typeof WorkType]

export const WorkStatus = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  SUBMITTED: 'submitted',
  GRADED: 'graded',
} as const

export type WorkStatus = (typeof WorkStatus)[keyof typeof WorkStatus]

export interface Work {
  id: number
  title: string
  description: string | null
  work_type: WorkType
  deadline: string | null // ISO datetime
  max_grade: number | null
  subject_id: number
  created_at: string
  updated_at: string
}

export interface WorkStatusData {
  id: number
  work_id: number
  user_id: number
  status: WorkStatus
  grade: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface WorkWithStatus extends Work {
  my_status: WorkStatusData | null
}

export interface WorkCreate {
  title: string
  description?: string | null
  work_type: WorkType
  deadline?: string | null
  max_grade?: number | null
  subject_id: number
}

export interface WorkUpdate {
  title?: string
  description?: string | null
  work_type?: WorkType
  deadline?: string | null
  max_grade?: number | null
  subject_id?: number
}

export interface WorkStatusUpdate {
  status?: WorkStatus
  grade?: number | null
  notes?: string | null
}

export interface UpcomingWork {
  id: number
  title: string
  work_type: WorkType
  deadline: string
  subject_id: number
  subject_name: string
  my_status: WorkStatus | null
}

// Helper labels
export const workTypeLabels: Record<WorkType, string> = {
  [WorkType.HOMEWORK]: 'Домашнее задание',
  [WorkType.LAB]: 'Лабораторная',
  [WorkType.PRACTICE]: 'Практика',
  [WorkType.COURSE_WORK]: 'Курсовая',
  [WorkType.REPORT]: 'Реферат',
  [WorkType.TEST]: 'Контрольная',
  [WorkType.EXAM]: 'Экзамен',
  [WorkType.OTHER]: 'Другое',
}

export const workStatusLabels: Record<WorkStatus, string> = {
  [WorkStatus.NOT_STARTED]: 'Не начато',
  [WorkStatus.IN_PROGRESS]: 'В процессе',
  [WorkStatus.COMPLETED]: 'Выполнено',
  [WorkStatus.SUBMITTED]: 'Сдано',
  [WorkStatus.GRADED]: 'Оценено',
}

export const workStatusColors: Record<WorkStatus, string> = {
  [WorkStatus.NOT_STARTED]: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
  [WorkStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
  [WorkStatus.COMPLETED]: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
  [WorkStatus.SUBMITTED]: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
  [WorkStatus.GRADED]: 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
}
