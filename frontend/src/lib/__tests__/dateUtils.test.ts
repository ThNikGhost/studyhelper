import { describe, it, expect, vi, afterEach } from 'vitest'
import { formatDeadline, getDeadlineColor, formatDateLocal, getToday } from '../dateUtils'

describe('formatDeadline', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns "Просрочено" for past dates', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-05')).toBe('Просрочено')
  })

  it('returns "Сегодня" when deadline just passed (within 24h)', () => {
    vi.useFakeTimers()
    // diffDays = Math.ceil(diffMs / day) = 0 when diffMs ∈ (-24h, 0]
    vi.setSystemTime(new Date('2026-02-07T14:00:00'))

    expect(formatDeadline('2026-02-07T12:00:00')).toBe('Сегодня')
  })

  it('returns "Завтра" for tomorrow', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-08T12:00:00')).toBe('Завтра')
  })

  it('returns "Через N дн." for dates within 7 days', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-12T12:00:00')).toBe('Через 5 дн.')
  })

  it('returns formatted date for dates beyond 7 days', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const result = formatDeadline('2026-03-01T12:00:00')
    // toLocaleDateString with ru-RU returns something like "1 мар."
    expect(result).toContain('1')
    expect(result).toMatch(/мар/i)
  })
})

describe('getDeadlineColor', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns red classes for overdue deadlines', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(getDeadlineColor('2026-02-05')).toContain('red')
  })

  it('returns orange classes for today/tomorrow (diffDays 0 or 1)', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T14:00:00'))

    // diffDays=0: deadline just passed (within 24h)
    expect(getDeadlineColor('2026-02-07T12:00:00')).toContain('orange')
    // diffDays=1: deadline within next 24h
    expect(getDeadlineColor('2026-02-08T12:00:00')).toContain('orange')
  })

  it('returns yellow classes for 2-3 days away', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(getDeadlineColor('2026-02-09T12:00:00')).toContain('yellow')
    expect(getDeadlineColor('2026-02-10T12:00:00')).toContain('yellow')
  })

  it('returns muted classes for 7+ days away', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(getDeadlineColor('2026-02-20T12:00:00')).toContain('muted')
  })
})

describe('formatDateLocal', () => {
  it('formats a date to YYYY-MM-DD', () => {
    const date = new Date(2026, 0, 15) // Jan 15, 2026
    expect(formatDateLocal(date)).toBe('2026-01-15')
  })

  it('pads single-digit months', () => {
    const date = new Date(2026, 2, 5) // Mar 5, 2026
    expect(formatDateLocal(date)).toBe('2026-03-05')
  })

  it('pads single-digit days', () => {
    const date = new Date(2026, 11, 1) // Dec 1, 2026
    expect(formatDateLocal(date)).toBe('2026-12-01')
  })

  it('uses local timezone (not UTC)', () => {
    // Create a date and verify it uses getFullYear/getMonth/getDate (local)
    const date = new Date(2026, 5, 20) // Jun 20, local
    const result = formatDateLocal(date)
    expect(result).toBe('2026-06-20')
  })
})

describe('getToday', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns YYYY-MM-DD format string', () => {
    const result = getToday()
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('returns the correct date', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 15)) // Jun 15, 2026

    expect(getToday()).toBe('2026-06-15')
  })
})
