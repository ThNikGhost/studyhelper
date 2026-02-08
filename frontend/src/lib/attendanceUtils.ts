/**
 * Format attendance percentage for display.
 *
 * @param percent - Attendance percentage (0-100).
 * @returns Formatted string like "85.0%".
 */
export function formatAttendancePercent(percent: number): string {
  return `${percent.toFixed(1)}%`
}

/**
 * Get Tailwind text color class based on attendance percentage.
 *
 * - green  for >= 80%
 * - yellow for >= 60%
 * - red    for < 60%
 */
export function getAttendanceColor(percent: number): string {
  if (percent >= 80) return 'text-green-600'
  if (percent >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

/**
 * Get Tailwind background color class for attendance progress bar.
 */
export function getAttendanceBarColor(percent: number): string {
  if (percent >= 80) return 'bg-green-500'
  if (percent >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

/** Mapping of lesson type codes to Russian labels. */
export const lessonTypeLabels: Record<string, string> = {
  lecture: 'Лекция',
  practice: 'Практика',
  lab: 'Лабораторная',
  seminar: 'Семинар',
  exam: 'Экзамен',
  consultation: 'Консультация',
  other: 'Другое',
}
