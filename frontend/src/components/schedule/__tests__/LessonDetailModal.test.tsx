import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { http, HttpResponse } from 'msw'
import { LessonDetailModal } from '../LessonDetailModal'
import { testScheduleEntries } from '@/test/mocks/handlers'
import { server } from '@/test/mocks/server'
import type { ScheduleEntry } from '@/types/schedule'

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  })
}

function renderModal(props: {
  entry: ScheduleEntry | null
  open: boolean
  onClose?: () => void
}) {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <LessonDetailModal
          entry={props.entry}
          open={props.open}
          onClose={props.onClose ?? vi.fn()}
        />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

// Entry with subject_id, teacher, room, building, subgroup
const fullEntry: ScheduleEntry = {
  ...testScheduleEntries[0],
  subgroup: 1,
  notes: 'Принести тетрадь',
}

// Entry without subject_id
const entryNoSubject: ScheduleEntry = {
  ...testScheduleEntries[0],
  subject_id: null,
  teacher_name: null,
  subgroup: null,
  notes: null,
}

describe('LessonDetailModal', () => {
  it('renders nothing when open is false', () => {
    renderModal({ entry: fullEntry, open: false })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders nothing when entry is null', () => {
    renderModal({ entry: null, open: true })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders subject name as title', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText(fullEntry.subject_name)).toBeInTheDocument()
  })

  it('displays time range', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText(/08:30 – 10:05/)).toBeInTheDocument()
  })

  it('displays lesson type', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('Лекция')).toBeInTheDocument()
  })

  it('displays location as building-room', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('Корпус 2-201')).toBeInTheDocument()
  })

  it('displays teacher name', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('Петров П.П.')).toBeInTheDocument()
  })

  it('displays subgroup when present', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('Подгруппа 1')).toBeInTheDocument()
  })

  it('displays group name', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('ПИ-101')).toBeInTheDocument()
  })

  it('shows subject link when subject_id is present', () => {
    renderModal({ entry: fullEntry, open: true })

    expect(screen.getByText('Перейти к предмету')).toBeInTheDocument()
  })

  it('hides subject link when subject_id is null', () => {
    renderModal({ entry: entryNoSubject, open: true })

    expect(screen.queryByText('Перейти к предмету')).not.toBeInTheDocument()
  })

  it('loads and displays works for subject', async () => {
    renderModal({ entry: fullEntry, open: true })

    await waitFor(() => {
      expect(screen.getByText('Лабораторная работа №1')).toBeInTheDocument()
    })
    expect(screen.getByText('Домашнее задание №3')).toBeInTheDocument()
  })

  it('shows empty state when no works exist', async () => {
    server.use(
      http.get('/api/v1/works', () => {
        return HttpResponse.json([])
      }),
    )

    renderModal({ entry: fullEntry, open: true })

    await waitFor(() => {
      expect(screen.getByText('Нет работ по этому предмету')).toBeInTheDocument()
    })
  })

  it('shows NoteEditor with existing note loaded from API', async () => {
    renderModal({ entry: fullEntry, open: true })

    // NoteEditor loads note via useQuery, wait for it
    await waitFor(() => {
      const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
      expect(textarea).toHaveValue('Запомнить формулу F=ma и второй закон Ньютона')
    })
  })

  it('shows empty NoteEditor when no note exists for entry', async () => {
    server.use(
      http.get('/api/v1/notes/entry/:entryId', () => {
        return HttpResponse.json({ detail: 'Not found' }, { status: 404 })
      }),
    )

    renderModal({ entry: entryNoSubject, open: true })

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
      expect(textarea).toHaveValue('')
    })
  })

  it('shows character counter in NoteEditor', async () => {
    renderModal({ entry: fullEntry, open: true })

    await waitFor(() => {
      expect(screen.getByTestId('char-counter')).toBeInTheDocument()
    })
  })

  it('calls onClose when backdrop is clicked', async () => {
    const onClose = vi.fn()
    renderModal({ entry: fullEntry, open: true, onClose })

    // Click the backdrop (first element with bg-black/50)
    const backdrop = document.querySelector('.bg-black\\/50')
    if (backdrop) {
      await userEvent.click(backdrop)
    }

    expect(onClose).toHaveBeenCalledTimes(1)
  })
})
