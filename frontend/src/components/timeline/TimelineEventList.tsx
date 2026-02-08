import { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Clock, BookOpen } from 'lucide-react'
import { formatTime } from '@/lib/dateUtils'
import { workTypeLabels } from '@/types/work'
import type { WorkType } from '@/types/work'
import type { TimelineDeadline, TimelineExam } from '@/types/timeline'

interface TimelineEventListProps {
  deadlines: TimelineDeadline[]
  exams: TimelineExam[]
  limit?: number
}

type TimelineEvent = {
  id: string
  date: Date
  type: 'deadline' | 'exam'
  title: string
  subject: string
  detail: string
  color: string
}

export function TimelineEventList({ deadlines, exams, limit = 10 }: TimelineEventListProps) {
  const events = useMemo(() => {
    const all: TimelineEvent[] = []

    for (const d of deadlines) {
      const label = workTypeLabels[d.work_type as WorkType] ?? d.work_type
      all.push({
        id: `d-${d.work_id}`,
        date: new Date(d.deadline),
        type: 'deadline',
        title: d.title,
        subject: d.subject_name,
        detail: label,
        color: d.status === 'completed' || d.status === 'submitted' || d.status === 'graded'
          ? 'text-green-500'
          : new Date(d.deadline) < new Date()
            ? 'text-red-500'
            : 'text-muted-foreground',
      })
    }

    for (const e of exams) {
      all.push({
        id: `e-${e.schedule_entry_id}`,
        date: new Date(e.lesson_date),
        type: 'exam',
        title: `Экзамен: ${e.subject_name}`,
        subject: e.subject_name,
        detail: `${formatTime(e.start_time)}${e.room ? ` · ауд. ${e.room}` : ''}`,
        color: 'text-purple-500',
      })
    }

    all.sort((a, b) => a.date.getTime() - b.date.getTime())

    // Show upcoming events first (from today), then past
    const now = new Date()
    const upcoming = all.filter((e) => e.date >= now)
    const past = all.filter((e) => e.date < now)

    return [...upcoming, ...past].slice(0, limit)
  }, [deadlines, exams, limit])

  if (events.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Ближайшие события</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {events.map((event) => (
          <div key={event.id} className="flex items-start gap-3 py-1">
            <div className={`mt-0.5 ${event.color}`}>
              {event.type === 'exam' ? (
                <BookOpen className="h-4 w-4" />
              ) : (
                <Clock className="h-4 w-4" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{event.title}</p>
              <p className="text-xs text-muted-foreground">
                {event.date.toLocaleDateString('ru-RU')} · {event.subject} · {event.detail}
              </p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
