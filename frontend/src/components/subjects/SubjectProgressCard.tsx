import { BookOpen, Pencil, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { ProgressBar } from '@/components/ui/progress-bar'
import { getProgressBarColor } from '@/lib/progressUtils'
import {
  WorkStatus,
  workStatusLabels,
  workStatusColors,
} from '@/types/work'
import type { Subject } from '@/types/subject'
import type { SubjectProgress } from '@/lib/progressUtils'

interface SubjectProgressCardProps {
  subject: Subject
  progress: SubjectProgress | undefined
  onClick?: () => void
  onEdit?: (e: React.MouseEvent) => void
  onDelete?: (e: React.MouseEvent) => void
}

export function SubjectProgressCard({
  subject,
  progress,
  onClick,
  onEdit,
  onDelete,
}: SubjectProgressCardProps) {
  const hasWorks = progress && progress.total > 0

  return (
    <Card
      className={onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : undefined}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e: React.KeyboardEvent) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onClick()
              }
            }
          : undefined
      }
    >
      <CardContent className="py-4 px-4">
        {/* Header: icon + name + short_name + hours + actions */}
        <div className="flex items-center gap-2 mb-2 pr-1">
          <BookOpen className="h-4 w-4 text-green-500 shrink-0" />
          <h3 className="font-medium truncate flex-1 min-w-0">{subject.name}</h3>
          {subject.short_name && (
            <span className="text-xs bg-secondary px-1.5 py-0.5 rounded shrink-0">
              {subject.short_name}
            </span>
          )}
          {subject.total_hours && (
            <span className="text-xs text-muted-foreground shrink-0">
              {subject.total_hours} ч.
            </span>
          )}
          {(onEdit || onDelete) && (
            <div className="flex gap-1 shrink-0 ml-1">
              {onEdit && (
                <button
                  type="button"
                  className="h-7 w-7 inline-flex items-center justify-center rounded-md hover:bg-accent text-muted-foreground"
                  onClick={onEdit}
                  aria-label="Редактировать предмет"
                >
                  <Pencil className="h-3.5 w-3.5" />
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  className="h-7 w-7 inline-flex items-center justify-center rounded-md hover:bg-accent text-destructive"
                  onClick={onDelete}
                  aria-label="Удалить предмет"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          )}
        </div>

        {hasWorks ? (
          <>
            {/* Progress bar */}
            <ProgressBar
              value={progress.percentage}
              color={getProgressBarColor(progress.percentage)}
              showLabel
              className="mb-2"
            />

            {/* Completion text */}
            <p className="text-sm text-muted-foreground mb-2">
              {progress.completed} из {progress.total} выполнено
            </p>

            {/* Status breakdown badges */}
            <div className="flex flex-wrap gap-1">
              {progress.completed > 0 && (
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${workStatusColors[WorkStatus.COMPLETED]}`}
                >
                  {workStatusLabels[WorkStatus.COMPLETED]}: {progress.completed}
                </span>
              )}
              {progress.inProgress > 0 && (
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${workStatusColors[WorkStatus.IN_PROGRESS]}`}
                >
                  {workStatusLabels[WorkStatus.IN_PROGRESS]}: {progress.inProgress}
                </span>
              )}
              {progress.notStarted > 0 && (
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${workStatusColors[WorkStatus.NOT_STARTED]}`}
                >
                  {workStatusLabels[WorkStatus.NOT_STARTED]}: {progress.notStarted}
                </span>
              )}
            </div>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Нет работ</p>
        )}
      </CardContent>
    </Card>
  )
}
