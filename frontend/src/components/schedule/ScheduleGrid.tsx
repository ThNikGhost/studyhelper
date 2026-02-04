import { cn } from '@/lib/utils'
import type { WeekSchedule, ScheduleEntry } from '@/types/schedule'
import { LessonType, lessonTypeLabels } from '@/types/schedule'

interface ScheduleGridProps {
  weekSchedule: WeekSchedule
  currentEntryId?: number
}

// Time slots for lessons (matching backend TIME_SLOTS)
const TIME_SLOTS = [
  { pair: 1, start: '08:45', end: '10:20' },
  { pair: 2, start: '10:30', end: '12:05' },
  { pair: 3, start: '12:45', end: '14:20' },
  { pair: 4, start: '14:30', end: '16:05' },
  { pair: 5, start: '16:15', end: '17:50' },
  { pair: 6, start: '18:00', end: '19:35' },
  { pair: 7, start: '19:45', end: '21:20' },
  { pair: 8, start: '21:30', end: '23:05' },
]

// Day names
const DAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Colors for lesson types - vibrant colors for better readability
const lessonTypeColors: Record<LessonType, string> = {
  [LessonType.LECTURE]: 'bg-blue-200 dark:bg-blue-800 border-blue-400 dark:border-blue-600 text-blue-900 dark:text-blue-100',
  [LessonType.PRACTICE]: 'bg-green-200 dark:bg-green-800 border-green-400 dark:border-green-600 text-green-900 dark:text-green-100',
  [LessonType.LAB]: 'bg-orange-200 dark:bg-orange-800 border-orange-400 dark:border-orange-600 text-orange-900 dark:text-orange-100',
  [LessonType.SEMINAR]: 'bg-purple-200 dark:bg-purple-800 border-purple-400 dark:border-purple-600 text-purple-900 dark:text-purple-100',
  [LessonType.EXAM]: 'bg-red-200 dark:bg-red-800 border-red-400 dark:border-red-600 text-red-900 dark:text-red-100',
  [LessonType.CONSULTATION]: 'bg-slate-200 dark:bg-slate-700 border-slate-400 dark:border-slate-500 text-slate-900 dark:text-slate-100',
  [LessonType.OTHER]: 'bg-slate-200 dark:bg-slate-700 border-slate-400 dark:border-slate-500 text-slate-900 dark:text-slate-100',
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
            <div key={`row-${slot.pair}`} className="contents">
              {/* Time column */}
              <div className="bg-muted p-2 text-center text-xs">
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
                        <div className="font-semibold line-clamp-2 leading-tight mb-0.5">
                          {entry.subject_name}
                        </div>

                        {/* Type badge */}
                        <div className="text-[10px] opacity-80 mb-0.5">
                          {lessonTypeLabels[entry.lesson_type]}
                        </div>

                        {/* Location */}
                        {formatLocation(entry) && (
                          <div className="text-[10px] opacity-80">
                            📍 {formatLocation(entry)}
                          </div>
                        )}

                        {/* Teacher (truncated) */}
                        {entry.teacher_name && (
                          <div className="text-[10px] opacity-80 truncate">
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
