import { http, HttpResponse } from 'msw'
import type { User, TokenResponse } from '@/types/auth'
import type { AttendanceEntry, AttendanceStats } from '@/types/attendance'
import type { StudyFile } from '@/types/file'
import type { LessonNote } from '@/types/note'
import type { CurrentLesson, DaySchedule, ScheduleEntry } from '@/types/schedule'
import type { Semester, Subject } from '@/types/subject'
import type { TimelineData, TimelineDeadline, TimelineExam } from '@/types/timeline'
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
  time_until_next: 60,
}

export const testSubjects: Subject[] = [
  {
    id: 1,
    name: 'Математический анализ',
    short_name: 'Матан',
    description: null,
    semester_id: 1,
    planned_classes: 32,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Физика',
    short_name: 'Физ',
    description: null,
    semester_id: 1,
    planned_classes: 28,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 3,
    name: 'Программирование',
    short_name: 'Прог',
    description: 'Основы программирования',
    semester_id: 1,
    planned_classes: 36,
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

export const testAttendanceEntries: AttendanceEntry[] = [
  {
    id: 10,
    lesson_date: '2026-02-05',
    subject_name: 'Физика',
    lesson_type: 'lecture',
    start_time: '08:30:00',
    end_time: '10:05:00',
    teacher_name: 'Петров П.П.',
    room: '201',
    subject_id: 2,
    is_absent: true,
    absence_id: 1,
  },
  {
    id: 1,
    lesson_date: '2026-02-05',
    subject_name: 'Математический анализ',
    lesson_type: 'lecture',
    start_time: '10:30:00',
    end_time: '12:05:00',
    teacher_name: 'Иванов И.И.',
    room: '301',
    subject_id: 1,
    is_absent: false,
    absence_id: null,
  },
  {
    id: 11,
    lesson_date: '2026-02-06',
    subject_name: 'Программирование',
    lesson_type: 'practice',
    start_time: '13:00:00',
    end_time: '14:35:00',
    teacher_name: 'Сидоров С.С.',
    room: '405',
    subject_id: 3,
    is_absent: false,
    absence_id: null,
  },
]

export const testAttendanceStats: AttendanceStats = {
  total_planned: 96,
  total_completed: 10,
  total_classes: 10,
  absences: 2,
  attended: 8,
  attendance_percent: 8.3,
  by_subject: [
    {
      subject_name: 'Математический анализ',
      subject_id: 1,
      planned_classes: 32,
      total_classes: 4,
      absences: 0,
      attended: 4,
      attendance_percent: 12.5,
    },
    {
      subject_name: 'Физика',
      subject_id: 2,
      planned_classes: 28,
      total_classes: 3,
      absences: 1,
      attended: 2,
      attendance_percent: 7.1,
    },
    {
      subject_name: 'Программирование',
      subject_id: 3,
      planned_classes: 36,
      total_classes: 3,
      absences: 1,
      attended: 2,
      attendance_percent: 5.6,
    },
  ],
}

export const testLessonNotes: LessonNote[] = [
  {
    id: 1,
    user_id: 1,
    schedule_entry_id: 10,
    subject_name: 'Физика',
    lesson_date: '2026-02-07',
    content: 'Запомнить формулу F=ma и второй закон Ньютона',
    created_at: '2026-02-07T12:00:00Z',
    updated_at: '2026-02-07T12:00:00Z',
  },
  {
    id: 2,
    user_id: 1,
    schedule_entry_id: 1,
    subject_name: 'Математический анализ',
    lesson_date: '2026-02-07',
    content: 'Разобрать теорему о пределе последовательности. Домашнее задание: стр. 45-50, задачи 1-10.',
    created_at: '2026-02-07T14:00:00Z',
    updated_at: '2026-02-07T14:00:00Z',
  },
  {
    id: 3,
    user_id: 1,
    schedule_entry_id: null,
    subject_name: 'Программирование',
    lesson_date: '2026-02-06',
    content: 'Подготовить отчёт по лабораторной работе. Срок до пятницы. Необходимо описать алгоритм сортировки и привести примеры. Также нужно добавить блок-схему и таблицу результатов тестирования.',
    created_at: '2026-02-06T10:00:00Z',
    updated_at: '2026-02-06T10:00:00Z',
  },
]

export const testSemester: Semester = {
  id: 1,
  number: 1,
  year_start: 2025,
  year_end: 2026,
  name: 'Осенний 2025/2026',
  is_current: true,
  start_date: '2025-09-01',
  end_date: '2026-01-31',
  created_at: '2025-09-01T00:00:00Z',
  updated_at: '2025-09-01T00:00:00Z',
}

export const testSemesterNoDates: Semester = {
  ...testSemester,
  id: 2,
  start_date: null,
  end_date: null,
}

export const testTimelineDeadlines: TimelineDeadline[] = [
  {
    work_id: 101,
    title: 'Контрольная работа №1',
    work_type: 'test',
    deadline: '2025-10-15T23:59:00Z',
    subject_name: 'Математический анализ',
    subject_id: 1,
    status: 'completed',
  },
  {
    work_id: 102,
    title: 'Лабораторная №1',
    work_type: 'lab',
    deadline: '2025-11-01T23:59:00Z',
    subject_name: 'Программирование',
    subject_id: 3,
    status: 'in_progress',
  },
  {
    work_id: 103,
    title: 'Реферат',
    work_type: 'report',
    deadline: '2025-12-20T23:59:00Z',
    subject_name: 'Физика',
    subject_id: 2,
    status: null,
  },
]

export const testTimelineExams: TimelineExam[] = [
  {
    schedule_entry_id: 200,
    subject_name: 'Математический анализ',
    lesson_date: '2026-01-15',
    start_time: '09:00:00',
    end_time: '12:00:00',
    room: '301',
    teacher_name: 'Иванов И.И.',
  },
  {
    schedule_entry_id: 201,
    subject_name: 'Физика',
    lesson_date: '2026-01-20',
    start_time: '10:00:00',
    end_time: '13:00:00',
    room: '201',
    teacher_name: 'Петров П.П.',
  },
]

export const testTimelineData: TimelineData = {
  semester: testSemester,
  deadlines: testTimelineDeadlines,
  exams: testTimelineExams,
}

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

  // Semester endpoints
  http.get('/api/v1/semesters/current', () => {
    return HttpResponse.json(testSemester)
  }),

  http.get('/api/v1/semesters/:id/timeline', ({ params }) => {
    const id = Number(params.id)
    if (id === testSemester.id) {
      return HttpResponse.json(testTimelineData)
    }
    return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
  }),

  http.get('/api/v1/semesters', () => {
    return HttpResponse.json([testSemester])
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

  // Attendance endpoints
  http.get('/api/v1/attendance/', () => {
    return HttpResponse.json(testAttendanceEntries)
  }),

  http.get('/api/v1/attendance/stats', () => {
    return HttpResponse.json(testAttendanceStats)
  }),

  http.get('/api/v1/attendance/stats/:subjectId', () => {
    return HttpResponse.json(testAttendanceStats.by_subject[0])
  }),

  http.post('/api/v1/attendance/mark-absent', () => {
    return HttpResponse.json(
      { id: 99, user_id: 1, schedule_entry_id: 1, created_at: '2026-02-08T00:00:00Z' },
      { status: 201 },
    )
  }),

  http.post('/api/v1/attendance/mark-present', () => {
    return new HttpResponse(null, { status: 204 })
  }),

  // Notes endpoints
  http.get('/api/v1/notes/', () => {
    return HttpResponse.json(testLessonNotes)
  }),

  http.get('/api/v1/notes/subject/:subjectName', ({ params }) => {
    const subjectName = decodeURIComponent(params.subjectName as string)
    const note = testLessonNotes.find((n) => n.subject_name === subjectName)
    if (!note) {
      return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    }
    return HttpResponse.json(note)
  }),

  http.get('/api/v1/notes/entry/:entryId', ({ params }) => {
    const entryId = Number(params.entryId)
    const note = testLessonNotes.find((n) => n.schedule_entry_id === entryId)
    if (!note) {
      return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    }
    return HttpResponse.json(note)
  }),

  http.post('/api/v1/notes/', async ({ request }) => {
    const body = (await request.json()) as {
      schedule_entry_id?: number
      subject_name: string
      lesson_date?: string
      content: string
    }
    const newNote: LessonNote = {
      id: 100,
      user_id: 1,
      schedule_entry_id: body.schedule_entry_id ?? null,
      subject_name: body.subject_name,
      lesson_date: body.lesson_date ?? null,
      content: body.content,
      created_at: '2026-02-08T00:00:00Z',
      updated_at: '2026-02-08T00:00:00Z',
    }
    return HttpResponse.json(newNote, { status: 201 })
  }),

  http.put('/api/v1/notes/:noteId', async ({ request, params }) => {
    const noteId = Number(params.noteId)
    const body = (await request.json()) as { content: string }
    const existing = testLessonNotes.find((n) => n.id === noteId)
    if (!existing) {
      return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    }
    return HttpResponse.json({
      ...existing,
      content: body.content,
      updated_at: '2026-02-08T12:00:00Z',
    })
  }),

  http.delete('/api/v1/notes/:noteId', () => {
    return new HttpResponse(null, { status: 204 })
  }),
]
