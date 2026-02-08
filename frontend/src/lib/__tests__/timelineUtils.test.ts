import { describe, it, expect, vi, afterEach } from 'vitest'
import {
  getPositionPercent,
  getMonthLabels,
  getSemesterProgress,
  getMarkerColor,
  getExamMarkerColor,
} from '../timelineUtils'

describe('getPositionPercent', () => {
  it('returns 0 for start date', () => {
    expect(getPositionPercent('2025-09-01', '2025-09-01', '2026-01-31')).toBe(0)
  })

  it('returns 100 for end date', () => {
    expect(getPositionPercent('2026-01-31', '2025-09-01', '2026-01-31')).toBe(100)
  })

  it('returns ~50 for midpoint', () => {
    const result = getPositionPercent('2025-11-15', '2025-09-01', '2026-01-31')
    expect(result).toBeGreaterThan(45)
    expect(result).toBeLessThan(55)
  })

  it('clamps to 0 for date before start', () => {
    expect(getPositionPercent('2025-01-01', '2025-09-01', '2026-01-31')).toBe(0)
  })

  it('clamps to 100 for date after end', () => {
    expect(getPositionPercent('2026-06-01', '2025-09-01', '2026-01-31')).toBe(100)
  })

  it('returns 0 if end <= start', () => {
    expect(getPositionPercent('2025-10-01', '2026-01-31', '2025-09-01')).toBe(0)
  })
})

describe('getMonthLabels', () => {
  it('returns month labels for a semester', () => {
    const labels = getMonthLabels('2025-09-01', '2026-01-31')
    expect(labels.length).toBeGreaterThanOrEqual(4)
    // Sep 1 is the 1st, so Sep is included
    expect(labels[0].label).toBe('Сен')
  })

  it('returns empty array if end <= start', () => {
    expect(getMonthLabels('2026-01-31', '2025-09-01')).toEqual([])
  })

  it('includes first month if start is the 1st', () => {
    const labels = getMonthLabels('2025-09-01', '2025-12-31')
    expect(labels[0].label).toBe('Сен')
    expect(labels[0].percent).toBe(0)
  })

  it('all labels have percent between 0 and 100', () => {
    const labels = getMonthLabels('2025-09-01', '2026-06-30')
    for (const label of labels) {
      expect(label.percent).toBeGreaterThanOrEqual(0)
      expect(label.percent).toBeLessThanOrEqual(100)
    }
  })
})

describe('getSemesterProgress', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns 0 before semester starts', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-08-01'))
    expect(getSemesterProgress('2025-09-01', '2026-01-31')).toBe(0)
  })

  it('returns 100 after semester ends', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-01'))
    expect(getSemesterProgress('2025-09-01', '2026-01-31')).toBe(100)
  })
})

describe('getMarkerColor', () => {
  it('returns green for completed status', () => {
    expect(getMarkerColor('2025-10-01', 'completed')).toBe('bg-green-500')
  })

  it('returns green for submitted status', () => {
    expect(getMarkerColor('2025-10-01', 'submitted')).toBe('bg-green-500')
  })

  it('returns green for graded status', () => {
    expect(getMarkerColor('2025-10-01', 'graded')).toBe('bg-green-500')
  })

  it('returns yellow for in_progress status', () => {
    expect(getMarkerColor('2099-10-01', 'in_progress')).toBe('bg-yellow-500')
  })

  it('returns red for overdue not_started', () => {
    expect(getMarkerColor('2020-01-01', 'not_started')).toBe('bg-red-500')
  })

  it('returns gray for future not_started', () => {
    expect(getMarkerColor('2099-12-31', 'not_started')).toBe('bg-gray-400')
  })

  it('returns red for overdue with null status', () => {
    expect(getMarkerColor('2020-01-01', null)).toBe('bg-red-500')
  })

  it('returns gray for future with null status', () => {
    expect(getMarkerColor('2099-12-31', null)).toBe('bg-gray-400')
  })
})

describe('getExamMarkerColor', () => {
  it('returns purple', () => {
    expect(getExamMarkerColor()).toBe('bg-purple-500')
  })
})
