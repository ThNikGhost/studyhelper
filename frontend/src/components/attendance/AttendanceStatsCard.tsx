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
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Общая посещаемость</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2 mb-2">
          <span
            className={`text-3xl font-bold tabular-nums ${getAttendanceColor(stats.attendance_percent)}`}
          >
            {formatAttendancePercent(stats.attendance_percent)}
          </span>
          <span className="text-sm text-muted-foreground">
            {stats.attended} из {stats.total_classes} занятий
          </span>
        </div>

        <ProgressBar
          value={stats.attendance_percent}
          color={getAttendanceBarColor(stats.attendance_percent)}
          size="md"
          className="mb-3"
        />

        {stats.absences > 0 && (
          <p className="text-sm text-muted-foreground">
            Пропущено: <span className="font-medium text-red-600 dark:text-red-400">{stats.absences}</span>{' '}
            {stats.absences === 1
              ? 'занятие'
              : stats.absences < 5
                ? 'занятия'
                : 'занятий'}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
