import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ProgressBar } from '@/components/ui/progress-bar'
import {
  formatAttendancePercent,
  getAttendanceColor,
  getAttendanceBarColor,
} from '@/lib/attendanceUtils'
import type { AttendanceStats } from '@/types/attendance'

interface AttendanceStatsCardProps {
  stats: AttendanceStats
}

export function AttendanceStatsCard({ stats }: AttendanceStatsCardProps) {
  // Use total_planned if set, otherwise fall back to total_completed
  const total = stats.total_planned > 0 ? stats.total_planned : stats.total_completed
  const hasPlannedClasses = stats.total_planned > 0

  // Progress for the bar: attended / total * 100
  const progressPercent = total > 0 ? (stats.attended / total) * 100 : 0

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Общая посещаемость</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-3xl font-bold tabular-nums">
            {stats.attended} из {total}
          </span>
          <span
            className={`text-sm font-medium ${getAttendanceColor(stats.attendance_percent)}`}
          >
            ({formatAttendancePercent(stats.attendance_percent)})
          </span>
        </div>

        <ProgressBar
          value={progressPercent}
          color={getAttendanceBarColor(stats.attendance_percent)}
          size="md"
          className="mb-3"
        />

        <div className="text-sm text-muted-foreground space-y-1">
          {hasPlannedClasses && (
            <p>
              Пройдено занятий: {stats.total_completed} из {stats.total_planned} запланированных
            </p>
          )}
          {stats.absences > 0 && (
            <p>
              Пропущено:{' '}
              <span className="font-medium text-red-600 dark:text-red-400">{stats.absences}</span>{' '}
              {stats.absences === 1
                ? 'занятие'
                : stats.absences < 5
                  ? 'занятия'
                  : 'занятий'}
            </p>
          )}
          {!hasPlannedClasses && stats.total_completed === 0 && (
            <p className="text-amber-600 dark:text-amber-400">
              Укажите количество пар в настройках предметов для точного расчёта
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
