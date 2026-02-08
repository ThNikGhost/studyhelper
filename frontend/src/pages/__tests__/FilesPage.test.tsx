import { describe, it, expect } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import FilesPage from '../FilesPage'

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

function renderFilesPage() {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <FilesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('FilesPage', () => {
  it('renders page title', () => {
    renderFilesPage()

    expect(screen.getByText('Файлы')).toBeInTheDocument()
  })

  it('renders dropzone', () => {
    renderFilesPage()

    expect(screen.getByText(/Перетащите файл/)).toBeInTheDocument()
  })

  it('renders file list after loading', async () => {
    renderFilesPage()

    await waitFor(() => {
      expect(screen.getByText('Лекция_01.pdf')).toBeInTheDocument()
    })

    expect(screen.getByText('Задачник.docx')).toBeInTheDocument()
    expect(screen.getByText('Шпаргалка.png')).toBeInTheDocument()
  })

  it('renders filter selects', () => {
    renderFilesPage()

    expect(screen.getByLabelText('Фильтр по предмету')).toBeInTheDocument()
    expect(screen.getByLabelText('Фильтр по категории')).toBeInTheDocument()
  })

  it('shows error state when API fails', async () => {
    server.use(
      http.get('/api/v1/files/', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    renderFilesPage()

    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки файлов')).toBeInTheDocument()
    })
  })

  it('shows delete confirmation modal', async () => {
    renderFilesPage()

    await waitFor(() => {
      expect(screen.getByText('Лекция_01.pdf')).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByLabelText(/Удалить/)
    fireEvent.click(deleteButtons[0])

    expect(screen.getByText('Удалить файл?')).toBeInTheDocument()
    expect(screen.getByText(/будет удалён/)).toBeInTheDocument()
  })

  it('renders back link to dashboard', () => {
    renderFilesPage()

    const backLink = screen.getByRole('link', { name: '' })
    expect(backLink).toHaveAttribute('href', '/')
  })

  it('renders refresh button', () => {
    renderFilesPage()

    expect(screen.getByLabelText('Обновить')).toBeInTheDocument()
  })
})
