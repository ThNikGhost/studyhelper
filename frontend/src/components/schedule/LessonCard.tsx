import { Card, CardContent } from '@/components/ui/card'
import type { ScheduleEntry } from '@/types/schedule'
import { LessonType, lessonTypeLabels } from '@/types/schedule'
import { cn } from '@/lib/utils'

interface LessonCardProps {
  entry: ScheduleEntry
  isActive?: boolean
}

// Colors for lesson types
const lessonTypeColors: Record<LessonType, string> = {
  [LessonType.LECTURE]: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  [LessonType.PRACTICE]: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  [LessonType.LAB]: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  [LessonType.SEMINAR]: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  [LessonType.EXAM]: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  [LessonType.CONSULTATION]: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  [LessonType.OTHER]: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
}

// Format time from HH:MM:SS to HH:MM
function formatTime(time: string): string {
  return time.slice(0, 5)
}

export function LessonCard({ entry, isActive = false }: LessonCardProps) {
  const startTime = formatTime(entry.start_time)
  const endTime = formatTime(entry.end_time)

  const location = [entry.room, entry.building && `корп. ${entry.building}`]
    .filter(Boolean)
    .join(', ')

  return (
    <Card
      className={cn(
        'transition-all',
        isActive && 'ring-2 ring-primary border-primary'
      )}
    >
      <CardContent className="p-4">
        {/* Time and type */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">
            {startTime} – {endTime}
          </span>
          <span
            className={cn(
              'text-xs px-2 py-0.5 rounded-full font-medium',
              lessonTypeColors[entry.lesson_type]
            )}
          >
            {lessonTypeLabels[entry.lesson_type]}
          </span>
        </div>

        {/* Subject name */}
        <h3 className="font-semibold text-foreground mb-2 leading-tight">
          {entry.subject_name}
        </h3>

        {/* Teacher and location */}
        <div className="flex flex-col gap-1 text-sm text-muted-foreground">
          {entry.teacher_name && (
            <div className="flex items-center gap-1.5">
              <span className="text-base">👤</span>
              <span>{entry.teacher_name}</span>
            </div>
          )}
          {location && (
            <div className="flex items-center gap-1.5">
              <span className="text-base">📍</span>
              <span>{location}</span>
            </div>
          )}
        </div>

        {/* Subgroup */}
        {entry.subgroup && (
          <div className="mt-2 text-xs text-muted-foreground">
            Подгруппа {entry.subgroup}
          </div>
        )}

        {/* Notes */}
        {entry.notes && (
          <div className="mt-2 text-xs text-muted-foreground italic">
            {entry.notes}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default LessonCard
