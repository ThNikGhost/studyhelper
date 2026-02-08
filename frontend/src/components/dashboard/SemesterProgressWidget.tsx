import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { ProgressBar } from '@/components/ui/progress-bar'
import {
  TrendingUp,
  AlertCircle,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { getProgressBarColor, getProgressColor } from '@/lib/progressUtils'
import type { SemesterProgress } from '@/lib/progressUtils'

interface SemesterProgressWidgetProps {
  progress: SemesterProgress | undefined
  isLoading: boolean
  isError: boolean
}

export function SemesterProgressWidget({
  progress,
  isLoading,
  isError,
}: SemesterProgressWidgetProps) {
  // Top-3 subjects with the lowest progress (motivation to work on them)
  const lowestSubjects = progress
    ? [...progress.subjects]
        .filter((s) => s.total > 0)
        .sort((a, b) => a.percentage - b.percentage)
        .slice(0, 3)
    : []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-green-500" />
          Прогресс семестра
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
            Не удалось загрузить прогресс
          </div>
        )}

        {!isLoading && !isError && progress && (
          <>
            {/* Overall progress */}
            <div className="mb-4">
              <div className="flex items-baseline justify-between mb-1">
                <span className="text-sm font-medium">Общий прогресс</span>
                <span
                  className={`text-sm font-semibold ${getProgressColor(progress.percentage)}`}
                >
                  {progress.completed} из {progress.total} ({progress.percentage}%)
                </span>
              </div>
              <ProgressBar
                value={progress.percentage}
                color={getProgressBarColor(progress.percentage)}
              />
            </div>

            {/* Top-3 subjects with lowest progress */}
            {lowestSubjects.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Требуют внимания
                </p>
                {lowestSubjects.map((sp) => (
                  <div key={sp.subjectId}>
                    <div className="flex items-baseline justify-between mb-0.5">
                      <span className="text-sm truncate flex-1 mr-2">
                        {sp.subjectName}
                      </span>
                      <span
                        className={`text-xs font-medium ${getProgressColor(sp.percentage)}`}
                      >
                        {sp.percentage}%
                      </span>
                    </div>
                    <ProgressBar
                      value={sp.percentage}
                      color={getProgressBarColor(sp.percentage)}
                      size="sm"
                    />
                  </div>
                ))}
              </div>
            )}

            {progress.total === 0 && (
              <p className="text-muted-foreground text-sm py-2">
                Нет работ в этом семестре
              </p>
            )}
          </>
        )}

        {!isLoading && !isError && (
          <Link
            to="/subjects"
            className="flex items-center justify-center gap-1 text-sm text-primary hover:underline mt-3 pt-3 border-t"
          >
            Все предметы
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        )}
      </CardContent>
    </Card>
  )
}
