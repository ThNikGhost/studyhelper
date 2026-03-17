/**
 * Shared date formatting utilities for consistent
 * deadline and date display across the application.
 */

/**
 * Append local timezone offset to a naive datetime string.
 *
 * Converts "2026-03-12T18:00" → "2026-03-12T18:00:00+06:00" (for UTC+6).
 * This ensures the backend receives a timezone-aware datetime.
 */
export function appendTimezoneOffset(naiveDatetime: string): string {
  const date = new Date(naiveDatetime)
  const offsetMinutes = -date.getTimezoneOffset()
  const sign = offsetMinutes >= 0 ? '+' : '-'
  const absMinutes = Math.abs(offsetMinutes)
  const hours = String(Math.floor(absMinutes / 60)).padStart(2, '0')
  const minutes = String(absMinutes % 60).padStart(2, '0')

  // Normalize to include seconds
  const base = naiveDatetime.length === 16 ? naiveDatetime + ':00' : naiveDatetime
  return `${base}${sign}${hours}:${minutes}`
}

/**
 * Convert an ISO string (possibly UTC) to a datetime-local input value.
 *
 * Parses the ISO string into a Date, then formats using local timezone
 * components to produce "YYYY-MM-DDTHH:MM".
 */
export function toLocalDatetimeString(isoString: string): string {
  const date = new Date(isoString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const mins = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${mins}`
}

export function formatDeadline(deadline: string, hasTime: boolean = true, status?: string): string {
  const date = new Date(deadline)
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const deadlineDay = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.round((deadlineDay.getTime() - todayStart.getTime()) / (1000 * 60 * 60 * 24))

  const timeStr = hasTime
    ? ` ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    : ''

  if (diffDays < 0) {
    // Show "Просрочено" only for not_started (or when status is unknown)
    if (status && status !== 'not_started') {
      const dateStr = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
      })
      return hasTime ? `${dateStr}${timeStr}` : dateStr
    }
    return 'Просрочено'
  }
  if (diffDays === 0) {
    return hasTime ? `Сегодня${timeStr}` : 'Сегодня'
  }
  if (diffDays === 1) {
    return hasTime ? `Завтра${timeStr}` : 'Завтра'
  }
  if (diffDays <= 7) {
    return hasTime ? `Через ${diffDays} дн.${timeStr}` : `Через ${diffDays} дн.`
  }

  const dateStr = date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  })
  return hasTime ? `${dateStr}${timeStr}` : dateStr
}

export function getDeadlineColor(deadline: string, status?: string): string {
  const date = new Date(deadline)
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const deadlineDay = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.round((deadlineDay.getTime() - todayStart.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    if (status && status !== 'not_started') {
      return 'text-muted-foreground'
    }
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
 * Format an ISO date string (YYYY-MM-DD) to DD.MM.YYYY for display.
 *
 * @param dateStr - ISO date string like "2025-09-01".
 * @returns Formatted string like "01.09.2025".
 */
export function formatIsoDate(dateStr: string): string {
  const [year, month, day] = dateStr.split('-')
  return `${day}.${month}.${year}`
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
  // Clean building: remove parentheses and "Корпус"/"корп."/"корпус" prefix/suffix
  // "Корпус 2" → "2", "1 корпус" → "1", "корп. 3" → "3", "(6" → "6"
  const cleanBuilding =
    building
      ?.replace(/[()]/g, '')
      .replace(/(?:корпус|корп)\.?\s*/gi, '')
      .trim() || null

  // Clean room: strip "ауд."/"аудитория" prefix, extract room number if contains "зал"
  // e.g., "113) Спортивный зал" → "113", "Спортивный зал" → null, "ауд. 301" → "301"
  let cleanRoom: string | null = null
  if (room) {
    const stripped = room.replace(/ауд(?:итория)?\.?\s*/gi, '').trim()
    if (/зал/i.test(stripped)) {
      // Extract number before ")" or space
      const match = stripped.match(/^(\d+)/)
      cleanRoom = match ? match[1] : null
    } else {
      // No "зал" — use room as-is, just clean parentheses
      cleanRoom = stripped.replace(/[()]/g, '').trim() || null
    }
  }

  if (cleanBuilding && cleanRoom) {
    return `${cleanBuilding}-${cleanRoom}`
  }
  return cleanRoom || cleanBuilding || null
}

/**
 * Format a date as a human-readable relative time string in Russian.
 *
 * @param date - Date to format.
 * @returns Formatted string like "только что", "5 минут назад", "2 часа назад", "вчера".
 */
export function formatDistanceToNow(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMinutes = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMinutes < 1) {
    return 'только что'
  }
  if (diffMinutes < 60) {
    return `${diffMinutes} мин. назад`
  }
  if (diffHours < 24) {
    return `${diffHours} ч. назад`
  }
  if (diffDays === 1) {
    return 'вчера'
  }
  if (diffDays < 7) {
    return `${diffDays} дн. назад`
  }

  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
