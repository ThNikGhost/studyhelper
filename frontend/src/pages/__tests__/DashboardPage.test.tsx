import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import { useAuthStore } from '@/stores/authStore'
import { testUser } from '@/test/mocks/handlers'
import DashboardPage from '../DashboardPage'

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

function renderDashboard() {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: testUser,
      isAuthenticated: true,
      isLoading: false,
    })
  })

  it('renders user greeting', () => {
    renderDashboard()

    expect(screen.getByText(`Привет, ${testUser.name}!`)).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    renderDashboard()

    expect(screen.getByText('Расписание')).toBeInTheDocument()
    expect(screen.getByText('Предметы')).toBeInTheDocument()
    expect(screen.getByText('Работы')).toBeInTheDocument()
    expect(screen.getByText('Одногруппники')).toBeInTheDocument()
    expect(screen.getByText('Семестры')).toBeInTheDocument()
  })

  it('renders today schedule widget', () => {
    renderDashboard()

    expect(screen.getByText('Расписание на сегодня')).toBeInTheDocument()
  })

  it('renders deadlines widget', () => {
    renderDashboard()

    expect(screen.getByText('Ближайшие дедлайны')).toBeInTheDocument()
  })

  it('loads and displays upcoming works', async () => {
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Лабораторная работа №1')).toBeInTheDocument()
    })
  })

  it('loads and displays today schedule data', async () => {
    renderDashboard()

    await waitFor(() => {
      expect(screen.getByText('Математический анализ')).toBeInTheDocument()
      expect(screen.getByText('Физика')).toBeInTheDocument()
      // "Программирование" appears in both schedule widget and deadlines subject_name
      expect(screen.getAllByText('Программирование').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('shows error state for schedule widget on API failure', async () => {
    server.use(
      http.get('/api/v1/schedule/today', () => {
        return HttpResponse.json(null, { status: 500 })
      }),
    )

    renderDashboard()

    await waitFor(() => {
      expect(
        screen.getByText('Не удалось загрузить расписание'),
      ).toBeInTheDocument()
    })
  })

  it('shows error state for deadlines widget on API failure', async () => {
    server.use(
      http.get('/api/v1/works/upcoming', () => {
        return HttpResponse.json(null, { status: 500 })
      }),
    )

    renderDashboard()

    await waitFor(() => {
      expect(
        screen.getByText('Не удалось загрузить дедлайны'),
      ).toBeInTheDocument()
    })
  })

  it('renders StudyHelper header', () => {
    renderDashboard()

    expect(screen.getByText('StudyHelper')).toBeInTheDocument()
  })

  it('displays user name in header', () => {
    renderDashboard()

    // User name appears in header and greeting
    const nameElements = screen.getAllByText(testUser.name)
    expect(nameElements.length).toBeGreaterThanOrEqual(1)
  })
})
