import { http, HttpResponse } from 'msw'
import type { User, TokenResponse } from '@/types/auth'
import type { CurrentLesson } from '@/types/schedule'
import type { UpcomingWork } from '@/types/work'

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
  http.get('/api/v1/schedule/current', () => {
    return HttpResponse.json(testCurrentLesson)
  }),

  // Works endpoints
  http.get('/api/v1/works/upcoming', () => {
    return HttpResponse.json(testUpcomingWorks)
  }),
]
