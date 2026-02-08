import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Calendar,
  Clock,
  MapPin,
  User,
  AlertCircle,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatTime, formatTimeUntil } from '@/lib/dateUtils'
import { lessonTypeLabels } from '@/types/schedule'
import type { ScheduleEntry, DaySchedule, CurrentLesson } from '@/types/schedule'

/** Determine lesson visual state relative to the current lesson. */
function getLessonState(
  entry: ScheduleEntry,
  currentLesson: CurrentLesson | undefined,
): 'past' | 'current' | 'upcoming' {
  if (currentLesson?.current?.id === entry.id) return 'current'
  if (!currentLesson?.current && !currentLesson?.next) return 'past'
  if (currentLesson?.current) {
    // Lessons before the current one are past
    if (entry.end_time <= currentLesson.current.start_time) return 'past'
  }
  if (currentLesson?.next) {
    // Lessons before the next one are past (when no current)
    if (!currentLesson.current && entry.end_time <= currentLesson.next.start_time) {
      return 'past'
    }
  }
  return 'upcoming'
}

interface LessonRowProps {
  entry: ScheduleEntry
  state: 'past' | 'current' | 'upcoming'
  timeUntil?: number | null
  onClick?: (entry: ScheduleEntry) => void
}

function LessonRow({ entry, state, timeUntil, onClick }: LessonRowProps) {
  const opacity = state === 'past' ? 'opacity-50' : ''
  const highlight =
    state === 'current'
      ? 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/30 pl-3'
      : 'pl-4'

  const handleClick = () => {
    onClick?.(entry)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault()
      onClick(entry)
    }
  }

  return (
    <div
      className={`py-2 ${opacity} ${highlight} rounded-r-lg ${onClick ? 'cursor-pointer hover:bg-accent/50' : ''}`}
      onClick={onClick ? handleClick : undefined}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? handleKeyDown : undefined}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-muted-foreground whitespace-nowrap">
              <Clock className="inline h-3.5 w-3.5 mr-1" />
              {formatTime(entry.start_time)} – {formatTime(entry.end_time)}
            </span>
            <span className="bg-secondary px-1.5 py-0.5 rounded text-xs whitespace-nowrap">
              {lessonTypeLabels[entry.lesson_type]}
            </span>
          </div>
          <div className="font-medium mt-0.5 truncate">{entry.subject_name}</div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
            {(entry.room || entry.building) && (
              <span className="inline-flex items-center gap-0.5">
                <MapPin className="h-3 w-3" />
                {[entry.room, entry.building].filter(Boolean).join(', ')}
              </span>
            )}
            {entry.teacher_name && (
              <span className="inline-flex items-center gap-0.5">
                <User className="h-3 w-3" />
                {entry.teacher_name}
              </span>
            )}
          </div>
        </div>
        {state === 'current' && (
          <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-0.5 rounded whitespace-nowrap flex-shrink-0">
            Сейчас
          </span>
        )}
        {state === 'upcoming' && timeUntil != null && (
          <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-0.5 rounded whitespace-nowrap flex-shrink-0">
            через {formatTimeUntil(timeUntil)}
          </span>
        )}
      </div>
    </div>
  )
}

interface TodayScheduleWidgetProps {
  todaySchedule: DaySchedule | undefined
  currentLesson: CurrentLesson | undefined
  isLoading: boolean
  isError: boolean
  onEntryClick?: (entry: ScheduleEntry) => void
}

export function TodayScheduleWidget({
  todaySchedule,
  currentLesson,
  isLoading,
  isError,
  onEntryClick,
}: TodayScheduleWidgetProps) {
  const entries = todaySchedule?.entries ?? []
  const count = entries.length

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-500" />
          Расписание на сегодня
          {count > 0 && (
            <span className="ml-auto text-sm font-normal text-muted-foreground">
              {count} {count === 1 ? 'пара' : count < 5 ? 'пары' : 'пар'}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {isError && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
            <AlertCircle className="h-4 w-4" />
            Не удалось загрузить расписание
          </div>
        )}

        {!isLoading && !isError && count > 0 && (
          <div className="space-y-1 -mx-2">
            {entries.map((entry, idx) => {
              const state = getLessonState(entry, currentLesson)
              // Show "time until" badge only for the first upcoming entry
              const isNextUpcoming =
                state === 'upcoming' &&
                (idx === 0 || getLessonState(entries[idx - 1], currentLesson) !== 'upcoming')
              const timeUntil = isNextUpcoming ? currentLesson?.time_until_next : null

              return (
                <LessonRow
                  key={entry.id}
                  entry={entry}
                  state={state}
                  timeUntil={timeUntil}
                  onClick={onEntryClick}
                />
              )
            })}
          </div>
        )}

        {!isLoading && !isError && count === 0 && (
          <p className="text-muted-foreground text-sm py-2">
            Сегодня занятий нет
          </p>
        )}

        {!isLoading && !isError && (
          <Link
            to="/schedule"
            className="flex items-center justify-center gap-1 text-sm text-primary hover:underline mt-3 pt-3 border-t"
          >
            Полное расписание
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        )}
      </CardContent>
    </Card>
  )
}
