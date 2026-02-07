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
    const works: UpcomingWork[] = Array.from({ length: 10 }, (_, i) =>
      createWork({
        id: i + 1,
        title: `Работа ${i + 1}`,
        deadline: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000).toISOString(),
      }),
    )
    renderWidget({ data: works })

    // Should show first 8
    expect(screen.getByText('Работа 1')).toBeInTheDocument()
    expect(screen.getByText('Работа 8')).toBeInTheDocument()
    // Should not show 9th and 10th
    expect(screen.queryByText('Работа 9')).not.toBeInTheDocument()
    expect(screen.queryByText('Работа 10')).not.toBeInTheDocument()
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
