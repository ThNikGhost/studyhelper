import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { NoteCard } from '../NoteCard'
import type { LessonNote } from '@/types/note'

const shortNote: LessonNote = {
  id: 1,
  user_id: 1,
  schedule_entry_id: 10,
  subject_name: 'Физика',
  lesson_date: '2026-02-07',
  content: 'Short note content',
  created_at: '2026-02-07T12:00:00Z',
  updated_at: '2026-02-07T12:00:00Z',
}

const longNote: LessonNote = {
  id: 2,
  user_id: 1,
  schedule_entry_id: null,
  subject_name: 'Математический анализ',
  lesson_date: '2026-02-06',
  content: 'A'.repeat(200),
  created_at: '2026-02-06T10:00:00Z',
  updated_at: '2026-02-06T10:00:00Z',
}

describe('NoteCard', () => {
  it('renders subject name and content', () => {
    render(<NoteCard note={shortNote} onDelete={vi.fn()} />)

    expect(screen.getByText('Физика')).toBeInTheDocument()
    expect(screen.getByText('Short note content')).toBeInTheDocument()
  })

  it('renders formatted date', () => {
    render(<NoteCard note={shortNote} onDelete={vi.fn()} />)

    // Should contain the date in Russian locale
    expect(screen.getByText(/7 февраля/)).toBeInTheDocument()
  })

  it('truncates long content with expand button', () => {
    render(<NoteCard note={longNote} onDelete={vi.fn()} />)

    // Content should be truncated with "..."
    const contentEl = screen.getByText(/A{10,}\.\.\./)
    expect(contentEl).toBeInTheDocument()

    // Expand button should be visible
    expect(screen.getByText('Развернуть')).toBeInTheDocument()
  })

  it('expands and collapses on button click', () => {
    render(<NoteCard note={longNote} onDelete={vi.fn()} />)

    // Click expand
    fireEvent.click(screen.getByText('Развернуть'))
    expect(screen.getByText('Свернуть')).toBeInTheDocument()

    // Click collapse
    fireEvent.click(screen.getByText('Свернуть'))
    expect(screen.getByText('Развернуть')).toBeInTheDocument()
  })

  it('calls onDelete with note id', () => {
    const onDelete = vi.fn()
    render(<NoteCard note={shortNote} onDelete={onDelete} />)

    fireEvent.click(screen.getByLabelText('Удалить заметку'))
    expect(onDelete).toHaveBeenCalledWith(1)
  })
})
