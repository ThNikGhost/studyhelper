import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import { NoteEditor } from '../NoteEditor'
import type { LessonNote } from '@/types/note'

const existingNote: LessonNote = {
  id: 1,
  user_id: 1,
  schedule_entry_id: 10,
  subject_name: 'Физика',
  lesson_date: '2026-02-07',
  content: 'Existing note content',
  created_at: '2026-02-07T12:00:00Z',
  updated_at: '2026-02-07T12:00:00Z',
}

describe('NoteEditor', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders empty textarea when no note', () => {
    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    expect(textarea).toBeInTheDocument()
    expect(textarea).toHaveValue('')
  })

  it('renders existing note content', () => {
    render(
      <NoteEditor
        note={existingNote}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    expect(textarea).toHaveValue('Existing note content')
  })

  it('shows character counter', () => {
    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    expect(screen.getByTestId('char-counter')).toHaveTextContent('0/2000')
  })

  it('updates character counter on input', () => {
    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    expect(screen.getByTestId('char-counter')).toHaveTextContent('5/2000')
  })

  it('does not accept content over 2000 characters', () => {
    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'a'.repeat(2001) } })

    expect(textarea).toHaveValue('')
  })

  it('creates note after debounce when no existing note', async () => {
    let createCalled = false
    server.use(
      http.post('/api/v1/notes/', async () => {
        createCalled = true
        return HttpResponse.json(
          { ...existingNote, id: 100, content: 'New note' },
          { status: 201 },
        )
      }),
    )

    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'New note' } })

    // Advance past debounce
    await act(async () => {
      vi.advanceTimersByTime(600)
    })

    await waitFor(() => {
      expect(createCalled).toBe(true)
    })
  })

  it('updates note after debounce when existing note', async () => {
    let updateCalled = false
    server.use(
      http.put('/api/v1/notes/:noteId', async () => {
        updateCalled = true
        return HttpResponse.json({ ...existingNote, content: 'Updated' })
      }),
    )

    render(
      <NoteEditor
        note={existingNote}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'Updated' } })

    await act(async () => {
      vi.advanceTimersByTime(600)
    })

    await waitFor(() => {
      expect(updateCalled).toBe(true)
    })
  })

  it('shows saving status indicator', async () => {
    server.use(
      http.post('/api/v1/notes/', async () => {
        // Delay response
        await new Promise((r) => setTimeout(r, 1000))
        return HttpResponse.json(
          { ...existingNote, id: 100 },
          { status: 201 },
        )
      }),
    )

    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'Test' } })

    await act(async () => {
      vi.advanceTimersByTime(600)
    })

    await waitFor(() => {
      expect(screen.getByTestId('save-status')).toHaveTextContent('Сохранение...')
    })
  })

  it('shows error status on save failure', async () => {
    server.use(
      http.post('/api/v1/notes/', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    fireEvent.change(textarea, { target: { value: 'Test' } })

    await act(async () => {
      vi.advanceTimersByTime(600)
    })

    await waitFor(() => {
      expect(screen.getByTestId('save-status')).toHaveTextContent('Ошибка сохранения')
    })
  })

  it('disables textarea when disabled prop is true', () => {
    render(
      <NoteEditor
        note={null}
        scheduleEntryId={10}
        subjectName="Физика"
        disabled
      />,
    )

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    expect(textarea).toBeDisabled()
  })
})
