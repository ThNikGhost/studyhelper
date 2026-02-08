import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { SemesterProgressWidget } from '../SemesterProgressWidget'
import type { SemesterProgress } from '@/lib/progressUtils'

function renderWidget(props: {
  progress?: SemesterProgress
  isLoading?: boolean
  isError?: boolean
}) {
  return render(
    <MemoryRouter>
      <SemesterProgressWidget
        progress={props.progress}
        isLoading={props.isLoading ?? false}
        isError={props.isError ?? false}
      />
    </MemoryRouter>,
  )
}

const testProgress: SemesterProgress = {
  total: 8,
  completed: 5,
  inProgress: 2,
  notStarted: 1,
  percentage: 63,
  subjects: [
    {
      subjectId: 1,
      subjectName: 'Математический анализ',
      total: 3,
      completed: 2,
      inProgress: 1,
      notStarted: 0,
      percentage: 67,
    },
    {
      subjectId: 2,
      subjectName: 'Физика',
      total: 2,
      completed: 0,
      inProgress: 1,
      notStarted: 1,
      percentage: 0,
    },
    {
      subjectId: 3,
      subjectName: 'Программирование',
      total: 3,
      completed: 3,
      inProgress: 0,
      notStarted: 0,
      percentage: 100,
    },
  ],
}

describe('SemesterProgressWidget', () => {
  it('renders widget title', () => {
    renderWidget({ progress: testProgress })

    expect(screen.getByText('Прогресс семестра')).toBeInTheDocument()
  })

  it('shows overall progress bar and text', () => {
    renderWidget({ progress: testProgress })

    expect(screen.getByText('5 из 8 (63%)')).toBeInTheDocument()
    // Multiple progressbars: overall + subject mini bars
    const bars = screen.getAllByRole('progressbar')
    expect(bars.length).toBeGreaterThanOrEqual(1)
    expect(bars[0]).toHaveAttribute('aria-valuenow', '63')
  })

  it('shows loading spinner', () => {
    renderWidget({ isLoading: true })

    expect(screen.queryByText(/из/)).not.toBeInTheDocument()
  })

  it('shows error message', () => {
    renderWidget({ isError: true })

    expect(screen.getByText('Не удалось загрузить прогресс')).toBeInTheDocument()
  })

  it('shows top-3 subjects with lowest progress', () => {
    renderWidget({ progress: testProgress })

    // Sorted by lowest: Физика (0%), Матан (67%), Программирование (100%)
    // Only shows subjects with total > 0
    expect(screen.getByText('Физика')).toBeInTheDocument()
    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Программирование')).toBeInTheDocument()
  })

  it('shows "Требуют внимания" section header', () => {
    renderWidget({ progress: testProgress })

    expect(screen.getByText('Требуют внимания')).toBeInTheDocument()
  })

  it('shows "Все предметы" link', () => {
    renderWidget({ progress: testProgress })

    expect(screen.getByText('Все предметы')).toBeInTheDocument()
  })

  it('shows empty state when no works', () => {
    const emptyProgress: SemesterProgress = {
      total: 0,
      completed: 0,
      inProgress: 0,
      notStarted: 0,
      percentage: 0,
      subjects: [],
    }
    renderWidget({ progress: emptyProgress })

    expect(screen.getByText('Нет работ в этом семестре')).toBeInTheDocument()
  })
})
