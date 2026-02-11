import { StickyNote } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TIME_SLOTS, LESSON_TYPE_COLORS } from '@/lib/constants'
import { formatLocation } from '@/lib/dateUtils'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import type { WeekSchedule, ScheduleEntry } from '@/types/schedule'
import { lessonTypeLabels } from '@/types/schedule'

interface ScheduleGridProps {
  weekSchedule: WeekSchedule
  currentEntryId?: number
  noteSubjectNames?: Set<string>
  onEntryClick?: (entry: ScheduleEntry) => void
  /** All unfiltered entries for finding alternates. */
  allEntries?: ScheduleEntry[]
  /** User's subgroup for alternate detection. */
  userSubgroup?: number | null
}

// Day names
const DAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

// Format date as "DD.MM"
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
}

// Wrapper to use shared formatLocation with entry
function getEntryLocation(entry: ScheduleEntry): string | null {
  return formatLocation(entry.building, entry.room)
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

export function ScheduleGrid({
  weekSchedule,
  currentEntryId,
  noteSubjectNames,
  onEntryClick,
  allEntries,
  userSubgroup,
}: ScheduleGridProps) {
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

                // Find alternate entry (other subgroup) if subgroup filter is active
                // Check both when we have an entry AND when we don't (empty slot)
                const alternateEntry =
                  allEntries && userSubgroup !== null && userSubgroup !== undefined
                    ? allEntries.find((e) => {
                        // Same time slot
                        if (e.start_time.slice(0, 5) !== slot.start) return false
                        // Same date
                        const entryDate = e.lesson_date ?? ''
                        if (entryDate !== day.date) return false
                        // Different subgroup (not null and not user's)
                        if (e.subgroup === null) return false
                        if (e.subgroup === userSubgroup) return false
                        return true
                      })
                    : undefined

                return (
                  <div
                    key={`${day.date}-${slot.pair}`}
                    className={cn(
                      'bg-background p-0.5 min-h-[60px] relative',
                      isTodayCell && 'bg-primary/5'
                    )}
                  >
                    {/* Show "!" for other subgroup's class on empty slot */}
                    {!entry && alternateEntry && (
                      <Popover>
                        <PopoverTrigger asChild>
                          <button
                            className="absolute top-1 right-1 w-5 h-5 bg-amber-500
                                       rounded-full text-white text-xs flex items-center
                                       justify-center font-bold hover:bg-amber-600 z-10"
                            aria-label="Пара для другой подгруппы"
                          >
                            !
                          </button>
                        </PopoverTrigger>
                        <PopoverContent className="w-52 p-3" align="end">
                          <p className="font-medium text-sm mb-1">
                            Подгруппа {alternateEntry.subgroup}
                          </p>
                          <p className="text-sm">{alternateEntry.subject_name}</p>
                          {alternateEntry.teacher_name && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {alternateEntry.teacher_name}
                            </p>
                          )}
                          {getEntryLocation(alternateEntry) && (
                            <p className="text-xs text-muted-foreground">
                              📍 {getEntryLocation(alternateEntry)}
                            </p>
                          )}
                        </PopoverContent>
                      </Popover>
                    )}
                    {entry && (
                      <div
                        className={cn(
                          'relative h-full p-1.5 rounded border text-xs',
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
                        {/* Alternate entry indicator */}
                        {alternateEntry && (
                          <Popover>
                            <PopoverTrigger asChild>
                              <button
                                className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500
                                           rounded-full text-white text-xs flex items-center
                                           justify-center font-bold hover:bg-amber-600 z-10"
                                aria-label="Есть пара для другой подгруппы"
                                onClick={(e) => e.stopPropagation()}
                              >
                                !
                              </button>
                            </PopoverTrigger>
                            <PopoverContent className="w-52 p-3" align="end">
                              <p className="font-medium text-sm mb-1">
                                Подгруппа {alternateEntry.subgroup}
                              </p>
                              <p className="text-sm">{alternateEntry.subject_name}</p>
                              {alternateEntry.teacher_name && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  {alternateEntry.teacher_name}
                                </p>
                              )}
                              {getEntryLocation(alternateEntry) && (
                                <p className="text-xs text-muted-foreground">
                                  📍 {getEntryLocation(alternateEntry)}
                                </p>
                              )}
                            </PopoverContent>
                          </Popover>
                        )}

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
                        {getEntryLocation(entry) && (
                          <div className="text-[10px] text-black">
                            📍 {getEntryLocation(entry)}
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
