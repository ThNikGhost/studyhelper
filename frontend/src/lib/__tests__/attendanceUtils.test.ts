import { describe, it, expect } from 'vitest'
import {
  formatAttendancePercent,
  getAttendanceColor,
  getAttendanceBarColor,
  lessonTypeLabels,
} from '../attendanceUtils'

describe('formatAttendancePercent', () => {
  it('formats 100%', () => {
    expect(formatAttendancePercent(100)).toBe('100.0%')
  })

  it('formats 0%', () => {
    expect(formatAttendancePercent(0)).toBe('0.0%')
  })

  it('formats decimal percent', () => {
    expect(formatAttendancePercent(85.7)).toBe('85.7%')
  })

  it('formats percent with rounding', () => {
    expect(formatAttendancePercent(66.666)).toBe('66.7%')
  })
})

describe('getAttendanceColor', () => {
  it('returns green for >= 80%', () => {
    expect(getAttendanceColor(80)).toBe('text-green-600 dark:text-green-400')
    expect(getAttendanceColor(100)).toBe('text-green-600 dark:text-green-400')
  })

  it('returns yellow for >= 60% and < 80%', () => {
    expect(getAttendanceColor(60)).toBe('text-yellow-600 dark:text-yellow-400')
    expect(getAttendanceColor(79)).toBe('text-yellow-600 dark:text-yellow-400')
  })

  it('returns red for < 60%', () => {
    expect(getAttendanceColor(59)).toBe('text-red-600 dark:text-red-400')
    expect(getAttendanceColor(0)).toBe('text-red-600 dark:text-red-400')
  })
})

describe('getAttendanceBarColor', () => {
  it('returns green bg for >= 80%', () => {
    expect(getAttendanceBarColor(80)).toBe('bg-green-500')
  })

  it('returns yellow bg for >= 60% and < 80%', () => {
    expect(getAttendanceBarColor(70)).toBe('bg-yellow-500')
  })

  it('returns red bg for < 60%', () => {
    expect(getAttendanceBarColor(30)).toBe('bg-red-500')
  })
})

describe('lessonTypeLabels', () => {
  it('has label for lecture', () => {
    expect(lessonTypeLabels.lecture).toBe('Лекция')
  })

  it('has label for practice', () => {
    expect(lessonTypeLabels.practice).toBe('Практика')
  })
})
