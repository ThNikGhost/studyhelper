import { http, HttpResponse } from 'msw'
import type { User, TokenResponse } from '@/types/auth'
import type { CurrentLesson, DaySchedule, ScheduleEntry } from '@/types/schedule'
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

export const testWorksForSubject: WorkWithStatus[] = [
  {
    id: 101,
    title: 'Лабораторная работа №1',
    description: null,
    work_type: 'lab',
    deadline: '2026-03-01T23:59:00Z',
    max_grade: 10,
    subject_id: 2,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: {
      id: 1,
      work_id: 101,
      user_id: 1,
      status: 'in_progress',
      grade: null,
      notes: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  },
  {
    id: 102,
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
]
