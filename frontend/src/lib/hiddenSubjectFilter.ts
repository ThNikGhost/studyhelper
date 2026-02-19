/**
 * Hidden subject filtering utilities.
 *
 * Filters schedule entries, days, and weeks by user's hidden subject IDs.
 */

import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

/**
 * Filter schedule entries by hidden subject IDs.
 *
 * @param entries - Schedule entries to filter.
 * @param hiddenIds - Subject IDs to hide.
 * @returns Filtered entries.
 */
export function filterHiddenEntries(
  entries: ScheduleEntry[],
  hiddenIds: number[],
): ScheduleEntry[] {
  if (hiddenIds.length === 0) return entries
  const hidden = new Set(hiddenIds)
  return entries.filter(
    (entry) => entry.subject_id === null || !hidden.has(entry.subject_id),
  )
}

/**
 * Filter a DaySchedule by hidden subject IDs.
 *
 * @param day - Day schedule to filter.
 * @param hiddenIds - Subject IDs to hide.
 * @returns Filtered day schedule.
 */
export function filterDayByHidden(
  day: DaySchedule,
  hiddenIds: number[],
): DaySchedule {
  if (hiddenIds.length === 0) return day
  return {
    ...day,
    entries: filterHiddenEntries(day.entries, hiddenIds),
  }
}

/**
 * Filter a WeekSchedule by hidden subject IDs.
 *
 * @param week - Week schedule to filter.
 * @param hiddenIds - Subject IDs to hide.
 * @returns Filtered week schedule.
 */
export function filterWeekByHidden(
  week: WeekSchedule,
  hiddenIds: number[],
): WeekSchedule {
  if (hiddenIds.length === 0) return week
  return {
    ...week,
    days: week.days.map((d) => filterDayByHidden(d, hiddenIds)),
  }
}
