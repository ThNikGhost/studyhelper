import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/mocks/server'
import { testTimelineData, testSemester, testSemesterNoDates } from '@/test/mocks/handlers'
import TimelinePage from '../TimelinePage'

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TimelinePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TimelinePage', () => {
  it('renders timeline with data', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Timeline')).toBeInTheDocument()
    })
    expect(screen.getByText(testSemester.name)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    renderPage()
    // Should show loading skeleton initially
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument()
  })

  it('shows filter checkboxes', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Дедлайны')).toBeInTheDocument()
    })
    expect(screen.getByText('Экзамены')).toBeInTheDocument()
  })

  it('toggles deadline filter', async () => {
    const user = userEvent.setup()
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Дедлайны')).toBeInTheDocument()
    })

    const checkbox = screen.getByRole('checkbox', { name: /дедлайны/i })
    expect(checkbox).toBeChecked()

    await user.click(checkbox)
    expect(checkbox).not.toBeChecked()
  })

  it('shows message when no current semester', async () => {
    server.use(
      http.get('/api/v1/semesters/current', () => {
        return HttpResponse.json(null)
      }),
    )

    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Текущий семестр не установлен')).toBeInTheDocument()
    })
  })

  it('shows message when semester has no dates', async () => {
    server.use(
      http.get('/api/v1/semesters/current', () => {
        return HttpResponse.json(testSemesterNoDates)
      }),
    )

    renderPage()
    await waitFor(() => {
      expect(screen.getByText(/укажите даты/i)).toBeInTheDocument()
    })
  })

  it('shows error state', async () => {
    server.use(
      http.get('/api/v1/semesters/current', () => {
        return HttpResponse.json({ detail: 'Error' }, { status: 500 })
      }),
    )

    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки данных')).toBeInTheDocument()
    })
  })

  it('renders event list with deadlines and exams', async () => {
    renderPage()
    await waitFor(() => {
      expect(screen.getByText('Ближайшие события')).toBeInTheDocument()
    })
    // Check some event titles are present
    expect(screen.getByText(testTimelineData.deadlines[0].title)).toBeInTheDocument()
  })
})
