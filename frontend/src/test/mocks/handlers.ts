import { http, HttpResponse } from 'msw'
import type { User, TokenResponse } from '@/types/auth'
import type { StudyFile } from '@/types/file'
import type { CurrentLesson, DaySchedule, ScheduleEntry } from '@/types/schedule'
import type { Subject } from '@/types/subject'
import type { UpcomingWork, WorkWithStatus } from '@/types/work'

// Test data factories
export const testUser: User = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  avatar_url: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

export const testTokens: TokenResponse = {
  access_token: 'test-access-token',
  refresh_token: 'test-refresh-token',
  token_type: 'bearer',
}

export const testScheduleEntries: ScheduleEntry[] = [
  {
    id: 10,
    lesson_date: '2026-02-07',
    day_of_week: 6,
    start_time: '08:30:00',
    end_time: '10:05:00',
    week_type: null,
    subject_name: 'Физика',
    lesson_type: 'lecture',
    teacher_name: 'Петров П.П.',
    room: '201',
    building: 'Корпус 2',
    group_name: 'ПИ-101',
    subgroup: null,
    notes: null,
    subject_id: 2,
    teacher_id: 2,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 1,
    lesson_date: '2026-02-07',
    day_of_week: 6,
    start_time: '10:30:00',
    end_time: '12:05:00',
    week_type: null,
    subject_name: 'Математический анализ',
    lesson_type: 'lecture',
    teacher_name: 'Иванов И.И.',
    room: '301',
    building: 'Корпус 1',
    group_name: 'ПИ-101',
    subgroup: null,
    notes: null,
    subject_id: 1,
    teacher_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 11,
    lesson_date: '2026-02-07',
    day_of_week: 6,
    start_time: '13:00:00',
    end_time: '14:35:00',
    week_type: null,
    subject_name: 'Программирование',
    lesson_type: 'practice',
    teacher_name: 'Сидоров С.С.',
    room: '405',
    building: 'Корпус 3',
    group_name: 'ПИ-101',
    subgroup: null,
    notes: null,
    subject_id: 3,
    teacher_id: 3,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const testTodaySchedule: DaySchedule = {
  date: '2026-02-07',
  day_of_week: 6,
  day_name: 'Суббота',
  entries: testScheduleEntries,
}

export const testCurrentLesson: CurrentLesson = {
  current: null,
  next: {
    id: 1,
    lesson_date: '2026-02-07',
    day_of_week: 6,
    start_time: '10:30:00',
    end_time: '12:05:00',
    week_type: null,
    subject_name: 'Математический анализ',
    lesson_type: 'lecture',
    teacher_name: 'Иванов И.И.',
    room: '301',
    building: 'Корпус 1',
    group_name: 'ПИ-101',
    subgroup: null,
    notes: null,
    subject_id: 1,
    teacher_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  time_until_next: 3600,
}

export const testSubjects: Subject[] = [
  {
    id: 1,
    name: 'Математический анализ',
    short_name: 'Матан',
    description: null,
    semester_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Физика',
    short_name: 'Физ',
    description: null,
    semester_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 3,
    name: 'Программирование',
    short_name: 'Прог',
    description: 'Основы программирования',
    semester_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

export const testWorksForSubject: WorkWithStatus[] = [
  // Subject 1: Матан — 2 completed, 1 in_progress (67%)
  {
    id: 101,
    title: 'Контрольная работа №1',
    description: null,
    work_type: 'test',
    deadline: '2026-02-15T23:59:00Z',
    max_grade: 10,
    subject_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 1,
      work_id: 101,
      user_id: 1,
      status: 'completed',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 102,
    title: 'Домашнее задание №1',
    description: null,
    work_type: 'homework',
    deadline: '2026-02-20T23:59:00Z',
    max_grade: 5,
    subject_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 2,
      work_id: 102,
      user_id: 1,
      status: 'graded',
      grade: 5,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 103,
    title: 'Домашнее задание №2',
    description: null,
    work_type: 'homework',
    deadline: '2026-03-01T23:59:00Z',
    max_grade: 5,
    subject_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 3,
      work_id: 103,
      user_id: 1,
      status: 'in_progress',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  // Subject 2: Физика — 1 in_progress, 1 not started (0%)
  {
    id: 104,
    title: 'Лабораторная работа №1',
    description: null,
    work_type: 'lab',
    deadline: '2026-03-01T23:59:00Z',
    max_grade: 10,
    subject_id: 2,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 4,
      work_id: 104,
      user_id: 1,
      status: 'in_progress',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 105,
    title: 'Домашнее задание №3',
    description: null,
    work_type: 'homework',
    deadline: '2026-02-20T23:59:00Z',
    max_grade: 5,
    subject_id: 2,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: null,
  },
  // Subject 3: Программирование — 2 completed, 1 submitted (100%)
  {
    id: 106,
    title: 'Лабораторная №1',
    description: null,
    work_type: 'lab',
    deadline: '2026-02-10T23:59:00Z',
    max_grade: 10,
    subject_id: 3,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 5,
      work_id: 106,
      user_id: 1,
      status: 'completed',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 107,
    title: 'Лабораторная №2',
    description: null,
    work_type: 'lab',
    deadline: '2026-02-25T23:59:00Z',
    max_grade: 10,
    subject_id: 3,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 6,
      work_id: 107,
      user_id: 1,
      status: 'submitted',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 108,
    title: 'Лабораторная №3',
    description: null,
    work_type: 'lab',
    deadline: '2026-03-10T23:59:00Z',
    max_grade: 10,
    subject_id: 3,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 7,
      work_id: 108,
      user_id: 1,
      status: 'graded',
      grade: 9,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
]

export const testFiles: StudyFile[] = [
  {
    id: 1,
    filename: 'Лекция_01.pdf',
    stored_filename: 'a1b2c3.pdf',
    mime_type: 'application/pdf',
    size: 2 * 1024 * 1024,
    category: 'lecture',
    subject_id: 1,
    subject_name: 'Математический анализ',
    uploaded_by: 1,
    created_at: '2026-01-15T10:00:00Z',
  },
  {
    id: 2,
    filename: 'Задачник.docx',
    stored_filename: 'd4e5f6.docx',
    mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    size: 512 * 1024,
    category: 'problem_set',
    subject_id: 2,
    subject_name: 'Физика',
    uploaded_by: 1,
    created_at: '2026-01-20T14:00:00Z',
  },
  {
    id: 3,
    filename: 'Шпаргалка.png',
    stored_filename: 'g7h8i9.png',
    mime_type: 'image/png',
    size: 150 * 1024,
    category: 'cheatsheet',
    subject_id: null,
    subject_name: null,
    uploaded_by: 1,
    created_at: '2026-02-01T08:00:00Z',
  },
]

export const testUpcomingWorks: UpcomingWork[] = [
  {
    id: 1,
    title: 'Лабораторная работа №1',
    work_type: 'lab',
    deadline: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    subject_id: 1,
    subject_name: 'Программирование',
    my_status: 'in_progress',
  },
  {
    id: 2,
    title: 'Реферат',
    work_type: 'report',
    deadline: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
    subject_id: 2,
    subject_name: 'История',
    my_status: null,
  },
]

export const handlers = [
  // Auth endpoints
  http.post('/api/v1/auth/login', () => {
    return HttpResponse.json(testTokens)
  }),

  http.post('/api/v1/auth/register', () => {
    return HttpResponse.json(testUser, { status: 201 })
  }),

  http.get('/api/v1/auth/me', () => {
    return HttpResponse.json(testUser)
  }),

  http.post('/api/v1/auth/logout', () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // Subject endpoints
  http.get('/api/v1/subjects', () => {
    return HttpResponse.json(testSubjects)
  }),

  // Schedule endpoints
  http.get('/api/v1/schedule/today', () => {
    return HttpResponse.json(testTodaySchedule)
  }),

  http.get('/api/v1/schedule/current', () => {
    return HttpResponse.json(testCurrentLesson)
  }),

  // Schedule entry update
  http.put('/api/v1/schedule/entries/:id', async ({ request, params }) => {
    const body = await request.json() as { notes?: string | null }
    const id = Number(params.id)
    const entry = testScheduleEntries.find((e) => e.id === id)
    if (!entry) {
      return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    }
    return HttpResponse.json({ ...entry, notes: body.notes ?? entry.notes })
  }),

  // Works endpoints
  http.get('/api/v1/works', ({ request }) => {
    const url = new URL(request.url)
    const subjectId = url.searchParams.get('subject_id')
    if (subjectId) {
      return HttpResponse.json(
        testWorksForSubject.filter((w) => w.subject_id === Number(subjectId))
      )
    }
    return HttpResponse.json(testWorksForSubject)
  }),

  http.get('/api/v1/works/upcoming', () => {
    return HttpResponse.json(testUpcomingWorks)
  }),

  // Files endpoints
  http.get('/api/v1/files/', () => {
    return HttpResponse.json(testFiles)
  }),

  http.post('/api/v1/files/upload', () => {
    const newFile: StudyFile = {
      id: 100,
      filename: 'uploaded.pdf',
      stored_filename: 'abc123.pdf',
      mime_type: 'application/pdf',
      size: 1024 * 1024,
      category: 'lecture',
      subject_id: null,
      subject_name: null,
      uploaded_by: 1,
      created_at: '2026-02-01T00:00:00Z',
    }
    return HttpResponse.json(newFile, { status: 201 })
  }),

  http.delete('/api/v1/files/:id', () => {
    return new HttpResponse(null, { status: 204 })
  }),
]
