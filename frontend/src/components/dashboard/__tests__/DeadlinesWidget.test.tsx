import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DeadlinesWidget } from '../DeadlinesWidget'
import type { UpcomingWork } from '@/types/work'

function renderWidget(props: {
  data?: UpcomingWork[]
  isLoading?: boolean
  isError?: boolean
}) {
  return render(
    <MemoryRouter>
      <DeadlinesWidget
        data={props.data}
        isLoading={props.isLoading ?? false}
        isError={props.isError ?? false}
      />
    </MemoryRouter>,
  )
}

function createWork(overrides: Partial<UpcomingWork> & { id: number; deadline: string }): UpcomingWork {
  return {
    title: `Work ${overrides.id}`,
    work_type: 'homework',
    deadline_has_time: true,
    subject_id: 1,
    subject_name: 'Тестовый предмет',
    my_status: null,
    ...overrides,
  }
}

describe('DeadlinesWidget', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders widget title', () => {
    renderWidget({})

    expect(screen.getByText('Ближайшие дедлайны')).toBeInTheDocument()
  })

  it('shows loading spinner', () => {
    renderWidget({ isLoading: true })

    expect(screen.queryByText('Нет ближайших дедлайнов')).not.toBeInTheDocument()
  })

  it('shows error message', () => {
    renderWidget({ isError: true })

    expect(screen.getByText('Не удалось загрузить дедлайны')).toBeInTheDocument()
  })

  it('shows empty state when no data', () => {
    renderWidget({ data: [] })

    expect(screen.getByText('Нет ближайших дедлайнов')).toBeInTheDocument()
  })

  it('renders work items', () => {
    const works: UpcomingWork[] = [
      createWork({
        id: 1,
        title: 'Лабораторная №1',
        deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      }),
    ]
    renderWidget({ data: works })

    expect(screen.getByText('Лабораторная №1')).toBeInTheDocument()
  })

  it('shows overdue badge when items are overdue', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const works: UpcomingWork[] = [
      createWork({
        id: 1,
        title: 'Просроченная работа',
        deadline: '2026-02-05T12:00:00',
      }),
      createWork({
        id: 2,
        title: 'Будущая работа',
        deadline: '2026-02-10T12:00:00',
      }),
    ]
    renderWidget({ data: works })

    expect(screen.getByText('1 просроч.')).toBeInTheDocument()
  })

  it('groups items by urgency with section headers', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const works: UpcomingWork[] = [
      createWork({
        id: 1,
        title: 'Задание А',
        deadline: '2026-02-05T12:00:00',
      }),
      createWork({
        id: 2,
        title: 'Задание Б',
        deadline: '2026-02-08T12:00:00',
      }),
      createWork({
        id: 3,
        title: 'Задание В',
        deadline: '2026-02-12T12:00:00',
      }),
    ]
    renderWidget({ data: works })

    // "Просрочено" appears as both group header and formatDeadline output
    const overdueElements = screen.getAllByText('Просрочено')
    expect(overdueElements.length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Сегодня / Завтра')).toBeInTheDocument()
    expect(screen.getByText('На неделе')).toBeInTheDocument()
  })

  it('renders "Все работы" link when data present', () => {
    const works: UpcomingWork[] = [
      createWork({
        id: 1,
        title: 'Работа',
        deadline: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      }),
    ]
    renderWidget({ data: works })

    const link = screen.getByText('Все работы')
    expect(link).toBeInTheDocument()
    expect(link.closest('a')).toHaveAttribute('href', '/works')
  })

  it('shows max 8 items', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    // 3 overdue + 7 within 7 days = 10 visible; capped at 8
    const works: UpcomingWork[] = [
      createWork({ id: 1, title: 'Работа 1', deadline: '2026-02-01T12:00:00' }),
      createWork({ id: 2, title: 'Работа 2', deadline: '2026-02-02T12:00:00' }),
      createWork({ id: 3, title: 'Работа 3', deadline: '2026-02-03T12:00:00' }),
      createWork({ id: 4, title: 'Работа 4', deadline: '2026-02-08T12:00:00' }),
      createWork({ id: 5, title: 'Работа 5', deadline: '2026-02-09T12:00:00' }),
      createWork({ id: 6, title: 'Работа 6', deadline: '2026-02-10T12:00:00' }),
      createWork({ id: 7, title: 'Работа 7', deadline: '2026-02-11T12:00:00' }),
      createWork({ id: 8, title: 'Работа 8', deadline: '2026-02-12T12:00:00' }),
      createWork({ id: 9, title: 'Работа 9', deadline: '2026-02-13T12:00:00' }),
      createWork({ id: 10, title: 'Работа 10', deadline: '2026-02-14T12:00:00' }),
    ]
    renderWidget({ data: works })

    // Sorted: overdue (1-3), soon (4), week (5-10); first 8 visible
    expect(screen.getByText('Работа 1')).toBeInTheDocument()
    expect(screen.getByText('Работа 8')).toBeInTheDocument()
    // 9th and 10th cut off by MAX_VISIBLE
    expect(screen.queryByText('Работа 9')).not.toBeInTheDocument()
    expect(screen.queryByText('Работа 10')).not.toBeInTheDocument()
  })

  it('does not show works with deadline beyond 7 days', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const works: UpcomingWork[] = [
      createWork({ id: 1, title: 'Работа 7 дней', deadline: '2026-02-14T12:00:00' }), // exactly 7 → shown
      createWork({ id: 2, title: 'Работа 8 дней', deadline: '2026-02-15T12:00:00' }), // 8 days → hidden
    ]
    renderWidget({ data: works })

    expect(screen.getByText('Работа 7 дней')).toBeInTheDocument()
    expect(screen.queryByText('Работа 8 дней')).not.toBeInTheDocument()
  })

  it('shows completed check icon for completed works', () => {
    const works: UpcomingWork[] = [
      createWork({
        id: 1,
        title: 'Сданная работа',
        deadline: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        my_status: 'completed',
      }),
    ]
    renderWidget({ data: works })

    expect(screen.getByText('Выполнено')).toBeInTheDocument()
  })
})
