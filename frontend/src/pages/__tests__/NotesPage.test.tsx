import { describe, it, expect } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import NotesPage from '../NotesPage'

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
    },
  })
}

function renderNotesPage() {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NotesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('NotesPage', () => {
  it('renders page title', async () => {
    renderNotesPage()

    await waitFor(() => {
      expect(screen.getByText('Заметки')).toBeInTheDocument()
    })
  })

  it('renders search input', async () => {
    renderNotesPage()

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Поиск в заметках...')).toBeInTheDocument()
    })
  })

  it('renders notes after loading', async () => {
    renderNotesPage()

    // Wait for notes to load — subject names appear both in cards and filter options
    await waitFor(() => {
      expect(screen.getAllByText('Физика').length).toBeGreaterThanOrEqual(1)
    })

    expect(screen.getAllByText('Математический анализ').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Программирование').length).toBeGreaterThanOrEqual(1)
  })

  it('renders subject filter with all subjects', async () => {
    renderNotesPage()

    await waitFor(() => {
      expect(screen.getByDisplayValue('Все предметы')).toBeInTheDocument()
    })

    // Verify filter options contain subject names
    const select = screen.getByDisplayValue('Все предметы')
    expect(select).toBeInTheDocument()
    const options = select.querySelectorAll('option')
    const optionTexts = Array.from(options).map((o) => o.textContent)
    expect(optionTexts).toContain('Физика')
    expect(optionTexts).toContain('Математический анализ')
    expect(optionTexts).toContain('Программирование')
  })

  it('renders empty state when no notes', async () => {
    server.use(
      http.get('/api/v1/notes/', () => {
        return HttpResponse.json([])
      }),
    )

    renderNotesPage()

    await waitFor(() => {
      expect(screen.getByText('Нет заметок')).toBeInTheDocument()
    })
  })

  it('renders error state', async () => {
    server.use(
      http.get('/api/v1/notes/', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    renderNotesPage()

    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки заметок')).toBeInTheDocument()
    })
  })

  it('shows delete confirmation modal', async () => {
    renderNotesPage()

    await waitFor(() => {
      expect(screen.getAllByLabelText('Удалить заметку').length).toBeGreaterThan(0)
    })

    // Click the first delete button
    const deleteButtons = screen.getAllByLabelText('Удалить заметку')
    fireEvent.click(deleteButtons[0])

    expect(screen.getByText('Удалить заметку?')).toBeInTheDocument()
    expect(screen.getByText('Это действие нельзя отменить.')).toBeInTheDocument()
  })

  it('can close delete modal with cancel', async () => {
    renderNotesPage()

    await waitFor(() => {
      expect(screen.getAllByLabelText('Удалить заметку').length).toBeGreaterThan(0)
    })

    const deleteButtons = screen.getAllByLabelText('Удалить заметку')
    fireEvent.click(deleteButtons[0])

    // Cancel
    fireEvent.click(screen.getByText('Отмена'))

    await waitFor(() => {
      expect(screen.queryByText('Удалить заметку?')).not.toBeInTheDocument()
    })
  })
})
