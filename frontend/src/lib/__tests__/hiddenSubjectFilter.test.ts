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
  it('returns all entries when hiddenNames is empty', () => {
    const entries = [makeEntry(), makeEntry({ subject_name: 'Физика' })]
    const result = filterHiddenEntries(entries, new Set())
    expect(result).toHaveLength(2)
  })

  it('filters out entries with matching subject_name', () => {
    const entries = [
      makeEntry({ subject_name: 'Математика' }),
      makeEntry({ subject_name: 'Физика' }),
      makeEntry({ subject_name: 'Химия' }),
    ]
    const result = filterHiddenEntries(entries, new Set(['Физика']))
    expect(result).toHaveLength(2)
    expect(result.map((e) => e.subject_name)).toEqual(['Математика', 'Химия'])
  })

  it('filters multiple hidden subjects', () => {
    const entries = [
      makeEntry({ subject_name: 'Математика' }),
      makeEntry({ subject_name: 'Физика' }),
      makeEntry({ subject_name: 'Химия' }),
    ]
    const result = filterHiddenEntries(entries, new Set(['Математика', 'Химия']))
    expect(result).toHaveLength(1)
    expect(result[0].subject_name).toBe('Физика')
  })

  it('is case-sensitive', () => {
    const entries = [makeEntry({ subject_name: 'Математика' })]
    const result = filterHiddenEntries(entries, new Set(['математика']))
    expect(result).toHaveLength(1)
  })
})

describe('filterDayByHidden', () => {
  it('returns day unchanged when hiddenNames is empty', () => {
    const day = makeDay([makeEntry()])
    const result = filterDayByHidden(day, new Set())
    expect(result).toBe(day)
  })

  it('filters entries within a day', () => {
    const day = makeDay([
      makeEntry({ subject_name: 'Математика' }),
      makeEntry({ subject_name: 'Физика' }),
    ])
    const result = filterDayByHidden(day, new Set(['Математика']))
    expect(result.entries).toHaveLength(1)
    expect(result.entries[0].subject_name).toBe('Физика')
  })
})

describe('filterWeekByHidden', () => {
  it('returns week unchanged when hiddenNames is empty', () => {
    const week = makeWeek([makeDay([makeEntry()])])
    const result = filterWeekByHidden(week, new Set())
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
    const result = filterWeekByHidden(week, new Set(['Математика']))
    expect(result.days[0].entries).toHaveLength(1)
    expect(result.days[0].entries[0].subject_name).toBe('Физика')
    expect(result.days[1].entries).toHaveLength(1)
    expect(result.days[1].entries[0].subject_name).toBe('Химия')
  })
})
