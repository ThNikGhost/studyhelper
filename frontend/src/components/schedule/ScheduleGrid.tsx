import { StickyNote } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TIME_SLOTS, LESSON_TYPE_COLORS } from '@/lib/constants'
import type { WeekSchedule, ScheduleEntry } from '@/types/schedule'
import { lessonTypeLabels } from '@/types/schedule'

interface ScheduleGridProps {
  weekSchedule: WeekSchedule
  currentEntryId?: number
  noteSubjectNames?: Set<string>
  onEntryClick?: (entry: ScheduleEntry) => void
}

// Day names
const DAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Format date as "DD.MM"
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
}

// Format location as "building-room"
function formatLocation(entry: ScheduleEntry): string | null {
  if (entry.building && entry.room) {
    return `${entry.building}-${entry.room}`
  }
  return entry.room || entry.building || null
}

// Get entry for specific day and time slot
function getEntryForSlot(
  entries: ScheduleEntry[],
  slotStart: string
): ScheduleEntry | undefined {
  return entries.find((e) => e.start_time.slice(0, 5) === slotStart)
}

// Check if today (local timezone)
function isToday(dateStr: string): boolean {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const today = `${year}-${month}-${day}`
  return dateStr === today
}

export function ScheduleGrid({ weekSchedule, currentEntryId, noteSubjectNames, onEntryClick }: ScheduleGridProps) {
  return (
    <div className="overflow-x-auto">
      <div className="min-w-[700px]">
        {/* Grid container - narrow time column, equal day columns */}
        <div className="grid rounded-lg overflow-hidden" style={{ gridTemplateColumns: '50px repeat(7, 1fr)' }}>
          {/* Header row - time column + days */}
          <div className="bg-muted p-1"></div>
          {weekSchedule.days.map((day) => (
            <div
              key={day.date}
              className={cn(
                'bg-muted p-2 text-center',
                isToday(day.date) && 'bg-primary/10'
              )}
            >
              <div className="font-medium text-sm">
                {DAY_NAMES[day.day_of_week - 1]}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatDate(day.date)}
              </div>
            </div>
          ))}

          {/* Time slots rows */}
          {TIME_SLOTS.map((slot) => (
            <div key={`row-${slot.pair}`} className="contents">
              {/* Time column */}
              <div className="bg-muted p-1 text-center">
                <div className="font-semibold text-sm">{slot.pair}</div>
                <div className="text-muted-foreground text-xs">
                  {slot.start}
                </div>
                <div className="text-muted-foreground text-xs">
                  {slot.end}
                </div>
              </div>

              {/* Day cells */}
              {weekSchedule.days.map((day) => {
                const entry = getEntryForSlot(day.entries, slot.start)
                const isActive = entry?.id === currentEntryId
                const isTodayCell = isToday(day.date)

                return (
                  <div
                    key={`${day.date}-${slot.pair}`}
                    className={cn(
                      'bg-background p-0.5 min-h-[60px]',
                      isTodayCell && 'bg-primary/5'
                    )}
                  >
                    {entry && (
                      <div
                        className={cn(
                          'h-full p-1.5 rounded border text-xs',
                          LESSON_TYPE_COLORS[entry.lesson_type],
                          isActive && 'ring-2 ring-primary',
                          onEntryClick && 'cursor-pointer hover:opacity-80'
                        )}
                        onClick={onEntryClick ? () => onEntryClick(entry) : undefined}
                        role={onEntryClick ? 'button' : undefined}
                        tabIndex={onEntryClick ? 0 : undefined}
                        onKeyDown={
                          onEntryClick
                            ? (e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault()
                                  onEntryClick(entry)
                                }
                              }
                            : undefined
                        }
                      >
                        {/* Subject name */}
                        <div className="flex items-start gap-0.5">
                          <div className="font-semibold line-clamp-2 leading-tight mb-0.5 flex-1">
                            {entry.subject_name}
                          </div>
                          {noteSubjectNames?.has(entry.subject_name) && (
                            <StickyNote className="h-3 w-3 text-amber-600 flex-shrink-0 mt-0.5" />
                          )}
                        </div>

                        {/* Type badge */}
                        <div className="text-[10px] text-black mb-0.5">
                          {lessonTypeLabels[entry.lesson_type]}
                        </div>

                        {/* Location */}
                        {formatLocation(entry) && (
                          <div className="text-[10px] text-black">
                            📍 {formatLocation(entry)}
                          </div>
                        )}

                        {/* Teacher (truncated) */}
                        {entry.teacher_name && (
                          <div className="text-[10px] text-black truncate">
                            {entry.teacher_name.split(' ').slice(0, 2).join(' ')}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ScheduleGrid
