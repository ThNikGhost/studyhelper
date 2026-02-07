import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { TodayScheduleWidget } from '../TodayScheduleWidget'
import {
  testTodaySchedule,
  testCurrentLesson,
  testScheduleEntries,
} from '@/test/mocks/handlers'
import type { DaySchedule, CurrentLesson } from '@/types/schedule'

function renderWidget(props: {
  todaySchedule?: DaySchedule
  currentLesson?: CurrentLesson
  isLoading?: boolean
  isError?: boolean
}) {
  return render(
    <MemoryRouter>
      <TodayScheduleWidget
        todaySchedule={props.todaySchedule}
        currentLesson={props.currentLesson}
        isLoading={props.isLoading ?? false}
        isError={props.isError ?? false}
      />
    </MemoryRouter>,
  )
}

describe('TodayScheduleWidget', () => {
  it('renders widget title', () => {
    renderWidget({})

    expect(screen.getByText('Расписание на сегодня')).toBeInTheDocument()
  })

  it('shows loading spinner', () => {
    renderWidget({ isLoading: true })

    expect(screen.queryByText('Сегодня занятий нет')).not.toBeInTheDocument()
  })

  it('shows error message', () => {
    renderWidget({ isError: true })

    expect(screen.getByText('Не удалось загрузить расписание')).toBeInTheDocument()
  })

  it('shows empty state when no entries', () => {
    const emptySchedule: DaySchedule = {
      date: '2026-02-07',
      day_of_week: 6,
      day_name: 'Суббота',
      entries: [],
    }
    renderWidget({ todaySchedule: emptySchedule })

    expect(screen.getByText('Сегодня занятий нет')).toBeInTheDocument()
  })

  it('renders all schedule entries', () => {
    renderWidget({
      todaySchedule: testTodaySchedule,
      currentLesson: testCurrentLesson,
    })

    expect(screen.getByText('Физика')).toBeInTheDocument()
    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Программирование')).toBeInTheDocument()
  })

  it('shows lesson count', () => {
    renderWidget({
      todaySchedule: testTodaySchedule,
      currentLesson: testCurrentLesson,
    })

    expect(screen.getByText('3 пары')).toBeInTheDocument()
  })

  it('highlights current lesson with "Сейчас" badge', () => {
    const currentLessonWithCurrent: CurrentLesson = {
      current: testScheduleEntries[1], // Матанализ
      next: testScheduleEntries[2],
      time_until_next: 3600,
    }
    renderWidget({
      todaySchedule: testTodaySchedule,
      currentLesson: currentLessonWithCurrent,
    })

    expect(screen.getByText('Сейчас')).toBeInTheDocument()
  })

  it('renders "Полное расписание" link', () => {
    renderWidget({ todaySchedule: testTodaySchedule })

    const link = screen.getByText('Полное расписание')
    expect(link).toBeInTheDocument()
    expect(link.closest('a')).toHaveAttribute('href', '/schedule')
  })

  it('shows time range for each entry', () => {
    renderWidget({
      todaySchedule: testTodaySchedule,
      currentLesson: testCurrentLesson,
    })

    expect(screen.getByText(/08:30/)).toBeInTheDocument()
    expect(screen.getByText(/10:30/)).toBeInTheDocument()
    expect(screen.getByText(/13:00/)).toBeInTheDocument()
  })

  it('shows teacher names', () => {
    renderWidget({
      todaySchedule: testTodaySchedule,
      currentLesson: testCurrentLesson,
    })

    expect(screen.getByText('Петров П.П.')).toBeInTheDocument()
    expect(screen.getByText('Иванов И.И.')).toBeInTheDocument()
    expect(screen.getByText('Сидоров С.С.')).toBeInTheDocument()
  })
})
