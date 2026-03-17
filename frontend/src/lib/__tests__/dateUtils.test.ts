import { describe, it, expect, vi, afterEach } from 'vitest'
import {
  formatDeadline,
  getDeadlineColor,
  formatDateLocal,
  getToday,
  formatTime,
  formatTimeUntil,
  formatLocation,
  appendTimezoneOffset,
  toLocalDatetimeString,
} from '../dateUtils'

describe('formatDeadline', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns "Просрочено" for past dates', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-05')).toBe('Просрочено')
  })

  it('returns "Сегодня" with time when hasTime=true', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T14:00:00'))

    expect(formatDeadline('2026-02-07T12:00:00')).toBe('Сегодня 12:00')
  })

  it('returns "Сегодня" without time when hasTime=false', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T14:00:00'))

    expect(formatDeadline('2026-02-07T12:00:00', false)).toBe('Сегодня')
  })

  it('returns "Завтра" with time when hasTime=true', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-08T12:00:00')).toBe('Завтра 12:00')
  })

  it('returns "Завтра" without time when hasTime=false', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-08T12:00:00', false)).toBe('Завтра')
  })

  it('returns "Через N дн." with time when hasTime=true', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-12T12:00:00')).toBe('Через 5 дн. 12:00')
  })

  it('returns "Через N дн." without time when hasTime=false', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-12T12:00:00', false)).toBe('Через 5 дн.')
  })

  it('returns formatted date with time for dates beyond 7 days', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const result = formatDeadline('2026-03-01T12:00:00')
    expect(result).toContain('1')
    expect(result).toMatch(/мар/i)
    expect(result).toContain('12:00')
  })

  it('returns formatted date without time when hasTime=false', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const result = formatDeadline('2026-03-01T12:00:00', false)
    expect(result).toContain('1')
    expect(result).toMatch(/мар/i)
    expect(result).not.toContain('12:00')
  })

  it('returns "Просрочено" for past dates with not_started status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-05', true, 'not_started')).toBe('Просрочено')
  })

  it('returns "Просрочено" for past dates with no status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(formatDeadline('2026-02-05')).toBe('Просрочено')
    expect(formatDeadline('2026-02-05', true, undefined)).toBe('Просрочено')
  })

  it('returns date instead of "Просрочено" for in_progress status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const result = formatDeadline('2026-02-05T14:00:00', true, 'in_progress')
    expect(result).not.toBe('Просрочено')
    expect(result).toContain('5')
    expect(result).toMatch(/февр/i)
    expect(result).toContain('14:00')
  })

  it('returns date instead of "Просрочено" for completed status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    const result = formatDeadline('2026-02-05T14:00:00', false, 'completed')
    expect(result).not.toBe('Просрочено')
    expect(result).toContain('5')
  })

  it('returns "Сегодня" for date-only deadline later the same day', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T08:00:00'))

    expect(formatDeadline('2026-02-07T23:59:00', false)).toBe('Сегодня')
  })

  it('returns "Завтра" for date-only deadline tomorrow viewed late today', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T22:00:00'))

    expect(formatDeadline('2026-02-08T06:00:00', false)).toBe('Завтра')
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

  it('returns muted for overdue with in_progress status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(getDeadlineColor('2026-02-05', 'in_progress')).toContain('muted')
    expect(getDeadlineColor('2026-02-05', 'completed')).toContain('muted')
    expect(getDeadlineColor('2026-02-05', 'submitted')).toContain('muted')
  })

  it('returns red for overdue with not_started status', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-02-07T12:00:00'))

    expect(getDeadlineColor('2026-02-05', 'not_started')).toContain('red')
    expect(getDeadlineColor('2026-02-05')).toContain('red')
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

describe('formatTime', () => {
  it('formats HH:MM:SS to HH:MM', () => {
    expect(formatTime('10:30:00')).toBe('10:30')
  })

  it('handles midnight', () => {
    expect(formatTime('00:00:00')).toBe('00:00')
  })

  it('handles single-digit hours in string', () => {
    expect(formatTime('09:05:00')).toBe('09:05')
  })
})

describe('formatTimeUntil', () => {
  it('returns "менее минуты" for less than 1 minute', () => {
    expect(formatTimeUntil(0)).toBe('менее минуты')
    expect(formatTimeUntil(0.5)).toBe('менее минуты')
  })

  it('returns minutes for less than 60 minutes', () => {
    expect(formatTimeUntil(1)).toBe('1 мин')
    expect(formatTimeUntil(5)).toBe('5 мин')
    expect(formatTimeUntil(59)).toBe('59 мин')
  })

  it('returns hours only when minutes are zero', () => {
    expect(formatTimeUntil(60)).toBe('1 ч')
    expect(formatTimeUntil(120)).toBe('2 ч')
  })

  it('returns hours and minutes', () => {
    expect(formatTimeUntil(90)).toBe('1 ч 30 мин')
    expect(formatTimeUntil(61)).toBe('1 ч 1 мин')
  })
})

describe('formatLocation', () => {
  it('returns "building-room" when both are present', () => {
    expect(formatLocation('6', '113')).toBe('6-113')
    expect(formatLocation('7', '140')).toBe('7-140')
  })

  it('cleans parentheses from building', () => {
    expect(formatLocation('(6', '113')).toBe('6-113')
    expect(formatLocation('6)', '113')).toBe('6-113')
    expect(formatLocation('(6)', '113')).toBe('6-113')
  })

  it('returns only building when room is null', () => {
    expect(formatLocation('6', null)).toBe('6')
    expect(formatLocation('(7', undefined)).toBe('7')
  })

  it('returns only room when building is null', () => {
    expect(formatLocation(null, '113')).toBe('113')
    expect(formatLocation(undefined, '140')).toBe('140')
  })

  it('returns null when both are null', () => {
    expect(formatLocation(null, null)).toBeNull()
    expect(formatLocation(undefined, undefined)).toBeNull()
  })

  it('extracts room number from "зал" strings', () => {
    expect(formatLocation('(6', '113) Спортивный зал')).toBe('6-113')
    expect(formatLocation('6', '115) Тренажерный зал')).toBe('6-115')
  })

  it('returns only building when "зал" has no room number', () => {
    expect(formatLocation('6', 'Спортивный зал')).toBe('6')
    expect(formatLocation('(6', 'Тренажерный зал')).toBe('6')
  })

  it('returns null when room is "зал" without number and no building', () => {
    expect(formatLocation(null, 'Спортивный зал')).toBeNull()
  })

  it('handles real API format "(6" + "113) Спортивный зал"', () => {
    expect(formatLocation('(6', '113) Спортивный зал')).toBe('6-113')
  })

  it('strips "Корпус" prefix from building', () => {
    expect(formatLocation('Корпус 2', '201')).toBe('2-201')
    expect(formatLocation('Корпус 1', '301')).toBe('1-301')
    expect(formatLocation('корпус 3', '101')).toBe('3-101')
  })

  it('strips "корпус" suffix from building', () => {
    expect(formatLocation('1 корпус', '301')).toBe('1-301')
  })

  it('strips "корп." abbreviation from building', () => {
    expect(formatLocation('корп. 2', '215')).toBe('2-215')
    expect(formatLocation('корп 3', '101')).toBe('3-101')
  })

  it('strips "ауд." prefix from room', () => {
    expect(formatLocation(null, 'ауд. 301')).toBe('301')
    expect(formatLocation('6', 'ауд. 114')).toBe('6-114')
  })

  it('strips "ауд." prefix from room with "зал"', () => {
    expect(formatLocation(null, 'ауд. 114 Спортивный зал')).toBe('114')
  })
})

describe('appendTimezoneOffset', () => {
  it('appends timezone offset to naive datetime', () => {
    const result = appendTimezoneOffset('2026-03-12T18:00')
    // Should end with timezone offset like +06:00 or -05:00
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/)
  })

  it('adds seconds if missing', () => {
    const result = appendTimezoneOffset('2026-03-12T18:00')
    expect(result).toContain('T18:00:00')
  })

  it('preserves seconds if already present', () => {
    const result = appendTimezoneOffset('2026-03-12T18:00:30')
    expect(result).toContain('T18:00:30')
  })
})

describe('toLocalDatetimeString', () => {
  it('converts ISO string to YYYY-MM-DDTHH:MM format', () => {
    // Use a date that we know the local representation of
    const result = toLocalDatetimeString('2026-03-12T12:00:00')
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
  })

  it('produces valid datetime-local input value', () => {
    const input = '2026-06-15T09:30:00'
    const result = toLocalDatetimeString(input)
    // Should be parseable as a date
    expect(new Date(result).toString()).not.toBe('Invalid Date')
  })
})
