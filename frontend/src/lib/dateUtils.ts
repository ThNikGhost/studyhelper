/**
 * Shared date formatting utilities for consistent
 * deadline and date display across the application.
 */

export function formatDeadline(deadline: string): string {
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return 'Просрочено'
  }
  if (diffDays === 0) {
    return 'Сегодня'
  }
  if (diffDays === 1) {
    return 'Завтра'
  }
  if (diffDays <= 7) {
    return `Через ${diffDays} дн.`
  }

  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  })
}

export function getDeadlineColor(deadline: string): string {
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return 'text-red-600 dark:text-red-400'
  }
  if (diffDays <= 1) {
    return 'text-orange-600 dark:text-orange-400'
  }
  if (diffDays <= 3) {
    return 'text-yellow-600 dark:text-yellow-400'
  }
  return 'text-muted-foreground'
}

/**
 * Format a date to YYYY-MM-DD using local timezone components.
 * Avoids timezone shift issues from toISOString().
 */
export function formatDateLocal(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Get today's date as YYYY-MM-DD in local timezone.
 */
export function getToday(): string {
  return formatDateLocal(new Date())
}
