import { render, screen, fireEvent } from '@testing-library/react'
import { LessonCard } from '../LessonCard'
import { testScheduleEntries } from '@/test/mocks/handlers'
import type { ScheduleEntry } from '@/types/schedule'

const entry: ScheduleEntry = testScheduleEntries[1] // Математический анализ

describe('LessonCard', () => {
  it('renders subject name', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
  })

  it('renders time range', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.getByText('10:30 – 12:05')).toBeInTheDocument()
  })

  it('renders lesson type label', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.getByText('Лекция')).toBeInTheDocument()
  })

  it('renders teacher name', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.getByText('Иванов И.И.')).toBeInTheDocument()
  })

  it('renders location as building-room', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.getByText('Корпус 1-301')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const onClick = vi.fn()
    render(<LessonCard entry={entry} onClick={onClick} />)

    const card = screen.getByRole('button')
    fireEvent.click(card)

    expect(onClick).toHaveBeenCalledTimes(1)
    expect(onClick).toHaveBeenCalledWith(entry)
  })

  it('has role="button" and tabIndex when onClick is provided', () => {
    render(<LessonCard entry={entry} onClick={vi.fn()} />)

    const card = screen.getByRole('button')
    expect(card).toHaveAttribute('tabindex', '0')
  })

  it('has aria-label when onClick is provided', () => {
    render(<LessonCard entry={entry} onClick={vi.fn()} />)

    const card = screen.getByRole('button')
    expect(card).toHaveAttribute(
      'aria-label',
      'Открыть занятие: Математический анализ, 10:30–12:05'
    )
  })

  it('does not have aria-label when onClick is not provided', () => {
    const { container } = render(<LessonCard entry={entry} />)

    const card = container.firstChild
    expect(card).not.toHaveAttribute('aria-label')
  })

  it('does not have role="button" when onClick is not provided', () => {
    render(<LessonCard entry={entry} />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('calls onClick on Enter key press', () => {
    const onClick = vi.fn()
    render(<LessonCard entry={entry} onClick={onClick} />)

    const card = screen.getByRole('button')
    fireEvent.keyDown(card, { key: 'Enter' })

    expect(onClick).toHaveBeenCalledTimes(1)
    expect(onClick).toHaveBeenCalledWith(entry)
  })

  it('calls onClick on Space key press', () => {
    const onClick = vi.fn()
    render(<LessonCard entry={entry} onClick={onClick} />)

    const card = screen.getByRole('button')
    fireEvent.keyDown(card, { key: ' ' })

    expect(onClick).toHaveBeenCalledTimes(1)
    expect(onClick).toHaveBeenCalledWith(entry)
  })

  it('renders notes when present', () => {
    const entryWithNotes: ScheduleEntry = {
      ...entry,
      notes: 'Важная заметка',
    }
    render(<LessonCard entry={entryWithNotes} />)

    expect(screen.getByText('Важная заметка')).toBeInTheDocument()
  })

  it('renders subgroup when present', () => {
    const entryWithSubgroup: ScheduleEntry = {
      ...entry,
      subgroup: 2,
    }
    render(<LessonCard entry={entryWithSubgroup} />)

    expect(screen.getByText('Подгруппа 2')).toBeInTheDocument()
  })

  it('shows note icon when hasNote is true', () => {
    render(<LessonCard entry={entry} hasNote />)

    expect(screen.getByLabelText('Есть заметка')).toBeInTheDocument()
  })

  it('does not show note icon when hasNote is false', () => {
    render(<LessonCard entry={entry} hasNote={false} />)

    expect(screen.queryByLabelText('Есть заметка')).not.toBeInTheDocument()
  })
})
