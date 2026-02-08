import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AttendanceStatsCard } from '../AttendanceStatsCard'
import type { AttendanceStats } from '@/types/attendance'

const fullStats: AttendanceStats = {
  total_classes: 20,
  absences: 3,
  attended: 17,
  attendance_percent: 85.0,
  by_subject: [],
}

const zeroStats: AttendanceStats = {
  total_classes: 0,
  absences: 0,
  attended: 0,
  attendance_percent: 100.0,
  by_subject: [],
}

describe('AttendanceStatsCard', () => {
  it('renders attendance percentage', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    expect(screen.getByText('85.0%')).toBeInTheDocument()
  })

  it('renders attended count', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    expect(screen.getByText(/17 из 20 занятий/)).toBeInTheDocument()
  })

  it('renders absences count', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    expect(screen.getByText(/3/)).toBeInTheDocument()
  })

  it('renders progress bar', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('does not show absences line when 0', () => {
    render(<AttendanceStatsCard stats={zeroStats} />)

    expect(screen.queryByText(/Пропущено/)).not.toBeInTheDocument()
  })
})
