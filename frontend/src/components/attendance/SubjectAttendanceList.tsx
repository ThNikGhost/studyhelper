import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ProgressBar } from '@/components/ui/progress-bar'
import {
  formatAttendancePercent,
  getAttendanceColor,
  getAttendanceBarColor,
} from '@/lib/attendanceUtils'
import type { SubjectAttendanceStats } from '@/types/attendance'

interface SubjectAttendanceListProps {
  subjects: SubjectAttendanceStats[]
  selectedSubjectId?: number | null
  onSelectSubject?: (subjectId: number | null) => void
}

export function SubjectAttendanceList({
  subjects,
  selectedSubjectId,
  onSelectSubject,
}: SubjectAttendanceListProps) {
  if (subjects.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-4 text-center">
        Нет данных о занятиях
      </p>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">По предметам</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {subjects.map((subj) => {
          const isSelected = selectedSubjectId === subj.subject_id
          return (
            <button
              key={subj.subject_name}
              type="button"
              className={`w-full text-left p-2 rounded-md transition-colors ${
                isSelected
                  ? 'bg-accent'
                  : 'hover:bg-muted/50'
              }`}
              onClick={() =>
                onSelectSubject?.(isSelected ? null : subj.subject_id)
              }
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium truncate flex-1">
                  {subj.subject_name}
                </span>
                <span
                  className={`text-sm font-bold tabular-nums ml-2 ${getAttendanceColor(subj.attendance_percent)}`}
                >
                  {formatAttendancePercent(subj.attendance_percent)}
                </span>
              </div>
              <ProgressBar
                value={subj.attendance_percent}
                color={getAttendanceBarColor(subj.attendance_percent)}
                size="sm"
              />
              <p className="text-xs text-muted-foreground mt-1">
                {subj.attended} из {subj.total_classes} · пропущено {subj.absences}
              </p>
            </button>
          )
        })}
      </CardContent>
    </Card>
  )
}
