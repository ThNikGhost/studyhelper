import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { Toaster } from 'sonner'
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
        <Toaster />
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

  it('shows notes textarea with existing notes', () => {
    renderModal({ entry: fullEntry, open: true })

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    expect(textarea).toHaveValue('Принести тетрадь')
  })

  it('shows empty textarea when no notes', () => {
    renderModal({ entry: entryNoSubject, open: true })

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    expect(textarea).toHaveValue('')
  })

  it('enables save button after editing notes', async () => {
    const user = userEvent.setup()
    renderModal({ entry: fullEntry, open: true })

    const saveButton = screen.getByRole('button', { name: /Сохранить/ })
    expect(saveButton).toBeDisabled()

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    await user.clear(textarea)
    await user.type(textarea, 'Новая заметка')

    expect(saveButton).toBeEnabled()
  })

  it('saves notes and shows success toast', async () => {
    const user = userEvent.setup()
    renderModal({ entry: fullEntry, open: true })

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    await user.clear(textarea)
    await user.type(textarea, 'Обновлённая заметка')

    const saveButton = screen.getByRole('button', { name: /Сохранить/ })
    await user.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Заметка сохранена')).toBeInTheDocument()
    })
  })

  it('shows error toast on save failure', async () => {
    server.use(
      http.put('/api/v1/schedule/entries/:id', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    const user = userEvent.setup()
    renderModal({ entry: fullEntry, open: true })

    const textarea = screen.getByPlaceholderText('Добавить заметку к занятию...')
    await user.clear(textarea)
    await user.type(textarea, 'Новая заметка')

    const saveButton = screen.getByRole('button', { name: /Сохранить/ })
    await user.click(saveButton)

    await waitFor(() => {
      expect(screen.getByText('Не удалось сохранить заметку')).toBeInTheDocument()
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
