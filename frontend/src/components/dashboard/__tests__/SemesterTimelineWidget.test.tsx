import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { SemesterTimelineWidget } from '../SemesterTimelineWidget'
import { testSemester, testTimelineData } from '@/test/mocks/handlers'

function renderWidget(props: Parameters<typeof SemesterTimelineWidget>[0]) {
  return render(
    <MemoryRouter>
      <SemesterTimelineWidget {...props} />
    </MemoryRouter>,
  )
}

describe('SemesterTimelineWidget', () => {
  it('shows loading state', () => {
    renderWidget({
      semester: null,
      timeline: undefined,
      isLoading: true,
      isError: false,
    })
    expect(screen.getByText('Timeline семестра')).toBeInTheDocument()
  })

  it('shows error state', () => {
    renderWidget({
      semester: null,
      timeline: undefined,
      isLoading: false,
      isError: true,
    })
    expect(screen.getByText('Ошибка загрузки')).toBeInTheDocument()
  })

  it('renders nothing when semester has no dates', () => {
    const { container } = renderWidget({
      semester: { ...testSemester, start_date: null, end_date: null },
      timeline: undefined,
      isLoading: false,
      isError: false,
    })
    expect(container.innerHTML).toBe('')
  })

  it('renders timeline bar with data', () => {
    renderWidget({
      semester: testSemester,
      timeline: testTimelineData,
      isLoading: false,
      isError: false,
    })
    expect(screen.getByText('Timeline семестра')).toBeInTheDocument()
    expect(screen.getByText('Подробнее →')).toBeInTheDocument()
  })

  it('links to full timeline page', () => {
    renderWidget({
      semester: testSemester,
      timeline: testTimelineData,
      isLoading: false,
      isError: false,
    })
    const link = screen.getByText('Подробнее →')
    expect(link.closest('a')).toHaveAttribute('href', '/timeline')
  })
})
