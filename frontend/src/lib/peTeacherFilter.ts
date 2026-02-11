/**
 * PE (Physical Education) teacher preference filter.
 *
 * The university schedule has multiple PE entries at the same time slot
 * (one per teacher/section). This utility lets the user pick their
 * preferred teacher and filters out the rest.
 */

import type { ScheduleEntry, DaySchedule, WeekSchedule } from '@/types/schedule'

const PE_KEYWORDS = ['физическая культура', 'физическ']

/** Check if a schedule entry is a PE lesson. */
export function isPeEntry(entry: ScheduleEntry): boolean {
  const name = entry.subject_name.toLowerCase()
  return PE_KEYWORDS.some((kw) => name.includes(kw))
}

/**
 * Filter schedule entries: keep only the preferred PE teacher, pass through all other entries.
 *
 * @param entries - Schedule entries to filter.
 * @param preferredTeacher - Preferred teacher name (from settingsStore).
 */
export function filterPeEntries(
  entries: ScheduleEntry[],
  preferredTeacher: string | null,
): ScheduleEntry[] {
  if (!preferredTeacher) return entries

  return entries.filter((entry) => {
    if (!isPeEntry(entry)) return true
    return entry.teacher_name === preferredTeacher
  })
}

/**
 * Filter a DaySchedule, applying PE teacher filter to its entries.
 *
 * @param day - Day schedule to filter.
 * @param preferredTeacher - Preferred teacher name (from settingsStore).
 */
export function filterDaySchedule(
  day: DaySchedule,
  preferredTeacher: string | null,
): DaySchedule {
  return {
    ...day,
    entries: filterPeEntries(day.entries, preferredTeacher),
  }
}

/**
 * Filter a WeekSchedule, applying PE teacher filter to all days.
 *
 * @param week - Week schedule to filter.
 * @param preferredTeacher - Preferred teacher name (from settingsStore).
 */
export function filterWeekSchedule(
  week: WeekSchedule,
  preferredTeacher: string | null,
): WeekSchedule {
  return {
    ...week,
    days: week.days.map((d) => filterDaySchedule(d, preferredTeacher)),
  }
}

/** Extract unique PE teacher names from a list of entries. */
export function getUniquePeTeachers(entries: ScheduleEntry[]): string[] {
  const teachers = new Set<string>()
  for (const entry of entries) {
    if (isPeEntry(entry) && entry.teacher_name) {
      teachers.add(entry.teacher_name)
    }
  }
  return Array.from(teachers).sort()
}

/** Extract unique PE teacher names from a WeekSchedule. */
export function getPeTeachersFromWeek(week: WeekSchedule): string[] {
  const allEntries = week.days.flatMap((d) => d.entries)
  return getUniquePeTeachers(allEntries)
}
