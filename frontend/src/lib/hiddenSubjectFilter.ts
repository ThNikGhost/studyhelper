/**
 * Hidden subject filtering utilities.
 *
 * Filters schedule entries, days, and weeks by hidden subject names.
 * Schedule entries from OmSU parser have subject_id=NULL, so we match
 * by subject_name instead of subject_id.
 */

import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

/**
 * Filter schedule entries by hidden subject names.
 *
 * @param entries - Schedule entries to filter.
 * @param hiddenNames - Subject names to hide.
 * @returns Filtered entries.
 */
export function filterHiddenEntries(
  entries: ScheduleEntry[],
  hiddenNames: Set<string>,
): ScheduleEntry[] {
  if (hiddenNames.size === 0) return entries
  return entries.filter((entry) => !hiddenNames.has(entry.subject_name))
}

/**
 * Filter a DaySchedule by hidden subject names.
 *
 * @param day - Day schedule to filter.
 * @param hiddenNames - Subject names to hide.
 * @returns Filtered day schedule.
 */
export function filterDayByHidden(
  day: DaySchedule,
  hiddenNames: Set<string>,
): DaySchedule {
  if (hiddenNames.size === 0) return day
  return {
    ...day,
    entries: filterHiddenEntries(day.entries, hiddenNames),
  }
}

/**
 * Filter a WeekSchedule by hidden subject names.
 *
 * @param week - Week schedule to filter.
 * @param hiddenNames - Subject names to hide.
 * @returns Filtered week schedule.
 */
export function filterWeekByHidden(
  week: WeekSchedule,
  hiddenNames: Set<string>,
): WeekSchedule {
  if (hiddenNames.size === 0) return week
  return {
    ...week,
    days: week.days.map((d) => filterDayByHidden(d, hiddenNames)),
  }
}
