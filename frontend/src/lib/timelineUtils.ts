/**
 * Calculate the position percentage of a date within a date range.
 * Returns a value clamped between 0 and 100.
 */
export function getPositionPercent(
  date: string | Date,
  startDate: string | Date,
  endDate: string | Date,
): number {
  const d = new Date(date).getTime()
  const start = new Date(startDate).getTime()
  const end = new Date(endDate).getTime()

  if (end <= start) return 0

  const percent = ((d - start) / (end - start)) * 100
  return Math.max(0, Math.min(100, percent))
}

export interface MonthLabel {
  label: string
  percent: number
}

const MONTH_NAMES_SHORT = [
  'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
  'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек',
]

/**
 * Generate month labels with their position percentages along the timeline.
 */
export function getMonthLabels(
  startDate: string | Date,
  endDate: string | Date,
): MonthLabel[] {
  const start = new Date(startDate)
  const end = new Date(endDate)

  if (end <= start) return []

  const labels: MonthLabel[] = []
  const current = new Date(start.getFullYear(), start.getMonth(), 1)

  // Move to first of next month if start is not the 1st
  if (start.getDate() > 1) {
    current.setMonth(current.getMonth() + 1)
  }

  while (current <= end) {
    const percent = getPositionPercent(current, start, end)
    if (percent >= 0 && percent <= 100) {
      labels.push({
        label: MONTH_NAMES_SHORT[current.getMonth()],
        percent,
      })
    }
    current.setMonth(current.getMonth() + 1)
  }

  return labels
}

/**
 * Calculate the semester progress percentage (how much time has passed).
 */
export function getSemesterProgress(
  startDate: string | Date,
  endDate: string | Date,
): number {
  const now = new Date()
  return getPositionPercent(now, startDate, endDate)
}

/**
 * Get a Tailwind color class for a deadline marker based on its status and due date.
 */
export function getMarkerColor(deadline: string, status: string | null): string {
  const isCompleted = status === 'completed' || status === 'submitted' || status === 'graded'
  if (isCompleted) return 'bg-green-500'

  const isOverdue = new Date(deadline) < new Date()
  if (status === 'in_progress') return 'bg-yellow-500'
  if (isOverdue) return 'bg-red-500'
  return 'bg-gray-400'
}

/**
 * Get a Tailwind color class for exam markers.
 */
export function getExamMarkerColor(): string {
  return 'bg-purple-500'
}
