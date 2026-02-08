import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { SubjectProgressCard } from '../SubjectProgressCard'
import type { Subject } from '@/types/subject'
import type { SubjectProgress } from '@/lib/progressUtils'

const testSubject: Subject = {
  id: 1,
  name: 'Математический анализ',
  short_name: 'Матан',
  description: null,
  semester_id: 1,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

const testProgress: SubjectProgress = {
  subjectId: 1,
  subjectName: 'Математический анализ',
  total: 5,
  completed: 3,
  inProgress: 1,
  notStarted: 1,
  percentage: 60,
}

describe('SubjectProgressCard', () => {
  it('renders subject name and short name', () => {
    render(<SubjectProgressCard subject={testSubject} progress={testProgress} />)

    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Матан')).toBeInTheDocument()
  })

  it('renders progress bar and completion text', () => {
    render(<SubjectProgressCard subject={testSubject} progress={testProgress} />)

    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '60')
    expect(screen.getByText('3 из 5 выполнено')).toBeInTheDocument()
  })

  it('shows status breakdown badges for non-zero counts', () => {
    render(<SubjectProgressCard subject={testSubject} progress={testProgress} />)

    expect(screen.getByText(/Выполнено: 3/)).toBeInTheDocument()
    expect(screen.getByText(/В процессе: 1/)).toBeInTheDocument()
    expect(screen.getByText(/Не начато: 1/)).toBeInTheDocument()
  })

  it('shows "Нет работ" when no progress data', () => {
    render(<SubjectProgressCard subject={testSubject} progress={undefined} />)

    expect(screen.getByText('Нет работ')).toBeInTheDocument()
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
  })

  it('shows "Нет работ" when total is 0', () => {
    const emptyProgress: SubjectProgress = {
      ...testProgress,
      total: 0,
      completed: 0,
      inProgress: 0,
      notStarted: 0,
      percentage: 0,
    }
    render(<SubjectProgressCard subject={testSubject} progress={emptyProgress} />)

    expect(screen.getByText('Нет работ')).toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn()
    render(
      <SubjectProgressCard
        subject={testSubject}
        progress={testProgress}
        onClick={handleClick}
      />,
    )

    fireEvent.click(screen.getByText('Математический анализ'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('handles keyboard activation with Enter', () => {
    const handleClick = vi.fn()
    render(
      <SubjectProgressCard
        subject={testSubject}
        progress={testProgress}
        onClick={handleClick}
      />,
    )

    const card = screen.getByRole('button')
    fireEvent.keyDown(card, { key: 'Enter' })
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
