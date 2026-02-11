/**
 * Subgroup filtering utilities.
 *
 * Filters schedule entries by user's subgroup and finds alternate entries
 * (entries for other subgroups in the same time slot).
 */

import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

/**
 * Filter schedule entries by subgroup.
 *
 * Keeps entries that match the user's subgroup OR have no subgroup set (general entries).
 *
 * @param entries - Schedule entries to filter.
 * @param userSubgroup - User's subgroup (1, 2, ...) or null to show all.
 * @returns Filtered entries.
 */
export function filterBySubgroup(
  entries: ScheduleEntry[],
  userSubgroup: number | null,
): ScheduleEntry[] {
  // No subgroup selected — show all entries
  if (userSubgroup === null) return entries

  return entries.filter((entry) => {
    // General entry (no subgroup) — always show
    if (entry.subgroup === null) return true
    // Entry matches user's subgroup
    return entry.subgroup === userSubgroup
  })
}

/**
 * Find an alternate entry for a time slot (entry for a different subgroup).
 *
 * Used to show indicator that there's another lesson happening for a different subgroup.
 *
 * @param allEntries - All entries (unfiltered) for the day/week.
 * @param slotStartTime - Start time of the slot (HH:MM:SS format).
 * @param slotDate - Date of the slot (YYYY-MM-DD format).
 * @param userSubgroup - User's subgroup.
 * @returns Alternate entry or undefined if none exists.
 */
export function getAlternateEntryForSlot(
  allEntries: ScheduleEntry[],
  slotStartTime: string,
  slotDate: string,
  userSubgroup: number | null,
): ScheduleEntry | undefined {
  // No subgroup selected — no alternates to show
  if (userSubgroup === null) return undefined

  return allEntries.find((entry) => {
    // Same time slot
    if (entry.start_time !== slotStartTime) return false
    // Same date
    if (entry.lesson_date !== slotDate) return false
    // Different subgroup (not null and not user's)
    if (entry.subgroup === null) return false
    if (entry.subgroup === userSubgroup) return false
    return true
  })
}

/**
 * Filter a DaySchedule by subgroup.
 *
 * @param day - Day schedule to filter.
 * @param userSubgroup - User's subgroup or null to show all.
 * @returns Filtered day schedule.
 */
export function filterDayBySubgroup(
  day: DaySchedule,
  userSubgroup: number | null,
): DaySchedule {
  return {
    ...day,
    entries: filterBySubgroup(day.entries, userSubgroup),
  }
}

/**
 * Filter a WeekSchedule by subgroup.
 *
 * @param week - Week schedule to filter.
 * @param userSubgroup - User's subgroup or null to show all.
 * @returns Filtered week schedule.
 */
export function filterWeekBySubgroup(
  week: WeekSchedule,
  userSubgroup: number | null,
): WeekSchedule {
  return {
    ...week,
    days: week.days.map((d) => filterDayBySubgroup(d, userSubgroup)),
  }
}

/**
 * Get all unique subgroup numbers from entries.
 *
 * @param entries - Schedule entries.
 * @returns Sorted array of subgroup numbers (excluding null).
 */
export function getUniqueSubgroups(entries: ScheduleEntry[]): number[] {
  const subgroups = new Set<number>()
  for (const entry of entries) {
    if (entry.subgroup !== null) {
      subgroups.add(entry.subgroup)
    }
  }
  return Array.from(subgroups).sort((a, b) => a - b)
}

/**
 * Get unique subgroups from a WeekSchedule.
 *
 * @param week - Week schedule.
 * @returns Sorted array of subgroup numbers.
 */
export function getSubgroupsFromWeek(week: WeekSchedule): number[] {
  const allEntries = week.days.flatMap((d) => d.entries)
  return getUniqueSubgroups(allEntries)
}
