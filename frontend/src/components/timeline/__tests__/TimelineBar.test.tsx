import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TimelineBar } from '../TimelineBar'
import type { TimelineDeadline, TimelineExam } from '@/types/timeline'

const deadlines: TimelineDeadline[] = [
  {
    work_id: 1,
    title: 'Контрольная',
    work_type: 'test',
    deadline: '2025-10-15T23:59:00Z',
    subject_name: 'Математика',
    subject_id: 1,
    status: 'completed',
  },
  {
    work_id: 2,
    title: 'Лабораторная',
    work_type: 'lab',
    deadline: '2025-11-20T23:59:00Z',
    subject_name: 'Физика',
    subject_id: 2,
    status: 'in_progress',
  },
]

const exams: TimelineExam[] = [
  {
    schedule_entry_id: 100,
    subject_name: 'Математика',
    lesson_date: '2026-01-15',
    start_time: '09:00:00',
    end_time: '12:00:00',
    room: '301',
    teacher_name: 'Иванов И.И.',
  },
]

describe('TimelineBar', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders the timeline container', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={[]}
        exams={[]}
      />,
    )
    expect(screen.getByRole('img', { name: /timeline/i })).toBeInTheDocument()
  })

  it('renders deadline markers', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={deadlines}
        exams={[]}
      />,
    )
    expect(screen.getByLabelText('Контрольная')).toBeInTheDocument()
    expect(screen.getByLabelText('Лабораторная')).toBeInTheDocument()
  })

  it('renders exam markers', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={[]}
        exams={exams}
      />,
    )
    expect(screen.getByLabelText(/экзамен.*математика/i)).toBeInTheDocument()
  })

  it('hides deadline markers when showDeadlines is false', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={deadlines}
        exams={[]}
        showDeadlines={false}
      />,
    )
    expect(screen.queryByLabelText('Контрольная')).not.toBeInTheDocument()
  })

  it('hides exam markers when showExams is false', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={[]}
        exams={exams}
        showExams={false}
      />,
    )
    expect(screen.queryByLabelText(/экзамен/i)).not.toBeInTheDocument()
  })

  it('filters deadlines by subject', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={deadlines}
        exams={[]}
        subjectFilter={1}
      />,
    )
    expect(screen.getByLabelText('Контрольная')).toBeInTheDocument()
    expect(screen.queryByLabelText('Лабораторная')).not.toBeInTheDocument()
  })

  it('renders month labels', () => {
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={[]}
        exams={[]}
      />,
    )
    expect(screen.getByText('Окт')).toBeInTheDocument()
    expect(screen.getByText('Ноя')).toBeInTheDocument()
  })

  it('shows today marker during semester', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-11-15'))
    render(
      <TimelineBar
        startDate="2025-09-01"
        endDate="2026-01-31"
        deadlines={[]}
        exams={[]}
      />,
    )
    expect(screen.getByText('Сегодня')).toBeInTheDocument()
  })
})
