import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import { useAuthStore } from '@/stores/authStore'
import { testUser, testWeekSchedule, testCurrentLesson } from '@/test/mocks/handlers'
import { SchedulePage } from '../SchedulePage'

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

function renderSchedulePage() {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <SchedulePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('SchedulePage', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: testUser,
      isAuthenticated: true,
      isLoading: false,
    })
  })

  it('renders page header', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Расписание')).toBeInTheDocument()
    })
  })

  it('renders week schedule after loading', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Неделя 6')).toBeInTheDocument()
    })

    expect(screen.getByText('(чётная)')).toBeInTheDocument()
  })

  it('renders schedule entries', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    })

    expect(screen.getByText('Физика')).toBeInTheDocument()
    expect(screen.getByText('Программирование')).toBeInTheDocument()
  })

  it('shows next lesson indicator', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Следующая:')).toBeInTheDocument()
    })

    expect(screen.getByText(testCurrentLesson.next!.subject_name)).toBeInTheDocument()
  })

  it('renders navigation buttons', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Неделя 6')).toBeInTheDocument()
    })

    // Previous/next week buttons
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBeGreaterThanOrEqual(3)
  })

  it('shows error state on API failure', async () => {
    server.use(
      http.get('/api/v1/schedule/week', () => {
        return HttpResponse.json(null, { status: 500 })
      }),
    )

    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки расписания')).toBeInTheDocument()
    })

    expect(screen.getByText('Попробовать снова')).toBeInTheDocument()
  })

  it('has refresh button', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Неделя 6')).toBeInTheDocument()
    })

    const refreshButton = screen.getByTitle('Обновить с сайта ОмГУ')
    expect(refreshButton).toBeInTheDocument()
  })

  it('opens lesson modal on entry click', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    })

    // Click on a schedule entry (via aria-label in grid)
    const gridCell = screen.getByRole('gridcell', {
      name: /Математический анализ/,
    })
    fireEvent.click(gridCell.querySelector('[role="button"]')!)

    // Modal should appear
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  it('can close lesson modal', async () => {
    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    })

    // Open modal
    const gridCell = screen.getByRole('gridcell', {
      name: /Математический анализ/,
    })
    fireEvent.click(gridCell.querySelector('[role="button"]')!)

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    // Close modal
    const closeButton = screen.getByLabelText('Закрыть')
    fireEvent.click(closeButton)

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  it('shows empty state when no entries', async () => {
    server.use(
      http.get('/api/v1/schedule/week', () => {
        return HttpResponse.json({
          ...testWeekSchedule,
          days: testWeekSchedule.days.map((d) => ({ ...d, entries: [] })),
        })
      }),
    )

    renderSchedulePage()

    await waitFor(() => {
      expect(screen.getByText('На этой неделе нет занятий')).toBeInTheDocument()
    })
  })
})
