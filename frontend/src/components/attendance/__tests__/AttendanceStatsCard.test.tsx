import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AttendanceStatsCard } from '../AttendanceStatsCard'
import type { AttendanceStats } from '@/types/attendance'

const fullStats: AttendanceStats = {
  total_planned: 96,
  total_completed: 20,
  total_classes: 20,
  absences: 3,
  attended: 17,
  attendance_percent: 17.7,
  by_subject: [],
}

const zeroStats: AttendanceStats = {
  total_planned: 96,
  total_completed: 0,
  total_classes: 0,
  absences: 0,
  attended: 0,
  attendance_percent: 0.0,
  by_subject: [],
}

const noPlannedStats: AttendanceStats = {
  total_planned: 0,
  total_completed: 10,
  total_classes: 10,
  absences: 2,
  attended: 8,
  attendance_percent: 80.0,
  by_subject: [],
}

describe('AttendanceStatsCard', () => {
  it('renders attended count out of total planned', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    // New format: "17 из 96" (attended out of total_planned)
    expect(screen.getByText(/17 из 96/)).toBeInTheDocument()
  })

  it('renders attendance percentage', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    expect(screen.getByText(/17\.7%/)).toBeInTheDocument()
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

  it('falls back to total_completed when total_planned is 0', () => {
    render(<AttendanceStatsCard stats={noPlannedStats} />)

    // When no planned classes, use total_completed as denominator
    expect(screen.getByText(/8 из 10/)).toBeInTheDocument()
  })

  it('shows completed classes count when has planned', () => {
    render(<AttendanceStatsCard stats={fullStats} />)

    // Shows "Пройдено занятий: X из Y запланированных"
    expect(screen.getByText(/Пройдено занятий: 20 из 96 запланированных/)).toBeInTheDocument()
  })
})
