import { cn } from '@/lib/utils'
import type { WeekSchedule, ScheduleEntry } from '@/types/schedule'
import { LessonType, lessonTypeLabels } from '@/types/schedule'

interface ScheduleGridProps {
  weekSchedule: WeekSchedule
  currentEntryId?: number
}

// Time slots for lessons
const TIME_SLOTS = [
  { pair: 1, start: '08:45', end: '10:20' },
  { pair: 2, start: '10:30', end: '12:05' },
  { pair: 3, start: '12:35', end: '14:10' },
  { pair: 4, start: '14:20', end: '15:55' },
  { pair: 5, start: '16:05', end: '17:40' },
  { pair: 6, start: '17:50', end: '19:25' },
  { pair: 7, start: '19:35', end: '21:10' },
]

// Day names
const DAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Colors for lesson types
const lessonTypeColors: Record<LessonType, string> = {
  [LessonType.LECTURE]: 'bg-blue-100 dark:bg-blue-900/50 border-blue-300 dark:border-blue-700',
  [LessonType.PRACTICE]: 'bg-green-100 dark:bg-green-900/50 border-green-300 dark:border-green-700',
  [LessonType.LAB]: 'bg-orange-100 dark:bg-orange-900/50 border-orange-300 dark:border-orange-700',
  [LessonType.SEMINAR]: 'bg-purple-100 dark:bg-purple-900/50 border-purple-300 dark:border-purple-700',
  [LessonType.EXAM]: 'bg-red-100 dark:bg-red-900/50 border-red-300 dark:border-red-700',
  [LessonType.CONSULTATION]: 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600',
  [LessonType.OTHER]: 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600',
}

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

// Check if today
function isToday(dateStr: string): boolean {
  const today = new Date().toISOString().split('T')[0]
  return dateStr === today
}

export function ScheduleGrid({ weekSchedule, currentEntryId }: ScheduleGridProps) {
  return (
    <div className="overflow-x-auto">
      <div className="min-w-[700px]">
        {/* Grid container */}
        <div className="grid grid-cols-8 gap-px bg-border rounded-lg overflow-hidden">
          {/* Header row - time column + days */}
          <div className="bg-muted p-2 text-center text-xs font-medium text-muted-foreground">
            Время
          </div>
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
            <>
              {/* Time column */}
              <div
                key={`time-${slot.pair}`}
                className="bg-muted p-2 text-center text-xs"
              >
                <div className="font-medium">{slot.pair}</div>
                <div className="text-muted-foreground text-[10px]">
                  {slot.start}
                </div>
                <div className="text-muted-foreground text-[10px]">
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
                      'bg-background p-1 min-h-[80px]',
                      isTodayCell && 'bg-primary/5'
                    )}
                  >
                    {entry && (
                      <div
                        className={cn(
                          'h-full p-1.5 rounded border text-xs',
                          lessonTypeColors[entry.lesson_type],
                          isActive && 'ring-2 ring-primary'
                        )}
                      >
                        {/* Subject name */}
                        <div className="font-medium line-clamp-2 leading-tight mb-0.5">
                          {entry.subject_name}
                        </div>

                        {/* Type badge */}
                        <div className="text-[10px] text-muted-foreground mb-0.5">
                          {lessonTypeLabels[entry.lesson_type]}
                        </div>

                        {/* Location */}
                        {formatLocation(entry) && (
                          <div className="text-[10px] text-muted-foreground">
                            📍 {formatLocation(entry)}
                          </div>
                        )}

                        {/* Teacher (truncated) */}
                        {entry.teacher_name && (
                          <div className="text-[10px] text-muted-foreground truncate">
                            {entry.teacher_name.split(' ').slice(0, 2).join(' ')}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ScheduleGrid
