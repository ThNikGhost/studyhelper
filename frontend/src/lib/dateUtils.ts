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

/**
 * Format time string from HH:MM:SS to HH:MM.
 */
export function formatTime(timeStr: string): string {
  return timeStr.slice(0, 5)
}

/**
 * Format minutes into a human-readable Russian string.
 *
 * @param minutes - Number of minutes to format.
 * @returns Formatted string like "менее минуты", "15 мин", "1 ч 30 мин".
 */
export function formatTimeUntil(minutes: number): string {
  if (minutes < 1) {
    return 'менее минуты'
  }
  if (minutes < 60) {
    return `${Math.floor(minutes)} мин`
  }
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = Math.floor(minutes % 60)
  if (remainingMinutes === 0) {
    return `${hours} ч`
  }
  return `${hours} ч ${remainingMinutes} мин`
}

/**
 * Format schedule entry location as "building-room".
 * Cleans up data format from API (e.g., "(6" → "6", "113) Спортивный зал" → "113").
 *
 * @param building - Building number/name (e.g., "(6" or "6")
 * @param room - Room number/name (e.g., "113) Спортивный зал" or "113")
 * @returns Formatted location string like "6-113" or null if no location data
 */
export function formatLocation(
  building: string | null | undefined,
  room: string | null | undefined
): string | null {
  // Clean building: remove parentheses "(6" or "6)" → "6"
  const cleanBuilding = building?.replace(/[()]/g, '').trim() || null

  // Clean room: extract room number if contains "зал"
  // e.g., "113) Спортивный зал" → "113", "Спортивный зал" → null
  let cleanRoom: string | null = null
  if (room) {
    if (/зал/i.test(room)) {
      // Extract number before ")" or space
      const match = room.match(/^(\d+)/)
      cleanRoom = match ? match[1] : null
    } else {
      // No "зал" — use room as-is, just clean parentheses
      cleanRoom = room.replace(/[()]/g, '').trim() || null
    }
  }

  if (cleanBuilding && cleanRoom) {
    return `${cleanBuilding}-${cleanRoom}`
  }
  return cleanRoom || cleanBuilding || null
}
