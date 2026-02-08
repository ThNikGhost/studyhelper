// File types matching backend schemas

export const FileCategory = {
  TEXTBOOK: 'textbook',
  PROBLEM_SET: 'problem_set',
  LECTURE: 'lecture',
  LAB: 'lab',
  CHEATSHEET: 'cheatsheet',
  OTHER: 'other',
} as const

export type FileCategory = (typeof FileCategory)[keyof typeof FileCategory]

export const fileCategoryLabels: Record<FileCategory, string> = {
  [FileCategory.TEXTBOOK]: 'Учебник',
  [FileCategory.PROBLEM_SET]: 'Задачник',
  [FileCategory.LECTURE]: 'Лекция',
  [FileCategory.LAB]: 'Лабораторная',
  [FileCategory.CHEATSHEET]: 'Шпаргалка',
  [FileCategory.OTHER]: 'Другое',
}

/**
 * StudyFile — uploaded file record.
 * Named "StudyFile" to avoid conflict with the Web API File interface.
 */
export interface StudyFile {
  id: number
  filename: string
  stored_filename?: string
  mime_type: string
  size: number
  category: FileCategory
  subject_id: number | null
  subject_name: string | null
  uploaded_by: number
  created_at: string
}
