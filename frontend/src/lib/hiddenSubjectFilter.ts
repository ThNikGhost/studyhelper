/**
 * Hidden subject filtering utilities.
 *
 * Filters schedule entries, days, and weeks by hidden subject config.
 * Supports per-lesson-type hiding: a subject can hide specific types
 * (e.g. only labs) while keeping others visible.
 *
 * Schedule entries from OmSU parser have subject_id=NULL, so we match
 * by subject_name instead of subject_id.
 */

import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

/**
 * Filter schedule entries by hidden subject config.
 *
 * @param entries - Schedule entries to filter.
 * @param hiddenEntries - Map of subject name → hidden lesson types (null = all).
 * @returns Filtered entries.
 */
export function filterHiddenEntries(
  entries: ScheduleEntry[],
  hiddenEntries: Map<string, Set<string> | null>,
): ScheduleEntry[] {
  if (hiddenEntries.size === 0) return entries
  return entries.filter((entry) => {
    const types = hiddenEntries.get(entry.subject_name)
    if (types === undefined) return true // not hidden
    if (types === null) return false // fully hidden
    return !types.has(entry.lesson_type) // type-specific
  })
}

/**
 * Filter a DaySchedule by hidden subject config.
 *
 * @param day - Day schedule to filter.
 * @param hiddenEntries - Map of subject name → hidden lesson types (null = all).
 * @returns Filtered day schedule.
 */
export function filterDayByHidden(
  day: DaySchedule,
  hiddenEntries: Map<string, Set<string> | null>,
): DaySchedule {
  if (hiddenEntries.size === 0) return day
  return {
    ...day,
    entries: filterHiddenEntries(day.entries, hiddenEntries),
  }
}

/**
 * Filter a WeekSchedule by hidden subject config.
 *
 * @param week - Week schedule to filter.
 * @param hiddenEntries - Map of subject name → hidden lesson types (null = all).
 * @returns Filtered week schedule.
 */
export function filterWeekByHidden(
  week: WeekSchedule,
  hiddenEntries: Map<string, Set<string> | null>,
): WeekSchedule {
  if (hiddenEntries.size === 0) return week
  return {
    ...week,
    days: week.days.map((d) => filterDayByHidden(d, hiddenEntries)),
  }
}
