import type { DaySchedule, ScheduleEntry } from '@/types/schedule'
import { LessonCard } from './LessonCard'
import { cn } from '@/lib/utils'

interface DayScheduleCardProps {
  day: DaySchedule
  currentEntryId?: number
  isToday?: boolean
  onEntryClick?: (entry: ScheduleEntry) => void
}

// Format date to "DD.MM"
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  return `${day}.${month}`
}

export function DayScheduleCard({
  day,
  currentEntryId,
  isToday = false,
  onEntryClick,
}: DayScheduleCardProps) {
  const hasEntries = day.entries.length > 0

  return (
    <div className="space-y-3">
      {/* Day header */}
      <div
        className={cn(
          'flex items-center gap-2 pb-2 border-b',
          isToday && 'border-primary'
        )}
      >
        <h2
          className={cn(
            'font-semibold',
            isToday ? 'text-primary' : 'text-foreground'
          )}
        >
          {day.day_name}
        </h2>
        <span className="text-sm text-muted-foreground">
          {formatDate(day.date)}
        </span>
        {isToday && (
          <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">
            Сегодня
          </span>
        )}
      </div>

      {/* Lessons list */}
      {hasEntries ? (
        <div className="space-y-2">
          {day.entries.map((entry: ScheduleEntry) => (
            <LessonCard
              key={entry.id}
              entry={entry}
              isActive={entry.id === currentEntryId}
              onClick={onEntryClick}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-muted-foreground">
          <p>Нет занятий</p>
        </div>
      )}
    </div>
  )
}

export default DayScheduleCard
