import { describe, it, expect } from 'vitest'
import {
  filterHiddenEntries,
  filterDayByHidden,
  filterWeekByHidden,
} from '../hiddenSubjectFilter'
import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

function makeEntry(overrides: Partial<ScheduleEntry> = {}): ScheduleEntry {
  return {
    id: 1,
    subject_name: 'Математика',
    subject_id: null,
    teacher_name: null,
    lesson_type: 'lecture',
    start_time: '09:00',
    end_time: '10:30',
    room: null,
    building: null,
    subgroup: null,
    lesson_date: '2026-01-15',
    day_of_week: 1,
    ...overrides,
  } as ScheduleEntry
}

function makeDay(entries: ScheduleEntry[]): DaySchedule {
  return {
    day_of_week: 1,
    day_name: 'Понедельник',
    date: '2026-01-15',
    entries,
  } as DaySchedule
}

function makeWeek(days: DaySchedule[]): WeekSchedule {
  return {
    week_start: '2026-01-13',
    week_end: '2026-01-19',
    week_number: 3,
    is_odd_week: true,
    days,
  } as WeekSchedule
}

describe('filterHiddenEntries', () => {
  it('returns all entries when hiddenEntries is empty', () => {
    const entries = [makeEntry(), makeEntry({ subject_name: 'Физика' })]
    const result = filterHiddenEntries(entries, new Map())
    expect(result).toHaveLength(2)
  })

  it('filters out fully hidden subjects (null = all types)', () => {
    const entries = [
      makeEntry({ subject_name: 'Математика' }),
      makeEntry({ subject_name: 'Физика' }),
      makeEntry({ subject_name: 'Химия' }),
    ]
    const hidden = new Map<string, Set<string> | null>([['Физика', null]])
    const result = filterHiddenEntries(entries, hidden)
    expect(result).toHaveLength(2)
    expect(result.map((e) => e.subject_name)).toEqual(['Математика', 'Химия'])
  })

  it('filters only specific lesson types', () => {
    const entries = [
      makeEntry({ subject_name: 'Математика', lesson_type: 'lecture' }),
      makeEntry({ subject_name: 'Математика', lesson_type: 'lab' }),
      makeEntry({ subject_name: 'Математика', lesson_type: 'practice' }),
    ]
    const hidden = new Map<string, Set<string> | null>([
      ['Математика', new Set(['lab'])],
    ])
    const result = filterHiddenEntries(entries, hidden)
    expect(result).toHaveLength(2)
    expect(result.map((e) => e.lesson_type)).toEqual(['lecture', 'practice'])
  })

  it('filters multiple lesson types for one subject', () => {
    const entries = [
      makeEntry({ subject_name: 'Физика', lesson_type: 'lecture' }),
      makeEntry({ subject_name: 'Физика', lesson_type: 'lab' }),
      makeEntry({ subject_name: 'Физика', lesson_type: 'practice' }),
    ]
    const hidden = new Map<string, Set<string> | null>([
      ['Физика', new Set(['lab', 'practice'])],
    ])
    const result = filterHiddenEntries(entries, hidden)
    expect(result).toHaveLength(1)
    expect(result[0].lesson_type).toBe('lecture')
  })

  it('handles mixed: one fully hidden, one per-type', () => {
    const entries = [
      makeEntry({ subject_name: 'Математика', lesson_type: 'lecture' }),
      makeEntry({ subject_name: 'Физика', lesson_type: 'lecture' }),
      makeEntry({ subject_name: 'Физика', lesson_type: 'lab' }),
    ]
    const hidden = new Map<string, Set<string> | null>([
      ['Математика', null],
      ['Физика', new Set(['lab'])],
    ])
    const result = filterHiddenEntries(entries, hidden)
    expect(result).toHaveLength(1)
    expect(result[0].subject_name).toBe('Физика')
    expect(result[0].lesson_type).toBe('lecture')
  })

  it('is case-sensitive', () => {
    const entries = [makeEntry({ subject_name: 'Математика' })]
    const hidden = new Map<string, Set<string> | null>([['математика', null]])
    const result = filterHiddenEntries(entries, hidden)
    expect(result).toHaveLength(1)
  })
})

describe('filterDayByHidden', () => {
  it('returns day unchanged when hiddenEntries is empty', () => {
    const day = makeDay([makeEntry()])
    const result = filterDayByHidden(day, new Map())
    expect(result).toBe(day)
  })

  it('filters entries within a day', () => {
    const day = makeDay([
      makeEntry({ subject_name: 'Математика' }),
      makeEntry({ subject_name: 'Физика' }),
    ])
    const hidden = new Map<string, Set<string> | null>([['Математика', null]])
    const result = filterDayByHidden(day, hidden)
    expect(result.entries).toHaveLength(1)
    expect(result.entries[0].subject_name).toBe('Физика')
  })
})

describe('filterWeekByHidden', () => {
  it('returns week unchanged when hiddenEntries is empty', () => {
    const week = makeWeek([makeDay([makeEntry()])])
    const result = filterWeekByHidden(week, new Map())
    expect(result).toBe(week)
  })

  it('filters entries across all days', () => {
    const week = makeWeek([
      makeDay([
        makeEntry({ subject_name: 'Математика' }),
        makeEntry({ subject_name: 'Физика' }),
      ]),
      makeDay([
        makeEntry({ subject_name: 'Математика' }),
        makeEntry({ subject_name: 'Химия' }),
      ]),
    ])
    const hidden = new Map<string, Set<string> | null>([['Математика', null]])
    const result = filterWeekByHidden(week, hidden)
    expect(result.days[0].entries).toHaveLength(1)
    expect(result.days[0].entries[0].subject_name).toBe('Физика')
    expect(result.days[1].entries).toHaveLength(1)
    expect(result.days[1].entries[0].subject_name).toBe('Химия')
  })

  it('per-type filter works across days', () => {
    const week = makeWeek([
      makeDay([
        makeEntry({ subject_name: 'Физика', lesson_type: 'lecture' }),
        makeEntry({ subject_name: 'Физика', lesson_type: 'lab' }),
      ]),
    ])
    const hidden = new Map<string, Set<string> | null>([
      ['Физика', new Set(['lab'])],
    ])
    const result = filterWeekByHidden(week, hidden)
    expect(result.days[0].entries).toHaveLength(1)
    expect(result.days[0].entries[0].lesson_type).toBe('lecture')
  })
})
