import { useMemo } from 'react'
import { getPositionPercent, getMonthLabels, getSemesterProgress, getMarkerColor, getExamMarkerColor } from '@/lib/timelineUtils'
import { TimelineMarker } from './TimelineMarker'
import type { TimelineDeadline, TimelineExam } from '@/types/timeline'
import { formatTime } from '@/lib/dateUtils'

interface TimelineBarProps {
  startDate: string
  endDate: string
  deadlines: TimelineDeadline[]
  exams: TimelineExam[]
  showDeadlines?: boolean
  showExams?: boolean
  subjectFilter?: number | null
  onMarkerClick?: (type: 'deadline' | 'exam', id: number) => void
}

export function TimelineBar({
  startDate,
  endDate,
  deadlines,
  exams,
  showDeadlines = true,
  showExams = true,
  subjectFilter = null,
  onMarkerClick,
}: TimelineBarProps) {
  const progress = useMemo(() => getSemesterProgress(startDate, endDate), [startDate, endDate])
  const monthLabels = useMemo(() => getMonthLabels(startDate, endDate), [startDate, endDate])
  const todayPercent = useMemo(() => getPositionPercent(new Date(), startDate, endDate), [startDate, endDate])

  const filteredDeadlines = useMemo(() => {
    if (!showDeadlines) return []
    if (subjectFilter) return deadlines.filter((d) => d.subject_id === subjectFilter)
    return deadlines
  }, [deadlines, showDeadlines, subjectFilter])

  const filteredExams = useMemo(() => {
    if (!showExams) return []
    return exams
  }, [exams, showExams])

  return (
    <div className="space-y-1">
      {/* Timeline bar container */}
      <div className="relative w-full h-12 bg-muted rounded-lg overflow-visible" role="img" aria-label="Timeline семестра">
        {/* Progress fill */}
        <div
          className="absolute top-0 left-0 h-full bg-primary/15 rounded-l-lg"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />

        {/* Today marker */}
        {todayPercent > 0 && todayPercent < 100 && (
          <div
            className="absolute top-0 h-full w-0.5 bg-red-500 z-20"
            style={{ left: `${todayPercent}%` }}
          >
            <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[10px] font-medium text-red-500 whitespace-nowrap">
              Сегодня
            </span>
          </div>
        )}

        {/* Deadline markers */}
        {filteredDeadlines.map((d) => {
          const percent = getPositionPercent(d.deadline, startDate, endDate)
          return (
            <TimelineMarker
              key={`d-${d.work_id}`}
              percent={percent}
              color={getMarkerColor(d.deadline, d.status)}
              label={d.title}
              sublabel={`${d.subject_name} · ${new Date(d.deadline).toLocaleDateString('ru-RU')}`}
              variant="circle"
              onClick={() => onMarkerClick?.('deadline', d.work_id)}
            />
          )
        })}

        {/* Exam markers */}
        {filteredExams.map((e) => {
          const percent = getPositionPercent(e.lesson_date, startDate, endDate)
          return (
            <TimelineMarker
              key={`e-${e.schedule_entry_id}`}
              percent={percent}
              color={getExamMarkerColor()}
              label={`Экзамен: ${e.subject_name}`}
              sublabel={`${new Date(e.lesson_date).toLocaleDateString('ru-RU')} · ${formatTime(e.start_time)}${e.room ? ` · ${e.room}` : ''}`}
              variant="diamond"
              onClick={() => onMarkerClick?.('exam', e.schedule_entry_id)}
            />
          )
        })}
      </div>

      {/* Month axis */}
      <div className="relative w-full h-4">
        {monthLabels.map((m) => (
          <span
            key={m.label + m.percent}
            className="absolute text-[10px] text-muted-foreground -translate-x-1/2"
            style={{ left: `${m.percent}%` }}
          >
            {m.label}
          </span>
        ))}
      </div>
    </div>
  )
}
