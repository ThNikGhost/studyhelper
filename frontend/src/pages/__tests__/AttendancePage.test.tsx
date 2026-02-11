import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import AttendancePage from '../AttendancePage'

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

function renderAttendancePage() {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AttendancePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('AttendancePage', () => {
  it('renders page title', () => {
    renderAttendancePage()

    expect(screen.getByText('Посещаемость')).toBeInTheDocument()
  })

  it('renders stats after loading', async () => {
    renderAttendancePage()

    await waitFor(() => {
      // New format uses total_planned (96) instead of total_classes
      expect(screen.getByText(/8 из 96/)).toBeInTheDocument()
    })

    // Percentage is now based on total_planned
    expect(screen.getByText(/8\.3%/)).toBeInTheDocument()
  })

  it('renders subject breakdown', async () => {
    renderAttendancePage()

    await waitFor(() => {
      expect(screen.getByText('По предметам')).toBeInTheDocument()
    })

    // Subject names appear in both subject list and entries table,
    // so use getAllByText to verify they are present
    expect(screen.getAllByText('Математический анализ').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Физика').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Программирование').length).toBeGreaterThan(0)
  })

  it('renders entries table', async () => {
    renderAttendancePage()

    await waitFor(() => {
      expect(screen.getByText('Журнал занятий')).toBeInTheDocument()
    })
  })

  it('shows error state when stats API fails', async () => {
    server.use(
      http.get('/api/v1/attendance/stats', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    renderAttendancePage()

    await waitFor(() => {
      expect(
        screen.getByText('Ошибка загрузки данных о посещаемости'),
      ).toBeInTheDocument()
    })
  })

  it('renders back link to dashboard', () => {
    renderAttendancePage()

    const backLink = screen.getByRole('link', { name: '' })
    expect(backLink).toHaveAttribute('href', '/')
  })

  it('renders refresh button', () => {
    renderAttendancePage()

    expect(screen.getByLabelText('Обновить')).toBeInTheDocument()
  })

  it('renders progress bars', async () => {
    renderAttendancePage()

    await waitFor(() => {
      const bars = screen.getAllByRole('progressbar')
      expect(bars.length).toBeGreaterThan(0)
    })
  })
})
